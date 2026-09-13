from __future__ import annotations

try:
    from backend.pipeline.llm_client import call_llm, get_reasoning_model
    from backend.pipeline.schemas import RedesignProposal, StaticWorkflowDiagram, StepScore, WorkflowStep
except ModuleNotFoundError:
    from pipeline.llm_client import call_llm, get_reasoning_model
    from pipeline.schemas import RedesignProposal, StaticWorkflowDiagram, StepScore, WorkflowStep
from pydantic import BaseModel, ConfigDict, field_validator


class RedesignDraft(BaseModel):
    model_config = ConfigDict(extra="ignore")

    problem_statement: str
    proposed_design: str
    agent_responsibilities: list[str]
    human_controls: list[str]
    expected_benefits: list[str]
    diagram: StaticWorkflowDiagram

    @field_validator(
        "agent_responsibilities", "human_controls", "expected_benefits", mode="before"
    )
    @classmethod
    def normalize_lists(cls, value):
        return [
            item if isinstance(item, str) else ": ".join(
                str(part) for part in item.values()
            )
            for item in value
        ]


def generate_redesign(step: WorkflowStep, score: StepScore) -> RedesignProposal:
    """Generate an agent-first redesign with explicit human control points."""
    if score.verdict != "redesign":
        raise ValueError("Redesign proposals require verdict='redesign'")

    prompt = f"""Redesign this investment-management workflow step around a bounded AI agent workflow.
Be specific to the actual step content, not generic. Describe the problem, proposed design,
agent responsibilities, human controls, and measurable expected benefits.
The diagram must show a simple linear agent-first flow with distinct role, handoff, and human checkpoint nodes.
Use node_type values such as input, agent, handoff, human_checkpoint, and output. Do not omit human controls.
Return a JSON object with exactly these fields: problem_statement, proposed_design,
agent_responsibilities, human_controls, expected_benefits, and diagram.

Step name: {step.name}
Step description: {step.description}
Scores: {score.scores.model_dump_json()}
Decision reasoning: {score.reasoning}
"""
    draft = call_llm(
        prompt,
        model=get_reasoning_model(),
        response_schema=RedesignDraft,
    )
    return RedesignProposal(
        workflow_id=score.workflow_id,
        step_id=score.step_id,
        current_step=step,
        problem_statement=draft.problem_statement,
        proposed_design=draft.proposed_design,
        agent_responsibilities=draft.agent_responsibilities,
        human_controls=draft.human_controls,
        expected_benefits=draft.expected_benefits,
        diagram=draft.diagram,
    )
