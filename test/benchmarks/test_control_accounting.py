"""T-52 / RUN-03: truthful control accounting over 30 fixed scheduled slots.

Every case here is a falsifier for one clause of RUN-03: the binary denominator
stays separate from missingness, no slot is ever replaced, and no usage figure
is invented, imputed or inferred from an inconsistent population.
"""

from __future__ import annotations

import random
import unittest

from benchmarks.ladder.evidence import EvidenceError
from benchmarks.ladder.metrics import (
    BUDGET_EXHAUSTED,
    budget_exhausted,
    publish_control_report,
    score_metrics,
    usage_totals,
)
from benchmarks.statistics import UsageTotals, usage_rate, wilson_interval
from test.benchmarks.test_metric_veto import _bound_row, _population
from test.benchmarks.test_preregistration import TASK_IDS, frozen_manifest

FAILED = {"disposition": "failed"}
#: An observed resource-ceiling stop. It occupies its scheduled slot.
EXHAUSTED = {"terminal_status": BUDGET_EXHAUSTED, "disposition": "not_run"}
TIMED_OUT = {
    "terminal_status": "abandoned",
    "disposition": "undeterminable",
    "undeterminable_reason": "provider timeout",
}


def _graded(manifest: dict, passes: int) -> list[dict]:
    """A complete 30-slot population with exactly ``passes`` binary successes."""
    return [
        _bound_row(manifest, task, settlement={} if index < passes else dict(FAILED))
        for index, task in enumerate(manifest["suite"]["tasks"])
    ]


class TestWilsonBoundary(unittest.TestCase):
    """RUN-03 accepts on a two-sided 95% Wilson lower bound >= 0.40."""

    CASES = (
        (17, "NEGATIVE", False),
        (18, "POSITIVE", True),
    )

    def test_the_seventeen_versus_eighteen_boundary_decides_the_canary(self) -> None:
        for passes, expected, admits in self.CASES:
            with self.subTest(passes=passes):
                lower, _ = wilson_interval(passes, 30)
                self.assertEqual(lower >= 0.40, admits, f"wilson lb {lower}")
                report = publish_control_report(
                    record=frozen_manifest(), rows=_graded(frozen_manifest(), passes))
                self.assertEqual(report["disposition"], expected)
                self.assertEqual(report["n_evaluable"], 30)
                self.assertEqual(report["n_passed"], passes)

    def test_the_preserved_interval_is_two_sided(self) -> None:
        low, high = wilson_interval(18, 30)
        self.assertAlmostEqual(low, 0.4232005249827384, places=12)
        self.assertAlmostEqual(high, 0.7540960567391659, places=12)
        self.assertLess(low, 18 / 30)
        self.assertGreater(high, 18 / 30)


class TestFixedSlotAccounting(unittest.TestCase):
    """30 slots are scheduled once; nothing is replaced or topped up."""

    def test_a_missing_outcome_never_shrinks_the_denominator(self) -> None:
        manifest = frozen_manifest()
        rows = _graded(manifest, 18)
        rows[29] = _bound_row(manifest, TASK_IDS[29], settlement=dict(TIMED_OUT))
        report = publish_control_report(record=manifest, rows=rows)
        self.assertEqual(report["n_scheduled"], 30)
        self.assertEqual(report["n_evaluable"], 29)
        self.assertEqual(report["n_missing"], 1)
        # 29 binary outcomes is insufficient evidence, not a negative result.
        self.assertEqual(report["disposition"], "UNDETERMINABLE")

    def test_a_replacement_attempt_for_a_missing_slot_is_refused(self) -> None:
        manifest = frozen_manifest()
        rows = _graded(manifest, 18)
        rows[29] = _bound_row(manifest, TASK_IDS[29], settlement=dict(TIMED_OUT))
        rows.append(_bound_row(manifest, TASK_IDS[29]))
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=rows)

    def test_a_duplicate_attempt_identity_is_refused(self) -> None:
        manifest = frozen_manifest()
        rows = _graded(manifest, 18)
        rows[7] = _bound_row(manifest, TASK_IDS[6])
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=rows)

    def test_a_population_mismatch_is_refused(self) -> None:
        manifest = frozen_manifest()
        for label, rows in (
            ("short", _graded(manifest, 18)[:29]),
            ("wrong n", _graded(manifest, 18)),
        ):
            with self.subTest(label):
                if label == "wrong n":
                    rows[0]["identity"]["n"] = 29
                with self.assertRaises(EvidenceError):
                    publish_control_report(record=manifest, rows=rows)

    def test_historical_and_live_evidence_cannot_be_mixed(self) -> None:
        manifest = frozen_manifest()
        rows = _graded(manifest, 18)
        rows[3] = _bound_row(
            manifest, TASK_IDS[3], execution={"evidence_label": "LIVE-HISTORICAL"})
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=rows)


