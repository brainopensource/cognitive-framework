"""Pure domain state representation for the ledger.

Owning contract: VG-01 §2, VG-04 §12, GTS-13C T3.2 / T3.3.

Invariants:
- Zero I/O, zero clocks, zero randomness.
- All state structures are immutable/frozen or purely value-based.
- Canonical state dictionary for byte-reproducible digests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence

from ..canonicalisation.digest import digest_of

__all__ = [
    "LedgerState",
    "EpisodeState",
    "BudgetLeaseState",
    "EffectRecord",
    "ArtifactRecord",
    "EvidenceRecord",
    "ApprovalRecord",
    "VerdictRecord",
]


@dataclass(frozen=True, slots=True)
class EpisodeState:
    """State of an episode within the ledger."""

    run_id: Optional[str] = None
    episode_id: Optional[str] = None
    status: str = "pending"  # "pending", "active", "completed", "recovered", "aborted"
    outcome: Optional[str] = None  # "resolved", "abandoned", "denied", "inconclusive", "abstained", "recovered"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    task_spec: Optional[Mapping[str, Any]] = None
    environment_snapshot: Optional[str] = None
    state_transitions: tuple[tuple[str, str, Optional[str]], ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class BudgetLeaseState:
    """State of a budget reservation and lease."""

    lease_id: str
    dimensions: Mapping[str, int]
    limits: Mapping[str, int]
    committed_debits: Mapping[str, int] = field(default_factory=dict)
    released_unused: Mapping[str, int] = field(default_factory=dict)
    is_released: bool = False


@dataclass(frozen=True, slots=True)
class EffectRecord:
    """State record for an effect request / execution / receipt."""

    descriptor_digest: str
    sink_class: Optional[str] = None  # "pure", "observation", "privileged"
    grant_id: Optional[str] = None
    preview_summary: Optional[str] = None
    status: str = "requested"  # "previewed", "started", "completed", "reconciled"
    receipt_digest: Optional[str] = None
    outcome: Optional[str] = None  # "ok", "failed", "undeterminable"
    result_digest: Optional[str] = None
    idempotency_key: Optional[str] = None
    reconciliation_status: Optional[str] = None  # "confirmed", "undeterminable"
    uncertainty: Optional[Mapping[str, Any]] = None


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    """Competence artifact lifecycle record."""

    artifact_id: str
    kind: str  # "R", "O", "M", "P"
    version: str
    content_digest: str
    status: str = "active"  # "candidate", "active", "quarantined", "deprecated", "retired"


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Evidence claim record."""

    claim_id: str
    subject: str
    predicate: str
    value: Any
    uncertainty: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    """Human or governance approval record."""

    approval_id: str
    reason: str
    risk_tier: str
    grant_ref: Optional[str] = None
    status: str = "requested"  # "requested", "approved", "rejected"
    reviewer: Optional[str] = None


@dataclass(frozen=True, slots=True)
class VerdictRecord:
    """A signed, bound verdict as reduced from `VerdictRecorded` (ADR-0076 §5).

    The ledgered `SignedVerdict` fields verbatim, keyed by
    `evaluation_request_id` -- the same binding field a reader re-verifies on
    read (`adapters/evaluators/gate.py`). The reducer does not re-verify the
    signature (that is the reader's job) and cannot fabricate one: the only
    writer of `VerdictRecorded` (`runtime/evaluator_gateway.py`) refuses to
    ledger anything without a bound, signed body, so every record here came
    from the daemon's own signed bytes.
    """

    evaluation_request_id: str
    verdict: str  # "pass" | "fail" | "inconclusive"
    signature: str
    subject_digest: Optional[str] = None
    oracle_id: Optional[str] = None
    nonce: Optional[str] = None
    key_id: Optional[str] = None
    signed_at: Optional[str] = None
    recorded_at: Optional[str] = None


