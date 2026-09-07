from __future__ import annotations

import json
import os
from uuid import uuid4
from pathlib import Path
from typing import Any, TypeVar
from urllib import error, request

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)

DEFAULT_BASE_URL = "https://opencode.ai/zen/go/v1"
DEFAULT_EXTRACTION_MODEL = "GLM-5.3-Flash"
DEFAULT_REASONING_MODEL = "GPT 5.6 Luna"


class LLMClientError(RuntimeError):
    """Raised when the OpenCode Go request or structured response fails."""


def _load_dotenv() -> None:
    """Load simple KEY=VALUE entries without overriding process environment."""

    project_root = Path(__file__).resolve().parents[2]
    candidates = (project_root / ".env", project_root / "backend" / ".env")
    for dotenv_path in candidates:
        if not dotenv_path.is_file():
            continue
        for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                os.environ.setdefault(key, value)


def get_extraction_model() -> str:
    _load_dotenv()
    return os.getenv("OPENCODE_GO_EXTRACTION_MODEL", DEFAULT_EXTRACTION_MODEL)


def get_reasoning_model() -> str:
    _load_dotenv()
    return os.getenv("OPENCODE_GO_REASONING_MODEL", DEFAULT_REASONING_MODEL)


def _provider_model(model: str) -> str:
    known_model_ids = {
        "glm-5.3-flash": "glm-5.3-flash",
        "glm 5.3 flash": "glm-5.3-flash",
    }
    return known_model_ids.get(model.strip().lower(), model)


def call_llm(
    prompt: str,
    model: str | None = None,
    *,
    system_prompt: str | None = None,
    response_schema: type[ModelT] | None = None,
    temperature: float = 0.0,
    timeout_seconds: float = 120.0,
) -> ModelT | dict[str, Any]:
    """Call the OpenCode Go OpenAI-compatible endpoint in JSON mode.

    ``response_schema`` makes the structured response boundary explicit: the
    decoded JSON is validated by the supplied Pydantic model before returning.
    """

    _load_dotenv()
    api_key = os.getenv("OPENCODE_GO_API_KEY")
    if not api_key:
        raise LLMClientError(
            "OPENCODE_GO_API_KEY is not configured in the environment or .env"
        )

    base_url = os.getenv("OPENCODE_GO_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    # The initial scaffold used the Zen URL. Keep that stale local setting from
    # routing a Go credential to the wrong gateway.
    if base_url == "https://opencode.ai/zen/v1":
        base_url = DEFAULT_BASE_URL
    endpoint = (
        base_url
        if base_url.endswith("/chat/completions")
        else f"{base_url}/chat/completions"
    )
    selected_model = _provider_model(model or get_extraction_model())
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": selected_model,
        "messages": messages,
        "temperature": temperature,
        "response_format": {"type": "json_object"},
    }
    http_request = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "AgenticWorkflowDiagnostic/0.1",
            "HTTP-Referer": "https://opencode.ai/",
            "X-Title": "Agentic Workflow Diagnostic & Redesign Platform",
            "x-opencode-session": f"ses_{uuid4().hex}",
        },
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LLMClientError(
            f"OpenCode Go request failed with HTTP {exc.code}: {body[:500]}"
        ) from exc
    except (error.URLError, TimeoutError) as exc:
        raise LLMClientError(f"OpenCode Go request failed: {exc}") from exc

    try:
        envelope = json.loads(response_body)
        content = envelope["choices"][0]["message"]["content"]
        decoded = json.loads(content) if isinstance(content, str) else content
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise LLMClientError("OpenCode Go returned an invalid JSON response") from exc

    if response_schema is None:
        if not isinstance(decoded, dict):
            raise LLMClientError("Structured LLM response must be a JSON object")
        return decoded
    try:
        return response_schema.model_validate(decoded)
    except ValidationError as exc:
        raise LLMClientError(
            f"OpenCode Go response did not match {response_schema.__name__}: {exc}"
        ) from exc
