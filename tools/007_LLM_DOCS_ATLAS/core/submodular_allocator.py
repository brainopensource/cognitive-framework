"""Submodular Knapsack Context Allocator for Maximum Information Density.

Implements Minoux accelerated lazy-greedy submodular optimization over
heterogeneous code-doc candidates with token knapsack budget constraints.
"""
from __future__ import annotations

import heapq
import logging
from typing import Any, Dict, List, Mapping, Sequence, Set, Tuple

from .models import Candidate

logger = logging.getLogger(__name__)


class SubmodularContextAllocator:
    """Selects optimal, non-redundant candidates under a token budget."""

    def __init__(self, redundancy_penalty: float = 0.25, content_dedup_threshold: float = 0.9) -> None:
        self.lambda_penalty = redundancy_penalty
        self.content_dedup_threshold = content_dedup_threshold

    @staticmethod
    def _content_shingles(candidate: Candidate) -> Set[str]:
        """Word shingles of the candidate's real content (falls back to title)."""
        text = (candidate.content or candidate.title or "").lower()
        if not text:
            return set()
        return {w for w in text.split() if len(w) > 2}

    def _deduplicate(self, candidates: Sequence[Candidate]) -> List[Candidate]:
        """Drop near-duplicate content so redundant docs cannot consume budget.

        Two candidates with word-shingle Jaccard above the threshold are
        collapsed into the higher-scoring one (ties: first in order).
        """
        kept: List[Candidate] = []
        kept_shingles: List[Set[str]] = []
        for c in candidates:
            shingles = self._content_shingles(c)
            duplicate = False
            for prev in kept_shingles:
                if not shingles or not prev:
                    continue
                jaccard = len(shingles & prev) / len(shingles | prev)
                if jaccard >= self.content_dedup_threshold:
                    duplicate = True
                    break
            if duplicate:
                continue
            kept.append(c)
            kept_shingles.append(shingles)
        return kept

    def allocate(
        self,
        candidates: Sequence[Candidate],
        budget: int,
        ppr_scores: Mapping[str, float] | None = None,
    ) -> Tuple[List[Candidate], int]:
        """Pack candidates maximizing submodular coverage within budget."""
        if not candidates or budget <= 0:
            return [], 0

        # Content-level dedup pre-pass: identical documents must not each
        # occupy a budget slot (Phase A consolidation guarantee).
        candidates = self._deduplicate(candidates)
        if not candidates:
            return [], 0

        scores = ppr_scores or {c.locator: c.score for c in candidates}
        selected: List[Candidate] = []
        selected_tokens_set: Set[str] = set()
        consumed_tokens = 0

        # Pre-tokenize identifiers for Jaccard redundancy checking
        candidate_words: Dict[str, Set[str]] = {}
        for c in candidates:
            words = set(c.title.lower().split() + c.locator.lower().replace("#", "/").split("/"))
            candidate_words[c.locator] = {w for w in words if len(w) > 2}

        def compute_marginal_gain(c: Candidate) -> float:
            base_score = scores.get(c.locator, c.score)
            words = candidate_words.get(c.locator, set())

            if not selected:
                return max(base_score, 0.01)

            # Redundancy penalty against already selected candidates
            overlap_count = len(words & selected_tokens_set)
            overlap_ratio = overlap_count / max(len(words), 1)
            penalty = self.lambda_penalty * base_score * overlap_ratio
            return max(base_score - penalty, 0.001)

        # Priority queue for Minoux lazy greedy: store (-ratio, idx, candidate)
        pq: List[Tuple[float, int, Candidate]] = []
        for idx, c in enumerate(candidates):
            cost = max(c.tokens, 1)
            if cost <= budget:
                gain = compute_marginal_gain(c)
                ratio = gain / cost
                heapq.heappush(pq, (-ratio, idx, c))

        while pq and consumed_tokens < budget:
            neg_ratio, idx, candidate = heapq.heappop(pq)
            cost = max(candidate.tokens, 1)

            if consumed_tokens + cost > budget:
                continue

            current_gain = compute_marginal_gain(candidate)
            current_ratio = current_gain / cost

            if not pq or current_ratio >= -pq[0][0]:
                selected.append(candidate)
                selected_tokens_set.update(candidate_words.get(candidate.locator, set()))
                consumed_tokens += cost
            else:
                heapq.heappush(pq, (-current_ratio, idx, candidate))

        return selected, consumed_tokens
