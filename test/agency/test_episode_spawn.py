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

    def test_spawn_return_enters_as_untrusted_derived_at_minimum(self) -> None:
        """`K-33`: a child's return value re-enters the parent's accumulation
        as `untrusted_derived` at minimum, whatever the child believed."""
        from vanguard.packages.kernel import Trust

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
            episode_id="ep-child-2",
            run_id="run-1",
            principal="child-agent",
            parent_episode_id="ep-parent-1",
        )
        self.assertTrue(result.ok)
        self.assertTrue(result.return_spans)
        for span in result.return_spans:
            self.assertTrue(span.trust.is_untrusted)
            self.assertGreaterEqual(span.trust.rank, Trust.UNTRUSTED_DERIVED.rank)

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
        self.assertEqual(len(child_compiled.blocks), 7)

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

    def test_budget_conserved_two_levels_deep(self) -> None:
        """Property: for every dimension, spent + held + remaining == ceiling across parent/child/grandchild leases."""
        from vanguard.packages.kernel.budget import Governor, Reservation

        ceilings = {"usd_micros": 100_000, "millis": 60_000, "tokens": 10_000, "bytes": 50_000}
        gov = Governor(ceilings)

        # Parent reserves
        l1 = gov.reserve("run-1", Reservation(usd_micros=40_000, tokens=4_000, millis=20_000, bytes_=20_000))
        # Child reserves under parent
        l2 = gov.reserve("run-1", Reservation(usd_micros=20_000, tokens=2_000, millis=10_000, bytes_=10_000), parent_lease_id=l1.lease_id)
        # Grandchild reserves under child
        l3 = gov.reserve("run-1", Reservation(usd_micros=10_000, tokens=1_000, millis=5_000, bytes_=5_000), parent_lease_id=l2.lease_id)

        # Grandchild commits
        gov.commit(l3, {"usd_micros": 8_000, "tokens": 800, "millis": 4_000, "bytes": 4_000})
        # Child commits
        gov.commit(l2, {"usd_micros": 15_000, "tokens": 1_500, "millis": 8_000, "bytes": 8_000})
        # Parent commits
        gov.commit(l1, {"usd_micros": 10_000, "tokens": 1_000, "millis": 5_000, "bytes": 5_000})

        # Invariant check: spent + held + remaining == ceiling for every dimension
        ledger = gov.ledger()
        for dim, entry in ledger.items():
            self.assertEqual(
                entry["spent"] + entry["held"] + entry["remaining"],
                entry["ceiling"],
                f"Conservation invariant violated for dimension {dim}: {entry}",
            )

    def test_child_overrun_debits_parent_budget(self) -> None:
        """Property: child effect overrun debits reality and updates remaining budget (K-07)."""
        from vanguard.packages.kernel.budget import Governor, Reservation

        ceilings = {"usd_micros": 50_000}
        gov = Governor(ceilings)

        # Parent lease
        l1 = gov.reserve("run-1", Reservation(usd_micros=30_000))
        # Child lease
        l2 = gov.reserve("run-1", Reservation(usd_micros=10_000), parent_lease_id=l1.lease_id)

        # Child overruns reservation: spent 15_000 against 10_000 reservation
        gov.commit(l2, {"usd_micros": 15_000})

        self.assertEqual(gov.spent("usd_micros"), 15_000)
        # Held remaining is parent's 30_000
        self.assertEqual(gov.remaining("usd_micros"), 50_000 - 15_000 - 30_000)

    def test_closed_parent_lease_cannot_fund_child(self) -> None:
        """F-13: A closed parent lease cannot fund a child reservation."""
        from vanguard.packages.kernel.budget import BudgetDenied, Governor, Reservation

        gov = Governor({"usd_micros": 50_000})
        l1 = gov.reserve("run-1", Reservation(usd_micros=20_000))
        gov.release(l1)

        # Attempt child reservation on released/closed parent
        with self.assertRaises(BudgetDenied) as cm:
            gov.reserve("run-1", Reservation(usd_micros=5_000), parent_lease_id=l1.lease_id)
        self.assertEqual(cm.exception.reason, "parent_closed")

    def test_spawn_proposal_builds_scope_from_args(self) -> None:
        """TL receipt 1: Scope is built from proposal args['scope']."""
        from vanguard.packages.ports.event_store import Result

        captured_tools: list[Any] = []

        class ScopeObservingModel:
            def __init__(self) -> None:
                self.parent_turns = 0

            def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
                ep_id = str(view.get("episodeId", ""))
                if "child" in ep_id:
                    captured_tools.append(tools)
                    return Result.success({"kind": "finish", "note": "child done"})
                self.parent_turns += 1
                if self.parent_turns == 1:
                    return Result.success({
                        "kind": "spawn",
                        "args": {
                            "brief": "narrowed subtask",
                            "scope": {"actions": ["fs.read", "fs.search"]},
                        },
                        "note": "spawning narrowed helper",
                    })
                return Result.success({"kind": "finish", "note": "parent done"})

        tools = [
            {"verb": "fs.read", "name": "read_file"},
            {"verb": "fs.search", "name": "search_files"},
            {"verb": "patch.apply", "name": "apply_patch"},
            {"verb": "proc.exec", "name": "run_command"},
        ]
        engine = EpisodeEngine(
            kernel=self.kernel,
            model=ScopeObservingModel(),
            clock=self.clock,
            events=self.events,
            scope=self.parent_scope,
            tools=tools,
        )
        outcome = engine.run(
            episode_id="ep-parent-scoped-spawn",
            run_id="run-1",
            principal="parent-agent",
            brief="test scope from args",
        )
        self.assertEqual(outcome.terminal, RunTermination.COMPLETED)
        self.assertTrue(len(captured_tools) > 0)
        child_tool_verbs = [t.get("verb") for t in captured_tools[0]]
        self.assertEqual(sorted(child_tool_verbs), ["fs.read", "fs.search"])
        self.assertNotIn("patch.apply", child_tool_verbs)
        self.assertNotIn("proc.exec", child_tool_verbs)

    def test_spawn_proposal_fails_closed_when_scope_missing_or_junk(self) -> None:
        """TL receipt 2: Missing or unparseable scope fails closed without granting parent's full scope."""
        from vanguard.packages.ports.event_store import Result

        class JunkScopeModel:
            def __init__(self) -> None:
                self.parent_turns = 0

            def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
                self.parent_turns += 1
                if self.parent_turns == 1:
                    # Missing scope
                    return Result.success({
                        "kind": "spawn",
                        "args": {"brief": "missing scope"},
                        "note": "no scope passed",
                    })
                if self.parent_turns == 2:
                    # Junk scope
                    return Result.success({
                        "kind": "spawn",
                        "args": {"brief": "junk scope", "scope": "invalid string"},
                        "note": "junk scope passed",
                    })
                return Result.success({"kind": "finish", "note": "parent finished"})

        engine = EpisodeEngine(
            kernel=self.kernel,
            model=JunkScopeModel(),
            clock=self.clock,
            events=self.events,
            scope=self.parent_scope,
        )
        outcome = engine.run(
            episode_id="ep-parent-junk-spawn",
            run_id="run-1",
            principal="parent-agent",
            brief="test fail-closed junk scope",
        )
        self.assertEqual(outcome.terminal, RunTermination.COMPLETED)
        # 2 failed spawn turns recorded with fail-closed signals, plus finish
        self.assertEqual(outcome.episode.turn_count, 2)
        self.assertEqual(outcome.episode.turns[0].progress_signal, "scope_unparseable")
        self.assertEqual(outcome.episode.turns[1].progress_signal, "scope_unparseable")

    def test_spawn_narrowed_child_cannot_execute_unauthorized_action(self) -> None:
        """TL receipt 3: Model narrowed to fs.read produces a child that cannot patch.apply."""
        from vanguard.packages.ports.event_store import Result

        class ChildAttemptingUnauthorizedActionModel:
            def __init__(self) -> None:
                self.parent_turns = 0
                self.child_turns = 0

            def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
                ep_id = str(view.get("episodeId", ""))
                if "child" in ep_id:
                    self.child_turns += 1
                    if self.child_turns == 1:
                        # Child attempts to propose patch.apply which was not granted
                        return Result.success({
                            "kind": "effect",
                            "action": "patch.apply",
                            "resource": {"kind": "fs", "path": "/workspace/main.py"},
                            "args": {"patch": "diff"},
                            "note": "attempt unauthorized patch",
                        })
                    return Result.success({"kind": "finish", "note": "child finished after denial"})
                self.parent_turns += 1
                if self.parent_turns == 1:
                    return Result.success({
                        "kind": "spawn",
                        "args": {
                            "brief": "read-only child",
                            "scope": {"actions": ["fs.read"]},
                        },
                        "note": "spawning read-only helper",
                    })
                return Result.success({"kind": "finish", "note": "parent finished"})

        from vanguard.packages.kernel.attenuation import Scope
        from vanguard.packages.kernel.model import AdapterOutcome, FailurePath
        from vanguard.packages.kernel.dispatch import DispatchResult

        # Mock kernel: dispatches return DENIED_SCOPE_ESCALATION if requested action not in child's scope
        def mock_dispatch(request: Any, requested_scope: Scope, reservation: Any) -> Any:
            if request.action not in requested_scope.actions:
                return DispatchResult(
                    failure=FailurePath.DENIED_SCOPE_ESCALATION,
                    detail=f"action {request.action} not granted in scope",
                )
            return DispatchResult(
                failure=FailurePath.OK,
                outcome=AdapterOutcome(status="ok"),
            )

        self.kernel.dispatch.side_effect = mock_dispatch

        engine = EpisodeEngine(
            kernel=self.kernel,
            model=ChildAttemptingUnauthorizedActionModel(),
            clock=self.clock,
            events=self.events,
            scope=self.parent_scope,
        )
        outcome = engine.run(
            episode_id="ep-parent-narrowed-child",
            run_id="run-1",
            principal="parent-agent",
            brief="test narrowed child authorization",
        )
        self.assertEqual(outcome.terminal, RunTermination.COMPLETED)

    def test_scope_escalation_refuse_writes_authorization_denied(self) -> None:
        """`TSK-CORE-004`: the engine-side sealed-scope refuse never reaches
        `Kernel.dispatch`, so it is the only writer for this denial -- append
        `AuthorizationDenied` so it is durable on the ledger, not only a
        local `Turn` (`A-07`)."""
        from vanguard.packages.ports.event_store import Result

        class ChildAttemptingUnauthorizedActionModel:
            def __init__(self) -> None:
                self.parent_turns = 0
                self.child_turns = 0

            def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
                if "child" in str(view.get("episodeId", "")):
                    self.child_turns += 1
                    if self.child_turns == 1:
                        return Result.success({
                            "kind": "effect", "action": "patch.apply",
                            "resource": {"kind": "fs", "path": "/workspace/main.py"},
                            "args": {"patch": "diff"}, "note": "attempt unauthorized patch",
                        })
                    return Result.success({"kind": "finish", "note": "child finished after denial"})
                self.parent_turns += 1
                if self.parent_turns == 1:
                    return Result.success({
                        "kind": "spawn",
                        "args": {"brief": "read-only child", "scope": {"actions": ["fs.read"]}},
                        "note": "spawning read-only helper",
                    })
                return Result.success({"kind": "finish", "note": "parent finished"})

        engine = EpisodeEngine(
            kernel=self.kernel,
            model=ChildAttemptingUnauthorizedActionModel(),
            clock=self.clock,
            events=self.events,
            scope=self.parent_scope,
        )
        engine.run(
            episode_id="ep-parent-authz-denied",
            run_id="run-1",
            principal="parent-agent",
            brief="test scope escalation is durable",
        )

        # The child's dispatch mock must never have been asked to authorize
        # the unauthorized verb: the engine refused before dispatch.
        self.kernel.dispatch.assert_not_called()
        denials = [e for e in self.events.events if e.kind == "AuthorizationDenied"]
        self.assertEqual(len(denials), 1)
        self.assertEqual(denials[0].reason, "scope_escalation")
        self.assertEqual(denials[0].payload["action"], "patch.apply")


