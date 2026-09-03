import unittest
from pathlib import Path
import tempfile
import sys
import importlib

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FactGraphStorage = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.storage").FactGraphStorage
CodeASTProvider = importlib.import_module("tools.007_LLM_DOCS_ATLAS.providers.code_ast").CodeASTProvider
TestAssociationEngine = importlib.import_module("tools.007_LLM_DOCS_ATLAS.core.test_association").TestAssociationEngine


class TestCallGraphAndQueries(unittest.TestCase):
    def test_call_graph_extraction_and_query(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            db_path = repo_root / ".lda" / "index.db"
            storage = FactGraphStorage(db_path)

            # Create production file
            src_dir = repo_root / "vanguard" / "packages" / "agency"
            src_dir.mkdir(parents=True, exist_ok=True)
            prod_file = src_dir / "target.py"
            prod_file.write_text("""
class TargetGate:
    def evaluate(self, val: int) -> bool:
        return val > 0
""")

            # Create caller file
            test_dir = repo_root / "test" / "agency"
            test_dir.mkdir(parents=True, exist_ok=True)
            test_file = test_dir / "test_target.py"
            test_file.write_text("""
from vanguard.packages.agency.target import TargetGate

class TestTarget(unittest.TestCase):
    def test_eval(self):
        gate = TargetGate()
        res = gate.evaluate(5)
        self.assertTrue(res)
""")

            index_repository = importlib.import_module("tools.007_LLM_DOCS_ATLAS.atlas").index_repository
            index_res = index_repository(repo_root)

            self.assertEqual(index_res["status"], "SUCCESS")
            self.assertGreaterEqual(index_res["total_symbols"], 3)
            self.assertGreaterEqual(index_res["total_relations"], 1)

            # 1. Symbol ranking
            syms = storage.get_symbol("TargetGate")
            self.assertGreaterEqual(len(syms), 1)
            self.assertEqual(syms[0]["name"], "TargetGate")
            self.assertTrue(syms[0]["file_path"].startswith("vanguard/"))

            # 2. Callers query
            callers = storage.get_callers("TargetGate.evaluate")
            self.assertGreaterEqual(len(callers), 1, "Must find callers for TargetGate.evaluate")

            # 3. Test association
            engine = TestAssociationEngine(storage)
            assoc = engine.find_associated_tests(["vanguard/packages/agency/target.py"])
            self.assertIn("test/agency/test_target.py", assoc["associated_test_files"])
            self.assertTrue(any("test.agency.test_target" in cmd for cmd in assoc["suggested_commands"]))


if __name__ == "__main__":
    unittest.main()
