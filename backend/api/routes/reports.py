from fastapi import APIRouter, HTTPException

try:
    from backend.db.db import get_workflow
    from backend.pipeline.report import generate_executive_report
    from backend.pipeline.schemas import ExecutiveReport
except ModuleNotFoundError:
    from db.db import get_workflow
    from pipeline.report import generate_executive_report
    from pipeline.schemas import ExecutiveReport


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{workflow_id}", response_model=ExecutiveReport)
def get_executive_report(workflow_id: str) -> ExecutiveReport:
    workflow = get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    try:
        return generate_executive_report(workflow)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
