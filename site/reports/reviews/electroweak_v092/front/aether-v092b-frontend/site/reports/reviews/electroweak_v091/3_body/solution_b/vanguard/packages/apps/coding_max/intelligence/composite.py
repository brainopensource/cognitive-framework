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
