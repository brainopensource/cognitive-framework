"""`TEST-EXEC-001` / `REQ-EXEC-001` — the depth-1 episode loop.

The kernel under these tests is the real kernel wired by `test/kernel/fakes.py`.
The claim being verified is not "the loop runs" but "the loop reaches an
effect **only** through `Kernel.dispatch`" (`05 §2.1`, `AT-01`), so a stubbed
kernel would make every assertion here vacuous.
"""

from __future__ import annotations

import unittest

from vanguard.packages.agency import EpisodeEngine, RunTermination
from vanguard.packages.agency.episode.admission_gate import AdmissionVerdict
from vanguard.packages.kernel import AdapterOutcome, FailurePath, Occurrence

from test.kernel import fakes
from test.agency import doubles


def build(proposals, *, model=None, **harness_kwargs):
    """A real kernel plus a scripted provider, wired as the composition root."""
    completion_admitter = harness_kwargs.pop("completion_admitter", None)
    harness = fakes.build(**harness_kwargs)
    engine = EpisodeEngine(
        kernel=harness.kernel,
        model=model if model is not None else doubles.ScriptedModel(proposals),
        clock=harness.clock,
        events=harness.sink,
        scope=fakes.child_scope(),
        max_turns=8,
        completion_admitter=completion_admitter,
    )
    return harness, engine


def run(engine, harness, **overrides):
    kwargs = {
        "episode_id": "episode-1",
        "run_id": "run-1",
        "principal": "agent-1",
        "brief": "write one file",
        "spans": (fakes.operator_span(),),
    }
    kwargs.update(overrides)
    return engine.run(**kwargs)


class TheLoop(unittest.TestCase):
    def test_a_cassette_effect_turn_goes_through_kernel_dispatch(self) -> None:
        """`REQ-EXEC-001`. The adapter ran, and it ran with a durable intent
        written first — which only the dispatch sequence does (`K-47`)."""
        harness, engine = build([doubles.effect(), doubles.finish()])
        outcome = run(engine, harness)

        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(len(harness.adapter.calls), 1)
        self.assertIs(outcome.dispatches[0].failure, FailurePath.OK)
        self.assertEqual([entry.kind for entry in harness.ledger.entries],
                         ["EffectStarted"])

    def test_the_loop_appends_proposal_produced_itself(self) -> None:
        """`VG-03 §6.1`: proposal production happens outside the sequence, so
        the loop appends it. Everything else on the wire is the kernel's."""
        harness, engine = build([doubles.effect(), doubles.finish()])
        run(engine, harness)

        kinds = [event.kind for event in harness.sink.events]
        self.assertEqual(kinds.count("ProposalProduced"), 2)
        self.assertLess(kinds.index("ProposalProduced"), kinds.index("EffectStarted"))
        self.assertIn("EffectCompleted", kinds)

    def test_a_proposal_event_discloses_a_descriptor_not_arguments(self) -> None:
        """`REQ-TRUST-001` margin: zero secrets in events. Arguments may
        reference one, so the event carries the digest instead."""
        harness, engine = build([doubles.effect(), doubles.finish()])
        run(engine, harness)

        produced = [e for e in harness.sink.events if e.kind == "ProposalProduced"]
        self.assertIn("proposalDescriptor", produced[0].payload)
        self.assertNotIn("args", produced[0].payload)

    def test_finish_proposal_discloses_note_for_narrative_visibility(self) -> None:
        """`ProposalProduced` carries note for finish so the UI transcript can show the assistant answer."""
        harness, engine = build([doubles.finish(note="Solution complete.")])
        run(engine, harness)

        produced = [e for e in harness.sink.events if e.kind == "ProposalProduced"]
        self.assertEqual(len(produced), 1)
        self.assertEqual(produced[0].payload.get("note"), "Solution complete.")
        self.assertNotIn("args", produced[0].payload)

    def test_each_turn_observes_the_previous_receipt(self) -> None:
        """observe -> propose: the view is materialised from episode state, so
        the second turn can see what the first one did."""
        model = doubles.ScriptedModel([doubles.effect(), doubles.finish()])
        harness, engine = build(None, model=model)
        run(engine, harness)

        self.assertEqual(model.calls[0]["turn"], 0)
        self.assertIsNone(model.calls[0]["lastReceiptDigest"])
        self.assertEqual(model.calls[1]["turn"], 1)
        self.assertEqual(model.calls[1]["lastProgressSignal"], "ok")


