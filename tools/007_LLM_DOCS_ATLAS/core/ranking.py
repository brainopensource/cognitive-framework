"""Multi-dimensional task-conditioned ranking and budget knapsack allocator."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from .models import Candidate
from .storage import FactGraphStorage

# Locator fragments that are never useful agent context. Benchmark runs, test
# fixtures, package shells, and build artifacts otherwise flood FTS results.
LOW_SIGNAL_LOCATOR_PATTERNS: Tuple[str, ...] = (
    "test/broken/",
    "/runs/",
    "benchmarks/frontier",
    "__init__.py",
    "/dist",
    "site/",
    "answer_bank",
    ".vanguard/",
    "node_modules",
    "dashboard.html",
    "tools/lda/index.html",
)

# Directory tiers that are non-canonical by repository convention even when
# their frontmatter omits `authority: non-canonical` (AGENTS.md authority tiers).
NON_CANONICAL_PREFIXES: Tuple[str, ...] = ("docs/research/", "docs/reports/", "docs/theory/")


def load_catalog_metadata(repo_root: Path) -> Dict[str, Dict[str, Any]]:
    """Load path-keyed catalog metadata (authority, estimated_tokens) from the
    canonical knowledge base in .generated/knowledge/catalog.jsonl."""
    catalog_path = Path(repo_root) / ".generated" / "knowledge" / "catalog.jsonl"
    by_path: Dict[str, Dict[str, Any]] = {}
    if not catalog_path.exists():
        return by_path
    try:
        for line in catalog_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("path"):
                by_path[row["path"]] = row
    except (OSError, json.JSONDecodeError):
        return {}
    return by_path


def is_low_signal(locator: str) -> bool:
    """True when a locator is build/test-fixture noise rather than agent context."""
    return any(pattern in locator for pattern in LOW_SIGNAL_LOCATOR_PATTERNS)


def catalog_fallback_candidates(
    task: str,
    catalog_by_path: Dict[str, Dict[str, Any]],
    limit: int = 12,
) -> List[Candidate]:
    """Authority-aware catalog keyword routing used when the FTS fact graph is
    empty or yields no results. Keeps LDA's context compiler useful without a
    populated .lda/index.db and propagates real authority metadata."""
    terms = [t.lower() for t in re.findall(r"[a-zA-Z0-9_/-]{2,}", task)]
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for row in catalog_by_path.values():
        path = row.get("path", "")
        authority = row.get("authority", "descriptive")
        if authority == "non-canonical":
            continue
        if any(path.startswith(p) for p in NON_CANONICAL_PREFIXES):
            continue
        haystack = " ".join([
            row.get("canonical_id", ""),
            row.get("title", ""),
            path,
        ]).lower()
        score = 0.0
        for term in terms:
            if term and term in haystack:
                score += 10.0
        if score <= 0.0:
            continue
        if authority == "normative":
            score *= 1.5
        elif authority == "binding-decision":
            score *= 1.3
        elif authority == "execution":
            score *= 1.2
        scored.append((score, row))
    scored.sort(key=lambda pair: (-pair[0], pair[1].get("path", "")))
    candidates: List[Candidate] = []
    for score, row in scored[:limit]:
        candidates.append(
            Candidate(
                locator=row.get("path", ""),
                kind="document",
                title=row.get("title", row.get("canonical_id", "")),
                score=score,
                tokens=int(row.get("estimated_tokens", 300) or 300),
                reason="Canonical knowledge-base catalog match",
                authority=row.get("authority"),
                representation="FULL",
            )
        )
    return candidates


def extract_search_terms(text: str) -> List[str]:
    """Extract salient search terms and code identifiers from a task prompt."""
    raw = re.findall(r"[a-zA-Z0-9_/-]{2,}", text)
    stopwords = {"and", "for", "the", "with", "from", "that", "this", "into", "over", "what", "when", "where", "which", "make", "help", "need"}
    return [t.lower() for t in raw if t.lower() not in stopwords]


def rank_entities(
    task: str,
    storage: FactGraphStorage,
    candidate_limit: int = 60,
    repo_root: Optional[Path] = None,
) -> List[Candidate]:
    """Rank repository entities using multi-signal scoring."""
    terms = extract_search_terms(task)
    if not terms:
        terms = ["readme"]

    if repo_root is None:
        repo_root = storage.db_path.parent.parent
    catalog_by_path = load_catalog_metadata(repo_root)

    fts_results = storage.search_fts(" ".join(terms), limit=candidate_limit)
    candidates: List[Candidate] = []
    seen_ids: Set[str] = set()

    for item in fts_results:
        entity_id = item["entity_id"]
        if entity_id in seen_ids:
            continue

        kind = item.get("kind", "unknown")
        title = item.get("title", item.get("name", entity_id))
        locator = item.get("locator", "")

        # Skip build/test-fixture noise: it is never useful agent context.
        if is_low_signal(locator):
            continue
        seen_ids.add(entity_id)

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
        authority: Optional[str] = None
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
            # Enrich from the canonical knowledge base when the fact graph has
            # no authority record (e.g. cold index).
            catalog_row = catalog_by_path.get(locator)
            if catalog_row:
                if not authority:
                    authority = catalog_row.get("authority")
                est_tokens = int(catalog_row.get("estimated_tokens", est_tokens) or est_tokens)
            # Demote non-canonical documentation tiers.
            if authority == "non-canonical" or any(locator.startswith(p) for p in NON_CANONICAL_PREFIXES):
                score *= 0.3
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

    # Fallback: route from the canonical catalog when the fact graph yields
    # nothing (an empty/cold .lda/index.db must not degrade agent routing).
    if not candidates:
        candidates = catalog_fallback_candidates(task, catalog_by_path)

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
