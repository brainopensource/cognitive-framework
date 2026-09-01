"""Reconstructible task state for semantic runtime continuation."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of

__all__ = ["CodingTaskState", "DeadEnd", "Discovery", "RouteDecision", "TodoItem", "fold_task_state"]


@dataclass(frozen=True, slots=True)
class Discovery:
    """A durable fact discovered during exploration, with its provenance."""

    fact: str
    source: str
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not self.fact.strip() or not self.source.strip() or not 0.0 <= self.confidence <= 1.0:
            raise ValueError("discovery requires source/fact and confidence in [0, 1]")

    def to_dict(self) -> dict[str, Any]:
        return {"fact": self.fact, "source": self.source, "confidence": self.confidence}


@dataclass(frozen=True, slots=True)
class DeadEnd:
    """A failed approach retained so escalation does not repeat it blindly."""

    attempt: str
    reason: str
    evidence: str = ""

    def __post_init__(self) -> None:
        if not self.attempt.strip() or not self.reason.strip():
            raise ValueError("dead end requires an attempt and reason")

    def to_dict(self) -> dict[str, str]:
        return {"attempt": self.attempt, "reason": self.reason, "evidence": self.evidence}


@dataclass(frozen=True, slots=True)
class RouteDecision:
    """A model-route decision and its typed failure, if any."""

    route: str
    reason: str
    failure: str | None = None
    trigger: str = ""
    parent_episode_id: str | None = None
    parent_state_digest: str | None = None
    budget_snapshot: Mapping[str, int] = field(default_factory=dict)
    provider_usage_status: str = "unknown"

    def to_dict(self) -> dict[str, str | None]:
        return {"route": self.route, "reason": self.reason, "failure": self.failure,
                "trigger": self.trigger, "parentEpisodeId": self.parent_episode_id,
                "parentStateDigest": self.parent_state_digest,
                "budgetSnapshot": dict(self.budget_snapshot),
                "providerUsageStatus": self.provider_usage_status}


@dataclass(frozen=True, slots=True)
class TodoItem:
    """TODO state whose completion requires the right evidence."""

    todo_id: str
    description: str
    status: str = "pending"
    receipt_digest: str | None = None

    def __post_init__(self) -> None:
        if not self.todo_id.strip() or not self.description.strip():
            raise ValueError("TODO requires an id and description")
        if self.status not in {"pending", "in_progress", "complete"}:
            raise ValueError(f"unknown TODO status: {self.status!r}")


@dataclass(frozen=True, slots=True)
class CodingTaskState:
    """Minimal durable state needed to resume a coding task semantically."""

    objective: str
    constraints: tuple[str, ...] = ()
    plan: tuple[str, ...] = ()
    strategy_steps: tuple[str, ...] = ()
    hypotheses: tuple[str, ...] = ()
    inspected_files: tuple[str, ...] = ()
    modified_files: tuple[str, ...] = ()
    verification_plan: tuple[str, ...] = ()
    last_verification: Mapping[str, Any] = field(default_factory=dict)
    failure_class: str | None = None
    next_action: str | None = None
    settled_effects: tuple[str, ...] = ()
    remaining_budgets: Mapping[str, int] = field(default_factory=dict)
    task_class: str = "coding"
    completion_requirements: tuple[str, ...] = ()
    discoveries: tuple[Discovery, ...] = ()
    dead_ends: tuple[DeadEnd, ...] = ()
    implicated_files: tuple[str, ...] = ()
    change_surface: tuple[str, ...] = ()
    todo_items: tuple[TodoItem, ...] = ()
    route_decisions: tuple[RouteDecision, ...] = ()
    recovery_state: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("objective must be non-empty")
        for name in ("constraints", "plan", "strategy_steps", "hypotheses", "inspected_files",
                     "modified_files", "verification_plan", "settled_effects"):
            values = getattr(self, name)
            if not isinstance(values, tuple) or not all(isinstance(v, str) for v in values):
                raise TypeError(f"{name} must be a tuple of strings")
        if any(not isinstance(k, str) or not isinstance(v, int) or v < 0
               for k, v in self.remaining_budgets.items()):
            raise ValueError("remaining_budgets must contain non-negative integers")
        if not isinstance(self.task_class, str) or not self.task_class.strip():
            raise ValueError("task_class must be non-empty")
        if not all(isinstance(v, str) and v for v in self.completion_requirements):
            raise TypeError("completion_requirements must contain non-empty strings")
        if not all(isinstance(v, Discovery) for v in self.discoveries):
            raise TypeError("discoveries must contain Discovery values")
        if not all(isinstance(v, DeadEnd) for v in self.dead_ends):
            raise TypeError("dead_ends must contain DeadEnd values")
        if not all(isinstance(v, TodoItem) for v in self.todo_items):
            raise TypeError("todo_items must contain TodoItem values")
        if not all(isinstance(v, RouteDecision) for v in self.route_decisions):
            raise TypeError("route_decisions must contain RouteDecision values")
        if not isinstance(self.recovery_state, Mapping):
            raise TypeError("recovery_state must be a mapping")

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective,
            "constraints": list(self.constraints),
            "plan": list(self.plan),
            "strategySteps": list(self.strategy_steps),
            "hypotheses": list(self.hypotheses),
            "inspectedFiles": list(self.inspected_files),
            "modifiedFiles": list(self.modified_files),
            "verificationPlan": list(self.verification_plan),
            "lastVerification": dict(self.last_verification),
            "failureClass": self.failure_class,
            "nextAction": self.next_action,
            "settledEffects": list(self.settled_effects),
            "remainingBudgets": dict(self.remaining_budgets),
            "taskClass": self.task_class,
            "completionRequirements": list(self.completion_requirements),
            "discoveries": [item.to_dict() for item in self.discoveries],
            "deadEnds": [item.to_dict() for item in self.dead_ends],
            "implicatedFiles": list(self.implicated_files),
            "changeSurface": list(self.change_surface),
            "todoItems": [{"todoId": item.todo_id, "description": item.description,
                           "status": item.status, "receiptDigest": item.receipt_digest}
                          for item in self.todo_items],
            "routeDecisions": [item.to_dict() for item in self.route_decisions],
            "recoveryState": dict(self.recovery_state),
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "CodingTaskState":
        def strings(name: str, camel: str) -> tuple[str, ...]:
            value = raw.get(camel, raw.get(name, ()))
            if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
                raise TypeError(f"{camel} must be a sequence")
            return tuple(str(item) for item in value)

        budgets = raw.get("remainingBudgets", raw.get("remaining_budgets", {}))
        verification = raw.get("lastVerification", raw.get("last_verification", {}))
        if not isinstance(budgets, Mapping) or not isinstance(verification, Mapping):
            raise TypeError("state mappings must be objects")
        discoveries = tuple(Discovery(str(item["fact"]), str(item["source"]), float(item.get("confidence", 1.0)))
                           for item in raw.get("discoveries", ()) if isinstance(item, Mapping))
        dead_ends = tuple(DeadEnd(str(item["attempt"]), str(item["reason"]), str(item.get("evidence", "")))
                         for item in raw.get("deadEnds", ()) if isinstance(item, Mapping))
        todos = tuple(TodoItem(str(item["todoId"]), str(item["description"]), str(item.get("status", "pending")), item.get("receiptDigest"))
                      for item in raw.get("todoItems", ()) if isinstance(item, Mapping))
        routes = tuple(RouteDecision(
            str(item["route"]), str(item["reason"]), item.get("failure"),
            str(item.get("trigger", "")), item.get("parentEpisodeId"),
            item.get("parentStateDigest"),
            dict(item.get("budgetSnapshot", {}) or {}),
            str(item.get("providerUsageStatus", "unknown")))
                       for item in raw.get("routeDecisions", ()) if isinstance(item, Mapping))
        return cls(
            objective=str(raw.get("objective", "")),
            constraints=strings("constraints", "constraints"),
            plan=strings("plan", "plan"),
            strategy_steps=strings("strategy_steps", "strategySteps"),
            hypotheses=strings("hypotheses", "hypotheses"),
            inspected_files=strings("inspected_files", "inspectedFiles"),
            modified_files=strings("modified_files", "modifiedFiles"),
            verification_plan=strings("verification_plan", "verificationPlan"),
            last_verification=dict(verification),
            failure_class=raw.get("failureClass", raw.get("failure_class")),
            next_action=raw.get("nextAction", raw.get("next_action")),
            settled_effects=strings("settled_effects", "settledEffects"),
            remaining_budgets={str(k): int(v) for k, v in budgets.items()},
            task_class=str(raw.get("taskClass", raw.get("task_class", "coding"))),
            completion_requirements=strings("completion_requirements", "completionRequirements"),
            discoveries=discoveries,
            dead_ends=dead_ends,
            implicated_files=strings("implicated_files", "implicatedFiles"),
            change_surface=strings("change_surface", "changeSurface"),
            todo_items=todos,
            route_decisions=routes,
            recovery_state=dict(raw.get("recoveryState", raw.get("recovery_state", {})) or {}),
        )

    def transition_todo(self, todo_id: str, status: str, *, receipt_digest: str | None = None,
                        verification_fresh: bool = False) -> "CodingTaskState":
        """Advance a TODO only when its evidence requirement is satisfied."""
        if status == "complete" and not receipt_digest:
            raise ValueError("TODO completion requires a receipt digest")
        if status == "complete" and ("verify" in self.completion_requirements or "verification" in self.completion_requirements) and not verification_fresh:
            raise ValueError("verification TODO requires a fresh verification receipt")
        updated = []
        found = False
        for item in self.todo_items:
            if item.todo_id == todo_id:
                updated.append(TodoItem(item.todo_id, item.description, status, receipt_digest or item.receipt_digest))
                found = True
            else:
                updated.append(item)
        if not found:
            raise KeyError(todo_id)
        return dataclasses.replace(self, todo_items=tuple(updated), next_action=None if status == "complete" else self.next_action)


def fold_task_state(events: Sequence[Any], *, objective: str = "") -> CodingTaskState:
    """Project durable coding facts without replaying any effect.

    The ledger remains authoritative for effects; this projection only records
    what a fresh process should tell the next planner. Unknown payload fields
    are ignored so older runs remain readable.
    """
    state: dict[str, Any] = {"objective": objective or "", "remainingBudgets": {},
                             "recoveryState": {}}
    inspected: set[str] = set()
    modified: set[str] = set()
    settled: set[str] = set()
    discoveries: list[Discovery] = []
    dead_ends: list[DeadEnd] = []
    todo_items: tuple[TodoItem, ...] = ()
    last_verification: dict[str, Any] = {}
    for event in events:
        payload = getattr(event, "payload", {})
        if not isinstance(payload, Mapping):
            continue
        kind = str(payload.get("kind") or getattr(event, "mhf_kind", "")
                   or getattr(event, "kind", ""))
        if isinstance(payload.get("plan"), Sequence) and not isinstance(payload.get("plan"), (str, bytes)):
            state["plan"] = [str(item) for item in payload["plan"]]
        if isinstance(payload.get("nextAction"), str):
            state["nextAction"] = payload["nextAction"]
        if isinstance(payload.get("lastVerification"), Mapping):
            state["lastVerification"] = dict(payload["lastVerification"])
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
        raw_dead_ends = payload.get("deadEnds", ())
        if isinstance(raw_dead_ends, Mapping):
            raw_dead_ends = (raw_dead_ends,)
        for item in raw_dead_ends if isinstance(raw_dead_ends, Sequence) else ():
            if isinstance(item, Mapping) and item.get("attempt") and item.get("reason"):
                dead_ends.append(DeadEnd(str(item["attempt"]), str(item["reason"]), str(item.get("evidence", ""))))
        raw_todos = payload.get("todoItems", ())
        if isinstance(raw_todos, Sequence) and not isinstance(raw_todos, (str, bytes)):
            todo_items = tuple(
                TodoItem(str(item["todoId"]), str(item["description"]), str(item.get("status", "pending")), item.get("receiptDigest"))
                for item in raw_todos if isinstance(item, Mapping) and item.get("todoId") and item.get("description")
            )
        candidate = payload.get("objective") or payload.get("brief") or payload.get("goal")
        if isinstance(candidate, str) and candidate.strip() and not candidate.startswith("Resume run "):
            state["objective"] = candidate.strip()
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
            diagnostics = payload.get("diagnostics")
            if isinstance(diagnostics, Mapping):
                state["lastVerification"] = dict(diagnostics) if isinstance(action, str) and "test" in action.lower() else state.get("lastVerification", {})
        if kind in {"VerificationCompleted", "VerificationPassed", "VerificationFailed"}:
            last_verification = dict(payload)
        if kind in {"EpisodeCompleted", "RunCompleted"}:
            state["nextAction"] = None
        if kind in {"RecoveryStateUpdated", "EpisodeStateChanged"} and isinstance(payload.get("recoveryState"), Mapping):
            state["recoveryState"] = dict(payload["recoveryState"])

    state["inspectedFiles"] = sorted(inspected)
    state["modifiedFiles"] = sorted(modified)
    state["settledEffects"] = sorted(settled)
    state["lastVerification"] = last_verification or state.get("lastVerification", {})
    state["discoveries"] = [item.to_dict() for item in discoveries]
    state["deadEnds"] = [item.to_dict() for item in dead_ends]
    state["todoItems"] = [{"todoId": item.todo_id, "description": item.description, "status": item.status}
                           for item in todo_items]
    return CodingTaskState.from_mapping(state)
