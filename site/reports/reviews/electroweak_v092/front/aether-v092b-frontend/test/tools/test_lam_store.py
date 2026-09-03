"""Tests for SQLite LAM store."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from store import LamStore


class TestLamStore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.tmp_dir) / "test_lam.sqlite"
        self.store = LamStore(self.db_path)

    def test_upsert_scenario_and_insert_trace(self) -> None:
        self.store.upsert_scenario(
            scenario_id="t1-calculator",
            tier=1,
            title="Calculator Test",
            atoms=["view_file", "edit_file", "run_command"],
            n_files=2,
            n_turns=3,
        )

        trace_id = self.store.insert_trace(
            scenario_id="t1-calculator",
            backend="lam",
            model="lam/t1-calculator",
            passed=True,
            llm_calls=4,
            prompt_tokens=100,
            completion_tokens=50,
            usd=0.0,
            wall_s=0.02,
        )
        self.assertGreater(trace_id, 0)

        kpis = self.store.get_summary_kpis()
        self.assertEqual(kpis["total_scenarios"], 1)
        self.assertEqual(kpis["total_traces"], 1)
        self.assertEqual(kpis["total_calls"], 4)
        self.assertEqual(kpis["total_tokens"], 150)
        self.assertEqual(len(kpis["model_ceilings"]), 1)
        self.assertEqual(kpis["model_ceilings"][0]["ceiling_tier"], 1)


if __name__ == "__main__":
    unittest.main()
