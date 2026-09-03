"""Local Ollama ModelPort adapter with the same canonical proposal path."""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Callable, Mapping, Sequence

from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas
from .invocation import ProposalTranslator
from .dialect import ModelIntent, compile_intent
from ...domain.models.profile import profile_for

Transport = Callable[[str, bytes], tuple[int, bytes]]

__all__ = ["OllamaModel"]


def _tool_payload(tool: Mapping[str, Any]) -> dict[str, Any]:
    """Render a manifest tool schema in the provider's function-calling shape.

    The manifest writes `{name, verb, description, schema}`; Ollama and every
    OpenAI-compatible endpoint want `{"type": "function", "function": {name,
    description, parameters}}`. Passing the manifest shape through unchanged
    produced `HTTP 500` on every request, which surfaced as
    `instrument_error: model_not_invoked` -- a live model that was never
    actually asked anything.

    A tool already in provider shape is passed through, so a pack may supply
    either.
    """
    if isinstance(tool.get("function"), Mapping):
        return dict(tool)
    parameters = tool.get("schema") or tool.get("parameters") or {
        "type": "object", "properties": {}}
    return {
        "type": "function",
        "function": {
            "name": str(tool.get("name") or tool.get("verb") or ""),
            "description": str(tool.get("description") or ""),
            "parameters": dict(parameters),
        },
    }


class OllamaModel:
    def __init__(
        self,
        *,
        model: str,
        endpoint: str = "http://127.0.0.1:11434/api/chat",
        transport: Transport | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.model = model
        self.endpoint = endpoint
        self._transport = transport or (
            lambda endpoint, body, _timeout=timeout_seconds: _http_transport(
                endpoint, body, timeout=_timeout)
        )
        self.timeout_seconds = timeout_seconds

    @property
    def capability_profile(self):
        return profile_for(self.model)

    provider = "ollama"
    mode = "live"

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        if not self.model:
            return Result.fail("instrument_error", "Ollama model is required")
        options = dict(sampling)
        if "num_ctx" not in options:
            options["num_ctx"] = 4096
        if "maxTokens" not in options and "num_predict" not in options:
            options["num_predict"] = 1024
        if "maxTokens" in options and "num_predict" not in options:
            options["num_predict"] = options.pop("maxTokens")
        dialect = compile_intent(
            ModelIntent(system="", messages=tuple(_messages(context)),
                        tools=tuple(tools), sampling=options),
            self.capability_profile,
        )
        body: dict[str, Any] = {
            "model": self.model,
            "messages": list(dialect.messages),
            "stream": False,
            "options": dict(dialect.sampling),
        }
        if dialect.tools:
            body["tools"] = list(dialect.tools)
        try:
            status, raw = self._transport(self.endpoint, json.dumps(body, separators=(",", ":")).encode("utf-8"))
        except Exception as exc:
            return Result.fail("instrument_error", f"Ollama request failed: {exc}", retryable=True)
        if status != 200:
            detail = raw.decode("utf-8", errors="replace").strip()[:512]
            suffix = f": {detail}" if detail else ""
            return Result.fail(
                "instrument_error",
                f"Ollama returned HTTP {status}{suffix}",
                retryable=status in {429, 500, 502, 503, 504},
            )
        try:
            payload = json.loads(raw.decode("utf-8"))
            message = payload.get("message")
            if not isinstance(message, Mapping):
                raise ValueError("missing message")
            calls = []
            for call in message.get("tool_calls") or ():
                if not isinstance(call, Mapping):
                    raise ValueError("malformed tool call")
                function = call.get("function")
                if not isinstance(function, Mapping):
                    raise ValueError("malformed tool function")
                calls.append({
                    "id": call.get("id"),
                    "name": function.get("name"),
                    "arguments": function.get("arguments", {}),
                })
            proposal = {
                "text": str(message.get("content") or ""),
                "toolCalls": calls,
                "resolved_model": str(payload.get("model") or self.model),
                "pricing_known": False,
                "pricing_source": "unknown",
                "usd_micros": 0,
                "usage": {
                    "prompt_tokens": _integer(payload.get("prompt_eval_count", 0)),
                    "completion_tokens": _integer(payload.get("eval_count", 0)),
                    "usd_micros": 0,
                    "pricing_known": False,
                },
            }
        except (UnicodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            return Result.fail("instrument_error", f"malformed Ollama response: {exc}")
        return ProposalTranslator.translate(proposal, tool_schemas=tools)


def _messages(context: ContextBundle) -> list[dict[str, str]]:
    if isinstance(context, Mapping):
        if isinstance(context.get("messages"), Sequence):
            return [
                {"role": str(item.get("role", "user")), "content": str(item.get("content", ""))}
                for item in context["messages"] if isinstance(item, Mapping)
            ]
        if isinstance(context.get("blocks"), Sequence):
            sys_parts = []
            usr_parts = []
            for b in context["blocks"]:
                if isinstance(b, Mapping):
                    lbl = str(b.get("label", ""))
                    cnt = str(b.get("content", ""))
                    if lbl in {"L0", "L1", "system"}:
                        sys_parts.append(cnt)
                    else:
                        usr_parts.append(cnt)
            res = []
            if sys_parts:
                res.append({"role": "system", "content": "\n\n".join(sys_parts)})
            if usr_parts:
                res.append({"role": "user", "content": "\n\n".join(usr_parts)})
            return res or [{"role": "user", "content": str(context)}]
    return [{"role": "user", "content": str(context)}]


def _integer(value: Any) -> int:
    return value if type(value) is int and value >= 0 else 0


def _http_transport(endpoint: str, body: bytes, timeout: float = 60.0) -> tuple[int, bytes]:
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return int(response.status), response.read(16 * 1024 * 1024 + 1)
