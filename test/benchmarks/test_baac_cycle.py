"""Integration test for full BaaC (Benchmarking as Code) cycle execution."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import tempfile
import unittest

from benchmarks.baac.lib.budget import BudgetCapConfig
from benchmarks.baac.lib.runner import BaaCRunner
from benchmarks.baac.lib.state import (
    generate_challenge_manifest,
    verify_challenge_zero_state,
)


class TestBaaCCycleIntegration(unittest.TestCase):
    """Hermetic end-to-end integration test of the BaaC cycle."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="baac-cycle-test-")
        self.root = Path(self.temp_dir)
        self.challenge_dir = self.root / "easy" / "sum_pair"
        (self.challenge_dir / "src").mkdir(parents=True)
        (self.challenge_dir / "oracle").mkdir(parents=True)

        (self.challenge_dir / "challenge.yaml").write_text(
            "schema: aether.baac.challenge/1\n"
            "id: sum_pair\n"
            "name: Sum Pair\n"
            "scope: single\n"
            "context_bracket: 2K\n"
            "tier: easy\n",
            encoding="utf-8",
        )
        (self.challenge_dir / "TASK.md").write_text("# Task\nImplement add_two(a, b) in src/calc.py\n", encoding="utf-8")
        (self.challenge_dir / "src" / "calc.py").write_text("def add_two(a: int, b: int) -> int:\n    return a + b\n", encoding="utf-8")

        # External oracle
        oracle_code = """#!/usr/bin/env python3
import sys, argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--workspace', default='.')
args = parser.parse_args()

ws = Path(args.workspace).resolve()
sys.path.insert(0, str(ws / 'src'))

from calc import add_two
assert add_two(2, 3) == 5
assert add_two(-1, 1) == 0
print('ALL ORACLE ASSERTIONS PASSED')
sys.exit(0)
"""
        (self.challenge_dir / "oracle" / "verify.py").write_text(oracle_code, encoding="utf-8")
        generate_challenge_manifest(self.challenge_dir)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_hermetic_baac_cycle(self) -> None:
        # Stage 1: Pre-verify zero-state
        ok_pre, drifts_pre = verify_challenge_zero_state(self.challenge_dir)
        self.assertTrue(ok_pre, f"Pre-verify failed: {drifts_pre}")

        # Stage 2: Execute Runner
        runner = BaaCRunner(
            preset="vg-1-forge",
            mode="lam",
            budget_config=BudgetCapConfig(max_turns=3, max_cost_usd=0.05),
        )
        res = runner.run_challenge(self.challenge_dir)

        self.assertEqual(res.status, "PASS")
        self.assertEqual(res.attribution, "PASS")
        self.assertIsNotNone(res.oracle_result)
        self.assertTrue(res.oracle_result.passed)

        # Stage 3: Post-verify zero-state to ensure pristine source was untouched
        ok_post, drifts_post = verify_challenge_zero_state(self.challenge_dir)
        self.assertTrue(ok_post, f"Post-verify failed (source drifted!): {drifts_post}")


if __name__ == "__main__":
    unittest.main()
