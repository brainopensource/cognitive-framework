"""T-141: unsafe automatic delegation fails before the public run activates."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test.agency.doubles import ScriptedModel, finish
from test.falsifiers.canonical_fixtures import code_pack
from vanguard.packages.runtime.child_runtime import RuntimeChildRunner
from test.falsifiers.test_rf55_rf59_delegation_e2e import (
    FakeEnvironment, _delegation_pack,
)
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.runtime.determinism import FixedClock, SeededRandom
from vanguard.packages.runtime.root import (
    CompositionError, Runtime, SessionPorts, TaskContext,
)


class ProductionActivation(unittest.TestCase):
    def test_unsafe_automatic_spawn_binding_refuses_before_session_activation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            harness = Runtime.compose(_delegation_pack(root / "pack"), episode_id="parent")
            environment = FakeEnvironment()
            ports = SessionPorts(
                model=ScriptedModel([finish()]), environment=environment,
                store=SqliteEventStore(":memory:"),
                clock=FixedClock(at="2026-08-26T12:00:00.000Z", step_ms=1),
                random=SeededRandom(seed=42), interactive=False,
            )
            task = TaskContext(
                brief="delegate safely", repo_path=root, run_id="t141-run",
                episode_id="parent", principal="agent-parent", max_turns=6,
            )
            self.assertIn("agent.spawn", harness.verbs)
            runner = RuntimeChildRunner(
                run_composed=Runtime.run_composed, harness=harness,
                parent_ports=ports, parent_task=task,
            )
            for child_runtime in (None, runner):
                with self.subTest(explicit_runner=child_runtime is not None):
                    with patch("vanguard.packages.runtime.root.HarnessSession") as session:
                        with self.assertRaisesRegex(CompositionError, "child-local effect"):
                            Runtime.run_composed(
                                harness, replace(ports, child_runtime=child_runtime), task)
                        session.assert_not_called()
            self.assertEqual(environment.applied, [])

            # Positive control: the same public path remains usable when the
            # composition cannot spawn. No session or run result is mocked.
            ordinary = Runtime.compose(code_pack(root), episode_id="ordinary")
            ordinary_task = replace(task, run_id="ordinary-run", episode_id="ordinary")
            result = Runtime.run_composed(ordinary, ports, ordinary_task)
            self.assertTrue(result.events)
            self.assertTrue(any(event.kind == "EpisodeStarted" for event in result.events))
