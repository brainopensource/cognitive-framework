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

import re
from pathlib import Path
from typing import Sequence

from ...ports.event_store import Result
from ...ports.index import Symbol

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


class InMemoryRepoIndex:
    """The fake. Fed directly, so compose tests need no filesystem."""

    def __init__(self, contents: dict[str, str] | None = None) -> None:
        self._contents = dict(contents or {})
        self._symbols: list[Symbol] = []
        self._scan()

    def _scan(self) -> None:
        self._symbols = []
        for path, text in sorted(self._contents.items()):
            self._symbols.extend(_symbols_in(path, text.splitlines()))

    def index(self, root: str) -> Result[int]:
        self._scan()
        return Result.success(len(self._contents))

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        return Result.success(
            tuple(sorted(p for p in self._contents if p.startswith(prefix))))

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        return Result.success(_filtered(self._symbols, name, path))


class FileRepoIndex:
    """The real one. Walks a workspace and records definitions by regex."""

    def __init__(self, max_bytes: int = 1_048_576) -> None:
        self.max_bytes = max_bytes
        self._root: Path | None = None
        self._files: tuple[str, ...] = ()
        self._symbols: tuple[Symbol, ...] = ()

    def index(self, root: str) -> Result[int]:
        base = Path(root)
        if not base.is_dir():
            return Result.fail("not_found", f"not a directory: {root}")
        files: list[str] = []
        symbols: list[Symbol] = []
        for path in sorted(base.rglob("*")):
            if not path.is_file() or set(path.parts) & _IGNORED:
                continue
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
        self._root = base
        self._files = tuple(files)
        self._symbols = tuple(symbols)
        return Result.success(len(files))

    def files(self, *, prefix: str = "") -> Result[Sequence[str]]:
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        return Result.success(tuple(p for p in self._files if p.startswith(prefix)))

    def symbols(self, *, name: str = "", path: str = "") -> Result[Sequence[Symbol]]:
        if self._root is None:
            return Result.fail("invalid_request", "index() has not been called")
        return Result.success(_filtered(self._symbols, name, path))


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
