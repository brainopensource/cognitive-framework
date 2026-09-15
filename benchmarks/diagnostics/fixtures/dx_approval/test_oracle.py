"""Exterior check for the T-137 synthetic write. Not a T-51 holdout oracle."""

from __future__ import annotations

import unittest
from pathlib import Path


class TestApprovedFlag(unittest.TestCase):
    def test_approved_module_flag(self) -> None:
        path = Path("approved.py")
        self.assertTrue(path.is_file(), "approved.py must exist")
        ns: dict[str, object] = {}
        exec(path.read_text(encoding="utf-8"), ns)
        self.assertIs(ns.get("APPROVED"), True)


if __name__ == "__main__":
    unittest.main()