class TestBudgetExhaustion(unittest.TestCase):
    """A ceiling stop is an observed terminal outcome, not an absent task."""

    def test_exhaustion_is_recognised_from_either_settlement_field(self) -> None:
        self.assertTrue(budget_exhausted({"settlement": dict(EXHAUSTED)}))
        self.assertTrue(budget_exhausted({"settlement": {
            "terminal_status": "abandoned", "disposition": "undeterminable",
            "undeterminable_reason": BUDGET_EXHAUSTED}}))
        self.assertFalse(budget_exhausted({"settlement": dict(TIMED_OUT)}))
        self.assertFalse(budget_exhausted({}))

    def test_an_exhausted_slot_is_counted_and_keeps_its_place(self) -> None:
        manifest = frozen_manifest()
        rows = _graded(manifest, 18)
        rows[29] = _bound_row(manifest, TASK_IDS[29], settlement=dict(EXHAUSTED))
        report = publish_control_report(record=manifest, rows=rows)
        self.assertEqual(report["n_scheduled"], 30)
        self.assertEqual(report["n_evaluable"], 29)
        self.assertEqual(report["n_missing"], 1)
        self.assertEqual(report["metrics"]["n_budget_exhausted"], 1)
        self.assertEqual(report["disposition"], "UNDETERMINABLE")

    def test_exhaustion_does_not_license_a_further_dispatch(self) -> None:
        manifest = frozen_manifest()
        rows = _graded(manifest, 18)
        rows[29] = _bound_row(manifest, TASK_IDS[29], settlement=dict(EXHAUSTED))
        rows.append(_bound_row(manifest, TASK_IDS[29]))
        with self.assertRaises(EvidenceError):
            publish_control_report(record=manifest, rows=rows)

    def test_a_complete_population_reports_zero_exhaustion(self) -> None:
        self.assertEqual(
            score_metrics(_population(frozen_manifest()))["n_budget_exhausted"], 0)


class TestUsageProvenance(unittest.TestCase):
    """Unknown usage stays unknown; an observed zero stays a measurement."""

    def test_totals_separate_observed_zero_from_unknown(self) -> None:
        rows = [
            {"economics": {"cost_usd_micros": 0}},
            {"economics": {"cost_usd_micros": 5}},
            {"economics": {"cost_usd_micros": None}},
            {"economics": {}},
            {"economics": {"cost_usd_micros": True}},
        ]
        totals = usage_totals(rows, "economics", "cost_usd_micros")
        self.assertEqual((totals.known, totals.unknown, totals.total), (2, 3, 5))
        self.assertIsNone(totals.settled_total)
        self.assertEqual(usage_totals(rows[:2], "economics", "cost_usd_micros").settled_total, 5)

    def test_a_zero_cost_execution_is_settled_not_unknown(self) -> None:
        manifest = frozen_manifest()
        rows = [
            _bound_row(manifest, task, economics={"cost_usd_micros": 0})
            for task in manifest["suite"]["tasks"]
        ]
        metrics = score_metrics(rows)
        self.assertEqual(metrics["total_cost_usd_micros"], 0)
        self.assertEqual(metrics["n_cost_unknown"], 0)

    def test_one_unknown_cost_unsettles_the_total(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        rows[11] = _bound_row(manifest, TASK_IDS[11], economics={"cost_usd_micros": None})
        metrics = score_metrics(rows)
        self.assertIsNone(metrics["total_cost_usd_micros"])
        self.assertEqual(metrics["n_cost_unknown"], 1)

    def test_one_unknown_token_count_withholds_kappa(self) -> None:
        manifest = frozen_manifest()
        rows = _population(manifest)
        self.assertIsNotNone(score_metrics(rows)["token_efficiency_kappa"])
        for field in ("prompt_tokens", "completion_tokens"):
            with self.subTest(field):
                partial = _population(manifest)
                partial[4] = _bound_row(manifest, TASK_IDS[4], economics={field: None})
                metrics = score_metrics(partial)
                self.assertIsNone(metrics["token_efficiency_kappa"])
                self.assertIsNone(metrics["total_tokens"])
                self.assertEqual(metrics["n_usage_unknown"], 1)

    def test_no_rate_is_inferred_from_an_inconsistent_population(self) -> None:
        settled = UsageTotals(known=3, unknown=0, total=90)
        self.assertEqual(usage_rate(settled, UsageTotals(3, 0, 9)), 10.0)
        for label, numerator, denominator in (
            ("unknown numerator", UsageTotals(2, 1, 60), UsageTotals(3, 0, 9)),
            ("unknown denominator", settled, UsageTotals(2, 1, 6)),
            ("different populations", settled, UsageTotals(4, 0, 12)),
            ("empty denominator", settled, UsageTotals(3, 0, 0)),
            ("empty numerator", UsageTotals(0, 0, 0), UsageTotals(0, 0, 0)),
        ):
            with self.subTest(label):
                self.assertIsNone(usage_rate(numerator, denominator))

    def test_zero_observed_turns_never_produce_a_fabricated_kappa(self) -> None:
        manifest = frozen_manifest()
        rows = [
            _bound_row(manifest, task, execution={"turns": 0})
            for task in manifest["suite"]["tasks"]
        ]
        self.assertIsNone(score_metrics(rows)["token_efficiency_kappa"])


class TestDeterminism(unittest.TestCase):
    """Accounting depends on the population, not on the arrival order."""

    def test_the_published_report_is_independent_of_row_order(self) -> None:
        manifest = frozen_manifest()
        rows = _graded(manifest, 18)
        rows[29] = _bound_row(manifest, TASK_IDS[29], settlement=dict(EXHAUSTED))
        baseline = publish_control_report(record=manifest, rows=rows)
        shuffled = list(rows)
        random.Random(52).shuffle(shuffled)
        self.assertNotEqual([r["identity"]["task_id"] for r in shuffled],
                            [r["identity"]["task_id"] for r in rows])
        self.assertEqual(publish_control_report(record=manifest, rows=shuffled), baseline)


if __name__ == "__main__":
    unittest.main()
