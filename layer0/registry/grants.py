"""Capability-ceiling intersection at composition / activation."""

from __future__ import annotations

from typing import Iterable, Mapping

__all__ = ["CeilingViolation", "intersect_ceilings"]


class CeilingViolation(ValueError):
    def __init__(self, capability: str) -> None:
        super().__init__(f"plugin capability {capability!r} exceeds harness ceiling")
        self.capability = capability


def intersect_ceilings(
    harness: Iterable[Mapping[str, object]],
    plugin: Iterable[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    allowed = {(str(item.get("verb")), _freeze(item.get("selector"))) for item in harness}
    granted = []
    for item in plugin:
        key = (str(item.get("verb")), _freeze(item.get("selector")))
        if key not in allowed and allowed:
            raise CeilingViolation(str(item.get("verb")))
        granted.append(dict(item))
    return tuple(granted)


def _freeze(value: object) -> str:
    return repr(value)
