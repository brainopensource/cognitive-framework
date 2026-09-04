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

import re
from dataclasses import replace
from typing import Any, Iterable, Mapping, Optional, Sequence

from ..canonicalisation.digest import digest_of
from .events import EventEnvelope
from .state import (
    ChildRecord,
    ApprovalRecord,
    ArtifactRecord,
    BudgetLeaseState,
    EffectRecord,
    EpisodeState,
    EvidenceRecord,
    LedgerState,
    PluginRecord,
    VerdictRecord,
)

__all__ = [
    "REDUCER_VERSION",
    "ReducerError",
    "initial_state",
    "reduce_event",
    "reduce_batch",
    "reconstruct_state",
    "compute_state_digest",
]


#: The identity of the fold these functions perform (`ADR-0098 Decision 6`).
#: A checkpoint is a memo of `reduce_batch`, so it is only reusable under the
#: reducer that produced it; `runtime/checkpoints.py` pins this value and
#: falls back to a cold fold when it moves. Bump it whenever a change to
#: `reduce_event` or `LedgerState` would make an existing fold a fold of
#: different rules -- a stale pin is a wrong answer served fast.
REDUCER_VERSION = "v1.1.0"


class ReducerError(ValueError):
    """Raised when a reduction invariant is violated (e.g. non-monotonic sequence)."""


def initial_state(run_id: Optional[str] = None, episode_id: Optional[str] = None) -> LedgerState:
    """Create a clean, empty initial ledger state."""
    return LedgerState(
        run_id=run_id,
        episode_id=episode_id,
        episode=EpisodeState(run_id=run_id, episode_id=episode_id),
    )



