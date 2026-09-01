"""Tests for LAM scenario schema validation."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from schema import validate_scenario


class TestLamSchema(unittest.TestCase):
    def test_valid_scenario_passes(self) -> None:
        raw = {
            "id": "t1-calculator",
            "tier": 1,
            "workspace": {"mod.py": "def calc(): return 1"},
            "turns": [
                {
                    "tool_calls": [{"function": {"name": "view_file"}}],
                    "finish_reason": "tool_calls",
                },
                {
                    "tool_calls": [],
                    "finish_reason": "stop",
                },
            ],
        }
        validate_scenario(raw)

    def test_rejects_unknown_atom(self) -> None:
        raw = {
            "id": "t1-calculator",
            "tier": 1,
            "turns": [
                {
                    "tool_calls": [{"function": {"name": "rm_rf"}}],
                    "finish_reason": "tool_calls",
                },
                {"finish_reason": "stop"},
            ],
        }
        with self.assertRaises(ValueError):
            validate_scenario(raw)

    def test_rejects_invalid_id(self) -> None:
        raw = {"id": "invalid-id", "turns": [{"finish_reason": "stop"}]}
        with self.assertRaises(ValueError):
            validate_scenario(raw)


if __name__ == "__main__":
    unittest.main()
