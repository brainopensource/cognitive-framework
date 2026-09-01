"""Sealed test oracle for Dogfood Task 02 (String dedupe preservation)."""

import unittest
from pathlib import Path

class TestStringDedupeOracle(unittest.TestCase):
    def test_dedupe_preserves_order(self) -> None:
        try:
            import dedupe
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(".").resolve()))
            import dedupe

        self.assertEqual(dedupe.unique_preserve(["a", "b", "a", "c", "b"]), ["a", "b", "c"])
        self.assertEqual(dedupe.unique_preserve([]), [])

if __name__ == "__main__":
    unittest.main()
