---
id: report.electroweak.3_body.solution_b.full_code_3manifestforge_wave-7
class: report
authority: non-canonical
canonical_for: []
status: proposal
owner: repository-governance
version: 0.9.2a2
last_verified: 2026-08-31
purpose: Non-canonical candidate input to the Coding Max architecture convergence review.
audience:
  - contributor
  - architect
---

# full_code_3manifestforge — Wave 7
## Repository Intelligence: Providers Determinísticos (código integral)

Os relatórios das Waves 1–4 mostraram estes arquivos com trechos elididos
(`...`). Aqui está o código completo, sem omissão.

**Contrato invariante:** todo método é *total*. Providers degradam para
resultado vazio, nunca levantam exceção. É isso — e só isso — que mantém LDA
genuinamente opcional (§9) e impede que um índice quebrado termine um run.

---

## Cap. 7.1 — `vanguard/packages/apps/coding_max/intelligence/native.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **440 linhas**

O piso da escada — o provider sempre disponível, para que o harness nunca dependa de um índice existir. Símbolos via AST, não regex: regex não distingue `def parse(` de `# def parse(`, e uma definição errada manda o worker ao arquivo errado — a classe `WRONG_FILE` que esta camada existe para evitar.

```python
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
```

---

## Cap. 7.2 — `vanguard/packages/apps/coding_max/intelligence/composite.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **387 linhas**

O objeto que o resto do harness usa. Implementa §9 literalmente, generalizado para uma escada de providers com isolamento, cache e merge por ranking.

