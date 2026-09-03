"""Tests for Core-Change Detector tool (S10-B-02)."""

from __future__ import annotations

import unittest
from pathlib import Path

from tools.linters.check_core_changes import count_core_changes


class TestCheckCoreChanges(unittest.TestCase):
    def test_count_core_changes_structure(self) -> None:
        """S10-B-02: Core change detector returns structured metric report."""
        repo_root = Path(__file__).resolve().parents[2]
        res = count_core_changes(repo_root=repo_root)
        self.assertIn("coreDirectories", res)
        self.assertIn("totalDeltaLoc", res)
        self.assertIn("c10ZeroAchieved", res)
        self.assertIsInstance(res["totalDeltaLoc"], int)


if __name__ == "__main__":
    unittest.main()
