# full_code_3manifestforge — Wave 9
## Contrato de Intelligence, Provider Git e Adaptador LDA (código integral)

---

## Cap. 9.1 — `vanguard/packages/apps/coding_max/intelligence/protocol.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **262 linhas**

O contrato §8. Todo resultado carrega `Provenance` porque o compilador de contexto precisa saber se um hit veio de ripgrep, de um walk AST ou de um índice semântico antes de poder pesá-lo.

```python
"""The `RepositoryIntelligence` contract (`spec §8`).

Providers answer questions about a repository. They return *normalized*
results and, per `spec §8`, **must not dictate context policy** -- ranking a
result is a provider's business, deciding what enters the prompt is the
context compiler's. That separation is why every result carries `provenance`:
the compiler needs to know whether a hit came from ripgrep, an AST walk, or a
semantic index before it can weigh it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from ....domain.canonicalisation.digest import digest_of

__all__ = [
    "DependencyResult",
    "Provenance",
    "RepoScope",
    "RepoSummary",
    "RepositoryIntelligence",
    "SearchHit",
    "SearchQuery",
    "SearchResult",
    "SymbolKind",
    "SymbolRef",
    "SymbolResult",
    "TestMapping",
]


class SymbolKind(str, Enum):
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    MODULE = "module"
    VARIABLE = "variable"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Provenance:
    """Where a result came from, and how much it should be trusted.

    `confidence` is a provider self-report and is treated as a ranking hint
    only. Nothing in the harness may promote a high-confidence hit to a fact
    without independent evidence -- that is the `spec §58` anti-pattern
    "grounded = text contains file name" in another costume.
    """

    provider: str
    version: str = "1"
    confidence: float = 0.5
    cached: bool = False
    elapsed_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "version": self.version,
            "confidence": round(self.confidence, 4),
            "cached": self.cached,
            "elapsedMs": self.elapsed_ms,
        }


@dataclass(frozen=True, slots=True)
class SearchQuery:
    pattern: str
    path: str = "."
    glob: str | None = None
    regex: bool = True
    case_sensitive: bool = False
    max_results: int = 40
    context_lines: int = 2

    def cache_key(self) -> str:
        return digest_of({
            "pattern": self.pattern, "path": self.path, "glob": self.glob,
            "regex": self.regex, "caseSensitive": self.case_sensitive,
            "maxResults": self.max_results, "contextLines": self.context_lines,
        })


@dataclass(frozen=True, slots=True)
class SearchHit:
    path: str
    line: int
    text: str
    context_before: tuple[str, ...] = ()
    context_after: tuple[str, ...] = ()
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path, "line": self.line, "text": self.text,
            "contextBefore": list(self.context_before),
            "contextAfter": list(self.context_after),
            "score": round(self.score, 4),
        }


@dataclass(frozen=True, slots=True)
class SearchResult:
    hits: tuple[SearchHit, ...] = ()
    truncated: bool = False
    provenance: Provenance = field(
        default_factory=lambda: Provenance(provider="unknown"))

    @property
    def paths(self) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for hit in self.hits:
            seen.setdefault(hit.path, None)
        return tuple(seen)

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": [hit.to_dict() for hit in self.hits],
            "truncated": self.truncated,
            "provenance": self.provenance.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class SymbolRef:
    name: str
    kind: SymbolKind
    path: str
    line: int
    signature: str = ""
    docstring_head: str = ""
    parent: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name, "kind": self.kind.value, "path": self.path,
            "line": self.line, "signature": self.signature,
            "docstringHead": self.docstring_head, "parent": self.parent,
        }


@dataclass(frozen=True, slots=True)
class SymbolResult:
    definitions: tuple[SymbolRef, ...] = ()
    references: tuple[SearchHit, ...] = ()
    provenance: Provenance = field(
        default_factory=lambda: Provenance(provider="unknown"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "definitions": [d.to_dict() for d in self.definitions],
            "references": [r.to_dict() for r in self.references],
            "provenance": self.provenance.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class DependencyResult:
    """Import-level edges around a target, in both directions."""

    target: str
    imports: tuple[str, ...] = ()
    imported_by: tuple[str, ...] = ()
    external: tuple[str, ...] = ()
    provenance: Provenance = field(
        default_factory=lambda: Provenance(provider="unknown"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target, "imports": list(self.imports),
            "importedBy": list(self.imported_by), "external": list(self.external),
            "provenance": self.provenance.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class TestMapping:
    """Which tests plausibly cover a target, and how that was decided.

    `direct` are tests that name the target; `sibling` are tests in the
    conventional mirror location. The two are kept apart because they justify
    different verification layers: `direct` drives V5 (targeted tests),
    `sibling` drives V6 (related tests).
    """

    target: str
    direct: tuple[str, ...] = ()
    sibling: tuple[str, ...] = ()
    command_hint: str = ""
    provenance: Provenance = field(
        default_factory=lambda: Provenance(provider="unknown"))

    @property
    def all_tests(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(self.direct + self.sibling))

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target, "direct": list(self.direct),
            "sibling": list(self.sibling), "commandHint": self.command_hint,
            "provenance": self.provenance.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class RepoScope:
    """What part of the repository a summary should cover."""

    paths: tuple[str, ...] = (".",)
    depth: int = 2
    max_entries: int = 200


@dataclass(frozen=True, slots=True)
class RepoSummary:
    languages: tuple[str, ...] = ()
    modules: tuple[Mapping[str, Any], ...] = ()
    entrypoints: tuple[str, ...] = ()
    test_roots: tuple[str, ...] = ()
    build_system: str = ""
    file_count: int = 0
    provenance: Provenance = field(
        default_factory=lambda: Provenance(provider="unknown"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "languages": list(self.languages),
            "modules": [dict(m) for m in self.modules],
            "entrypoints": list(self.entrypoints),
            "testRoots": list(self.test_roots),
            "buildSystem": self.build_system,
            "fileCount": self.file_count,
            "provenance": self.provenance.to_dict(),
        }


@runtime_checkable
class RepositoryIntelligence(Protocol):
    """`spec §8`. Every method is total: providers degrade, they do not raise.

    A provider that cannot answer returns an empty result whose provenance
    names it. Raising would let one weak provider end a run, which is exactly
    the coupling `spec §9` forbids for LDA.
    """

    name: str

    def available(self) -> bool: ...

    def search(self, query: SearchQuery) -> SearchResult: ...

    def symbol(self, name: str) -> SymbolResult: ...

    def dependencies(self, target: str) -> DependencyResult: ...

    def tests_for(self, target: str) -> TestMapping: ...

    def summarize(self, scope: RepoScope) -> RepoSummary: ...
```

