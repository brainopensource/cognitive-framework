"""Tests for Periodic Re-grounding Policy (S10-B-04)."""

from __future__ import annotations

import unittest

from vanguard.packages.agency.context.regrounding import RegroundPolicy


class TestRegroundPolicy(unittest.TestCase):
    def test_cadence_trigger(self) -> None:
        """S10-B-04: should_reground returns true at configured cadence."""
        policy = RegroundPolicy(interval_turns=5, observation_verb="fs.read")
        self.assertFalse(policy.should_reground(0))
        self.assertFalse(policy.should_reground(1))
        self.assertFalse(policy.should_reground(4))
        self.assertTrue(policy.should_reground(5))
        self.assertTrue(policy.should_reground(10))

    def test_creates_standard_effect_request(self) -> None:
        """S10-B-04: create_effect_request constructs standard EffectRequest without bypass."""
        policy = RegroundPolicy(interval_turns=3, observation_verb="fs.read")
        req = policy.create_effect_request(episode_id="ep-101", turn_index=3)
        self.assertEqual(req.verb, "fs.read")
        self.assertEqual(req.action, "read")
        self.assertEqual(req.args.get("purpose"), "periodic_regrounding")
        self.assertEqual(req.args.get("episode_id"), "ep-101")


if __name__ == "__main__":
    unittest.main()
