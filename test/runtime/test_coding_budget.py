"""Tests for hard microdollar budget controller (REQ-TRUST-001, S32)."""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.coding_budget import (
    BudgetController,
    ReservationResult,
)


class TestCodingBudget(unittest.TestCase):
    def test_free_model_reservation_zero_cost(self) -> None:
        controller = BudgetController(max_micros=500_000, max_paid_calls=10)
        res = controller.reserve(
            requested_model="openrouter/free",
            resolved_model="openrouter/free",
            pricing=None,
        )
        self.assertTrue(res.ok)
        self.assertIsNotNone(res.reservation)
        self.assertEqual(res.reservation.reserved_micros, 0)

        # Reconcile free call
        charge = controller.reconcile(
            res.reservation.reservation_id,
            actual_prompt_tokens=500,
            actual_completion_tokens=200,
        )
        self.assertEqual(charge, 0)
        self.assertEqual(controller.spent_micros, 0)
        self.assertEqual(controller.paid_calls_count, 0)

    def test_paid_model_reservation_and_reconciliation(self) -> None:
        controller = BudgetController(max_micros=500_000, max_paid_calls=10)
        # DeepSeek V4 Flash: (140_000, 280_000, 14_000) micros per 1M tokens
        pricing = (140_000, 280_000, 14_000)
        res = controller.reserve(
            requested_model="deepseek/deepseek-v4-flash",
            resolved_model="deepseek/deepseek-v4-flash",
            pricing=pricing,
            max_prompt_tokens=10_000,
            max_completion_tokens=5_000,
        )
        self.assertTrue(res.ok)
        self.assertIsNotNone(res.reservation)
        # Worst case: ceil(10000 * 140000 / 1e6) + ceil(5000 * 280000 / 1e6) = 1400 + 1400 = 2800 micros
        self.assertEqual(res.reservation.reserved_micros, 2800)
        self.assertEqual(controller.reserved_micros, 2800)
        self.assertEqual(controller.committed_micros, 2800)

        # Reconcile actual usage: 2000 prompt tokens, 1000 completion tokens
        # Actual: ceil(2000 * 140000 / 1e6) + ceil(1000 * 280000 / 1e6) = 280 + 280 = 560 micros
        charge = controller.reconcile(
            res.reservation.reservation_id,
            actual_prompt_tokens=2000,
            actual_completion_tokens=1000,
        )
        self.assertEqual(charge, 560)
        self.assertEqual(controller.spent_micros, 560)
        self.assertEqual(controller.reserved_micros, 0)
        self.assertEqual(controller.paid_calls_count, 1)

    def test_unknown_pricing_fails_closed(self) -> None:
        controller = BudgetController(max_micros=500_000)
        res = controller.reserve(
            requested_model="vendor/unpriced-model",
            resolved_model="vendor/unpriced-model",
            pricing=None,
        )
        self.assertFalse(res.ok)
        self.assertEqual(res.error_kind, "instrument_error:price_unknown")

    def test_budget_exhaustion_stops_reservation(self) -> None:
        # Budget of 1,000 micros ($0.001)
        controller = BudgetController(max_micros=1000, max_paid_calls=5)
        pricing = (500_000, 1_000_000, 50_000)
        res = controller.reserve(
            requested_model="expensive/model",
            resolved_model="expensive/model",
            pricing=pricing,
            max_prompt_tokens=5000,
            max_completion_tokens=2000,
        )
        # Reservation would be ceil(5000 * 500000 / 1e6) + ceil(2000 * 1000000 / 1e6) = 2500 + 2000 = 4500 micros
        self.assertFalse(res.ok)
        self.assertEqual(res.error_kind, "budget_exhausted")

    def test_unattributed_usage_is_safely_charged(self) -> None:
        controller = BudgetController(max_micros=100_000)
        pricing = (100_000, 200_000, 10_000)
        res = controller.reserve(
            requested_model="deepseek/deepseek-v4-flash",
            resolved_model="deepseek/deepseek-v4-flash",
            pricing=pricing,
            max_prompt_tokens=2000,
            max_completion_tokens=1000,
        )
        self.assertTrue(res.ok)
        # Reconcile with missing usage (None)
        charge = controller.reconcile(
            res.reservation.reservation_id,
            actual_prompt_tokens=None,
            actual_completion_tokens=None,
        )
        self.assertEqual(charge, res.reservation.reserved_micros)
        self.assertEqual(controller.unattributed_usage_count, 1)


if __name__ == "__main__":
    unittest.main()
