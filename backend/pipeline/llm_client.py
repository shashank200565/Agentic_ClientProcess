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

# OpenCode Go exposes different wire protocols by model family. Keep this
# mapping here so pipeline stages only provide a model name.
MODEL_PROTOCOL_PREFIXES = {
    "responses": ("gpt-", "grok-"),
    "chat_completions": ("glm-", "deepseek-"),
}


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
        "gpt 5.6 luna": "gpt-5.6-luna",
        "gpt-5.6 luna": "gpt-5.6-luna",
    }
    return known_model_ids.get(model.strip().lower(), model)


def _protocol_for_model(model: str) -> str:
    normalized_model = model.strip().lower()
    for protocol, prefixes in MODEL_PROTOCOL_PREFIXES.items():
        if normalized_model.startswith(prefixes):
            return protocol
    return "chat_completions"


def _decode_structured_response(envelope: dict[str, Any], protocol: str) -> Any:
    def parse_json_text(text: str) -> Any:
        normalized = text.strip()
        if normalized.startswith("```"):
            normalized = normalized.split("\n", 1)[1]
            if normalized.rstrip().endswith("```"):
                normalized = normalized.rstrip()[:-3].rstrip()
        return json.loads(normalized)

    try:
        if protocol == "responses":
            output_text = envelope.get("output_text")
            if not isinstance(output_text, str):
                text_parts = [
                    part["text"]
                    for item in envelope["output"]
                    for part in item.get("content", [])
                    if isinstance(part.get("text"), str)
                ]
                output_text = "".join(text_parts)
            if not output_text:
                raise KeyError("output[].content[].text")
            return parse_json_text(output_text)

        content = envelope["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(
                part["text"]
                for part in content
                if isinstance(part, dict) and isinstance(part.get("text"), str)
            )
        return parse_json_text(content) if isinstance(content, str) else content
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise LLMClientError(
            f"OpenCode Go returned an invalid structured {protocol} response"
        ) from exc


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
    selected_model = _provider_model(model or get_extraction_model())
    protocol = _protocol_for_model(selected_model)
    endpoint_suffix = "/responses" if protocol == "responses" else "/chat/completions"
    endpoint = base_url if base_url.endswith(endpoint_suffix) else f"{base_url}{endpoint_suffix}"
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    if protocol == "responses":
        payload = {
            "model": selected_model,
            "input": messages,
            "text": {"format": {"type": "json_object"}},
        }
    else:
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
        decoded = _decode_structured_response(envelope, protocol)
    except json.JSONDecodeError as exc:
        raise LLMClientError("OpenCode Go returned an invalid JSON envelope") from exc

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
