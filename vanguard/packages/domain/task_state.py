"""Semantic task-state values. Stdlib + RFC 8785 JCS only (I-STATE / T-09)."""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Literal, Mapping, Sequence

from .canonicalisation.digest import digest_bytes, digest_of
from .canonicalisation.jcs import canonical_bytes, parse_json_text

__all__ = [
    "CodingTaskState",
    "DeadEnd",
    "Discovery",
    "Evidence",
    "MemoryView",
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
    "TaskStep",
    "TodoItem",
    "critical_state",
    "validate_revision_invariants",
]


def _detached(value: Any) -> Any:
    """A copy that shares no container with the caller, at any depth.

    A shallow copy stops `state.last_verification["ok"] = False` and nothing
    else: `state.last_verification["nested"]["count"] = 99` still reaches
    through, because the inner object was never copied. Since these values are
    canonicalised and digested whole, a nested edit moves the digest just as
    surely as a top-level one.
    """
    if isinstance(value, Mapping):
        return {str(key): _detached(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_detached(item) for item in value]
    return value


def _frozen_mapping(value: Any, field: str) -> Mapping[str, Any]:
    """Copy a caller's mapping behind a read-only view (`I-STATE`).

    A frozen dataclass freezes its *attributes*, not the objects they point
    at. Holding the caller's `dict` therefore leaves the caller able to edit
    state that has already been digested, checkpointed or compared — and the
    edit is invisible, because nothing about it goes through this type. The
    deep copy is what makes the value immutable; the proxy is what stops the
    next reader from assuming it can write through the top level.

    The proxy is deliberately only one layer deep. Freezing every nested
    container would change what `to_canonical_dict` hands to JCS from plain
    JSON types into proxies and tuples, which is a wire-format change dressed
    up as a safety fix. The copy already removes every path back to the
    caller; the proxy only removes the most inviting one.
    """
    if not isinstance(value, Mapping):
        raise TypeError(f"{field} must be a mapping")
    return MappingProxyType(_detached(value))


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

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "budget_snapshot", _frozen_mapping(self.budget_snapshot, "budget_snapshot"))

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
        # Before any validation: a mapping validated in place and then kept by
        # reference is validated against bytes the caller can still change.
        for name in ("last_verification", "remaining_budgets", "recovery_state"):
            object.__setattr__(self, name, _frozen_mapping(getattr(self, name), name))
        if self.selection_policy_identity is not None:
            object.__setattr__(
                self, "selection_policy_identity",
                _frozen_mapping(self.selection_policy_identity, "selection_policy_identity"))
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

