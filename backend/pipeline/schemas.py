from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class Workflow(BaseModel):
    """A workflow and its progressively populated analysis data."""

    model_config = ConfigDict(extra="forbid")

    workflow_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    source_type: str = Field(default="uploaded_document", min_length=1)
    status: WorkflowStatus = "uploaded"
    raw_text: str | None = None
    steps: list[WorkflowStep] = Field(default_factory=list)
    scores: list[StepScore] = Field(default_factory=list)


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
