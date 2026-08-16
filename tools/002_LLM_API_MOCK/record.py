"""Record live OpenRouter traces into reproducible LAM scenarios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from schema import validate_scenario


def sanitize_secrets(text: str) -> str:
    """Redact keys, tokens, and environment secrets from text."""
    import re
    cleaned = re.sub(r"(sk-[a-zA-Z0-9]{32,})", "[REDACTED_API_KEY]", text)
    cleaned = re.sub(r"(OPENROUTER_API_KEY=)[^\s]+", r"\1[REDACTED]", cleaned)
    return cleaned


def trace_to_scenario(
    scenario_id: str,
    tier: int,
    workspace: Mapping[str, str],
    captures: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Convert captured turn messages into a validated scenario dictionary."""
    turns: list[dict[str, Any]] = []

    for idx, cap in enumerate(captures):
        tool_calls = cap.get("tool_calls", [])
        finish_reason = "stop" if idx == len(captures) - 1 else "tool_calls"

        sanitized_calls: list[dict[str, Any]] = []
        for tc in tool_calls:
            func = tc.get("function", {})
            name = func.get("name", "view_file")
            args_raw = func.get("arguments", "{}")
            if isinstance(args_raw, str):
                args_san = sanitize_secrets(args_raw)
                args_obj = json.loads(args_san)
            else:
                args_obj = args_raw

            sanitized_calls.append({
                "type": "function",
                "function": {
                    "name": name,
                    "arguments": json.dumps(args_obj, sort_keys=True),
                },
            })

        turns.append({
            "tool_messages_seen": idx,
            "tool_calls": sanitized_calls,
            "finish_reason": finish_reason,
        })

    scenario = {
        "id": scenario_id,
        "tier": tier,
        "workspace": dict(workspace),
        "turns": turns,
    }

    validate_scenario(scenario)
    return scenario
