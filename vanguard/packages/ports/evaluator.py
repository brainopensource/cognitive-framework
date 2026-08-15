"""EvaluatorPort interface.

Owning contract: ICD §4 EvaluatorPort, REQ-PORT-004, ADR-0048.
Invariants:
- Agency has no import path here.
- Fail-closed: instrument errors become inconclusive verdicts, not task passes.
- Zero concrete implementation in this package.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence

from .event_store import Result

__all__ = [
    "RunRef",
    "EvaluationProtocol",
    "Verdict",
    "EvaluatorPort",
]


@dataclass(frozen=True, slots=True)
class RunRef:
    """Identity of a completed run presented to an exterior evaluator."""

    run_id: str
    episode_id: str | None = None


@dataclass(frozen=True, slots=True)
class EvaluationProtocol:
    """Named evaluation procedure. OS isolation of the evaluator is Sprint 5."""

    name: str
    parameters: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Verdict:
    """Fail-closed evaluation outcome."""

    outcome: str  # "claims" | "inconclusive"
    claims: tuple[Mapping[str, Any], ...] = ()
    reason: str = ""


class EvaluatorPort(Protocol):
    """Exterior evaluation. Agency must not import this module."""

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        """Return fixed claims, or an inconclusive verdict on instrument error."""
        ...
