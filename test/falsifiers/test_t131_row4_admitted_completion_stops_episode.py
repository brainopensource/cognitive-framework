"""T-131 row 4 (`RUN-09` defect 4): an episode must STOP at a valid admitted
completion rather than consume its turn ceiling.

`RUN-09` is explicit that "a mechanism that exists is not a mechanism that is
qualified": `EpisodeEngine` already breaks out of the loop after an admissible
`AdmissionVerdict`, and `HarnessSession._admit_completion` already produces one.
That is mechanism. This module is the qualification, and it is built as an
*instrument plus its negative controls*:

* `stop_at_completion_failures` is the instrument. It is a pure predicate over
  an observed run, so the same instrument scores the positive route and the
  injected defect.
* `TheProductRouteStopsAtCompletion` is the product-route POSITIVE falsifier.
  The loop is the canonical `EpisodeEngine` (`RUN-10`: one engine, no second
  agent loop) driving the *real* kernel from `test/kernel/fakes.py`.
* `TheInstrumentRedsOnCeilingConsumption` is the ADVERSARIAL falsifier. It runs
  a real product-route episode that *does* consume its ceiling and proves the
  instrument reds on it, and it feeds the instrument each individual defect
  signature to prove no single clause is decorative.

`RUN-12`: zero provider calls. The provider is the local scripted cassette
double; nothing here reaches a network or a paid model.
"""

from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Sequence

from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.adapters.stores.repo_index import InMemoryRepoIndex
from vanguard.packages.runtime.root import (
    HarnessSession,
    Runtime,
    SessionPorts,
    TaskContext,
)

from test.runtime.test_harness_session import FakeClock, FakeEnvironment

from vanguard.packages.agency import EpisodeEngine, RunTermination
from vanguard.packages.agency.episode.admission_gate import AdmissionVerdict

from test.agency import doubles
from test.kernel import fakes

MAX_TURNS = 8


class RecordingAdmitter:
    """A completion admitter that records every verdict it issued."""

    def __init__(self, verdicts: Sequence[AdmissionVerdict]) -> None:
        self._verdicts = list(verdicts)
        self.calls: list[tuple[int, AdmissionVerdict]] = []

    def __call__(self, episode: Any, proposal: Any) -> AdmissionVerdict:
        index = min(len(self.calls), len(self._verdicts) - 1)
        verdict = self._verdicts[index]
        self.calls.append((episode.turn_count, verdict))
        return verdict

    @property
    def first_admitted_turn(self) -> int | None:
        for turn, verdict in self.calls:
            if verdict.admissible:
                return turn
        return None


def stop_at_completion_failures(
    *,
    outcome: Any,
    admitter: RecordingAdmitter,
    model_calls: int,
    events: Sequence[Any],
    max_turns: int,
) -> list[str]:
    """Score one observed episode against T-131 row 4. Empty list == green.

    Every clause names a way the product could burn turns it was not entitled
    to after it had already been told its completion was admissible.
    """
    failures: list[str] = []
    admitted_turn = admitter.first_admitted_turn
    if admitted_turn is None:
        failures.append("no completion was ever admitted: row 4 is unexercised")
        return failures
    if outcome.terminal is not RunTermination.COMPLETED:
        failures.append(
            f"admitted completion did not terminate COMPLETED: {outcome.terminal}")
    if outcome.episode.turn_count >= max_turns:
        failures.append(
            f"episode consumed its turn ceiling ({outcome.episode.turn_count} "
            f">= {max_turns}) despite an admitted completion")
    if outcome.episode.turn_count != admitted_turn:
        failures.append(
            f"episode ran past the admitted completion turn {admitted_turn} "
            f"to turn {outcome.episode.turn_count}")
    # One provider call per turn, so a call after the admitted turn is a turn
    # the episode paid for after it was entitled to stop.
    if model_calls != admitted_turn + 1:
        failures.append(
            f"provider was called {model_calls} times for an episode admitted at "
            f"turn {admitted_turn}: completion did not stop the loop")
    kinds = [getattr(event, "kind", "") for event in events]
    if kinds.count("ProposalProduced") != admitted_turn + 1:
        failures.append(
            f"{kinds.count('ProposalProduced')} proposals recorded for an episode "
            f"admitted at turn {admitted_turn}")
    if len(admitter.calls) != 1 + sum(
            1 for _, verdict in admitter.calls if not verdict.admissible):
        failures.append("admitter was consulted after it had already admitted")
    return failures


