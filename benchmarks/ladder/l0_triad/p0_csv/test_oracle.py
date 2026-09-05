"""Exterior oracle for P0-CSV."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from pipeline import transform


class CsvOracle(unittest.TestCase):
    def test_totals(self) -> None:
        src = Path(__file__).with_name("input.csv")
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "out.csv"
            transform(str(src), str(dst))
            rows = list(csv.DictReader(dst.open(encoding="utf-8")))
        self.assertEqual(rows[0]["total"], "6")
        self.assertEqual(rows[1]["total"], "20")

    def test_missing_column_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "bad.csv"
            src.write_text("name,qty\na,1\n", encoding="utf-8")
            with self.assertRaises(Exception):
                transform(str(src), str(Path(tmp) / "out.csv"))


if __name__ == "__main__":
    unittest.main()
