from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..domain.task_state import (
    CodingTaskState,
    DeadEnd,
    Discovery,
    RouteDecision,
    SemanticTaskState,
    StepState,
    TASK_MUTABLE_FIELDS,
    TASK_REVISION_CONFLICTING,
    TASK_REVISION_MALFORMED,
    TASK_REVISION_STALE,
    TASK_REVISION_WIDENING,
    TaskMutableField,
    TaskRevision,
    TaskStep,
    TodoItem,
    validate_revision_invariants,
)
from ..ports.event_store import Result

__all__ = [
    "CodingTaskState",
    "DeadEnd",
    "Discovery",
    "RouteDecision",
    "SemanticTaskState",
    "StepState",
    "TASK_MUTABLE_FIELDS",
    "TASK_REVISION_CONFLICTING",
    "TASK_REVISION_MALFORMED",
    "TASK_REVISION_STALE",
    "TASK_REVISION_WIDENING",
    "TaskMutableField",
    "TaskRevision",
    "TaskRevisionHook",
    "TaskStep",
    "TodoItem",
    "append_task_revision",
    "episode_id_from_events",
    "fold_task_state",
    "validate_task_revision_request",
]

#: T-131.7. Continuation identity is not only "what was the plan": a fresh
#: process must also know what it already spent, what authority it still
#: holds, and which effects are settled versus still in flight. Every kind
#: here is in ``WRITABLE_KINDS`` with a real kernel producer, so each one is
#: a carrier a production run actually originates rather than a fold-only
#: name (`ADR-0098 Decision 3`).
_CONTINUITY_KINDS = frozenset({
    "EffectStarted",
    "EffectRejected",
    "EffectReconciled",
    "BudgetReserved",
    "BudgetCommitted",
    "BudgetExhausted",
    "CapabilityGranted",
    "CapabilityRevoked",
    "CapabilityAttenuated",
})

#: Effect kinds that close an open ``EffectStarted`` intent. Kept identical to
#: ``RecoveryScanner.reconcile_open_intents`` (`runtime/ledger/recovery.py`):
#: if the two disagreed, the scanner would reconcile an intent this projection
#: still reports as pending, or the reverse.
_EFFECT_TERMINAL_KINDS = frozenset({
    "EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled",
})

_KNOWN_KINDS = frozenset({
    "EpisodeStarted",
    "ObservationProduced",
    "EffectCompleted",
    "EffectFailed",
    "ProposalProduced",
    "VerificationCompleted",
    "VerificationPassed",
    "VerificationFailed",
    "VerificationRecorded",
    "EpisodeCompleted",
    "RunCompleted",
    "RecoveryStateUpdated",
    "EpisodeStateChanged",
    "TaskClassified",
    "AmbiguityRecorded",
    "ConstraintDiscovered",
    "HypothesisOpened",
    "HypothesisSupported",
    "HypothesisRejected",
    "PlanDeclared",
    "PlanRevised",
    "ObligationOpened",
    "ObligationSatisfied",
    "DeadEndRecorded",
    "ChangeSurfaceUpdated",
    "NextActionSelected",
    "ContextSelectionRecorded",
    "OperatorDirectiveReceived",
}) | _CONTINUITY_KINDS


def episode_id_from_events(events: Sequence[Any], *, run_id: str) -> str:
    """Prefer the ledger episode id; synthesize only when none was recorded."""
    for event in events:
        eid = getattr(event, "episode_id", None)
        if isinstance(eid, str) and eid.strip():
            return eid.strip()
        payload = getattr(event, "payload", {})
        if isinstance(payload, Mapping):
            for key in ("episodeId", "episode_id"):
                value = payload.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    return f"episode-{run_id}"


