"""Pure M-6.5 progress and confidence projections.

These types derive observations from ledger events. They do not emit events,
invoke models, grant authority, or make scheduling decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from ..canonicalisation.digest import digest_of

__all__ = [
    "ConfidenceRecord",
    "ProgressProjection",
    "ProgressView",
    "SemanticCheckpointRef",
    "fold_progress",
    "fold_progress_projection",
]


@dataclass(frozen=True, slots=True)
class SemanticCheckpointRef:
    """`ADR-0103`: semantic reference binding (run_id, episode_id, epoch, attempt)."""

    run_id: str
    episode_id: str
    epoch: int = 0
    attempt: int = 0

    def __post_init__(self) -> None:
        if not self.run_id or not self.episode_id:
            raise ValueError("run_id and episode_id are required")
        if self.epoch < 0 or self.attempt < 0:
            raise ValueError("epoch and attempt must be non-negative integers")

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "episodeId": self.episode_id,
            "epoch": self.epoch,
            "attempt": self.attempt,
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())


@dataclass(frozen=True, slots=True)
class ProgressProjection:
    """`ProgressProjection/2` (`ADR-0103`): derived projection from the ledger."""

    verified_delta: float = 0.0
    failed_unknown_rate: float = 0.0
    repeat_entropy: float = 0.0
    novelty: float = 0.0
    normalized_burn: float = 0.0
    revision_effectiveness: float = 0.0
    calibrated_uncertainty: float = 0.0
    schema: str = "ProgressProjection/2"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "verifiedDelta": round(self.verified_delta, 6),
            "failedUnknownRate": round(self.failed_unknown_rate, 6),
            "repeatEntropy": round(self.repeat_entropy, 6),
            "novelty": round(self.novelty, 6),
            "normalizedBurn": round(self.normalized_burn, 6),
            "revisionEffectiveness": round(self.revision_effectiveness, 6),
            "calibratedUncertainty": round(self.calibrated_uncertainty, 6),
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())



@dataclass(frozen=True, slots=True)
class ConfidenceRecord:
    signal: str
    value: float
    subject_ref: str
    basis: tuple[str, ...] = ()
    calibration: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.signal not in {"self_report", "logprob", "behavioral", "external_verifier", "ensemble_disagreement"}:
            raise ValueError("unsupported confidence signal")
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("confidence value must be between 0 and 1")
        if not self.subject_ref:
            raise ValueError("confidence subject_ref is required")
        if not self.basis or any(not isinstance(item, str) or not item for item in self.basis):
            raise ValueError("confidence evidence basis is required")
        if self.calibration is None or not isinstance(self.calibration, Mapping):
            raise ValueError("confidence calibration metadata is required")
        # Freeze the externally supplied mapping at the value boundary.  A
        # mutable calibration dict must not change a record's digest later.
        object.__setattr__(self, "calibration", dict(self.calibration))

    @property
    def subject(self) -> str:
        return self.subject_ref

    @property
    def context_epoch(self) -> int | None:
        if not self.calibration:
            return None
        epoch = self.calibration.get("contextEpoch", self.calibration.get("context_epoch"))
        return int(epoch) if epoch is not None else None

    def digest(self) -> str:
        return digest_of({"signal": self.signal, "value": self.value,
                          "subjectRef": self.subject_ref, "basis": self.basis,
                          "calibration": dict(self.calibration)})


@dataclass(frozen=True, slots=True)
class ProgressView:
    assessment: str | None = None
    stall_count: int = 0
    repeat_signatures: tuple[str, ...] = ()
    budget_burn_rate: float = 0.0
    last_change: str | None = None
    confidence_digests: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"assessment": self.assessment, "stallCount": self.stall_count,
                "repeatSignatures": self.repeat_signatures,
                "budgetBurnRate": self.budget_burn_rate,
                "lastChange": self.last_change}


def _payload(event: Mapping[str, Any]) -> Mapping[str, Any]:
    payload = event.get("payload", event)
    return payload if isinstance(payload, Mapping) else {}


def fold_progress(events: Iterable[Mapping[str, Any]]) -> ProgressView:
    """Derive progress signals deterministically from event payloads."""
    assessment: str | None = None
    stalls = 0
    repeats: list[str] = []
    last_change: str | None = None
    budgets: list[float] = []
    for event in events:
        payload = _payload(event)
        kind = str(payload.get("kind", event.get("kind", "")))
        if kind == "ProgressAssessed":
            value = payload.get("assessment")
            if isinstance(value, str):
                assessment = value
                stalls = stalls + 1 if value in {"stalled", "regressing"} else 0
            signals = payload.get("signals")
            if isinstance(signals, Mapping):
                consumed = signals.get("budgetConsumed")
                if isinstance(consumed, (int, float)) and not isinstance(consumed, bool):
                    budgets.append(float(consumed))
        elif kind == "EffectFailed":
            stalls += 1
        elif kind == "StrategyChanged":
            value = payload.get("to", payload.get("toStrategy"))
            if isinstance(value, str):
                last_change = value
        signature = payload.get("repeatSignature", payload.get("repeat_signature"))
        if isinstance(signature, str) and signature not in repeats:
            repeats.append(signature)
    rate = (budgets[-1] - budgets[0]) / (len(budgets) - 1) if len(budgets) > 1 else 0.0
    return ProgressView(assessment=assessment, stall_count=stalls,
                        repeat_signatures=tuple(repeats), budget_burn_rate=rate,
                        last_change=last_change)


def fold_progress_projection(
    events: Iterable[Mapping[str, Any]],
    confidence: Sequence[ConfidenceRecord] = (),
) -> ProgressProjection:
    """Derive `ProgressProjection/2` deterministically from events and confidence."""
    total_effects = 0
    failed_effects = 0
    descriptors: list[str] = []
    revisions = 0
    revision_successes = 0
    recent_revision = False
    budgets: list[float] = []

    for event in events:
        payload = _payload(event)
        kind = str(payload.get("kind", event.get("kind", "")))
        if kind in {"EffectCompleted", "EffectFailed", "EffectReconciled", "EffectRejected", "AuthorizationDenied"}:
            total_effects += 1
            if kind in {"EffectFailed", "EffectRejected", "AuthorizationDenied"}:
                failed_effects += 1
                recent_revision = False
            else:
                if recent_revision:
                    revision_successes += 1
                    recent_revision = False
            descriptor = payload.get("descriptorDigest", payload.get("repeatSignature"))
            if isinstance(descriptor, str):
                descriptors.append(descriptor)
        elif kind == "StrategyChanged":
            revisions += 1
            recent_revision = True
        elif kind == "ProgressAssessed":
            signals = payload.get("signals")
            if isinstance(signals, Mapping):
                consumed = signals.get("budgetConsumed")
                if isinstance(consumed, (int, float)) and not isinstance(consumed, bool):
                    budgets.append(float(consumed))

    failed_unknown_rate = (failed_effects / total_effects) if total_effects > 0 else 0.0
    unique_desc = set(descriptors)
    novelty = (len(unique_desc) / len(descriptors)) if descriptors else 1.0

    repeat_count = len(descriptors) - len(unique_desc)
    repeat_entropy = (repeat_count / len(descriptors)) if descriptors else 0.0

    normalized_burn = (budgets[-1] - budgets[0]) / (len(budgets) - 1) if len(budgets) > 1 else 0.0
    revision_eff = (revision_successes / revisions) if revisions > 0 else 1.0

    uncertainties = [1.0 - c.value for c in confidence]
    calibrated_unc = (sum(uncertainties) / len(uncertainties)) if uncertainties else 0.0

    return ProgressProjection(
        verified_delta=0.0,
        failed_unknown_rate=failed_unknown_rate,
        repeat_entropy=repeat_entropy,
        novelty=novelty,
        normalized_burn=normalized_burn,
        revision_effectiveness=revision_eff,
        calibrated_uncertainty=calibrated_unc,
    )

