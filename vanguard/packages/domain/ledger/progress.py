"""Pure M-6.5 progress and confidence projections.

These types derive observations from ledger events. They do not emit events,
invoke models, grant authority, or make scheduling decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from ..canonicalisation.digest import digest_of

__all__ = ["ConfidenceRecord", "ProgressView", "fold_progress"]


@dataclass(frozen=True, slots=True)
class ConfidenceRecord:
    signal: str
    value: float
    subject_ref: str
    basis: tuple[str, ...] = ()
    calibration: Mapping[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.signal not in {"self_report", "logprob", "behavioral", "external_verifier", "ensemble_disagreement"}:
            raise ValueError("unsupported confidence signal")
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("confidence value must be between 0 and 1")
        if not self.subject_ref:
            raise ValueError("confidence subject_ref is required")
        if self.calibration is None:
            object.__setattr__(self, "calibration", {})

    def digest(self) -> str:
        return digest_of({"signal": self.signal, "value": self.value,
                          "subjectRef": self.subject_ref, "basis": self.basis,
                          "calibration": dict(self.calibration or {})})


@dataclass(frozen=True, slots=True)
class ProgressView:
    assessment: str | None = None
    stall_count: int = 0
    repeat_signatures: tuple[str, ...] = ()
    budget_burn_rate: float = 0.0
    last_change: str | None = None

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