def fold_task_state(events: Sequence[Any], *, objective: str = "") -> CodingTaskState:
    """Project durable coding facts without replaying any effect.

    Unknown event kinds are ignored. The ledger remains authoritative for
    effects; this projection only records what a fresh process should tell
    the next planner.
    """
    state: dict[str, Any] = {
        "objective": objective or "",
        "remainingBudgets": {},
        "recoveryState": {},
        "runId": "",
        "revision": 0,
        "taskClass": "coding",
        "falsifiedHypotheses": [],
        "settledInvariants": [],
        "changeSurface": [],
        "backlog": [],
    }
    inspected: set[str] = set()
    modified: set[str] = set()
    settled: set[str] = set()
    hypotheses: list[str] = []
    falsified: list[str] = []
    invariants: list[str] = []
    change_surface: list[str] = []
    discoveries: list[Discovery] = []
    dead_ends: list[DeadEnd] = []
    todo_by_id: dict[str, TodoItem] = {}
    backlog: list[TaskStep] = []
    last_verification: dict[str, Any] = {}
    revision = 0
    # -- T-131.7 continuation identity ------------------------------------
    # The ceiling is pinned to the FIRST `EpisodeStarted` in the stream. A
    # restart re-declares it, and adopting the later declaration is exactly
    # how a continuation replenishes a budget it already spent. Later
    # declarations may only attenuate, never widen.
    ceiling: dict[str, int] = {}
    ceiling_pinned = False
    consumed: dict[str, int] = {}
    reserved_by_lease: dict[str, dict[str, int]] = {}
    started_effects: dict[str, dict[str, Any]] = {}
    resolved_effects: set[str] = set()
    undeterminable_effects: set[str] = set()
    grants: dict[str, dict[str, Any]] = {}
    grant_children: dict[str, list[str]] = {}
    revoked_grants: set[str] = set()
    for event in events:
        payload = getattr(event, "payload", {})
        if not isinstance(payload, Mapping):
            continue
        kind = str(payload.get("kind") or getattr(event, "mhf_kind", "")
                   or getattr(event, "kind", ""))
        if kind and kind not in _KNOWN_KINDS:
            continue
        revision += 1
        run_id = getattr(event, "run_id", None)
        if isinstance(run_id, str) and run_id and not state["runId"]:
            state["runId"] = run_id
        payload_run = payload.get("runId") or payload.get("run_id")
        if isinstance(payload_run, str) and payload_run and not state["runId"]:
            state["runId"] = payload_run
        if isinstance(payload.get("plan"), Sequence) and not isinstance(payload.get("plan"), (str, bytes)):
            state["plan"] = [str(item) for item in payload["plan"]]
        if isinstance(payload.get("nextAction"), str):
            state["nextAction"] = payload["nextAction"]
        if isinstance(payload.get("lastVerification"), Mapping):
            state["lastVerification"] = dict(payload["lastVerification"])
        if isinstance(payload.get("taskClass") or payload.get("task_class"), str):
            classified = str(payload.get("taskClass") or payload.get("task_class"))
            if classified.strip():
                state["taskClass"] = classified.strip()
        for path in payload.get("modifiedFiles", ()) if isinstance(payload.get("modifiedFiles"), Sequence) else ():
            if isinstance(path, str):
                modified.add(path)
        for path in payload.get("inspectedFiles", ()) if isinstance(payload.get("inspectedFiles"), Sequence) else ():
            if isinstance(path, str):
                inspected.add(path)
        if isinstance(payload.get("remainingBudgets"), Mapping):
            # An explicitly declared remainder attenuates the derived one; it
            # never raises it. Before T-131.7 the last event to carry this
            # field simply won, so any writer -- including a resumed episode
            # header -- could hand the next planner a replenished budget.
            observed = {
                str(k): int(v) for k, v in payload["remainingBudgets"].items()
                if isinstance(v, int) and not isinstance(v, bool) and v >= 0
            }
            if not ceiling_pinned:
                ceiling = observed
                ceiling_pinned = True
            else:
                ceiling = {
                    dimension: min(amount, observed[dimension])
                    for dimension, amount in ceiling.items()
                    if dimension in observed
                }
        for descriptor in payload.get("settledEffects", ()) if isinstance(payload.get("settledEffects"), Sequence) else ():
            if isinstance(descriptor, str):
                settled.add(descriptor)
        raw_discoveries = payload.get("discoveries", ())
        if isinstance(raw_discoveries, Mapping):
            raw_discoveries = (raw_discoveries,)
        for item in raw_discoveries if isinstance(raw_discoveries, Sequence) else ():
            if isinstance(item, Mapping) and item.get("fact") and item.get("source"):
                discoveries.append(Discovery(str(item["fact"]), str(item["source"]), float(item.get("confidence", 1.0))))
                if item["fact"] not in invariants:
                    invariants.append(str(item["fact"]))
        raw_dead_ends = payload.get("deadEnds", ())
        if isinstance(raw_dead_ends, Mapping):
            raw_dead_ends = (raw_dead_ends,)
        for item in raw_dead_ends if isinstance(raw_dead_ends, Sequence) else ():
            if isinstance(item, Mapping) and item.get("attempt") and item.get("reason"):
                dead_ends.append(DeadEnd(str(item["attempt"]), str(item["reason"]), str(item.get("evidence", ""))))
        if "todoItems" in payload:
            raw_todos = payload.get("todoItems")
            if isinstance(raw_todos, Sequence) and not isinstance(raw_todos, (str, bytes)):
                todo_by_id = {
                    str(item["todoId"]): TodoItem(
                        str(item["todoId"]), str(item["description"]),
                        str(item.get("status", "pending")), item.get("receiptDigest"),
                    )
                    for item in raw_todos if isinstance(item, Mapping) and item.get("todoId") and item.get("description")
                }
        candidate = payload.get("objective") or payload.get("brief") or payload.get("goal")
        if isinstance(candidate, str) and candidate.strip() and not candidate.startswith("Resume run "):
            state["objective"] = candidate.strip()
        tree_hash = payload.get("changedFilesTreeHash") or payload.get("changed_files_tree_hash")
        if isinstance(tree_hash, str) and tree_hash:
            state["changedFilesTreeHash"] = tree_hash
        if kind == "EpisodeStarted":
            budgets = payload.get("budgetCeiling") or payload.get("budget")
            if isinstance(budgets, Mapping):
                declared = {
                    str(k): int(v) for k, v in budgets.items()
                    if isinstance(v, int) and not isinstance(v, bool) and v >= 0
                }
                if not ceiling_pinned:
                    ceiling = declared
                    ceiling_pinned = True
                else:
                    # A resumed process re-declares the ceiling. Taking the
                    # smaller of the two lets an operator tighten a budget on
                    # restart while making a widened one unreachable, so a
                    # restart can never buy authority the first episode did
                    # not have.
                    ceiling = {
                        dimension: min(amount, declared[dimension])
                        for dimension, amount in ceiling.items()
                        if dimension in declared
                    }
            if isinstance(payload.get("behaviorIdentity"), Mapping):
                # Keep this inside the existing policy-identity field so the
                # pure domain value remains unchanged while cold continuation
                # still receives every runtime binding it must validate.
                state["selectionPolicyIdentity"] = {
                    "behaviorIdentity": dict(payload["behaviorIdentity"]),
                    "contextEpoch": payload.get("contextEpoch"),
                }
        if kind == "ObservationProduced":
            path = payload.get("path")
            if isinstance(path, str) and path:
                inspected.add(path)
            for path in payload.get("inspectedFiles", ()) if isinstance(payload.get("inspectedFiles"), Sequence) else ():
                if isinstance(path, str):
                    inspected.add(path)
        if kind in _CONTINUITY_KINDS or kind in {"EffectCompleted", "EffectFailed"}:
            _fold_continuity_event(
                kind, payload,
                consumed=consumed, reserved_by_lease=reserved_by_lease,
                started_effects=started_effects, resolved_effects=resolved_effects,
                undeterminable_effects=undeterminable_effects, settled=settled,
                grants=grants, grant_children=grant_children,
                revoked_grants=revoked_grants,
            )
        if kind in {"EffectCompleted", "EffectFailed"}:
            descriptor = payload.get("descriptorDigest")
            if isinstance(descriptor, str) and kind == "EffectCompleted":
                settled.add(descriptor)
            path = payload.get("path")
            action = str(payload.get("action", ""))
            if isinstance(path, str) and action in {"patch.apply", "fs.patch", "fs.write", "write", "patch"}:
                modified.add(path)
        if kind == "ProposalProduced":
            action = payload.get("action")
            if isinstance(action, str):
                state["nextAction"] = action
        if kind in {"VerificationCompleted", "VerificationPassed", "VerificationFailed", "VerificationRecorded"}:
            last_verification = dict(payload)
        if kind in {"EpisodeCompleted", "RunCompleted"}:
            state["nextAction"] = None
        if kind in {"RecoveryStateUpdated", "EpisodeStateChanged"} and isinstance(payload.get("recoveryState"), Mapping):
            state["recoveryState"] = dict(payload["recoveryState"])
        if kind == "TaskClassified":
            classified = payload.get("taskClass") or payload.get("class") or payload.get("task_class")
            if isinstance(classified, str) and classified.strip():
                state["taskClass"] = classified.strip()
        if kind == "HypothesisOpened":
            text = payload.get("hypothesis") or payload.get("text")
            if isinstance(text, str) and text and text not in hypotheses:
                hypotheses.append(text)
        if kind == "HypothesisSupported":
            text = payload.get("hypothesis") or payload.get("text")
            if isinstance(text, str) and text and text not in hypotheses:
                hypotheses.append(text)
        if kind == "HypothesisRejected":
            text = payload.get("hypothesis") or payload.get("text")
            if isinstance(text, str) and text:
                if text in hypotheses:
                    hypotheses.remove(text)
                if text not in falsified:
                    falsified.append(text)
        if kind in {"PlanDeclared", "PlanRevised"}:
            if isinstance(payload.get("plan"), Sequence) and not isinstance(payload.get("plan"), (str, bytes)):
                state["plan"] = [str(item) for item in payload["plan"]]
            raw_strategy = payload.get("strategySteps") or payload.get("strategy_steps")
            if isinstance(raw_strategy, Sequence) and not isinstance(raw_strategy, (str, bytes)):
                state["strategySteps"] = [str(item) for item in raw_strategy]
            raw_hypotheses = payload.get("hypotheses")
            if isinstance(raw_hypotheses, Sequence) and not isinstance(raw_hypotheses, (str, bytes)):
                hypotheses = [str(item) for item in raw_hypotheses]
            raw_verification = payload.get("verificationPlan") or payload.get("verification_plan")
            if isinstance(raw_verification, Sequence) and not isinstance(raw_verification, (str, bytes)):
                state["verificationPlan"] = [str(item) for item in raw_verification]
            next_act = payload.get("nextAction") or payload.get("next_action")
            if isinstance(next_act, str):
                state["nextAction"] = next_act
            raw_backlog = payload.get("backlog", ())
            if isinstance(raw_backlog, Sequence) and not isinstance(raw_backlog, (str, bytes)):
                backlog = [TaskStep.from_mapping(item) for item in raw_backlog if isinstance(item, Mapping)]
            active = payload.get("activeStepId") or payload.get("active_step_id")
            if isinstance(active, str):
                state["activeStepId"] = active
        if kind == "ObligationOpened":
            todo_id = str(payload.get("todoId") or payload.get("obligationId") or "")
            description = str(payload.get("description") or payload.get("obligation") or "")
            if todo_id and description:
                todo_by_id[todo_id] = TodoItem(todo_id, description, "pending", payload.get("receiptDigest"))
        if kind == "ObligationSatisfied":
            todo_id = str(payload.get("todoId") or payload.get("obligationId") or "")
            if todo_id in todo_by_id:
                prior = todo_by_id[todo_id]
                todo_by_id[todo_id] = TodoItem(
                    prior.todo_id, prior.description, "complete",
                    payload.get("receiptDigest") or prior.receipt_digest,
                )
        if kind == "DeadEndRecorded":
            attempt = payload.get("attempt")
            reason = payload.get("reason")
            if isinstance(attempt, str) and isinstance(reason, str) and attempt and reason:
                dead_ends.append(DeadEnd(attempt, reason, str(payload.get("evidence", ""))))
        if kind == "ChangeSurfaceUpdated":
            surface = payload.get("changeSurface") or payload.get("change_surface")
            if isinstance(surface, Sequence) and not isinstance(surface, (str, bytes)):
                for path in surface:
                    if isinstance(path, str) and path not in change_surface:
                        change_surface.append(path)
                    # DIR-D1. A deleted path is a changed path: a resumed
                    # planner that saw only surviving files would believe a
                    # delete never happened and propose it again. The carrier
                    # publishes the complete set, deletions included, so the
                    # modified-file projection takes the whole set.
                    if isinstance(path, str) and path:
                        modified.add(path)
            candidate_digest = payload.get("candidateDigest") or payload.get("candidate_digest")
            if isinstance(candidate_digest, str) and candidate_digest:
                # T-131.7. `HarnessSession._append_change_surface` publishes the
                # candidate postimage under `candidateDigest`; no production
                # writer emits `changedFilesTreeHash`, which is the only key
                # this fold used to read. Candidate identity was therefore
                # empty on every real continuation while a handcrafted fixture
                # carrying the unwritten key looked green.
                state["changedFilesTreeHash"] = candidate_digest
            recorded = last_verification.get("workspaceDigest")
            if (isinstance(candidate_digest, str) and candidate_digest
                    and isinstance(recorded, str) and recorded
                    and recorded != candidate_digest):
                # DIR-D1: replay rejects stale evidence. The receipt attests a
                # postimage this surface fact has superseded, so it is not
                # evidence about the current candidate and must not be handed
                # to the completion gate as though it were. Dropping it is not
                # a loss of history -- the event stays in the ledger; only the
                # projection refuses to present it as applicable.
                last_verification = {}
        if kind == "NextActionSelected":
            action = payload.get("nextAction") or payload.get("action")
            if isinstance(action, str):
                state["nextAction"] = action
        if kind == "ContextSelectionRecorded":
            subject = payload.get("repositorySubject", payload.get("repositoryIdentity"))
            if isinstance(subject, str):
                state["repositoryIdentity"] = subject
            if isinstance(payload.get("selectionPolicyIdentity"), Mapping):
                state["selectionPolicyIdentity"] = dict(payload["selectionPolicyIdentity"])
            if "indexSnapshotDigest" in payload:
                state["indexSnapshotDigest"] = payload.get("indexSnapshotDigest")
        if kind == "ConstraintDiscovered":
            constraint = payload.get("constraint") or payload.get("text")
            if isinstance(constraint, str) and constraint:
                existing = list(state.get("constraints") or [])
                if constraint not in existing:
                    existing.append(constraint)
                state["constraints"] = existing
        if kind == "AmbiguityRecorded":
            note = payload.get("ambiguity") or payload.get("text")
            if isinstance(note, str) and note and note not in invariants:
                pass

    state["inspectedFiles"] = sorted(inspected)
    state["modifiedFiles"] = sorted(modified)
    state["settledEffects"] = sorted(settled)
    state["lastVerification"] = last_verification or state.get("lastVerification", {})
    state["discoveries"] = [item.to_dict() for item in discoveries]
    state["deadEnds"] = [item.to_dict() for item in dead_ends]
    state["todoItems"] = [item.to_dict() for item in todo_by_id.values()]
    state["hypotheses"] = list(hypotheses)
    state["falsifiedHypotheses"] = list(dict.fromkeys(falsified))
    state["settledInvariants"] = list(dict.fromkeys(invariants))
    state["changeSurface"] = list(change_surface)
    state["backlog"] = [item.to_dict() for item in backlog]
    state["revision"] = revision

    # -- T-131.7 continuation identity -------------------------------------
    # Resources: remaining is DERIVED from the pinned ceiling minus aggregate
    # consumption, never read back from a header. A dimension cannot go below
    # zero, and an overrun still counts as fully consumed.
    state["remainingBudgets"] = {
        dimension: max(amount - consumed.get(dimension, 0), 0)
        for dimension, amount in ceiling.items()
    }
    state["settledEffects"] = sorted(settled)
    pending = [
        started_effects[descriptor]
        for descriptor in sorted(
            set(started_effects) - (resolved_effects - undeterminable_effects))
    ]
    for descriptor in sorted(undeterminable_effects):
        if descriptor not in started_effects:
            pending.append({"descriptorDigest": descriptor, "action": ""})
    for entry in pending:
        entry["occurrence"] = (
            "undeterminable" if entry["descriptorDigest"] in undeterminable_effects
            else "unknown")
    live_grants = [
        grants[grant_id] for grant_id in sorted(grants)
        if grant_id not in revoked_grants
    ]
    # `recovery_state` is the domain's existing free mapping for "what an
    # interrupted process must be told"; carrying continuity under one
    # namespaced key keeps `SemanticTaskState` the sole task-state authority
    # without adding a second schema beside it. `ProtocolRecoveryState`
    # ignores keys it does not name, so the protocol carrier is unaffected.
    recovery = dict(state.get("recoveryState") or {})
    recovery["continuity"] = {
        "budgetCeiling": dict(ceiling),
        "consumedBudgets": {k: v for k, v in sorted(consumed.items()) if v},
        "pendingEffects": pending,
        "liveGrants": live_grants,
        "revokedGrants": sorted(revoked_grants),
    }
    state["recoveryState"] = recovery
    return CodingTaskState.from_mapping(state)


