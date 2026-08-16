"""LAM (LLM API Mock) — stateless OpenAI-compatible chat completions.

Owning idea: tools/002_LLM_API_MOCK. A harness CI accelerator that replays
recorded agentic coding cascades (system + tools + tool observations) in
milliseconds, with the same JSON shape OpenRouter would return.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAM = ROOT / "tools" / "002_LLM_API_MOCK"


class LamImport(unittest.TestCase):
    def test_engine_module_exists(self) -> None:
        self.assertTrue((LAM / "engine.py").is_file(), "tools/002_LLM_API_MOCK/engine.py must exist")


class StatelessTurnAdvance(unittest.TestCase):
    def setUp(self) -> None:
        import sys

        sys.path.insert(0, str(LAM))
        from engine import LamEngine

        self.engine = LamEngine.from_directory(LAM / "scenarios")

    def test_tier1_calculator_turn0_calls_view_file(self) -> None:
        body = {
            "model": "lam/t1-calculator",
            "messages": [
                {"role": "system", "content": "You are OpenCode."},
                {
                    "role": "user",
                    "content": "Fix the bug in src/calculator.py where calculate_value(A, B) fails tests for formula (A + B) * B.",
                },
            ],
            "tools": [{"type": "function", "function": {"name": "view_file"}}],
        }
        result = self.engine.complete(body)
        message = result["choices"][0]["message"]
        self.assertEqual(result["choices"][0]["finish_reason"], "tool_calls")
        self.assertEqual(message["tool_calls"][0]["function"]["name"], "view_file")
        args = json.loads(message["tool_calls"][0]["function"]["arguments"])
        self.assertEqual(args["path"], "src/calculator.py")

    def test_tier1_advances_on_tool_observation_count_not_session_state(self) -> None:
        """Stateless: two independent engines with the same history must agree."""
        history = [
            {"role": "system", "content": "You are OpenCode."},
            {"role": "user", "content": "Fix the bug in src/calculator.py where calculate_value(A, B) fails tests for formula (A + B) * B."},
            {
                "role": "assistant",
                "content": "inspect",
                "tool_calls": [
                    {
                        "id": "call_view_001",
                        "type": "function",
                        "function": {"name": "view_file", "arguments": '{"path": "src/calculator.py"}'},
                    }
                ],
            },
            {
                "role": "tool",
                "tool_call_id": "call_view_001",
                "name": "view_file",
                "content": "def calculate_value(A, B):\n    return (A + B) + B\n",
            },
        ]
        import sys

        sys.path.insert(0, str(LAM))
        from engine import LamEngine

        a = LamEngine.from_directory(LAM / "scenarios")
        b = LamEngine.from_directory(LAM / "scenarios")
        first = a.complete({"model": "lam/t1-calculator", "messages": history})
        second = b.complete({"model": "lam/t1-calculator", "messages": history})
        self.assertEqual(first["choices"][0]["message"]["tool_calls"][0]["function"]["name"], "edit_file")
        self.assertEqual(
            first["choices"][0]["message"]["tool_calls"],
            second["choices"][0]["message"]["tool_calls"],
        )

    def test_tier1_stop_after_tests_pass(self) -> None:
        messages = [
            {"role": "system", "content": "You are OpenCode."},
            {"role": "user", "content": "Fix the bug in src/calculator.py where calculate_value(A, B) fails tests for formula (A + B) * B."},
            {"role": "assistant", "tool_calls": [{"id": "a", "type": "function", "function": {"name": "view_file", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "a", "content": "file"},
            {"role": "assistant", "tool_calls": [{"id": "b", "type": "function", "function": {"name": "edit_file", "arguments": "{}"}}]},
            {"role": "tool", "tool_call_id": "b", "content": "ok"},
            {"role": "user", "content": "Verification test runner output:\n$ pytest test_calculator.py\n3 passed"},
        ]
        result = self.engine.complete({"model": "lam/t1-calculator", "messages": messages})
        self.assertEqual(result["choices"][0]["finish_reason"], "stop")
        self.assertIn("usage", result)
        self.assertGreater(result["usage"]["total_tokens"], 0)

    def test_five_tiers_are_registered(self) -> None:
        ids = {scenario.id for scenario in self.engine.scenarios}
        self.assertTrue(any(s.startswith("t1-") for s in ids))
        self.assertTrue(any(s.startswith("t2-") for s in ids))
        self.assertTrue(any(s.startswith("t3-") for s in ids))
        self.assertTrue(any(s.startswith("t4-") for s in ids))
        self.assertTrue(any(s.startswith("t5-") for s in ids))

    def test_tier5_has_more_turns_than_tier1(self) -> None:
        max_t5 = max(len(s.turns) for s in self.engine.scenarios if s.id.startswith("t5-"))
        min_t1 = min(len(s.turns) for s in self.engine.scenarios if s.id.startswith("t1-"))
        self.assertGreater(max_t5, min_t1)

    def test_unknown_model_is_instrument_error_not_a_guess(self) -> None:
        with self.assertRaises(KeyError):
            self.engine.complete({"model": "lam/does-not-exist", "messages": []})


class SimulatedHarnessMetrics(unittest.TestCase):
    def test_tier1_cascade_reports_calls_tokens_and_price(self) -> None:
        import sys

        sys.path.insert(0, str(LAM))
        from simulate import simulate_scenario

        report = simulate_scenario("t1-calculator")
        self.assertGreaterEqual(report["llm_calls"], 3)
        self.assertGreater(report["total_tokens"], 0)
        self.assertEqual(report["estimated_usd_lam"], 0.0)
        self.assertGreater(report["estimated_usd_if_sonnet"], 0.0)
        self.assertLess(report["wall_ms"], 500)


if __name__ == "__main__":
    unittest.main()
