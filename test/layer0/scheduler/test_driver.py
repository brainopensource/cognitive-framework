from __future__ import annotations

import unittest

from layer0.scheduler.driver import SequentialTurnDriver
from layer0.spi.fakes import EchoToolkit, FixedGate, ScriptedPlanner
from layer0.spi.types_gen import EventKind, Proposal, Reservation
from test.layer0.support import build_kernel, echo_request, parent_scope


class SchedulerTests(unittest.TestCase):
    def test_sequential_episode_emits_trajectory(self) -> None:
        kernel, store = build_kernel()
        planner = ScriptedPlanner((Proposal(requests=(echo_request(),)),))
        driver = SequentialTurnDriver(
            kernel=kernel,
            planner=planner,
            toolkit=EchoToolkit(),
            gate=FixedGate(),
            emitter=store.emitter,
            scope=parent_scope(),
            budget=Reservation(0, 0, 16, 0, 3, 2),
        )
        traj = driver.run(run_id="run-1", episode_id="ep-1", principal="episode", goal="echo once")
        kinds = [envelope.kind.value for envelope in store.envelopes]
        self.assertIn("RunStarted", kinds)
        self.assertIn("EpisodeStarted", kinds)
        self.assertIn("TurnStarted", kinds)
        self.assertIn("ProposalProduced", kinds)
        self.assertIn("Heartbeat", kinds)
        self.assertIn("EpisodeCompleted", kinds)
        self.assertIn("RunCompleted", kinds)
        self.assertEqual(traj.schema, "mhf.trajectory/1")
        self.assertTrue(traj.digest.startswith("sha256:"))
        _ = EventKind

    def test_spawn_round_trips_child_spans(self) -> None:
        kernel, store = build_kernel()
        driver = SequentialTurnDriver(
            kernel=kernel,
            planner=ScriptedPlanner(()),
            toolkit=EchoToolkit(),
            gate=FixedGate(),
            emitter=store.emitter,
            scope=parent_scope(),
            budget=Reservation(0, 0, 0, 0, 1, 2),
        )
        driver.spawn(run_id="run-1", principal="episode", child_id="child-1",
                     parent_depth=0, budget=Reservation(0, 0, 0, 0, 1, 2))
        kinds = [envelope.kind.value for envelope in store.envelopes]
        self.assertEqual(kinds, ["ChildSpawned", "ChildReturned"])
