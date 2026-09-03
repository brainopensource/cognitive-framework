"""Runtime fold of domain SemanticTaskState. One authority, no second store."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..domain.task_state import (
    CodingTaskState,
    DeadEnd,
    Discovery,
    RouteDecision,
    SemanticTaskState,
    StepState,
    TaskStep,
    TodoItem,
)

__all__ = [
    "CodingTaskState",
    "DeadEnd",
    "Discovery",
    "RouteDecision",
    "SemanticTaskState",
    "StepState",
    "TaskStep",
    "TodoItem",
    "episode_id_from_events",
    "fold_task_state",
]

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
})


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
            state["remainingBudgets"] = {
                str(k): int(v) for k, v in payload["remainingBudgets"].items()
                if isinstance(v, int) and v >= 0
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
                state["remainingBudgets"] = {str(k): int(v) for k, v in budgets.items() if isinstance(v, int) and v >= 0}
        if kind == "ObservationProduced":
            path = payload.get("path")
            if isinstance(path, str) and path:
                inspected.add(path)
            for path in payload.get("inspectedFiles", ()) if isinstance(payload.get("inspectedFiles"), Sequence) else ():
                if isinstance(path, str):
                    inspected.add(path)
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
        if kind == "NextActionSelected":
            action = payload.get("nextAction") or payload.get("action")
            if isinstance(action, str):
                state["nextAction"] = action
        if kind == "ContextSelectionRecorded":
            if isinstance(payload.get("repositoryIdentity"), str):
                state["repositoryIdentity"] = payload["repositoryIdentity"]
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
    return CodingTaskState.from_mapping(state)