@dataclass(frozen=True, slots=True)
class LedgerState:
    """The aggregate deterministic state reduced from the event log."""

    run_id: Optional[str] = None
    episode_id: Optional[str] = None
    last_seq: Optional[str] = None
    #: SPEC §1.3: time-travel debugging is "fold to `seq=N` + resume with a
    #: divergent `branch_id`". The branch the fold most recently observed, so
    #: a resumed branch is distinguishable from the trunk in reduced state and
    #: in the state digest -- without it two folds of genuinely different
    #: histories collide. Absorbed at 2.2-A from `layer0/events/fold.py`,
    #: which was the only implementation of this law.
    branch_id: str = "main"
    event_count: int = 0
    state_version: int = 0
    episode: EpisodeState = field(default_factory=EpisodeState)
    grants: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    revoked_grants: tuple[str, ...] = field(default_factory=tuple)
    denials: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    leases: Mapping[str, BudgetLeaseState] = field(default_factory=dict)
    cumulative_budget_debits: Mapping[str, int] = field(default_factory=dict)
    effects: Mapping[str, EffectRecord] = field(default_factory=dict)
    observations: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    proposals: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    artifacts: Mapping[str, ArtifactRecord] = field(default_factory=dict)
    evidence_claims: Mapping[str, EvidenceRecord] = field(default_factory=dict)
    approvals: Mapping[str, ApprovalRecord] = field(default_factory=dict)
    heartbeats: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)
    conflicts: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    terminal_recovery: Optional[Mapping[str, Any]] = None
    #: `VerdictRecorded` reduced, keyed by `evaluation_request_id` (ADR-0076
    #: §5). A ledgered verdict is evidence, not decoration: cold replay must
    #: reconstruct it as state, not lose it to `unknown_events`.
    verdicts: Mapping[str, "VerdictRecord"] = field(default_factory=dict)
    unknown_events: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

    def to_canonical_dict(self) -> dict[str, Any]:
        """Convert state to a sorted canonical dictionary for digest computation."""
        return {
            "runId": self.run_id,
            "episodeId": self.episode_id,
            "lastSeq": self.last_seq,
            "branchId": self.branch_id,
            "eventCount": self.event_count,
            "stateVersion": self.state_version,
            "episode": {
                "runId": self.episode.run_id,
                "episodeId": self.episode.episode_id,
                "status": self.episode.status,
                "outcome": self.episode.outcome,
                "startedAt": self.episode.started_at,
                "completedAt": self.episode.completed_at,
                "environmentSnapshot": self.episode.environment_snapshot,
                "transitions": [list(t) for t in self.episode.state_transitions],
            },
            "grants": {k: dict(v) for k, v in sorted(self.grants.items())},
            "revokedGrants": sorted(self.revoked_grants),
            "denials": [dict(d) for d in self.denials],
            "leases": {
                k: {
                    "leaseId": v.lease_id,
                    "dimensions": dict(sorted(v.dimensions.items())),
                    "limits": dict(sorted(v.limits.items())),
                    "committedDebits": dict(sorted(v.committed_debits.items())),
                    "releasedUnused": dict(sorted(v.released_unused.items())),
                    "isReleased": v.is_released,
                }
                for k, v in sorted(self.leases.items())
            },
            "cumulativeBudgetDebits": dict(sorted(self.cumulative_budget_debits.items())),
            "effects": {
                k: {
                    "descriptorDigest": v.descriptor_digest,
                    "sinkClass": v.sink_class,
                    "grantId": v.grant_id,
                    "status": v.status,
                    "receiptDigest": v.receipt_digest,
                    "outcome": v.outcome,
                    "resultDigest": v.result_digest,
                    "idempotencyKey": v.idempotency_key,
                    "reconciliationStatus": v.reconciliation_status,
                    "uncertainty": dict(v.uncertainty) if v.uncertainty else None,
                }
                for k, v in sorted(self.effects.items())
            },
            "observations": [dict(o) for o in self.observations],
            "proposals": [dict(p) for p in self.proposals],
            "artifacts": {
                k: {
                    "artifactId": v.artifact_id,
                    "kind": v.kind,
                    "version": v.version,
                    "contentDigest": v.content_digest,
                    "status": v.status,
                }
                for k, v in sorted(self.artifacts.items())
            },
            "evidenceClaims": {
                k: {
                    "claimId": v.claim_id,
                    "subject": v.subject,
                    "predicate": v.predicate,
                    "value": v.value,
                    "uncertainty": dict(v.uncertainty),
                }
                for k, v in sorted(self.evidence_claims.items())
            },
            "approvals": {
                k: {
                    "approvalId": v.approval_id,
                    "reason": v.reason,
                    "riskTier": v.risk_tier,
                    "grantRef": v.grant_ref,
                    "status": v.status,
                    "reviewer": v.reviewer,
                }
                for k, v in sorted(self.approvals.items())
            },
            "heartbeats": {k: dict(v) for k, v in sorted(self.heartbeats.items())},
            "conflicts": [dict(c) for c in self.conflicts],
            "terminalRecovery": dict(self.terminal_recovery) if self.terminal_recovery else None,
            "verdicts": {
                k: {
                    "evaluationRequestId": v.evaluation_request_id,
                    "verdict": v.verdict,
                    "signature": v.signature,
                    "subjectDigest": v.subject_digest,
                    "oracleId": v.oracle_id,
                    "nonce": v.nonce,
                    "keyId": v.key_id,
                    "signedAt": v.signed_at,
                    "recordedAt": v.recorded_at,
                }
                for k, v in sorted(self.verdicts.items())
            },
            "unknownEventsCount": len(self.unknown_events),
        }

    def digest(self) -> str:
        """Compute the deterministic state digest (sha256:...)."""
        return digest_of(self.to_canonical_dict())
