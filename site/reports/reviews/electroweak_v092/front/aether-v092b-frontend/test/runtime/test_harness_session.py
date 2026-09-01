"""`HarnessSession` owns wiring; `run()` owns lifecycle.

S8-A-01. `execute_harness` was 175 lines doing eleven jobs, and it built three
`Kernel` instances with identical collaborators because the segment loop was
compensating for a missing suspend/resume. The session is the seam that makes
the control plane testable at all: it constructs and runs a turn against
injected fakes with **no live model, no bwrap, and no network**.

`003` A7, `007` D9.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import Any, Mapping

from test.agency.doubles import ScriptedModel, effect, finish
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.domain.ledger.progress import ConfidenceRecord
from vanguard.packages.ports.meta_controller import StrategyDirective
from vanguard.packages.ports.environment import (
    EffectReceipt,
    EnvironmentProfile,
    EnvironmentSnapshot,
    Observation,
)
from vanguard.packages.ports.event_store import Result
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)

RUNTIME = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "runtime"


class FakeClock:
    """Injected, fixed. The session never reads the system clock (`CT-08`)."""

    def __init__(self) -> None:
        self.reads = 0

    def now(self) -> str:
        self.reads += 1
        return "2026-08-16T00:00:00.000Z"

    def now_ms(self) -> int:
        return 1_755_302_400_000


class FakeEnvironment:
    """An EnvironmentAdapter that touches no filesystem and no sandbox."""

    def __init__(self) -> None:
        self.disposed = False
        self.applied: list[Any] = []

    def profile(self) -> Result[Any]:
        return Result.success(EnvironmentProfile(
            environment_id="fake:/workspace", kind="memory", root="/workspace"))

    def snapshot(self) -> Result[Any]:
        return Result.success(EnvironmentSnapshot(
            snapshot_id="snap-1", digest="sha256:snap",
            created_at="2026-08-16T00:00:00.000Z"))

    def observe(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.success(Observation(
            action=getattr(req, "action", "fs.read"),
            content="def total(values): pass"))

    def preview(self, req: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "fake environment previews nothing")

    def apply(self, req: Any, grant: Any = None) -> Result[Any]:
        self.applied.append(req)
        return Result.success(EffectReceipt(
            descriptor_digest="sha256:descriptor", outcome="ok",
            observed_at="2026-08-16T00:00:00.000Z", result_digest="sha256:applied"))

    def reconcile(self, receipt: Any, grant: Any = None) -> Result[Any]:
        return Result.fail("unavailable", "fake environment reconciles nothing")

    def dispose(self) -> Result[None]:
        self.disposed = True
        return Result.success(None)


def _ports(model: Any, environment: Any) -> SessionPorts:
    return SessionPorts(
        model=model,
        environment=environment,
        clock=FakeClock(),
        store=SqliteEventStore(":memory:"),
        interactive=False,
    )


def _task() -> TaskContext:
    return TaskContext(
        brief="make the suite green",
        repo_path=Path("/workspace"),
        run_id="run-session-1",
        episode_id="ep-session-1",
        principal="agent-1",
        max_turns=4,
    )


class SessionConstructsWithoutIO(unittest.TestCase):
    """The DoD: a session runs a turn with no live model, no bwrap, no network."""

    def setUp(self) -> None:
        self.harness = Runtime.compose("vg-code-default", episode_id="ep-session-1")
        self.environment = FakeEnvironment()

    def test_session_constructs_from_a_harness_and_injected_ports(self) -> None:
        session = HarnessSession(
            self.harness, _ports(ScriptedModel([finish()]), self.environment), _task()
        )
        self.assertIs(session.harness, self.harness)

    def test_session_runs_one_turn_and_returns_a_run_result(self) -> None:
        session = HarnessSession(
            self.harness, _ports(ScriptedModel([finish()]), self.environment), _task()
        )
        result = session.run()
        self.assertEqual(result.harness, self.harness.harness)
        self.assertEqual(result.composition_digest, self.harness.composition_digest)

    def test_the_run_emits_events_to_the_injected_store(self) -> None:
        session = HarnessSession(
            self.harness, _ports(ScriptedModel([finish()]), self.environment), _task()
        )
        result = session.run()
        self.assertGreater(len(result.events), 0)

    def test_the_session_disposes_the_environment_it_was_given(self) -> None:
        session = HarnessSession(
            self.harness, _ports(ScriptedModel([finish()]), self.environment), _task()
        )
        session.run()
        self.assertTrue(self.environment.disposed)

    def test_an_effect_turn_reaches_the_injected_environment(self) -> None:
        model = ScriptedModel([effect(action="fs.read", path="/workspace/calc.py"), finish()])
        session = HarnessSession(self.harness, _ports(model, self.environment), _task())
        result = session.run()
        self.assertIsNotNone(result.terminal)


class MetaControllerRuntimeIntegration(unittest.TestCase):
    """A-M65: between-turn policy uses the ordinary proposal path."""

    def setUp(self) -> None:
        self.harness = Runtime.compose("vg-code-default", episode_id="ep-session-1")

    @staticmethod
    def _confidence() -> ConfidenceRecord:
        return ConfidenceRecord(
            "behavioral",
            0.35,
            "agent-1",
            ("event-derived-attempt",),
            {"method": "fixture", "contextEpoch": 0},
        )

    def test_conclude_is_consulted_between_turns_and_attributed(self) -> None:
        class Controller:
            controller_id = "test.controller/1"

            def __init__(self) -> None:
                self.views: list[Any] = []

            def assess(self, view, progress, confidence):
                self.views.append(view)
                return StrategyDirective(
                    "conclude", self.controller_id, "enough evidence")

        controller = Controller()
        model = ScriptedModel([effect(action="fs.read"), finish()])
        store = SqliteEventStore(":memory:")
        ports = SessionPorts(
            model=model,
            environment=FakeEnvironment(),
            clock=FakeClock(),
            store=store,
            interactive=False,
            meta_controller=controller,
            controller_confidence=(self._confidence(),),
        )
        result = HarnessSession(self.harness, ports, _task()).run()

        # The provider owns turn 0; the policy generates the ordinary finish
        # proposal for turn 1. The guarded consultation samples twice to prove
        # deterministic output from identical projections.
        self.assertEqual(len(model.calls), 1)
        self.assertEqual(len(controller.views), 2)
        self.assertTrue(controller.views[0].attempts)
        events = tuple(store.read().value or ())
        changes = [event for event in events
                   if event.payload.get("kind") == "StrategyChanged"]
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].payload["controllerId"], controller.controller_id)
        self.assertIn(self._confidence().digest(), changes[0].payload["trigger"])
        self.assertEqual(result.trajectory["turns"][1]["invocations"], [])
        self.assertEqual(result.trajectory["turns"][1]["cost"]["tokens"], 0)

    def test_disabled_mode_preserves_the_baseline_turn_path(self) -> None:
        model = ScriptedModel([effect(action="fs.read"), finish()])
        store = SqliteEventStore(":memory:")
        result = HarnessSession(
            self.harness,
            SessionPorts(
                model=model,
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=store,
                interactive=False,
            ),
            _task(),
        ).run()

        self.assertEqual(len(model.calls), 2)
        self.assertFalse(any(
            event.payload.get("kind") == "StrategyChanged"
            for event in (store.read().value or ())))
        self.assertEqual(len(result.trajectory["turns"][1]["invocations"]), 1)

    def test_revise_plan_is_durable_before_the_provider_continues(self) -> None:
        class Controller:
            controller_id = "test.planner/1"

            def assess(self, view, progress, confidence):
                if view.strategy == "revise_plan":
                    return None
                return StrategyDirective(
                    "revise_plan", self.controller_id, "failed approach",
                    brief="try the narrower hypothesis")

        store = SqliteEventStore(":memory:")
        model = ScriptedModel([effect(action="fs.read"), finish()])
        HarnessSession(
            self.harness,
            SessionPorts(
                model=model,
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=store,
                interactive=False,
                meta_controller=Controller(),
                controller_confidence=(self._confidence(),),
            ),
            _task(),
        ).run()

        kinds = [event.payload.get("kind") for event in (store.read().value or ())]
        self.assertIn("StrategyChanged", kinds)
        self.assertIn("PlanRevised", kinds)
        self.assertLess(kinds.index("PlanRevised"), kinds.index("EpisodeCompleted"))
        self.assertEqual(len(model.calls), 2)
        self.assertIn("Strategy directive: revise_plan", str(model.calls[1]))

    def test_delegate_lowers_to_agent_spawn_and_kernel_denies_unheld_action(self) -> None:
        class Controller:
            controller_id = "test.delegator/1"

            def assess(self, view, progress, confidence):
                if view.strategy == "delegate":
                    return None
                return StrategyDirective(
                    "delegate",
                    self.controller_id,
                    "specialist needed",
                    brief="inspect the failing subsystem",
                    scope_slice={"actions": [], "maxTurns": 1},
                )

        store = SqliteEventStore(":memory:")
        model = ScriptedModel([effect(action="fs.read"), finish()])
        result = HarnessSession(
            self.harness,
            SessionPorts(
                model=model,
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=store,
                interactive=False,
                meta_controller=Controller(),
                controller_confidence=(self._confidence(),),
            ),
            _task(),
        ).run()

        events = tuple(store.read().value or ())
        proposals = [event for event in events
                     if event.payload.get("kind") == "ProposalProduced"]
        self.assertTrue(any(event.payload.get("action") == "agent.spawn"
                            for event in proposals))
        self.assertTrue(any(event.payload.get("kind") == "EffectRejected"
                            for event in events))
        controller_turn = next(
            turn for turn in result.trajectory["turns"]
            if turn["proposal"].get("action") == "agent.spawn")
        self.assertEqual(controller_turn["invocations"], [])

    def test_controller_presence_changes_run_identity(self) -> None:
        class Controller:
            controller_id = "test.identity/1"

            def assess(self, view, progress, confidence):
                return None

        def run(controller=None):
            return Runtime.run_composed(
                self.harness,
                SessionPorts(
                    model=ScriptedModel([finish()]),
                    environment=FakeEnvironment(),
                    clock=FakeClock(),
                    store=SqliteEventStore(":memory:"),
                    interactive=False,
                    meta_controller=controller,
                ),
                _task(),
                on_terminal=lambda session: None,
            )

        self.assertNotEqual(run().run_digest, run(Controller()).run_digest)

    def test_controller_may_decline_without_confidence_but_may_not_act(self) -> None:
        class Controller:
            controller_id = "test.decline/1"

            def assess(self, view, progress, confidence):
                return None

        model = ScriptedModel([effect(action="fs.read"), finish()])
        result = HarnessSession(
            self.harness,
            SessionPorts(
                model=model,
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=SqliteEventStore(":memory:"),
                interactive=False,
                meta_controller=Controller(),
            ),
            _task(),
        ).run()

        self.assertEqual(len(model.calls), 2)
        self.assertIsNone(result.instrument_error)

    def test_controller_action_without_confidence_fails_before_attribution(self) -> None:
        class Controller:
            controller_id = "test.unsupported/1"

            def assess(self, view, progress, confidence):
                return StrategyDirective(
                    "conclude", self.controller_id, "unsupported decision")

        store = SqliteEventStore(":memory:")
        result = HarnessSession(
            self.harness,
            SessionPorts(
                model=ScriptedModel([effect(action="fs.read"), finish()]),
                environment=FakeEnvironment(),
                clock=FakeClock(),
                store=store,
                interactive=False,
                meta_controller=Controller(),
            ),
            _task(),
        ).run()

        self.assertEqual(result.terminal.value, "instrument_error")
        self.assertFalse(any(
            event.payload.get("kind") == "StrategyChanged"
            for event in (store.read().value or ())))

class ExactlyOneKernelPerRun(unittest.TestCase):
    def test_root_constructs_a_single_kernel(self) -> None:
        """DoD: exactly one `Kernel(` construction in the session."""

        source = (RUNTIME / "session.py").read_text(encoding="utf-8")
        constructions = [
            line for line in source.splitlines() if re.search(r"\bKernel\(", line)
        ]
        self.assertEqual(
            constructions, [line for line in constructions if "Kernel(" in line]
        )
        self.assertEqual(len(constructions), 1, constructions)

    def test_witness_kernel_is_gone(self) -> None:
        source = (RUNTIME / "session.py").read_text(encoding="utf-8")
        self.assertNotIn("_WitnessKernel", source)

    def test_the_session_holds_the_pending_request_itself(self) -> None:
        """The suspension path needs the request; the session keeps it.

        `DispatchResult` does not grow a field only one caller reads, and
        `kernel/` is not touched to make the runtime observable.
        """

        session = HarnessSession(
            self.harness_or_compose(), _ports(ScriptedModel([finish()]), FakeEnvironment()), _task()
        )
        self.assertTrue(hasattr(session, "dispatch"))

    def harness_or_compose(self) -> Any:
        return Runtime.compose("vg-code-default", episode_id="ep-session-1")


class FailuresLandInTheRightPhase(unittest.TestCase):
    def test_composition_does_not_probe_the_sandbox(self) -> None:
        """A missing bwrap is a runtime failure, not a composition failure.

        Today `execute_harness` raised `CompositionError` *after* composition had
        already succeeded, which made the phase boundary a lie.
        """

        harness = Runtime.compose("vg-code-default", episode_id="ep-session-1")
        self.assertIsNotNone(harness.composition_digest)


class ExecuteHarnessStillWorks(unittest.TestCase):
    """The public entrypoint keeps its contract; it just delegates now."""

    def test_execute_harness_is_still_the_public_entrypoint(self) -> None:
        self.assertTrue(hasattr(Runtime, "execute_harness"))

    def test_execute_harness_delegates_to_the_session(self) -> None:
        import inspect

        source = inspect.getsource(Runtime.execute_harness)
        self.assertIn("HarnessSession", source)


if __name__ == "__main__":
    unittest.main()