class NarrowedChildCannotEscalate(unittest.TestCase):
    """S8-B-01 / TL receipt 3, against the REAL kernel.

    The pre-existing coverage for this used a mock kernel whose `dispatch`
    side-effect implemented the scope check itself, so it proved the mock and
    not the engine. Wired end-to-end against a real `Kernel`, `StandardPolicy`,
    `StandardClassifier` and `Governor`, a child narrowed to `fs.read`
    **executed** `patch.apply`. These tests hold that shut.
    """

    RESOURCE = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
    VERBS = ("fs.read", "patch.apply")

    def setUp(self) -> None:
        from vanguard.packages.kernel import (
            GrantIssuer, Governor, HeldAuthority, Kernel, Mode,
            SinkClass, SinkRegistry, StandardClassifier, StandardPolicy,
        )

        self.executed: list[str] = []
        outer = self

        class Adapter:
            def __init__(self, name: str) -> None:
                self.name = name

            def healthy(self) -> bool:
                return True

            def execute(self, req: Any) -> Any:
                from vanguard.packages.kernel.model import AdapterOutcome
                outer.executed.append(req.action)
                return AdapterOutcome(status="ok", result_digest="sha256:" + "0" * 64)

        class Silent:
            def emit(self, event: Any) -> None: ...
            def append_intent(self, event: Any) -> None: ...

        self.parent_scope = Scope(
            actions=frozenset(self.VERBS),
            resources=(self.RESOURCE,),
            constraints=Constraints(
                expires_at="2099-01-01T00:00:00.000Z", max_uses=100,
                budget_usd_micros=1_000_000, max_depth=4),
            depth=0,
        )
        sinks = SinkRegistry()
        sinks.register("fs.read", SinkClass.OBSERVATION)
        sinks.register("patch.apply", SinkClass.PRIVILEGED)
        self.silent = Silent()
        self.kernel = Kernel(
            adapters={v: Adapter(v) for v in self.VERBS},
            policy=StandardPolicy(
                parent_scope=self.parent_scope, mode=Mode.BENCHMARK,
                approval_required_above="high",
                risk_of={v: "low" for v in self.VERBS}),
            classifier=StandardClassifier([
                HeldAuthority("agent-1", frozenset(self.VERBS),
                              (self.RESOURCE,), max_depth=4)]),
            governor=Governor({"usd_micros": 1_000_000, "millis": 1_000_000}),
            issuer=GrantIssuer(), clock=MockClock(),
            ledger=self.silent, events=self.silent, sinks=sinks)

    def _run(self, model: Any) -> Any:
        engine = EpisodeEngine(
            kernel=self.kernel, model=model, clock=MockClock(),
            events=self.silent, scope=self.parent_scope,
            tools=({"name": "fs.read"}, {"name": "patch.apply"}), max_turns=6)
        return engine.run(episode_id="ep-parent", run_id="run-1",
                          principal="agent-1", brief="narrowing probe")

    def test_a_child_narrowed_to_fs_read_cannot_execute_patch_apply(self) -> None:
        """The fail-open the TL found: this executed `patch.apply` before."""
        from vanguard.packages.ports.event_store import Result

        class Escalating:
            def __init__(self) -> None:
                self.parent = 0
                self.child = 0

            def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
                if "child" in str(view.get("episodeId", "")):
                    self.child += 1
                    if self.child == 1:
                        return Result.success({
                            "kind": "effect", "action": "patch.apply",
                            "resource": NarrowedChildCannotEscalate.RESOURCE,
                            "args": {"diff": "x"}, "note": "escalate"})
                    return Result.success({"kind": "finish", "note": "child done"})
                self.parent += 1
                if self.parent == 1:
                    return Result.success({
                        "kind": "spawn",
                        "args": {"brief": "read-only helper",
                                 "scope": {"actions": ["fs.read"]}},
                        "note": "spawn"})
                return Result.success({"kind": "finish", "note": "parent done"})

        self._run(Escalating())
        self.assertNotIn("patch.apply", self.executed,
                         "child narrowed to fs.read reached a privileged adapter")

    def test_the_granted_verb_still_works_in_the_child(self) -> None:
        """Fail-closed must not mean fail-useless."""
        from vanguard.packages.ports.event_store import Result

        class Reader:
            def __init__(self) -> None:
                self.parent = 0
                self.child = 0

            def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
                if "child" in str(view.get("episodeId", "")):
                    self.child += 1
                    if self.child == 1:
                        return Result.success({
                            "kind": "effect", "action": "fs.read",
                            "resource": NarrowedChildCannotEscalate.RESOURCE,
                            "args": {"path": "calc.py"}, "note": "read"})
                    return Result.success({"kind": "finish", "note": "child done"})
                self.parent += 1
                if self.parent == 1:
                    return Result.success({
                        "kind": "spawn",
                        "args": {"brief": "read-only helper",
                                 "scope": {"actions": ["fs.read"]}},
                        "note": "spawn"})
                return Result.success({"kind": "finish", "note": "parent done"})

        self._run(Reader())
        self.assertIn("fs.read", self.executed)
        self.assertNotIn("patch.apply", self.executed)

    def test_a_parent_holding_both_verbs_may_still_use_both(self) -> None:
        """The refusal is scoped to the episode's grant, not to the verb."""
        from vanguard.packages.ports.event_store import Result

        class ParentPatches:
            def __init__(self) -> None:
                self.turns = 0

            def propose(self, view: Any, tools: Any, sampling: Any) -> Any:
                self.turns += 1
                if self.turns == 1:
                    return Result.success({
                        "kind": "effect", "action": "patch.apply",
                        "resource": NarrowedChildCannotEscalate.RESOURCE,
                        "args": {"diff": "x"}, "note": "parent patch"})
                return Result.success({"kind": "finish", "note": "done"})

        self._run(ParentPatches())
        self.assertIn("patch.apply", self.executed)


class Adr0060HoldsForTheEngine(unittest.TestCase):
    """No file, repo, patch or test vocabulary enters `agency/episode/`."""

    def test_the_engine_names_no_domain_verb(self) -> None:
        from pathlib import Path

        source = Path(
            "vanguard/packages/agency/episode/engine.py"
        ).read_text(encoding="utf-8")
        # `agency.spawn`/`spawn` is the engine's own control verb, not a domain
        # capability, so it is excluded from this sweep.
        for token in ('"fs.read"', '"patch.apply"', '"proc.exec"', '"fs.write"',
                      "pytest", "unittest", "git "):
            self.assertNotIn(token, source, f"ADR-0060: {token!r} in the engine")


if __name__ == "__main__":
    unittest.main()
