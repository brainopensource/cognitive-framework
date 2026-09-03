"""Tests for StructuredConsolidateStrategy and deadEnds tracking (S10-B-03)."""

from __future__ import annotations

import unittest

from vanguard.packages.agency.context.compaction import (
    StructuredConsolidateStrategy,
    StructuredRecord,
    resolve_compaction_strategy,
)
from vanguard.packages.agency.context.layers import Block, Layer


class TestStructuredCompaction(unittest.TestCase):
    def test_structured_record_formats_summary(self) -> None:
        """S10-B-03: StructuredRecord formats decisions, invariants, open items, and deadEnds."""
        rec = StructuredRecord(
            decisions=["Use relational model"],
            invariants=["Sum = 100"],
            open_items=["Task 3"],
            artifacts=["accounts_table"],
            dead_ends=["Failed approach using regex parser"],
        )
        text = rec.to_summary_text()
        self.assertIn("Decisions:", text)
        self.assertIn("Invariants:", text)
        self.assertIn("DeadEnds", text)
        self.assertIn("regex parser", text)

    def test_compaction_replaces_overflowing_dialogue_with_structured_record(self) -> None:
        """S10-B-03: StructuredConsolidateStrategy captures dead ends and drops excessive tokens."""
        strategy = StructuredConsolidateStrategy()
        notes = []
        dialogue = [
            Block(Layer.DIALOGUE, "model", "turn_1", "I tried algorithm A but got an error / dead end", evictable=True),
            Block(Layer.DIALOGUE, "model", "turn_2", "Decision: switched to algorithm B", evictable=True),
            Block(Layer.DIALOGUE, "model", "turn_3", "Now inspecting final results", evictable=False),
        ]

        # Compact with small ceiling (65 < total 78) so older turns consolidate
        elided, dropped = strategy.compact(floor=50, ceiling=65, notes=notes, dialogue=dialogue)
        self.assertIn("turn_1", dropped)
        self.assertIn("structured_record", elided)
        self.assertTrue(len(dialogue) > 0)
        self.assertEqual(dialogue[0].label, "structured_record")
        self.assertIn("DeadEnds", dialogue[0].text)

    def test_resolution_from_manifest_policy(self) -> None:
        """S10-B-03: resolve_compaction_strategy resolves structured-consolidate."""
        strat, _ = resolve_compaction_strategy("structured-consolidate")
        self.assertIsInstance(strat, StructuredConsolidateStrategy)


if __name__ == "__main__":
    unittest.main()