```python
"""Provider composition, caching, and failure isolation (`spec §8`, `§9`, `§13`).

This is the object the rest of the harness talks to. It implements the
`spec §9` requirement literally:

    if lda.available(): use_enriched_intelligence()
    else:               use_native_repository_tools()

but generalises it to a ladder, because the same rule applies to git and AST.
Two behaviours matter more than the merge itself:

* **Isolation.** A provider that raises is disabled for the rest of the run
  and recorded, never retried in a loop. One broken index cannot degrade into
  a per-call exception storm.
* **Union, not override.** Results merge with deterministic providers ranked
  above semantic ones. A semantic provider can *add* a candidate the
  deterministic ones missed; it can never *displace* one they found.

The cache key follows `spec §13`: repo identity, HEAD, provider version, and
the query. HEAD changing invalidates derived knowledge, which is what makes it
safe to cache a repository map across turns while the worker is editing.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence, TypeVar

from ....domain.canonicalisation.digest import digest_of
from .gitprov import GitProvider
from .lda import LDAAdapter, LDAConfig
from .native import NativeRepoSearch
from .protocol import (
    DependencyResult,
    Provenance,
    RepoScope,
    RepoSummary,
    RepositoryIntelligence,
    SearchHit,
    SearchQuery,
    SearchResult,
    SymbolRef,
    SymbolResult,
    TestMapping,
)

__all__ = ["CompositeIntelligence", "IntelligenceCache", "ProviderHealth"]

T = TypeVar("T")

#: Deterministic providers outrank semantic ones when merging.
_RANK: Mapping[str, int] = {"native": 3, "git": 2, "ast": 3, "lda": 1}


@dataclass
class ProviderHealth:
    """Per-provider liveness. Disabled providers are never retried."""

    name: str
    enabled: bool = True
    calls: int = 0
    failures: int = 0
    disabled_reason: str = ""
    total_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.name, "enabled": self.enabled, "calls": self.calls,
            "failures": self.failures, "disabledReason": self.disabled_reason,
            "totalMs": self.total_ms,
        }


@dataclass
class IntelligenceCache:
    """`spec §13`. Keyed on repo identity + HEAD + provider version + query."""

    repo_identity: str
    head: str = ""
    max_entries: int = 512
    _entries: dict[str, Any] = field(default_factory=dict, repr=False)
    hits: int = 0
    misses: int = 0

    def key(self, operation: str, payload: Mapping[str, Any], provider_version: str) -> str:
        return digest_of({
            "repo": self.repo_identity, "head": self.head,
            "op": operation, "payload": dict(payload), "pv": provider_version,
        })

    def get(self, key: str) -> Any | None:
        if key in self._entries:
            self.hits += 1
            return self._entries[key]
        self.misses += 1
        return None

    def put(self, key: str, value: Any) -> None:
        if len(self._entries) >= self.max_entries:
            # FIFO eviction. An LRU would need per-entry bookkeeping for a
            # cache that lives one run; the entries are uniform in cost.
            self._entries.pop(next(iter(self._entries)), None)
        self._entries[key] = value

    def invalidate_head(self, new_head: str) -> int:
        """`spec §13`: invalidate only what the new HEAD affects.

        Everything derived is keyed by HEAD, so a HEAD change makes prior
        entries unreachable rather than wrong. Dropping them keeps the map
        bounded without a scan.
        """
        if new_head == self.head:
            return 0
        dropped = len(self._entries)
        self._entries.clear()
        self.head = new_head
        return dropped

    def stats(self) -> dict[str, Any]:
        total = self.hits + self.misses
        return {
            "entries": len(self._entries), "hits": self.hits, "misses": self.misses,
            "hitRate": round(self.hits / total, 4) if total else 0.0,
        }


class CompositeIntelligence:
    """The `RepositoryIntelligence` the harness actually uses."""

    name = "composite"

    def __init__(
        self,
        root: Path | str,
        *,
        providers: Sequence[RepositoryIntelligence] | None = None,
        use_lda: bool = True,
        cache: IntelligenceCache | None = None,
    ) -> None:
        self._root = Path(root).resolve()
        self._native = NativeRepoSearch(self._root)
        self._git = GitProvider(self._root)

        ladder: list[Any] = list(providers) if providers is not None else [
            self._native, self._git,
        ]
        if providers is None and use_lda:
            adapter = LDAAdapter(LDAConfig.for_workspace(self._root))
            if adapter.available():
                ladder.append(adapter)

        self._providers: tuple[Any, ...] = tuple(ladder)
        self._health = {p.name: ProviderHealth(name=p.name) for p in self._providers}
        head = self._git.head() if self._git.available() else ""
        self._cache = cache or IntelligenceCache(
            repo_identity=digest_of({"root": str(self._root)}), head=head,
        )

    # -- introspection ---------------------------------------------------

    @property
    def root(self) -> Path:
        return self._root

    @property
    def git(self) -> GitProvider:
        return self._git

    @property
    def cache(self) -> IntelligenceCache:
        return self._cache

    def provider_names(self) -> tuple[str, ...]:
        return tuple(p.name for p in self._providers if self._health[p.name].enabled)

    def lda_enabled(self) -> bool:
        return "lda" in self.provider_names()

    def health(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(h.to_dict() for h in self._health.values())

    def refresh_head(self) -> int:
        """Re-read HEAD and drop stale derived entries. Called after commits."""
        return self._cache.invalidate_head(
            self._git.head() if self._git.available() else "")

    # -- fan-out ---------------------------------------------------------

    def _each(
        self,
        operation: str,
        payload: Mapping[str, Any],
        call: Callable[[Any], T],
        *,
        empty: T,
    ) -> list[tuple[str, T]]:
        """Call every live provider, isolating failures and timing each."""
        collected: list[tuple[str, T]] = []
        for provider in self._providers:
            health = self._health[provider.name]
            if not health.enabled:
                continue
            started = time.monotonic()
            try:
                if not provider.available():
                    continue
                result = call(provider)
            except Exception as exc:  # noqa: BLE001 - isolation is the point
                health.failures += 1
                health.enabled = False
                health.disabled_reason = f"{type(exc).__name__}: {exc}"[:200]
                continue
            finally:
                health.calls += 1
                health.total_ms += int((time.monotonic() - started) * 1000)
            collected.append((provider.name, result))
        return collected

    # -- RepositoryIntelligence surface ----------------------------------

    def available(self) -> bool:
        return self._native.available()

    def search(self, query: SearchQuery) -> SearchResult:
        key = self._cache.key("search", {"q": query.cache_key()}, self._version())
        cached = self._cache.get(key)
        if cached is not None:
            return _mark_cached(cached)

        results = self._each("search", {}, lambda p: p.search(query), empty=SearchResult())
        merged = self._merge_hits(results, limit=query.max_results)
        outcome = SearchResult(
            hits=merged,
            truncated=any(r.truncated for _, r in results),
            provenance=self._provenance("search", results),
        )
        self._cache.put(key, outcome)
        return outcome

    def symbol(self, name: str) -> SymbolResult:
        key = self._cache.key("symbol", {"name": name}, self._version())
        cached = self._cache.get(key)
        if cached is not None:
            return _mark_cached(cached)

        results = self._each("symbol", {}, lambda p: p.symbol(name), empty=SymbolResult())
        definitions: dict[tuple[str, int], SymbolRef] = {}
        references: list[tuple[float, SearchHit]] = []
        for provider_name, result in results:
            rank = _RANK.get(provider_name.split(":")[0], 1)
            for definition in result.definitions:
                definitions.setdefault((definition.path, definition.line), definition)
            for reference in result.references:
                references.append((rank + reference.score, reference))

        references.sort(key=lambda item: -item[0])
        outcome = SymbolResult(
            definitions=tuple(definitions.values()),
            references=tuple(hit for _, hit in references[:40]),
            provenance=self._provenance("symbol", results),
        )
        self._cache.put(key, outcome)
        return outcome

    def dependencies(self, target: str) -> DependencyResult:
        key = self._cache.key("dependencies", {"target": target}, self._version())
        cached = self._cache.get(key)
        if cached is not None:
            return _mark_cached(cached)

        results = self._each("deps", {}, lambda p: p.dependencies(target),
                             empty=DependencyResult(target=target))
        imports: list[str] = []
        imported_by: list[str] = []
        external: list[str] = []
        for _, result in results:
            imports.extend(result.imports)
            imported_by.extend(result.imported_by)
            external.extend(result.external)
        outcome = DependencyResult(
            target=target,
            imports=tuple(dict.fromkeys(imports)),
            imported_by=tuple(dict.fromkeys(imported_by)),
            external=tuple(dict.fromkeys(external)),
            provenance=self._provenance("dependencies", results),
        )
        self._cache.put(key, outcome)
        return outcome

    def tests_for(self, target: str) -> TestMapping:
        key = self._cache.key("tests", {"target": target}, self._version())
        cached = self._cache.get(key)
        if cached is not None:
            return _mark_cached(cached)

        results = self._each("tests", {}, lambda p: p.tests_for(target),
                             empty=TestMapping(target=target))
        direct: list[str] = []
        sibling: list[str] = []
        hint = ""
        for _, result in results:
            direct.extend(result.direct)
            sibling.extend(result.sibling)
            hint = hint or result.command_hint
        direct_unique = tuple(dict.fromkeys(direct))
        outcome = TestMapping(
            target=target,
            direct=direct_unique,
            sibling=tuple(p for p in dict.fromkeys(sibling) if p not in direct_unique),
            command_hint=hint,
            provenance=self._provenance("tests_for", results),
        )
        self._cache.put(key, outcome)
        return outcome

    def summarize(self, scope: RepoScope) -> RepoSummary:
        key = self._cache.key(
            "summary", {"paths": list(scope.paths), "depth": scope.depth},
            self._version(),
        )
        cached = self._cache.get(key)
        if cached is not None:
            return _mark_cached(cached)

        results = self._each("summarize", {}, lambda p: p.summarize(scope),
                             empty=RepoSummary())
        best = max(
            (r for _, r in results),
            key=lambda r: (r.file_count, len(r.modules)),
            default=RepoSummary(),
        )
        self._cache.put(key, best)
        return best

    # -- merge helpers ---------------------------------------------------

    @staticmethod
    def _merge_hits(
        results: Sequence[tuple[str, SearchResult]], *, limit: int
    ) -> tuple[SearchHit, ...]:
        """Rank by provider class, then by the provider's own score.

        Deduplicated on (path, line): the same location found by two providers
        is one piece of evidence, and counting it twice would let a redundant
        provider inflate a file's apparent relevance.
        """
        scored: dict[tuple[str, int], tuple[float, SearchHit]] = {}
        for provider_name, result in results:
            rank = _RANK.get(provider_name.split(":")[0], 1)
            for hit in result.hits:
                identity = (hit.path, hit.line)
                value = rank + hit.score
                if identity not in scored or scored[identity][0] < value:
                    scored[identity] = (value, hit)
        ordered = sorted(scored.values(), key=lambda item: -item[0])
        return tuple(hit for _, hit in ordered[:limit])

    def _provenance(
        self, operation: str, results: Sequence[tuple[str, Any]]
    ) -> Provenance:
        names = ",".join(sorted({name for name, _ in results})) or "none"
        confidences = [
            getattr(result.provenance, "confidence", 0.0) for _, result in results
        ]
        elapsed = sum(
            getattr(result.provenance, "elapsed_ms", 0) for _, result in results
        )
        return Provenance(
            provider=f"composite[{names}]",
            confidence=max(confidences) if confidences else 0.0,
            elapsed_ms=elapsed,
        )

    def _version(self) -> str:
        return digest_of({"providers": sorted(self.provider_names())})


def _mark_cached(result: T) -> T:
    """Restamp provenance so a cached answer is legible as one (`spec §13`)."""
    provenance = getattr(result, "provenance", None)
    if provenance is None:
        return result
    from dataclasses import replace

    return replace(result, provenance=replace(provenance, cached=True))
```

