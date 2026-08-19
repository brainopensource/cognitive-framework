from __future__ import annotations

import unittest

from layer0.kernel.budget import BudgetDenied, Governor
from layer0.spi.types_gen import Reservation


class SixDimensionBudgetTests(unittest.TestCase):
    def test_reservation_exposes_turns_and_depth(self) -> None:
        res = Reservation(usd_micros=1, millis=2, tokens=3, bytes=4, turns=5, depth=6)
        self.assertEqual(res.as_map()["turns"], 5)
        self.assertEqual(res.as_map()["depth"], 6)

    def test_exhausted_turns_are_denied(self) -> None:
        gov = Governor({"turns": 1, "depth": 2, "tokens": 10})
        gov.reserve("run", Reservation(0, 0, 0, 0, 1, 0))
        with self.assertRaises(BudgetDenied) as caught:
            gov.reserve("run", Reservation(0, 0, 0, 0, 1, 0))
        self.assertEqual(caught.exception.dimension, "turns")

    def test_overrun_is_debited(self) -> None:
        gov = Governor({"tokens": 10})
        lease = gov.reserve("run", Reservation(0, 0, 4, 0, 0, 0))
        gov.commit(lease, {"tokens": 7})
        self.assertEqual(gov.spent("tokens"), 7)
        self.assertEqual(gov.remaining("tokens"), 3)
