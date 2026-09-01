"""Tests for budget gate."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from budget import allow_live_call, get_remaining_budget


class TestLamBudget(unittest.TestCase):
    def test_free_band_always_allowed(self) -> None:
        allow_live_call(0.0, "free")
        allow_live_call(-5.0, "free")

    def test_paid_band_requires_positive_budget(self) -> None:
        allow_live_call(1.0, "medium")
        with self.assertRaises(RuntimeError):
            allow_live_call(0.0, "medium")
        with self.assertRaises(RuntimeError):
            allow_live_call(-0.5, "high")


if __name__ == "__main__":
    unittest.main()
