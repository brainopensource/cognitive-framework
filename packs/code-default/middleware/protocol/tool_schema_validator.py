"""Validates tool arguments against standard expected schemas."""

from __future__ import annotations

from typing import Any, Mapping


def validate_tool_arguments(action: str, args: Mapping[str, Any]) -> list[str]:
    """Return a list of validation errors if tool arguments violate expected schemas."""
    errors: list[str] = []
    if not isinstance(args, Mapping):
        return ["arguments must be an object"]

    if action in {"fs.read", "read_file"}:
        if "path" not in args and "file_path" not in args and "filepath" not in args:
            errors.append("missing required argument 'path'")
    elif action in {"patch.apply", "apply_patch"}:
        if "patch" not in args and "diff" not in args and "patch_content" not in args:
            errors.append("missing required argument 'patch' or 'diff'")
    elif action in {"proc.exec", "execute_command"}:
        if "command" not in args and "argv" not in args and "cmd" not in args:
            errors.append("missing required argument 'command' or 'argv'")
    elif action in {"fs.search", "grep_search", "find_files"}:
        if "pattern" not in args and "query" not in args:
            errors.append("missing required argument 'pattern' or 'query'")

    return errors
