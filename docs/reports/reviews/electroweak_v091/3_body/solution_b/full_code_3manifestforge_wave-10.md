# full_code_3manifestforge — Wave 10
## Contexto Progressivo e Planejamento (código integral)

**Invariante que atravessa toda esta wave:** adições em meio de run vão para a
camada DIALOGUE, nunca para o prefixo. O `ContextCompiler` do substrato cacheia
o prefixo SYSTEM/TOOLS/ENVIRONMENT e quebra esse cache se ele mudar — uma
retrieval que reescrevesse o prefixo multiplicaria silenciosamente o custo em
tokens de **todos** os turnos restantes.

---

## Cap. 10.1 — `vanguard/packages/apps/coding_max/context/scoring.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **128 linhas**

Pontuação §11. **Puro**: sem I/O, então um ranking é reproduzível a partir de um trace.

```python
"""Context candidate scoring (`spec §11`)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

__all__ = ["Candidate", "ScoreBreakdown", "score_candidates"]


@dataclass(frozen=True, slots=True)
class Candidate:
    path: str
    text: str = ""
    line: int = 0
    provider: str = ""
    provider_confidence: float = 0.5
    pinned: bool = False

    @property
    def token_estimate(self) -> int:
        return max(1, len(self.text) // 4)


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    """Every term from `spec §11`, kept separate so a ranking is explainable."""

    task_similarity: float = 0.0
    symbol_relevance: float = 0.0
    dependency_proximity: float = 0.0
    test_relationship: float = 0.0
    stacktrace_relevance: float = 0.0
    recent_failure_relevance: float = 0.0
    plan_relevance: float = 0.0
    edit_proximity: float = 0.0
    redundancy: float = 0.0
    staleness: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.task_similarity + self.symbol_relevance + self.dependency_proximity
            + self.test_relationship + self.stacktrace_relevance
            + self.recent_failure_relevance + self.plan_relevance + self.edit_proximity
            - self.redundancy - self.staleness
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "taskSimilarity": round(self.task_similarity, 4),
            "symbolRelevance": round(self.symbol_relevance, 4),
            "dependencyProximity": round(self.dependency_proximity, 4),
            "testRelationship": round(self.test_relationship, 4),
            "stacktraceRelevance": round(self.stacktrace_relevance, 4),
            "recentFailureRelevance": round(self.recent_failure_relevance, 4),
            "planRelevance": round(self.plan_relevance, 4),
            "editProximity": round(self.edit_proximity, 4),
            "redundancy": round(self.redundancy, 4),
            "staleness": round(self.staleness, 4),
            "total": round(self.total, 4),
        }


def _tokens(text: str) -> set[str]:
    return {w for w in "".join(c if c.isalnum() else " " for c in text.lower()).split()
            if len(w) > 2}


def score_candidates(
    candidates: Sequence[Candidate],
    *,
    task: str = "",
    symbols: Sequence[str] = (),
    dependencies: Sequence[str] = (),
    tests: Sequence[str] = (),
    stacktrace_paths: Sequence[str] = (),
    failed_paths: Sequence[str] = (),
    plan_paths: Sequence[str] = (),
    edited_paths: Sequence[str] = (),
    seen_digests: Sequence[str] = (),
) -> tuple[tuple[Candidate, ScoreBreakdown], ...]:
    """Rank candidates. Pure: no I/O, so a ranking is reproducible from a trace."""
    task_tokens = _tokens(task)
    symbol_set = {s.lower() for s in symbols}
    dep_set = set(dependencies)
    test_set = set(tests)
    trace_set = set(stacktrace_paths)
    failed_set = set(failed_paths)
    plan_set = set(plan_paths)
    edited_set = set(edited_paths)
    seen = set(seen_digests)

    scored: list[tuple[Candidate, ScoreBreakdown]] = []
    for candidate in candidates:
        stem = Path(candidate.path).stem.lower()
        body_tokens = _tokens(candidate.text) | _tokens(candidate.path)
        overlap = len(task_tokens & body_tokens) / max(len(task_tokens), 1)

        breakdown = ScoreBreakdown(
            task_similarity=2.0 * overlap,
            symbol_relevance=1.5 if (stem in symbol_set or
                                     any(s in candidate.text.lower() for s in symbol_set)) else 0.0,
            dependency_proximity=1.0 if candidate.path in dep_set else 0.0,
            test_relationship=0.8 if candidate.path in test_set else 0.0,
            # A stack trace names the failing frame outright; nothing else in
            # the score is that direct a piece of localisation evidence.
            stacktrace_relevance=3.0 if candidate.path in trace_set else 0.0,
            recent_failure_relevance=1.2 if candidate.path in failed_set else 0.0,
            plan_relevance=1.0 if candidate.path in plan_set else 0.0,
            edit_proximity=1.4 if candidate.path in edited_set else 0.0,
            redundancy=2.0 if _digest(candidate) in seen else 0.0,
            # Large blobs crowd out several small, better-targeted candidates.
            staleness=min(1.5, candidate.token_estimate / 4000.0),
        )
        scored.append((candidate, breakdown))

    # Pinned candidates sort first regardless of score: pinning is an explicit
    # operator/plan decision and must not be silently overridden by ranking.
    scored.sort(key=lambda pair: (pair[0].pinned, pair[1].total), reverse=True)
    return tuple(scored)


def _digest(candidate: Candidate) -> str:
    from ....domain.canonicalisation.digest import digest_of

    return digest_of({"path": candidate.path, "text": candidate.text})
```

