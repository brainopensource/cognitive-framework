"""Record live OpenRouter and Ollama traces into reproducible LAM scenarios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from schema import validate_scenario
from vanguard_bridge import translate_vanguard_call_to_lam


def sanitize_secrets(text: str) -> str:
    """Redact keys, tokens, and environment secrets from text."""
    import re
    cleaned = re.sub(r"(sk-[a-zA-Z0-9]{32,})", "[REDACTED_API_KEY]", text)
    cleaned = re.sub(r"(OPENROUTER_API_KEY=)[^\s]+", r"\1[REDACTED]", cleaned)
    cleaned = re.sub(r"(Bearer\s+)[^\s\"']+", r"\1[REDACTED]", cleaned)
    return cleaned


def trace_to_scenario(
    scenario_id: str,
    tier: int,
    workspace: Mapping[str, str],
    captures: Sequence[Mapping[str, Any]],
) -> Dict[str, Any]:
    """Convert captured turn messages (OpenAI or Ollama wire) into a validated scenario dictionary."""
    turns: list[dict[str, Any]] = []

    for idx, cap in enumerate(captures):
        # Support OpenAI {"tool_calls": [...]} or Ollama {"message": {"tool_calls": [...]}}
        tool_calls = cap.get("tool_calls")
        if tool_calls is None and isinstance(cap.get("message"), Mapping):
            tool_calls = cap["message"].get("tool_calls")
        if tool_calls is None:
            tool_calls = []

        content = cap.get("content")
        if content is None and isinstance(cap.get("message"), Mapping):
            content = cap["message"].get("content")
        content_str = sanitize_secrets(str(content or ""))

        finish_reason = cap.get("finish_reason")
        if finish_reason is None:
            finish_reason = "stop" if idx == len(captures) - 1 and not tool_calls else "tool_calls"

        sanitized_calls: list[dict[str, Any]] = []
        for tc in tool_calls:
            func = tc.get("function", {})
            raw_name = func.get("name", "view_file")
            args_raw = func.get("arguments", {})
            if isinstance(args_raw, str):
                args_san = sanitize_secrets(args_raw)
                try:
                    args_obj = json.loads(args_san)
                except Exception:
                    args_obj = {}
            elif isinstance(args_raw, Mapping):
                args_obj = dict(args_raw)
            else:
                args_obj = {}

            # Standardize verbs using vanguard_bridge
            lam_name, lam_args = translate_vanguard_call_to_lam(raw_name, args_obj)

            sanitized_calls.append({
                "type": "function",
                "function": {
                    "name": lam_name,
                    "arguments": json.dumps(lam_args, sort_keys=True),
                },
            })

        turn_dict: dict[str, Any] = {
            "tool_messages_seen": idx,
            "finish_reason": finish_reason,
            "tool_calls": sanitized_calls,
        }
        if content_str:
            turn_dict["content"] = content_str

        turns.append(turn_dict)

    scenario = {
        "id": scenario_id,
        "tier": tier,
        "title": f"Scenario {scenario_id}",
        "workspace": dict(workspace),
        "turns": turns,
    }

    validate_scenario(scenario)
    return scenario

