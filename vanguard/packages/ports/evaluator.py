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
    "PreregisteredEvaluation",
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
class PreregisteredEvaluation:
    """Immutable trust inputs supplied to the exterior evaluator."""

    preregistration_digest: str
    task_digest: str
    oracle_id: str
    oracle_digest: str
    evaluator_key_id: str
    protocol: str
    subject_digest: str


@dataclass(frozen=True, slots=True)
class Verdict:
    """Fail-closed evaluation outcome."""

    outcome: str  # "claims" | "inconclusive"
    claims: tuple[Mapping[str, Any], ...] = ()
    reason: str = ""
    signature: str | None = None
    signer_key_id: str | None = None
    #: The exact JCS-signed body the daemon produced (ADR-0076 §5): `verdict`
    #: plus `subject_digest` / `evaluation_request_id` / `oracle_id` / `nonce`
    #: / `key_id` / `signed_at`. `None` when no verdict was ever signed (no
    #: evaluator bound, or a legacy/unsigned response) -- the evaluator
    #: gateway (`runtime/evaluator_gateway.py`) refuses to ledger a
    #: `VerdictRecorded` without it, so an unsigned/unbound verdict can never
    #: reach the ledger as a pass.
    binding: Mapping[str, Any] | None = None


class EvaluatorPort(Protocol):
    """Exterior evaluation. Agency must not import this module."""

    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        """Return fixed claims, or an inconclusive verdict on instrument error."""
        ...
