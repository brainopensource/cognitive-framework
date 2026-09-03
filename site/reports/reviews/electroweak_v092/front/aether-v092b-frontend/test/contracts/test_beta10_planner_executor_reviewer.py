"""BETA-10: Multi-agent Planner / Executor / Reviewer composition and settlement.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md BETA-10, S8-B-01.

Invariants:
- Three roles execute through scoped spawn and one unified settlement authority.
- Authority is monotonically attenuated: child authority never exceeds parent authority.
- Every child has an attributable lineage and causal parent.
- Planner has no execution verbs; Executor has attenuated execution verbs; Reviewer evaluates and critiques.
- Terminal settlement occurs deterministically without kernel modification.
"""

from __future__ import annotations

import unittest
from typing import Any, Mapping
from unittest.mock import MagicMock

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.agency import EpisodeEngine, RunTermination
from vanguard.packages.agency.episode.state import SpawnResult
from vanguard.packages.kernel import Event
from vanguard.packages.kernel.attenuation import Constraints, Scope, attenuate
from vanguard.packages.kernel.model import FailurePath


class DeterministicClock:
    def __init__(self, start: int = 1000) -> None:
        self._t = start

    def now(self) -> str:
        self._t += 1
        return f"2026-08-28T00:00:{self._t:02d}.000Z"

    def now_ms(self) -> int:
        self._t += 10
        return self._t


class MockEventSink:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, event: Event) -> None:
        self.events.append(event)


