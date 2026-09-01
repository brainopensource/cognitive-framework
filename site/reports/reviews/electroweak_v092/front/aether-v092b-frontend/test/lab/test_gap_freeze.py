"""Tests for Verifier-Deployment Gap Freeze (S10-C-02)."""

from __future__ import annotations

import unittest

from tools.telemetry.gap_freeze import GapFreezeMonitor, PromotionFrozenError


class TestGapFreeze(unittest.TestCase):
    def test_promotion_allowed_when_gap_within_threshold(self) -> None:
        """S10-C-02: Promotion proceeds when verifier and deployment align."""
        monitor = GapFreezeMonitor(max_allowed_gap=0.15)
        monitor.record_deployment_outcome("pack-001", promotion_score=0.85, deployment_score=0.80)
        self.assertFalse(monitor.is_frozen)
        # Should not raise
        monitor.verify_promotion_allowed("pack-002")

    def test_promotion_automatically_freezes_when_gap_widens(self) -> None:
        """S10-C-02: Automatic freeze triggered when gap > max_allowed_gap (T8.7)."""
        monitor = GapFreezeMonitor(max_allowed_gap=0.15)
        monitor.record_deployment_outcome("pack-002", promotion_score=0.90, deployment_score=0.60)
        self.assertTrue(monitor.is_frozen)
        self.assertIn("exceeded threshold", monitor.freeze_reason)

        with self.assertRaises(PromotionFrozenError):
            monitor.verify_promotion_allowed("pack-003")


if __name__ == "__main__":
    unittest.main()
