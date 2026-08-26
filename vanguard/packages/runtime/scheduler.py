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

__all__ = ["ReadyOperation", "ScheduleDecision", "SchedulerPolicy", "SequentialScheduler"]


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
        pending = sorted(operations, key=lambda op: op.operation_id)
        decisions: list[ScheduleDecision] = []
        for index, operation in enumerate(pending):
            if any(dep not in settled and dep in {x.operation_id for x in pending} for dep in operation.causal_predecessors):
                decisions.append(ScheduleDecision(operation.operation_id, index, False, "causal-dependency"))
            else:
                decisions.append(ScheduleDecision(operation.operation_id, index, False))
        return tuple(decisions)


def safe_read_only_group(operations: Sequence[ReadyOperation]) -> tuple[str, ...]:
    """Return a group only when every safety precondition is explicit."""
    if not operations or any(not op.read_only or op.selector is None or op.sink is None for op in operations):
        return ()
    for index, left in enumerate(operations):
        for right in operations[index + 1:]:
            if left.causal_predecessors or right.causal_predecessors:
                return ()
            try:
                if left.sink == right.sink or not disjoint(left.selector, right.selector):
                    return ()
            except Exception:
                return ()
    return tuple(sorted(op.operation_id for op in operations))


def schedule_digest(decisions: Sequence[ScheduleDecision]) -> str:
    return digest_of([{ "operationId": d.operation_id, "wave": d.wave,
                       "parallel": d.parallel, "reason": d.reason } for d in decisions])
