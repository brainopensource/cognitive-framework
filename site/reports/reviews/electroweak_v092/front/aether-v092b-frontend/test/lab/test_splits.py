"""Tests for Corpus Splits and Touch Ledger (S9-C-05)."""

from __future__ import annotations

import unittest

from tools.telemetry.splits import SplitPartition, SplitRegistry


class TestSplitRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self.splits = {
            SplitPartition.DEV: ["task-dev-1", "task-dev-2"],
            SplitPartition.HOLDOUT: ["task-holdout-1", "task-holdout-2"],
            SplitPartition.SEALED: ["task-sealed-1"],
            SplitPartition.LIVE: ["task-live-1"],
            SplitPartition.DEPLOYMENT: ["task-dep-1"],
        }
        self.registry = SplitRegistry(self.splits)

    def test_evaluation_read_preserves_holdout(self) -> None:
        """S9-C-05: Reading for evaluation preserves holdout partition."""
        part = self.registry.access_instance("task-holdout-1", access_type="eval_read", actor="evaluator")
        self.assertEqual(part, SplitPartition.HOLDOUT)
        self.assertEqual(self.registry.get_partition("task-holdout-1"), SplitPartition.HOLDOUT)
        self.assertFalse(self.registry.is_burned("task-holdout-1"))

    def test_prompt_tuning_access_burns_holdout_to_dev_forever(self) -> None:
        """S9-C-05: Contamination is one-way: tuning on HOLDOUT permanently burns it to DEV."""
        part = self.registry.access_instance("task-holdout-1", access_type="prompt_tuning", actor="developer")
        self.assertEqual(part, SplitPartition.DEV)
        self.assertEqual(self.registry.get_partition("task-holdout-1"), SplitPartition.DEV)
        self.assertTrue(self.registry.is_burned("task-holdout-1"))

        # Subsequent evaluation read still reflects DEV partition
        part2 = self.registry.access_instance("task-holdout-1", access_type="eval_read", actor="evaluator")
        self.assertEqual(part2, SplitPartition.DEV)

        # Audit ledger has record
        ledger = self.registry.touch_ledger()
        self.assertEqual(len(ledger), 2)
        self.assertEqual(ledger[0].burned_to, SplitPartition.DEV)


if __name__ == "__main__":
    unittest.main()
