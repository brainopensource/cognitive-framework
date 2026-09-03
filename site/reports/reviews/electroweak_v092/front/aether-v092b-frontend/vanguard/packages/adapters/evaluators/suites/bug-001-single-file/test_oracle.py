"""Property oracle: formula behaviour, not a source substring."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


def _load_calculator():
    path = Path("src/calculator.py")
    spec = importlib.util.spec_from_file_location("calculator_under_test", path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return getattr(module, "calculate_value", None) or getattr(module, "calculate")


class CalculatorOracle(unittest.TestCase):
    def test_formula_repair(self) -> None:
        fn = _load_calculator()
        self.assertEqual(fn(2, 3), 15)
        self.assertEqual(fn(0, 4), 16)
        self.assertEqual(fn(1, 1), 2)
        # Extra numeric cases and edge conditions (S9-C-06)
        self.assertEqual(fn(-2, 3), 3)
        self.assertEqual(fn(10, 5), 75)
        self.assertEqual(fn(-5, -2), 14)
        self.assertEqual(fn(0, 0), 0)

    def test_metamorphic_invariant(self) -> None:
        """Metamorphic property: fn(A, B) must identically equal A*B + B^2."""
        fn = _load_calculator()
        for a in (-10, -1, 0, 1, 5, 12):
            for b in (-5, 0, 2, 7):
                expected = (a + b) * b
                self.assertEqual(fn(a, b), expected, f"Metamorphic invariant failed for A={a}, B={b}")


if __name__ == "__main__":
    unittest.main()