def _natural_amounts(raw: Any) -> dict[str, int]:
    """Integer dimensions of a budget payload; anything else is not a budget."""
    if not isinstance(raw, Mapping):
        return {}
    return {
        str(key): int(value) for key, value in raw.items()
        if isinstance(value, int) and not isinstance(value, bool)
    }


def _fold_continuity_event(
    kind: str,
    payload: Mapping[str, Any],
    *,
    consumed: dict[str, int],
    reserved_by_lease: dict[str, dict[str, int]],
    started_effects: dict[str, dict[str, Any]],
    resolved_effects: set[str],
    undeterminable_effects: set[str],
    settled: set[str],
    grants: dict[str, dict[str, Any]],
    grant_children: dict[str, list[str]],
    revoked_grants: set[str],
) -> None:
    """Accumulate consumption, authority and effect occurrence for one event.

    T-131.7. These three are what a continuation cannot reconstruct from the
    plan: a fresh process that reads only the semantic fields believes it has
    spent nothing, holds every grant it was ever issued, and has no effect in
    flight. Each accumulator below is driven by the carrier the *kernel*
    actually writes, not by the shape a reader would prefer.
    """
    descriptor = payload.get("descriptorDigest")
    descriptor = descriptor if isinstance(descriptor, str) and descriptor else None

    if kind == "EffectStarted" and descriptor is not None:
        started_effects[descriptor] = {
            "descriptorDigest": descriptor,
            "action": str(payload.get("action") or ""),
            "grantId": payload.get("grantId"),
            "leaseId": payload.get("leaseId"),
            "idempotencyKey": payload.get("idempotencyKey"),
        }
    elif kind in _EFFECT_TERMINAL_KINDS and descriptor is not None:
        resolved_effects.add(descriptor)
        if kind == "EffectReconciled":
            # `F-22`: uncertainty is first-class. An intent the recovery
            # scanner could not resolve is neither settled nor undone, so it
            # stays unresolved work and must NOT enter `settledEffects` --
            # presenting it as settled is how a continuation skips an effect
            # that may never have happened.
            occurrence = str(payload.get("occurrence") or "undeterminable")
            if occurrence == "occurred":
                settled.add(descriptor)
            else:
                undeterminable_effects.add(descriptor)

    elif kind == "BudgetReserved":
        lease_id = payload.get("leaseId") or payload.get("lease_id")
        if isinstance(lease_id, str) and lease_id:
            reserved_by_lease[lease_id] = _natural_amounts(
                payload.get("reserved", payload.get("dimensions")))

    elif kind in {"BudgetCommitted", "BudgetExhausted"}:
        lease_id = payload.get("leaseId") or payload.get("lease_id")
        reserved = reserved_by_lease.get(lease_id or "", {})
        debits = _natural_amounts(payload.get("debits"))
        if not debits:
            # `Governor.commit` returns `reserved - actual` per dimension and
            # retains it when negative (`kernel/budget.py`, `MF-KRN-007`), so
            # the spend is the inverse of the settlement the kernel emits.
            # This is the same inversion `child_runtime` already performs; the
            # reducer's `debits` spelling is honoured first where a writer
            # supplies it.
            settlement = _natural_amounts(payload.get("settlement"))
            debits = {
                dimension: reserved.get(dimension, 0) - amount
                for dimension, amount in settlement.items()
            }
        for dimension, amount in debits.items():
            if amount:
                consumed[dimension] = consumed.get(dimension, 0) + amount

    elif kind in {"CapabilityGranted", "CapabilityAttenuated"}:
        grant_id = payload.get("grantId") or payload.get("id")
        if isinstance(grant_id, str) and grant_id:
            grants[grant_id] = {
                "grantId": grant_id,
                "principal": payload.get("principal"),
                "descriptorDigest": payload.get("descriptorDigest"),
                "actions": [
                    str(item) for item in payload.get("actions", ())
                    if isinstance(item, str)
                ],
                "expiresAt": payload.get("expiresAt"),
                "singleUse": bool(payload.get("singleUse", False)),
            }
            parent = payload.get("parentGrantId") or payload.get("parentId")
            if isinstance(parent, str) and parent:
                grant_children.setdefault(parent, []).append(grant_id)

    elif kind == "CapabilityRevoked":
        grant_id = payload.get("grantId") or payload.get("id")
        if isinstance(grant_id, str) and grant_id:
            # `K-49`: revocation is transitive over descendants. A projection
            # that revoked only the named grant would report a child of a
            # revoked parent as live authority.
            frontier = [grant_id]
            while frontier:
                current = frontier.pop()
                if current in revoked_grants:
                    continue
                revoked_grants.add(current)
                frontier.extend(grant_children.get(current, ()))


