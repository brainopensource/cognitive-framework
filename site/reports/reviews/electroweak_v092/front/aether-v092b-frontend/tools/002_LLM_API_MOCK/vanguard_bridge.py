"""Bridge between Vanguard kernel tool contracts and LAM benchmark trajectory format."""

from __future__ import annotations

import json
from typing import Any, Dict

VANGUARD_TO_LAM_VERBS = {
    "fs.read": "view_file",
    "patch.apply": "edit_file",
    "proc.exec": "run_command",
    "fs.list": "list_dir",
    "fs.search": "grep_file",
}

LAM_TO_VANGUARD_VERBS = {v: k for k, v in VANGUARD_TO_LAM_VERBS.items()}


def translate_vanguard_call_to_lam(tool_name: str, args: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Translate Vanguard kernel tool call to LAM tool call."""
    lam_name = VANGUARD_TO_LAM_VERBS.get(tool_name, tool_name)
    lam_args = dict(args)

    if tool_name == "fs.read" and "path" not in lam_args and "file" in lam_args:
        lam_args["path"] = lam_args.pop("file")
    elif tool_name == "proc.exec" and "command" not in lam_args and "cmd" in lam_args:
        lam_args["command"] = lam_args.pop("cmd")

    return lam_name, lam_args


def translate_lam_call_to_vanguard(tool_name: str, args: Dict[str, Any]) -> tuple[str, Dict[str, Any]]:
    """Translate LAM tool call to Vanguard kernel tool call."""
    vg_name = LAM_TO_VANGUARD_VERBS.get(tool_name, tool_name)
    vg_args = dict(args)

    if vg_name == "fs.read" and "file" not in vg_args and "path" in vg_args:
        vg_args["file"] = vg_args.pop("path")

    return vg_name, vg_args
