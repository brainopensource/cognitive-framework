"""M-6.5 study statistics: every shortcut to a claim must be refused (`B-M65`).

`MEASUREMENT.md` is unusual among specs in that each of its rules records a
defect that actually happened.  These tests hold the study module to them, and
the emphasis is deliberately lopsided: there is one test that a real effect is
reported, and many that a fake one is not.  That asymmetry is the point --
the expensive failure mode in agent measurement is a confident number, not a
missed one.
"""

from __future__ import annotations

import unittest

from lab.m65_study import (
    ComparabilityError,
    DegenerateFloorError,
    aa_noise_floor,
    assert_comparable,
    holm_bonferroni,
    run_study,
)
from vanguard.packages.runtime.paired_evaluation import RunMetrics

FAMILY = {"hypotheses": ["controller raises success rate"],
          "primaryMetric": "successRate", "alpha": 0.05,
          "correction": "holm-bonferroni", "stoppingRule": "fixed-n=40"}
BASE_TUPLE = {"benchmark": "m65-fixed-v1", "modelFingerprint": "fake-1",
              "harnessCommit": "abc", "controller": "off", "runId": "r1"}
TREAT_TUPLE = {**BASE_TUPLE, "controller": "on", "runId": "r2"}


def _runs(arm: str, successes: list[bool], *, directives: int = 0) -> list[RunMetrics]:
    return [RunMetrics(task_id=f"T{i}", seed=1, arm=arm, success=ok,
                       turns=4, directives=directives)
            for i, ok in enumerate(successes)]


def _floor(n: int = 40):
    # A floor that is neither degenerate nor implausibly quiet: the same
    # configuration disagreeing with itself on a few instances.
    left = _runs("aa", [i % 5 != 0 for i in range(n)])
    right = _runs("aa", [i % 7 != 0 for i in range(n)])
    return aa_noise_floor(left, right)


class TheArmsMustBeComparable(unittest.TestCase):
    """`M-18`: the highest-leverage rule, because it turns an analysis error
    into a runtime failure."""

    def test_an_undeclared_differing_dimension_is_refused(self) -> None:
        with self.assertRaises(ComparabilityError) as ctx:
            assert_comparable(BASE_TUPLE, {**TREAT_TUPLE, "modelFingerprint": "other"},
                              ("controller",))
        self.assertIn("modelFingerprint", str(ctx.exception))

    def test_observation_metadata_is_excluded_from_the_equality_check(self) -> None:
        assert_comparable(BASE_TUPLE, {**TREAT_TUPLE, "timestamp": "later",
                                       "nodeId": "n9", "operator": "someone"},
                          ("controller",))

    def test_an_axis_that_did_not_move_is_an_aa_run_not_a_comparison(self) -> None:
        with self.assertRaises(ComparabilityError) as ctx:
            assert_comparable(BASE_TUPLE, dict(BASE_TUPLE), ("controller",))
        self.assertIn("A/A run", str(ctx.exception))

    def test_declaring_no_axis_at_all_is_refused(self) -> None:
        with self.assertRaises(ComparabilityError):
            assert_comparable(BASE_TUPLE, TREAT_TUPLE, ())


class TheNoiseFloorMustBeReal(unittest.TestCase):
    """`M-07`--`M-10`: a floor at the boundary characterises nothing."""

    def test_a_floor_at_zero_percent_is_refused(self) -> None:
        with self.assertRaises(DegenerateFloorError) as ctx:
            aa_noise_floor(_runs("aa", [False] * 30), _runs("aa", [False] * 30))
        self.assertIn("unobserved, not low", str(ctx.exception))

    def test_a_floor_at_one_hundred_percent_is_refused(self) -> None:
        with self.assertRaises(DegenerateFloorError):
            aa_noise_floor(_runs("aa", [True] * 30), _runs("aa", [True] * 30))

    def test_a_small_floor_is_marked_preliminary(self) -> None:
        floor = aa_noise_floor(_runs("aa", [True, False, True]),
                               _runs("aa", [True, True, False]))
        self.assertTrue(floor.preliminary)

    def test_the_floor_records_the_manifest_it_was_computed_on(self) -> None:
        # `M-09`: noise is task-set dependent, so a floor without its manifest
        # cannot license a comparison on any other task set.
        self.assertTrue(_floor().manifest_digest.startswith("sha256:"))

    def test_unshared_aa_arms_are_refused(self) -> None:
        with self.assertRaises(DegenerateFloorError):
            aa_noise_floor([RunMetrics("T1", 1, "aa", True)],
                           [RunMetrics("T2", 1, "aa", True)])


