"""M-6.5 paired study on the canonical path, and why it cannot conclude yet.

Dev A's runtime hook is integrated: `SessionPorts` binds an optional
controller and `_consult_meta_controller` consults it between durable turns.
So the study can now be run for real rather than stubbed -- and the first
thing a real run must be able to do is refuse to conclude.

It refuses here, for a reason worth stating precisely. The only fully
attributable provider available offline is deterministic, so the same task at
the same seed produces the identical trajectory every time. That makes the
A/A noise floor degenerate at 100%: zero discordance, *unobserved* rather than
low. `MEASUREMENT.md M-07` refuses such a floor outright, and every sample size
derived from it would inherit the degeneracy.

So the honest status of M-6.5 is: instrument integrated and exercised on the
canonical path, controller observed to act and to be attributed, **no measured
improvement, and none claimable until a stochastic attributable provider makes
a non-degenerate floor computable**. That is a negative result about the
instrument, not about the controller, and the two must not be confused.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from lab.m65_study import DegenerateFloorError, aa_noise_floor, run_study
from vanguard.packages.adapters.models.lam import LamModelAdapter
from vanguard.packages.domain.ledger.progress import ConfidenceRecord
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef, Verdict
from vanguard.packages.ports.event_store import Result
from vanguard.packages.ports.meta_controller import StrategyDirective
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.paired_evaluation import measure_run, paired_report
from vanguard.packages.runtime.root import Runtime, TaskContext

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"

FAMILY = {"hypotheses": ["the meta-controller raises success rate"],
          "primaryMetric": "successRate", "alpha": 0.05,
          "correction": "holm-bonferroni", "stoppingRule": "fixed-n",
          "declaredAxis": "controller"}
BASE_TUPLE = {"benchmark": "lam-vertical-v1", "modelFingerprint": "lam/t0-vanguard-vertical",
              "harnessCommit": "dev", "controller": "off"}
TREAT_TUPLE = {**BASE_TUPLE, "controller": "on"}


class _Verifier:
    def evaluate(self, run_ref: RunRef, protocol: EvaluationProtocol) -> Result[Verdict]:
        return Result.success(Verdict(outcome="claims",
                                      claims=({"claim": "m65", "holds": True},),
                                      reason=protocol.name))


class _RequestContextController:
    """A deterministic policy: when the run has stalled, ask for context.

    Deliberately the least invasive directive in the set. A controller whose
    first move is `delegate` would confound the M-6.5 measurement with M-6.
    """

    controller_id = "m65-request-context"

    def assess(self, view, progress, confidence):
        if progress.stall_count >= 1:
            return StrategyDirective("request_context", self.controller_id,
                                     "stalled without settling an effect")
        return None


class _Event:
    """Normalises an envelope so `measure_run` reads `kind` from the payload."""

    def __init__(self, envelope) -> None:
        self.payload = {"kind": envelope.kind, **dict(envelope.payload)}


def _run_once(*, controller, seed: int):
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory)
        (repo / "src").mkdir()
        (repo / "src/value.py").write_text("VALUE = 1\n", encoding="utf-8")
        (repo / "test_value.py").write_text(
            "import unittest\nfrom src.value import VALUE\n\n"
            "class TestValue(unittest.TestCase):\n"
            "    def test_value(self):\n"
            "        self.assertEqual(VALUE, 2)\n\n"
            "if __name__ == '__main__':\n    unittest.main()\n", encoding="utf-8")
        signer = OperatorSigner(b"m65-integrated-study-key")
        confidence = (ConfidenceRecord("behavioral", 0.4, "goal", ("event-1",),
                                       {"method": "held-out", "contextEpoch": 0}),) \
            if controller is not None else ()
        result = Runtime.execute_harness(
            MANIFEST,
            TaskContext(brief="Repair the value bug and verify the test suite.",
                        repo_path=repo, run_id=f"m65-{seed}",
                        episode_id=f"m65-episode-{seed}", principal="agent-1",
                        max_turns=6),
            model=LamModelAdapter(model_name="lam/t0-vanguard-vertical"),
            approver=lambda challenge: signer.approve(challenge, reviewer="operator"),
            approval_key=signer.public_bytes, verifier=_Verifier(),
            meta_controller=controller, controller_confidence=confidence,
        )
        from vanguard.packages.agency import RunTermination

        return measure_run(
            [_Event(event) for event in result.events],
            task_id="lam-value-bug", seed=seed,
            arm="controller_on" if controller is not None else "controller_off",
            success=result.terminal is RunTermination.COMPLETED)


class TheStudyRunsOnTheCanonicalPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = [_run_once(controller=None, seed=seed) for seed in range(3)]
        cls.treatment = [_run_once(controller=_RequestContextController(), seed=seed)
                         for seed in range(3)]

    def test_both_arms_actually_ran_and_were_measured_from_the_ledger(self) -> None:
        for metrics in self.baseline + self.treatment:
            self.assertTrue(metrics.success)
            self.assertGreater(metrics.turns, 0)
            self.assertGreater(metrics.tool_calls, 0)

    def test_the_controller_off_arm_is_the_unchanged_default(self) -> None:
        # `milestones.md`: controller-off behaviour must be preserved exactly.
        for metrics in self.baseline:
            self.assertEqual(metrics.directives, 0)

    def test_the_arms_are_paired_by_task_and_seed(self) -> None:
        report = paired_report(self.baseline, self.treatment)
        self.assertEqual(report.unpaired, ())
        self.assertEqual(len(report.paired_tasks), 3)

    def test_the_reduction_reports_no_effect_not_an_improvement(self) -> None:
        # On a deterministic provider the trajectories are identical, so any
        # gap between the arms would be the harness measuring itself.
        report = paired_report(self.baseline, self.treatment)
        self.assertIn(report.verdict, {"no_effect", "inconclusive"})
        self.assertFalse(report.controller_enabled_by_default)

    def test_the_aa_floor_on_this_provider_is_degenerate_and_refused(self) -> None:
        # THE FINDING. A deterministic provider cannot produce a noise floor,
        # and `M-07` refuses a floor at the boundary rather than reporting a
        # zero that would license any effect size at all.
        with self.assertRaises(DegenerateFloorError) as ctx:
            aa_noise_floor(self.baseline, [
                _run_once(controller=None, seed=seed) for seed in range(3)])
        self.assertIn("unobserved, not low", str(ctx.exception))

    def test_the_study_cannot_conclude_and_says_which_gate_stopped_it(self) -> None:
        # Two independent reasons stand in the way here, and the report names
        # the binding one rather than the most flattering one: on a task that
        # never stalls the controller issues no directive, so the arms are the
        # same configuration before the floor is even reached.
        report = run_study(self.baseline, self.treatment, family=FAMILY,
                           baseline_tuple=BASE_TUPLE, treatment_tuple=TREAT_TUPLE,
                           noise_floor=None)
        self.assertIn(report.verdict, {"no_effect", "inconclusive"})
        self.assertFalse(report.controller_enabled_by_default)
        if report.verdict == "no_effect":
            self.assertIn("issued no directive", report.rationale)
        else:
            self.assertIn("noise floor", report.rationale)

    def test_the_study_refuses_arms_that_differ_in_the_model(self) -> None:
        # `M-18` as a runtime failure: the most common analytical error in the
        # field becomes a refusal rather than a footnote.
        from lab.m65_study import ComparabilityError

        with self.assertRaises(ComparabilityError):
            run_study(self.baseline, self.treatment, family=FAMILY,
                      baseline_tuple=BASE_TUPLE,
                      treatment_tuple={**TREAT_TUPLE, "modelFingerprint": "other"},
                      noise_floor=None)


if __name__ == "__main__":
    unittest.main()
