"""Attribute prompt-prefix misses to the first changed cache layer."""

from __future__ import annotations

from typing import Any, Mapping

from .cache_replay import prefix_digest


def prefix_miss_reason(previous: Mapping[str, Any], current: Mapping[str, Any]) -> str:
    """Return ``hit`` or the first changed V5-L layer."""
    layers = (
        ("system", "system"),
        ("tools", "tools"),
        ("compact", "compact"),
        ("snip", "snip"),
    )
    for reason, key in layers:
        if previous.get(key) != current.get(key):
            return reason
    return "hit"


def attribute_call(previous: Mapping[str, Any], current: Mapping[str, Any]) -> dict[str, Any]:
    reason = prefix_miss_reason(previous, current)
    return {
        "prefixDigest": prefix_digest({"context": current.get("context", current), "tools": current.get("tools", [])}),
        "prefixMissReason": reason,
        "cacheHit": reason == "hit",
    }