---

## Cap. 9.2 — `vanguard/packages/apps/coding_max/intelligence/gitprov.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **199 linhas**

Git read-only. Churn, co-mudança e working-tree como priors de localização.

```python
"""Git-backed repository intelligence (`spec §8`).

Git answers a question no static analysis can: *what has actually been
changing*. Recency and churn are strong localisation priors -- a bug reported
today is far more likely to live in a file touched this month than in one
untouched for three years -- and they cost one subprocess call.

This provider is deliberately read-only. Effects on the repository go through
the existing `GitEnvironment` adapter under kernel authorisation
(`spec §40`); nothing here may write.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Sequence

from .protocol import (
    DependencyResult,
    Provenance,
    RepoScope,
    RepoSummary,
    SearchHit,
    SearchQuery,
    SearchResult,
    SymbolResult,
    TestMapping,
)

__all__ = ["GitProvider"]


class GitProvider:
    """Read-only git queries. Degrades to empty results outside a repo."""

    name = "git"

    def __init__(self, root: Path | str, *, timeout_s: float = 15.0) -> None:
        self._root = Path(root).resolve()
        self._timeout = timeout_s
        self._available: bool | None = None

    def available(self) -> bool:
        if self._available is None:
            result = self._git("rev-parse", "--is-inside-work-tree")
            self._available = result.strip() == "true"
        return self._available

    # -- git-specific surface used by the repo map and context scorer ----

    def head(self) -> str:
        return self._git("rev-parse", "HEAD").strip()

    def branch(self) -> str:
        return self._git("rev-parse", "--abbrev-ref", "HEAD").strip()

    def dirty(self) -> bool:
        return bool(self._git("status", "--porcelain").strip())

    def diff(self, *, staged: bool = False, paths: Sequence[str] = ()) -> str:
        args = ["diff", "--unified=3"]
        if staged:
            args.append("--cached")
        if paths:
            args += ["--", *paths]
        return self._git(*args)

    def changed_files(self) -> tuple[str, ...]:
        """Working-tree changes. This is the harness's own edit footprint."""
        lines = self._git("status", "--porcelain").splitlines()
        return tuple(line[3:].strip() for line in lines if len(line) > 3)

    def recent_files(self, limit: int = 60, since: str = "3.months") -> tuple[str, ...]:
        raw = self._git("log", f"--since={since}", "--name-only",
                        "--pretty=format:", "-n", "400")
        counts: dict[str, int] = {}
        for line in raw.splitlines():
            name = line.strip()
            if name:
                counts[name] = counts.get(name, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: -kv[1])
        return tuple(name for name, _ in ranked[:limit])

    def churn(self, path: str, since: str = "1.year") -> int:
        raw = self._git("log", f"--since={since}", "--oneline", "--", path)
        return len([line for line in raw.splitlines() if line.strip()])

    def blame_head(self, path: str, line: int) -> str:
        raw = self._git("blame", "-L", f"{line},{line}", "--porcelain", "--", path)
        return raw.splitlines()[0].split()[0] if raw.strip() else ""

    # -- RepositoryIntelligence surface ----------------------------------

    def search(self, query: SearchQuery) -> SearchResult:
        """`git grep`: index-aware, so it never walks ignored files."""
        started = time.monotonic()
        if not self.available():
            return SearchResult(provenance=Provenance(provider=self.name, confidence=0.0))
        args = ["grep", "--line-number", "--no-color",
                "-C", str(max(0, query.context_lines))]
        if not query.case_sensitive:
            args.append("--ignore-case")
        if not query.regex:
            args.append("--fixed-strings")
        else:
            args.append("--extended-regexp")
        args += ["-e", query.pattern]
        if query.glob:
            args += ["--", query.glob]

        raw = self._git(*args)
        hits: list[SearchHit] = []
        for line in raw.splitlines():
            parts = line.split(":", 2)
            if len(parts) != 3 or not parts[1].isdigit():
                continue
            hits.append(SearchHit(path=parts[0], line=int(parts[1]),
                                  text=parts[2][:500], score=1.0))
            if len(hits) >= query.max_results:
                break
        return SearchResult(
            hits=tuple(hits),
            truncated=len(hits) >= query.max_results,
            provenance=Provenance(
                provider=f"{self.name}:grep", confidence=0.65,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            ),
        )

    def symbol(self, name: str) -> SymbolResult:
        """Git has no symbol table; the composite falls through to AST."""
        return SymbolResult(provenance=Provenance(provider=self.name, confidence=0.0))

    def dependencies(self, target: str) -> DependencyResult:
        """Co-change coupling: files that historically change *with* the target.

        This is a genuinely different dependency signal from imports. A file
        with no import edge to the target but a 0.8 co-change rate is usually
        an interface partner, and missing it is a common source of the
        `INCOMPLETE_PATCH` failure class.
        """
        if not self.available():
            return DependencyResult(target=target,
                                    provenance=Provenance(provider=self.name, confidence=0.0))
        started = time.monotonic()
        commits = [c for c in self._git(
            "log", "--pretty=format:%H", "-n", "120", "--", target).splitlines() if c]
        counts: dict[str, int] = {}
        for commit in commits:
            for name in self._git("show", "--name-only", "--pretty=format:",
                                  commit).splitlines():
                name = name.strip()
                if name and name != target:
                    counts[name] = counts.get(name, 0) + 1
        coupled = tuple(
            name for name, n in sorted(counts.items(), key=lambda kv: -kv[1])[:15]
            if n >= 2
        )
        return DependencyResult(
            target=target, imported_by=coupled,
            provenance=Provenance(
                provider=f"{self.name}:cochange", confidence=0.5,
                elapsed_ms=int((time.monotonic() - started) * 1000),
            ),
        )

    def tests_for(self, target: str) -> TestMapping:
        """Tests that historically changed alongside the target."""
        coupled = self.dependencies(target).imported_by
        tests = tuple(
            path for path in coupled
            if "test" in Path(path).parts or Path(path).name.startswith("test_")
        )
        return TestMapping(
            target=target, direct=tests,
            command_hint=f"pytest {' '.join(tests[:6])}" if tests else "",
            provenance=Provenance(provider=f"{self.name}:cochange",
                                  confidence=0.45 if tests else 0.0),
        )

    def summarize(self, scope: RepoScope) -> RepoSummary:
        return RepoSummary(provenance=Provenance(provider=self.name, confidence=0.0))

    # -- internals -------------------------------------------------------

    def _git(self, *args: str) -> str:
        try:
            proc = subprocess.run(
                ["git", "-C", str(self._root), *args],
                capture_output=True, text=True,
                timeout=self._timeout, check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return ""
        # `git grep` exits 1 on no matches; treat any nonzero as an empty
        # answer rather than an error, so a missing repo degrades silently.
        return proc.stdout if proc.returncode in (0, 1) else ""
```

