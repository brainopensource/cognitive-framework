"""Tests for Vanguard bridge tool translation."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

tools_dir = Path(__file__).resolve().parents[2] / "tools" / "002_LLM_API_MOCK"
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from vanguard_bridge import translate_lam_call_to_vanguard, translate_vanguard_call_to_lam


class TestVanguardBridge(unittest.TestCase):
    def test_vanguard_to_lam_translation(self) -> None:
        name, args = translate_vanguard_call_to_lam("fs.read", {"file": "mod.py"})
        self.assertEqual(name, "view_file")
        self.assertEqual(args["path"], "mod.py")

    def test_lam_to_vanguard_translation(self) -> None:
        name, args = translate_lam_call_to_vanguard("view_file", {"path": "mod.py"})
        self.assertEqual(name, "fs.read")
        self.assertEqual(args["file"], "mod.py")


if __name__ == "__main__":
    unittest.main()
