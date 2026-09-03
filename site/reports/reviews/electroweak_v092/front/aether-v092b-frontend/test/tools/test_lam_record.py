"""Tests for live trace recorder."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from record import sanitize_secrets, trace_to_scenario


class TestLamRecord(unittest.TestCase):
    def test_sanitize_secrets_redacts_api_keys(self) -> None:
        raw = "key=sk-1234567890123456789012345678901234 OPENROUTER_API_KEY=secret_key_123"
        cleaned = sanitize_secrets(raw)
        self.assertNotIn("sk-1234567890123456789012345678901234", cleaned)
        self.assertNotIn("secret_key_123", cleaned)

    def test_trace_to_scenario_creates_valid_scenario(self) -> None:
        workspace = {"mod.py": "def foo(): pass"}
        captures = [
            {
                "tool_calls": [
                    {
                        "function": {
                            "name": "view_file",
                            "arguments": '{"path": "mod.py"}',
                        }
                    }
                ]
            },
            {"tool_calls": []},
        ]
        sc = trace_to_scenario("t1-calculator", 1, workspace, captures)
        self.assertEqual(sc["id"], "t1-calculator")
        self.assertEqual(len(sc["turns"]), 2)
        self.assertEqual(sc["turns"][-1]["finish_reason"], "stop")


if __name__ == "__main__":
    unittest.main()
