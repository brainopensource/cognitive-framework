"""M-6.5 (`B-M65`): the paired-run harness must be able to report *no* effect.

A measurement instrument that can only find improvement is not an instrument.
These tests attack the harness the way a reviewer should attack the eventual
result: identical arms, missing pairs, and an arm that never actually acted.

`milestones.md` binds the consequence: only a demonstrated improvement enables
the controller by default. A negative result is a valid milestone outcome.
"""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.paired_evaluation import (
    RunMetrics,
    measure_run,
    paired_report,
)


class _Event:
    def __init__(self, **payload):
        self.payload = payload


def _run(arm: str, seed: int, *, success=True, directives=0, **kw) -> RunMetrics:
    return RunMetrics(task_id="T1", seed=seed, arm=arm, success=success,
                      directives=directives, **kw)


class MetricsComeFromTheLedger(unittest.TestCase):
    def test_turns_tool_calls_and_cost_are_reduced_from_events(self) -> None:
        events = [
            _Event(kind="ProposalProduced", diagnostics={"usage": {"usd_micros": 40}}),
            _Event(kind="EffectCompleted", descriptorDigest="d1"),
            _Event(kind="ProposalProduced", diagnostics={"usage": {"usd_micros": 60}}),
            _Event(kind="EffectRejected"),
        ]
        metrics = measure_run(events, task_id="T1", seed=1, arm="controller_off",
                              success=True, latency_millis=1200)
        self.assertEqual(metrics.turns, 2)
        self.assertEqual(metrics.tool_calls, 1)
        self.assertEqual(metrics.rejected_calls, 1)
        self.assertEqual(metrics.cost_usd_micros, 100)
        self.assertEqual(metrics.latency_millis, 1200)

    def test_a_rejected_effect_is_not_counted_as_a_tool_call(self) -> None:
        # Otherwise the arm that proposes more illegal work scores as busier.
        events = [_Event(kind="EffectRejected"), _Event(kind="AuthorizationDenied")]
        metrics = measure_run(events, task_id="T1", seed=1, arm="a", success=False)
        self.assertEqual(metrics.tool_calls, 0)
        self.assertEqual(metrics.rejected_calls, 2)

    def test_repeat_loops_count_repeats_not_distinct_descriptors(self) -> None:
        events = [_Event(kind="EffectCompleted", descriptorDigest="same")
                  for _ in range(4)]
        metrics = measure_run(events, task_id="T1", seed=1, arm="a", success=False)
        # Four settlements of one descriptor is three repeats, not one.
        self.assertEqual(metrics.repeat_loops, 3)

    def test_distinct_effects_are_not_loops(self) -> None:
        events = [_Event(kind="EffectCompleted", descriptorDigest=f"d{i}")
                  for i in range(4)]
        self.assertEqual(
            measure_run(events, task_id="T1", seed=1, arm="a", success=True).repeat_loops, 0)

    def test_recoveries_are_counted(self) -> None:
        events = [_Event(kind="RunRecovered"),
                  _Event(kind="EffectReconciled", descriptorDigest="d")]
        self.assertEqual(
            measure_run(events, task_id="T1", seed=1, arm="a", success=True).recoveries, 2)


class IdenticalArmsReportNoEffect(unittest.TestCase):
    """The first thing a reviewer should try to break."""

    def test_two_identical_arms_are_no_effect(self) -> None:
        base = [_run("controller_off", s, turns=5) for s in range(6)]
        treat = [_run("controller_on", s, turns=5) for s in range(6)]
        report = paired_report(base, treat)
        self.assertEqual(report.verdict, "no_effect")
        self.assertFalse(report.controller_enabled_by_default)

    def test_an_arm_that_issued_no_directive_cannot_claim_improvement(self) -> None:
        # Even with a large apparent success gain: if the controller never
        # acted, the arms are the same configuration and the gap is noise.
        base = [_run("controller_off", s, success=False) for s in range(6)]
        treat = [_run("controller_on", s, success=True, directives=0) for s in range(6)]
        report = paired_report(base, treat)
        self.assertEqual(report.verdict, "no_effect")
        self.assertIn("issued no directive", report.rationale)
        self.assertFalse(report.controller_enabled_by_default)

    def test_a_real_improvement_is_reported_when_the_controller_acted(self) -> None:
        base = [_run("controller_off", s, success=False) for s in range(6)]
        treat = [_run("controller_on", s, success=True, directives=2) for s in range(6)]
        report = paired_report(base, treat)
        self.assertEqual(report.verdict, "improvement")
        self.assertTrue(report.controller_enabled_by_default)

    def test_a_regression_is_reported_not_hidden(self) -> None:
        base = [_run("controller_off", s, success=True) for s in range(6)]
        treat = [_run("controller_on", s, success=False, directives=2) for s in range(6)]
        report = paired_report(base, treat)
        self.assertEqual(report.verdict, "regression")
        self.assertFalse(report.controller_enabled_by_default)


class OnlySharedPairsAreCompared(unittest.TestCase):
    def test_unpaired_runs_are_excluded_and_named(self) -> None:
        base = [_run("controller_off", s, directives=0) for s in (1, 2, 3)]
        treat = [_run("controller_on", s, directives=1) for s in (2, 3, 4)]
        report = paired_report(base, treat)
        self.assertEqual(report.paired_tasks, (("T1", 2), ("T1", 3)))
        self.assertIn(("T1", 1), report.unpaired)
        self.assertIn(("T1", 4), report.unpaired)
        self.assertEqual(report.baseline.runs, 2)

    def test_no_shared_pair_is_inconclusive_not_no_effect(self) -> None:
        report = paired_report([_run("controller_off", 1)], [_run("controller_on", 2)])
        self.assertEqual(report.verdict, "inconclusive")
        self.assertFalse(report.controller_enabled_by_default)

    def test_the_report_serialises_for_the_gate(self) -> None:
        import json
        report = paired_report([_run("controller_off", 1)], [_run("controller_on", 1)])
        json.dumps(report.to_dict())
        self.assertIn("controllerEnabledByDefault", report.to_dict())


class TheControllerIsIntegrated(unittest.TestCase):
    """A-M65 supplies the optional path the B-M65 study exercises."""

    def test_runtime_exposes_an_opt_in_controller_binding(self) -> None:
        from vanguard.packages.runtime.session import SessionPorts

        fields = SessionPorts.__dataclass_fields__
        self.assertIn("meta_controller", fields)
        self.assertIsNone(fields["meta_controller"].default)
        self.assertEqual(fields["controller_confidence"].default, ())


if __name__ == "__main__":
    unittest.main()
