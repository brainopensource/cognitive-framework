from __future__ import annotations

import unittest

from busy import merge_busy


class BusyMergeOracle(unittest.TestCase):
    def test_nested_interval_disappears(self) -> None:
        self.assertEqual(merge_busy([(0, 10), (2, 3), (9, 12)]), [(0, 12)])

    def test_identical_duplicates(self) -> None:
        self.assertEqual(merge_busy([(4, 4), (4, 4)]), [(4, 4)])

    def test_chain_of_abutting_slots(self) -> None:
        self.assertEqual(merge_busy([(0, 1), (1, 2), (2, 3)]), [(0, 3)])


if __name__ == "__main__":
    unittest.main()