---

## Cap. 10.2 — `vanguard/packages/apps/coding_max/context/progressive.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **217 linhas**

Os seis verbos de mutação do §12: add, drop, pin, compress, refresh, replace_all.

```python
"""Progressive context with mutation operations (`spec §12`).

`spec §12` forbids loading everything up front. The model starts with a
minimal working set, states what it is missing, and the harness retrieves
exactly that. This object owns the working set and the six mutation verbs.

One invariant matters above the rest: mid-run additions go to the DIALOGUE
layer, never into the prefix. The substrate's `ContextCompiler` caches the
SYSTEM/TOOLS/ENVIRONMENT prefix and breaks that cache if it changes, so a
retrieval that rewrote the prefix would silently multiply the token cost of
every remaining turn.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

from ....domain.canonicalisation.digest import digest_of
from .scoring import Candidate, ScoreBreakdown, score_candidates

__all__ = ["ContextEntry", "ProgressiveContext"]


@dataclass(frozen=True, slots=True)
class ContextEntry:
    key: str
    label: str
    text: str
    source: str
    pinned: bool = False
    epoch: int = 0
    score: float = 0.0

    @property
    def token_estimate(self) -> int:
        return max(1, len(self.text) // 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key, "label": self.label, "source": self.source,
            "pinned": self.pinned, "epoch": self.epoch,
            "tokens": self.token_estimate, "score": round(self.score, 4),
        }


class ProgressiveContext:
    """The working set. `epoch` increments on every mutation.

    The epoch is not decoration: `runtime/meta_controller.py::validate_confidence`
    refuses a confidence record whose `contextEpoch` does not match the current
    view, so a stale signal cannot drive a directive. Every mutation here must
    therefore be visible as an epoch bump.
    """

    def __init__(self, *, token_budget: int = 120_000) -> None:
        self._entries: dict[str, ContextEntry] = {}
        self._budget = token_budget
        self._epoch = 0
        self._dropped: list[str] = []
        self._history: list[Mapping[str, Any]] = []

    # -- introspection ---------------------------------------------------

    @property
    def epoch(self) -> int:
        return self._epoch

    @property
    def token_budget(self) -> int:
        return self._budget

    def total_tokens(self) -> int:
        return sum(entry.token_estimate for entry in self._entries.values())

    def entries(self) -> tuple[ContextEntry, ...]:
        return tuple(sorted(
            self._entries.values(),
            key=lambda e: (e.pinned, e.score), reverse=True,
        ))

    def paths(self) -> tuple[str, ...]:
        return tuple(entry.key for entry in self._entries.values())

    def digest(self) -> str:
        return digest_of({
            "epoch": self._epoch,
            "entries": [e.to_dict() for e in self.entries()],
        })

    def history(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self._history)

    # -- mutation verbs (`spec §12`) -------------------------------------

    def add(self, key: str, text: str, *, label: str = "", source: str = "",
            score: float = 0.0, pinned: bool = False) -> bool:
        """Admit one entry. Returns False if it was already present unchanged."""
        existing = self._entries.get(key)
        if existing is not None and existing.text == text:
            return False
        self._entries[key] = ContextEntry(
            key=key, label=label or key, text=text, source=source,
            pinned=pinned, epoch=self._epoch + 1, score=score,
        )
        self._bump("add", {"key": key, "tokens": max(1, len(text) // 4)})
        self._evict_if_needed()
        return True

    def drop(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is None or entry.pinned:
            return False
        del self._entries[key]
        self._dropped.append(key)
        self._bump("drop", {"key": key})
        return True

    def pin(self, key: str) -> bool:
        """Protect an entry from eviction and compression."""
        entry = self._entries.get(key)
        if entry is None or entry.pinned:
            return False
        self._entries[key] = replace(entry, pinned=True, epoch=self._epoch + 1)
        self._bump("pin", {"key": key})
        return True

    def compress(self, key: str, summary: str) -> bool:
        """Replace a body with a summary, keeping the key reachable.

        Compression is lossy and irreversible within a run, so it never
        touches a pinned entry and never shrinks something already small --
        a summary of forty tokens costs more than it saves.
        """
        entry = self._entries.get(key)
        if entry is None or entry.pinned or entry.token_estimate < 200:
            return False
        self._entries[key] = replace(
            entry, text=summary, epoch=self._epoch + 1,
            label=f"{entry.label} (compressed)",
        )
        self._bump("compress", {"key": key})
        return True

    def refresh(self, key: str, text: str) -> bool:
        """Re-read an entry whose underlying file changed."""
        entry = self._entries.get(key)
        if entry is None:
            return False
        if entry.text == text:
            return False
        self._entries[key] = replace(entry, text=text, epoch=self._epoch + 1)
        self._bump("refresh", {"key": key})
        return True

    def replace_all(self, entries: Sequence[ContextEntry]) -> None:
        """Wholesale swap, preserving pins. Used on strategy change."""
        pinned = {k: v for k, v in self._entries.items() if v.pinned}
        self._entries = dict(pinned)
        for entry in entries:
            self._entries.setdefault(entry.key, entry)
        self._bump("replace", {"count": len(entries)})

    # -- retrieval -------------------------------------------------------

    def admit_ranked(
        self,
        candidates: Sequence[Candidate],
        *,
        task: str = "",
        limit: int = 12,
        **signals: Any,
    ) -> tuple[str, ...]:
        """Score candidates and admit the best that fit the budget.

        Candidates already in the working set are skipped rather than
        re-scored: re-admitting an entry would reset its epoch and make every
        outstanding confidence record stale for no informational gain.
        """
        ranked = score_candidates(candidates, task=task, **signals)
        admitted: list[str] = []
        for candidate, breakdown in ranked:
            if len(admitted) >= limit:
                break
            if candidate.path in self._entries:
                continue
            if self.total_tokens() + candidate.token_estimate > self._budget:
                continue
            if self.add(candidate.path, candidate.text,
                        source=candidate.provider, score=breakdown.total,
                        pinned=candidate.pinned):
                admitted.append(candidate.path)
        return tuple(admitted)

    def needs_update(self, *, missing: Sequence[str] = ()) -> bool:
        return bool(missing) or self.total_tokens() > self._budget

    # -- internals -------------------------------------------------------

    def _evict_if_needed(self) -> None:
        """Evict lowest-scoring unpinned entries until inside budget."""
        if self.total_tokens() <= self._budget:
            return
        evictable = sorted(
            (e for e in self._entries.values() if not e.pinned),
            key=lambda e: e.score,
        )
        for entry in evictable:
            if self.total_tokens() <= self._budget:
                break
            del self._entries[entry.key]
            self._dropped.append(entry.key)
            self._history.append({"op": "evict", "key": entry.key, "epoch": self._epoch})

    def _bump(self, operation: str, payload: Mapping[str, Any]) -> None:
        self._epoch += 1
        self._history.append({"op": operation, "epoch": self._epoch, **dict(payload)})
```

