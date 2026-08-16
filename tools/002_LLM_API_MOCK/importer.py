"""Importer to convert external Claude-Code or OpenAI JSONL trajectory logs into gold LAM scenarios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping

from record import trace_to_scenario
from schema import validate_scenario

VERB_MAP = {
    "read_file": "view_file",
    "view": "view_file",
    "fs.read": "view_file",
    "write_file": "edit_file",
    "apply_diff": "edit_file",
    "edit": "edit_file",
    "patch.apply": "edit_file",
    "bash": "run_command",
    "exec": "run_command",
    "proc.exec": "run_command",
    "ls": "list_dir",
    "fs.list": "list_dir",
    "grep": "grep_file",
    "fs.search": "grep_file",
}


def import_trajectory(
    jsonl_path: Path | str,
    scenario_id: str,
    tier: int,
    title: str,
    workspace: Mapping[str, str],
) -> Dict[str, Any]:
    """Import a JSONL trajectory log and output a validated gold scenario dictionary."""
    path = Path(jsonl_path)
    if not path.is_file():
        raise FileNotFoundError(f"Trajectory JSONL missing at {path}")

    captures: List[Dict[str, Any]] = []

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except Exception:
            continue

        tool_calls = entry.get("tool_calls", [])
        mapped_calls = []

        for tc in tool_calls:
            func = tc.get("function", {})
            raw_name = func.get("name", "view_file")
            mapped_name = VERB_MAP.get(raw_name, raw_name)

            args = func.get("arguments", "{}")
            if isinstance(args, str):
                try:
                    args_obj = json.loads(args)
                except Exception:
                    args_obj = {}
            else:
                args_obj = args

            mapped_calls.append({
                "type": "function",
                "function": {
                    "name": mapped_name,
                    "arguments": json.dumps(args_obj, sort_keys=True),
                },
            })

        captures.append({"tool_calls": mapped_calls})

    if not captures:
        raise ValueError("JSONL trajectory file contained no valid tool calls")

    scenario = trace_to_scenario(scenario_id, tier, workspace, captures)
    scenario["title"] = title
    validate_scenario(scenario)
    return scenario
