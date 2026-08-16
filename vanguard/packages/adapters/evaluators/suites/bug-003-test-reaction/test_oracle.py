from pathlib import Path


def test_repair_keeps_regression_test() -> None:
    source = Path("src/parser.py").read_text(encoding="utf-8")
    tests = Path("test_parser.py").read_text(encoding="utf-8")
    assert "return tokens" in source
    assert "regression" in tests.lower()
