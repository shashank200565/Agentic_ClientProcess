from __future__ import annotations

try:
    from backend.pipeline.llm_client import call_llm, get_extraction_model
    from backend.pipeline.schemas import AutomationBlueprint, StaticWorkflowDiagram, StepScore, WorkflowStep
except ModuleNotFoundError:
    from pipeline.llm_client import call_llm, get_extraction_model
    from pipeline.schemas import AutomationBlueprint, StaticWorkflowDiagram, StepScore, WorkflowStep
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AutomationDraft(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mechanism_type: str
    trigger_condition: str | None = None
    trigger: str | None = None
    rationale: str
    diagram: StaticWorkflowDiagram | None = None

    @field_validator("diagram", mode="before")
    @classmethod
    def ignore_malformed_diagram(cls, value):
        return value if isinstance(value, dict) else None

    def trigger_text(self) -> str:
        return self.trigger_condition or self.trigger or "When the workflow step is ready to run."


def generate_automation_blueprint(
    step: WorkflowStep, score: StepScore, user_notes: str | None = None
) -> AutomationBlueprint:
    """Generate a small, conventional automation proposal for one automate step."""
    if score.verdict != "automate":
        raise ValueError("Automation blueprints require verdict='automate'")

    notes = f"\nAdditional user instructions for this regeneration:\n{user_notes.strip()}\n" if user_notes and user_notes.strip() else ""
    prompt = f"""Create a concise conventional automation blueprint for this investment-management workflow step.
Do not propose an AI agent, autonomous reasoning, branching, or creative redesign.
Choose one mechanism_type: rules_engine, rpa, scheduled_job, or existing_stp_extension.
The trigger must be short and specific to the step. The rationale must be 1-2 sentences and
explicitly reference the actual repetitiveness score ({score.scores.repetitiveness}/5) and
compliance sensitivity score ({score.scores.compliance_sensitivity}/5).
Return a JSON object with exactly these fields: mechanism_type, trigger_condition, rationale, diagram.
The diagram must be exactly linear: input -> mechanism -> output,
with node_type values input, mechanism, and output.

Step name: {step.name}
Step description: {step.description}
Scores: {score.scores.model_dump_json()}
{notes}
"""
    draft = call_llm(
        prompt,
        model=get_extraction_model(),
        response_schema=AutomationDraft,
    )
    blueprint = AutomationBlueprint(
        workflow_id=score.workflow_id,
        step_id=score.step_id,
        agent_name=_agent_name_for_step(step, draft.mechanism_type),
        current_step=step,
        mechanism_type=draft.mechanism_type,
        trigger_condition=draft.trigger_text(),
        rationale=draft.rationale,
        diagram=draft.diagram or StaticWorkflowDiagram(
            nodes=[
                {"id": "input", "label": step.name, "node_type": "input"},
                {"id": "mechanism", "label": draft.mechanism_type, "node_type": "mechanism"},
                {"id": "output", "label": f"Completed {step.name}", "node_type": "output"},
            ],
            edges=[{"source": "input", "target": "mechanism"}, {"source": "mechanism", "target": "output"}],
        ),
    )
    return blueprint


def _agent_name_for_step(step: WorkflowStep, mechanism_type: str) -> str:
    text = f"{step.name} {step.description}".lower()
    if any(term in text for term in ("reconcil", "match", "confirmation")):
        return "Reconciliation Bot"
    if any(term in text for term in ("exception", "escalat", "handoff", "route")):
        return "Routing Agent"
    if any(term in text for term in ("complete", "validat", "required", "quality")):
        return "Validation Bot"
    if any(term in text for term in ("threshold", "limit", "compare", "calculate")):
        return "Control Rules Agent"
    if any(term in text for term in ("report", "assemble", "template")):
        return "Reporting Automation Bot"
    return {
        "rpa": "Robotic Process Automation (RPA) Bot",
        "scheduled_job": "Scheduled Workflow Runner",
        "existing_stp_extension": "Straight-Through Processing Agent",
    }.get(mechanism_type, "Workflow Automation Agent")
