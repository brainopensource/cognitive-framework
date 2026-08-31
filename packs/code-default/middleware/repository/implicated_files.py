"""Build bounded implicated-file sets from repository-index observations."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from vanguard.packages.ports.index import DependencyEdge, IndexPort, Symbol, TestAssociation


@dataclass(frozen=True, slots=True)
class ImplicatedFile:
    path: str
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ImplicatedFileSet:
    files: tuple[ImplicatedFile, ...]
    truncated: bool = False
    max_depth: int = 0

    @property
    def paths(self) -> tuple[str, ...]:
        return tuple(item.path for item in self.files)


class ImplicatedFileSetBuilder:
    """Expand task references through a bounded dependency/test closure."""

    _PATH = re.compile(r"(?<![\w./-])(?:[\w.-]+/)*[\w.-]+\.(?:py|ts|tsx|js|jsx|sql|toml|yaml|yml|json)")
    _SYMBOL = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")

    def build(
        self,
        task_text: str,
        index: IndexPort,
        *,
        max_depth: int = 1,
        max_files: int = 128,
        symbols: Sequence[Symbol] | None = None,
        dependencies: Sequence[DependencyEdge] | None = None,
        tests: Sequence[TestAssociation] | None = None,
    ) -> ImplicatedFileSet:
        if max_depth < 0 or max_files <= 0:
            raise ValueError("max_depth must be non-negative and max_files must be positive")
        indexed_files = tuple(self._value(index.files()))
        known = set(indexed_files)
        reasons: dict[str, set[str]] = {}

        def add(path: str, reason: str) -> None:
            if path in known:
                reasons.setdefault(path, set()).add(reason)

        for candidate in self._PATH.findall(task_text):
            matches = [path for path in indexed_files if path == candidate or path.endswith("/" + candidate)]
            for path in matches:
                add(path, "task_path")

        symbol_rows = tuple(symbols) if symbols is not None else tuple(self._value(index.symbols()))
        words = {word.lower() for word in self._SYMBOL.findall(task_text)}
        for symbol in symbol_rows:
            if symbol.name.lower() in words or symbol.name.rsplit(".", 1)[-1].lower() in words:
                add(symbol.path, f"symbol:{symbol.name}")

        dep_rows = tuple(dependencies) if dependencies is not None else tuple(self._value(index.dependencies()))
        test_rows = tuple(tests) if tests is not None else tuple(self._value(index.tests()))
        adjacency: dict[str, set[str]] = {}
        reverse: dict[str, set[str]] = {}
        for edge in dep_rows:
            adjacency.setdefault(edge.source, set()).add(edge.target)
            reverse.setdefault(edge.target, set()).add(edge.source)

        frontier = set(reasons)
        visited = set(frontier)
        for depth in range(max_depth + 1):
            discovered: set[str] = set()
            for path in tuple(frontier):
                for related in adjacency.get(path, ()):
                    if related in known and related not in visited:
                        add(related, f"dependency:depth_{depth + 1}")
                        discovered.add(related)
                for related in reverse.get(path, ()):
                    if related in known and related not in visited:
                        add(related, f"dependent:depth_{depth + 1}")
                        discovered.add(related)
            visited.update(discovered)
            frontier = discovered
            if not frontier:
                break

        implicated = set(reasons)
        for association in test_rows:
            if association.source_path in implicated or association.test_path in implicated:
                add(association.test_path, f"test_for:{association.source_path}")
                add(association.source_path, f"source_for_test:{association.test_path}")

        ordered = sorted(reasons.items(), key=lambda item: item[0])
        truncated = len(ordered) > max_files
        return ImplicatedFileSet(
            tuple(ImplicatedFile(path, tuple(sorted(values))) for path, values in ordered[:max_files]),
            truncated=truncated,
            max_depth=max_depth,
        )

    @staticmethod
    def _value(result: object) -> Sequence[object]:
        if not getattr(result, "ok", False):
            return ()
        value = getattr(result, "value", ())
        return value if value is not None else ()


def build_implicated_file_set(
    task_text: str, index: IndexPort, *, max_depth: int = 1, max_files: int = 128
) -> ImplicatedFileSet:
    """Functional entry point for pack composition."""
    return ImplicatedFileSetBuilder().build(task_text, index, max_depth=max_depth, max_files=max_files)
