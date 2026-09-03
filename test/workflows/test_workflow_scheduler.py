"""Tests for WorkflowScheduler, event-sourced reduction, and cycle enforcement (Invariant I1)."""

from __future__ import annotations

import unittest

from test.transforms.test_transform_runtime import JsonLowerTransform, MemoryBlobStore
from vanguard.packages.domain.workflows.contracts import (
    WorkflowEdge,
    WorkflowNode,
    WorkflowSpec,
)
from vanguard.packages.domain.workflows.reducer import WorkflowState, reduce_workflow
from vanguard.packages.runtime.transform_registry import TransformRegistry
from vanguard.packages.runtime.transform_runtime import TransformRuntime
from vanguard.packages.runtime.workflow_recovery import replay_workflow_events
from vanguard.packages.runtime.workflow_scheduler import WorkflowScheduler


class TestWorkflowScheduler(unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryBlobStore()
        self.registry = TransformRegistry()
        self.registry.register(JsonLowerTransform())
        self.transform_runtime = TransformRuntime(self.store, self.registry)

    def test_pure_transform_workflow_execution(self) -> None:
        spec = WorkflowSpec(
            topology_id="topo.two-stage/1",
            version="1.0.0",
            nodes=(
                WorkflowNode(id="step1", kind="transform", policy_ref="test.lower/1"),
                WorkflowNode(id="step2", kind="transform", policy_ref="test.lower/1"),
            ),
            edges=(
                WorkflowEdge(from_node="step1", to_node="step2", condition="accepted"),
            ),
            entry_node="step1",
        )
        scheduler = WorkflowScheduler(spec, self.transform_runtime, self.store)

        in_digest = self.store.put(b"UPPER INPUT").value
        outcome = scheduler.run("wf-01", initial_artifact_digest=in_digest)

        self.assertTrue(outcome.completed)
        self.assertIsNotNone(outcome.result_digest)
        out_bytes = self.store.get(outcome.result_digest).value
        self.assertEqual(out_bytes, b"upper input")

        # Test replay equivalence (Invariant I9)
        replayed_state = replay_workflow_events("wf-01", "topo.two-stage/1", outcome.events)
        self.assertTrue(replayed_state.completed)
        self.assertEqual(replayed_state.result_digest, outcome.result_digest)

    def test_cycle_limit_enforcement(self) -> None:
        # A cycle between step1 and step2 without terminating condition
        spec = WorkflowSpec(
            topology_id="topo.cycle/1",
            version="1.0.0",
            nodes=(
                WorkflowNode(id="node_a", kind="transform", policy_ref="test.lower/1"),
                WorkflowNode(id="node_b", kind="transform", policy_ref="test.lower/1"),
            ),
            edges=(
                WorkflowEdge(from_node="node_a", to_node="node_b", condition="accepted"),
                WorkflowEdge(from_node="node_b", to_node="node_a", condition="accepted"),
            ),
            entry_node="node_a",
            max_cycles=2,
        )
        scheduler = WorkflowScheduler(spec, self.transform_runtime, self.store)
        in_digest = self.store.put(b"TEST").value
        outcome = scheduler.run("wf-cycle", initial_artifact_digest=in_digest)

        self.assertFalse(outcome.completed)
        self.assertTrue(outcome.final_state.suspended)
        self.assertEqual(outcome.final_state.suspend_reason, "CYCLE_LIMIT_EXCEEDED")

    def test_resume_does_not_reexecute_settled_prefix(self) -> None:
        spec = WorkflowSpec(
            topology_id="topo.resume/1", version="1.0.0",
            nodes=(WorkflowNode("step1", "transform", "test.lower/1"),
                   WorkflowNode("step2", "transform", "test.lower/1")),
            edges=(WorkflowEdge("step1", "step2", "accepted"),), entry_node="step1")
        scheduler = WorkflowScheduler(spec, self.transform_runtime, self.store)
        input_digest = self.store.put(b"RESUME").value
        first = scheduler.run("wf-resume", initial_artifact_digest=input_digest)
        prefix = [event for event in first.events if event["type"] != "WorkflowCompleted"][:2]
        resumed = scheduler.run("wf-resume", initial_artifact_digest=input_digest,
                                prior_events=prefix)
        self.assertTrue(resumed.completed)
        self.assertNotIn("step1", [event["payload"].get("nodeId")
                                    for event in resumed.events
                                    if event["type"] == "NodeScheduled"])


if __name__ == "__main__":
    unittest.main()
