from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

try:
    from backend.pipeline.llm_client import LLMClientError, call_llm, get_reasoning_model
    from backend.pipeline.schemas import StepScore, WorkflowStep
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from pipeline.llm_client import LLMClientError, call_llm, get_reasoning_model
    from pipeline.schemas import StepScore, WorkflowStep


DECISION_SYSTEM_PROMPT = """You are the Decision Engine for an investment-management workflow diagnostic.
Score the supplied current-state workflow step on each dimension from 1 to 5.
Return only a JSON object with exactly these fields: scores (an object containing
repetitiveness, judgment_need, compliance_sensitivity, and ai_suitability) and
reasoning. Do not return workflow_id, step_id, or verdict; those are supplied and
computed by the application.

Score each dimension independently. The score is 1 to 5, where 5 means high:

Repetitiveness: how frequently the step repeats the same or very similar work
across cases.
Score the repeatability of the interpretive work itself, not merely whether the
step's high-level procedural pattern appears in every case. Evidence-gathering
and analytical steps such as reviewing transaction history to determine cause
should generally score repetitiveness at 2 or below when the judgment content
differs materially case to case.
1 = rare or one-off activity; the work is materially different each time.
2 = infrequent activity with some recurring elements but substantial variation.
3 = regular activity with a mixed pattern of repeatable and variable work.
4 = frequent activity that follows a mostly repeatable pattern.
5 = high-volume activity with nearly identical steps, inputs, and outputs.

Judgment need: how much expert interpretation, ambiguity handling, negotiation, or
contextual decision-making the step requires.
Do not score synthesis or drafting steps as low judgment merely because they use a
template or recur in every case. If the step selects evidence, interprets causes,
frames a conclusion, or recommends an action for professional review, the judgment
content is material and should generally score at least 3.
1 = deterministic rule or lookup; little or no discretion is required.
2 = minor interpretation is needed, but clear rules resolve most cases.
3 = material judgment is needed in common exceptions or ambiguous cases.
4 = specialist judgment is needed for most cases and evidence must be weighed.
5 = highly contextual, strategic, or relationship-sensitive expert judgment is central.

Compliance sensitivity: the consequence and control sensitivity of an error,
including regulatory obligations, client mandates, fiduciary duties, auditability,
and financial or reputational harm.
1 = internal convenience activity with negligible compliance consequence.
2 = low-impact control or reporting activity; errors are readily corrected.
3 = material control or client-impacting activity requiring evidence and review.
4 = regulatory, mandate, fiduciary, or audit-sensitive activity with significant consequences.
5 = critical compliance or client-protection decision where an error could cause serious breach, loss, or enforcement action.

AI suitability: how much AI or agentic reasoning could materially improve the step
beyond deterministic automation, considering data availability, repeatability,
explainability, error tolerance, and human oversight.
1 = poor fit: data is unavailable or the step is too bespoke, high-risk, or judgment-heavy.
2 = limited fit: AI may assist with retrieval or drafting, but reliable execution is unlikely.
3 = conditional fit: useful with constrained scope, strong controls, and mandatory human review.
4 = good fit: structured data and repeatable reasoning support controlled automation with exception handling.
5 = strong fit: deterministic, high-volume, auditable work can be automated with low residual risk.
High AI suitability does not mean full autonomy; a step can be highly AI-suitable
and still require human approval.

Calibration: score AI suitability by the incremental value of AI reasoning beyond
what deterministic rules already achieve, not by whether an LLM is technically
capable of performing the task. Use these anchors:
- Exact field-matching against structured data, such as matching a broker
  confirmation to an internal trade record, is usually 1-2 when there is no
  interpretation of ambiguous or incomplete information; a rules engine already
  performs it reliably and more cheaply.
- Loading a portfolio snapshot, looking up a mandate limit, calculating an
  exposure percentage, comparing a threshold, or creating a fixed exception record
  is usually 1-2 when the operation is a deterministic lookup, calculation, or
  status write with no material interpretation.
- Reviewing variable transaction history, weighing evidence to determine root
  cause, or drafting a conclusion from conflicting facts can be 3-4 because AI
  reasoning may add value beyond deterministic automation, but controls and human
  review remain necessary.
Do not award a 4 or 5 merely because the step runs at high volume or an LLM could
technically execute its instructions. Reserve 5 for cases where AI reasoning adds
substantial value beyond a reliable rules engine through auditable interpretation,
exception reasoning, or evidence synthesis.

The reasoning must be at least 20 words and reference specific facts from the step
description and workflow context. Avoid generic statements.
"""


GOVERNANCE_TERMS = (
    "sign-off",
    "sign off",
    "signoff",
    "approval",
    "approve",
    "approved",
    "escalation",
    "escalate",
    "record retention",
    "retention",
)


def _workflow_id_from_context(workflow_context: str) -> str:
    match = re.search(r"(?:^|\s)workflow_id=([^\s]+)", workflow_context)
    return match.group(1) if match else "unknown"


def _is_governance_action(step: WorkflowStep) -> bool:
    # Description references can mention escalation or review incidentally. Only
    # the step's primary action name can trigger the governance override.
    text = step.name.lower()
    return any(term in text for term in GOVERNANCE_TERMS)


def _verdict_for(step: WorkflowStep, score: StepScore) -> str:
    scores = score.scores
    if (
        scores.compliance_sensitivity >= 4
        and _is_governance_action(step)
    ):
        return "leave_as_is"
    if scores.repetitiveness >= 4 and scores.judgment_need <= 2:
        return "leave_as_is" if scores.ai_suitability <= 2 else "automate"
    if scores.judgment_need >= 3 and scores.ai_suitability >= 3:
        return "redesign"
    return "automate" if scores.ai_suitability <= 2 else "redesign"


def score_step(step: WorkflowStep, workflow_context: str) -> StepScore:
    """Score one step with the reasoning model and apply the fixed verdict rule."""

    result = call_llm(
        prompt=(
            "Score this workflow step using the rubric in your system instructions. "
            "Return the nested `scores` object and a specific reasoning string.\n\n"
            f"WORKFLOW CONTEXT:\n{workflow_context}\n\n"
            f"STEP:\nname: {step.name}\ndescription: {step.description}"
        ),
        model=get_reasoning_model(),
        system_prompt=DECISION_SYSTEM_PROMPT,
        temperature=0.0,
    )
    if not isinstance(result, dict):
        raise LLMClientError("Decision Engine returned an unexpected response type")

    reasoning = result.get("reasoning")
    if not isinstance(reasoning, str) or len(reasoning.split()) < 20:
        raise LLMClientError("Decision Engine reasoning must contain at least 20 words")

    payload: dict[str, Any] = {
        **result,
        "workflow_id": _workflow_id_from_context(workflow_context),
        "step_id": step.step_id,
        "verdict": "leave_as_is",
    }
    try:
        validated = StepScore.model_validate(payload)
    except ValidationError as exc:
        raise LLMClientError(f"Decision Engine response did not match StepScore: {exc}") from exc

    return validated.model_copy(update={"verdict": _verdict_for(step, validated)})
