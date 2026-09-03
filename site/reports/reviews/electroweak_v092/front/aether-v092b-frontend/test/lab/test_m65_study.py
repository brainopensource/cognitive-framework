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
        self.assertEqual(holm_bonferroni({"a": 0.04, "b": 0.03}),
                         {"b": False, "a": False})

    def test_the_step_down_is_more_powerful_than_plain_bonferroni(self) -> None:
        self.assertEqual(holm_bonferroni({"a": 0.04, "b": 0.001}),
                         {"b": True, "a": True})

    def test_a_single_hypothesis_reduces_to_alpha(self) -> None:
        self.assertEqual(holm_bonferroni({"only": 0.049}), {"only": True})
        self.assertEqual(holm_bonferroni({"only": 0.051}), {"only": False})


class TheRegressionBudgetIsEnforced(unittest.TestCase):
    def test_regression_beyond_budget_ceiling_is_flagged(self) -> None:
        from lab.m65_study import RegressionBudget

        floor = _floor(40)
        # Baseline won 30 tasks, treatment won only 10 (20 baseline-only drops = 50% regression)
        base = _runs("off", [True] * 30 + [False] * 10)
        treat = _runs("on", [False] * 30 + [True] * 10, directives=2)
        budget = RegressionBudget(max_baseline_success_drop=0.0)
        report = run_study(base, treat, family=FAMILY, baseline_tuple=BASE_TUPLE,
                           treatment_tuple=TREAT_TUPLE, noise_floor=floor,
                           regression_budget=budget)
        self.assertEqual(report.verdict, "regression")
        self.assertIn("regressed on baseline success", report.rationale)
        self.assertFalse(report.controller_enabled_by_default)


class PerturbationKeyBindsSemanticCheckpoints(unittest.TestCase):
    def test_perturbation_key_binds_semantic_checkpoint_ref_never_turn_index(self) -> None:
        from lab.m65_study import perturbation_key
        from vanguard.packages.domain.ledger.progress import SemanticCheckpointRef

        cp1 = SemanticCheckpointRef(run_id="r1", episode_id="ep1", epoch=0, attempt=0)
        cp2 = SemanticCheckpointRef(run_id="r1", episode_id="ep1", epoch=0, attempt=1)

        key1 = perturbation_key("sha256:task", 42, cp1, attempt_ordinal=0)
        key2 = perturbation_key("sha256:task", 42, cp2, attempt_ordinal=1)
        self.assertNotEqual(key1, key2)

        # Same key is 100% deterministic replay
        key1_again = perturbation_key("sha256:task", 42, cp1, attempt_ordinal=0)
        self.assertEqual(key1, key1_again)

    def test_semantic_checkpoint_ref_rejects_negative_epoch_or_attempt(self) -> None:
        from vanguard.packages.domain.ledger.progress import SemanticCheckpointRef

        with self.assertRaises(ValueError):
            SemanticCheckpointRef(run_id="r", episode_id="ep", epoch=-1, attempt=0)
        with self.assertRaises(ValueError):
            SemanticCheckpointRef(run_id="r", episode_id="ep", epoch=0, attempt=-1)
        with self.assertRaises(ValueError):
            SemanticCheckpointRef(run_id="", episode_id="ep")


class TheStochasticStudyMeetsAllMilestoneRequirements(unittest.TestCase):
    def test_benchmark_task_suite_has_at_least_20_tasks_and_4_block_types(self) -> None:
        from lab.m65_tasks import generate_m65_task_suite
        from vanguard.packages.adapters.models.stochastic import RECOVERABLE_BLOCK_TYPES

        suite = generate_m65_task_suite(24)
        self.assertGreaterEqual(len(suite), 20)
        block_types = {t.block_type for t in suite}
        self.assertEqual(block_types, RECOVERABLE_BLOCK_TYPES)
        self.assertGreaterEqual(len(block_types), 4)

        for task in suite:
            self.assertTrue(task.digest().startswith("sha256:"))

    def test_full_stochastic_study_executes_at_least_60_pairs_with_valid_floor(self) -> None:
        from lab.m65_study import execute_stochastic_m65_study

        report, floor = execute_stochastic_m65_study()
        self.assertGreaterEqual(floor.pairs, 60)
        self.assertFalse(floor.preliminary)
        self.assertGreater(floor.discordance_rate, 0.0)
        self.assertLess(floor.discordance_rate, 1.0)
        self.assertGreater(floor.success_rate, 0.0)
        self.assertLess(floor.success_rate, 1.0)

        # Verification of study report
        self.assertIn(report.verdict, {"improvement", "no_effect", "regression"})
        self.assertIn("turns", report.effect_intervals)
        self.assertIn("repeat_loops", report.effect_intervals)
        self.assertIn("wasted_loops", report.effect_intervals)
        self.assertIn("cost_usd_micros", report.effect_intervals)
        self.assertIn("latency_millis", report.effect_intervals)


class EvidenceEnvelopeIsSignedAndAttributable(unittest.TestCase):
    def test_evidence_envelope_builds_and_signs_properly(self) -> None:
        import tempfile
        from pathlib import Path as _Path

        from lab.m65_study import build_m65_evidence_envelope, execute_stochastic_m65_study
        from vanguard.packages.domain.evidence.envelope import parse_envelope
        from tools.runners.keygen_evidence_key import generate, public_b64, load_key

        report, _ = execute_stochastic_m65_study()
        directory = self.enterContext(tempfile.TemporaryDirectory())
        key_path, _ = generate("m65-unit-test", _Path(directory) / "k.key")
        envelope = build_m65_evidence_envelope(
            report, signing_key=key_path, key_id="m65-unit-test")

        self.assertEqual(envelope.claim, "M-6.5")
        self.assertEqual(envelope.protocol, "aether.m65.attributable-paired-study/1")
        self.assertIn("package:WP-B2", envelope.subjects)
        # The contract is not "a long string": it is a signature the independent
        # verifier can re-derive. A bare hex blob satisfies the length check and
        # still fails the gate, which is how the old signing path went unnoticed.
        import sys as _sys
        _root = _Path(__file__).resolve().parents[2]
        _sys.path.insert(0, str(_root / "tools" / "linters"))
        from verify_evidence import verify_signature_reason

        self.assertTrue(envelope.signature.startswith("ed25519:"))
        self.assertIsNone(
            verify_signature_reason(envelope, public_b64(load_key(key_path))))

        # Roundtrip parse
        wire = envelope.to_wire()
        parsed = parse_envelope(wire)
        self.assertEqual(parsed.digest(), envelope.digest())
        self.assertEqual(parsed.signature, envelope.signature)


if __name__ == "__main__":
    unittest.main()