---

## Cap. 9.3 — `vanguard/packages/apps/coding_max/intelligence/lda.py`

**Status:** ARQUIVO NOVO (criar integralmente) · **257 linhas**

Adaptador **opcional** com isolamento estrito. Declara disponibilidade honestamente, responde dentro de timeout duro, isola toda falha, e estampa proveniência.

```python
"""Optional LDA / Atlas adapter (`spec §9`).

`spec §9` states the constraint plainly: *"Do not make Coding Max dependent on
LDA."* This adapter therefore does four things and nothing else -- it declares
availability honestly, it answers within a hard timeout, it isolates every
failure, and it stamps provenance so a downstream ranking can discount a
semantic hit against a deterministic one.

The repository ships a `.lda/index.db` SQLite index. The adapter probes for
that shape and treats *any* deviation as unavailability rather than trying to
repair it: a half-understood index that returns plausible-but-wrong files is
worse than no index, because it produces confident mis-localisation.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

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

__all__ = ["LDAAdapter", "LDAConfig"]

#: Columns the adapter can work with, in preference order. The index schema is
#: probed rather than assumed, because an upstream schema change must degrade
#: to "unavailable", never to "wrong answers".
_PATH_COLUMNS = ("path", "file_path", "filepath", "file", "relpath")
_NAME_COLUMNS = ("name", "symbol", "symbol_name", "identifier")
_LINE_COLUMNS = ("line", "lineno", "line_number", "start_line")
_KIND_COLUMNS = ("kind", "type", "symbol_kind", "node_type")


class LDAConfig:
    """Declarative adapter policy (`spec §9`: timeout, caching, isolation)."""

    __slots__ = ("db_path", "timeout_s", "max_results", "enabled", "confidence")

    def __init__(
        self,
        db_path: Path | str,
        *,
        timeout_s: float = 3.0,
        max_results: int = 40,
        enabled: bool = True,
        confidence: float = 0.55,
    ) -> None:
        self.db_path = Path(db_path)
        self.timeout_s = timeout_s
        self.max_results = max_results
        self.enabled = enabled
        # Below the deterministic providers on purpose. A semantic hit is a
        # hint about where to look; a ripgrep hit is a fact about what is
        # written. Ranking them equally is how retrieval starts hallucinating.
        self.confidence = confidence

    @classmethod
    def for_workspace(cls, root: Path | str, **kwargs: Any) -> "LDAConfig":
        return cls(Path(root) / ".lda" / "index.db", **kwargs)


class LDAAdapter:
    """Semantic/index-backed intelligence. Never required, always isolated."""

    name = "lda"

    def __init__(self, config: LDAConfig) -> None:
        self._config = config
        self._schema: Mapping[str, Mapping[str, str]] | None = None
        self._probed = False

    # -- availability ----------------------------------------------------

    def available(self) -> bool:
        """True only if the index exists *and* exposes a usable symbol table."""
        if not self._config.enabled:
            return False
        if not self._config.db_path.is_file():
            return False
        self._probe()
        return bool(self._schema)

    def _probe(self) -> None:
        if self._probed:
            return
        self._probed = True
        try:
            with self._connect() as conn:
                tables = [
                    row[0] for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type IN ('table','view')"
                    ).fetchall()
                ]
                usable: dict[str, dict[str, str]] = {}
                for table in tables:
                    columns = {
                        str(row[1]).lower()
                        for row in conn.execute(f'PRAGMA table_info("{table}")').fetchall()
                    }
                    path_col = _first(columns, _PATH_COLUMNS)
                    name_col = _first(columns, _NAME_COLUMNS)
                    if not path_col:
                        continue
                    usable[table] = {
                        "path": path_col,
                        "name": name_col or "",
                        "line": _first(columns, _LINE_COLUMNS) or "",
                        "kind": _first(columns, _KIND_COLUMNS) or "",
                    }
                self._schema = usable or None
        except (sqlite3.Error, OSError):
            self._schema = None

    def _connect(self) -> sqlite3.Connection:
        # Read-only URI plus a busy timeout: the harness must never block on
        # or mutate an index another process owns.
        conn = sqlite3.connect(
            f"file:{self._config.db_path}?mode=ro",
            uri=True, timeout=self._config.timeout_s,
        )
        conn.execute(f"PRAGMA busy_timeout = {int(self._config.timeout_s * 1000)}")
        return conn

    # -- RepositoryIntelligence surface ----------------------------------

    def search(self, query: SearchQuery) -> SearchResult:
        started = time.monotonic()
        if not self.available():
            return self._empty_search(started)
        rows = self._query_symbols(query.pattern, limit=query.max_results)
        hits = tuple(
            SearchHit(path=row["path"], line=row["line"],
                      text=row["text"], score=self._config.confidence)
            for row in rows
        )
        return SearchResult(
            hits=hits, truncated=len(hits) >= query.max_results,
            provenance=self._provenance(started),
        )

    def symbol(self, name: str) -> SymbolResult:
        started = time.monotonic()
        if not self.available():
            return SymbolResult(provenance=self._provenance(started, confidence=0.0))
        rows = self._query_symbols(name, limit=self._config.max_results, exact=True)
        definitions = tuple(
            SymbolRef(
                name=row["name"] or name,
                kind=_kind_of(row["kind"]),
                path=row["path"], line=row["line"],
            )
            for row in rows
        )
        return SymbolResult(definitions=definitions, provenance=self._provenance(started))

    def dependencies(self, target: str) -> DependencyResult:
        return DependencyResult(
            target=target,
            provenance=Provenance(provider=self.name, confidence=0.0),
        )

    def tests_for(self, target: str) -> TestMapping:
        return TestMapping(
            target=target,
            provenance=Provenance(provider=self.name, confidence=0.0),
        )

    def summarize(self, scope: RepoScope) -> RepoSummary:
        return RepoSummary(provenance=Provenance(provider=self.name, confidence=0.0))

    # -- internals -------------------------------------------------------

    def _query_symbols(
        self, term: str, *, limit: int, exact: bool = False
    ) -> list[dict[str, Any]]:
        """Run the lookup against every usable table, isolating all failures.

        Parameterised throughout: the term is user/model-influenced text, and
        an index query is not a place to concatenate it into SQL.
        """
        assert self._schema is not None
        results: list[dict[str, Any]] = []
        deadline = time.monotonic() + self._config.timeout_s
        try:
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                for table, columns in self._schema.items():
                    if time.monotonic() > deadline or len(results) >= limit:
                        break
                    name_col = columns["name"]
                    if not name_col:
                        continue
                    operator, value = ("=", term) if exact else ("LIKE", f"%{term}%")
                    selected = [f'"{columns["path"]}" AS p', f'"{name_col}" AS n']
                    selected.append(f'"{columns["line"]}" AS l' if columns["line"]
                                    else "0 AS l")
                    selected.append(f'"{columns["kind"]}" AS k' if columns["kind"]
                                    else "'' AS k")
                    sql = (f'SELECT {", ".join(selected)} FROM "{table}" '
                           f'WHERE "{name_col}" {operator} ? LIMIT ?')
                    try:
                        rows = conn.execute(sql, (value, limit - len(results))).fetchall()
                    except sqlite3.Error:
                        continue
                    for row in rows:
                        results.append({
                            "path": str(row["p"] or ""),
                            "name": str(row["n"] or ""),
                            "line": _as_int(row["l"]),
                            "kind": str(row["k"] or ""),
                            "text": f'{row["k"] or "symbol"} {row["n"]}',
                        })
        except (sqlite3.Error, OSError):
            return results
        return results[:limit]

    def _provenance(self, started: float, confidence: float | None = None) -> Provenance:
        return Provenance(
            provider=f"{self.name}:index",
            confidence=self._config.confidence if confidence is None else confidence,
            elapsed_ms=int((time.monotonic() - started) * 1000),
        )

    def _empty_search(self, started: float) -> SearchResult:
        return SearchResult(provenance=self._provenance(started, confidence=0.0))


def _first(available: set[str], candidates: Sequence[str]) -> str:
    return next((c for c in candidates if c in available), "")


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _kind_of(raw: str) -> SymbolKind:
    lowered = (raw or "").lower()
    for kind in SymbolKind:
        if kind.value in lowered:
            return kind
    return SymbolKind.UNKNOWN
```

