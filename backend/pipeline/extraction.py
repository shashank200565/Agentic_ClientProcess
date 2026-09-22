from __future__ import annotations

try:
    from backend.pipeline.llm_client import call_llm, get_extraction_model
    from backend.pipeline.schemas import ConsistencyCheckResult, ConsistencyFlag, ExtractedSteps, WorkflowStep
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from pipeline.llm_client import call_llm, get_extraction_model
    from pipeline.schemas import ConsistencyCheckResult, ConsistencyFlag, ExtractedSteps, WorkflowStep


EXTRACTION_SYSTEM_PROMPT = """You extract current-state investment-management workflows.
Return only JSON matching the requested schema. Preserve the actual sequence of
work, split materially different activities into separate steps, and do not
invent systems, approvals, or data that are not supported by the source text.
Each step needs a concise name and a specific description of the work performed.
"""


def extract_steps(raw_document_text: str) -> list[WorkflowStep]:
    """Extract a validated ordered step list from raw document text."""

    if not raw_document_text.strip():
        raise ValueError("Raw document text cannot be empty")
    result = call_llm(
        prompt=(
            "Extract the workflow steps from the following document. Return a "
            "JSON object with a non-empty `steps` array. Each array item must "
            "contain `step_id`, `name`, and `description`.\n\n"
            f"DOCUMENT:\n{raw_document_text}"
        ),
        model=get_extraction_model(),
        system_prompt=EXTRACTION_SYSTEM_PROMPT,
        response_schema=ExtractedSteps,
        temperature=0.0,
    )
    if not isinstance(result, ExtractedSteps):
        raise TypeError("Extraction client returned an unexpected response type")
    return result.steps


CONSISTENCY_SYSTEM_PROMPT = """You check whether an extracted workflow step list covers the source document.
Return only JSON matching the requested schema. Flag only a concrete action, handoff,
approval, escalation, review, or other workflow activity that is referenced or implied
by the source but has no corresponding extracted step. Every flag must include an exact
or near-exact quote from the source document as evidence. Do not flag context, goals,
roles, systems, or actions already adequately represented by an extracted step. When
there are no gaps, return an empty `flags` array.
"""


def check_extraction_consistency(
    raw_document_text: str,
    steps: list[WorkflowStep],
) -> list[ConsistencyFlag]:
    """Find source-grounded workflow actions not represented in the extracted steps."""

    if not raw_document_text.strip():
        raise ValueError("Raw document text cannot be empty")
    result = call_llm(
        prompt=(
            "Review the full source document against the extracted steps below. Return a "
            "JSON object with a `flags` array. Each flag must contain `referenced_action`, "
            "`evidence_quote`, and `likely_missing`. `likely_missing` must be a JSON "
            "boolean (`true` or `false`) only, with no explanation in that field.\n\n"
            "SOURCE DOCUMENT:\n"
            f"{raw_document_text}\n\nEXTRACTED STEPS:\n"
            + "\n".join(f"{step.step_id}. {step.name}: {step.description}" for step in steps)
        ),
        model=get_extraction_model(),
        system_prompt=CONSISTENCY_SYSTEM_PROMPT,
        response_schema=ConsistencyCheckResult,
        temperature=0.0,
    )
    if not isinstance(result, ConsistencyCheckResult):
        raise TypeError("Consistency client returned an unexpected response type")
    return [flag for flag in result.flags if flag.likely_missing]
