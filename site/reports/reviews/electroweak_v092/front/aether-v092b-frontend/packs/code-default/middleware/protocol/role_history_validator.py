"""Validates role sequencing in multi-turn tool conversations."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def validate_role_history(messages: Sequence[Mapping[str, Any]]) -> list[str]:
    """Ensure message sequences satisfy tool call/response pairing invariants."""
    errors: list[str] = []
    pending_tool_call_ids: set[str] = set()

    for idx, msg in enumerate(messages):
        role = msg.get("role")
        if role == "assistant":
            tool_calls = msg.get("tool_calls")
            if isinstance(tool_calls, list):
                for tc in tool_calls:
                    if isinstance(tc, Mapping) and "id" in tc:
                        pending_tool_call_ids.add(tc["id"])
        elif role == "tool":
            tc_id = msg.get("tool_call_id")
            if not tc_id:
                errors.append(f"message[{idx}] role 'tool' missing 'tool_call_id'")
            elif tc_id in pending_tool_call_ids:
                pending_tool_call_ids.remove(tc_id)

    if pending_tool_call_ids:
        errors.append(f"unanswered tool calls: {sorted(pending_tool_call_ids)}")

    return errors
