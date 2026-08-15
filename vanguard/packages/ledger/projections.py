"""Projections rebuildable from zero.

Owning contract: GTS-13C T3.4.

Invariants:
- A projection is a pure derived cache, NEVER a source of truth.
- Rebuilding a projection from sequence 0 against the EventStore
  produces an identical state and digest as incremental updates.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional, Sequence, TypeVar

from ..domain.canonicalisation.digest import digest_of
from ..domain.ledger.events import EventEnvelope
from ..domain.primitives.primitives import int_string_to_int
from ..ports.event_store import EventRange, EventStorePort

__all__ = [
    "Projection",
    "RunSummaryProjection",
    "BudgetProjection",
    "AuditProjection",
    "ArtifactRegistryProjection",
    "rebuild_projection",
]

P = TypeVar("P", bound="Projection")


class Projection(ABC):
    """Abstract base projection."""

    @abstractmethod
    def apply(self, event: EventEnvelope) -> None:
        """Incrementally apply one event to the projection cache."""
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """Export projection data as a canonical dictionary."""
        ...

    def digest(self) -> str:
        """Compute the deterministic sha256 digest of this projection's contents."""
        return digest_of(self.to_dict())


class RunSummaryProjection(Projection):
    """High-level summary of a run's lifecycle, duration, and outcome."""

    def __init__(self) -> None:
        self.run_id: Optional[str] = None
        self.episode_id: Optional[str] = None
        self.status: str = "pending"
        self.outcome: Optional[str] = None
        self.started_at: Optional[str] = None
        self.completed_at: Optional[str] = None
        self.event_count: int = 0
        self.last_seq: Optional[str] = None
        self.tool_calls_count: int = 0
        self.grants_count: int = 0
        self.denials_count: int = 0

    def apply(self, event: EventEnvelope) -> None:
        self.event_count += 1
        self.last_seq = event.seq
        if self.run_id is None and event.run_id is not None:
            self.run_id = event.run_id
        if self.episode_id is None and event.episode_id is not None:
            self.episode_id = event.episode_id

        kind = event.payload.get("kind", "")
        if kind == "EpisodeStarted":
            self.status = "active"
            self.started_at = event.occurred_at
        elif kind == "EpisodeStateChanged":
            self.status = event.payload.get("toState", self.status)
        elif kind == "EpisodeCompleted":
            self.status = "completed"
            self.outcome = event.payload.get("outcome", "resolved")
            self.completed_at = event.occurred_at
        elif kind == "RunRecovered":
            self.status = "recovered"
            self.outcome = "recovered"
            self.completed_at = event.occurred_at
        elif kind == "RunAborted":
            self.status = "aborted"
            self.outcome = "aborted"
            self.completed_at = event.occurred_at
        elif kind == "ProposalProduced":
            tool_calls = event.payload.get("toolCalls", [])
            self.tool_calls_count += len(tool_calls)
        elif kind == "CapabilityGranted":
            self.grants_count += 1
        elif kind == "AuthorizationDenied":
            self.denials_count += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "runId": self.run_id,
            "episodeId": self.episode_id,
            "status": self.status,
            "outcome": self.outcome,
            "startedAt": self.started_at,
            "completedAt": self.completed_at,
            "eventCount": self.event_count,
            "lastSeq": self.last_seq,
            "toolCallsCount": self.tool_calls_count,
            "grantsCount": self.grants_count,
            "denialsCount": self.denials_count,
        }


class BudgetProjection(Projection):
    """Projection tracking cumulative budget reservations, commitments, and leases."""

    def __init__(self) -> None:
        self.reserved_by_dimension: dict[str, int] = {}
        self.committed_by_dimension: dict[str, int] = {}
        self.released_by_dimension: dict[str, int] = {}
        self.active_leases: set[str] = set()

    def apply(self, event: EventEnvelope) -> None:
        kind = event.payload.get("kind", "")
        if kind == "BudgetReserved":
            lease_id = event.payload.get("leaseId")
            if lease_id:
                self.active_leases.add(lease_id)
            dims = event.payload.get("dimensions", {})
            for dim, amt in dims.items():
                self.reserved_by_dimension[dim] = self.reserved_by_dimension.get(dim, 0) + int(amt)

        elif kind == "BudgetCommitted":
            debits = event.payload.get("debits", {})
            for dim, amt in debits.items():
                self.committed_by_dimension[dim] = self.committed_by_dimension.get(dim, 0) + int(amt)

        elif kind == "BudgetReleased":
            lease_id = event.payload.get("leaseId")
            if lease_id:
                self.active_leases.discard(lease_id)
            unused = event.payload.get("unused", {})
            for dim, amt in unused.items():
                self.released_by_dimension[dim] = self.released_by_dimension.get(dim, 0) + int(amt)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reserved": dict(sorted(self.reserved_by_dimension.items())),
            "committed": dict(sorted(self.committed_by_dimension.items())),
            "released": dict(sorted(self.released_by_dimension.items())),
            "activeLeases": sorted(self.active_leases),
        }


