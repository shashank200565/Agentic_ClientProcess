from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

try:
    from backend.pipeline.llm_client import call_llm, get_reasoning_model
except ModuleNotFoundError:
    from pipeline.llm_client import call_llm, get_reasoning_model


class ScreenAnswer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    answer: str = Field(min_length=1)


SCREEN_ASSISTANT_SYSTEM_PROMPT = """You are the on-screen assistant for an investment-management workflow diagnostic.
Answer only from the supplied screen context. This is retrieval and explanation, not a new
workflow analysis. Cite the actual step name, scores, verdict, reasoning, risk score, and
generated content when they are present. Do not invent missing facts.

If the user asks to change a verdict or asks whether a step can be automated instead, explain
the score tension explicitly. For example, say that judgment_need 4 is why the deterministic
verdict rule routes to redesign rather than automate. Never change a verdict, save a proposal,
or claim that you regenerated anything. Tell the user they can use the existing "Regenerate with
notes" action in the workflow map side panel if they want to explore an alternative design.

Keep answers concise and practical: return 2-4 short bullet points, one sentence per bullet.
Use Markdown bullets beginning with '-'. Return JSON with exactly one field: answer.
"""


def answer_screen_question(question: str, context: dict[str, Any], history: list[dict[str, str]] | None = None) -> str:
    """Answer a grounded screen question without creating a write path."""
    prompt = (
        "SCREEN CONTEXT (authoritative JSON):\n"
        f"{json.dumps(context, ensure_ascii=True, default=str)}\n\n"
        "CONVERSATION HISTORY (oldest first; use it to resolve follow-up references):\n"
        f"{json.dumps(history or [], ensure_ascii=True)}\n\n"
        f"USER QUESTION:\n{question.strip()}"
    )
    result = call_llm(
        prompt,
        model=get_reasoning_model(),
        system_prompt=SCREEN_ASSISTANT_SYSTEM_PROMPT,
        response_schema=ScreenAnswer,
        temperature=0.0,
    )
    return result.answer
