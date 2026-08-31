"""`CMX-03` — the no-progress detector and the repeated-action escalation ladder.

The detector these tests cover was unreachable before this suite existed:
`Turn.signature` carried `state_digest`, which hashes the *growing* turn
history, so two consecutive turns could never share a signature and
`Episode.repeats()` was unsatisfiable. Live traces showed 8-12 identical
`fs.read({"path": "."})` calls burning the whole turn budget with the
detector never firing.

The kernel under these tests is the real kernel from `test/kernel/fakes.py`,
for the same reason `test_episode.py` uses it: a stubbed kernel would make the
dispatch-count assertions vacuous.
"""

from __future__ import annotations

import unittest

from vanguard.packages.agency import RunTermination
from vanguard.packages.agency.episode.state import Episode, Turn

from test.agency import doubles
from test.agency.test_episode import build, run


def _turn(index: int, *, state_digest: str = "sha256:" + "a" * 64,
          descriptor: str = "descriptor-1",
          receipt: str | None = "sha256:" + "1" * 64,
          signal: str = "ok") -> Turn:
    return Turn(
        index=index,
        state_digest=state_digest,
        proposal_descriptor=descriptor,
        receipt_digest=receipt,
        progress_signal=signal,
    )


class TheSignature(unittest.TestCase):
    """`Turn.signature` must answer "did anything change?", not "how long is
    the history?"."""

    def test_the_signature_is_blind_to_history_growth(self) -> None:
        """Two turns proposing the identical action against an identical
        receipt are the same transition, whatever the history length."""
        early = _turn(1, state_digest="sha256:" + "a" * 64)
        late = _turn(7, state_digest="sha256:" + "b" * 64)

        self.assertEqual(early.signature, late.signature)

    def test_a_changed_receipt_is_not_a_repeat(self) -> None:
        """The carve-out the detector's own docstring promises: re-running a
        test whose output changed is progress, not a livelock."""
        first = _turn(1, receipt="sha256:" + "1" * 64)
        second = _turn(2, receipt="sha256:" + "2" * 64)

        self.assertNotEqual(first.signature, second.signature)

    def test_a_changed_progress_signal_is_not_a_repeat(self) -> None:
        first = _turn(1, signal="ok")
        second = _turn(2, signal="budget_denied")

        self.assertNotEqual(first.signature, second.signature)

    def test_repeats_fires_on_identical_consecutive_turns(self) -> None:
        """The predicate itself, isolated from the engine."""
        episode = Episode(episode_id="e", run_id="r", principal="p")
        episode = episode.with_turn(_turn(0)).with_turn(_turn(1))

        self.assertTrue(episode.repeats(_turn(2), limit=3))

    def test_repeats_does_not_fire_when_the_receipt_moved(self) -> None:
        episode = Episode(episode_id="e", run_id="r", principal="p")
        episode = episode.with_turn(_turn(0)).with_turn(
            _turn(1, receipt="sha256:" + "2" * 64))

        self.assertFalse(episode.repeats(_turn(2), limit=3))


class TheEscalationLadder(unittest.TestCase):
    """A livelock must be interrupted with corrective feedback first, and only
    abandoned if the model will not take a different action."""

    def test_a_repeated_action_stops_being_dispatched(self) -> None:
        """The Nth identical proposal is blocked *before* the kernel, so the
        livelock stops costing effects as well as turns."""
        model = doubles.ScriptedModel([doubles.effect()] * 8)
        harness, engine = build([], model=model)

        run(engine, harness)

        # Two dispatches, then the ladder takes over. Without the ladder this
        # is 8 — one per scripted proposal.
        self.assertEqual(len(harness.adapter.calls), 2)

    def test_the_model_is_told_which_action_it_repeated(self) -> None:
        model = doubles.ScriptedModel([doubles.effect()] * 8)
        harness, engine = build([], model=model)

        run(engine, harness)

        feedback = [call["recoveryFeedback"] for call in model.calls
                    if "recoveryFeedback" in call]
        self.assertTrue(feedback, "the ladder must reach the model as feedback")
        self.assertEqual(feedback[0]["reason"], "REPEATED_ACTION")
        self.assertEqual(feedback[0]["repeatedAction"], "fs.write")

    def test_an_endless_repeat_terminates_well_before_the_turn_bound(self) -> None:
        """The failure this whole suite exists for: the run used to reach
        `max_turns` and report a turn-bound abandonment instead."""
        model = doubles.ScriptedModel([doubles.effect()] * 30)
        harness, engine = build([], model=model)  # build() pins max_turns=8

        outcome = run(engine, harness)

        self.assertIs(outcome.terminal, RunTermination.ABANDONED)
        self.assertIn("repeated action", outcome.episode.detail)
        self.assertLess(outcome.episode.turn_count, 8)

    def test_a_corrected_action_after_the_nudge_still_completes(self) -> None:
        """Escalation must be a nudge, not a fast fail: a model that takes the
        hint and moves on still reaches a normal terminal."""
        model = doubles.ScriptedModel([
            doubles.effect(),
            doubles.effect(),
            doubles.effect(),            # blocked; nudge issued here
            doubles.effect(path="/workspace/src/b.ts"),
            doubles.finish(),
        ])
        harness, engine = build([], model=model)

        outcome = run(engine, harness)

        self.assertIs(outcome.terminal, RunTermination.COMPLETED)

    def test_distinct_actions_are_never_throttled(self) -> None:
        """The ladder must not interfere with an episode making progress."""
        model = doubles.ScriptedModel([
            doubles.effect(path="/workspace/src/a.ts"),
            doubles.effect(path="/workspace/src/b.ts"),
            doubles.effect(path="/workspace/src/c.ts"),
            doubles.effect(path="/workspace/src/d.ts"),
            doubles.finish(),
        ])
        harness, engine = build([], model=model)

        outcome = run(engine, harness)

        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(len(harness.adapter.calls), 4)

    def test_a_retry_after_a_failed_dispatch_is_not_a_livelock(self) -> None:
        """Re-proposing an action whose last dispatch was *denied* is
        legitimate: the receipt in hand is a failure, so the next attempt may
        genuinely differ. Only an action that keeps succeeding identically is
        stuck, so the ladder must stay out of the way and let the kernel's own
        terminal win.
        """
        model = doubles.ScriptedModel([doubles.effect(usd_micros=50_000)] * 6)
        harness, engine = build([], model=model)

        outcome = run(engine, harness)

        self.assertIs(outcome.terminal, RunTermination.BUDGET_EXHAUSTED)


if __name__ == "__main__":
    unittest.main()
