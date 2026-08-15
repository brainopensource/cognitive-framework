"""Pure deterministic state reducer for the Vanguard event ledger.

Owning contract: VG-01 §2, VG-04 §12, GTS-13C T3.2 / T3.3 / T3.4.

Pure reducer invariants:
1. Zero I/O: no disk reads/writes, no network, no IPC.
2. Zero clocks: no system time / datetime.now calls; time flows ONLY through envelope timestamps.
3. Zero randomness: no random / uuid generation; strictly deterministic.
4. Associative over batches:
   reduce_batch(reduce_batch(s, b1), b2) == reduce_batch(s, list(b1) + list(b2))
5. CT-44 compliant: unknown events are preserved without crashing.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional, Sequence

from ..canonicalisation.digest import digest_of
from .events import EventEnvelope
from .state import (
    ApprovalRecord,
    ArtifactRecord,
    BudgetLeaseState,
    EffectRecord,
    EpisodeState,
    EvidenceRecord,
    LedgerState,
)

__all__ = [
    "ReducerError",
    "initial_state",
    "reduce_event",
    "reduce_batch",
    "reconstruct_state",
    "compute_state_digest",
]


class ReducerError(ValueError):
    """Raised when a reduction invariant is violated (e.g. non-monotonic sequence)."""


def initial_state(run_id: Optional[str] = None, episode_id: Optional[str] = None) -> LedgerState:
    """Create a clean, empty initial ledger state."""
    return LedgerState(
        run_id=run_id,
        episode_id=episode_id,
        episode=EpisodeState(run_id=run_id, episode_id=episode_id),
    )


def reduce_event(state: LedgerState, envelope: EventEnvelope) -> LedgerState:
    """Pure reducer: (State, EventEnvelope) -> State.
    
    Invariants:
    - Zero I/O, zero clocks, zero randomness.
    - Strictly monotonic sequence enforcement within the run.
    - Pure functional updates returning a new immutable LedgerState.
    """
    seq_int = int(envelope.seq)
    if state.last_seq is not None:
        last_seq_int = int(state.last_seq)
        if seq_int <= last_seq_int:
            raise ReducerError(
                f"Non-monotonic sequence: incoming seq {envelope.seq} ({seq_int}) "
                f"<= last seen seq {state.last_seq} ({last_seq_int})"
            )

    run_id = state.run_id or envelope.run_id
    episode_id = state.episode_id or envelope.episode_id
    payload = envelope.payload
    kind = payload.get("kind", "")

    # Copy current collections for functional update
    episode = state.episode
    grants = dict(state.grants)
    revoked_grants = list(state.revoked_grants)
    denials = list(state.denials)
    leases = dict(state.leases)
    cumulative_debits = dict(state.cumulative_budget_debits)
    effects = dict(state.effects)
    observations = list(state.observations)
    proposals = list(state.proposals)
    artifacts = dict(state.artifacts)
    evidence_claims = dict(state.evidence_claims)
    approvals = dict(state.approvals)
    heartbeats = dict(state.heartbeats)
    conflicts = list(state.conflicts)
    terminal_recovery = state.terminal_recovery
    unknown_events = list(state.unknown_events)

    if kind == "EpisodeStarted":
        episode = EpisodeState(
            run_id=envelope.run_id,
            episode_id=envelope.episode_id,
            status="active",
            started_at=envelope.occurred_at,
            task_spec=payload.get("taskSpec"),
            environment_snapshot=envelope.environment_snapshot or payload.get("environmentSnapshot"),
            state_transitions=episode.state_transitions + (("pending", "active", "EpisodeStarted"),),
        )

    elif kind == "EpisodeStateChanged":
        from_state = payload.get("fromState", episode.status)
        to_state = payload.get("toState", episode.status)
        reason = payload.get("reason")
        episode = EpisodeState(
            run_id=episode.run_id or envelope.run_id,
            episode_id=episode.episode_id or envelope.episode_id,
            status=to_state,
            outcome=episode.outcome,
            started_at=episode.started_at,
            completed_at=episode.completed_at,
            task_spec=episode.task_spec,
            environment_snapshot=episode.environment_snapshot,
            state_transitions=episode.state_transitions + ((from_state, to_state, reason),),
        )

    elif kind == "EpisodeCompleted":
        outcome = payload.get("outcome", "resolved")
        episode = EpisodeState(
            run_id=episode.run_id or envelope.run_id,
            episode_id=episode.episode_id or envelope.episode_id,
            status="completed",
            outcome=outcome,
            started_at=episode.started_at,
            completed_at=envelope.occurred_at,
            task_spec=episode.task_spec,
            environment_snapshot=episode.environment_snapshot,
            state_transitions=episode.state_transitions + ((episode.status, "completed", outcome),),
        )

    elif kind == "ObservationProduced":
        observations.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "snapshot": payload.get("snapshot"),
            "contentDigest": payload.get("contentDigest"),
            "provenanceLabel": payload.get("provenanceLabel"),
        })

    elif kind == "ProposalProduced":
        proposals.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "operatorId": payload.get("operatorId"),
            "proposalDigest": payload.get("proposalDigest"),
            "toolCalls": payload.get("toolCalls", []),
        })

    elif kind == "CapabilityGranted":
        grant_id = payload.get("grantId") or payload.get("id")
        if grant_id:
            grants[grant_id] = {
                "id": grant_id,
                "principal": payload.get("principal", envelope.principal),
                "descriptorDigest": payload.get("descriptorDigest"),
                "actions": payload.get("actions", []),
                "resources": payload.get("resources", []),
                "constraints": payload.get("constraints", {}),
                "purposeDigest": payload.get("purposeDigest"),
                "parentGrantId": payload.get("parentGrantId"),
                "grantedAt": envelope.occurred_at,
            }

    elif kind == "CapabilityRevoked":
        grant_id = payload.get("grantId")
        if grant_id:
            grants.pop(grant_id, None)
            if grant_id not in revoked_grants:
                revoked_grants.append(grant_id)

    elif kind == "AuthorizationDenied":
        denials.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "principal": payload.get("principal", envelope.principal),
            "reason": payload.get("reason"),
            "requested": payload.get("requested"),
            "grantable": payload.get("grantable"),
        })

    elif kind == "BudgetReserved":
        lease_id = payload.get("leaseId")
        if lease_id:
            dims = payload.get("dimensions", {})
            lims = payload.get("limits", dims)
            leases[lease_id] = BudgetLeaseState(
                lease_id=lease_id,
                dimensions=dims,
                limits=lims,
                committed_debits={},
                released_unused={},
                is_released=False,
            )

    elif kind == "BudgetCommitted":
        lease_id = payload.get("leaseId")
        debits = payload.get("debits", {})
        if lease_id and lease_id in leases:
            current_lease = leases[lease_id]
            updated_debits = dict(current_lease.committed_debits)
            for dim, amt in debits.items():
                updated_debits[dim] = updated_debits.get(dim, 0) + int(amt)
                cumulative_debits[dim] = cumulative_debits.get(dim, 0) + int(amt)
            leases[lease_id] = BudgetLeaseState(
                lease_id=lease_id,
                dimensions=current_lease.dimensions,
                limits=current_lease.limits,
                committed_debits=updated_debits,
                released_unused=current_lease.released_unused,
                is_released=current_lease.is_released,
            )
        else:
            for dim, amt in debits.items():
                cumulative_debits[dim] = cumulative_debits.get(dim, 0) + int(amt)

    elif kind == "BudgetReleased":
        lease_id = payload.get("leaseId")
        unused = payload.get("unused", {})
        if lease_id and lease_id in leases:
            current_lease = leases[lease_id]
            leases[lease_id] = BudgetLeaseState(
                lease_id=lease_id,
                dimensions=current_lease.dimensions,
                limits=current_lease.limits,
                committed_debits=current_lease.committed_debits,
                released_unused=unused,
                is_released=True,
            )

    elif kind == "EffectPreviewed":
        desc_digest = payload.get("descriptorDigest")
        if desc_digest:
            prev = effects.get(desc_digest)
            effects[desc_digest] = EffectRecord(
                descriptor_digest=desc_digest,
                sink_class=prev.sink_class if prev else None,
                grant_id=prev.grant_id if prev else None,
                preview_summary=payload.get("summary"),
                status="previewed",
                receipt_digest=prev.receipt_digest if prev else None,
                outcome=prev.outcome if prev else None,
                result_digest=prev.result_digest if prev else None,
                idempotency_key=prev.idempotency_key if prev else None,
                reconciliation_status=prev.reconciliation_status if prev else None,
                uncertainty=prev.uncertainty if prev else None,
            )

    elif kind == "EffectStarted":
        desc_digest = payload.get("descriptorDigest")
        if desc_digest:
            prev = effects.get(desc_digest)
            effects[desc_digest] = EffectRecord(
                descriptor_digest=desc_digest,
                sink_class=payload.get("sinkClass"),
                grant_id=payload.get("grantId"),
                preview_summary=prev.preview_summary if prev else None,
                status="started",
                receipt_digest=prev.receipt_digest if prev else None,
                outcome=prev.outcome if prev else None,
                result_digest=prev.result_digest if prev else None,
                idempotency_key=prev.idempotency_key if prev else None,
                reconciliation_status=prev.reconciliation_status if prev else None,
                uncertainty=prev.uncertainty if prev else None,
            )

    elif kind == "EffectCompleted":
        desc_digest = payload.get("descriptorDigest")
        if desc_digest:
            prev = effects.get(desc_digest)
            effects[desc_digest] = EffectRecord(
                descriptor_digest=desc_digest,
                sink_class=prev.sink_class if prev else None,
                grant_id=prev.grant_id if prev else None,
                preview_summary=prev.preview_summary if prev else None,
                status="completed",
                receipt_digest=payload.get("receiptDigest"),
                outcome=payload.get("outcome", "ok"),
                result_digest=payload.get("resultDigest"),
                idempotency_key=prev.idempotency_key if prev else None,
                reconciliation_status=prev.reconciliation_status if prev else None,
                uncertainty=prev.uncertainty if prev else None,
            )

    elif kind == "EffectReconciled":
        desc_digest = payload.get("descriptorDigest")
        if desc_digest:
            prev = effects.get(desc_digest)
            reconcile_status = payload.get("status", "undeterminable")
            outcome = reconcile_status if reconcile_status == "undeterminable" else (prev.outcome if prev and prev.outcome else "ok")
            effects[desc_digest] = EffectRecord(
                descriptor_digest=desc_digest,
                sink_class=prev.sink_class if prev else None,
                grant_id=prev.grant_id if prev else None,
                preview_summary=prev.preview_summary if prev else None,
                status="reconciled",
                receipt_digest=prev.receipt_digest if prev else payload.get("receiptDigest"),
                outcome=outcome,
                result_digest=prev.result_digest if prev else None,
                idempotency_key=payload.get("idempotencyKey"),
                reconciliation_status=reconcile_status,
                uncertainty=payload.get("uncertainty"),
            )

    elif kind == "ArtifactCreated":
        artifact_data = payload.get("artifact", payload)
        artifact_id = artifact_data.get("artifactId") or artifact_data.get("id")
        if artifact_id:
            art_kind = artifact_data.get("artifactKind") or (artifact_data.get("kind") if artifact_data.get("kind") != "ArtifactCreated" else "M")
            artifacts[artifact_id] = ArtifactRecord(
                artifact_id=artifact_id,
                kind=art_kind or "M",
                version=artifact_data.get("version") or artifact_data.get("artifactVersion", "1.0.0"),
                content_digest=artifact_data.get("contentDigest", ""),
                status="active",
            )

    elif kind == "ActivationChanged":
        artifact_id = payload.get("artifactId")
        to_status = payload.get("toStatus", "active")
        if artifact_id and artifact_id in artifacts:
            curr = artifacts[artifact_id]
            artifacts[artifact_id] = ArtifactRecord(
                artifact_id=curr.artifact_id,
                kind=curr.kind,
                version=curr.version,
                content_digest=curr.content_digest,
                status=to_status,
            )

    elif kind == "EvidenceClaimProduced":
        claim_id = payload.get("claimId") or payload.get("id")
        if claim_id:
            evidence_claims[claim_id] = EvidenceRecord(
                claim_id=claim_id,
                subject=payload.get("subject", ""),
                predicate=payload.get("predicate", ""),
                value=payload.get("value"),
                uncertainty=payload.get("uncertainty", {}),
            )

    elif kind == "ApprovalRequested":
        approval_id = payload.get("approvalId") or payload.get("id")
        if approval_id:
            approvals[approval_id] = ApprovalRecord(
                approval_id=approval_id,
                reason=payload.get("reason", ""),
                risk_tier=payload.get("riskTier", "medium"),
                grant_ref=payload.get("grantRef"),
                status="requested",
            )

    elif kind == "ApprovalResolved":
        approval_id = payload.get("approvalId") or payload.get("id")
        resolution = payload.get("resolution", "approved")
        reviewer = payload.get("reviewer")
        if approval_id and approval_id in approvals:
            curr = approvals[approval_id]
            approvals[approval_id] = ApprovalRecord(
                approval_id=curr.approval_id,
                reason=curr.reason,
                risk_tier=curr.risk_tier,
                grant_ref=curr.grant_ref,
                status="approved" if resolution == "approved" else "rejected",
                reviewer=reviewer,
            )

    elif kind == "Heartbeat":
        lease_id = payload.get("leaseId", "default")
        heartbeats[lease_id] = {
            "seq": envelope.seq,
            "seqNum": payload.get("seqNum", 0),
            "timestamp": payload.get("timestamp", envelope.occurred_at),
        }

    elif kind == "ConflictDetected":
        conflicts.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "resource": payload.get("resource"),
            "conflictingRuns": payload.get("conflictingRuns", []),
            "description": payload.get("description"),
        })

    elif kind == "RunRecovered":
        terminal_recovery = {
            "kind": "RunRecovered",
            "recoveredBy": payload.get("recoveredBy"),
            "priorState": payload.get("priorState"),
            "recoveryReason": payload.get("recoveryReason"),
            "recoveredAt": envelope.occurred_at,
        }
        episode = EpisodeState(
            run_id=episode.run_id or envelope.run_id,
            episode_id=episode.episode_id or envelope.episode_id,
            status="recovered",
            outcome="recovered",
            started_at=episode.started_at,
            completed_at=envelope.occurred_at,
            task_spec=episode.task_spec,
            environment_snapshot=episode.environment_snapshot,
            state_transitions=episode.state_transitions + ((episode.status, "recovered", "RunRecovered"),),
        )

    elif kind == "RunAborted":
        terminal_recovery = {
            "kind": "RunAborted",
            "abortedBy": payload.get("abortedBy"),
            "reason": payload.get("reason"),
            "abortedAt": envelope.occurred_at,
        }
        episode = EpisodeState(
            run_id=episode.run_id or envelope.run_id,
            episode_id=episode.episode_id or envelope.episode_id,
            status="aborted",
            outcome="aborted",
            started_at=episode.started_at,
            completed_at=envelope.occurred_at,
            task_spec=episode.task_spec,
            environment_snapshot=episode.environment_snapshot,
            state_transitions=episode.state_transitions + ((episode.status, "aborted", "RunAborted"),),
        )

    else:
        # CT-44: unknown event kind preserved in state
        unknown_events.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "kind": kind,
            "payload": dict(payload),
        })

    return LedgerState(
        run_id=run_id,
        episode_id=episode_id,
        last_seq=envelope.seq,
        event_count=state.event_count + 1,
        state_version=state.state_version + 1,
        episode=episode,
        grants=grants,
        revoked_grants=tuple(revoked_grants),
        denials=tuple(denials),
        leases=leases,
        cumulative_budget_debits=cumulative_debits,
        effects=effects,
        observations=tuple(observations),
        proposals=tuple(proposals),
        artifacts=artifacts,
        evidence_claims=evidence_claims,
        approvals=approvals,
        heartbeats=heartbeats,
        conflicts=tuple(conflicts),
        terminal_recovery=terminal_recovery,
        unknown_events=tuple(unknown_events),
    )


def reduce_batch(state: LedgerState, envelopes: Iterable[EventEnvelope]) -> LedgerState:
    """Fold `reduce_event` across an iterable of EventEnvelopes."""
    current = state
    for envelope in envelopes:
        current = reduce_event(current, envelope)
    return current


def reconstruct_state(
    envelopes: Iterable[EventEnvelope],
    initial: Optional[LedgerState] = None,
) -> LedgerState:
    """Reconstruct complete state from the beginning of the event stream."""
    return reduce_batch(initial or initial_state(), envelopes)


def compute_state_digest(state: LedgerState) -> str:
    """Calculate the deterministic sha256 state digest."""
    return state.digest()
