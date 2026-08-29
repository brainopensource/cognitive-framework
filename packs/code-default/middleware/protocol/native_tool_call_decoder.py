"""Decodes native model tool call formats into normalized proposal dictionaries."""

from __future__ import annotations

import json
from typing import Any, Mapping


def decode_native_tool_call(raw: Any) -> Mapping[str, Any] | None:
    """Extract a standard proposal dictionary from native tool call representations."""
    if not isinstance(raw, Mapping):
        return None

    # Standard Proposal dictionary already present
    if "kind" in raw and raw.get("kind") in {"effect", "finish", "abstain", "escalate", "spawn"}:
        return raw

    # OpenAI-style tool_calls: [{"id": "...", "type": "function", "function": {"name": "...", "arguments": "..."}}]
    tool_calls = raw.get("tool_calls")
    if isinstance(tool_calls, list) and tool_calls:
        first = tool_calls[0]
        if isinstance(first, Mapping):
            fn = first.get("function", {})
            name = fn.get("name") or first.get("name")
            args_raw = fn.get("arguments", {})
            if isinstance(args_raw, str):
                try:
                    args = json.loads(args_raw)
                except Exception:
                    args = {"_raw": args_raw}
            elif isinstance(args_raw, Mapping):
                args = dict(args_raw)
            else:
                args = {}
            if name:
                return {
                    "kind": "effect",
                    "action": str(name),
                    "args": args,
                    "idempotency_key": first.get("id"),
                }

    # Direct function call mapping: {"name": "...", "arguments": "..."}
    if "name" in raw and ("arguments" in raw or "args" in raw):
        name = raw["name"]
        args_raw = raw.get("arguments", raw.get("args", {}))
        if isinstance(args_raw, str):
            try:
                args = json.loads(args_raw)
            except Exception:
                args = {"_raw": args_raw}
        elif isinstance(args_raw, Mapping):
            args = dict(args_raw)
        else:
            args = {}
        return {
            "kind": "effect",
            "action": str(name),
            "args": args,
        }

    return None
