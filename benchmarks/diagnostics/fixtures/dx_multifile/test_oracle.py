import unittest

import ledger
from formatter import format_row


class TestSplit(unittest.TestCase):
    def test_parse_stays_in_ledger(self) -> None:
        self.assertEqual(ledger.parse_row("a = 1"), {"key": "a", "value": "1"})

    def test_formatter_moved(self) -> None:
        self.assertEqual(format_row({"key": "a", "value": "1"}), "a=1")

    def test_ledger_reexports(self) -> None:
        self.assertIs(ledger.format_row, format_row)


if __name__ == "__main__":
    unittest.main()
