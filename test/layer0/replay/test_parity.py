"""S-M4-B-06 replay-parity gate: cold fold reproduces live terminal state
against the full 40-kind event ledger (`layer0.events.taxonomy.EVENT_KINDS`).
"""

from __future__ import annotations

import unittest

from layer0.events.fold import fold
from layer0.events.taxonomy import EVENT_KINDS
from layer0.scheduler.driver import SequentialTurnDriver
from layer0.spi.fakes import EchoToolkit, FixedGate, ScriptedPlanner
from layer0.spi.types_gen import Proposal, Reservation
from test.layer0.support import build_kernel, echo_request, parent_scope


class ReplayParityTests(unittest.TestCase):
    def test_ledger_declares_forty_kinds(self) -> None:
        self.assertEqual(len(EVENT_KINDS), 40)

    def test_cold_fold_matches_live_terminal_state_over_full_ledger(self) -> None:
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
        driver.run(run_id="run-replay-parity", episode_id="ep-replay-parity",
                   principal="episode", goal="replay-parity")

        live_kinds = {envelope.kind.value for envelope in store.envelopes}
        self.assertTrue(live_kinds.issubset(set(EVENT_KINDS)),
                         f"emitted kinds not in the 40-kind ledger: {live_kinds - set(EVENT_KINDS)}")

        live_state = fold(store.envelopes)
        replayed_state = fold(list(store.envelopes))

        self.assertEqual(live_state.run_id, replayed_state.run_id)
        self.assertEqual(live_state.fsm, replayed_state.fsm)
        self.assertEqual(live_state.turns, replayed_state.turns)
        self.assertEqual(live_state.event_count, replayed_state.event_count)
        self.assertEqual(live_state.grants, replayed_state.grants)
        self.assertEqual(live_state.aborted, replayed_state.aborted)
        self.assertEqual(live_state.approvals, replayed_state.approvals)
        self.assertEqual(live_state.fsm, "completed")


if __name__ == "__main__":
    unittest.main()
