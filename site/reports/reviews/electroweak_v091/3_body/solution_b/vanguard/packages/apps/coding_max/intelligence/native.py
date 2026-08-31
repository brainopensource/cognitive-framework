"""Native repository search: ripgrep when present, Python walk otherwise.

`spec §20` says to favour deterministic tools over model reasoning. This is
the floor of that ladder -- the provider that is always available, so the
harness never depends on an index existing.

The pure-Python fallback is not a toy. A run on a machine without ripgrep must
produce the same *shape* of result, or the harness would silently become a
different system depending on the host, and paired benchmark arms would stop
being comparable.
"""

from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Iterator, Sequence

from ..errors import RepositoryAccessError
from .protocol import (
    DependencyResult,
    Provenance,
    RepoScope,
    RepoSummary,
    SearchHit,
    SearchQuery,
    SearchResult,
    SymbolKind,
    SymbolRef,
    SymbolResult,
    TestMapping,
)

__all__ = ["NativeRepoSearch"]

#: Directories never worth walking. Skipping these is the difference between
#: a 200ms and a 40s search on a repo with a populated virtualenv.
_SKIP_DIRS = frozenset({
    ".git", ".hg", ".svn", "node_modules", "__pycache__", ".venv", "venv",
    ".tox", ".mypy_cache", ".pytest_cache", ".ruff_cache", "dist", "build",
    ".next", "target", ".gradle", "site-packages", ".generated", ".lda",
})

_CODE_SUFFIXES = frozenset({
    ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java",
    ".rb", ".c", ".cc", ".cpp", ".h", ".hpp", ".cs", ".kt", ".swift",
    ".scala", ".sh", ".sql", ".toml", ".cfg", ".ini", ".yaml", ".yml",
})

_LANG_FOR_SUFFIX = {
    ".py": "python", ".pyi": "python", ".ts": "typescript", ".tsx": "typescript",
    ".js": "javascript", ".jsx": "javascript", ".go": "go", ".rs": "rust",
    ".java": "java", ".rb": "ruby", ".c": "c", ".cc": "cpp", ".cpp": "cpp",
    ".h": "c", ".hpp": "cpp", ".cs": "csharp", ".kt": "kotlin",
    ".swift": "swift", ".scala": "scala", ".sh": "shell", ".sql": "sql",
}

_BUILD_MARKERS = (
    ("pyproject.toml", "python/pyproject"), ("setup.py", "python/setuptools"),
    ("package.json", "node/npm"), ("Cargo.toml", "rust/cargo"),
    ("go.mod", "go/modules"), ("pom.xml", "java/maven"),
    ("build.gradle", "java/gradle"), ("Makefile", "make"),
    ("justfile", "just"), ("Gemfile", "ruby/bundler"),
)

#: A file larger than this is almost certainly generated or vendored data.
_MAX_FILE_BYTES = 2_000_000


