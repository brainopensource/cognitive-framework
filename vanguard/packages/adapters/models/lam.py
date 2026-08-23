"""Deterministic LAM ModelPort adapter.

LAM is an explicit mock provider. It has no session state: the accumulated
context/observation messages determine the next scenario turn.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from ...ports.event_store import Result
from ...ports.model import ContextBundle, Proposal, Sampling, ToolSchemas
from .invocation import ProposalTranslator

_TOOLS = Path(__file__).resolve().parents[4] / "tools" / "002_LLM_API_MOCK"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

try:
    from engine import LamEngine
except ImportError:  # pragma: no cover - packaging without benchmark resources
    LamEngine = None  # type: ignore[assignment,misc]

__all__ = ["LamModelAdapter"]


_DEFAULT_LAM_ALIASES = {
    "read": "fs.read",
    "search": "fs.search",
    "patch": "patch.apply",
    "test": "proc.exec",
    "Read": "fs.read",
    "Grep": "fs.search",
    "Edit": "patch.apply",
    "Bash": "proc.exec",
    "view_file": "fs.read",
    "grep_file": "fs.search",
    "edit_file": "patch.apply",
    "run_command": "proc.exec",
    "bash": "proc.exec",
    "list_dir": "fs.read",
}


class LamModelAdapter:
    """ModelPort adapter over the stateless local scenario engine."""

    def __init__(
        self,
        model_name: str = "lam/t1-calculator",
        scenario_dir: str | Path | None = None,
    ) -> None:
        self.model_name = model_name
        root = Path(scenario_dir) if scenario_dir else _TOOLS / "scenarios"
        self._engine = LamEngine.from_directory(root) if LamEngine is not None and root.is_dir() else None

    def propose(
        self,
        context: Mapping[str, Any] | Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] = (),
        sampling: Mapping[str, Any] = {},
    ) -> Result[Mapping[str, Any]]:
        del sampling
        if self._engine is None:
            return Result.fail("instrument_error", "LAM scenario directory is unavailable")

        messages = _messages_from_context(context)
        try:
            completion = self._engine.complete({
                "model": self.model_name,
                "messages": messages,
                "tools": list(tools),
            })
        except KeyError as exc:
            return Result.fail("instrument_error", f"unknown LAM scenario: {exc.args[0]}")
        except Exception as exc:
            return Result.fail("instrument_error", f"LAM completion failed: {exc}")

        choices = completion.get("choices")
        if not isinstance(choices, list) or not choices:
            return Result.fail("instrument_error", "LAM returned no choices")
        message = choices[0].get("message", {})
        if not isinstance(message, Mapping):
            return Result.fail("instrument_error", "LAM returned malformed message")

        calls = []
        for raw in message.get("tool_calls") or ():
            if not isinstance(raw, Mapping):
                return Result.fail("instrument_error", "LAM returned malformed tool call")
            function = raw.get("function")
            function = function if isinstance(function, Mapping) else raw
            calls.append({
                "id": raw.get("id"),
                "name": function.get("name", ""),
                "arguments": function.get("arguments", {}),
            })

        raw_proposal: dict[str, Any] = {
            "text": str(message.get("content") or ""),
            "toolCalls": calls,
            "resolved_model": self.model_name,
            "pricing_known": True,
            "usd_micros": 0,
        }
        return ProposalTranslator.translate(raw_proposal, tool_schemas=tools, aliases=_DEFAULT_LAM_ALIASES)


def _messages_from_context(context: ContextBundle) -> list[dict[str, str]]:
    """Convert the structural context bundle without retaining provider state."""
    messages: list[dict[str, str]] = []
    if isinstance(context, Mapping) and isinstance(context.get("layers"), Sequence):
        for layer in context["layers"]:
            if not isinstance(layer, Mapping):
                continue
            # L5 is the observation channel even though the generic context
            # compiler labels it as user dialogue for provider neutrality.
            role = "tool" if str(layer.get("layer")) == "L5" else str(layer.get("role", "user"))
            fragments = layer.get("fragments")
            if role == "tool" and isinstance(fragments, Sequence):
                for fragment in fragments:
                    if isinstance(fragment, Mapping):
                        messages.append({"role": "tool", "content": str(fragment.get("content", ""))})
                continue
            messages.append({"role": role, "content": str(layer.get("content", ""))})
        return messages
    if isinstance(context, Mapping) and isinstance(context.get("messages"), Sequence):
        for message in context["messages"]:
            if isinstance(message, Mapping):
                messages.append({"role": str(message.get("role", "user")), "content": str(message.get("content", ""))})
        return messages
    if isinstance(context, Sequence) and not isinstance(context, (str, bytes, bytearray)):
        for message in context:
            if isinstance(message, Mapping):
                messages.append({"role": str(message.get("role", "user")), "content": str(message.get("content", ""))})
        return messages
    return [{"role": "user", "content": str(context)}]