---

## Cap. 9.4 — Git responde o que análise estática não responde

Recência e churn são **priors fortes de localização**: um bug reportado hoje é
muito mais provável de viver num arquivo tocado este mês do que num intocado há
três anos. Custa uma chamada de subprocess.

```python
    def recent_files(self, limit: int = 60, since: str = "3.months") -> tuple[str, ...]:
```

E co-mudança é sinal de dependência genuinamente diferente de imports:

```python
    def dependencies(self, target: str) -> DependencyResult:
        """Co-change coupling: files that historically change *with* the target.

        This is a genuinely different dependency signal from imports. A file
        with no import edge to the target but a 0.8 co-change rate is usually
        an interface partner, and missing it is a common source of the
        `INCOMPLETE_PATCH` failure class.
        """
```

**Read-only por construção.** Efeitos no repositório vão pelo `GitEnvironment`
sob autorização do kernel (§40); nada aqui escreve.

```python
    def _git(self, *args: str) -> str:
        ...
        # `git grep` exits 1 on no matches; treat any nonzero as an empty
        # answer rather than an error, so a missing repo degrades silently.
        return proc.stdout if proc.returncode in (0, 1) else ""
```

---

## Cap. 9.5 — LDA: por que o schema é sondado, nunca assumido

```python
    def available(self) -> bool:
        """True only if the index exists *and* exposes a usable symbol table."""
```

