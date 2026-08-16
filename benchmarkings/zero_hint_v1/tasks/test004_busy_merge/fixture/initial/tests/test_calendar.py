from __future__ import annotations

import unittest

from busy import merge_busy


class BusyMergeTests(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(merge_busy([]), [])

    def test_overlapping_periods_collapse(self) -> None:
        self.assertEqual(merge_busy([(1, 4), (3, 6)]), [(1, 6)])

    def test_touching_periods_are_one_period(self) -> None:
        self.assertEqual(merge_busy([(1, 2), (2, 3)]), [(1, 3)])

    def test_order_does_not_matter(self) -> None:
        self.assertEqual(
            merge_busy([(10, 12), (1, 3), (3, 5)]),
            [(1, 5), (10, 12)],
        )


if __name__ == "__main__":
    unittest.main()
