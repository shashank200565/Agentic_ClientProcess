from __future__ import annotations

import io
import re
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, ValidationError
from pypdf import PdfReader

try:
    from backend.db.db import save_workflow
    from backend.pipeline.extraction import extract_steps
    from backend.pipeline.llm_client import LLMClientError
    from backend.pipeline.schemas import Workflow
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from db.db import save_workflow
    from pipeline.extraction import extract_steps
    from pipeline.llm_client import LLMClientError
    from pipeline.schemas import Workflow


router = APIRouter(prefix="/analyze", tags=["analysis"])


class TextExtractionRequest(BaseModel):
    text: str = Field(min_length=1)
    workflow_id: str | None = None
    name: str | None = None


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
