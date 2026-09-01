import json
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("lam_schema", ROOT / "tools/002_LLM_API_MOCK/schema.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
validate_scenario = MODULE.validate_scenario


class TestLamSchemaCorpus(unittest.TestCase):
    def test_every_checked_in_scenario_validates(self) -> None:
        root = Path(__file__).parents[2] / "tools/002_LLM_API_MOCK/scenarios"
        scenarios = sorted(root.glob("*.json"))
        self.assertTrue(scenarios)
        for path in scenarios:
            with self.subTest(path=path.name):
                validate_scenario(json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
