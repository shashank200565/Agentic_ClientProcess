from uuid import uuid4

from fastapi import APIRouter, HTTPException

try:
    from backend.db.db import get_session, get_workflow, save_session
    from backend.pipeline.schemas import WorkflowSession
except ModuleNotFoundError:
    from db.db import get_session, get_workflow, save_session
    from pipeline.schemas import WorkflowSession

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/{workflow_id}", response_model=WorkflowSession)
def create_workflow_session(workflow_id: str) -> WorkflowSession:
    workflow = get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    session = WorkflowSession(session_id=uuid4().hex, workflow_id=workflow_id, current_stage=workflow.status, workflow=workflow)
    save_session(session)
    return session


@router.get("/{session_id}", response_model=WorkflowSession)
def resume_workflow_session(session_id: str) -> WorkflowSession:
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