---

## Cap. 10.3 — `vanguard/packages/apps/coding_max/planning/todo.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **266 linhas**

Máquina de estados §16. O valor está na tabela de transições e na regra de evidência.

```python
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
```

---

## Cap. 10.4 — `vanguard/packages/apps/coding_max/planning/planner.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **302 linhas**

Determinístico e por template. Plano autorado por modelo é suportado via `Plan.from_mapping` mas não exigido: para um `test_failure` o plano é sempre \"reproduz, localiza, corrige, verifica\".

```python
"""Plan construction and revision (`spec §15`, `§17`).

The planner is deterministic and template-driven. A model-authored plan is
supported (`Plan.from_mapping`) but is not required, because `spec §6`'s rule
about avoiding needless model calls applies just as much here: for a
`test_failure` the plan is always "reproduce, localise, patch, verify", and
paying a strong model to rediscover that is waste.

`spec §15`: *"Planner must remain mutable."* Revision is therefore a first
class operation that records why it happened.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, Mapping, Sequence

from ....domain.canonicalisation.digest import digest_of
from ..profile import TaskProfile, TaskType
from .todo import TodoManager

__all__ = ["Plan", "Planner", "ReplanTrigger", "Replanner"]


@dataclass(frozen=True, slots=True)
class Plan:
    objective: str
    assumptions: tuple[str, ...] = ()
    steps: tuple[str, ...] = ()
    verification_strategy: tuple[str, ...] = ()
    risk_points: tuple[str, ...] = ()
    revision: int = 0
    reason: str = "initial"

    def to_canonical_dict(self) -> dict[str, Any]:
        return {
            "objective": self.objective, "assumptions": list(self.assumptions),
            "steps": list(self.steps),
            "verificationStrategy": list(self.verification_strategy),
            "riskPoints": list(self.risk_points),
            "revision": self.revision, "reason": self.reason,
        }

    def digest(self) -> str:
        return digest_of(self.to_canonical_dict())

    def to_todos(self) -> TodoManager:
        return TodoManager.from_steps(self.steps)

    def render(self) -> str:
        lines = [f"# Plan (rev {self.revision}): {self.objective}"]
        if self.assumptions:
            lines.append("\n## Assumptions (falsify these first)")
            lines += [f"  - {a}" for a in self.assumptions]
        lines.append("\n## Steps")
        lines += [f"  {i}. {s}" for i, s in enumerate(self.steps, start=1)]
        if self.verification_strategy:
            lines.append("\n## Verification")
            lines += [f"  - {v}" for v in self.verification_strategy]
        if self.risk_points:
            lines.append("\n## Risks")
            lines += [f"  - {r}" for r in self.risk_points]
        return "\n".join(lines)

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any], *, objective: str = "") -> "Plan":
        """Parse a model-authored plan. Parsed, never cast (`CT-03` posture)."""
        steps = tuple(str(s) for s in (raw.get("steps") or ()) if str(s).strip())
        if not steps:
            raise ValueError("a plan must contain at least one step")
        return cls(
            objective=str(raw.get("objective") or objective or "unspecified"),
            assumptions=tuple(str(a) for a in (raw.get("assumptions") or ())),
            steps=steps,
            verification_strategy=tuple(
                str(v) for v in (raw.get("verificationStrategy")
                                 or raw.get("verification_strategy") or ())),
            risk_points=tuple(str(r) for r in (raw.get("riskPoints")
                                               or raw.get("risk_points") or ())),
        )


#: Step templates per task type. `spec §15`'s worked example is the
#: `complex_bug` row; the others are the same shape adapted to what the task
#: actually requires evidence of.
_TEMPLATES: Mapping[TaskType, tuple[str, ...]] = {
    TaskType.TEST_FAILURE: (
        "Run the failing test and capture the exact failure output",
        "Read the failing assertion and the code under test",
        "Form a hypothesis for the defect and name the owning file",
        "Apply a minimal patch to the implementation",
        "Re-run the targeted test",
        "Run related tests to check for regression",
    ),
    TaskType.COMPLEX_BUG: (
        "Reproduce the reported failure deterministically",
        "Identify the implementation owner of the failing behaviour",
        "Inspect related tests and existing invariants",
        "Form and record a hypothesis with its falsifier",
        "Apply a minimal scoped patch",
        "Run targeted tests",
        "Inspect the diff for interface changes and run related tests",
    ),
    TaskType.SIMPLE_FIX: (
        "Locate the exact target",
        "Apply the minimal edit",
        "Verify syntax and run any directly related test",
    ),
    TaskType.REFACTOR: (
        "Map the current structure and all call sites",
        "Establish a green baseline before changing anything",
        "Apply the restructuring in reviewable increments",
        "Re-run the baseline test set after each increment",
        "Confirm no public interface changed unintentionally",
    ),
    TaskType.FEATURE: (
        "Identify the module that should own the new behaviour",
        "Inspect neighbouring code for conventions to follow",
        "Implement the behaviour",
        "Add or extend a test that fails without the change",
        "Run the targeted and related tests",
    ),
    TaskType.MULTI_FILE_FEATURE: (
        "Build a repository map of the affected subsystems",
        "Enumerate every call site and integration point",
        "Establish a green baseline",
        "Implement the core behaviour in its owning module",
        "Wire the behaviour through each integration point",
        "Add tests covering the seams",
        "Run targeted, related, and broader test sets",
    ),
    TaskType.DEPENDENCY_ISSUE: (
        "Reproduce the import or resolution failure",
        "Inspect the declared dependency manifest",
        "Determine the correct constraint",
        "Apply the manifest change",
        "Re-run the failing import and the test suite entrypoint",
    ),
    TaskType.REPOSITORY_EXPLORATION: (
        "Build a repository map",
        "Read the entrypoints and canonical modules",
        "Trace the specific flow the question concerns",
        "Answer with file and line citations",
    ),
    TaskType.GREENFIELD: (
        "Confirm the target layout and build system",
        "Scaffold the module skeleton",
        "Implement the core behaviour",
        "Add tests that exercise the public surface",
        "Run the full new-module test set",
    ),
    TaskType.LONG_TASK: (
        "Build a repository map and establish a green baseline",
        "Partition the work into independently verifiable units",
        "Execute one unit and verify it before starting the next",
        "Checkpoint after each verified unit",
        "Run the broader test set once all units are complete",
    ),
}

_DEFAULT_STEPS: tuple[str, ...] = (
    "Search the repository for the relevant code",
    "Read the candidate files",
    "Apply a minimal change",
    "Verify with the available tests",
)

_VERIFICATION_FOR: Mapping[TaskType, tuple[str, ...]] = {
    TaskType.SIMPLE_FIX: ("V1 syntax", "V5 targeted tests"),
    TaskType.TEST_FAILURE: ("V1 syntax", "V5 targeted tests", "V6 related tests"),
    TaskType.REPOSITORY_EXPLORATION: ("V8 task verification",),
}
_DEFAULT_VERIFICATION = ("V1 syntax", "V3 lint", "V5 targeted tests",
                         "V6 related tests", "V8 task verification")


class Planner:
    """Deterministic plan construction from a `TaskProfile`."""

    def create(
        self,
        task: str,
        profile: TaskProfile,
        *,
        repo_map: Any = None,
        extra_assumptions: Sequence[str] = (),
    ) -> Plan:
        steps = _TEMPLATES.get(profile.task_type, _DEFAULT_STEPS)
        assumptions = list(extra_assumptions)
        if profile.mentioned_paths:
            assumptions.append(
                f"The change belongs in one of: {', '.join(profile.mentioned_paths)}")
        if profile.has_stacktrace:
            assumptions.append("The stack trace names the failing frame accurately")
        if not profile.reproduction_available:
            assumptions.append(
                "No reproduction exists yet; one must be built before patching")

        risks: list[str] = []
        if profile.uncertainty > 0.6:
            risks.append("Localisation is uncertain; expect to revise the target file")
        if profile.repo_familiarity < 0.4:
            risks.append("Repository is unfamiliar; conventions must be read, not assumed")
        if getattr(repo_map, "dirty", False):
            risks.append("Working tree is dirty; baseline may not be green")

        return Plan(
            objective=task.strip()[:400],
            assumptions=tuple(assumptions),
            steps=steps,
            verification_strategy=_VERIFICATION_FOR.get(
                profile.task_type, _DEFAULT_VERIFICATION),
            risk_points=tuple(risks),
        )


class ReplanTrigger(str, Enum):
    """`spec §17`. Each trigger names an observation, not a mood."""

    FAILED_ASSUMPTION = "failed_assumption"
    WRONG_LOCALIZATION = "wrong_localization"
    UNEXPECTED_DEPENDENCY = "unexpected_dependency"
    REPEATED_FAILED_PATCH = "repeated_failed_patch"
    UNEXPECTED_TEST_BEHAVIOR = "unexpected_test_behavior"
    MAJOR_CONTEXT_DISCOVERY = "major_context_discovery"
    BUDGET_PRESSURE = "budget_pressure"


class Replanner:
    """Revises a plan in response to evidence (`spec §17`).

    Revision is additive where possible. Discarding the whole plan on the
    first contradiction throws away the steps that already produced evidence,
    and re-deriving them costs turns the budget cannot spare.
    """

    #: How each trigger reshapes the remaining plan.
    _INSERTIONS: Mapping[ReplanTrigger, tuple[str, ...]] = {
        ReplanTrigger.WRONG_LOCALIZATION: (
            "Widen the repository search with different terms and symbol lookup",
            "Re-identify the owning file from fresh evidence",
        ),
        ReplanTrigger.FAILED_ASSUMPTION: (
            "Record the falsified assumption and its contradicting evidence",
            "Re-derive the hypothesis from the observed behaviour",
        ),
        ReplanTrigger.UNEXPECTED_DEPENDENCY: (
            "Map the dependency edges around the target",
            "Extend the patch scope to cover the affected callers",
        ),
        ReplanTrigger.REPEATED_FAILED_PATCH: (
            "Roll back to the last verified state",
            "Re-read the target at current HEAD before re-patching",
        ),
        ReplanTrigger.UNEXPECTED_TEST_BEHAVIOR: (
            "Read the failing test to establish what it actually asserts",
            "Reconcile the implementation with the asserted contract",
        ),
        ReplanTrigger.MAJOR_CONTEXT_DISCOVERY: (
            "Re-rank context against the new discovery",
        ),
        ReplanTrigger.BUDGET_PRESSURE: (
            "Drop speculative exploration and finish the best current candidate",
        ),
    }

    def revise(
        self,
        current_plan: Plan,
        trigger: ReplanTrigger,
        *,
        evidence: Sequence[str] = (),
        completed_steps: Sequence[str] = (),
    ) -> Plan:
        remaining = tuple(s for s in current_plan.steps if s not in set(completed_steps))
        insertions = self._INSERTIONS.get(trigger, ())

        if trigger is ReplanTrigger.BUDGET_PRESSURE:
            # Completion mode (`spec §42`): shrink rather than grow.
            steps = insertions + tuple(
                s for s in remaining if "broader" not in s.lower()
                and "speculative" not in s.lower())
        else:
            steps = insertions + remaining

        assumptions = current_plan.assumptions
        if trigger is ReplanTrigger.FAILED_ASSUMPTION and assumptions:
            # The falsified assumption is dropped, not silently retained --
            # a plan that still asserts a disproven premise will keep
            # producing the same wrong step.
            assumptions = assumptions[1:]

        return replace(
            current_plan,
            steps=steps or current_plan.steps,
            assumptions=assumptions,
            risk_points=tuple(dict.fromkeys(
                current_plan.risk_points + tuple(evidence))),
            revision=current_plan.revision + 1,
            reason=trigger.value,
        )
```

