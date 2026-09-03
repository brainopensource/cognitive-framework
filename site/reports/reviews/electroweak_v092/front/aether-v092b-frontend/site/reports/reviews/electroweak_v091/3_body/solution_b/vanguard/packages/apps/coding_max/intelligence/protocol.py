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