Qualquer desvio de schema → `unavailable`. A justificativa está no docstring do
módulo:

> Um índice meio-compreendido que retorna arquivos plausíveis-mas-errados é
> **pior** que índice nenhum, porque produz mis-localização confiante.

O `.lda/index.db` presente neste repositório **foi detectado e é usável**:

```
PROVIDERS: ('native', 'git', 'lda')   LDA: True
```

### Postura de segurança do adaptador

```python
    def _connect(self) -> sqlite3.Connection:
        # Read-only URI plus a busy timeout: the harness must never block on
        # or mutate an index another process owns.
        conn = sqlite3.connect(
            f"file:{self._config.db_path}?mode=ro",
            uri=True, timeout=self._config.timeout_s,
        )
```

Toda query é **parametrizada**:

```python
        """Run the lookup against every usable table, isolating all failures.

        Parameterised throughout: the term is user/model-influenced text, and
        an index query is not a place to concatenate it into SQL.
        """
```

### Confiança abaixo dos determinísticos, deliberadamente

```python
        # Below the deterministic providers on purpose. A semantic hit is a
        # hint about where to look; a ripgrep hit is a fact about what is
        # written. Ranking them equally is how retrieval starts hallucinating.
        self.confidence = confidence   # default 0.55
```

---

## Cap. 9.6 — Para desligar LDA

Três caminhos, todos suportados:

```python
# 1. Por configuração de preset
HarnessConfig.for_preset('coding-balanced')     # use_lda=False

# 2. Por construção explícita
CompositeIntelligence(root, use_lda=False)

# 3. Por config do adaptador
LDAConfig.for_workspace(root, enabled=False)
```

E no manifest, via `retrieval-policy.json`:

```json
{"providers":["native","git","ast"], "lda":{"required":false,"timeoutMs":3000}}
```

`required` é sempre `false`. Não existe caminho em que LDA seja obrigatório —
essa é a garantia literal do §9.

---

## Cap. 9.7 — `TestMapping`: por que `direct` e `sibling` são separados

```python
@dataclass(frozen=True, slots=True)
class TestMapping:
    """Which tests plausibly cover a target, and how that was decided.

    `direct` are tests that name the target; `sibling` are tests in the
    conventional mirror location. The two are kept apart because they justify
    different verification layers: `direct` drives V5 (targeted tests),
    `sibling` drives V6 (related tests).
    """
```

Colapsar os dois faria V5 e V6 rodarem o mesmo conjunto, desperdiçando a camada
mais barata e removendo o sinal de regressão que V6 existe para dar.
