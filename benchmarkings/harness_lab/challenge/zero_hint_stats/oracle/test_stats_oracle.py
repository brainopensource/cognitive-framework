from __future__ import annotations

import unittest

from pkg.stats import mean, median


class StatsOracle(unittest.TestCase):
    """Held-out. Never shown to the model (`oracleVisibleToModel: false`)."""

    def test_mean_does_not_truncate(self) -> None:
        self.assertAlmostEqual(mean([1, 2, 2]), 5 / 3)
        self.assertAlmostEqual(mean([-1, 2]), 0.5)

    def test_median_handles_unsorted_even_length(self) -> None:
        self.assertAlmostEqual(median([4, 1, 3, 2]), 2.5)
        self.assertAlmostEqual(median([10, -10]), 0.0)

    def test_median_odd_length_unsorted(self) -> None:
        self.assertEqual(median([9, 1, 5]), 5)

    def test_both_reject_empty(self) -> None:
        for fn in (mean, median):
            with self.assertRaises(ValueError):
                fn([])


if __name__ == "__main__":
    unittest.main()
