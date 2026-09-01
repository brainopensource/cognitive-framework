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

    def __init__(self, redundancy_penalty: float = 0.25) -> None:
        self.lambda_penalty = redundancy_penalty

    def allocate(
        self,
        candidates: Sequence[Candidate],
        budget: int,
        ppr_scores: Mapping[str, float] | None = None,
    ) -> Tuple[List[Candidate], int]:
        """Pack candidates maximizing submodular coverage within budget."""
        if not candidates or budget <= 0:
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