def run_episode(proposals, admitter, *, max_turns: int = MAX_TURNS):
    """One canonical product-route episode over the real kernel."""
    harness = fakes.build()
    model = doubles.ScriptedModel(proposals)
    engine = EpisodeEngine(
        kernel=harness.kernel,
        model=model,
        clock=harness.clock,
        events=harness.sink,
        scope=fakes.child_scope(),
        max_turns=max_turns,
        completion_admitter=admitter,
    )
    outcome = engine.run(
        episode_id="episode-t131-row4",
        run_id="run-t131-row4",
        principal="agent-1",
        brief="write one file",
        spans=(fakes.operator_span(),),
    )
    return outcome, model, harness


ADMIT = AdmissionVerdict(True, "completion_admissible")
REJECT = AdmissionVerdict(False, "VERIFICATION_REQUIRED", "verify before finishing")


class TheProductRouteStopsAtCompletion(unittest.TestCase):
    """POSITIVE falsifier — T-131 row 4 on the product route."""

    def test_an_admitted_completion_ends_the_episode_well_inside_the_ceiling(self) -> None:
        admitter = RecordingAdmitter([ADMIT])
        # Eight finishes are on the tape; the ceiling is eight turns. Only a
        # loop that actually stops leaves seven of them unread.
        outcome, model, harness = run_episode(
            [doubles.effect(), doubles.finish()] + [doubles.finish()] * 6, admitter)

        self.assertEqual(
            stop_at_completion_failures(
                outcome=outcome, admitter=admitter, model_calls=len(model.calls),
                events=harness.sink.events, max_turns=MAX_TURNS),
            [])
        self.assertEqual(outcome.episode.turn_count, 1)
        self.assertEqual(len(model.calls), 2)

    def test_a_rejection_then_an_admission_still_stops_at_the_admission(self) -> None:
        """Retry is permitted; burning the remaining ceiling afterwards is not."""
        admitter = RecordingAdmitter([REJECT, ADMIT])
        outcome, model, harness = run_episode([doubles.finish()] * 8, admitter)

        self.assertEqual(
            stop_at_completion_failures(
                outcome=outcome, admitter=admitter, model_calls=len(model.calls),
                events=harness.sink.events, max_turns=MAX_TURNS),
            [])
        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertLess(outcome.episode.turn_count, MAX_TURNS)


class TheInstrumentRedsOnCeilingConsumption(unittest.TestCase):
    """ADVERSARIAL falsifier — the instrument is sensitive to the real defect.

    A green positive proves nothing unless the same instrument reds when the
    episode really does keep burning turns. The first test is a genuine
    product-route run that consumes its entire ceiling; the rest inject each
    defect signature separately so no clause can be vacuous.
    """

    def test_a_real_ceiling_consuming_episode_reds(self) -> None:
        """The defect's observable signature, produced by the real loop.

        A run whose loop never stops spends every turn it is allowed and then
        dies on the turn bound. That is the trace row 4 forbids once a
        completion has been admitted, and the instrument must red on it.
        """
        admitter = RecordingAdmitter([ADMIT])
        outcome, model, harness = run_episode(
            [doubles.effect(path=f"/workspace/src/a{i}.ts") for i in range(20)],
            admitter)

        # The real loop really did burn the whole ceiling.
        self.assertIs(outcome.terminal, RunTermination.ABANDONED)
        self.assertEqual(outcome.episode.turn_count, MAX_TURNS)
        self.assertEqual(admitter.calls, [], "no finish was proposed, so none was admitted")

        # Now score that same real trace as though a completion HAD been
        # admitted at turn 0. This is precisely the defect: admitted, yet the
        # loop kept paying for turns until the bound stopped it.
        admitter.calls.append((0, ADMIT))
        failures = stop_at_completion_failures(
            outcome=outcome, admitter=admitter, model_calls=len(model.calls),
            events=harness.sink.events, max_turns=MAX_TURNS)
        self.assertTrue(failures)
        self.assertTrue(
            any("consumed its turn ceiling" in item for item in failures), failures)
        self.assertTrue(
            any("ran past the admitted completion" in item for item in failures), failures)
        self.assertTrue(
            any("did not stop the loop" in item for item in failures), failures)

    def test_each_defect_signature_reds_on_its_own(self) -> None:
        admitter = RecordingAdmitter([ADMIT])
        outcome, model, harness = run_episode(
            [doubles.effect(), doubles.finish()] + [doubles.finish()] * 6, admitter)
        base = dict(
            outcome=outcome, admitter=admitter, model_calls=len(model.calls),
            events=harness.sink.events, max_turns=MAX_TURNS)
        self.assertEqual(stop_at_completion_failures(**base), [])

        # (a) one extra provider call after the admitted completion.
        extra_call = dict(base, model_calls=len(model.calls) + 1)
        self.assertTrue(
            any("did not stop the loop" in item
                for item in stop_at_completion_failures(**extra_call)))

        # (b) one extra recorded proposal after the admitted completion.
        class _FakeEvent:
            kind = "ProposalProduced"

        extra_proposal = dict(
            base, events=list(harness.sink.events) + [_FakeEvent()])
        self.assertTrue(
            any("proposals recorded" in item
                for item in stop_at_completion_failures(**extra_proposal)))

        # (c) a ceiling low enough that this very episode counts as exhausted.
        tight = dict(base, max_turns=outcome.episode.turn_count)
        self.assertTrue(
            any("consumed its turn ceiling" in item
                for item in stop_at_completion_failures(**tight)))

    def test_an_unexercised_row_is_reported_not_scored_green(self) -> None:
        """A run that never admitted anything must never read as row-4 green."""
        admitter = RecordingAdmitter([REJECT])
        outcome, model, harness = run_episode([doubles.finish()] * 20, admitter)
        failures = stop_at_completion_failures(
            outcome=outcome, admitter=admitter, model_calls=len(model.calls),
            events=harness.sink.events, max_turns=MAX_TURNS)
        self.assertEqual(failures, ["no completion was ever admitted: row 4 is unexercised"])


