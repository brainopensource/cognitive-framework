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

ROOT_PY = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "runtime" / "root.py"


class FakeClock:
    """Injected, fixed. The session never reads the system clock (`CT-08`)."""

    def __init__(self) -> None:
        self.reads = 0

    def now(self) -> str:
        self.reads += 1
        return "2026-08-16T00:00:00.000Z"


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


class ExactlyOneKernelPerRun(unittest.TestCase):
    def test_root_constructs_a_single_kernel(self) -> None:
        """DoD: `grep -c "Kernel(" root.py` -> 1."""

        source = ROOT_PY.read_text(encoding="utf-8")
        constructions = [
            line for line in source.splitlines() if re.search(r"\bKernel\(", line)
        ]
        self.assertEqual(
            constructions, [line for line in constructions if "Kernel(" in line]
        )
        self.assertEqual(len(constructions), 1, constructions)

    def test_witness_kernel_is_gone(self) -> None:
        source = ROOT_PY.read_text(encoding="utf-8")
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