def _child_field(payload: Mapping[str, Any], camel: str) -> Any:
    """Read an ADR-0090 child payload field under either spelling.

    Every other payload in this reducer is camelCase (`grantId`,
    `descriptorDigest`, `parentGrantId`), and so is every emitter in the tree.
    The ADR-0090 fold shipped reading snake_case only, matching the bundle's
    `child_events.schema.json` but nothing that emits into this ledger -- so on
    a repo-convention `ChildSpawned` it read `None` and folded nothing.

    Both spellings are accepted rather than one being declared the winner,
    because `SpawnAdapter` does not exist yet and picking for it here would be
    guessing. camelCase is preferred, matching the rest of the roster. When the
    adapter lands and the schema is ratified into `schemas/mhf/`, the loser can
    be dropped.
    """
    if camel in payload:
        return payload[camel]
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", camel).lower()
    return payload.get(snake)


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
    verdicts = dict(state.verdicts)
    plugins = dict(state.plugins)
    children = dict(state.children)
    unknown_events = list(state.unknown_events)
    goals = list(state.goals)
    plan_revisions = list(state.plan_revisions)
    strategy_changes = list(state.strategy_changes)
    progress_assessments = list(state.progress_assessments)
    context_compactions = list(state.context_compactions)

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

    elif kind == "TurnStarted":
        # `or` treats turn 0 as absent and silently relabels the first turn
        # with the envelope seq, so an episode's transitions read
        # `TurnStarted:7, TurnStarted:1, TurnStarted:2`. Turn numbering is
        # 0-based, so presence must be tested explicitly.
        turn_val = next(
            (payload[key] for key in ("turn", "turnNumber", "turn_index")
             if payload.get(key) is not None),
            envelope.seq,
        )
        episode = EpisodeState(
            run_id=episode.run_id or envelope.run_id,
            episode_id=episode.episode_id or envelope.episode_id,
            status="active",
            outcome=episode.outcome,
            started_at=episode.started_at or envelope.occurred_at,
            completed_at=episode.completed_at,
            task_spec=episode.task_spec,
            environment_snapshot=episode.environment_snapshot,
            state_transitions=episode.state_transitions + ((episode.status, "active", f"TurnStarted:{turn_val}"),),
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

    elif kind == "CapabilityAttenuated":
        grant_id = payload.get("grantId") or payload.get("id") or payload.get("childGrantId")
        if grant_id:
            grants[grant_id] = {
                "id": grant_id,
                "principal": payload.get("principal", envelope.principal),
                "descriptorDigest": payload.get("descriptorDigest"),
                "actions": payload.get("actions", []),
                "resources": payload.get("resources", []),
                "constraints": payload.get("constraints", {}),
                "purposeDigest": payload.get("purposeDigest"),
                "parentGrantId": payload.get("parentGrantId") or payload.get("parentId"),
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
        lease_id = payload.get("leaseId") or payload.get("lease_id")
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

    elif kind == "BudgetExhausted":
        lease_id = payload.get("leaseId") or payload.get("lease_id")
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
                is_released=True,
            )
        else:
            for dim, amt in debits.items():
                cumulative_debits[dim] = cumulative_debits.get(dim, 0) + int(amt)

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
        desc_digest = payload.get("descriptorDigest") or payload.get("descriptor_digest")
        if desc_digest:
            prev = effects.get(desc_digest)
            effects[desc_digest] = EffectRecord(
                descriptor_digest=desc_digest,
                sink_class=prev.sink_class if prev else None,
                grant_id=prev.grant_id if prev else None,
                preview_summary=prev.preview_summary if prev else None,
                status="completed",
                receipt_digest=payload.get("receiptDigest") or payload.get("receipt_digest"),
                outcome=payload.get("outcome", "ok"),
                result_digest=payload.get("resultDigest") or payload.get("result_digest"),
                idempotency_key=prev.idempotency_key if prev else None,
                reconciliation_status=prev.reconciliation_status if prev else None,
                uncertainty=prev.uncertainty if prev else None,
            )

    elif kind == "EffectFailed":
        desc_digest = payload.get("descriptorDigest") or payload.get("descriptor_digest")
        if desc_digest:
            prev = effects.get(desc_digest)
            effects[desc_digest] = EffectRecord(
                descriptor_digest=desc_digest,
                sink_class=prev.sink_class if prev else payload.get("sinkClass"),
                grant_id=prev.grant_id if prev else payload.get("grantId"),
                preview_summary=prev.preview_summary if prev else None,
                status="failed",
                receipt_digest=payload.get("receiptDigest") or payload.get("receipt_digest") or (prev.receipt_digest if prev else None),
                outcome=payload.get("error") or payload.get("outcome") or payload.get("reason") or "failed",
                result_digest=payload.get("resultDigest") or payload.get("result_digest") or (prev.result_digest if prev else None),
                idempotency_key=prev.idempotency_key if prev else payload.get("idempotencyKey"),
                reconciliation_status=prev.reconciliation_status if prev else None,
                uncertainty=prev.uncertainty if prev else payload.get("uncertainty"),
            )

    elif kind == "EffectRejected":
        desc_digest = payload.get("descriptorDigest") or payload.get("descriptor_digest")
        if desc_digest:
            prev = effects.get(desc_digest)
            effects[desc_digest] = EffectRecord(
                descriptor_digest=desc_digest,
                sink_class=prev.sink_class if prev else payload.get("sinkClass"),
                grant_id=prev.grant_id if prev else payload.get("grantId"),
                preview_summary=prev.preview_summary if prev else None,
                status="rejected",
                receipt_digest=payload.get("receiptDigest") or payload.get("receipt_digest") or (prev.receipt_digest if prev else None),
                outcome=payload.get("reason") or payload.get("outcome") or "rejected",
                result_digest=payload.get("resultDigest") or payload.get("result_digest") or (prev.result_digest if prev else None),
                idempotency_key=prev.idempotency_key if prev else payload.get("idempotencyKey"),
                reconciliation_status=prev.reconciliation_status if prev else None,
                uncertainty=prev.uncertainty if prev else payload.get("uncertainty"),
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

    elif kind == "GoalDeclared":
        # Digest and optional verified artifact reference only. A payload that
        # carried the goal text would put unwithdrawable content in an
        # append-only store (`ADR-0098 Decision 5`).
        goals.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "goalDigest": payload.get("goalDigest"),
            "goalArtifact": payload.get("goalArtifact"),
            "parentGoalDigest": payload.get("parentGoalDigest"),
        })

    elif kind == "PlanRevised":
        plan_revisions.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "planDigest": payload.get("planDigest"),
            "previousPlanDigest": payload.get("previousPlanDigest"),
            "planArtifact": payload.get("planArtifact"),
            "rationaleDigest": payload.get("rationaleDigest"),
            "reason": payload.get("reason") or payload.get("rationaleDigest"),
            "revision": payload.get("revision"),
        })

    elif kind == "StrategyChanged":
        strategy_changes.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "fromStrategy": payload.get("from") or payload.get("fromStrategy"),
            "toStrategy": payload.get("to") or payload.get("toStrategy"),
            "reason": payload.get("trigger") or payload.get("reason"),
            "controllerId": payload.get("controllerId"),
        })

    elif kind == "ProgressAssessed":
        progress_assessments.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "assessment": payload.get("assessment"),
            "signals": payload.get("signals", {}),
            "basis": payload.get("basis", []),
            "confidence": payload.get("confidence"),
            "evidenceDigest": payload.get("evidenceDigest"),
        })

    elif kind == "ContextCompacted":
        context_compactions.append({
            "seq": envelope.seq,
            "occurredAt": envelope.occurred_at,
            "strategy": payload.get("strategy"),
            "inputDigest": payload.get("inputDigest"),
            "outputDigest": payload.get("outputDigest"),
            "tokensBefore": payload.get("tokensBefore"),
            "tokensAfter": payload.get("tokensAfter"),
            "removedTokens": payload.get("removedTokens"),
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

    elif kind == "VerdictRecorded":
        # ADR-0076 §5: the payload is the daemon's own signed `SignedVerdict`
        # body, ledgered verbatim by `runtime/evaluator_gateway.py` -- the
        # sole legal writer. Reduce it as evidence, keyed by
        # `evaluation_request_id`, the same binding field a reader
        # re-verifies against. No signature check here: that is the reader's
        # job (`adapters/evaluators/gate.py`), not the state reducer's, and
        # there is nothing to verify against a false claim -- an unsigned or
        # unbound verdict never reaches this kind at all (the writer refuses
        # to ledger one).
        signed = payload.get("signedVerdict")
        if isinstance(signed, Mapping):
            request_id = signed.get("evaluation_request_id") or envelope.event_id
            verdicts[str(request_id)] = VerdictRecord(
                evaluation_request_id=str(request_id),
                verdict=str(signed.get("verdict", "")),
                signature=str(signed.get("signature", "")),
                subject_digest=signed.get("subject_digest"),
                oracle_id=signed.get("oracle_id"),
                nonce=signed.get("nonce"),
                key_id=signed.get("key_id"),
                signed_at=signed.get("signed_at"),
                recorded_at=envelope.occurred_at,
            )

    elif kind == "PluginDiscovered":
        plugin_id = payload.get("plugin_id") or payload.get("pluginId") or payload.get("id")
        if plugin_id:
            plugins[str(plugin_id)] = PluginRecord(
                plugin_id=str(plugin_id),
                status="discovered",
                manifest_digest=payload.get("manifest_digest") or payload.get("manifestDigest"),
                occurred_at=envelope.occurred_at,
            )

    elif kind == "PluginResolved":
        plugin_id = payload.get("plugin_id") or payload.get("pluginId") or payload.get("id")
        if plugin_id:
            plugins[str(plugin_id)] = PluginRecord(
                plugin_id=str(plugin_id),
                status="resolved",
                manifest_digest=payload.get("manifest_digest") or payload.get("manifestDigest"),
                occurred_at=envelope.occurred_at,
            )

    elif kind == "PluginVerified":
        plugin_id = payload.get("plugin_id") or payload.get("pluginId") or payload.get("id")
        if plugin_id:
            prev_plugin = plugins.get(str(plugin_id))
            plugins[str(plugin_id)] = PluginRecord(
                plugin_id=str(plugin_id),
                status="verified",
                manifest_digest=prev_plugin.manifest_digest if prev_plugin else (payload.get("manifest_digest") or payload.get("manifestDigest")),
                occurred_at=envelope.occurred_at,
            )

    elif kind == "PluginActivated":
        plugin_id = payload.get("plugin_id") or payload.get("pluginId") or payload.get("id")
        if plugin_id:
            prev_plugin = plugins.get(str(plugin_id))
            plugins[str(plugin_id)] = PluginRecord(
                plugin_id=str(plugin_id),
                status="activated",
                manifest_digest=prev_plugin.manifest_digest if prev_plugin else (payload.get("manifest_digest") or payload.get("manifestDigest")),
                occurred_at=envelope.occurred_at,
            )

    elif kind == "PluginQuiesced":
        plugin_id = payload.get("plugin_id") or payload.get("pluginId") or payload.get("id")
        if plugin_id:
            prev_plugin = plugins.get(str(plugin_id))
            plugins[str(plugin_id)] = PluginRecord(
                plugin_id=str(plugin_id),
                status="quiesced",
                manifest_digest=prev_plugin.manifest_digest if prev_plugin else None,
                occurred_at=envelope.occurred_at,
            )

    elif kind == "PluginRetired":
        plugin_id = payload.get("plugin_id") or payload.get("pluginId") or payload.get("id")
        if plugin_id:
            prev_plugin = plugins.get(str(plugin_id))
            plugins[str(plugin_id)] = PluginRecord(
                plugin_id=str(plugin_id),
                status="retired",
                manifest_digest=prev_plugin.manifest_digest if prev_plugin else None,
                occurred_at=envelope.occurred_at,
            )

    elif kind == "PluginFaulted":
        plugin_id = payload.get("plugin_id") or payload.get("pluginId") or payload.get("id")
        if plugin_id:
            prev_plugin = plugins.get(str(plugin_id))
            plugins[str(plugin_id)] = PluginRecord(
                plugin_id=str(plugin_id),
                status="faulted",
                reason=payload.get("reason", "faulted"),
                manifest_digest=prev_plugin.manifest_digest if prev_plugin else None,
                occurred_at=envelope.occurred_at,
            )

    elif kind == "ChildSpawned":
        # ADR-0090: material FSM transition, not an advisory marker.
        cid = _child_field(payload, "childEpisodeId")
        if not cid:
            # Fail closed. The original ADR-0090 fold skipped a payload whose id
            # it could not read, so a `ChildSpawned` this reducer did not
            # understand folded to nothing *and said nothing* -- and the orphan
            # guard below then had no record to fire against. A delegation event
            # that cannot be folded is a reducer error, not a no-op.
            raise ReducerError("ChildSpawned without a child episode id")
        cid = str(cid)
        if cid in children:
            raise ReducerError(f"duplicate ChildSpawned for {cid!r}")
        children[cid] = ChildRecord(
            child_episode_id=cid,
            parent_episode_id=str(_child_field(payload, "parentEpisodeId") or ""),
            authority=tuple(payload.get("authority", ())),
            depth=int(payload.get("depth") or 0),
            lineage=tuple(payload.get("lineage", ())),
            settled_intent_key=str(_child_field(payload, "settledIntentKey") or ""),
        )

    elif kind == "ChildReturned":
        cid = _child_field(payload, "childEpisodeId")
        if not cid:
            raise ReducerError("ChildReturned without a child episode id")
        cid = str(cid)
        prev_child = children.get(cid)
        if prev_child is None:
            raise ReducerError(f"ChildReturned without ChildSpawned for {cid!r}")
        if prev_child.status == "closed":
            raise ReducerError(f"child {cid!r} returned twice")
        key = _child_field(payload, "settledIntentKey")
        if key is not None and prev_child.settled_intent_key != str(key):
            raise ReducerError(f"settled intent key mismatch for {cid!r}")
        children[cid] = replace(
            prev_child, status="closed",
            outcome=payload.get("outcome"), terminal=payload.get("terminal"),
            cost=payload.get("cost"),
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
        # SPEC §1.3 branch resume: the last branch observed wins, so folding a
        # prefix and then a divergent continuation reports the divergence
        # rather than the trunk it forked from.
        branch_id=envelope.mhf_branch_id or state.branch_id,
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
        verdicts=verdicts,
        plugins=plugins,
        children=children,
        goals=tuple(goals),
        plan_revisions=tuple(plan_revisions),
        strategy_changes=tuple(strategy_changes),
        progress_assessments=tuple(progress_assessments),
        context_compactions=tuple(context_compactions),
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