---

## Cap. 7.3 — Por que o fallback Python não é brinquedo

`NativeRepoSearch` usa ripgrep quando presente e um walk Python quando não.
Sem o fallback, o harness viraria **sistema diferente conforme o host**, e
braços pareados de benchmark deixariam de ser comparáveis — o resultado de um
run passaria a depender de qual máquina o executou.

Nesta máquina de validação ripgrep **não está instalado**. Todos os resultados
reportados nos relatórios anteriores vieram do caminho Python, e têm formato
idêntico ao que ripgrep produziria.

```
HITS: [('test/falsifiers/test_rf55_rf59_delegation_e2e.py', 155),
       ('vanguard/packages/runtime/session.py', 395)]  provider=native:python
```

---

## Cap. 7.4 — Contenção de path: defesa em profundidade

```python
    def _safe_path(self, candidate: str) -> Path:
        """Resolve inside the workspace or fall back to its root.

        Containment is enforced here as well as in the environment adapter.
        The adapter enforces it for *effects*; this enforces it for
        *observations*, so a crafted `path` argument cannot make the harness
        read and then summarise a file outside the workspace into a prompt.
        """
```

O `GitEnvironment` já contém efeitos. Mas uma **observação** que escapa do
workspace é igualmente perigosa por um caminho diferente: o conteúdo lido entra
no prompt, e a partir daí influencia todo comportamento subsequente. Duas
camadas, dois vetores.

