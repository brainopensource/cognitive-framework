"""Exterior, deterministic checks used by the benchmark driver."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OracleResult:
    instrument_valid: bool
    fail_to_pass: bool | None
    pass_to_pass: bool | None
    no_op: bool
    reason: str | None = None


def reject_noop(before: set[str], after: set[str]) -> OracleResult:
    """Reject an empty source delta without pretending to run hidden tests."""
    changed = before != after
    return OracleResult(True, None, None, not changed, "NO_PATCH" if not changed else None)


def validate_source_delta(before: set[str], after: set[str]) -> OracleResult:
    result = reject_noop(before, after)
    if result.no_op:
        return result
    return OracleResult(True, None, None, False)


def snapshot_sources(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*.py") if p.is_file()}
