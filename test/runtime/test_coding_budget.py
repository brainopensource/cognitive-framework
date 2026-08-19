"""Worst-case spend is a 6D Reservation settled by the kernel Governor."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"


class TestPackReservationGovernor(unittest.TestCase):
    def setUp(self) -> None:
        sys.path.insert(0, str(PACK))
        from layer0.kernel.budget import BudgetDenied, Governor
        from reservation import worst_case_reservation

        self.BudgetDenied = BudgetDenied
        self.Governor = Governor
        self.worst_case_reservation = worst_case_reservation

    def test_free_model_reservation_zero_usd(self) -> None:
        governor = self.Governor({
            "usd_micros": 500_000, "millis": 10**9, "tokens": 10**6,
            "bytes": 0, "turns": 10, "depth": 2,
        })
        reserved = self.worst_case_reservation(model="openrouter/free", pricing=None)
        self.assertEqual(reserved.usd_micros, 0)
        lease = governor.reserve("run", reserved)
        self.assertEqual(lease.reserved.get("usd_micros", 0), 0)

    def test_paid_model_worst_case_micros(self) -> None:
        reserved = self.worst_case_reservation(
            model="deepseek/deepseek-v4-flash",
            pricing=(140_000, 280_000, 14_000),
            max_prompt_tokens=10_000,
            max_completion_tokens=5_000,
        )
        self.assertEqual(reserved.usd_micros, 2800)

    def test_unknown_pricing_fails_closed(self) -> None:
        with self.assertRaises(self.BudgetDenied):
            self.worst_case_reservation(model="vendor/unpriced-model", pricing=None)


if __name__ == "__main__":
    unittest.main()
