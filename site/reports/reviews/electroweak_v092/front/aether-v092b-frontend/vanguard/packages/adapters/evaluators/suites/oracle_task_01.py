"""Sealed test oracle for Dogfood Task 01 (Calculator off-by-one sum)."""

import unittest
from pathlib import Path

class TestCalculatorOracle(unittest.TestCase):
    def test_sum_addition(self) -> None:
        try:
            import calc
        except ImportError:
            import sys
            sys.path.insert(0, str(Path(".").resolve()))
            import calc

        self.assertEqual(calc.total([1, 2, 3]), 6)
        self.assertEqual(calc.total([]), 0)
        self.assertEqual(calc.total([10, -5]), 5)

if __name__ == "__main__":
    unittest.main()
