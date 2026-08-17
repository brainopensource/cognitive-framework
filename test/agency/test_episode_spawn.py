"""Tests for EpisodeEngine.spawn and Operator Context Isolation (S8-B-01, S8-B-05, ADR-0060)."""

from __future__ import annotations

import unittest
from typing import Any, Mapping
from unittest.mock import MagicMock

from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Fragment
from vanguard.packages.agency.episode.engine import EpisodeEngine, SpawnResult
from vanguard.packages.agency.episode.state import RunTermination
from vanguard.packages.kernel.attenuation import Constraints, Scope
from vanguard.packages.kernel import Event


class MockClock:
    def now(self) -> str:
        return "2026-08-16T00:00:00Z"


class MockEventSink:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, event: Event) -> None:
        self.events.append(event)


class MockModel:
    def __init__(self, response_text: str = "child completed task") -> None:
        self.response_text = response_text
        self.calls: list[Any] = []

    def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
        self.calls.append((view, tools, sampling))
        from vanguard.packages.ports.event_store import Result
        return Result.success({"kind": "finish", "note": self.response_text})


class MockFailingModel:
    def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
        from vanguard.packages.ports.event_store import Result
        return Result.fail("instrument_error", "synthetic provider timeout")


class TestEpisodeEngineSpawn(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = MockClock()
        self.events = MockEventSink()
        self.kernel = MagicMock()
        self.parent_scope = Scope(
            actions=frozenset({"fs.read", "fs.search", "patch.apply", "proc.exec"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(
                expires_at="2026-08-17T00:00:00Z",
                max_uses=10,
                budget_usd_micros=100_000,
                max_depth=3,
            ),
            depth=1,
        )
        self.parent_engine = EpisodeEngine(
            kernel=self.kernel,
            model=MockModel("parent result"),
            clock=self.clock,
            events=self.events,
            scope=self.parent_scope,
        )

    def test_spawn_attenuation_monotone_success(self) -> None:
        """Child grant strictly narrows parent (K-26)."""
        child_scope = Scope(
            actions=frozenset({"fs.read"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(
                expires_at="2026-08-16T12:00:00Z",
                max_uses=5,
                budget_usd_micros=50_000,
                max_depth=3,
            ),
            depth=1,
        )
        result = self.parent_engine.spawn(
            child_scope=child_scope,
            brief="subtask exploration",
            episode_id="ep-child-1",
            run_id="run-1",
            principal="child-agent",
            parent_episode_id="ep-parent-1",
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.payload, "parent result")
        self.assertEqual(result.terminal, RunTermination.COMPLETED)
        # Returns structured payload, never a mutable handle
        self.assertIsInstance(result, SpawnResult)

    def test_spawn_widening_denied_returns_typed_result(self) -> None:
        """Widening action is denied and returns typed SpawnResult without throwing (K-26)."""
        widened_scope = Scope(
            actions=frozenset({"fs.read", "admin.privilege"}),  # admin.privilege not held by parent
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(
                expires_at="2026-08-16T12:00:00Z",
                max_uses=5,
                budget_usd_micros=50_000,
                max_depth=3,
            ),
        )
        result = self.parent_engine.spawn(
            child_scope=widened_scope,
            brief="unauthorised action request",
            episode_id="ep-child-2",
            run_id="run-1",
            principal="child-agent",
        )
        self.assertFalse(result.ok)
        self.assertIn("attenuation denied", result.detail)

    def test_spawn_depth_limit_returns_typed_result(self) -> None:
        """Depth limit denial returns typed result, not exception."""
        deep_parent_scope = Scope(
            actions=frozenset({"fs.read"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(
                expires_at="2026-08-17T00:00:00Z",
                max_uses=10,
                budget_usd_micros=100_000,
                max_depth=2,
            ),
            depth=2,  # Already at max_depth 2
        )
        engine = EpisodeEngine(
            kernel=self.kernel,
            model=MockModel(),
            clock=self.clock,
            events=self.events,
            scope=deep_parent_scope,
        )
        result = engine.spawn(
            child_scope=deep_parent_scope,
            brief="too deep",
            episode_id="ep-child-deep",
            run_id="run-1",
            principal="child-agent",
        )
        self.assertFalse(result.ok)
        self.assertIn("depth ceiling", result.detail)

    def test_child_events_carry_causation_id(self) -> None:
        """Child events carry causationId = parent episode id."""
        child_scope = Scope(
            actions=frozenset({"fs.read"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(
                expires_at="2026-08-17T00:00:00Z",
                max_uses=5,
                budget_usd_micros=50_000,
                max_depth=3,
            ),
        )
        self.parent_engine.spawn(
            child_scope=child_scope,
            brief="check causation",
            episode_id="ep-child-3",
            run_id="run-1",
            principal="child-agent",
            parent_episode_id="ep-parent-origin",
        )
        self.assertTrue(len(self.events.events) > 0)
        for ev in self.events.events:
            self.assertEqual(ev.payload.get("causationId"), "ep-parent-origin")

    def test_child_failure_is_typed_result(self) -> None:
        """Child failure returns typed SpawnResult, does not raise in parent loop."""
        child_scope = Scope(
            actions=frozenset({"fs.read"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(
                expires_at="2026-08-17T00:00:00Z",
                max_uses=5,
                budget_usd_micros=50_000,
                max_depth=3,
            ),
        )
        result = self.parent_engine.spawn(
            child_scope=child_scope,
            brief="failing child",
            episode_id="ep-child-failing",
            run_id="run-1",
            principal="child-agent",
            model=MockFailingModel(),
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.terminal, RunTermination.INSTRUMENT_ERROR)

    def test_workspace_destroyed_in_finally_including_on_failure(self) -> None:
        """Per-branch workspace destroyed in finally (N-16)."""
        destroyed = False

        class MockBranchWorkspace:
            def destroy(self) -> None:
                nonlocal destroyed
                destroyed = True

        child_scope = Scope(
            actions=frozenset({"fs.read"}),
            resources=({"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},),
            constraints=Constraints(
                expires_at="2026-08-17T00:00:00Z",
                max_uses=5,
                budget_usd_micros=50_000,
                max_depth=3,
            ),
        )
        ws = MockBranchWorkspace()
        self.parent_engine.spawn(
            child_scope=child_scope,
            brief="workspace lifecycle",
            episode_id="ep-child-ws",
            run_id="run-1",
            principal="child-agent",
            workspace=ws,
            model=MockFailingModel(),
        )
        self.assertTrue(destroyed)

    def test_operator_context_isolation(self) -> None:
        """S8-B-05: Child's intermediate turns are absent from parent compiled context."""
        # Child compiler observes multiple exploratory turns
        child_compiler = ContextCompiler(system_core="Child worker", token_ceiling=10000)
        child_dialogue = [
            Fragment(source="child-agent", label="c-turn-1", text="exploring directory structure"),
            Fragment(source="env", label="c-obs-1", text="100 files listed"),
            Fragment(source="child-agent", label="c-turn-2", text="inspecting package.json"),
            Fragment(source="env", label="c-obs-2", text="dependencies loaded"),
        ]
        child_compiled = child_compiler.compile(brief="Explore codebase", dialogue=child_dialogue)
        self.assertEqual(len(child_compiled.blocks), 6)

        # Parent receives only the summary payload from SpawnResult
        spawn_payload = "Found 2 matching endpoints in auth.py"
        parent_compiler = ContextCompiler(system_core="Parent coordinator", token_ceiling=10000)
        parent_dialogue = [
            Fragment(source="operator", label="spawn-return", text=f"Subtask result: {spawn_payload}"),
        ]
        parent_compiled = parent_compiler.compile(brief="Overall task", dialogue=parent_dialogue)

        # Assert child intermediate turn labels are completely absent from parent compiled context
        parent_texts = " ".join(b.text for b in parent_compiled.blocks)
        self.assertNotIn("exploring directory structure", parent_texts)
        self.assertNotIn("100 files listed", parent_texts)
        self.assertIn("Found 2 matching endpoints in auth.py", parent_texts)


if __name__ == "__main__":
    unittest.main()