class Terminals(unittest.TestCase):
    """`VG-03 §6.2` run-termination names. No evaluation verdict appears."""

    def test_finish_completes(self) -> None:
        harness, engine = build([doubles.finish()])
        self.assertIs(run(engine, harness).terminal, RunTermination.COMPLETED)

    def test_completion_admission_rejection_returns_to_the_model(self) -> None:
        harness, engine = build(
            [doubles.finish(), doubles.finish()],
            completion_admitter=lambda episode, proposal: (
                AdmissionVerdict(False, "VERIFICATION_REQUIRED")
                if episode.turn_count == 0
                else AdmissionVerdict(True, "completion_admissible")
            ),
        )
        outcome = run(engine, harness)

        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(outcome.episode.turn_count, 1)

    def test_abstain_abstains(self) -> None:
        harness, engine = build([doubles.abstain()])
        self.assertIs(run(engine, harness).terminal, RunTermination.ABSTAINED)

    def test_escalate_escalates(self) -> None:
        harness, engine = build([doubles.escalate()])
        self.assertIs(run(engine, harness).terminal, RunTermination.ESCALATED)

    def test_cassette_exhaustion_is_instrument_error_not_a_verdict(self) -> None:
        """`VG-03 §6.2`: a provider failure is never a task verdict, and
        `CT-33` requires it to arrive as a typed value rather than a raise."""
        harness, engine = build([])
        outcome = run(engine, harness)
        self.assertIs(outcome.terminal, RunTermination.INSTRUMENT_ERROR)
        self.assertEqual(len(harness.adapter.calls), 0)

    def test_a_provider_that_raises_is_still_an_instrument_error(self) -> None:
        harness, engine = build(None, model=doubles.RaisingModel())
        self.assertIs(run(engine, harness).terminal, RunTermination.INSTRUMENT_ERROR)

    def test_a_malformed_proposal_is_an_instrument_error(self) -> None:
        """`CT-03`: external data is parsed, never cast. The malformed payload
        never reaches the kernel as an `EffectRequest`."""
        harness, engine = build([{"kind": "effect"}])
        outcome = run(engine, harness)
        self.assertIs(outcome.terminal, RunTermination.INSTRUMENT_ERROR)
        self.assertEqual(len(harness.adapter.calls), 0)

    def test_budget_denial_terminates_as_budget_exhausted(self) -> None:
        harness, engine = build(
            [doubles.effect(usd_micros=50_000), doubles.finish()])
        outcome = run(engine, harness)
        self.assertIs(outcome.terminal, RunTermination.BUDGET_EXHAUSTED)
        self.assertIs(outcome.dispatches[-1].failure, FailurePath.BUDGET_DENIED)

    def test_an_unbounded_run_is_abandoned_rather_than_unbounded(self) -> None:
        """`VG-03 §6.5`: every turn is bounded. A cassette that never finishes
        terminates on the turn bound, and the run state says so."""
        harness, engine = build([doubles.effect(path=f"/workspace/src/a_{i}.ts") for i in range(20)],
                                ceilings={"usd_micros": 10_000_000, "millis": 10_000_000})
        outcome = run(engine, harness)
        self.assertIs(outcome.terminal, RunTermination.ABANDONED)
        self.assertEqual(len(harness.adapter.calls), 8)

    def test_every_terminal_is_a_run_state_never_an_evaluation_outcome(self) -> None:
        """`VG-03 §6.2`: the two axes are separate. Collapsing them is how
        instrument failure silently becomes task failure."""
        evaluation_axis = {"satisfied", "unsatisfied", "partially_satisfied",
                           "inconclusive", "invalid_evaluation"}
        names = {member.value for member in RunTermination}
        self.assertEqual(names & evaluation_axis, set())
        self.assertEqual(names, {
            "completed", "abstained", "escalated", "cancelled",
            "budget_exhausted", "instrument_error", "runtime_error", "abandoned"})


class DenialIsAnEvent(unittest.TestCase):
    def test_a_denied_call_is_reduced_and_the_loop_continues(self) -> None:
        """`VG-03 §6.1`. A denial that ended the run would be
        indistinguishable from a crash, and the trajectory would lose the
        attribution that makes the denial worth recording."""
        harness, engine = build([doubles.effect(action="fs.chmod"),
                                 doubles.effect(),
                                 doubles.finish()])
        outcome = run(engine, harness)

        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertIs(outcome.dispatches[0].failure, FailurePath.UNKNOWN_ACTION)
        self.assertIs(outcome.dispatches[1].failure, FailurePath.OK)
        self.assertEqual(len(harness.adapter.calls), 1)

    def test_an_adapter_error_does_not_terminate_the_run(self) -> None:
        """A real failure is a result to react to (`VG-03 §6.3`, cognitive
        retry), not an instrument error and not a crash."""
        failing = fakes.FakeAdapter("fs.write", outcome=AdapterOutcome(
            "error", Occurrence.DID_NOT_OCCUR, {"usd_micros": 10}, detail="disk full"))
        harness, engine = build([doubles.effect(), doubles.finish()],
                                adapter=failing)
        outcome = run(engine, harness)
        self.assertIs(outcome.dispatches[0].failure, FailurePath.ADAPTER_ERROR)
        self.assertIs(outcome.terminal, RunTermination.COMPLETED)


class NoSelfEvaluation(unittest.TestCase):
    def test_the_engine_reaches_no_evaluator(self) -> None:
        """`ICD §3`: evaluation is exterior. An episode terminates; it does
        not grade itself. The assertion below is reachability, not a call
        count — a defence proved only by an uncalled double is a comment
        (`VG-03 §6.5`), so `test_agency_lint.py` proves unreachability from
        the source itself."""
        import sys

        import vanguard.packages.agency as agency_pkg

        evaluator = doubles.RecordingEvaluator()
        harness, engine = build([doubles.effect(), doubles.finish()])
        outcome = run(engine, harness)

        self.assertIs(outcome.terminal, RunTermination.COMPLETED)
        self.assertEqual(evaluator.calls, [])
        loaded = [name for name in sys.modules if name.startswith(agency_pkg.__name__)]
        self.assertFalse(any("evaluator" in name.lower() for name in loaded), loaded)


if __name__ == "__main__":
    unittest.main()