---

## Cap. 10.5 — O epoch não é decoração

```python
class ProgressiveContext:
    """The working set. `epoch` increments on every mutation.

    The epoch is not decoration: `runtime/meta_controller.py::validate_confidence`
    refuses a confidence record whose `contextEpoch` does not match the current
    view, so a stale signal cannot drive a directive. Every mutation here must
    therefore be visible as an epoch bump.
    """
```

Isso foi verificado contra o kernel real:

```
STALE REFUSED: ControllerInputError — confidence for epoch 1 is stale at epoch 3
```

E é por isso que `admit_ranked` pula candidatos já presentes:

```python
            if candidate.path in self._entries:
                continue
```

> Re-admitir uma entrada resetaria seu epoch e tornaria todo `ConfidenceRecord`
> pendente obsoleto, sem ganho informacional algum.

---

## Cap. 10.6 — Pesos de scoring: cada um com justificativa

| Termo | Peso | Justificativa |
|---|---|---|
| `stacktrace_relevance` | **+3.0** | Um stack trace nomeia o frame que falhou. Nada mais no score é evidência de localização tão direta |
| `task_similarity` | +2.0 × overlap | Sobreposição léxica normalizada |
| `symbol_relevance` | +1.5 | Nome do símbolo bate com stem do arquivo ou aparece no corpo |
| `edit_proximity` | +1.4 | Arquivos que este run já editou |
| `recent_failure_relevance` | +1.2 | Arquivos implicados na última falha |
| `dependency_proximity` | +1.0 | Aresta de import ou co-mudança |
| `plan_relevance` | +1.0 | Nomeado no plano corrente |
| `test_relationship` | +0.8 | Teste mapeado ao alvo |
| `redundancy` | **−2.0** | Conteúdo idêntico já admitido |
| `staleness` | −min(1.5, tok/4000) | Blobs grandes expulsam vários candidatos melhor direcionados |