class NativeRepoSearch:
    """Filesystem-backed intelligence. Always available given a real path."""

    name = "native"

    def __init__(self, root: Path | str, *, timeout_s: float = 20.0) -> None:
        self._root = Path(root).resolve()
        if not self._root.is_dir():
            raise RepositoryAccessError(f"workspace {self._root} is not a directory")
        self._timeout = timeout_s
        self._rg = shutil.which("rg")
        self._file_cache: tuple[Path, ...] | None = None

    def available(self) -> bool:
        return self._root.is_dir()

    @property
    def root(self) -> Path:
        return self._root

    # -- search ----------------------------------------------------------

    def search(self, query: SearchQuery) -> SearchResult:
        started = time.monotonic()
        try:
            hits, truncated = (
                self._search_ripgrep(query) if self._rg
                else self._search_python(query)
            )
        except (OSError, subprocess.SubprocessError, re.error):
            # A malformed regex is the caller's problem to see as "no hits",
            # not a reason to end the run.
            hits, truncated = (), False
        elapsed = int((time.monotonic() - started) * 1000)
        return SearchResult(
            hits=hits,
            truncated=truncated,
            provenance=Provenance(
                provider=f"{self.name}:{'ripgrep' if self._rg else 'python'}",
                confidence=0.6, elapsed_ms=elapsed,
            ),
        )

    def _search_ripgrep(self, query: SearchQuery) -> tuple[tuple[SearchHit, ...], bool]:
        cmd = [
            self._rg or "rg", "--line-number", "--no-heading", "--color", "never",
            "--max-count", str(query.max_results),
            "-C", str(max(0, query.context_lines)),
        ]
        if not query.case_sensitive:
            cmd.append("--ignore-case")
        if not query.regex:
            cmd.append("--fixed-strings")
        if query.glob:
            cmd += ["--glob", query.glob]
        for skip in sorted(_SKIP_DIRS):
            cmd += ["--glob", f"!{skip}/**"]
        cmd += ["--", query.pattern, str(self._safe_path(query.path))]

        proc = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=self._timeout, cwd=str(self._root), check=False,
        )
        # rg exits 1 for "no matches", which is a valid empty answer.
        if proc.returncode not in (0, 1):
            return (), False
        return self._parse_rg(proc.stdout, query.max_results)

    def _parse_rg(self, stdout: str, limit: int) -> tuple[tuple[SearchHit, ...], bool]:
        hits: list[SearchHit] = []
        for raw in stdout.splitlines():
            # Context lines use `path-line-text`; matches use `path:line:text`.
            match = re.match(r"^(.+?)[:-](\d+)[:-](.*)$", raw)
            if not match:
                continue
            path, line, text = match.group(1), int(match.group(2)), match.group(3)
            if ":" not in raw[: raw.find(text) or len(raw)]:
                continue  # a context line, folded into the match below
            hits.append(SearchHit(
                path=self._relative(path), line=line, text=text[:500], score=1.0,
            ))
            if len(hits) >= limit:
                return tuple(hits), True
        return tuple(hits), False

    def _search_python(self, query: SearchQuery) -> tuple[tuple[SearchHit, ...], bool]:
        flags = 0 if query.case_sensitive else re.IGNORECASE
        pattern = (re.compile(query.pattern, flags) if query.regex
                   else re.compile(re.escape(query.pattern), flags))
        hits: list[SearchHit] = []
        for path in self._iter_files(self._safe_path(query.path), query.glob):
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except (OSError, ValueError):
                continue
            for index, line in enumerate(lines):
                if not pattern.search(line):
                    continue
                low = max(0, index - query.context_lines)
                high = min(len(lines), index + query.context_lines + 1)
                hits.append(SearchHit(
                    path=self._relative(path), line=index + 1, text=line[:500],
                    context_before=tuple(lines[low:index]),
                    context_after=tuple(lines[index + 1:high]),
                    score=1.0,
                ))
                if len(hits) >= query.max_results:
                    return tuple(hits), True
        return tuple(hits), False

    # -- symbols ---------------------------------------------------------

    def symbol(self, name: str) -> SymbolResult:
        """Definitions via Python AST; references via a word-boundary search.

        AST is used rather than a regex for definitions because a regex cannot
        distinguish `def parse(` from `# def parse(` or a string containing it,
        and a wrong definition sends the worker to the wrong file -- the
        `WRONG_FILE` failure class this whole layer exists to avoid.
        """
        started = time.monotonic()
        definitions: list[SymbolRef] = []
        for path in self._iter_files(self._root, "*.py"):
            definitions.extend(self._defs_in(path, name))
            if len(definitions) >= 40:
                break
        references = self.search(SearchQuery(
            pattern=rf"\b{re.escape(name)}\b", regex=True,
            case_sensitive=True, max_results=40, context_lines=1,
        )).hits
        return SymbolResult(
            definitions=tuple(definitions),
            references=references,
            provenance=Provenance(
                provider=f"{self.name}:ast", confidence=0.75,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            ),
        )

    def _defs_in(self, path: Path, name: str) -> list[SymbolRef]:
        tree = self._parse_python(path)
        if tree is None:
            return []
        found: list[SymbolRef] = []
        for node, parent in _walk_with_parent(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            if node.name != name:
                continue
            if isinstance(node, ast.ClassDef):
                kind = SymbolKind.CLASS
            elif isinstance(parent, ast.ClassDef):
                kind = SymbolKind.METHOD
            else:
                kind = SymbolKind.FUNCTION
            doc = ast.get_docstring(node) or ""
            found.append(SymbolRef(
                name=name, kind=kind, path=self._relative(path),
                line=node.lineno, signature=_signature(node),
                docstring_head=doc.strip().splitlines()[0][:200] if doc.strip() else "",
                parent=parent.name if isinstance(parent, ast.ClassDef) else None,
            ))
        return found

    # -- dependencies ----------------------------------------------------

    def dependencies(self, target: str) -> DependencyResult:
        started = time.monotonic()
        path = self._safe_path(target)
        imports: list[str] = []
        external: list[str] = []
        if path.is_file() and path.suffix == ".py":
            tree = self._parse_python(path)
            if tree is not None:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            (imports if alias.name.startswith(".")
                             else external).append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = ("." * (node.level or 0)) + (node.module or "")
                        (imports if node.level else external).append(module)

        module_name = Path(target).stem
        imported_by = tuple(dict.fromkeys(
            hit.path for hit in self.search(SearchQuery(
                pattern=rf"(from|import)\s+[\w.]*\b{re.escape(module_name)}\b",
                glob="*.py", max_results=60, context_lines=0,
            )).hits if hit.path != self._relative(path)
        ))
        return DependencyResult(
            target=target,
            imports=tuple(dict.fromkeys(imports)),
            imported_by=imported_by,
            external=tuple(dict.fromkeys(external)),
            provenance=Provenance(
                provider=f"{self.name}:imports", confidence=0.7,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            ),
        )

    # -- tests -----------------------------------------------------------

    def tests_for(self, target: str) -> TestMapping:
        started = time.monotonic()
        stem = Path(target).stem
        direct = tuple(dict.fromkeys(
            hit.path for hit in self.search(SearchQuery(
                pattern=rf"\b{re.escape(stem)}\b", glob="**/test_*.py",
                max_results=40, context_lines=0,
            )).hits
        ))
        sibling: list[str] = []
        for candidate in (f"test_{stem}.py", f"{stem}_test.py"):
            sibling.extend(
                self._relative(path) for path in self._iter_files(self._root, candidate)
            )
        sibling_only = tuple(p for p in dict.fromkeys(sibling) if p not in direct)
        chosen = direct or sibling_only
        return TestMapping(
            target=target, direct=direct, sibling=sibling_only,
            command_hint=f"pytest {' '.join(chosen[:6])}" if chosen else "pytest",
            provenance=Provenance(
                provider=f"{self.name}:tests", confidence=0.55,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            ),
        )

    # -- summary ---------------------------------------------------------

    def summarize(self, scope: RepoScope) -> RepoSummary:
        started = time.monotonic()
        languages: dict[str, int] = {}
        modules: dict[str, int] = {}
        test_roots: set[str] = set()
        entrypoints: list[str] = []
        count = 0

        for path in self._all_files():
            count += 1
            language = _LANG_FOR_SUFFIX.get(path.suffix)
            if language:
                languages[language] = languages.get(language, 0) + 1
            relative = self._relative(path)
            top = relative.split("/")[0] if "/" in relative else "."
            modules[top] = modules.get(top, 0) + 1
            parts = set(Path(relative).parts)
            if parts & {"tests", "test", "spec", "__tests__"}:
                test_roots.add(sorted(parts & {"tests", "test", "spec", "__tests__"})[0])
            if path.name in {"__main__.py", "main.py", "cli.py", "app.py", "index.ts"}:
                entrypoints.append(relative)

        build = next(
            (label for marker, label in _BUILD_MARKERS
             if (self._root / marker).exists()),
            "",
        )
        ranked_modules = tuple(
            {"path": name, "files": n}
            for name, n in sorted(modules.items(), key=lambda kv: -kv[1])
            [: scope.max_entries]
        )
        return RepoSummary(
            languages=tuple(sorted(languages, key=lambda k: -languages[k])),
            modules=ranked_modules,
            entrypoints=tuple(sorted(entrypoints)[:20]),
            test_roots=tuple(sorted(test_roots)),
            build_system=build,
            file_count=count,
            provenance=Provenance(
                provider=f"{self.name}:summary", confidence=0.8,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            ),
        )

    # -- internals -------------------------------------------------------

    def _safe_path(self, candidate: str) -> Path:
        """Resolve inside the workspace or fall back to its root.

        Containment is enforced here as well as in the environment adapter.
        The adapter enforces it for *effects*; this enforces it for
        *observations*, so a crafted `path` argument cannot make the harness
        read and then summarise a file outside the workspace into a prompt.
        """
        resolved = (self._root / candidate).resolve() if candidate not in ("", ".") \
            else self._root
        try:
            resolved.relative_to(self._root)
        except ValueError:
            return self._root
        return resolved if resolved.exists() else self._root

    def _relative(self, path: Path | str) -> str:
        try:
            return str(Path(path).resolve().relative_to(self._root))
        except (ValueError, OSError):
            return str(path)

    def _all_files(self) -> tuple[Path, ...]:
        if self._file_cache is None:
            self._file_cache = tuple(self._iter_files(self._root, None))
        return self._file_cache

    def _iter_files(self, base: Path, glob: str | None) -> Iterator[Path]:
        if base.is_file():
            yield base
            return
        matcher = _glob_matcher(glob)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames
                           if d not in _SKIP_DIRS and not d.startswith(".")]
            for filename in filenames:
                path = Path(dirpath) / filename
                if path.suffix not in _CODE_SUFFIXES and glob is None:
                    continue
                if matcher and not matcher(path.name, self._relative(path)):
                    continue
                try:
                    if path.stat().st_size > _MAX_FILE_BYTES:
                        continue
                except OSError:
                    continue
                yield path

    @staticmethod
    def _parse_python(path: Path) -> ast.Module | None:
        try:
            return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (OSError, SyntaxError, ValueError, RecursionError):
            return None


def _glob_matcher(glob: str | None):
    if not glob:
        return None
    import fnmatch

    def matches(name: str, relative: str) -> bool:
        return fnmatch.fnmatch(name, glob) or fnmatch.fnmatch(relative, glob)

    return matches


def _walk_with_parent(tree: ast.AST) -> Iterator[tuple[ast.AST, ast.AST | None]]:
    stack: list[tuple[ast.AST, ast.AST | None]] = [(tree, None)]
    while stack:
        node, parent = stack.pop()
        yield node, parent
        for child in ast.iter_child_nodes(node):
            stack.append((child, node))


def _signature(node: ast.AST) -> str:
    if isinstance(node, ast.ClassDef):
        bases = ", ".join(getattr(base, "id", "…") for base in node.bases)
        return f"class {node.name}({bases})" if bases else f"class {node.name}"
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = [arg.arg for arg in node.args.args]
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        return f"{prefix} {node.name}({', '.join(args)})"
    return ""
