from __future__ import annotations

import unittest

from pkg.stats import mean, median


class StatsTests(unittest.TestCase):
    def test_mean_is_a_float(self) -> None:
        self.assertEqual(mean([1, 2]), 1.5)

    def test_median_sorts_first(self) -> None:
        self.assertEqual(median([3, 1, 2]), 2)

    def test_median_of_even_length(self) -> None:
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_empty_raises(self) -> None:
        with self.assertRaises(ValueError):
            mean([])
        with self.assertRaises(ValueError):
            median([])


if __name__ == "__main__":
    unittest.main()
