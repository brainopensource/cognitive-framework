"""Multi-dimensional task-conditioned ranking and budget knapsack allocator."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple
from .models import Candidate
from .storage import FactGraphStorage


def extract_search_terms(text: str) -> List[str]:
    """Extract salient search terms and code identifiers from a task prompt."""
    raw = re.findall(r"[a-zA-Z0-9_/-]{2,}", text)
    stopwords = {"and", "for", "the", "with", "from", "that", "this", "into", "over", "what", "when", "where", "which", "make", "help", "need"}
    return [t.lower() for t in raw if t.lower() not in stopwords]


def rank_entities(
    task: str,
    storage: FactGraphStorage,
    candidate_limit: int = 60,
) -> List[Candidate]:
    """Rank repository entities using multi-signal scoring."""
    terms = extract_search_terms(task)
    if not terms:
        terms = ["readme"]

    fts_results = storage.search_fts(" ".join(terms), limit=candidate_limit)
    candidates: List[Candidate] = []
    seen_ids: Set[str] = set()

    for item in fts_results:
        entity_id = item["entity_id"]
        if entity_id in seen_ids:
            continue
        seen_ids.add(entity_id)

        kind = item.get("kind", "unknown")
        title = item.get("title", item.get("name", entity_id))
        locator = item.get("locator", "")

        # 1. Lexical / BM25 baseline score
        rank_val = abs(float(item.get("rank", 0.0)))
        score = 25.0 + rank_val * 5.0

        # 2. Exact identifier boost
        title_lower = title.lower()
        if any(t == title_lower for t in terms):
            score += 40.0
        elif any(t in title_lower for t in terms):
            score += 20.0

        # 3. Code vs Doc classification
        authority = None
        est_tokens = 100

        if kind == "document":
            # Check document authority
            docs = storage.get_docs_for_symbol(entity_id)
            if docs:
                authority = docs[0].get("authority")
            if authority in ("constitutional", "normative", "canonical"):
                score += 30.0
            elif "readme" in locator.lower() or "spec" in locator.lower():
                score += 20.0
            est_tokens = 300
        elif kind == "symbol":
            # Check for tests and callers
            callers = storage.get_callers(entity_id)
            if callers:
                score += min(len(callers) * 5.0, 25.0)
            tests = storage.get_tests_for_symbol(entity_id)
            if tests:
                score += 15.0
            est_tokens = 120

        candidates.append(
            Candidate(
                locator=locator,
                kind=kind,
                title=title,
                score=score,
                tokens=est_tokens,
                reason="Task relevance & graph match",
                authority=authority,
                representation="FULL" if score > 50 else "SKELETON"
            )
        )

    # Sort descending by score
    candidates.sort(key=lambda c: (-c.score, c.tokens, c.locator))
    return candidates


def allocate_budget(
    candidates: List[Candidate],
    budget: int,
) -> Tuple[List[Candidate], int]:
    """Knapsack budget allocation to pack highest-value evidence under token limit."""
    selected: List[Candidate] = []
    used_tokens = 0

    for c in candidates:
        if used_tokens + c.tokens <= budget:
            selected.append(c)
            used_tokens += c.tokens

    return selected, used_tokens
