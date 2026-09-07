from __future__ import annotations

try:
    from backend.pipeline.llm_client import call_llm, get_extraction_model
    from backend.pipeline.schemas import ExtractedSteps, WorkflowStep
except ModuleNotFoundError:  # Supports the documented `cd backend` launch.
    from pipeline.llm_client import call_llm, get_extraction_model
    from pipeline.schemas import ExtractedSteps, WorkflowStep


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
    )
    if not isinstance(result, ExtractedSteps):
        raise TypeError("Extraction client returned an unexpected response type")
    return result.steps
