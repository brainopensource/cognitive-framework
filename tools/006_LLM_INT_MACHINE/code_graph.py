"""In-memory AST Symbol Indexer, Call Graph, and PageRank Locator for 006_LLM_INT_MACHINE.

Enables instant structural code navigation, callers/definitions resolution, and skeleton generation.
"""

from __future__ import annotations
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Sequence


@dataclass
class SymbolNode:
    """Represents a discrete code symbol in the workspace."""
    name: str
    kind: str  # "function" | "class" | "method"
    file_path: str
    line_start: int
    line_end: int
    docstring: str = ""
    calls: set[str] = field(default_factory=set)


class ASTCodeGraph:
    """Workspace-level AST symbol extractor and PageRank graph indexer."""

    def __init__(self, workspace_root: Path):
        self.root = workspace_root
        self.symbols: dict[str, SymbolNode] = {}
        self.call_graph: dict[str, set[str]] = {}
        self.pagerank_scores: dict[str, float] = {}

    def index_workspace(self) -> None:
        """Parse all Python files in the workspace into the symbol graph."""
        self.symbols.clear()
        self.call_graph.clear()
        self.pagerank_scores.clear()

        for py_file in self.root.rglob("*.py"):
            if ".git" in py_file.parts or "__pycache__" in py_file.parts or ".pytest_cache" in py_file.parts:
                continue
            rel_path = py_file.relative_to(self.root).as_posix()
            try:
                content = py_file.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(content, filename=rel_path)
                self._traverse_ast(tree, rel_path)
            except Exception:
                continue

        self._compute_pagerank()

    def _traverse_ast(self, tree: ast.AST, rel_path: str) -> None:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                sym_id = f"{rel_path}:{node.name}"
                doc = ast.get_docstring(node) or ""
                sym_node = SymbolNode(
                    name=node.name,
                    kind="function",
                    file_path=rel_path,
                    line_start=node.lineno,
                    line_end=getattr(node, "end_lineno", node.lineno),
                    docstring=doc,
                )
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            sym_node.calls.add(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            sym_node.calls.add(child.func.attr)
                self.symbols[sym_id] = sym_node

            elif isinstance(node, ast.ClassDef):
                sym_id = f"{rel_path}:{node.name}"
                doc = ast.get_docstring(node) or ""
                self.symbols[sym_id] = SymbolNode(
                    name=node.name,
                    kind="class",
                    file_path=rel_path,
                    line_start=node.lineno,
                    line_end=getattr(node, "end_lineno", node.lineno),
                    docstring=doc,
                )

    def _compute_pagerank(self, d: float = 0.85, iters: int = 15) -> None:
        n = len(self.symbols)
        if n == 0:
            return
        scores = {k: 1.0 / n for k in self.symbols}
        for _ in range(iters):
            new_scores = {k: (1.0 - d) / n for k in self.symbols}
            for u_id, u_node in self.symbols.items():
                if u_node.calls:
                    contrib = (d * scores[u_id]) / len(u_node.calls)
                    for call_name in u_node.calls:
                        for target_id in self.symbols:
                            if target_id.endswith(f":{call_name}"):
                                new_scores[target_id] += contrib
            scores = new_scores
        self.pagerank_scores = scores

    def find_definitions(self, symbol_name: str) -> list[SymbolNode]:
        """Find all definitions matching symbol_name."""
        return [s for s in self.symbols.values() if s.name == symbol_name]

    def find_callers(self, symbol_name: str) -> list[str]:
        """Find all symbol IDs that call symbol_name."""
        callers = []
        for sym_id, sym_node in self.symbols.items():
            if symbol_name in sym_node.calls:
                callers.append(sym_id)
        return callers

    def generate_compact_skeleton(self) -> str:
        """Generate a compact structural outline of all classes and functions."""
        if not self.symbols:
            self.index_workspace()
        lines = ["[Codebase Structural Outline]"]
        by_file: dict[str, list[SymbolNode]] = {}
        for s in self.symbols.values():
            by_file.setdefault(s.file_path, []).append(s)

        for f_path, syms in sorted(by_file.items()):
            lines.append(f"File: {f_path}")
            for s in sorted(syms, key=lambda x: x.line_start):
                lines.append(f"  - {s.kind.upper()} {s.name} (Lines {s.line_start}-{s.line_end})")
        return "\n".join(lines)
