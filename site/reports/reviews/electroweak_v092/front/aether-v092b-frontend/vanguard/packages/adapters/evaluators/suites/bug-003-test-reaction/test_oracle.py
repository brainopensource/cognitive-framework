import unittest
from pathlib import Path


class ParserOracle(unittest.TestCase):
    def test_repair_keeps_regression_test(self) -> None:
        source = Path("src/parser.py").read_text(encoding="utf-8")
        tests = Path("test_parser.py").read_text(encoding="utf-8")
        self.assertIn("return tokens", source)
        self.assertIn("regression", tests.lower())


if __name__ == "__main__":
    unittest.main()
