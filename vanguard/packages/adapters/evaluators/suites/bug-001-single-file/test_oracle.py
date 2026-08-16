from pathlib import Path


def test_formula_repair() -> None:
    source = Path("src/calculator.py").read_text(encoding="utf-8")
    assert "(A + B) * B" in source
