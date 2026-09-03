"""Contract test for EVO-14: Async Concurrent Lineage Execution & Graph Scheduler.

Owning contract: EVO-14, GTS-13C §7.2, ADR-0096 §14.5.
Invariants:
- Disjoint resource branches execute in parallel waves.
- Overlapping resource selectors fall back to sequential wave ordering.
- Causal predecessors strictly constrain wave assignment.
- execute_graph_async completes waves deterministically.
"""

from __future__ import annotations

import asyncio
import unittest

from vanguard.packages.runtime.scheduler import (
    AsyncGraphScheduler,
    ReadyOperation,
    ScheduleDecision,
    execute_graph_async,
)


class TestEvo14AsyncScheduler(unittest.TestCase):
    def setUp(self) -> None:
        self.scheduler = AsyncGraphScheduler()

    def test_disjoint_privileged_writes_still_run_sequentially(self) -> None:
        """ADR-0099 rule 4 / ADR-0106: writes stay sequential regardless of
        selector disjointness -- only read-only, non-exclusive-sink pairs may
        share a parallel wave. This was previously (incorrectly, and without
        the evidence ADR-0099 rule 5 requires) asserting `privileged`-sink
        operations went parallel just because their selectors didn't
        overlap; corrected after ADR-0106's preregistered study validated
        only the read-only case."""
        ops = [
            ReadyOperation(
                operation_id="op_a",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/a"]},
                sink="privileged",
            ),
            ReadyOperation(
                operation_id="op_b",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/b"]},
                sink="privileged",
            ),
        ]
        decisions = self.scheduler.decide(ops)
        self.assertEqual(len(decisions), 2)
        self.assertEqual(decisions[0].wave, 0)
        self.assertEqual(decisions[1].wave, 1)
        self.assertFalse(decisions[0].parallel)
        self.assertFalse(decisions[1].parallel)

    def test_disjoint_read_only_operations_with_non_exclusive_sinks_run_in_parallel(self) -> None:
        """The case ADR-0106 actually authorizes: read-only, non-exclusive-sink,
        disjoint-selector operations may share a parallel wave."""
        ops = [
            ReadyOperation(
                operation_id="op_a",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/a"]},
                sink="observation", read_only=True,
            ),
            ReadyOperation(
                operation_id="op_b",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/b"]},
                sink="observation", read_only=True,
            ),
        ]
        decisions = self.scheduler.decide(ops)
        self.assertEqual(len(decisions), 2)
        self.assertEqual(decisions[0].wave, 0)
        self.assertEqual(decisions[1].wave, 0)
        self.assertTrue(decisions[0].parallel)
        self.assertTrue(decisions[1].parallel)

    def test_conflicting_resources_scheduled_sequentially(self) -> None:
        """Prove that operations with overlapping selectors are split into separate waves."""
        ops = [
            ReadyOperation(
                operation_id="op_a",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]},
                sink="privileged",
            ),
            ReadyOperation(
                operation_id="op_b",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/deep"]},
                sink="privileged",
            ),
        ]
        decisions = self.scheduler.decide(ops)
        self.assertEqual(len(decisions), 2)
        self.assertEqual(decisions[0].wave, 0)
        self.assertEqual(decisions[1].wave, 1)
        self.assertFalse(decisions[0].parallel)
        self.assertFalse(decisions[1].parallel)

    def test_causal_predecessors_constrain_waves(self) -> None:
        """Prove that causal dependencies prevent downstream operations from running until predecessors settle."""
        ops = [
            ReadyOperation(operation_id="root", selector={"kind": "fs", "root": "/workspace", "paths": ["/a"]}),
            ReadyOperation(
                operation_id="child",
                causal_predecessors=("root",),
                selector={"kind": "fs", "root": "/workspace", "paths": ["/b"]},
            ),
        ]
        # When root is not settled, only root is runnable
        decisions_1 = self.scheduler.decide(ops, settled=frozenset())
        self.assertEqual(len(decisions_1), 1)
        self.assertEqual(decisions_1[0].operation_id, "root")

        # When root is settled, child becomes runnable
        decisions_2 = self.scheduler.decide(ops, settled=frozenset({"root"}))
        self.assertEqual(len(decisions_2), 1)
        self.assertEqual(decisions_2[0].operation_id, "child")

    def test_read_only_observation_operations_parallel(self) -> None:
        """Prove read-only operations with observation sinks can execute in parallel."""
        ops = [
            ReadyOperation(
                operation_id="read_1",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
                sink="observation",
                read_only=True,
            ),
            ReadyOperation(
                operation_id="read_2",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
                sink="observation",
                read_only=True,
            ),
        ]
        decisions = self.scheduler.decide(ops)
        self.assertEqual(len(decisions), 2)
        self.assertEqual(decisions[0].wave, 0)
        self.assertEqual(decisions[1].wave, 0)
        self.assertTrue(decisions[0].parallel)

    def test_execute_graph_async_execution(self) -> None:
        """Verify execute_graph_async completes operations and aggregates results."""
        ops = [
            ReadyOperation(
                operation_id="op_1",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace/1"]},
            ),
            ReadyOperation(
                operation_id="op_2",
                selector={"kind": "fs", "root": "/workspace", "paths": ["/workspace/2"]},
            ),
        ]

        async def mock_executor(op: ReadyOperation) -> str:
            await asyncio.sleep(0.01)
            return f"done_{op.operation_id}"

        results = asyncio.run(execute_graph_async(ops, mock_executor))
        self.assertEqual(len(results), 2)
        self.assertIn("done_op_1", results)
        self.assertIn("done_op_2", results)


if __name__ == "__main__":
    unittest.main()
