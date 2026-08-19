"""S-M3-B-06: compaction + repo-map budgets from harness.yaml."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"


class ContextPolicyTests(unittest.TestCase):
    def test_policy_reads_harness_config(self) -> None:
        sys.path.insert(0, str(PACK))
        from context_policy import context_policy_from_harness

        policy = context_policy_from_harness()
        self.assertEqual(policy["token_budget"], 4000)
        self.assertEqual(policy["compaction"], "recency-window")
        self.assertTrue(policy["prefix_freeze"])

    def test_prefix_freeze_survives_compaction(self) -> None:
        sys.path.insert(0, str(PACK / "toolkits"))
        from repo_map import IndexToolkit, RepoMapContext
        from layer0.spi.types_gen import EpisodeView, Receipt, Reservation

        index = IndexToolkit("/tmp")
        context = RepoMapContext(system_prefix="FROZEN-PREFIX\n", index=index, token_budget=32)
        compiled = context.compile(EpisodeView("r", "e", 1, "g"), 32)
        prefix = compiled.value.prefix
        context.ingest((Receipt("sha256:" + "0" * 64, "completed", Reservation(0, 0, 0, 0, 1, 1)),))
        context.compact(2.0)
        again = context.compile(EpisodeView("r", "e", 2, "g"), 32)
        self.assertEqual(again.value.prefix, prefix)
        self.assertEqual(again.value.prefix, "FROZEN-PREFIX\n")


if __name__ == "__main__":
    unittest.main()