def _to_camel(snake_str: str) -> str:
    components = snake_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def validate_task_revision_request(
    current_state: SemanticTaskState,
    request_args: Mapping[str, Any],
    *,
    target_binding: tuple[str, str, str, str] = ("run-default", "ep-default", "turn-default", "prop-default"),
    authority_proof: str = "authenticated-dispatch",
) -> Result[TaskRevision]:
    """Validate a candidate revision request against current state.

    Fails closed with typed kinds:
    - TASK_REVISION_MALFORMED
    - TASK_REVISION_STALE
    - TASK_REVISION_WIDENING
    """
    if not isinstance(request_args, Mapping):
        return Result.fail(TASK_REVISION_MALFORMED, "request_args must be a mapping")

    # Extract declared mutated_fields
    raw_mutated = request_args.get("mutated_fields", request_args.get("mutatedFields"))
    if raw_mutated is None:
        mutated_list = [
            f for f in sorted(TASK_MUTABLE_FIELDS)
            if f in request_args or _to_camel(f) in request_args
        ]
        if not mutated_list and "proposed_state" not in request_args and "proposedState" not in request_args:
            return Result.fail(TASK_REVISION_MALFORMED, "no mutable fields specified in revision request")
        mutated_fields = tuple(mutated_list)
    elif isinstance(raw_mutated, (list, tuple)):
        for f in raw_mutated:
            if f not in TASK_MUTABLE_FIELDS:
                return Result.fail(TASK_REVISION_MALFORMED, f"unknown mutable field {f!r}")
        mutated_fields = tuple(raw_mutated)
    else:
        return Result.fail(TASK_REVISION_MALFORMED, "mutated_fields must be a sequence of field names")

    # Expected revision
    expected_rev_raw = request_args.get("expected_revision", request_args.get("expectedRevision"))
    if expected_rev_raw is not None:
        if not isinstance(expected_rev_raw, int) or expected_rev_raw < 0:
            return Result.fail(TASK_REVISION_MALFORMED, "expected_revision must be a non-negative integer")
        expected_revision = expected_rev_raw
    else:
        expected_revision = current_state.revision

    # Expected state digest
    expected_state_digest_raw = request_args.get("expected_state_digest", request_args.get("expectedStateDigest"))
    if expected_state_digest_raw is not None:
        if not isinstance(expected_state_digest_raw, str) or not expected_state_digest_raw.strip():
            return Result.fail(TASK_REVISION_MALFORMED, "expected_state_digest must be a non-empty string")
        expected_state_digest = expected_state_digest_raw
    else:
        expected_state_digest = current_state.digest()

    # Target binding check
    raw_binding = request_args.get("target_binding", request_args.get("targetBinding", target_binding))
    if isinstance(raw_binding, (list, tuple)) and len(raw_binding) == 4:
        binding = tuple(str(x) for x in raw_binding)
    else:
        binding = target_binding

    # Build proposed_state
    proposed_raw = request_args.get("proposed_state", request_args.get("proposedState"))
    if proposed_raw is not None:
        if isinstance(proposed_raw, SemanticTaskState):
            proposed_state = proposed_raw
        elif isinstance(proposed_raw, Mapping):
            try:
                proposed_state = SemanticTaskState.from_mapping(proposed_raw)
            except Exception as e:
                return Result.fail(TASK_REVISION_MALFORMED, f"malformed proposed_state: {e}")
        else:
            return Result.fail(TASK_REVISION_MALFORMED, "proposed_state must be a mapping or SemanticTaskState")
    else:
        state_dict = current_state.to_canonical_dict()
        state_dict["revision"] = expected_revision + 1
        for f in mutated_fields:
            val = request_args.get(f, request_args.get(_to_camel(f)))
            if val is not None:
                if f in ("plan", "strategy_steps", "hypotheses", "verification_plan"):
                    if not isinstance(val, (list, tuple)):
                        return Result.fail(TASK_REVISION_MALFORMED, f"{f} must be a sequence of strings")
                    state_dict[_to_camel(f)] = [str(x) for x in val]
                elif f == "next_action":
                    state_dict["nextAction"] = str(val) if val is not None else None
                elif f == "active_step_id":
                    state_dict["activeStepId"] = str(val) if val is not None else None
                elif f == "backlog":
                    if not isinstance(val, (list, tuple)):
                        return Result.fail(TASK_REVISION_MALFORMED, "backlog must be a sequence of objects")
                    state_dict["backlog"] = [
                        item if isinstance(item, Mapping) else item.to_dict()
                        for item in val
                    ]
        try:
            proposed_state = SemanticTaskState.from_mapping(state_dict)
        except Exception as e:
            return Result.fail(TASK_REVISION_MALFORMED, f"failed to build proposed state: {e}")

    # Canonical revision_id
    canonical_payload = {
        "targetBinding": list(binding),
        "expectedRevision": expected_revision,
        "expectedStateDigest": expected_state_digest,
        "mutatedFields": list(mutated_fields),
        "proposedStateDigest": proposed_state.digest(),
    }
    explicit_id = request_args.get("revision_id", request_args.get("revisionId"))
    revision_id = str(explicit_id) if explicit_id else digest_of(canonical_payload)

    # Authority proof check
    raw_proof = request_args.get("authority_proof", request_args.get("authorityProof", authority_proof))
    if not isinstance(raw_proof, str) or not raw_proof.strip():
        return Result.fail(TASK_REVISION_MALFORMED, "authority_proof must be a non-empty string")
    proof = raw_proof.strip()

    try:
        revision = TaskRevision(
            revision_id=revision_id,
            target_binding=binding,  # type: ignore[arg-type]
            expected_revision=expected_revision,
            expected_state_digest=expected_state_digest,
            mutated_fields=mutated_fields,  # type: ignore[arg-type]
            proposed_state=proposed_state,
            authority_proof=proof,
        )
    except (TypeError, ValueError) as e:
        return Result.fail(TASK_REVISION_MALFORMED, str(e))

    is_valid, failure_kind, failure_msg = validate_revision_invariants(current_state, revision)
    if not is_valid:
        return Result.fail(failure_kind or TASK_REVISION_MALFORMED, failure_msg or "invalid revision")

    return Result.success(revision)