---

## Cap. 7.5 — Merge: união, nunca sobreposição

```python
_RANK: Mapping[str, int] = {"native": 3, "git": 2, "ast": 3, "lda": 1}
```

Um provider semântico pode **adicionar** um candidato que os determinísticos
perderam. Nunca pode **deslocar** um que eles acharam. Ranquear um hit de
índice semântico no mesmo nível de um hit de ripgrep é como retrieval começa a
alucinar: o primeiro é uma *dica* sobre onde olhar, o segundo é um *fato* sobre
o que está escrito.

Dedup em `(path, line)`:

```python
                identity = (hit.path, hit.line)
                value = rank + hit.score
                if identity not in scored or scored[identity][0] < value:
                    scored[identity] = (value, hit)
```

O mesmo local achado por dois providers é **uma** evidência. Contá-lo duas
vezes deixaria um provider redundante inflar a relevância aparente de um arquivo.

---

## Cap. 7.6 — Isolamento: um provider quebrado não gera tempestade de exceções

```python
            except Exception as exc:  # noqa: BLE001 - isolation is the point
                health.failures += 1
                health.enabled = False
                health.disabled_reason = f"{type(exc).__name__}: {exc}"[:200]
                continue
```

Desabilitado **pelo resto do run**, não re-tentado em laço. Um índice corrompido
que levanta a cada chamada consumiria o budget inteiro em falhas idênticas.

---

## Cap. 7.7 — Cache §13: HEAD torna entradas inalcançáveis, não erradas

```python
    def invalidate_head(self, new_head: str) -> int:
        if new_head == self.head:
            return 0
        dropped = len(self._entries)
        self._entries.clear()
        self.head = new_head
        return dropped
```

Tudo derivado é chaveado por HEAD. Uma mudança de HEAD torna entradas
anteriores **inalcançáveis** em vez de erradas — descartá-las mantém o mapa
limitado sem varredura. É isso que torna seguro cachear um mapa de repositório
entre turnos enquanto o worker está editando.

`_mark_cached` reestampa a proveniência para que uma resposta cacheada seja
legível como tal:

```python
def _mark_cached(result: T) -> T:
    provenance = getattr(result, "provenance", None)
    if provenance is None:
        return result
    from dataclasses import replace
    return replace(result, provenance=replace(provenance, cached=True))
```

Sem isso, um downstream não teria como distinguir evidência fresca de evidência
de três turnos atrás — e a diferença importa quando o worker está editando os
mesmos arquivos.
