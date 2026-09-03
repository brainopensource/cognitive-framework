"""Normalizes relaxed JSON arguments into standard JSON dictionaries."""

from __future__ import annotations

import json
import re
from typing import Any, Mapping


def normalize_json_arguments(raw_args: Any) -> tuple[dict[str, Any], bool]:
    """Attempt to parse and normalize relaxed or malformed JSON arguments.

    Returns (normalized_dict, was_repaired).
    """
    if isinstance(raw_args, dict):
        return dict(raw_args), False
    if not isinstance(raw_args, str):
        return {}, False

    stripped = raw_args.strip()
    if not stripped:
        return {}, False

    # Standard JSON parse first
    try:
        val = json.loads(stripped)
        if isinstance(val, dict):
            return val, False
    except Exception:
        pass

    # Repair: remove trailing commas before closing braces/brackets
    cleaned = re.sub(r",\s*([}\]])", r"\1", stripped)
    # Repair: replace unescaped single quotes with double quotes where possible
    if cleaned.startswith("{") and "'" in cleaned and '"' not in cleaned:
        cleaned = cleaned.replace("'", '"')

    try:
        val = json.loads(cleaned)
        if isinstance(val, dict):
            return val, True
    except Exception:
        pass

    return {"_raw": raw_args}, False
