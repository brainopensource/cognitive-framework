"""Tests for context and repository middleware in code-default pack."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.context.duplicate_observation_filter import filter_redundant_observation
from middleware.context.history_compactor import compact_action_history
from middleware.context.stable_prefix_builder import build_stable_prefix
from middleware.repository.context_ranker import rank_repository_context, RankingWeights
from middleware.repository.import_graph import extract_file_imports
from middleware.repository.multi_file_completeness import check_multi_file_completeness
from middleware.repository.symbol_indexer import index_python_source


class ContextMiddlewareTests(unittest.TestCase):
    def test_duplicate_observation_filter_detects_unmodified_content(self) -> None:
        observed = {}
        # First observation: not duplicate
        is_dup, digest1, text1 = filter_redundant_observation("foo.py", "def foo(): pass\n", observed)
        self.assertFalse(is_dup)
        self.assertEqual(text1, "def foo(): pass\n")
        observed["foo.py"] = digest1

        # Second observation with same content: duplicate
        is_dup2, digest2, text2 = filter_redundant_observation("foo.py", "def foo(): pass\n", observed)
        self.assertTrue(is_dup2)
        self.assertEqual(digest1, digest2)
        self.assertIn("unchanged", text2)

        # Third observation with changed content: not duplicate
        is_dup3, digest3, text3 = filter_redundant_observation("foo.py", "def foo(): return 1\n", observed)
        self.assertFalse(is_dup3)
        self.assertNotEqual(digest1, digest3)
        self.assertEqual(text3, "def foo(): return 1\n")

    def test_history_compactor_preserves_recent_receipts(self) -> None:
        turns = [
            {"role": "user", "action": "fs.read", "proposal": "read file a"},
            {"role": "user", "action": "fs.read", "proposal": "read file b"},
            {"role": "user", "action": "fs.patch", "proposal": "modify file b"},
            {"role": "user", "action": "proc.exec", "proposal": "run tests"},
            {"role": "user", "action": "proc.exec", "proposal": "verify fix"},
        ]
        compacted = compact_action_history(turns, keep_last_n_receipts=2)
        self.assertEqual(len(compacted), 5)
        # First 3 turns should be summarized
        self.assertIn("[Turn 1 summary]", compacted[0]["content"])
        self.assertIn("[Turn 2 summary]", compacted[1]["content"])
        self.assertIn("[Turn 3 summary]", compacted[2]["content"])
        # Last 2 turns should be exact copies
        self.assertEqual(compacted[3]["proposal"], "run tests")
        self.assertEqual(compacted[4]["proposal"], "verify fix")

    def test_stable_prefix_builder_combines_system_and_instructions(self) -> None:
        prefix = build_stable_prefix(
            constitutional_rules=["Do not edit generated files.", "Verify before completion."],
            role_contract="You are an expert software engineer.",
            tool_schemas_summary="fs.read, fs.patch, proc.exec",
        )
        self.assertIn("# Core Constraints", prefix)
        self.assertIn("Do not edit generated files.", prefix)
        self.assertIn("# Role Contract", prefix)
        self.assertIn("You are an expert software engineer.", prefix)
        self.assertIn("# Available Operations", prefix)
        self.assertIn("fs.read, fs.patch, proc.exec", prefix)


class RepositoryMiddlewareTests(unittest.TestCase):
    def test_rank_repository_context_multi_signal(self) -> None:
        files = {
            "src/cache/lru.py": "class LRUCache:\n    def get(self, key):\n        pass\n",
            "src/cache/entry.py": "class CacheEntry:\n    def is_expired(self):\n        pass\n",
            "src/utils/math.py": "def add(a, b):\n    return a + b\n",
            "tests/test_cache.py": "def test_lru_cache():\n    pass\n",
        }
        ranked = rank_repository_context(["LRUCache", "get"], files)
        self.assertGreater(len(ranked), 0)
        self.assertEqual(ranked[0].file_path, "src/cache/lru.py")
        self.assertIn("lrucache", ranked[0].matched_symbols)
        self.assertIn("get", ranked[0].matched_symbols)

    def test_symbol_indexer_extracts_classes_and_functions(self) -> None:
        code = """
class MyService:
    def process(self):
        pass

def helper_fn(x, y):
    return x * y
"""
        symbols = index_python_source("service.py", code)
        self.assertGreaterEqual(len(symbols), 2)
        names = {s.name for s in symbols}
        self.assertIn("MyService", names)
        self.assertIn("helper_fn", names)

    def test_import_graph_detects_imports(self) -> None:
        code = "from service import MyService\nimport utils\n"
        deps = extract_file_imports("app.py", code)
        self.assertEqual(deps.file_path, "app.py")
        self.assertIn("utils", deps.imports)
        self.assertIn(("service", "MyService"), deps.from_imports)

    def test_multi_file_completeness_assessment(self) -> None:
        implicated = ["app.py", "service.py", "utils.py"]
        inspected = ["app.py", "service.py"]
        modified = ["app.py"]

        # Missing utils.py -> incomplete
        report = check_multi_file_completeness(implicated, inspected, modified)
        self.assertFalse(report.is_complete)
        self.assertIn("utils.py", report.missing_inspections)

        # All inspected -> complete
        report_complete = check_multi_file_completeness(implicated, ["app.py", "service.py", "utils.py"], modified)
        self.assertTrue(report_complete.is_complete)
        self.assertEqual(len(report_complete.missing_inspections), 0)


if __name__ == "__main__":
    unittest.main()
