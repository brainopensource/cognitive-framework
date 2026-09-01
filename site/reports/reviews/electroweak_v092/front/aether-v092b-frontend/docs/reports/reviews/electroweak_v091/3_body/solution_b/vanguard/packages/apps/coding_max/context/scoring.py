"""Context candidate scoring (`spec §11`)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

__all__ = ["Candidate", "ScoreBreakdown", "score_candidates"]


@dataclass(frozen=True, slots=True)
class Candidate:
    path: str
    text: str = ""
    line: int = 0
    provider: str = ""
    provider_confidence: float = 0.5
    pinned: bool = False

    @property
    def token_estimate(self) -> int:
        return max(1, len(self.text) // 4)


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    """Every term from `spec §11`, kept separate so a ranking is explainable."""

    task_similarity: float = 0.0
    symbol_relevance: float = 0.0
    dependency_proximity: float = 0.0
    test_relationship: float = 0.0
    stacktrace_relevance: float = 0.0
    recent_failure_relevance: float = 0.0
    plan_relevance: float = 0.0
    edit_proximity: float = 0.0
    redundancy: float = 0.0
    staleness: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.task_similarity + self.symbol_relevance + self.dependency_proximity
            + self.test_relationship + self.stacktrace_relevance
            + self.recent_failure_relevance + self.plan_relevance + self.edit_proximity
            - self.redundancy - self.staleness
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "taskSimilarity": round(self.task_similarity, 4),
            "symbolRelevance": round(self.symbol_relevance, 4),
            "dependencyProximity": round(self.dependency_proximity, 4),
            "testRelationship": round(self.test_relationship, 4),
            "stacktraceRelevance": round(self.stacktrace_relevance, 4),
            "recentFailureRelevance": round(self.recent_failure_relevance, 4),
            "planRelevance": round(self.plan_relevance, 4),
            "editProximity": round(self.edit_proximity, 4),
            "redundancy": round(self.redundancy, 4),
            "staleness": round(self.staleness, 4),
            "total": round(self.total, 4),
        }


def _tokens(text: str) -> set[str]:
    return {w for w in "".join(c if c.isalnum() else " " for c in text.lower()).split()
            if len(w) > 2}


def score_candidates(
    candidates: Sequence[Candidate],
    *,
    task: str = "",
    symbols: Sequence[str] = (),
    dependencies: Sequence[str] = (),
    tests: Sequence[str] = (),
    stacktrace_paths: Sequence[str] = (),
    failed_paths: Sequence[str] = (),
    plan_paths: Sequence[str] = (),
    edited_paths: Sequence[str] = (),
    seen_digests: Sequence[str] = (),
) -> tuple[tuple[Candidate, ScoreBreakdown], ...]:
    """Rank candidates. Pure: no I/O, so a ranking is reproducible from a trace."""
    task_tokens = _tokens(task)
    symbol_set = {s.lower() for s in symbols}
    dep_set = set(dependencies)
    test_set = set(tests)
    trace_set = set(stacktrace_paths)
    failed_set = set(failed_paths)
    plan_set = set(plan_paths)
    edited_set = set(edited_paths)
    seen = set(seen_digests)

    scored: list[tuple[Candidate, ScoreBreakdown]] = []
    for candidate in candidates:
        stem = Path(candidate.path).stem.lower()
        body_tokens = _tokens(candidate.text) | _tokens(candidate.path)
        overlap = len(task_tokens & body_tokens) / max(len(task_tokens), 1)

        breakdown = ScoreBreakdown(
            task_similarity=2.0 * overlap,
            symbol_relevance=1.5 if (stem in symbol_set or
                                     any(s in candidate.text.lower() for s in symbol_set)) else 0.0,
            dependency_proximity=1.0 if candidate.path in dep_set else 0.0,
            test_relationship=0.8 if candidate.path in test_set else 0.0,
            # A stack trace names the failing frame outright; nothing else in
            # the score is that direct a piece of localisation evidence.
            stacktrace_relevance=3.0 if candidate.path in trace_set else 0.0,
            recent_failure_relevance=1.2 if candidate.path in failed_set else 0.0,
            plan_relevance=1.0 if candidate.path in plan_set else 0.0,
            edit_proximity=1.4 if candidate.path in edited_set else 0.0,
            redundancy=2.0 if _digest(candidate) in seen else 0.0,
            # Large blobs crowd out several small, better-targeted candidates.
            staleness=min(1.5, candidate.token_estimate / 4000.0),
        )
        scored.append((candidate, breakdown))

    # Pinned candidates sort first regardless of score: pinning is an explicit
    # operator/plan decision and must not be silently overridden by ranking.
    scored.sort(key=lambda pair: (pair[0].pinned, pair[1].total), reverse=True)
    return tuple(scored)


def _digest(candidate: Candidate) -> str:
    from ....domain.canonicalisation.digest import digest_of

    return digest_of({"path": candidate.path, "text": candidate.text})
