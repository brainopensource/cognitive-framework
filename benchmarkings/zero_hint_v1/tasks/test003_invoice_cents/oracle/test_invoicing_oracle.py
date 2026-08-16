from __future__ import annotations

import unittest

from invoicing import invoice_cents, line_cents


class InvoiceOracle(unittest.TestCase):
    def test_many_small_units(self) -> None:
        self.assertEqual(line_cents(1, "0.29"), 29)
        self.assertEqual(line_cents(17, "0.10"), 170)
        self.assertEqual(invoice_cents([(17, "0.10"), (1, "0.29")]), 199)

    def test_large_quantity_catalog_price(self) -> None:
        self.assertEqual(line_cents(8, "19.99"), 15992)


if __name__ == "__main__":
    unittest.main()