MEMORY_VIEW_SCHEMA = "aether.memory-view/1"
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _natural(value: Any, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid {field}")
    return value


def _require_digest(value: Any, field: str) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError(f"malformed {field}")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


@dataclass(frozen=True, slots=True)
class Evidence:
    """One unique, artifact-bound finding in an `aether.memory-view/1` snapshot."""

    key: str
    subject: str
    artifact: str
    finding: str
    body: str = ""

    def __post_init__(self) -> None:
        _require_text(self.key, "evidence key")
        _require_text(self.finding, "evidence finding")
        _require_digest(self.subject, "evidence subject")
        _require_digest(self.artifact, "evidence artifact")
        if not isinstance(self.body, str):
            raise TypeError("evidence body must be a string")

    def to_dict(self) -> dict[str, str]:
        return {
            "key": self.key,
            "subject": self.subject,
            "artifact": self.artifact,
            "finding": self.finding,
            "body": self.body,
        }

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "Evidence":
        if not isinstance(raw, Mapping):
            raise TypeError("evidence must be an object")
        return cls(
            key=str(raw.get("key", "")),
            subject=raw.get("subject", ""),
            artifact=raw.get("artifact", ""),
            finding=str(raw.get("finding", "")),
            body=str(raw.get("body", "")),
        )


@dataclass(frozen=True, slots=True)
class MemoryView:
    """Immutable `aether.memory-view/1` snapshot around a complete SemanticTaskState."""

    task_bytes: bytes
    cursor: int
    lineage_id: str
    reducer_version: str
    evidence: tuple[Evidence, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.task_bytes, (bytes, bytearray)):
            raise TypeError("task snapshot must be canonical bytes")
        object.__setattr__(self, "task_bytes", bytes(self.task_bytes))
        object.__setattr__(self, "evidence", tuple(self.evidence))
        _natural(self.cursor, "cursor")
        _require_text(self.lineage_id, "lineage_id")
        _require_text(self.reducer_version, "reducer_version")
        task_raw = parse_json_text(self.task_bytes.decode("utf-8"))
        if not isinstance(task_raw, Mapping):
            raise TypeError("task snapshot must be an object")
        task = SemanticTaskState.from_mapping(task_raw)
        if canonical_bytes(task.to_canonical_dict()) != self.task_bytes:
            raise ValueError("task snapshot is not canonical")
        if len({item.key for item in self.evidence}) != len(self.evidence):
            raise ValueError("duplicate evidence key")
        if not all(isinstance(item, Evidence) for item in self.evidence):
            raise TypeError("evidence must contain Evidence values")

    @property
    def task(self) -> SemanticTaskState:
        return SemanticTaskState.from_mapping(parse_json_text(self.task_bytes.decode("utf-8")))

    @classmethod
    def capture(
        cls,
        task: SemanticTaskState,
        cursor: int,
        *,
        lineage_id: str,
        reducer_version: str,
        evidence: Sequence[Evidence] = (),
    ) -> "MemoryView":
        if not isinstance(task, SemanticTaskState):
            raise TypeError("memory view requires a SemanticTaskState")
        return cls(
            task_bytes=canonical_bytes(task.to_canonical_dict()),
            cursor=cursor,
            lineage_id=lineage_id,
            reducer_version=reducer_version,
            evidence=tuple(evidence),
        )

    def encode(self) -> bytes:
        return canonical_bytes({
            "schema": MEMORY_VIEW_SCHEMA,
            "cursor": self.cursor,
            "lineageId": self.lineage_id,
            "reducerVersion": self.reducer_version,
            "task": parse_json_text(self.task_bytes.decode("utf-8")),
            "evidence": [item.to_dict() for item in self.evidence],
        })

    def digest(self) -> str:
        return digest_bytes(self.encode())

    @classmethod
    def decode(cls, payload: bytes, expected_digest: str) -> "MemoryView":
        if not isinstance(payload, (bytes, bytearray)):
            raise TypeError("memory view payload must be bytes")
        payload_bytes = bytes(payload)
        _require_digest(expected_digest, "memory digest")
        if digest_bytes(payload_bytes) != expected_digest:
            raise ValueError("memory digest mismatch")
        raw = parse_json_text(payload_bytes.decode("utf-8"))
        if not isinstance(raw, Mapping):
            raise TypeError("memory view must be an object")
        if raw.get("schema") != MEMORY_VIEW_SCHEMA:
            raise ValueError("unsupported memory schema")
        task_raw = raw.get("task")
        if not isinstance(task_raw, Mapping):
            raise TypeError("task snapshot must be an object")
        evidence_raw = raw.get("evidence", ())
        if not isinstance(evidence_raw, Sequence) or isinstance(evidence_raw, (str, bytes)):
            raise TypeError("evidence must be a sequence")
        view = cls(
            task_bytes=canonical_bytes(dict(task_raw)),
            cursor=raw.get("cursor"),
            lineage_id=str(raw.get("lineageId", raw.get("lineage_id", ""))),
            reducer_version=str(raw.get("reducerVersion", raw.get("reducer_version", ""))),
            evidence=tuple(
                Evidence.from_mapping(item) for item in evidence_raw if isinstance(item, Mapping)
            ),
        )
        if len(view.evidence) != len(tuple(evidence_raw)):
            raise TypeError("evidence must contain objects")
        if view.encode() != payload_bytes:
            raise ValueError("noncanonical or unknown memory fields")
        return view


def critical_state(view: MemoryView) -> dict[str, Any]:
    """Projection of durable obligations; not a writeback format.

    `T-131` row 7 / `RUN-09` defect 7. This projection is the mandatory-state
    brief `ContextCompiler.compile_packet` places *below* the eviction
    watermark, so anything absent from it is compactable. `changed_files_tree_hash`
    was absent: compaction could therefore retain the changed-file *list* while
    dropping the identity of the candidate tree those changes produced, which is
    exactly the "compaction loses candidate identity" defect. It is carried here
    so the candidate a turn is reasoning about survives context pressure.
    """
    task = view.task
    return {
        "objective": task.objective,
        "constraints": list(task.constraints),
        "plan": list(task.plan),
        "next_action": task.next_action,
        "modified_files": list(task.modified_files),
        "changed_files_tree_hash": task.changed_files_tree_hash,
        "failure": task.failure_class,
        "verification": dict(task.last_verification),
        "verification_plan": list(task.verification_plan),
        "settled_effects": list(task.settled_effects),
        "remaining_budgets": dict(task.remaining_budgets),
        "requirements": list(task.completion_requirements),
        "invariants": list(task.settled_invariants),
        "hypotheses": list(task.hypotheses),
        "state_ref": digest_bytes(view.encode()),
        "cursor": view.cursor,
        "lineage_id": view.lineage_id,
        "reducer_version": view.reducer_version,
    }


TaskMutableField = Literal[
    "plan",
    "strategy_steps",
    "hypotheses",
    "verification_plan",
    "next_action",
    "active_step_id",
    "backlog",
]

TASK_MUTABLE_FIELDS: frozenset[str] = frozenset({
    "plan",
    "strategy_steps",
    "hypotheses",
    "verification_plan",
    "next_action",
    "active_step_id",
    "backlog",
})

TASK_REVISION_MALFORMED = "TASK_REVISION_MALFORMED"
TASK_REVISION_STALE = "TASK_REVISION_STALE"
TASK_REVISION_CONFLICTING = "TASK_REVISION_CONFLICTING"
TASK_REVISION_WIDENING = "TASK_REVISION_WIDENING"


@dataclass(frozen=True, slots=True)
class TaskRevision:
    """ADR-0107 / D-1: typed task revision seam."""

    revision_id: str
    target_binding: tuple[str, str, str, str]
    expected_revision: int
    expected_state_digest: str
    mutated_fields: tuple[TaskMutableField, ...]
    proposed_state: SemanticTaskState
    authority_proof: str

    def __post_init__(self) -> None:
        if not isinstance(self.revision_id, str) or not self.revision_id.strip():
            raise ValueError("revision_id must be a non-empty string")
        if not isinstance(self.target_binding, tuple) or len(self.target_binding) != 4:
            raise TypeError("target_binding must be a 4-tuple of strings")
        if not all(isinstance(x, str) for x in self.target_binding):
            raise TypeError("target_binding entries must be strings")
        if not isinstance(self.expected_revision, int) or self.expected_revision < 0:
            raise ValueError("expected_revision must be a non-negative integer")
        if not isinstance(self.expected_state_digest, str) or not self.expected_state_digest.strip():
            raise ValueError("expected_state_digest must be a non-empty string")
        if not isinstance(self.mutated_fields, tuple):
            raise TypeError("mutated_fields must be a tuple")
        for f in self.mutated_fields:
            if f not in TASK_MUTABLE_FIELDS:
                raise ValueError(f"unknown mutated field {f!r}")
        if not isinstance(self.proposed_state, SemanticTaskState):
            raise TypeError("proposed_state must be a SemanticTaskState")
        if not isinstance(self.authority_proof, str) or not self.authority_proof.strip():
            raise ValueError("authority_proof must be a non-empty string")

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "revisionId": self.revision_id,
            "targetBinding": list(self.target_binding),
            "expectedRevision": self.expected_revision,
            "expectedStateDigest": self.expected_state_digest,
            "mutatedFields": list(self.mutated_fields),
            "proposedState": self.proposed_state.to_canonical_dict(),
            "authorityProof": self.authority_proof,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "TaskRevision":
        target = raw.get("targetBinding", raw.get("target_binding", ()))
        if not isinstance(target, (tuple, list)) or len(target) != 4:
            raise TypeError("target_binding must be a sequence of 4 strings")
        target_tuple = tuple(str(x) for x in target)

        mutated = raw.get("mutatedFields", raw.get("mutated_fields", ()))
        if not isinstance(mutated, (tuple, list)):
            raise TypeError("mutated_fields must be a sequence of strings")
        mutated_tuple = tuple(str(x) for x in mutated)

        proposed_raw = raw.get("proposedState", raw.get("proposed_state"))
        if isinstance(proposed_raw, SemanticTaskState):
            proposed = proposed_raw
        elif isinstance(proposed_raw, Mapping):
            proposed = SemanticTaskState.from_mapping(proposed_raw)
        else:
            raise TypeError("proposed_state must be a mapping or SemanticTaskState")

        return cls(
            revision_id=str(raw.get("revisionId", raw.get("revision_id", ""))),
            target_binding=target_tuple,
            expected_revision=int(raw.get("expectedRevision", raw.get("expected_revision", 0))),
            expected_state_digest=str(raw.get("expectedStateDigest", raw.get("expected_state_digest", ""))),
            mutated_fields=mutated_tuple,  # type: ignore[arg-type]
            proposed_state=proposed,
            authority_proof=str(raw.get("authorityProof", raw.get("authority_proof", ""))),
        )


def validate_revision_invariants(
    current_state: SemanticTaskState,
    revision: TaskRevision,
) -> tuple[bool, str | None, str | None]:
    """Pure domain check of TaskRevision against current SemanticTaskState.

    Returns (is_valid, failure_kind, failure_message).
    """
    if revision.expected_revision != current_state.revision:
        return (
            False,
            TASK_REVISION_STALE,
            f"stale revision: expected {revision.expected_revision}, current is {current_state.revision}",
        )
    if revision.expected_state_digest and revision.expected_state_digest != current_state.digest():
        return (
            False,
            TASK_REVISION_STALE,
            f"stale state digest: expected {revision.expected_state_digest}, current is {current_state.digest()}",
        )

    for field_name in revision.mutated_fields:
        if field_name not in TASK_MUTABLE_FIELDS:
            return (
                False,
                TASK_REVISION_MALFORMED,
                f"unauthorized mutated field: {field_name}",
            )

    proposed = revision.proposed_state
    if current_state.objective != proposed.objective:
        return False, TASK_REVISION_WIDENING, "cannot mutate objective"
    if current_state.constraints != proposed.constraints:
        return False, TASK_REVISION_WIDENING, "cannot mutate constraints"
    if dict(current_state.remaining_budgets) != dict(proposed.remaining_budgets):
        return False, TASK_REVISION_WIDENING, "cannot mutate remaining_budgets"
    if current_state.task_class != proposed.task_class:
        return False, TASK_REVISION_WIDENING, "cannot mutate task_class"
    if current_state.completion_requirements != proposed.completion_requirements:
        return False, TASK_REVISION_WIDENING, "cannot mutate completion_requirements"
    if current_state.settled_effects != proposed.settled_effects:
        return False, TASK_REVISION_WIDENING, "cannot mutate settled_effects"
    if current_state.settled_invariants != proposed.settled_invariants:
        return False, TASK_REVISION_WIDENING, "cannot mutate settled_invariants"
    if current_state.discoveries != proposed.discoveries:
        return False, TASK_REVISION_WIDENING, "cannot mutate discoveries"
    if current_state.dead_ends != proposed.dead_ends:
        return False, TASK_REVISION_WIDENING, "cannot mutate dead_ends"
    if current_state.todo_items != proposed.todo_items:
        return False, TASK_REVISION_WIDENING, "cannot mutate todo_items"
    if current_state.route_decisions != proposed.route_decisions:
        return False, TASK_REVISION_WIDENING, "cannot mutate route_decisions"
    if current_state.inspected_files != proposed.inspected_files:
        return False, TASK_REVISION_WIDENING, "cannot mutate inspected_files"
    if current_state.modified_files != proposed.modified_files:
        return False, TASK_REVISION_WIDENING, "cannot mutate modified_files"
    if current_state.implicated_files != proposed.implicated_files:
        return False, TASK_REVISION_WIDENING, "cannot mutate implicated_files"
    if current_state.change_surface != proposed.change_surface:
        return False, TASK_REVISION_WIDENING, "cannot mutate change_surface"
    if dict(current_state.last_verification) != dict(proposed.last_verification):
        return False, TASK_REVISION_WIDENING, "cannot mutate last_verification"
    if current_state.failure_class != proposed.failure_class:
        return False, TASK_REVISION_WIDENING, "cannot mutate failure_class"
    if current_state.falsified_hypotheses != proposed.falsified_hypotheses:
        return False, TASK_REVISION_WIDENING, "cannot mutate falsified_hypotheses"
    if current_state.changed_files_tree_hash != proposed.changed_files_tree_hash:
        return False, TASK_REVISION_WIDENING, "cannot mutate changed_files_tree_hash"
    if current_state.repository_identity != proposed.repository_identity:
        return False, TASK_REVISION_WIDENING, "cannot mutate repository_identity"
    if current_state.selection_policy_identity != proposed.selection_policy_identity:
        return False, TASK_REVISION_WIDENING, "cannot mutate selection_policy_identity"
    if current_state.index_snapshot_digest != proposed.index_snapshot_digest:
        return False, TASK_REVISION_WIDENING, "cannot mutate index_snapshot_digest"
    if dict(current_state.recovery_state) != dict(proposed.recovery_state):
        return False, TASK_REVISION_WIDENING, "cannot mutate recovery_state"
    if current_state.run_id != proposed.run_id:
        return False, TASK_REVISION_WIDENING, "cannot mutate run_id"

    mutable_attrs = {
        "plan": (current_state.plan != proposed.plan),
        "strategy_steps": (current_state.strategy_steps != proposed.strategy_steps),
        "hypotheses": (current_state.hypotheses != proposed.hypotheses),
        "verification_plan": (current_state.verification_plan != proposed.verification_plan),
        "next_action": (current_state.next_action != proposed.next_action),
        "active_step_id": (current_state.active_step_id != proposed.active_step_id),
        "backlog": (current_state.backlog != proposed.backlog),
    }
    for field_name, was_mutated in mutable_attrs.items():
        if was_mutated and field_name not in revision.mutated_fields:
            return (
                False,
                TASK_REVISION_WIDENING,
                f"field {field_name!r} was mutated but not declared in mutated_fields",
            )

    return True, None, None
