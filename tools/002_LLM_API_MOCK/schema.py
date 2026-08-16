"""Scenario schema validation for LAM benchmark corpus."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

ALLOWED_ATOMS = ("view_file", "edit_file", "run_command", "grep_file", "list_dir")


def validate_scenario(raw: Mapping[str, Any], allowed_atoms: Sequence[str] = ALLOWED_ATOMS) -> None:
    """Validate a scenario dict against the strict LAM benchmark corpus schema."""
    if not isinstance(raw, dict):
        raise ValueError("Scenario must be a dictionary")

    scenario_id = raw.get("id") or raw.get("key")
    if not scenario_id or not isinstance(scenario_id, str):
        raise ValueError("Scenario missing valid 'id' string")

    if not re.match(r"^t[1-5]-", scenario_id):
        raise ValueError(f"Scenario id '{scenario_id}' must match pattern '^t[1-5]-'")

    tier = raw.get("tier")
    if tier is not None:
        if not isinstance(tier, int) or tier < 1 or tier > 6:
            raise ValueError(f"Scenario tier '{tier}' must be an integer 1..6")

    workspace = raw.get("workspace")
    if workspace is not None:
        if not isinstance(workspace, dict):
            raise ValueError("Scenario 'workspace' must be a map of relative file paths")
        for path_str in workspace.keys():
            if ".." in path_str or path_str.startswith("/"):
                raise ValueError(f"Invalid workspace relative path '{path_str}'")

    turns = raw.get("turns")
    if not isinstance(turns, list) or not turns:
        raise ValueError("Scenario must contain a non-empty 'turns' array")

    has_stop = False
    prev_tool_count = 0

    for idx, turn in enumerate(turns):
        if not isinstance(turn, dict):
            raise ValueError(f"Turn {idx} must be a dictionary")

        finish_reason = turn.get("finish_reason")
        if finish_reason == "stop":
            has_stop = True

        tool_calls = turn.get("tool_calls", [])
        if not isinstance(tool_calls, list):
            raise ValueError(f"Turn {idx} 'tool_calls' must be a list")

        for tc in tool_calls:
            func = tc.get("function", {})
            name = func.get("name")
            if name not in allowed_atoms:
                raise ValueError(f"Turn {idx} tool call '{name}' not in allowed atoms {allowed_atoms}")

        tool_messages = turn.get("tool_messages_seen", idx)
        if isinstance(tool_messages, int):
            if tool_messages < prev_tool_count:
                raise ValueError(f"Turn {idx} tool_messages_seen must be monotonically non-decreasing")
            prev_tool_count = tool_messages

    if not has_stop:
        raise ValueError("Scenario must contain at least one turn with finish_reason='stop'")
