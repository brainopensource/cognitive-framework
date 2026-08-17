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


if __name__ == "__main__":
    unittest.main()
