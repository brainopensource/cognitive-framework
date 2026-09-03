"""Coding Max product-arm quarantine for published reports.

Forge and Chimera may remain experimental harnesses. Their scores cannot
enter a Coding Max report. Product arms are exactly the facade presets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from benchmarks.protocols import write_b20_report

__all__ = [
    "CODING_MAX_ARMS",
    "CodingMaxArmError",
    "normalize_coding_max_arm",
    "assert_coding_max_arms",
    "write_coding_max_report",
]

CODING_MAX_ARMS = frozenset({"vg-code-fast", "vg-code-balanced", "vg-code-max"})
_SHORT_PRESETS = {
    "fast": "vg-code-fast",
    "balanced": "vg-code-balanced",
    "max": "vg-code-max",
}


class CodingMaxArmError(ValueError):
    """A report tried to treat Forge/Chimera as a Coding Max product arm."""


def normalize_coding_max_arm(name: str) -> str:
    raw = str(name or "").strip()
    if raw in _SHORT_PRESETS:
        return _SHORT_PRESETS[raw]
    if raw.startswith("vg-code-") and raw[8:] in _SHORT_PRESETS:
        return raw
    return raw


def assert_coding_max_arms(arms: Iterable[str]) -> tuple[str, ...]:
    """Refuse any arm outside ``{vg-code-fast, vg-code-balanced, vg-code-max}``."""
    normalized: list[str] = []
    seen: set[str] = set()
    for arm in arms:
        name = normalize_coding_max_arm(arm)
        if name not in CODING_MAX_ARMS:
            raise CodingMaxArmError(
                f"Forge/Chimera scores cannot enter Coding Max reports: {arm}"
            )
        if name not in seen:
            seen.add(name)
            normalized.append(name)
    return tuple(normalized)


def write_coding_max_report(
    path: Path | None,
    *,
    subject_sha: str,
    arms: Sequence[str],
    results: Sequence[Mapping[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Write a Coding Max report after quarantining non-product arms."""
    normalized_arms = list(assert_coding_max_arms(arms))
    rows = [dict(row) for row in (results or [])]
    for row in rows:
        harness = row.get("harness") or row.get("preset") or row.get("arm")
        if harness and normalize_coding_max_arm(str(harness)) not in CODING_MAX_ARMS:
            raise CodingMaxArmError(
                f"Forge/Chimera scores cannot enter Coding Max reports: {harness}"
            )
    payload = write_b20_report(
        None,
        subject_sha=subject_sha,
        results=rows,
        **kwargs,
    )
    payload["arms"] = normalized_arms
    if path is not None:
        Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload
