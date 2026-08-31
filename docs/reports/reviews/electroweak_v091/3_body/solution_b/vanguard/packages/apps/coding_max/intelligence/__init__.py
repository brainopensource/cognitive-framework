"""Repository intelligence providers (`spec §8`, `§9`)."""

from __future__ import annotations

from .composite import CompositeIntelligence, IntelligenceCache, ProviderHealth
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
    SymbolKind,
    SymbolRef,
    SymbolResult,
    TestMapping,
)

__all__ = [
    "CompositeIntelligence", "DependencyResult", "GitProvider", "IntelligenceCache",
    "LDAAdapter", "LDAConfig", "NativeRepoSearch", "Provenance", "ProviderHealth",
    "RepoScope", "RepoSummary", "RepositoryIntelligence", "SearchHit", "SearchQuery",
    "SearchResult", "SymbolKind", "SymbolRef", "SymbolResult", "TestMapping",
]
