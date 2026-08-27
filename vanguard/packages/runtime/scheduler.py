"""Sequential reference scheduler for M-7.

This is an interface and deterministic reference ordering, not a concurrent
executor.  Read-only grouping is an analysis result and must be explicitly
consumed by a future decision; it is never enabled here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

from ..domain.canonicalisation.digest import digest_of
from ..domain.selectors.independence import disjoint

__all__ = [
    "ReadyOperation",
    "ScheduleDecision",
    "ScheduleError",
    "SchedulerPolicy",
    "SequentialScheduler",
    "ready_operations",
    "safe_read_only_group",
    "schedule_digest",
]


class ScheduleError(ValueError):
    """A readiness graph is malformed and therefore cannot be scheduled."""


@dataclass(frozen=True, slots=True)
class ReadyOperation:
    operation_id: str
    causal_predecessors: tuple[str, ...] = ()
    selector: Mapping[str, Any] | None = None
    sink: str | None = None
    read_only: bool = False


@dataclass(frozen=True, slots=True)
class ScheduleDecision:
    operation_id: str
    wave: int
    parallel: bool = False
    reason: str = "sequential-reference"


class SchedulerPolicy(Protocol):
    def decide(self, operations: Sequence[ReadyOperation], settled: frozenset[str]) -> tuple[ScheduleDecision, ...]: ...


class SequentialScheduler:
    """Fail-closed stable scheduler.  Every operation receives its own wave."""

    def decide(self, operations: Sequence[ReadyOperation], settled: frozenset[str] = frozenset()) -> tuple[ScheduleDecision, ...]:
        ready = ready_operations(operations, settled=settled)
        return tuple(
            ScheduleDecision(operation.operation_id, index, False)
            for index, operation in enumerate(ready)
        )


def ready_operations(
    operations: Sequence[ReadyOperation],
    *,
    settled: frozenset[str] = frozenset(),
) -> tuple[ReadyOperation, ...]:
    """Derive the currently runnable set from settled causal predecessors.

    Blocked operations are absent, never returned with a suggestive decision.
    Returning them was semantically equivalent to scheduling work whose inputs
    did not exist. Unknown predecessors and duplicate identities fail closed.
    """
    by_id: dict[str, ReadyOperation] = {}
    for operation in operations:
        if not operation.operation_id:
            raise ScheduleError("operation_id is required")
        if operation.operation_id in by_id:
            raise ScheduleError(f"duplicate operation_id {operation.operation_id!r}")
        by_id[operation.operation_id] = operation
    known = frozenset(by_id) | settled
    for operation in operations:
        if operation.operation_id in operation.causal_predecessors:
            raise ScheduleError(
                f"operation {operation.operation_id!r} depends on itself")
        unknown = sorted(set(operation.causal_predecessors) - known)
        if unknown:
            raise ScheduleError(
                f"operation {operation.operation_id!r} has unknown predecessors {unknown}")
    return tuple(sorted(
        (operation for operation in operations
         if operation.operation_id not in settled
         and set(operation.causal_predecessors) <= settled),
        key=lambda operation: operation.operation_id,
    ))


def safe_read_only_group(operations: Sequence[ReadyOperation]) -> tuple[str, ...]:
    """Prove an analysis-only group under the already-allowed read rule.

    This does not execute the group. Shared observation/advisory sinks are
    non-mutating; every other shared or unknown sink is treated as exclusive.
    """
    if not operations or any(not op.read_only or op.selector is None or op.sink is None for op in operations):
        return ()
    non_exclusive = frozenset({"observation", "advisory"})
    for index, left in enumerate(operations):
        for right in operations[index + 1:]:
            if left.causal_predecessors or right.causal_predecessors:
                return ()
            try:
                if (left.sink == right.sink and left.sink not in non_exclusive) or not disjoint(
                    left.selector, right.selector
                ):
                    return ()
            except Exception:
                return ()
    return tuple(sorted(op.operation_id for op in operations))


def schedule_digest(decisions: Sequence[ScheduleDecision]) -> str:
    return digest_of([{ "operationId": d.operation_id, "wave": d.wave,
                       "parallel": d.parallel, "reason": d.reason } for d in decisions])
