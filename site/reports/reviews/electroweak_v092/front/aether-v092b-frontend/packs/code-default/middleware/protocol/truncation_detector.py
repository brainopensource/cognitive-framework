"""Detects output truncated by token limits or incomplete syntax."""

from __future__ import annotations

from typing import Any, Mapping


def detect_truncation(raw_response: Any) -> bool:
    """Check if model response exhibits signs of truncation."""
    if isinstance(raw_response, Mapping):
        finish_reason = raw_response.get("finish_reason")
        if finish_reason in {"length", "max_tokens"}:
            return True
        content = raw_response.get("content") or raw_response.get("text") or ""
    elif isinstance(raw_response, str):
        content = raw_response
    else:
        return False

    if isinstance(content, str):
        content_stripped = content.rstrip()
        # Open unclosed string or unclosed json structure at end of text
        if content_stripped.count("{") > content_stripped.count("}"):
            return True
        if content_stripped.count("[") > content_stripped.count("]"):
            return True

    return False
