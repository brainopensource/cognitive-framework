"""Repository indexes: in-memory and a cheap file/symbol scan (`S10-A-03`).

Two implementations per `T10.2`. Both are observation sources and neither
proposes anything -- the index answers what is in the workspace and the episode
decides what that means. A component that chose what the agent should read next
would be a second policy (`A-05`).

The real one is deliberately cheap: a regex definition scan, no parser, no
language server. tree-sitter can replace the body later without the port
moving, which is the point of having the port now.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Mapping, Sequence

from ...ports.event_store import Result
from ...ports.index import DependencyEdge, RepositoryMap, Symbol, TestAssociation

__all__ = ["FileRepoIndex", "InMemoryRepoIndex"]

#: Definition forms this scan recognises. Adding a language is a row.
_DEFINITIONS: tuple[tuple[str, str, re.Pattern[str]], ...] = (
    (".py", "function", re.compile(r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)")),
    (".py", "class", re.compile(r"^\s*class\s+([A-Za-z_]\w*)")),
    (".ts", "function", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)")),
    (".ts", "class", re.compile(r"^\s*(?:export\s+)?class\s+([A-Za-z_]\w*)")),
    (".tsx", "function", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)")),
)

_IGNORED = {".git", "__pycache__", "node_modules", ".venv", "dist", "build"}


def _query_path(value: str) -> str:
    if value == "":
        return ""
    candidate = Path(value.replace("\\", "/"))
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"path query must be workspace-relative: {value!r}")
    return candidate.as_posix()


def _source_revision(files: Mapping[str, str]) -> str:
    return "sha256:" + hashlib.sha256(json.dumps(dict(sorted(files.items())), separators=(",", ":")).encode()).hexdigest()


def _bounded_map(files: Sequence[str], symbols: Sequence[Symbol],
                 dependencies: Sequence[DependencyEdge], tests: Sequence[TestAssociation],
                 adapter_id: str, revision: str, token_budget: int) -> RepositoryMap:
    capacity = token_budget * 4
    used = 0
    kept_files: list[str] = []
    for path in files:
        cost = len(path) + 1
        if used + cost > capacity:
            break
        kept_files.append(path)
        used += cost
    kept_symbols = tuple(symbols[:max(0, capacity - used) // 12])
    used += sum(len(item.name) + len(item.path) + 8 for item in kept_symbols)
    kept_edges = tuple(dependencies[:max(0, capacity - used) // 16])
    used += sum(len(item.source) + len(item.target) + 8 for item in kept_edges)
    kept_tests = tuple(tests[:max(0, capacity - used) // 16])
    truncated = len(kept_files) < len(files) or len(kept_symbols) < len(symbols) or len(kept_edges) < len(dependencies) or len(kept_tests) < len(tests)
    return RepositoryMap(tuple(kept_files), kept_symbols, kept_edges, kept_tests,
                         adapter_id, revision, truncated=truncated,
                         token_estimate=max(1, used // 4) if used else 0)


def _edges_and_tests(contents: Mapping[str, str]) -> tuple[list[DependencyEdge], list[TestAssociation]]:
    edges: list[DependencyEdge] = []
    tests: list[TestAssociation] = []
    module_paths = {path[:-3].replace("/", "."): path for path in contents if path.endswith(".py")}
    for path, text in sorted(contents.items()):
        if not path.endswith(".py"):
            continue
        try:
            tree = ast.parse(text)
        except (SyntaxError, ValueError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            else:
                continue
            for name in names:
                target = module_paths.get(name, name.replace(".", "/") + ".py")
                edges.append(DependencyEdge(path, target))
        if "/test" in f"/{path}" or path.startswith("test") or Path(path).name.startswith("test_"):
            for target in sorted(contents):
                if target == path or target.startswith("test"):
                    continue
                stem = Path(target).stem
                if stem in text or Path(target).name in text:
                    tests.append(TestAssociation(path, target))
    return sorted(set(edges), key=lambda item: (item.source, item.target, item.kind)), sorted(set(tests), key=lambda item: (item.test_path, item.source_path))


class InMemoryRepoIndex:
    """The fake. Fed directly, so compose tests need no filesystem."""

    def __init__(self, contents: dict[str, str] | None = None) -> None:
        self._contents = {}
        for path, text in (contents or {}).items():
            self._contents[_query_path(path)] = str(text)
        self._symbols: list[Symbol] = []
        self._dependencies: list[DependencyEdge] = []
        self._tests: list[TestAssociation] = []
        self._scan()

    def _scan(self) -> None:
        self._symbols = []
        for path, text in sorted(self._contents.items()):
            self._symbols.extend(_symbols_in(path, text.splitlines()))
        self._dependencies, self._tests = _edges_and_tests(self._contents)

    def index(self, root: str) -> Result[int]:
        self._scan()
        return Result.success(len(self._contents))

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        try:
            prefix = _query_path(prefix)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(tuple(sorted(p for p in self._contents if p.startswith(prefix))))

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        try:
            path = _query_path(path)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(_filtered(self._symbols, name, path))

    def dependencies(self, *, path: str = "") -> Result[Sequence[DependencyEdge]]:
        try:
            path = _query_path(path)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(tuple(edge for edge in self._dependencies if not path or edge.source.startswith(path)))

    def tests(self, *, path: str = "") -> Result[Sequence[TestAssociation]]:
        try:
            path = _query_path(path)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(tuple(item for item in self._tests if not path or item.source_path.startswith(path) or item.test_path.startswith(path)))

    def repo_map(self, *, token_budget: int = 4000) -> Result[RepositoryMap]:
        if token_budget < 0:
            return Result.fail("invalid_request", "token_budget must be non-negative")
        return Result.success(_bounded_map(tuple(sorted(self._contents)), self._symbols,
                                           self._dependencies, self._tests,
                                           "in-memory-repo-index/1", _source_revision(self._contents), token_budget))


class FileRepoIndex:
    """The real one. Walks a workspace and records definitions by regex."""

    def __init__(self, max_bytes: int = 1_048_576, *, max_files: int = 10_000,
                 max_symbols: int = 20_000, max_edges: int = 20_000,
                 max_tests: int = 20_000) -> None:
        if max_bytes <= 0 or any(value < 0 for value in (max_files, max_symbols, max_edges, max_tests)):
            raise ValueError("repository index limits must be positive/non-negative")
        self.max_bytes = max_bytes
        self.max_files, self.max_symbols = max_files, max_symbols
        self.max_edges, self.max_tests = max_edges, max_tests
        self._root: Path | None = None
        self._files: tuple[str, ...] = ()
        self._symbols: tuple[Symbol, ...] = ()
        self._dependencies: tuple[DependencyEdge, ...] = ()
        self._tests: tuple[TestAssociation, ...] = ()
        self._revision = ""

    def index(self, root: str) -> Result[int]:
        base = Path(root).resolve()
        if not base.is_dir():
            return Result.fail("not_found", f"not a directory: {root}")
        files: list[str] = []
        symbols: list[Symbol] = []
        for path in sorted(base.rglob("*")):
            if path.is_symlink():
                return Result.fail("invalid_request", f"symlink escape is not indexable: {path.relative_to(base)}")
            if not path.is_file() or set(path.parts) & _IGNORED:
                continue
            if len(files) >= self.max_files:
                break
            relative = path.relative_to(base).as_posix()
            files.append(relative)
            if path.suffix not in {suffix for suffix, _, _ in _DEFINITIONS}:
                continue
            try:
                if path.stat().st_size > self.max_bytes:
                    continue
                lines = path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                # An unreadable file is not indexed and not an error: a repo
                # containing one binary is still a repo worth indexing.
                continue
            symbols.extend(_symbols_in(relative, lines))
            if len(symbols) > self.max_symbols:
                symbols = symbols[:self.max_symbols]
        content_digests: dict[str, str] = {}
        for relative in files:
            try:
                content_digests[relative] = hashlib.sha256((base / relative).read_bytes()).hexdigest()
            except OSError:
                continue
        contents: dict[str, str] = {}
        for relative in files:
            if Path(relative).suffix == ".py":
                try:
                    contents[relative] = (base / relative).read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
        dependencies, tests = _edges_and_tests(contents)
        self._root = base
        self._files = tuple(sorted(files))
        self._symbols = tuple(symbols)
        self._dependencies = tuple(dependencies[:self.max_edges])
        self._tests = tuple(tests[:self.max_tests])
        self._revision = _source_revision(content_digests)
        return Result.success(len(files))

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        try:
            prefix = _query_path(prefix)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(tuple(p for p in self._files if p.startswith(prefix)))

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        try:
            path = _query_path(path)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(_filtered(self._symbols, name, path))

    def dependencies(self, *, path: str = "") -> Result[Sequence[DependencyEdge]]:
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        try:
            path = _query_path(path)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(tuple(edge for edge in self._dependencies if not path or edge.source.startswith(path)))

    def tests(self, *, path: str = "") -> Result[Sequence[TestAssociation]]:
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        try:
            path = _query_path(path)
        except ValueError as exc:
            return Result.fail("invalid_request", str(exc))
        return Result.success(tuple(item for item in self._tests if not path or item.source_path.startswith(path) or item.test_path.startswith(path)))

    def repo_map(self, *, token_budget: int = 4000) -> Result[RepositoryMap]:
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        if token_budget < 0:
            return Result.fail("invalid_request", "token_budget must be non-negative")
        return Result.success(_bounded_map(self._files, self._symbols, self._dependencies,
                                           self._tests, "file-repo-index/1", self._revision,
                                           token_budget))


def _symbols_in(path: str, lines: Sequence[str]) -> list[Symbol]:
    suffix = "." + path.rsplit(".", 1)[-1] if "." in path else ""
    found: list[Symbol] = []
    for number, line in enumerate(lines, start=1):
        for want_suffix, kind, pattern in _DEFINITIONS:
            if want_suffix != suffix:
                continue
            match = pattern.match(line)
            if match:
                found.append(Symbol(name=match.group(1), kind=kind,
                                    path=path, line=number))
    return found


def _filtered(symbols: Sequence[Symbol], name: str, path: str) -> tuple[Symbol, ...]:
    return tuple(s for s in symbols
                 if (not name or s.name == name) and (not path or s.path.startswith(path)))
