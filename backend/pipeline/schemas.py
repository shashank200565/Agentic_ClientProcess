from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


Verdict = Literal["leave_as_is", "automate", "redesign"]
WorkflowStatus = Literal["uploaded", "extracted", "analyzed"]


class WorkflowStep(BaseModel):
    """A single current-state step extracted from a workflow description."""

    model_config = ConfigDict(extra="forbid")

    step_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)

    @field_validator("step_id", mode="before")
    @classmethod
    def normalize_step_id(cls, value: object) -> str:
        return str(value)


class ExtractedSteps(BaseModel):
    """Structured envelope returned by the extraction model."""

    model_config = ConfigDict(extra="forbid")

    steps: list[WorkflowStep] = Field(min_length=1)


class ConsistencyFlag(BaseModel):
    """A source-grounded action that may be missing from the extracted steps."""

    model_config = ConfigDict(extra="forbid")

    referenced_action: str = Field(min_length=1)
    evidence_quote: str = Field(min_length=1)
    likely_missing: bool


class ConsistencyCheckResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    flags: list[ConsistencyFlag] = Field(default_factory=list)


class StepScores(BaseModel):
    """The four ordinal dimensions used by the Phase 0 rubric."""

    model_config = ConfigDict(extra="forbid")

    repetitiveness: int = Field(ge=1, le=5)
    judgment_need: int = Field(ge=1, le=5)
    compliance_sensitivity: int = Field(ge=1, le=5)
    ai_suitability: int = Field(ge=1, le=5)


class StepScore(BaseModel):
    """Decision Engine output for one workflow step."""

    model_config = ConfigDict(extra="forbid")

    workflow_id: str = Field(min_length=1)
    step_id: str = Field(min_length=1)
    scores: StepScores
    reasoning: str = Field(min_length=1)
    verdict: Verdict


class DiagramNode(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    node_type: str = Field(min_length=1)


class DiagramEdge(BaseModel):
    model_config = ConfigDict(extra="ignore")

    source: str = Field(min_length=1, validation_alias=AliasChoices("source", "from"))
    target: str = Field(min_length=1, validation_alias=AliasChoices("target", "to"))
    label: str | None = None


class StaticWorkflowDiagram(BaseModel):
    model_config = ConfigDict(extra="ignore")

    nodes: list[DiagramNode] = Field(min_length=1)
    edges: list[DiagramEdge] = Field(min_length=1)


class Workflow(BaseModel):
    """A workflow and its progressively populated analysis data."""

    model_config = ConfigDict(extra="forbid")

    workflow_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    source_type: str = Field(default="uploaded_document", min_length=1)
    status: WorkflowStatus = "uploaded"
    raw_text: str | None = None
    steps: list[WorkflowStep] = Field(default_factory=list)
    consistency_flags: list[ConsistencyFlag] = Field(default_factory=list)
    scores: list[StepScore] = Field(default_factory=list)
    automation_blueprints: list["AutomationBlueprint"] = Field(default_factory=list)
    redesign_proposals: list["RedesignProposal"] = Field(default_factory=list)


class AutomationBlueprint(BaseModel):
    """Constrained conventional automation proposal for an automate step."""

    model_config = ConfigDict(extra="forbid")

    workflow_id: str = Field(min_length=1)
    step_id: str = Field(min_length=1)
    agent_name: str = Field(default="Workflow Automation Agent", min_length=1)
    current_step: WorkflowStep
    mechanism_type: Literal["rules_engine", "rpa", "scheduled_job", "existing_stp_extension"]
    trigger_condition: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    diagram: StaticWorkflowDiagram


class RedesignProposal(BaseModel):
    """Agent-first redesign proposal for a step marked ``redesign``."""

    model_config = ConfigDict(extra="forbid")

    workflow_id: str = Field(min_length=1)
    step_id: str = Field(min_length=1)
    current_step: WorkflowStep
    problem_statement: str = Field(min_length=1)
    proposed_design: str = Field(min_length=1)
    agent_responsibilities: list[str] = Field(min_length=1)
    human_controls: list[str] = Field(min_length=1)
    expected_benefits: list[str] = Field(min_length=1)
    diagram: StaticWorkflowDiagram


class ReportMetrics(BaseModel):
    total_steps: int = Field(ge=0)
    leave_as_is: int = Field(ge=0)
    automate: int = Field(ge=0)
    redesign: int = Field(ge=0)
    average_ai_suitability: float = Field(ge=0, le=5)
    average_compliance_sensitivity: float = Field(ge=0, le=5)


class ReportStepSummary(BaseModel):
    step: WorkflowStep
    score: StepScore
    automation_blueprint: AutomationBlueprint | None = None
    redesign_proposal: RedesignProposal | None = None


class ExecutiveReport(BaseModel):
    workflow_id: str = Field(min_length=1)
    workflow_name: str = Field(min_length=1)
    executive_summary: str = Field(min_length=1)
    headline_verdict: str = Field(min_length=1)
    metrics: ReportMetrics
    key_recommendations: list[str] = Field(min_length=1)
    step_summaries: list[ReportStepSummary] = Field(min_length=1)


class WorkflowSession(BaseModel):
    session_id: str = Field(min_length=1)
    workflow_id: str = Field(min_length=1)
    current_stage: str = Field(min_length=1)
    completed_step_ids: list[str] = Field(default_factory=list)
    workflow: Workflow
