"""Replay-parity contract: live fixture run → cold fold → structural diff (SPEC §1.3)."""

from __future__ import annotations

import unittest

from layer0.events.fold import fold
from layer0.scheduler.driver import SequentialTurnDriver
from layer0.spi.fakes import EchoToolkit, FixedGate, ScriptedPlanner
from layer0.spi.types_gen import EffectContext, Proposal, Reservation
from test.layer0.support import build_kernel, echo_request, parent_scope


class ReplayParityTests(unittest.TestCase):
    def test_cold_fold_matches_live_terminal_state(self) -> None:
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
        driver.run(run_id="run-parity", episode_id="ep-parity", principal="episode", goal="parity")
        live_kinds = [envelope.kind.value for envelope in store.envelopes]
        folded = fold(store.envelopes)

        self.assertEqual(folded.run_id, "run-parity")
        self.assertEqual(folded.fsm, "completed")
        self.assertGreaterEqual(folded.turns, 1)
        self.assertEqual(folded.event_count, len(store.envelopes))
        self.assertIn("EpisodeStarted", live_kinds)
        self.assertIn("RunCompleted", live_kinds)

        live_grant_ids = set(kernel._issuer.issued())
        self.assertEqual(set(folded.grants), live_grant_ids)

        live_budget = kernel._governor.ledger()
        self.assertIn("tokens", live_budget)
        self.assertEqual(folded.aborted, False)

        approval_kinds = {kind for kind in live_kinds if kind.startswith("Approval")}
        self.assertEqual(len(folded.approvals), len(approval_kinds))

    def test_effect_started_orphan_is_visible_after_fold(self) -> None:
        kernel, store = build_kernel()
        result = kernel.dispatch(
            echo_request(),
            EffectContext(principal="episode", run_id="run-orphan"),
            requested_scope=parent_scope(),
        )
        self.assertTrue(result.ok)
        orphan = [env for env in store.envelopes if env.kind.value == "EffectStarted"]
        terminal = [env for env in store.envelopes if env.kind.value in {
            "EffectCompleted", "EffectFailed", "EffectRejected", "EffectReconciled",
        }]
        prefix = [env for env in store.envelopes if env.seq <= orphan[0].seq]
        state = fold(prefix)
        self.assertEqual(state.open_intents, (orphan[0].payload.get("descriptorDigest"),))
        self.assertTrue(terminal)
