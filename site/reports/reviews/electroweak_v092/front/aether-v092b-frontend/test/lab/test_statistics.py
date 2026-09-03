"""Tests for Statistics Module (S9-C-04)."""

from __future__ import annotations

import unittest

from tools.telemetry.statistics import (
    kaplan_meier_survival,
    mcnemar_exact,
    paired_bootstrap_ci,
)


class TestStatistics(unittest.TestCase):
    def test_mcnemar_refuses_p_value_at_n_less_than_20(self) -> None:
        """S9-C-04: M-28 rule: No p-values when n < 20."""
        res = mcnemar_exact(b=2, c=1, n_total=3)
        self.assertTrue(res.refused_p_value)
        self.assertIsNone(res.p_value)
        self.assertIn("insufficient", res.reason)

        res_n19 = mcnemar_exact(b=10, c=2, n_total=19)
        self.assertTrue(res_n19.refused_p_value)
        self.assertIsNone(res_n19.p_value)

    def test_mcnemar_emits_p_value_at_n_greater_equal_20(self) -> None:
        """S9-C-04: McNemar exact emits valid p-value when n >= 20."""
        res = mcnemar_exact(b=15, c=2, n_total=25)
        self.assertFalse(res.refused_p_value)
        self.assertIsNotNone(res.p_value)
        self.assertTrue(0.0 <= res.p_value <= 1.0)
        self.assertEqual(res.risk_difference, (15 - 2) / 25)

    def test_paired_bootstrap_ci(self) -> None:
        """S9-C-04: Paired bootstrap calculates empirical confidence intervals."""
        a = [10.0, 12.0, 15.0, 20.0, 18.0, 22.0, 25.0, 30.0]
        b = [8.0, 10.0, 11.0, 14.0, 12.0, 18.0, 20.0, 22.0]
        res = paired_bootstrap_ci(a, b, n_iterations=500, confidence_level=0.95)
        # b is consistently lower than a -> mean diff should be negative
        self.assertTrue(res.mean_diff < 0)
        self.assertTrue(res.ci_lower <= res.mean_diff <= res.ci_upper)

    def test_survival_methods_for_censoring_and_timeouts(self) -> None:
        """S9-C-04: Right-censored survival curves for execution duration."""
        times = [100, 200, 300, 400, 500]
        # events: 3 succeeded, 2 timed out/censored
        events = [True, True, False, True, False]
        curve = kaplan_meier_survival(times, events)
        self.assertEqual(len(curve), 5)
        self.assertEqual(curve[0].survival_prob, 1.0 - (1 / 5))
        # Survival prob decreases monotonically
        for i in range(1, len(curve)):
            self.assertTrue(curve[i].survival_prob <= curve[i - 1].survival_prob)


if __name__ == "__main__":
    unittest.main()
