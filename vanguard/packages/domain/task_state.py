"""Semantic task-state values. Stdlib + RFC 8785 JCS only (I-STATE / T-09)."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .canonicalisation.digest import digest_of

__all__ = [
    "CodingTaskState",
    "DeadEnd",
    "Discovery",
    "RouteDecision",
    "SemanticTaskState",
    "StepState",
    "TaskStep",
    "TodoItem",
]


class StepState(str, Enum):
    PENDING = "pending"
    READY = "ready"
    ACTIVE = "active"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class TaskStep:
    """One DAG node in the domain task backlog."""

    step_id: str
    title: str
    target_files: tuple[str, ...] = ()
    dependencies: tuple[str, ...] = ()
    state: StepState = StepState.PENDING
    falsification_evidence: str | None = None
    verification_digest: str | None = None

    def __post_init__(self) -> None:
        if not self.step_id.strip() or not self.title.strip():
            raise ValueError("task step requires an id and title")
        if not isinstance(self.state, StepState):
            object.__setattr__(self, "state", StepState(str(self.state)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "stepId": self.step_id,
            "title": self.title,
            "targetFiles": list(self.target_files),
            "dependencies": list(self.dependencies),
            "state": self.state.value,
            "falsificationEvidence": self.falsification_evidence,
            "verificationDigest": self.verification_digest,
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "TaskStep":
        state_raw = raw.get("state", StepState.PENDING.value)
        return cls(
            step_id=str(raw.get("stepId", raw.get("step_id", ""))),
            title=str(raw.get("title", "")),
            target_files=tuple(str(item) for item in raw.get("targetFiles", raw.get("target_files", ())) or ()),
            dependencies=tuple(str(item) for item in raw.get("dependencies", ()) or ()),
            state=StepState(str(state_raw)),
            falsification_evidence=raw.get("falsificationEvidence", raw.get("falsification_evidence")),
            verification_digest=raw.get("verificationDigest", raw.get("verification_digest")),
        )


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

    def to_dict(self) -> dict[str, Any]:
        return {
            "route": self.route, "reason": self.reason, "failure": self.failure,
            "trigger": self.trigger, "parentEpisodeId": self.parent_episode_id,
            "parentStateDigest": self.parent_state_digest,
            "budgetSnapshot": dict(self.budget_snapshot),
            "providerUsageStatus": self.provider_usage_status,
        }


@dataclass(frozen=True, slots=True)
class TodoItem:
    """TODO / obligation whose completion requires the right evidence."""

    todo_id: str
    description: str
    status: str = "pending"
    receipt_digest: str | None = None

    def __post_init__(self) -> None:
        if not self.todo_id.strip() or not self.description.strip():
            raise ValueError("TODO requires an id and description")
        if self.status not in {"pending", "in_progress", "complete"}:
            raise ValueError(f"unknown TODO status: {self.status!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "todoId": self.todo_id,
            "description": self.description,
            "status": self.status,
            "receiptDigest": self.receipt_digest,
        }


@dataclass(frozen=True, slots=True)
class SemanticTaskState:
    """Merged FEATURE_SPEC SemanticTaskState + live CodingTaskState schema.

    One value. The runtime fold is the only authority that produces it.
    """

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
    task_class: str = "unspecified"
    completion_requirements: tuple[str, ...] = ()
    discoveries: tuple[Discovery, ...] = ()
    dead_ends: tuple[DeadEnd, ...] = ()
    implicated_files: tuple[str, ...] = ()
    change_surface: tuple[str, ...] = ()
    todo_items: tuple[TodoItem, ...] = ()
    route_decisions: tuple[RouteDecision, ...] = ()
    recovery_state: Mapping[str, Any] = field(default_factory=dict)
    run_id: str = ""
    revision: int = 0
    active_step_id: str | None = None
    backlog: tuple[TaskStep, ...] = ()
    falsified_hypotheses: tuple[str, ...] = ()
    settled_invariants: tuple[str, ...] = ()
    changed_files_tree_hash: str = ""
    repository_identity: str | None = None
    selection_policy_identity: Mapping[str, Any] | None = None
    index_snapshot_digest: str | None = None

    def __post_init__(self) -> None:
        if not self.objective.strip():
            raise ValueError("objective must be non-empty")
        if self.revision < 0:
            raise ValueError("revision must be non-negative")
        for name in ("constraints", "plan", "strategy_steps", "hypotheses", "inspected_files",
                     "modified_files", "verification_plan", "settled_effects",
                     "falsified_hypotheses", "settled_invariants"):
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
        if not all(isinstance(v, TaskStep) for v in self.backlog):
            raise TypeError("backlog must contain TaskStep values")
        if not isinstance(self.recovery_state, Mapping):
            raise TypeError("recovery_state must be a mapping")

    @property
    def overarching_goal(self) -> str:
        return self.objective

    def to_canonical_dict(self) -> dict[str, Any]:
        value: dict[str, Any] = {
            "objective": self.objective,
            "overarchingGoal": self.objective,
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
            "todoItems": [item.to_dict() for item in self.todo_items],
            "routeDecisions": [item.to_dict() for item in self.route_decisions],
            "recoveryState": dict(self.recovery_state),
            "runId": self.run_id,
            "revision": self.revision,
            "activeStepId": self.active_step_id,
            "backlog": [item.to_dict() for item in self.backlog],
            "falsifiedHypotheses": list(self.falsified_hypotheses),
            "settledInvariants": list(self.settled_invariants),
            "changedFilesTreeHash": self.changed_files_tree_hash,
        }
        if self.repository_identity is not None:
            value["repositoryIdentity"] = self.repository_identity
        if self.selection_policy_identity is not None:
            value["selectionPolicyIdentity"] = dict(self.selection_policy_identity)
        if self.index_snapshot_digest is not None:
            value["indexSnapshotDigest"] = self.index_snapshot_digest
        return value

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "SemanticTaskState":
        def strings(name: str, camel: str) -> tuple[str, ...]:
            value = raw.get(camel, raw.get(name, ()))
            if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
                raise TypeError(f"{camel} must be a sequence")
            return tuple(str(item) for item in value)

        budgets = raw.get("remainingBudgets", raw.get("remaining_budgets", {}))
        verification = raw.get("lastVerification", raw.get("last_verification", {}))
        if not isinstance(budgets, Mapping) or not isinstance(verification, Mapping):
            raise TypeError("state mappings must be objects")
        discoveries = tuple(
            Discovery(str(item["fact"]), str(item["source"]), float(item.get("confidence", 1.0)))
            for item in raw.get("discoveries", ()) if isinstance(item, Mapping)
        )
        dead_ends = tuple(
            DeadEnd(str(item["attempt"]), str(item["reason"]), str(item.get("evidence", "")))
            for item in raw.get("deadEnds", raw.get("dead_ends", ())) if isinstance(item, Mapping)
        )
        todos = tuple(
            TodoItem(
                str(item.get("todoId", item.get("todo_id", ""))),
                str(item.get("description", "")),
                str(item.get("status", "pending")),
                item.get("receiptDigest", item.get("receipt_digest")),
            )
            for item in raw.get("todoItems", raw.get("todo_items", ())) if isinstance(item, Mapping)
        )
        routes = tuple(
            RouteDecision(
                str(item["route"]), str(item["reason"]), item.get("failure"),
                str(item.get("trigger", "")), item.get("parentEpisodeId"),
                item.get("parentStateDigest"),
                dict(item.get("budgetSnapshot", {}) or {}),
                str(item.get("providerUsageStatus", "unknown")),
            )
            for item in raw.get("routeDecisions", raw.get("route_decisions", ()))
            if isinstance(item, Mapping)
        )
        backlog = tuple(
            TaskStep.from_mapping(item)
            for item in raw.get("backlog", ()) if isinstance(item, Mapping)
        )
        policy = raw.get("selectionPolicyIdentity", raw.get("selection_policy_identity"))
        objective = str(raw.get("objective") or raw.get("overarchingGoal") or raw.get("overarching_goal") or "")
        return cls(
            objective=objective,
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
            task_class=str(raw.get("taskClass", raw.get("task_class", "unspecified"))),
            completion_requirements=strings("completion_requirements", "completionRequirements"),
            discoveries=discoveries,
            dead_ends=dead_ends,
            implicated_files=strings("implicated_files", "implicatedFiles"),
            change_surface=strings("change_surface", "changeSurface"),
            todo_items=todos,
            route_decisions=routes,
            recovery_state=dict(raw.get("recoveryState", raw.get("recovery_state", {})) or {}),
            run_id=str(raw.get("runId", raw.get("run_id", "")) or ""),
            revision=int(raw.get("revision", 0) or 0),
            active_step_id=raw.get("activeStepId", raw.get("active_step_id")),
            backlog=backlog,
            falsified_hypotheses=strings("falsified_hypotheses", "falsifiedHypotheses"),
            settled_invariants=strings("settled_invariants", "settledInvariants"),
            changed_files_tree_hash=str(raw.get("changedFilesTreeHash", raw.get("changed_files_tree_hash", "")) or ""),
            repository_identity=_optional_str(raw.get("repositoryIdentity", raw.get("repository_identity"))),
            selection_policy_identity=dict(policy) if isinstance(policy, Mapping) else None,
            index_snapshot_digest=_optional_str(raw.get("indexSnapshotDigest", raw.get("index_snapshot_digest"))),
        )

    def transition_todo(
        self,
        todo_id: str,
        status: str,
        *,
        receipt_digest: str | None = None,
        verification_fresh: bool = False,
    ) -> "SemanticTaskState":
        """Advance a TODO only when its evidence requirement is satisfied."""
        if status == "complete" and not receipt_digest:
            raise ValueError("TODO completion requires a receipt digest")
        if (
            status == "complete"
            and ("verify" in self.completion_requirements or "verification" in self.completion_requirements)
            and not verification_fresh
        ):
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
        return dataclasses.replace(
            self,
            todo_items=tuple(updated),
            next_action=None if status == "complete" else self.next_action,
        )


CodingTaskState = SemanticTaskState


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None
