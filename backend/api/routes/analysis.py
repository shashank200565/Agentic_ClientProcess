from __future__ import annotations

import io
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, ValidationError
from pypdf import PdfReader

try:
    from backend.db.db import get_analyzed_workflows, get_workflow, save_workflow
    from backend.pipeline.extraction import extract_steps
    from backend.pipeline.decision_engine import score_step
    from backend.pipeline.automation_blueprint import generate_automation_blueprint
    from backend.pipeline.redesign import generate_redesign
    from backend.pipeline.orchestration import run_orchestration
    from backend.pipeline.llm_client import LLMClientError
    from backend.pipeline.schemas import AutomationBlueprint, RedesignProposal, Workflow
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from db.db import get_analyzed_workflows, get_workflow, save_workflow
    from pipeline.extraction import extract_steps
    from pipeline.decision_engine import score_step
    from pipeline.automation_blueprint import generate_automation_blueprint
    from pipeline.redesign import generate_redesign
    from pipeline.orchestration import run_orchestration
    from pipeline.llm_client import LLMClientError
    from pipeline.schemas import AutomationBlueprint, RedesignProposal, Workflow


router = APIRouter(prefix="/analyze", tags=["analysis"])


class TextExtractionRequest(BaseModel):
    text: str = Field(min_length=1)
    workflow_id: str | None = None
    name: str | None = None


class ScoreWorkflowRequest(BaseModel):
    workflow_id: str = Field(min_length=1)


class GeneratorRequest(BaseModel):
    workflow_id: str = Field(min_length=1)
    step_id: str = Field(min_length=1)
    user_notes: str | None = Field(default=None, max_length=2000)


class OrchestrationRequest(BaseModel):
    workflow_id: str = Field(min_length=1)


@router.get("/workflows", response_model=list[Workflow])
def list_analyzed_workflows() -> list[Workflow]:
    return get_analyzed_workflows()


def _safe_name(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9 _-]+", "", value).strip()
    return normalized or "Uploaded workflow"


def _pdf_text(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
        text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read the PDF") from exc
    if not text.strip():
        raise HTTPException(status_code=400, detail="The PDF contains no extractable text")
    return text


async def _request_input(request: Request) -> tuple[str, str, str | None, str]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        try:
            payload = TextExtractionRequest.model_validate(await request.json())
        except (ValueError, ValidationError) as exc:
            raise HTTPException(status_code=422, detail="JSON body must include text") from exc
        return payload.text, _safe_name(payload.name or "Uploaded workflow"), payload.workflow_id, "text"

    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        workflow_id = str(form.get("workflow_id")) if form.get("workflow_id") else None
        name = _safe_name(str(form.get("name") or "Uploaded workflow"))
        text_value = form.get("text")
        upload = form.get("file")
        if upload is not None and hasattr(upload, "read"):
            filename = getattr(upload, "filename", "") or ""
            content = await upload.read()
            if filename.lower().endswith(".pdf") or getattr(upload, "content_type", "") == "application/pdf":
                return _pdf_text(content), _safe_name(Path(filename).stem or name), workflow_id, "pdf"
            decoded = content.decode("utf-8", errors="replace")
            if decoded.strip():
                return decoded, _safe_name(Path(filename).stem or name), workflow_id, "text"
        if isinstance(text_value, str) and text_value.strip():
            return text_value, name, workflow_id, "text"
        raise HTTPException(status_code=422, detail="Multipart body must include text or a file")

    if content_type.startswith("text/plain"):
        text = (await request.body()).decode("utf-8", errors="replace")
        if text.strip():
            return text, "Uploaded workflow", None, "text"

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Use application/json, text/plain, or multipart/form-data",
    )


@router.post("/extract", response_model=Workflow)
async def extract_workflow(request: Request) -> Workflow:
    raw_text, name, workflow_id, source_type = await _request_input(request)
    try:
        steps = extract_steps(raw_text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except LLMClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    workflow = Workflow(
        workflow_id=workflow_id or uuid4().hex,
        name=name,
        source_type=source_type,
        status="extracted",
        raw_text=raw_text,
        steps=steps,
    )
    save_workflow(workflow)
    return workflow


@router.post("/score", response_model=Workflow)
def score_workflow(payload: ScoreWorkflowRequest) -> Workflow:
    workflow = get_workflow(payload.workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not workflow.steps:
        raise HTTPException(status_code=422, detail="Workflow has no extracted steps")

    sibling_names = ", ".join(step.name for step in workflow.steps)
    try:
        scores = [
            score_step(
                step,
                (
                    f"workflow_id={workflow.workflow_id} workflow_name={workflow.name!r} "
                    f"step_position={position} of {len(workflow.steps)} "
                    f"sibling_steps=[{sibling_names}]"
                ),
            )
            for position, step in enumerate(workflow.steps, start=1)
        ]
    except LLMClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    analyzed_workflow = workflow.model_copy(update={"scores": scores, "status": "analyzed"})
    save_workflow(analyzed_workflow)
    return analyzed_workflow


def _generator_inputs(payload: GeneratorRequest, expected_verdict: str):
    workflow = get_workflow(payload.workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    step = next((item for item in workflow.steps if item.step_id == payload.step_id), None)
    score = next((item for item in workflow.scores if item.step_id == payload.step_id), None)
    if step is None or score is None:
        raise HTTPException(status_code=404, detail="Step or score not found")
    if score.verdict != expected_verdict:
        raise HTTPException(
            status_code=422,
            detail=f"Step verdict must be '{expected_verdict}'",
        )
    return workflow, step, score


@router.post("/automation-blueprint", response_model=AutomationBlueprint)
def create_automation_blueprint(payload: GeneratorRequest) -> AutomationBlueprint:
    workflow, step, score = _generator_inputs(payload, "automate")
    try:
        blueprint = generate_automation_blueprint(step, score, payload.user_notes)
    except (LLMClientError, ValueError) as exc:
        raise HTTPException(status_code=502 if isinstance(exc, LLMClientError) else 422, detail=str(exc)) from exc
    updated = workflow.model_copy(update={
        "automation_blueprints": [
            item for item in workflow.automation_blueprints
            if item.step_id != payload.step_id
        ] + [blueprint]
    })
    save_workflow(updated)
    return blueprint


@router.post("/redesign", response_model=RedesignProposal)
def create_redesign(payload: GeneratorRequest) -> RedesignProposal:
    workflow, step, score = _generator_inputs(payload, "redesign")
    try:
        proposal = generate_redesign(step, score, payload.user_notes)
    except (LLMClientError, ValueError) as exc:
        raise HTTPException(status_code=502 if isinstance(exc, LLMClientError) else 422, detail=str(exc)) from exc
    updated = workflow.model_copy(update={
        "redesign_proposals": [
            item for item in workflow.redesign_proposals
            if item.step_id != payload.step_id
        ] + [proposal]
    })
    save_workflow(updated)
    return proposal


@router.post("/orchestrate", response_model=Workflow)
def orchestrate_workflow(payload: OrchestrationRequest) -> Workflow:
    workflow = get_workflow(payload.workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if not workflow.scores:
        raise HTTPException(status_code=422, detail="Workflow must be scored before orchestration")
    try:
        completed = run_orchestration(workflow)
    except (LLMClientError, ValueError) as exc:
        raise HTTPException(status_code=502 if isinstance(exc, LLMClientError) else 422, detail=str(exc)) from exc
    save_workflow(completed)
    return completed