class TheFullProductSessionStopsAtCompletion(unittest.TestCase):
    """The same claim one layer up: `HarnessSession.run` on a real preset.

    `HarnessSession` re-enters `EpisodeEngine` across approval boundaries, and
    the ceiling is meant to bound the *episode*, not each segment of it
    (`session.py` S8-A-02). A stop that only holds inside one engine call would
    still let the session buy more turns, so row 4 is asserted here too.

    POSITIVE plus its ADVERSARIAL control, both hermetic: fake environment,
    fake clock, in-memory store and index, scripted cassette provider. Zero
    provider calls and zero USD (`RUN-12`).
    """

    CEILING = 8

    def _session(self, policy, *, model):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        Path(tmp, "a.py").write_text("def f():\n    return 1\n")
        harness = Runtime.compose("vg-code-default", episode_id="ep-t131-row4")
        session = HarnessSession(
            harness,
            SessionPorts(
                model=model, environment=FakeEnvironment(), clock=FakeClock(),
                store=SqliteEventStore(":memory:"), index=InMemoryRepoIndex(),
                interactive=False, completion_policy=policy),
            TaskContext(
                brief="stop when admitted", repo_path=Path(tmp),
                project_id="project-t131", run_id="run-t131-row4",
                episode_id="ep-t131-row4", principal="agent-1",
                max_turns=self.CEILING))
        return session

    def test_an_admitted_completion_ends_the_session_run(self) -> None:
        policy = _RecordingPolicy(ADMIT)
        model = doubles.ScriptedModel([doubles.finish("done")] * 20)
        session = self._session(policy, model=model)
        result = session.run()

        self.assertIs(result.terminal, RunTermination.COMPLETED)
        self.assertEqual(policy.calls, 1, "completion policy consulted more than once")
        self.assertEqual(session.turns_consumed(), 1)
        self.assertLess(session.turns_consumed(), self.CEILING)
        self.assertEqual(len(model.calls), 1,
                         "the provider was asked again after an admitted completion")
        self.assertEqual(len(model.calls), session.turns_consumed())

    def test_the_session_level_check_reds_when_the_ceiling_is_burned(self) -> None:
        """ADVERSARIAL control for the session-level assertion.

        A rejecting policy is the only way to make the real product session
        keep going past a finish claim. The run must not read as COMPLETED,
        and the assertions above must be demonstrably capable of failing: the
        provider IS asked again, and turns DO accumulate.
        """
        policy = _RecordingPolicy(REJECT)
        model = doubles.ScriptedModel([doubles.finish("done")] * 20)
        session = self._session(policy, model=model)
        result = session.run()

        self.assertIsNot(result.terminal, RunTermination.COMPLETED)
        self.assertGreater(policy.calls, 1,
                           "a rejected completion must be re-examined, not accepted")
        self.assertGreater(len(model.calls), 1,
                           "the ceiling-burning control did not actually burn turns")
        # The exact assertions the positive relies on must fail on this trace.
        with self.assertRaises(AssertionError):
            self.assertEqual(len(model.calls), 1)
        with self.assertRaises(AssertionError):
            self.assertEqual(policy.calls, 1)


class _RecordingPolicy:
    """An `ICompletionPolicy` stand-in that counts how often it was consulted."""

    def __init__(self, verdict: AdmissionVerdict) -> None:
        self._verdict = verdict
        self.calls = 0

    def evaluate(self, **kwargs: Any) -> AdmissionVerdict:
        self.calls += 1
        return self._verdict


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