class TestBeta10PlannerExecutorReviewer(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = DeterministicClock()
        self.events = MockEventSink()
        self.kernel = MagicMock()
        mock_dispatch = MagicMock()
        mock_dispatch.failure = FailurePath.OK
        mock_dispatch.outcome = MagicMock()
        mock_dispatch.outcome.result_digest = "sha256:result-digest"
        self.kernel.dispatch.return_value = mock_dispatch

    def test_planner_executor_reviewer_composition_lifecycle(self) -> None:
        """Execute 3-role workflow: Planner plans -> spawns Executor -> spawns Reviewer -> settles."""
        # Root Parent Scope (Orchestrator/Planner)
        parent_constraints = Constraints(
            expires_at="2026-12-31T23:59:59.000Z",
            max_uses=100,
            budget_usd_micros=1_000_000,
            max_depth=3,
        )
        parent_scope = Scope(
            actions=frozenset({"spawn", "plan", "review", "fs.read", "patch.apply", "finish"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=parent_constraints,
            depth=0,
        )

        # 1. Planner model: decomposes task into subgoals, finishes planning
        planner_model = FakeModel([
            {
                "kind": "finish",
                "note": "Planner: task decomposed into execution and review phases",
            }
        ])

        planner_engine = EpisodeEngine(
            kernel=self.kernel,
            model=planner_model,
            clock=self.clock,
            events=self.events,
            scope=parent_scope,
            max_turns=5,
        )

        planner_outcome = planner_engine.run(
            episode_id="ep-planner-01",
            run_id="run-beta10-01",
            principal="planner-agent",
            brief="Optimize backend routing routine",
        )
        self.assertEqual(planner_outcome.terminal, RunTermination.COMPLETED)

        # 2. Spawn Executor child with attenuated authority (only fs.read + patch.apply, NO spawn authority)
        executor_constraints = Constraints(
            expires_at="2026-12-31T23:59:59.000Z",
            max_uses=50,
            budget_usd_micros=500_000,
            max_depth=2,
        )
        executor_scope = Scope(
            actions=frozenset({"fs.read", "patch.apply", "finish"}),
            resources=parent_scope.resources,
            constraints=executor_constraints,
            depth=1,
        )

        # Verify child authority strictly narrows parent (K-26)
        attenuation = attenuate(parent_scope, executor_scope)
        self.assertTrue(attenuation.ok)
        self.assertNotIn("spawn", executor_scope.actions, "Executor child must not have spawn authority")

        executor_model = FakeModel([
            {
                "kind": "finish",
                "note": "Executor: patched router.py successfully and verified AST",
            }
        ])

        spawn_executor_res: SpawnResult = planner_engine.spawn(
            child_scope=executor_scope,
            brief="Execute router optimization patch",
            episode_id="ep-executor-01",
            run_id="run-beta10-01",
            principal="executor-agent",
            parent_episode_id="ep-planner-01",
            model=executor_model,
        )

        self.assertTrue(spawn_executor_res.ok)
        self.assertEqual(spawn_executor_res.terminal, RunTermination.COMPLETED)
        self.assertIn("patched router.py", spawn_executor_res.payload)

        # 3. Spawn Reviewer child with strictly read-only audit authority
        reviewer_constraints = Constraints(
            expires_at="2026-12-31T23:59:59.000Z",
            max_uses=20,
            budget_usd_micros=200_000,
            max_depth=2,
        )
        reviewer_scope = Scope(
            actions=frozenset({"fs.read", "review", "finish"}),
            resources=parent_scope.resources,
            constraints=reviewer_constraints,
            depth=1,
        )
        self.assertNotIn("patch.apply", reviewer_scope.actions, "Reviewer must be strictly read-only")

        reviewer_model = FakeModel([
            {
                "kind": "finish",
                "note": "Reviewer: verification approved, zero security invariants violated",
            }
        ])

        spawn_reviewer_res: SpawnResult = planner_engine.spawn(
            child_scope=reviewer_scope,
            brief="Audit executor changes for correctness and security",
            episode_id="ep-reviewer-01",
            run_id="run-beta10-01",
            principal="reviewer-agent",
            parent_episode_id="ep-planner-01",
            model=reviewer_model,
        )

        self.assertTrue(spawn_reviewer_res.ok)
        self.assertEqual(spawn_reviewer_res.terminal, RunTermination.COMPLETED)
        self.assertIn("verification approved", spawn_reviewer_res.payload)

        # 4. Verify causal parent linkage in emitted event stream
        emitted_events = self.events.events
        causation_ids = [
            e.payload.get("causationId")
            for e in emitted_events
            if isinstance(getattr(e, "payload", None), Mapping) and "causationId" in e.payload
        ]
        self.assertIn("ep-planner-01", causation_ids, "Child events must carry parent causation ID")

    def test_child_scope_escalation_is_denied_fail_closed(self) -> None:
        """Attempting to spawn a child with broader authority than parent fails closed immediately."""
        parent_constraints = Constraints(
            expires_at="2026-12-31T23:59:59.000Z",
            max_uses=100,
            budget_usd_micros=1_000_000,
            max_depth=2,
        )
        parent_scope = Scope(
            actions=frozenset({"fs.read", "spawn", "finish"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=parent_constraints,
            depth=0,
        )

        # Child requests 'proc.exec' and 'net.listen' which parent does NOT possess
        escalated_constraints = Constraints(
            expires_at="2026-12-31T23:59:59.000Z",
            max_uses=100,
            budget_usd_micros=1_000_000,
            max_depth=2,
        )
        escalated_scope = Scope(
            actions=frozenset({"fs.read", "proc.exec", "net.listen", "finish"}),
            resources=parent_scope.resources,
            constraints=escalated_constraints,
            depth=1,
        )

        engine = EpisodeEngine(
            kernel=self.kernel,
            model=FakeModel([]),
            clock=self.clock,
            events=self.events,
            scope=parent_scope,
        )

        res = engine.spawn(
            child_scope=escalated_scope,
            brief="Unauthorized escalation attempt",
            episode_id="ep-escalated-01",
            run_id="run-beta10-escalate",
            principal="malicious-agent",
        )

        self.assertFalse(res.ok)
        self.assertEqual(res.terminal, RunTermination.ABANDONED)
        self.assertIn("attenuation denied", res.detail)


if __name__ == "__main__":
    unittest.main()
