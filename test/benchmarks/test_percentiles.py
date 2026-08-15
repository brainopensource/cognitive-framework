"""Unit tests for exact percentile calculation (p50, p95, p99).

Owning contract: REQ-BENCH-001, VG-07 §5.6.
"""

from __future__ import annotations

import unittest

from tools.telemetry.metrics import calculate_percentiles


class PercentilesTest(unittest.TestCase):
    def test_empty_samples(self) -> None:
        res = calculate_percentiles([])
        self.assertEqual(res["p50"], 0.0)
        self.assertEqual(res["p95"], 0.0)
        self.assertEqual(res["p99"], 0.0)
        self.assertEqual(res["count"], 0.0)
        self.assertEqual(res["mean"], 0.0)

    def test_single_sample(self) -> None:
        res = calculate_percentiles([42.5])
        self.assertEqual(res["p50"], 42.5)
        self.assertEqual(res["p95"], 42.5)
        self.assertEqual(res["p99"], 42.5)
        self.assertEqual(res["min"], 42.5)
        self.assertEqual(res["max"], 42.5)
        self.assertEqual(res["mean"], 42.5)
        self.assertEqual(res["count"], 1.0)

    def test_known_distribution_percentiles(self) -> None:
        # 100 samples from 1 to 100
        samples = list(range(1, 101))
        res = calculate_percentiles(samples, percentiles=(50.0, 90.0, 95.0, 99.0))
        self.assertAlmostEqual(res["p50"], 50.5, places=1)
        self.assertAlmostEqual(res["p95"], 95.05, places=1)
        self.assertAlmostEqual(res["p99"], 99.01, places=1)
        self.assertEqual(res["min"], 1.0)
        self.assertEqual(res["max"], 100.0)
        self.assertAlmostEqual(res["mean"], 50.5, places=2)
        self.assertEqual(res["count"], 100.0)

    def test_odd_and_even_counts(self) -> None:
        odd_samples = [10.0, 20.0, 30.0]
        res_odd = calculate_percentiles(odd_samples)
        self.assertEqual(res_odd["p50"], 20.0)

        even_samples = [10.0, 20.0, 30.0, 40.0]
        res_even = calculate_percentiles(even_samples)
        self.assertEqual(res_even["p50"], 25.0)


if __name__ == "__main__":
    unittest.main()