Pinned ordena primeiro **independente do score**:

```python
    # Pinned candidates sort first regardless of score: pinning is an explicit
    # operator/plan decision and must not be silently overridden by ranking.
    scored.sort(key=lambda pair: (pair[0].pinned, pair[1].total), reverse=True)
```

---

## Cap. 10.7 — Compressão é lossy, logo tem guardas

```python
        entry = self._entries.get(key)
        if entry is None or entry.pinned or entry.token_estimate < 200:
            return False
```

Três recusas: entrada inexistente, entrada pinned, entrada pequena demais.

> Compressão é lossy e irreversível dentro de um run, então nunca toca entrada
> pinned e nunca encolhe algo já pequeno — um resumo de quarenta tokens custa
> mais do que economiza.

---

## Cap. 10.8 — A regra que fecha o anti-padrão §58 no TODO

```python
        # `spec §24`: completion is an evidence claim, so it must carry one.
        if status is TodoStatus.DONE and not (evidence or item.evidence):
            raise TodoTransitionError(
                f"todo {identifier!r} cannot be completed without evidence; "
                f"a model's assertion of success is not verification")
```

Verificado:

```
REFUSED: illegal transition pending -> done for todo 't2'
```

E transições ilegais **levantam**, não viram no-op:

> Uma transição ilegal engolida produz um plano que discorda da trajetória e
> nenhum jeito de dizer qual está certo.

---

## Cap. 10.9 — `from_canonical_dict` ignora a checagem por design

```python
    @classmethod
    def from_canonical_dict(cls, raw: Mapping[str, Any]) -> "TodoManager":
        """Rebuild from a checkpoint. Bypasses transition checks by design:
        a persisted state is already the product of legal transitions."""
```

Reaplicar a validação na reconstrução recusaria estados legítimos: um item
`DONE` restaurado não tem como re-provar a transição que já o produziu.

---

## Cap. 10.10 — Replanning é aditivo

```python
class Replanner:
    """Revises a plan in response to evidence (`spec §17`).

    Revision is additive where possible. Discarding the whole plan on the
    first contradiction throws away the steps that already produced evidence,
    and re-deriving them costs turns the budget cannot spare.
    """
```

E a premissa falsificada é **descartada**, não mantida:

```python
        if trigger is ReplanTrigger.FAILED_ASSUMPTION and assumptions:
            # The falsified assumption is dropped, not silently retained --
            # a plan that still asserts a disproven premise will keep
            # producing the same wrong step.
            assumptions = assumptions[1:]
```

Verificado:

```
REV 1 wrong_localization -> ('Widen the repository search with different terms
                             and symbol lookup', 'Re-identify the owning file...')
```
