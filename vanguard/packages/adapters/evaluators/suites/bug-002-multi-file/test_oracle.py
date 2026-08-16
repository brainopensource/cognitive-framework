import unittest
from pathlib import Path


class ImportCycleOracle(unittest.TestCase):
    def test_import_cycle_repair(self) -> None:
        db = Path("db.py").read_text(encoding="utf-8")
        models = Path("models.py").read_text(encoding="utf-8")
        self.assertNotIn("from models import User", db)
        self.assertIn("class User", models)


if __name__ == "__main__":
    unittest.main()
