"""Deterministic import dependency graph builder."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class FileDependencies:
    file_path: str
    imports: tuple[str, ...] = field(default_factory=tuple)
    from_imports: tuple[tuple[str, str], ...] = field(default_factory=tuple)  # (module, symbol)


def extract_file_imports(file_path: str, source_code: str) -> FileDependencies:
    """Extract all module imports from python source code."""
    imports: list[str] = []
    from_imports: list[tuple[str, str]] = []

    try:
        tree = ast.parse(source_code, filename=file_path)
    except SyntaxError:
        return FileDependencies(file_path=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                from_imports.append((mod, alias.name))

    return FileDependencies(
        file_path=file_path,
        imports=tuple(sorted(set(imports))),
        from_imports=tuple(sorted(set(from_imports))),
    )
