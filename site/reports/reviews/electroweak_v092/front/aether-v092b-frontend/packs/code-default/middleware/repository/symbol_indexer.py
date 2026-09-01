"""Deterministic AST-based symbol indexer for Python repositories."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class SymbolDefinition:
    name: str
    kind: str  # "class", "function", "method", "constant"
    file_path: str
    line_number: int
    end_line_number: int
    docstring: str | None = None


def index_python_source(file_path: str, source_code: str) -> tuple[SymbolDefinition, ...]:
    """Parse python source code into a sequence of symbol definitions."""
    symbols: list[SymbolDefinition] = []
    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError:
        return ()

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            symbols.append(
                SymbolDefinition(
                    name=node.name,
                    kind="class",
                    file_path=file_path,
                    line_number=node.lineno,
                    end_line_number=getattr(node, "end_lineno", node.lineno),
                    docstring=ast.get_docstring(node),
                )
            )
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    symbols.append(
                        SymbolDefinition(
                            name=f"{node.name}.{item.name}",
                            kind="method",
                            file_path=file_path,
                            line_number=item.lineno,
                            end_line_number=getattr(item, "end_lineno", item.lineno),
                            docstring=ast.get_docstring(item),
                        )
                    )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(
                SymbolDefinition(
                    name=node.name,
                    kind="function",
                    file_path=file_path,
                    line_number=node.lineno,
                    end_line_number=getattr(node, "end_lineno", node.lineno),
                    docstring=ast.get_docstring(node),
                )
            )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    symbols.append(
                        SymbolDefinition(
                            name=target.id,
                            kind="constant",
                            file_path=file_path,
                            line_number=node.lineno,
                            end_line_number=getattr(node, "end_lineno", node.lineno),
                        )
                    )

    return tuple(symbols)
