"""Effect reconciliation by idempotency key.

Owning contract: VG-04 §12.2 / §12.4, GTS-13C T3.7.

Invariants:
- Where occurrence cannot be determined, the record says `undeterminable` and STAYS that way.
- Never assume an in-flight effect succeeded or failed without definitive proof.
- Preserved uncertainty metadata records exact scope and reason.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional

from ..domain.canonicalisation.digest import digest_of
from ..domain.ledger.events import EventEnvelope

__all__ = [
    "ReconciliationVerdict",
    "EffectReconciler",
]


@dataclass(frozen=True, slots=True)
class ReconciliationVerdict:
    """Verdict of an effect reconciliation attempt."""

    descriptor_digest: str
    idempotency_key: str
    status: str  # "confirmed" | "undeterminable"
    uncertainty: Optional[Mapping[str, Any]] = None
    receipt_digest: Optional[str] = None


class EffectReconciler:
    """Reconciles interrupted or crash-recovered effects against external state."""

    @staticmethod
    def reconcile(
        descriptor_digest: str,
        idempotency_key: str,
        external_receipt_digest: Optional[str] = None,
        is_definitively_confirmed: bool = False,
        uncertainty_reason: Optional[str] = None,
    ) -> ReconciliationVerdict:
        """Reconcile an effect by idempotency key.
        
        Rule (T3.7): If occurrence cannot be definitively confirmed, status is
        'undeterminable' with explicit uncertainty and remains so.
        """
        if is_definitively_confirmed and external_receipt_digest is not None:
            return ReconciliationVerdict(
                descriptor_digest=descriptor_digest,
                idempotency_key=idempotency_key,
                status="confirmed",
                receipt_digest=external_receipt_digest,
                uncertainty=None,
            )

        reason = uncertainty_reason or "Effect occurrence could not be verified after crash / restart"
        return ReconciliationVerdict(
            descriptor_digest=descriptor_digest,
            idempotency_key=idempotency_key,
            status="undeterminable",
            receipt_digest=external_receipt_digest,
            uncertainty={
                "scope": "effect_occurrence",
                "reason": reason,
            },
        )

    @staticmethod
    def build_reconciled_payload(verdict: ReconciliationVerdict) -> dict[str, Any]:
        """Produce the canonical EffectReconciled event payload dictionary."""
        payload: dict[str, Any] = {
            "kind": "EffectReconciled",
            "descriptorDigest": verdict.descriptor_digest,
            "idempotencyKey": verdict.idempotency_key,
            "status": verdict.status,
        }
        if verdict.receipt_digest is not None:
            payload["receiptDigest"] = verdict.receipt_digest
        if verdict.uncertainty is not None:
            payload["uncertainty"] = dict(verdict.uncertainty)
        return payload
