"""Local Ollama ModelPort adapter with the same canonical proposal path."""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Callable, Mapping, Sequence

from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas
from .invocation import ProposalTranslator

Transport = Callable[[str, bytes], tuple[int, bytes]]

__all__ = ["OllamaModel"]


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
        self._transport = transport or _http_transport
        self.timeout_seconds = timeout_seconds

    def propose(
        self,
        context: ContextBundle,
        tools: ToolSchemas,
        sampling: Sampling,
    ) -> Result[Proposal]:
        if not self.model:
            return Result.fail("instrument_error", "Ollama model is required")
        body = {
            "model": self.model,
            "messages": _messages(context),
            "tools": [dict(tool) for tool in tools],
            "stream": False,
            "options": dict(sampling),
        }
        try:
            status, raw = self._transport(self.endpoint, json.dumps(body, separators=(",", ":")).encode("utf-8"))
        except Exception as exc:
            return Result.fail("instrument_error", f"Ollama request failed: {exc}", retryable=True)
        if status != 200:
            return Result.fail("instrument_error", f"Ollama returned HTTP {status}", retryable=status in {429, 500, 502, 503, 504})
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
    if isinstance(context, Mapping) and isinstance(context.get("messages"), Sequence):
        return [
            {"role": str(item.get("role", "user")), "content": str(item.get("content", ""))}
            for item in context["messages"] if isinstance(item, Mapping)
        ]
    return [{"role": "user", "content": str(context)}]


def _integer(value: Any) -> int:
    return value if type(value) is int and value >= 0 else 0


def _http_transport(endpoint: str, body: bytes) -> tuple[int, bytes]:
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60.0) as response:
        return int(response.status), response.read(16 * 1024 * 1024 + 1)
