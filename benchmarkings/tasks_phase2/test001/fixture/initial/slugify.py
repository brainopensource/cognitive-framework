"""Small public fixture for Phase 2 benchmark test001."""

from __future__ import annotations

import re


def slugify(value: str, *, max_length: int = 24) -> str:
    """Return a lowercase hyphenated identifier no longer than ``max_length``.

    Empty or punctuation-only input produces an empty identifier. The defect is
    intentionally limited to a separator at a truncation boundary.
    """
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    if not isinstance(max_length, int) or isinstance(max_length, bool) or max_length < 1:
        raise ValueError("max_length must be a positive integer")
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    normalized = normalized.strip("-")
    return normalized[:max_length]
