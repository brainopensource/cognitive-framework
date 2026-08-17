"""Pre-registration schema, hashing, and execution lifecycle (S9-C-02).

Owning contract: VG-07 §5.7, REQ-BENCH-001.

Ensures hypotheses, metrics, alpha, stopping rules, and manifest digests
are cryptographically committed before any experimental arm executes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of


class PreregistrationStatus(str, Enum):
    PREREGISTERED = "preregistered_not_executed"
    EXECUTED_LAB = "executed-lab"
    EXECUTED_LIVE = "executed-live"
    REJECTED = "rejected"


class PreregistrationError(ValueError):
    """Raised when pre-registration verification fails or un-hashed arm runs are attempted."""
    pass


@dataclass
class Preregistration:
    """Immutable scientific hypothesis and experimental plan."""

    preregistration_id: str
    hypotheses: Sequence[str]
    primary_metric: str
    alpha: float
    correction: str
    manifest_digests: Mapping[str, str]
    model_id: str
    stopping_rule: str
    corpus_split_ids: Sequence[str]
    instrument_error_policy: str
    created_at: str
    backend: str = "mock"
    status: PreregistrationStatus = PreregistrationStatus.PREREGISTERED
    run_ids: list[str] = field(default_factory=list)

    def compute_hash(self) -> str:
        """Compute canonical SHA-256 hash of the frozen scientific commitments."""
        payload = {
            "preregistrationId": self.preregistration_id,
            "hypotheses": list(self.hypotheses),
            "primaryMetric": self.primary_metric,
            "alpha": self.alpha,
            "correction": self.correction,
            "manifestDigests": dict(sorted(self.manifest_digests.items())),
            "modelId": self.model_id,
            "stoppingRule": self.stopping_rule,
            "corpusSplitIds": list(self.corpus_split_ids),
            "instrumentErrorPolicy": self.instrument_error_policy,
            "createdAt": self.created_at,
            "backend": self.backend,
        }
        return digest_of(payload)

    def verify_prior_hash(self, expected_hash: str) -> bool:
        """Verify that the active preregistration matches an expected/prior committed hash."""
        return self.compute_hash() == expected_hash

    def mark_executed(self, run_id: str, is_live: bool = False) -> None:
        """Transition status from preregistered to executed with attached run ID."""
        if self.status == PreregistrationStatus.REJECTED:
            raise PreregistrationError("Cannot execute against a rejected preregistration")
        self.status = PreregistrationStatus.EXECUTED_LIVE if is_live else PreregistrationStatus.EXECUTED_LAB
        if run_id not in self.run_ids:
            self.run_ids.append(run_id)

    def to_dict(self) -> dict[str, Any]:
        return {
            "preregistrationId": self.preregistration_id,
            "hash": self.compute_hash(),
            "hypotheses": list(self.hypotheses),
            "primaryMetric": self.primary_metric,
            "alpha": self.alpha,
            "correction": self.correction,
            "manifestDigests": dict(self.manifest_digests),
            "modelId": self.model_id,
            "stoppingRule": self.stopping_rule,
            "corpusSplitIds": list(self.corpus_split_ids),
            "instrumentErrorPolicy": self.instrument_error_policy,
            "createdAt": self.created_at,
            "backend": self.backend,
            "status": self.status.value,
            "runIds": list(self.run_ids),
        }
