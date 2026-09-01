"""TODO state machine (`spec §16`).

States and events are exactly those in `spec §16`. The value of this module is
the *transition table*: a TODO item that can move anywhere is not a state
machine, and the failure it hides is an agent that marks work DONE without
evidence -- `spec §58`'s "model self-report == verification" in miniature.

`DONE` therefore requires evidence. That is enforced here, not by convention.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Iterable, Mapping, Sequence

from ....domain.canonicalisation.digest import digest_of

__all__ = ["TodoEvent", "TodoItem", "TodoManager", "TodoStatus", "TodoTransitionError"]


class TodoStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    BLOCKED = "blocked"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"


class TodoEvent(str, Enum):
    """`spec §16` event vocabulary, emitted as ordinary runtime facts."""

    CREATED = "todo.created"
    STARTED = "todo.started"
    COMPLETED = "todo.completed"
    FAILED = "todo.failed"
    REOPENED = "todo.reopened"
    BLOCKED = "todo.blocked"
    SKIPPED = "todo.skipped"


#: Legal transitions. Anything absent raises rather than silently no-opping,
#: because a swallowed illegal transition produces a plan that disagrees with
#: the trajectory and no way to tell which is right.
_LEGAL: Mapping[TodoStatus, frozenset[TodoStatus]] = {
    TodoStatus.PENDING: frozenset({TodoStatus.ACTIVE, TodoStatus.BLOCKED,
                                   TodoStatus.SKIPPED}),
    TodoStatus.ACTIVE: frozenset({TodoStatus.DONE, TodoStatus.FAILED,
                                  TodoStatus.BLOCKED, TodoStatus.PENDING}),
    TodoStatus.BLOCKED: frozenset({TodoStatus.PENDING, TodoStatus.ACTIVE,
                                   TodoStatus.SKIPPED, TodoStatus.FAILED}),
    TodoStatus.FAILED: frozenset({TodoStatus.PENDING, TodoStatus.SKIPPED}),
    TodoStatus.DONE: frozenset({TodoStatus.PENDING}),   # reopened on regression
    TodoStatus.SKIPPED: frozenset({TodoStatus.PENDING}),
}

_EVENT_FOR: Mapping[TodoStatus, TodoEvent] = {
    TodoStatus.ACTIVE: TodoEvent.STARTED,
    TodoStatus.DONE: TodoEvent.COMPLETED,
    TodoStatus.FAILED: TodoEvent.FAILED,
    TodoStatus.BLOCKED: TodoEvent.BLOCKED,
    TodoStatus.SKIPPED: TodoEvent.SKIPPED,
    TodoStatus.PENDING: TodoEvent.REOPENED,
}


class TodoTransitionError(ValueError):
    """An illegal TODO transition was attempted."""


@dataclass(frozen=True, slots=True)
class TodoItem:
    id: str
    description: str
    dependencies: tuple[str, ...] = ()
    status: TodoStatus = TodoStatus.PENDING
    evidence: tuple[str, ...] = ()
    attempts: int = 0
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "description": self.description,
            "dependencies": list(self.dependencies), "status": self.status.value,
            "evidence": list(self.evidence), "attempts": self.attempts,
            "detail": self.detail,
        }


class TodoManager:
    """Ordered TODO list with dependency-aware readiness."""

    def __init__(self, items: Sequence[TodoItem] = ()) -> None:
        self._items: dict[str, TodoItem] = {}
        self._order: list[str] = []
        self._log: list[Mapping[str, Any]] = []
        for item in items:
            self.create(item)

    # -- construction ----------------------------------------------------

    def create(self, item: TodoItem) -> TodoItem:
        if item.id in self._items:
            raise TodoTransitionError(f"todo {item.id!r} already exists")
        unknown = [d for d in item.dependencies if d not in self._items]
        if unknown:
            raise TodoTransitionError(
                f"todo {item.id!r} depends on unknown items {unknown!r}")
        self._items[item.id] = item
        self._order.append(item.id)
        self._emit(TodoEvent.CREATED, item.id, {"description": item.description})
        return item

    @classmethod
    def from_steps(cls, steps: Sequence[str], *, chain: bool = True) -> "TodoManager":
        """Build a linear TODO chain from planner steps.

        Chained by default: a plan's steps are ordinarily sequential, and a
        parallel-by-default list would let the worker patch before it has
        localised.
        """
        manager = cls()
        previous: str | None = None
        for index, step in enumerate(steps, start=1):
            identifier = f"t{index}"
            manager.create(TodoItem(
                id=identifier, description=step,
                dependencies=(previous,) if chain and previous else (),
            ))
            previous = identifier
        return manager

    # -- queries ---------------------------------------------------------

    def items(self) -> tuple[TodoItem, ...]:
        return tuple(self._items[i] for i in self._order)

    def get(self, identifier: str) -> TodoItem | None:
        return self._items.get(identifier)

    def ready(self) -> tuple[TodoItem, ...]:
        """PENDING items whose dependencies are all DONE or SKIPPED."""
        settled = {TodoStatus.DONE, TodoStatus.SKIPPED}
        return tuple(
            item for item in self.items()
            if item.status is TodoStatus.PENDING
            and all(self._items[d].status in settled for d in item.dependencies)
        )

    def next_action(self) -> TodoItem | None:
        active = [i for i in self.items() if i.status is TodoStatus.ACTIVE]
        if active:
            return active[0]
        ready = self.ready()
        return ready[0] if ready else None

    def complete(self) -> bool:
        """True when nothing remains that could still be worked."""
        open_states = {TodoStatus.PENDING, TodoStatus.ACTIVE, TodoStatus.BLOCKED}
        return not any(item.status in open_states for item in self.items())

    def failed_items(self) -> tuple[TodoItem, ...]:
        return tuple(i for i in self.items() if i.status is TodoStatus.FAILED)

    def progress(self) -> Mapping[str, Any]:
        counts: dict[str, int] = {}
        for item in self.items():
            counts[item.status.value] = counts.get(item.status.value, 0) + 1
        total = len(self._items)
        done = counts.get(TodoStatus.DONE.value, 0)
        return {
            "total": total, "counts": counts,
            "fraction": round(done / total, 4) if total else 0.0,
        }

    # -- transitions -----------------------------------------------------

    def transition(
        self,
        identifier: str,
        status: TodoStatus,
        *,
        evidence: Sequence[str] = (),
        detail: str = "",
    ) -> TodoItem:
        item = self._items.get(identifier)
        if item is None:
            raise TodoTransitionError(f"unknown todo {identifier!r}")
        if status is item.status:
            return item
        if status not in _LEGAL[item.status]:
            raise TodoTransitionError(
                f"illegal transition {item.status.value} -> {status.value} "
                f"for todo {identifier!r}")
        # `spec §24`: completion is an evidence claim, so it must carry one.
        if status is TodoStatus.DONE and not (evidence or item.evidence):
            raise TodoTransitionError(
                f"todo {identifier!r} cannot be completed without evidence; "
                f"a model's assertion of success is not verification")

        updated = replace(
            item, status=status, detail=detail,
            evidence=tuple(dict.fromkeys(item.evidence + tuple(evidence))),
            attempts=item.attempts + (1 if status is TodoStatus.ACTIVE else 0),
        )
        self._items[identifier] = updated
        self._emit(_EVENT_FOR[status], identifier,
                   {"detail": detail, "evidence": list(evidence)})
        return updated

    def start(self, identifier: str) -> TodoItem:
        return self.transition(identifier, TodoStatus.ACTIVE)

    def finish(self, identifier: str, evidence: Sequence[str]) -> TodoItem:
        return self.transition(identifier, TodoStatus.DONE, evidence=evidence)

    def fail(self, identifier: str, detail: str) -> TodoItem:
        return self.transition(identifier, TodoStatus.FAILED, detail=detail)

    def reopen(self, identifier: str, detail: str = "") -> TodoItem:
        return self.transition(identifier, TodoStatus.PENDING, detail=detail)

    # -- durability ------------------------------------------------------

    def events(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self._log)

    def to_canonical_dict(self) -> dict[str, Any]:
        return {"items": [i.to_dict() for i in self.items()]}

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    @classmethod
    def from_canonical_dict(cls, raw: Mapping[str, Any]) -> "TodoManager":
        """Rebuild from a checkpoint. Bypasses transition checks by design:
        a persisted state is already the product of legal transitions."""
        manager = cls()
        for entry in raw.get("items", []) or []:
            item = TodoItem(
                id=str(entry["id"]), description=str(entry.get("description", "")),
                dependencies=tuple(entry.get("dependencies", []) or ()),
                status=TodoStatus(entry.get("status", "pending")),
                evidence=tuple(entry.get("evidence", []) or ()),
                attempts=int(entry.get("attempts", 0)),
                detail=str(entry.get("detail", "")),
            )
            manager._items[item.id] = item
            manager._order.append(item.id)
        return manager

    def render(self) -> str:
        marks = {
            TodoStatus.PENDING: "[ ]", TodoStatus.ACTIVE: "[>]",
            TodoStatus.BLOCKED: "[!]", TodoStatus.DONE: "[x]",
            TodoStatus.FAILED: "[F]", TodoStatus.SKIPPED: "[-]",
        }
        lines = ["# TODO"]
        for item in self.items():
            suffix = f"  ({item.detail})" if item.detail else ""
            lines.append(f"{marks[item.status]} {item.id}. {item.description}{suffix}")
        return "\n".join(lines)

    def _emit(self, event: TodoEvent, identifier: str, payload: Mapping[str, Any]) -> None:
        self._log.append({"event": event.value, "todoId": identifier, **dict(payload)})