def append_task_revision(
    emitter: Any,
    revision: TaskRevision,
    *,
    run_id: str,
    principal: str,
    episode_id: str,
) -> Any:
    """Append PlanRevised through sole ledger writer authority."""
    payload: dict[str, Any] = {
        "revision": revision.expected_revision + 1,
        "planDigest": digest_of(revision.proposed_state.to_canonical_dict()),
        "revisionId": revision.revision_id,
        "targetBinding": list(revision.target_binding),
        "expectedRevision": revision.expected_revision,
        "expectedStateDigest": revision.expected_state_digest,
        "mutatedFields": list(revision.mutated_fields),
        "authorityProof": revision.authority_proof,
        "plan": list(revision.proposed_state.plan),
        "strategySteps": list(revision.proposed_state.strategy_steps),
        "hypotheses": list(revision.proposed_state.hypotheses),
        "verificationPlan": list(revision.proposed_state.verification_plan),
        "nextAction": revision.proposed_state.next_action,
        "activeStepId": revision.proposed_state.active_step_id,
        "backlog": [s.to_dict() for s in revision.proposed_state.backlog],
    }
    if hasattr(emitter, "emit_kind"):
        return emitter.emit_kind(
            "PlanRevised",
            run_id=run_id,
            principal=principal,
            payload=payload,
            episode_id=episode_id,
        )
    from ..kernel.model import Event
    event_payload = dict(payload)
    if episode_id:
        event_payload.setdefault("episodeId", episode_id)
    event = Event(
        kind="PlanRevised",
        reason="task_revision",
        at="2026-09-13T00:00:00.000Z",
        run_id=run_id,
        principal=principal,
        payload=event_payload,
    )
    if hasattr(emitter, "emit"):
        return emitter.emit(event)
    return event