class AuditProjection(Projection):
    """Projection compiling security, authorization, and governance audit trail."""

    def __init__(self) -> None:
        self.active_grants: dict[str, dict[str, Any]] = {}
        self.revoked_grants: set[str] = set()
        self.denials: list[dict[str, Any]] = []
        self.approvals: dict[str, dict[str, Any]] = []
        self.conflicts: list[dict[str, Any]] = []

    def apply(self, event: EventEnvelope) -> None:
        kind = event.payload.get("kind", "")
        if kind == "CapabilityGranted":
            grant_id = event.payload.get("grantId") or event.payload.get("id")
            if grant_id:
                self.active_grants[grant_id] = {
                    "grantId": grant_id,
                    "principal": event.principal,
                    "descriptorDigest": event.payload.get("descriptorDigest"),
                    "actions": event.payload.get("actions", []),
                    "grantedAt": event.occurred_at,
                }
        elif kind == "CapabilityRevoked":
            grant_id = event.payload.get("grantId")
            if grant_id:
                self.active_grants.pop(grant_id, None)
                self.revoked_grants.add(grant_id)
        elif kind == "AuthorizationDenied":
            self.denials.append({
                "seq": event.seq,
                "occurredAt": event.occurred_at,
                "principal": event.principal,
                "reason": event.payload.get("reason"),
                "requested": event.payload.get("requested"),
                "grantable": event.payload.get("grantable"),
            })
        elif kind == "ApprovalRequested":
            approval_id = event.payload.get("approvalId") or event.payload.get("id")
            if approval_id:
                self.approvals.append({
                    "approvalId": approval_id,
                    "status": "requested",
                    "reason": event.payload.get("reason"),
                    "riskTier": event.payload.get("riskTier"),
                })
        elif kind == "ApprovalResolved":
            approval_id = event.payload.get("approvalId") or event.payload.get("id")
            resolution = event.payload.get("resolution", "approved")
            for app in self.approvals:
                if app.get("approvalId") == approval_id:
                    app["status"] = "approved" if resolution == "approved" else "rejected"
                    app["reviewer"] = event.payload.get("reviewer")
        elif kind == "ConflictDetected":
            self.conflicts.append({
                "seq": event.seq,
                "resource": event.payload.get("resource"),
                "conflictingRuns": event.payload.get("conflictingRuns", []),
            })

    def to_dict(self) -> dict[str, Any]:
        return {
            "activeGrants": {k: dict(v) for k, v in sorted(self.active_grants.items())},
            "revokedGrants": sorted(self.revoked_grants),
            "denials": list(self.denials),
            "approvals": list(self.approvals),
            "conflicts": list(self.conflicts),
        }


class ArtifactRegistryProjection(Projection):
    """Projection tracking competence artifacts and their activation states."""

    def __init__(self) -> None:
        self.artifacts: dict[str, dict[str, Any]] = {}

    def apply(self, event: EventEnvelope) -> None:
        kind = event.payload.get("kind", "")
        if kind == "ArtifactCreated":
            artifact_id = event.payload.get("artifactId") or event.payload.get("id")
            if artifact_id:
                self.artifacts[artifact_id] = {
                    "artifactId": artifact_id,
                    "kind": event.payload.get("kind", "M"),
                    "version": event.payload.get("version", "1.0.0"),
                    "contentDigest": event.payload.get("contentDigest", ""),
                    "status": "active",
                }
        elif kind == "ActivationChanged":
            artifact_id = event.payload.get("artifactId")
            to_status = event.payload.get("toStatus", "active")
            if artifact_id and artifact_id in self.artifacts:
                self.artifacts[artifact_id]["status"] = to_status

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifacts": {k: dict(v) for k, v in sorted(self.artifacts.items())},
        }


def rebuild_projection(store: EventStorePort, projection: P, run_id: Optional[str] = None) -> P:
    """Rebuild a projection from scratch by replaying all matching events from the store."""
    read_res = store.read(EventRange(run_id=run_id, after_seq=None))
    if not read_res.ok or read_res.value is None:
        raise RuntimeError(f"Failed to read events for projection rebuild: {read_res.error}")

    for event in read_res.value:
        projection.apply(event)

    return projection
