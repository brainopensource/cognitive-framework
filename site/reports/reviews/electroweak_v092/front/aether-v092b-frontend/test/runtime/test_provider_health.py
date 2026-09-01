"""Tests for provider health tracking and deterministic rotation (REQ-TRUST-001, S31)."""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.provider_health import (
    ProviderHealthTracker,
)


class TestProviderHealth(unittest.TestCase):
    def test_provider_health_recording(self) -> None:
        tracker = ProviderHealthTracker()
        self.assertTrue(tracker.is_healthy("openrouter/free"))

        tracker.record_success("openrouter/free", is_tool_call=True)
        stats = tracker.get_stats("openrouter/free")
        self.assertEqual(stats.successful_calls, 1)
        self.assertEqual(stats.tool_call_successes, 1)
        self.assertEqual(stats.consecutive_failures, 0)

        # Record malformed response
        tracker.record_malformed("openrouter/free", cooldown_seconds=10.0)
        self.assertEqual(tracker.get_stats("openrouter/free").malformed_calls, 1)
        self.assertTrue(tracker.get_stats("openrouter/free").is_in_cooldown)
        self.assertFalse(tracker.is_healthy("openrouter/free"))

    def test_rotation_selects_healthy_alternative(self) -> None:
        tracker = ProviderHealthTracker()
        candidates = [
            "openrouter/free",
            "cohere/north-mini-code:free",
            "google/gemma-4-26b-a4b-it:free",
        ]
        # Malformed on openrouter/free
        tracker.record_malformed("openrouter/free", cooldown_seconds=60.0)

        next_model = tracker.rotate_provider(candidates, current="openrouter/free")
        self.assertIn(next_model, ["cohere/north-mini-code:free", "google/gemma-4-26b-a4b-it:free"])
        self.assertNotEqual(next_model, "openrouter/free")


if __name__ == "__main__":
    unittest.main()
