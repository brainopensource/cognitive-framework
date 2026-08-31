"""Deterministic multi-signal relevance context ranker for repository navigation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class RankedReference:
    file_path: str
    score: float
    matched_symbols: tuple[str, ...] = field(default_factory=tuple)
    reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class RankingWeights:
    lexical: float = 0.30
    symbol: float = 0.25
    dependency: float = 0.20
    path_prior: float = 0.10
    test_reference: float = 0.10
    recency: float = 0.05


def rank_repository_context(
    query_terms: Sequence[str],
    candidate_files: Mapping[str, str],  # file_path -> file_content
    *,
    weights: RankingWeights = RankingWeights(),
    test_files: Sequence[str] = (),
) -> tuple[RankedReference, ...]:
    """Rank repository files deterministically based on weighted multi-signal scoring."""
    ranked: list[RankedReference] = []
    query_set = {t.lower() for t in query_terms if t}

    for path, content in candidate_files.items():
        path_lower = path.lower()
        content_lower = content.lower()
        reasons: list[str] = []
        matched_symbols: list[str] = []

        # 1. Lexical match
        lexical_hits = sum(1 for t in query_set if t in content_lower)
        lexical_score = (lexical_hits / len(query_set)) if query_set else 0.0
        if lexical_score > 0:
            reasons.append(f"lexical_hits:{lexical_hits}")

        # 2. Path match (path prior)
        path_hits = sum(1 for t in query_set if t in path_lower)
        path_score = min(1.0, path_hits * 0.5)
        if path_score > 0:
            reasons.append(f"path_match:{path_hits}")

        # 3. Symbol match (simple name match)
        symbol_score = 0.0
        for t in query_set:
            if f"def {t}" in content_lower or f"class {t}" in content_lower:
                symbol_score = min(1.0, symbol_score + 0.5)
                matched_symbols.append(t)
        if symbol_score > 0:
            reasons.append(f"symbol_match:{','.join(matched_symbols)}")

        # 4. Test reference match
        test_score = 1.0 if path in test_files or "test" in path_lower else 0.0

        # Weighted total
        total_score = (
            weights.lexical * lexical_score
            + weights.symbol * symbol_score
            + weights.path_prior * path_score
            + weights.test_reference * test_score
        )

        if total_score > 0:
            ranked.append(
                RankedReference(
                    file_path=path,
                    score=round(total_score, 4),
                    matched_symbols=tuple(matched_symbols),
                    reasons=tuple(reasons),
                )
            )

    ranked.sort(key=lambda r: (-r.score, r.file_path))
    return tuple(ranked)
