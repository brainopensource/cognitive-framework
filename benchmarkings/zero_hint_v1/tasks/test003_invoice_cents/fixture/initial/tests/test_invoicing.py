from __future__ import annotations

import unittest

from invoicing import invoice_cents, line_cents


class InvoiceTests(unittest.TestCase):
    def test_rejects_malformed_price(self) -> None:
        with self.assertRaises(ValueError):
            line_cents(1, "1.2")
        with self.assertRaises(ValueError):
            line_cents(-1, "1.00")

    def test_zero_quantity_is_free(self) -> None:
        self.assertEqual(line_cents(0, "19.99"), 0)

    def test_repeated_catalog_price(self) -> None:
        self.assertEqual(line_cents(1, "0.29"), 29)
        self.assertEqual(line_cents(3, "1.15"), 345)
        self.assertEqual(line_cents(3, "19.99"), 5997)

    def test_invoice_matches_the_sum_of_lines(self) -> None:
        lines = [(3, "1.15"), (2, "0.10"), (1, "0.29")]
        parts = [line_cents(q, p) for q, p in lines]
        self.assertEqual(invoice_cents(lines), sum(parts))
        self.assertEqual(invoice_cents(lines), 394)


if __name__ == "__main__":
    unittest.main()
