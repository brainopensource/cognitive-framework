from __future__ import annotations

import unittest

from layer0.events.envelope import EnvelopeFactory
from layer0.events.fold import fold
from layer0.spi.types_gen import EventKind


class FoldTests(unittest.TestCase):
    def test_fold_reconstructs_lifecycle_and_grants(self) -> None:
        factory = EnvelopeFactory()
        events = [
            factory.emit(EventKind.RUN_STARTED, run_id="r", principal="p"),
            factory.emit(EventKind.EPISODE_STARTED, run_id="r", principal="p", episode_id="e"),
            factory.emit(EventKind.CAPABILITY_GRANTED, run_id="r", principal="p",
                         payload={"grantId": "grant-1", "actions": ["echo"]}),
            factory.emit(EventKind.BUDGET_RESERVED, run_id="r", principal="p",
                         payload={"reserved": {"tokens": 8}}),
            factory.emit(EventKind.APPROVAL_REQUESTED, run_id="r", principal="p",
                         payload={"tokenId": "t1"}),
            factory.emit(EventKind.APPROVAL_RESOLVED, run_id="r", principal="p",
                         payload={"tokenId": "t1", "approved": True}),
            factory.emit(EventKind.EPISODE_COMPLETED, run_id="r", principal="p",
                         payload={"trajectory_digest": "sha256:" + "a" * 64}),
            factory.emit(EventKind.RUN_COMPLETED, run_id="r", principal="p"),
        ]
        state = fold(events)
        self.assertEqual(state.fsm, "completed")
        self.assertIn("grant-1", state.grants)
        self.assertEqual(state.budget.get("tokens"), 8)
        self.assertEqual(len(state.approvals), 2)
        self.assertEqual(state.event_count, 8)

    def test_branch_resume_keeps_divergent_branch_id(self) -> None:
        factory = EnvelopeFactory()
        prefix = [
            factory.emit(EventKind.RUN_STARTED, run_id="r", principal="p", branch_id="main"),
            factory.emit(EventKind.TURN_STARTED, run_id="r", principal="p", branch_id="main"),
        ]
        forked = factory.emit(EventKind.TURN_STARTED, run_id="r", principal="p", branch_id="alt")
        state = fold(prefix + [forked])
        self.assertEqual(state.branch_id, "alt")
        self.assertEqual(state.turns, 2)
