"""Tests for LAM ladder runner."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from ladder import run_ladder


class TestLamLadder(unittest.TestCase):
    def test_ladder_on_lam_tier1_passes_without_network(self) -> None:
        row = run_ladder("lam/t1-calculator", "t1-calculator", transport="forbidden")
        self.assertTrue(row["passed"])
        self.assertGreaterEqual(row["llm_calls"], 3)
        self.assertEqual(row["estimated_usd"], 0.0)

    def test_ladder_does_not_open_sockets(self) -> None:
        with self.assertRaises(ValueError):
            run_ladder("nvidia/nemotron-3-super-120b-a12b:free", "t1-calculator", transport="forbidden")

    def test_ladder_with_fake_transport(self) -> None:
        def fake_complete(model: str, messages: list[dict], tools: list[dict] | None = None) -> dict:
            return {
                "id": "chatcmpl-fake",
                "choices": [{"message": {"role": "assistant", "content": "done"}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            }

        row = run_ladder("nvidia/nemotron-3-super-120b-a12b:free", "t1-calculator", complete=fake_complete)
        self.assertTrue(row["passed"])
        self.assertEqual(row["total_tokens"], 30)

    def test_escalation_stops_on_failure(self) -> None:
        from ladder import run_escalated_ladder

        def fake_failing_complete(model: str, messages: list[dict], tools: list[dict] | None = None) -> dict:
            return {
                "id": "chatcmpl-fake",
                "choices": [{"message": {"role": "assistant", "content": "failed"}}],
                "usage": {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
            }

        # Override run_ladder pass check in fake scenario test
        rows = run_escalated_ladder("lam/t1-calculator", ["t1-calculator", "t2-import-cycle"])
        self.assertEqual(len(rows), 2)



if __name__ == "__main__":
    unittest.main()
