"""OpenAI-compatible OpenRouter adapter for ModelPort.

Owning contract: REQ-PORT-006, T2.7, CT-33, ADR-0047.
Never import `slice/` or `spike/`. Secrets are references, never stored values.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Mapping, Sequence

from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas
from .cassette import Cassette, CassettePlayer, CassetteRecorder

__all__ = [
    "OpenRouterModel",
    "DEFAULT_ENDPOINT",
    "DEFAULT_KEY_REF",
    "DEFAULT_MODEL",
]

DEFAULT_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_KEY_REF = "OPENROUTER_API_KEY"
DEFAULT_MODEL = "openai/gpt-4o-mini"

Transport = Callable[[str, dict[str, str], bytes], tuple[int, bytes]]


def _http_post(url: str, headers: dict[str, str], body: bytes) -> tuple[int, bytes]:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return int(response.status), response.read()
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read() or b""


def _redact(text: str, secret: str | None, ref: str) -> str:
    if secret:
        return text.replace(secret, ref)
    return text


def _messages(context: ContextBundle) -> list[dict[str, Any]]:
    if "messages" in context:
        return [dict(item) for item in context["messages"]]
    messages: list[dict[str, Any]] = []
    system = context.get("system")
    if isinstance(system, str) and system:
        messages.append({"role": "system", "content": system})
    for block in context.get("blocks") or ():
        label = block.get("label", "")
        content = block.get("content", "")
        messages.append({"role": "user", "content": f"[{label}] {content}"})
    for item in context.get("history") or ():
        if isinstance(item, str):
            messages.append({"role": "user", "content": item})
        elif isinstance(item, Mapping):
            messages.append(dict(item))
    if not messages:
        messages.append({"role": "user", "content": ""})
    return messages


def _tools_payload(tools: ToolSchemas) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for tool in tools:
        payload.append(
            {
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "parameters": tool.get("schema") or {"type": "object"},
                },
            }
        )
    return payload


def _parse_proposal(body: Mapping[str, Any]) -> Proposal | None:
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    if not isinstance(first, Mapping):
        return None
    message = first.get("message")
    if not isinstance(message, Mapping):
        return None
    text = message.get("content")
    if text is None:
        text = ""
    if not isinstance(text, str):
        return None
    tool_calls: list[dict[str, Any]] = []
    raw_calls = message.get("tool_calls") or ()
    for raw in raw_calls:
        if not isinstance(raw, Mapping):
            continue
        function = raw.get("function") if isinstance(raw.get("function"), Mapping) else {}
        arguments: Any = function.get("arguments", {})
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {"raw": arguments}
        tool_calls.append(
            {
                "id": str(raw.get("id", "")),
                "name": str(function.get("name", "")),
                "arguments": arguments if isinstance(arguments, Mapping) else {},
            }
        )
    return {"text": text, "toolCalls": tool_calls}


class OpenRouterModel:
    """Live or cassette-backed ModelPort. Trust-spine tests must not construct this."""

    def __init__(
        self,
        *,
        api_key_ref: str = DEFAULT_KEY_REF,
        endpoint: str = DEFAULT_ENDPOINT,
        model: str = DEFAULT_MODEL,
        cassette: Cassette | None = None,
        mode: str = "live",
        transport: Transport | None = None,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        self.api_key_ref = api_key_ref
        self._endpoint = endpoint
        self._model = model
        self._mode = mode
        self._transport = transport
        self._environ = dict(environ) if environ is not None else None
        self._player = (
            CassettePlayer(cassette, match_mode="tape")
            if cassette is not None and mode == "replay"
            else None
        )
        self._recorder = (
            CassetteRecorder(cassette)
            if cassette is not None and mode == "record"
            else None
        )

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        if self._player is not None:
            return self._player.propose(context, tools, sampling)
        return self._complete(context, tools, sampling)

    def _lookup_secret(self) -> str | None:
        if self._environ is not None:
            value = self._environ.get(self.api_key_ref)
        else:
            value = os.environ.get(self.api_key_ref)
        return value if value else None

    def _complete(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        secret = self._lookup_secret()
        if secret is None:
            return Result.fail(
                kind="instrument_error",
                message=f"secret reference {self.api_key_ref} is unset",
            )
        body_obj: dict[str, Any] = {
            "model": self._model,
            "messages": _messages(context),
            "temperature": sampling.get("temperature", 0.0),
            "max_tokens": sampling.get("maxTokens", 256),
        }
        tool_payload = _tools_payload(tools)
        if tool_payload:
            body_obj["tools"] = tool_payload
        payload = json.dumps(body_obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {secret}",
        }
        transport = self._transport or _http_post
        try:
            status, raw = transport(self._endpoint, headers, payload)
        except Exception as exc:
            return Result.fail(
                kind="instrument_error",
                message=_redact(f"provider request failed: {exc}", secret, self.api_key_ref),
                retryable=True,
            )
        decoded = raw.decode("utf-8", "replace")
        if status != 200:
            return Result.fail(
                kind="instrument_error",
                message=_redact(f"provider returned HTTP {status}", secret, self.api_key_ref),
                retryable=status == 429 or status >= 500,
            )
        try:
            parsed = json.loads(decoded)
        except json.JSONDecodeError:
            return Result.fail(
                kind="instrument_error",
                message="provider response was not JSON",
            )
        if not isinstance(parsed, Mapping):
            return Result.fail(kind="instrument_error", message="provider response was not an object")
        proposal = _parse_proposal(parsed)
        if proposal is None:
            return Result.fail(
                kind="instrument_error",
                message="provider response did not contain a chat completion",
            )
        if self._recorder is not None:
            self._recorder.record_interaction(context, tools, sampling, proposal)
        return Result.success(proposal)
