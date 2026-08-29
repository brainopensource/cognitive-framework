"""Tests for context compaction and prompt prefix middleware."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.context.duplicate_observation_filter import filter_redundant_observation
from middleware.context.history_compactor import compact_action_history
from middleware.context.stable_prefix_builder import build_stable_prefix


class TestContextMiddleware(unittest.TestCase):
    def test_build_stable_prefix(self) -> None:
        prefix = build_stable_prefix(
            constitutional_rules=["Rule 1: no bypass", "Rule 2: fail closed"],
            role_contract="You are an autonomous bug fixer.",
            tool_schemas_summary="fs.read, patch.apply",
        )
        self.assertIn("Rule 1: no bypass", prefix)
        self.assertIn("Role Contract", prefix)
        self.assertIn("Available Operations", prefix)

    def test_compact_action_history(self) -> None:
        turns = [
            {"action": "fs.read", "proposal": "read file 1", "receipt": "contents 1"},
            {"action": "fs.search", "proposal": "search foo", "receipt": "hits"},
            {"action": "patch.apply", "proposal": "apply patch", "receipt": "ok"},
            {"action": "proc.exec", "proposal": "run test", "receipt": "passed"},
        ]
        compacted = compact_action_history(turns, keep_last_n_receipts=2)
        self.assertEqual(len(compacted), 4)
        self.assertIn("summary", compacted[0]["content"])
        self.assertEqual(compacted[2]["action"], "patch.apply")

    def test_duplicate_observation_filter(self) -> None:
        observed = {}
        content = "print('hello')"
        is_dup, digest, out_text = filter_redundant_observation("main.py", content, observed)
        self.assertFalse(is_dup)
        self.assertEqual(out_text, content)

        observed["main.py"] = digest
        is_dup2, digest2, out_text2 = filter_redundant_observation("main.py", content, observed)
        self.assertTrue(is_dup2)
        self.assertIn("unchanged", out_text2)


if __name__ == "__main__":
    unittest.main()