class TheStudyRefusesEveryShortcut(unittest.TestCase):
    def _study(self, base, treat, floor=None):
        return run_study(base, treat, family=FAMILY, baseline_tuple=BASE_TUPLE,
                         treatment_tuple=TREAT_TUPLE, noise_floor=floor)

    def test_without_a_noise_floor_the_result_is_inconclusive(self) -> None:
        report = self._study(_runs("off", [False] * 40),
                             _runs("on", [True] * 40, directives=2))
        self.assertEqual(report.verdict, "inconclusive")
        self.assertIn("noise floor", report.rationale)
        self.assertFalse(report.controller_enabled_by_default)

    def test_a_preliminary_floor_cannot_license_an_admission_run(self) -> None:
        floor = aa_noise_floor(_runs("aa", [True, False, True]),
                               _runs("aa", [True, True, False]))
        report = self._study(_runs("off", [False] * 40),
                             _runs("on", [True] * 40, directives=2), floor)
        self.assertEqual(report.verdict, "inconclusive")
        self.assertFalse(report.controller_enabled_by_default)

    def test_a_controller_that_never_acted_cannot_claim_an_effect(self) -> None:
        report = self._study(_runs("off", [False] * 40),
                             _runs("on", [True] * 40, directives=0), _floor())
        self.assertEqual(report.verdict, "no_effect")

    def test_a_difference_inside_the_floor_is_not_an_effect(self) -> None:
        floor = _floor()
        # One discordant pair against a floor that disagreed with itself far
        # more often than that.
        base = _runs("off", [True] * 40)
        treat = _runs("on", [True] * 39 + [False], directives=1)
        report = self._study(base, treat, floor)
        self.assertEqual(report.verdict, "no_effect")
        self.assertIn("noise", report.rationale)

    def test_too_small_a_sample_refuses_the_p_value_rather_than_reporting_one(self) -> None:
        floor = _floor()
        base = _runs("off", [False] * 10)
        treat = _runs("on", [True] * 10, directives=2)
        report = self._study(base, treat, floor)
        self.assertTrue(report.mcnemar["refusedPValue"])
        self.assertEqual(report.verdict, "inconclusive")

    def test_a_real_improvement_is_reported_with_counts_p_and_an_interval(self) -> None:
        floor = _floor()
        base = _runs("off", [False] * 40)
        treat = _runs("on", [True] * 40, directives=2)
        report = self._study(base, treat, floor)
        self.assertEqual(report.verdict, "improvement")
        self.assertTrue(report.controller_enabled_by_default)
        self.assertEqual(report.discordant_treatment_only, 40)
        self.assertEqual(report.discordant_baseline_only, 0)
        self.assertIsNotNone(report.mcnemar["pValue"])
        self.assertIn("turns", report.effect_intervals)

    def test_a_regression_is_reported_not_hidden(self) -> None:
        floor = _floor()
        base = _runs("off", [True] * 40)
        treat = _runs("on", [False] * 40, directives=2)
        report = self._study(base, treat, floor)
        self.assertEqual(report.verdict, "regression")
        self.assertFalse(report.controller_enabled_by_default)

    def test_the_preregistered_family_travels_with_the_report(self) -> None:
        # `M-06`: post-hoc family selection is undetectable after the fact,
        # which is exactly why the declaration must be in the artifact.
        report = self._study(_runs("off", [False] * 40),
                             _runs("on", [True] * 40, directives=2), _floor())
        self.assertEqual(report.to_dict()["family"]["stoppingRule"], "fixed-n=40")
        self.assertEqual(report.to_dict()["family"]["correction"], "holm-bonferroni")

    def test_the_report_is_digest_stable_and_serialises(self) -> None:
        import json
        args = (_runs("off", [False] * 40), _runs("on", [True] * 40, directives=2),
                _floor())
        first, second = self._study(*args), self._study(*args)
        self.assertEqual(first.report_digest, second.report_digest)
        json.dumps(first.to_dict())

    def test_the_report_declares_itself_analysis_only(self) -> None:
        report = self._study(_runs("off", [True] * 40),
                             _runs("on", [True] * 40, directives=1), _floor())
        self.assertTrue(report.to_dict()["analysisOnly"])


class HolmBonferroniControlsTheFamily(unittest.TestCase):
    """`M-05`: uniformly more powerful than plain Bonferroni, same assumptions."""

    def test_the_smallest_p_is_tested_against_the_strictest_threshold(self) -> None:
        self.assertEqual(holm_bonferroni({"a": 0.01, "b": 0.02, "c": 0.04}),
                         {"a": True, "b": True, "c": True})

    def test_a_failure_stops_the_step_down(self) -> None:
        # Holm is a step-down procedure: the first hypothesis that fails its
        # threshold stops the procedure, and every larger p-value fails with
        # it -- even one that would have cleared plain alpha on its own.
        self.assertEqual(holm_bonferroni({"a": 0.04, "b": 0.03}),
                         {"b": False, "a": False})

    def test_the_step_down_is_more_powerful_than_plain_bonferroni(self) -> None:
        # p=0.04 would fail Bonferroni's 0.05/2 = 0.025 outright; under Holm
        # it is tested against 0.05 once the stricter hypothesis has been
        # rejected. That extra power is the reason for choosing Holm.
        self.assertEqual(holm_bonferroni({"a": 0.04, "b": 0.001}),
                         {"b": True, "a": True})

    def test_a_single_hypothesis_reduces_to_alpha(self) -> None:
        self.assertEqual(holm_bonferroni({"only": 0.049}), {"only": True})
        self.assertEqual(holm_bonferroni({"only": 0.051}), {"only": False})


if __name__ == "__main__":
    unittest.main()
