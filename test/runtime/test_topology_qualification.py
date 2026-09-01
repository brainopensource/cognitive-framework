"""BEP-04 qualification vectors for bounded topology lowering/scheduling."""

from __future__ import annotations

import threading
import unittest

from vanguard.packages.domain.workflows import WorkflowEdge, WorkflowNode, WorkflowSpec
from vanguard.packages.runtime.topology import (
    TopologyError, lower_topology, qualification_topology,
)
from vanguard.packages.runtime.workflow_scheduler import WorkflowScheduler


class _Transform:
    def execute(self, _policy: str, digest: str):
        return type("Transform", (), {"output_digest": digest, "status": "passed"})()


class TopologyQualificationTests(unittest.TestCase):
    def test_three_named_graphs_have_expected_role_flow(self) -> None:
        self.assertEqual(
            len(qualification_topology("sequential").roles), 3)
        self.assertEqual(
            len(qualification_topology("reviewer_in_loop").roles), 4)
        parallel = qualification_topology("parallel_investigators")
        lowered = lower_topology(parallel)
        self.assertEqual(lowered["executionMode"], "bounded_parallel")
        self.assertEqual(lowered["schedulerPolicy"], "bounded-parallel-reference")
        self.assertEqual(len(lowered["roleOperations"]), 5)

    def test_unknown_topology_fails_closed(self) -> None:
        with self.assertRaises(TopologyError):
            qualification_topology("unbounded_mailbox")

    def test_delegated_budget_cannot_increase(self) -> None:
        topology = qualification_topology("sequential")
        roles = tuple(
            role if role.role_id != "implementer"
            else type(role)(role.role_id, role.policy_ref, role.scope_template,
                            {"turns": 2, "tokens": 1000}, role.context)
            for role in topology.roles)
        widened = type(topology)(
            topology.topology_id, topology.version, roles,
            topology.edge_records, topology.artifact_flows, topology.entry_role)
        with self.assertRaisesRegex(TopologyError, "exceeds parent"):
            lower_topology(widened)

    def test_parallel_join_waits_for_both_investigators_and_is_bounded(self) -> None:
        active = 0
        peak = 0
        lock = threading.Lock()

        def execute(node, digest):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            with lock:
                active -= 1
            return digest or node.id, "passed"

        nodes = tuple(WorkflowNode(role, "model", role)
                      for role in ("coordinator", "investigator_a",
                                   "investigator_b", "synthesizer", "verifier"))
        edges = (
            WorkflowEdge("coordinator", "investigator_a"),
            WorkflowEdge("coordinator", "investigator_b"),
            WorkflowEdge("investigator_a", "synthesizer"),
            WorkflowEdge("investigator_b", "synthesizer"),
            WorkflowEdge("synthesizer", "verifier"),
        )
        spec = WorkflowSpec("bep04", "1", nodes, edges, "coordinator",
                            execution_mode="bounded_parallel",
                            max_concurrency=2)
        result = WorkflowScheduler(spec, _Transform(), object(),
                                    node_executors={"model": execute}).run("w")
        self.assertTrue(result.completed)
        self.assertEqual(result.final_state.settled_nodes, tuple(
            ("coordinator", "investigator_a", "investigator_b",
             "synthesizer", "verifier")))
        self.assertLessEqual(peak, 2)
        self.assertEqual(
            sum(event["type"] == "LeaseAcquired" for event in result.events), 5)


if __name__ == "__main__":
    unittest.main()
