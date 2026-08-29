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


if __name__ == "__main__":
    unittest.main()
