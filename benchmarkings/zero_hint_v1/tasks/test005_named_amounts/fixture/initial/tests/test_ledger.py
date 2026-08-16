from __future__ import annotations

import unittest

from pkg.parser import parse_rows
from pkg.stats import grand_total, totals_by_name


class NamedAmountTests(unittest.TestCase):
    def test_two_named_amounts(self) -> None:
        rows = parse_rows(["alice,10", "bob,20"])
        self.assertEqual(rows, [("alice", 10), ("bob", 20)])
        self.assertEqual(totals_by_name(rows), {"alice": 10, "bob": 20})
        total = grand_total(rows)
        self.assertEqual(total, 30)
        self.assertIsInstance(total, int)


if __name__ == "__main__":
    unittest.main()
