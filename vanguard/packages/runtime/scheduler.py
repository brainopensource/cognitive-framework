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
    "AsyncGraphScheduler",
    "ready_operations",
    "safe_read_only_group",
    "schedule_digest",
    "execute_graph_async",
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


class AsyncGraphScheduler:
    """Concurrent non-blocking DAG scheduler for disjoint resource branches (EVO-14).

    Schedules ready operations in parallel waves when their resource selectors
    are proven disjoint or when all operations are read-only with non-exclusive sinks.
    Conflicting operations fall back safely to sequential waves.
    """

    def decide(
        self,
        operations: Sequence[ReadyOperation],
        settled: frozenset[str] = frozenset(),
    ) -> tuple[ScheduleDecision, ...]:
        ready = ready_operations(operations, settled=settled)
        if not ready:
            return ()

        decisions: list[ScheduleDecision] = []
        remaining = list(ready)
        current_wave = 0
        non_exclusive_sinks = frozenset({"observation", "advisory", "audit"})

        while remaining:
            current_batch: list[ReadyOperation] = []
            next_remaining: list[ReadyOperation] = []

            for op in remaining:
                can_add = True
                for batch_op in current_batch:
                    # If both are read-only with non-exclusive sinks, they can safely co-exist
                    if op.read_only and batch_op.read_only:
                        if op.sink in non_exclusive_sinks and batch_op.sink in non_exclusive_sinks:
                            continue

                    # Check disjointness of resource selectors
                    if op.selector is not None and batch_op.selector is not None:
                        try:
                            if not disjoint(op.selector, batch_op.selector):
                                can_add = False
                                break
                        except Exception:
                            can_add = False
                            break
                    else:
                        can_add = False
                        break

                if can_add:
                    current_batch.append(op)
                else:
                    next_remaining.append(op)

            is_parallel = len(current_batch) > 1
            for op in current_batch:
                decisions.append(
                    ScheduleDecision(
                        operation_id=op.operation_id,
                        wave=current_wave,
                        parallel=is_parallel,
                        reason="disjoint-resource-parallel" if is_parallel else "sequential-fallback",
                    )
                )
            current_wave += 1
            remaining = next_remaining

        return tuple(decisions)


async def execute_graph_async(
    operations: Sequence[ReadyOperation],
    executor: Any,
    *,
    settled: frozenset[str] = frozenset(),
    scheduler: SchedulerPolicy | None = None,
) -> list[Any]:
    """Execute a DAG of operations wave-by-wave with async parallelism."""
    import asyncio

    sched = scheduler or AsyncGraphScheduler()
    decisions = sched.decide(operations, settled=settled)
    if not decisions:
        return []

    # Group by wave
    by_wave: dict[int, list[str]] = {}
    for d in decisions:
        by_wave.setdefault(d.wave, []).append(d.operation_id)

    op_map = {op.operation_id: op for op in operations}
    results: list[Any] = []

    for wave_num in sorted(by_wave):
        wave_op_ids = by_wave[wave_num]
        wave_ops = [op_map[op_id] for op_id in wave_op_ids]
        
        # Execute wave concurrently
        tasks = [executor(op) for op in wave_ops]
        wave_results = await asyncio.gather(*tasks)
        results.extend(wave_results)

    return results


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
