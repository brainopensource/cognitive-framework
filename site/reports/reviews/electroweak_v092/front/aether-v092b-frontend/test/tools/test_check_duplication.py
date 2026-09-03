"""Duplication detector (F-16) — Wave 2 enforce + planted fixture."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DuplicationGateTests(unittest.TestCase):
    def test_production_tree_has_no_second_algebra(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "linters" / "check_duplication.py"), "--enforce"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)

    def test_planted_fork_fails_closed(self) -> None:
        fixture = ROOT / "test" / "broken" / "fixtures" / "duplicate_algebra"
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "linters" / "check_duplication.py"),
             "--root", str(fixture), "--expect-fail"],
            cwd=ROOT,
            check=False,
        )
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
