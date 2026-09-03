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
