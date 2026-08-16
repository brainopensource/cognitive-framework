import unittest
from pathlib import Path


class CalculatorOracle(unittest.TestCase):
    def test_formula_repair(self) -> None:
        source = Path("src/calculator.py").read_text(encoding="utf-8")
        self.assertIn("(A + B) * B", source)


if __name__ == "__main__":
    unittest.main()
