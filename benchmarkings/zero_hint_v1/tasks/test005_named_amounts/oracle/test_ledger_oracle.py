from __future__ import annotations

import unittest

from pkg.parser import parse_rows
from pkg.stats import grand_total, totals_by_name


class NamedAmountOracle(unittest.TestCase):
    def test_blank_lines_and_whitespace(self) -> None:
        rows = parse_rows(["  alice, 10 ", "", "bob,5"])
        self.assertEqual(rows, [("alice", 10), ("bob", 5)])

    def test_duplicate_names_accumulate(self) -> None:
        rows = parse_rows(["a,1", "a,2", "b,3"])
        self.assertEqual(totals_by_name(rows), {"a": 3, "b": 3})
        self.assertEqual(grand_total(rows), 6)


if __name__ == "__main__":
    unittest.main()
