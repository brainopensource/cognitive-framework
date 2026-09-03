"""M-5a Dev B contracts: execution values and deterministic AgentView fold."""

from __future__ import annotations

import unittest

from vanguard.packages.domain.execution import (
    ExecutionScope,
    InvalidScopeAttenuation,
    LineageRef,
    OperationRecord,
    OperationStatus,
)
from vanguard.packages.domain.ledger.agent_view import fold_agent_view
from vanguard.packages.domain.ledger.events import EventEnvelope


def event(seq: int, kind: str, **payload: object) -> EventEnvelope:
    return EventEnvelope(
        schema_version="mhf.event/2",
        event_id=f"event-{seq}",
        scope="episode",
        seq=str(seq),
        occurred_at=f"2026-08-25T00:00:{seq:02d}.000Z",
        recorded_at=f"2026-08-25T00:00:{seq:02d}.000Z",
        principal="agent-1",
        principal_role="episode",
        tenant_id="tenant-default",
        owner_id="owner-platform",
        confidentiality="internal",
        retention_class="standard",
        trainability="prohibited",
        redaction_status="none",
        payload={"kind": kind, **payload},
        run_id="run-1",
        episode_id="episode-1",
        project_id="project-1",
        principal_id="lineage-1",
        authority_source="orchestrator-policy",
        policy_version="m5a-test",
    )


class ExecutionValueContracts(unittest.TestCase):
    def test_scope_child_is_strictly_narrowed(self) -> None:
        parent = ExecutionScope(
            lineage_id="root",
            budget={"tokens": 100, "bytes": 1000},
            max_depth=3,
            max_turns=8,
            capability_grant="grant-root",
            terminal_conditions=("verified_done",),
        )
        child = parent.attenuated_for_child(
            lineage_id="child",
            budget_slice={"tokens": 50, "bytes": 500},
            max_depth=2,
            max_turns=4,
            capability_grant="grant-child",
        )
        self.assertEqual(child.max_depth, 2)
        self.assertEqual(child.budget["tokens"], 50)
        with self.assertRaises(InvalidScopeAttenuation):
            parent.attenuated_for_child(
                lineage_id="child-2",
                budget_slice={"tokens": 101},
                capability_grant="grant-child-2",
            )

    def test_lineage_and_operation_are_value_contracts(self) -> None:
        self.assertEqual(LineageRef("root", None, "root", 0).depth, 0)
        operation = OperationRecord(
            operation_id="op-1",
            verb="read",
            input_refs=("sha256:in",),
            output_refs=(),
            causation_id=None,
            lineage_id="root",
            scope_digest="sha256:scope",
            status=OperationStatus.PROPOSED,
            resources={"tokens": 2},
        )
        self.assertEqual(operation.status, OperationStatus.PROPOSED)


class AgentViewFold(unittest.TestCase):
    def test_semantic_history_folds_into_projection(self) -> None:
        events = [
            event(0, "GoalDeclared", goalDigest="sha256:" + "a" * 64),
            event(1, "PlanRevised", revision=0, planDigest="sha256:" + "b" * 64),
            event(2, "ProposalProduced", operationId="op-1", verb="proc.exec"),
            event(3, "EffectStarted", operationId="op-1", descriptorDigest="sha256:" + "c" * 64),
            event(4, "EffectCompleted", operationId="op-1", action="proc.exec", idempotencyKey="idem-1", outcome="ok"),
            event(5, "BudgetCommitted", settlement={"tokens": 7, "millis": 3}),
            event(6, "StrategyChanged", **{"from": "breadth", "to": "depth", "trigger": "stalled"}),
            event(7, "ProgressAssessed", assessment="advancing", signals={"tests": "green"}, basis=["event-4"]),
            event(8, "ContextCompacted", inputDigest="sha256:" + "d" * 64, outputDigest="sha256:" + "e" * 64),
            event(9, "EpisodeCompleted", outcome="resolved"),
        ]
        view = fold_agent_view(None, events)
        self.assertEqual(view.lineage_id, "lineage-1")
        self.assertEqual(view.goal, "sha256:" + "a" * 64)
        self.assertEqual(len(view.plan_revisions), 1)
        self.assertEqual(view.strategy, "depth")
        self.assertEqual(view.progress_log[0]["assessment"], "advancing")
        self.assertEqual(view.context_epoch, 1)
        self.assertEqual(view.settled_effects["idem-1"], "ok")
        self.assertEqual(view.budget_consumed, {"millis": 3, "tokens": 7})
        self.assertEqual(view.attempts[0]["verb"], "proc.exec")
        self.assertEqual(view.attempts[1]["status"], "dispatched")
        self.assertEqual(view.attempts[2]["verb"], "proc.exec")
        self.assertEqual(view.attempts[2]["status"], "ok")
        self.assertEqual(view.terminal, "resolved")
        self.assertEqual(view.covered_through, "event-9")

    def test_deprecated_history_is_readable_and_noop(self) -> None:
        view = fold_agent_view(None, [event(0, "OperatorInvoked")])
        self.assertEqual(view.lineage_id, "lineage-1")
        self.assertEqual(view.attempts, ())

    def test_child_lifecycle_and_failed_effects_fold(self) -> None:
        events = [
            event(0, "GoalDeclared", goalDigest="sha256:" + "0" * 64),
            event(1, "ChildSpawned", childId="child-sub-1", role="subagent"),
            event(2, "ProposalProduced", operationId="op-2", action="fs.write"),
            event(3, "EffectFailed", operationId="op-2", action="fs.write", idempotencyKey="idem-2", outcome="failed"),
            event(4, "ChildReturned", childId="child-sub-1", status="success"),
            event(5, "BudgetCommitted", settlement={"bytes": 1024, "usd_micros": 500}),
            event(6, "EpisodeCompleted", outcome="completed"),
        ]
        view = fold_agent_view(None, events)
        self.assertEqual(len(view.children), 1)
        self.assertEqual(view.children[0]["childId"], "child-sub-1")
        self.assertEqual(view.children[0]["status"], "success")
        self.assertEqual(view.settled_effects["idem-2"], "failed")
        self.assertEqual(view.budget_consumed, {"bytes": 1024, "usd_micros": 500})
        self.assertEqual(view.terminal, "completed")
        self.assertEqual(view.covered_through, "event-6")


if __name__ == "__main__":
    unittest.main()
