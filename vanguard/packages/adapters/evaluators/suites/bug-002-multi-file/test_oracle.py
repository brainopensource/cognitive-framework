from pathlib import Path


def test_import_cycle_repair() -> None:
    db = Path("db.py").read_text(encoding="utf-8")
    models = Path("models.py").read_text(encoding="utf-8")
    assert "from models import User" not in db
    assert "class User" in models
