"""Tests for repository intelligence middleware (symbols, imports, ranking, completeness)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "packs" / "code-default"
if str(PACK) not in sys.path:
    sys.path.insert(0, str(PACK))

from middleware.repository.context_ranker import rank_repository_context
from middleware.repository.import_graph import extract_file_imports
from middleware.repository.multi_file_completeness import check_multi_file_completeness
from middleware.repository.symbol_indexer import index_python_source
from middleware.repository.task_classifier import classify_task
from middleware.repository.implicated_files import ImplicatedFileSetBuilder
from vanguard.packages.adapters.stores.repo_index import InMemoryRepoIndex


class TestRepositoryMiddleware(unittest.TestCase):
    def test_index_python_source(self) -> None:
        code = """
MY_CONSTANT = 42

class Calculator:
    def add(self, a, b):
        return a + b

def standalone_func():
    pass
"""
        symbols = index_python_source("src/calc.py", code)
        names = [s.name for s in symbols]
        self.assertIn("MY_CONSTANT", names)
        self.assertIn("Calculator", names)
        self.assertIn("Calculator.add", names)
        self.assertIn("standalone_func", names)

    def test_extract_imports(self) -> None:
        code = """
import os
import sys
from pathlib import Path
from math import sqrt, pi
"""
        deps = extract_file_imports("src/util.py", code)
        self.assertIn("os", deps.imports)
        self.assertIn("sys", deps.imports)
        self.assertIn(("pathlib", "Path"), deps.from_imports)
        self.assertIn(("math", "sqrt"), deps.from_imports)

    def test_rank_repository_context(self) -> None:
        files = {
            "src/math/calc.py": "def multiply(a, b): return a * b",
            "src/web/server.py": "class HttpServer: pass",
            "test/test_calc.py": "def test_multiply(): assert multiply(2, 3) == 6",
        }
        ranked = rank_repository_context(["multiply", "calc"], files)
        self.assertTrue(len(ranked) > 0)
        top = ranked[0]
        self.assertIn("calc", top.file_path)

    def test_check_multi_file_completeness(self) -> None:
        report = check_multi_file_completeness(
            implicated_files=["src/a.py", "src/b.py"],
            inspected_files=["src/a.py"],
            modified_files=["src/a.py"],
        )
        self.assertFalse(report.is_complete)
        self.assertIn("src/b.py", report.missing_inspections)

    def test_classify_task_prefers_specific_migration_signal(self) -> None:
        result = classify_task("Migrate the API and add backward compatibility for old clients")
        self.assertEqual(result.kind, "migration")
        self.assertIn("migrate", result.signals)
        self.assertFalse(result.ambiguous)

    def test_implicated_file_builder_closes_dependencies_and_tests(self) -> None:
        index = InMemoryRepoIndex({
            "pkg/api.py": "from pkg.service import Service\n",
            "pkg/service.py": "class Service: pass\n",
            "tests/test_api.py": "from pkg.api import api\n",
        })
        result = ImplicatedFileSetBuilder().build("Fix pkg/api.py", index, max_depth=1)
        self.assertEqual(result.paths, ("pkg/api.py", "pkg/service.py", "tests/test_api.py"))
        reasons = {item.path: item.reasons for item in result.files}
        self.assertIn("task_path", reasons["pkg/api.py"])
        self.assertIn("dependency:depth_1", reasons["pkg/service.py"])
        self.assertIn("test_for:pkg/api.py", reasons["tests/test_api.py"])


if __name__ == "__main__":
    unittest.main()