class TaskRevisionHook:
    """Session-facing collaborator managing task.revise validation, conflicts, and emission."""

    def __init__(
        self,
        *,
        emitter: Any = None,
        target_binding: tuple[str, str, str, str] = ("run-default", "ep-default", "turn-default", "prop-default"),
        authority_proof: str = "authenticated-dispatch",
    ) -> None:
        self.emitter = emitter
        self.target_binding = target_binding
        self.authority_proof = authority_proof
        self._seen_revisions: dict[str, tuple[str, Any]] = {}
        self._pending_revision: TaskRevision | None = None

    def handle_revision(
        self,
        current_state: SemanticTaskState,
        request_args: Mapping[str, Any],
        *,
        target_binding: tuple[str, str, str, str] | None = None,
        authority_proof: str | None = None,
    ) -> Result[tuple[TaskRevision, Any]]:
        """Validate revision, check idempotence/conflict, and append event."""
        binding = target_binding or self.target_binding
        proof = authority_proof or self.authority_proof

        val_res = validate_task_revision_request(
            current_state,
            request_args,
            target_binding=binding,
            authority_proof=proof,
        )
        if not val_res.ok or val_res.value is None:
            return Result.fail(
                val_res.error.kind if val_res.error else TASK_REVISION_MALFORMED,
                val_res.error.message if val_res.error else "validation failed",
            )

        revision = val_res.value
        content_digest = digest_of(revision.to_canonical_dict())

        # Check conflict / idempotent replay
        if revision.revision_id in self._seen_revisions:
            prev_digest, prev_receipt = self._seen_revisions[revision.revision_id]
            if prev_digest == content_digest:
                # Idempotent replay: return cached receipt
                return Result.success((revision, prev_receipt))
            else:
                return Result.fail(
                    TASK_REVISION_CONFLICTING,
                    f"revision_id {revision.revision_id} reused with different content",
                )

        receipt = None
        if self.emitter is not None:
            run_id = revision.target_binding[0] if revision.target_binding[0] else "run-1"
            episode_id = revision.target_binding[1] if revision.target_binding[1] else "ep-1"
            receipt = append_task_revision(
                self.emitter,
                revision,
                run_id=run_id,
                principal="agent-1",
                episode_id=episode_id,
            )
        self._seen_revisions[revision.revision_id] = (content_digest, receipt)
        self._pending_revision = revision
        return Result.success((revision, receipt))

    def append_before_next_compile(
        self,
        current_state: SemanticTaskState,
    ) -> SemanticTaskState:
        """Hook for session binding: ensures latest revision is reflected in working state before compile."""
        if self._pending_revision is not None:
            new_state = self._pending_revision.proposed_state
            self._pending_revision = None
            return new_state
        return current_state
