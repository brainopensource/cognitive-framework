"""Semantic Intent Symbol Resolution Engine (Requirement Phase 3).

Resolves natural language queries and architectural concepts to exact symbols
without requiring the caller to know the precise symbol name.
Deterministic, 100% offline, zero-network, zero-torch/external models.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .storage import FactGraphStorage

_STOP_WORDS: Set[str] = {
    "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "with",
    "is", "it", "at", "by", "from", "as", "into", "how", "what", "which",
    "can", "should", "will", "all", "each", "both", "any", "some", "our",
}

_STEM_SUFFIXES = (
    "tion", "sion", "ing", "ers", "er", "or", "ed", "es", "ies",
    "s", "al", "ic", "able", "ible", "ive", "ate", "ize", "ise",
)


def _stem(word: str) -> str:
    w = word.lower()
    for _ in range(2):
        stripped = False
        for suffix in _STEM_SUFFIXES:
            if w.endswith(suffix) and len(w) - len(suffix) >= 3:
                w = w[:-len(suffix)]
                stripped = True
                break
        if not stripped:
            break
    return w


def _tokenize_query(query: str) -> List[str]:
    """Tokenize query into clean, significant lowercase terms."""
    # Split camelCase / snake_case / spaces / punctuation
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", query)
    raw = re.findall(r"[a-zA-Z0-9_]+", s)
    terms = [
        w.lower()
        for w in raw
        if len(w) >= 3 and w.lower() not in _STOP_WORDS
    ]
    return terms


def resolve_symbol_intent(
    storage: FactGraphStorage,
    query: str,
    top_k: int = 5,
    profile: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """Resolve natural language query to candidate symbols using multi-signal offline ranking."""
    terms = _tokenize_query(query)
    if not terms:
        return []

    con = storage.get_connection()
    candidates: Dict[str, Dict[str, Any]] = {}

    # 1. SQL LIKE query across symbols (ordered by architectural tiers)
    for t in terms[:6]:
        t_stem = _stem(t)
        cur = con.execute(
            """
            SELECT id, name, qualified_name, kind, file_path, signature, docstring, start_line, end_line
            FROM symbols
            WHERE name LIKE ? OR docstring LIKE ? OR signature LIKE ? OR file_path LIKE ?
            ORDER BY CASE
                WHEN file_path LIKE 'vanguard/packages/kernel/%' THEN 1
                WHEN file_path LIKE 'vanguard/packages/domain/%' THEN 2
                WHEN file_path LIKE 'vanguard/packages/ports/%' THEN 3
                WHEN file_path LIKE 'vanguard/packages/agency/%' THEN 4
                WHEN file_path LIKE 'vanguard/packages/runtime/%' THEN 5
                WHEN file_path LIKE 'vanguard/packages/adapters/%' THEN 6
                WHEN file_path LIKE 'test/%' THEN 8
                WHEN file_path LIKE 'benchmarks/%' THEN 9
                ELSE 7 END
            LIMIT 60
            """,
            (f"%{t_stem}%", f"%{t}%", f"%{t}%", f"%{t}%"),
        )
        for r in cur.fetchall():
            d = dict(r)
            candidates[d["id"]] = d

    # 2. FTS5 BM25 search over symbol entities
    fts_terms = [t.replace("'", "''") for t in terms[:6]]
    fts_expr = " OR ".join(fts_terms)
    try:
        cur_fts = con.execute(
            """
            SELECT entity_id, bm25(fts_search) as rank
            FROM fts_search
            WHERE fts_search MATCH ? AND kind IN ('symbol', 'function', 'class', 'method')
            ORDER BY rank
            LIMIT 40
            """,
            (fts_expr,),
        )
        for f in cur_fts.fetchall():
            eid = f["entity_id"]
            if eid not in candidates:
                s_cur = con.execute("SELECT * FROM symbols WHERE id = ?", (eid,))
                s_row = s_cur.fetchone()
                if s_row:
                    candidates[eid] = dict(s_row)
                    candidates[eid]["fts_rank"] = f["rank"]
            else:
                candidates[eid]["fts_rank"] = f["rank"]
    except Exception:
        pass

    # 3. Multi-signal scoring and re-ranking
    scored: List[Dict[str, Any]] = []
    wants_test = any(t in ("test", "tests", "benchmark", "fake", "mock") for t in terms)

    for cid, sym in candidates.items():
        score = 0.0
        reasons: List[str] = []
        name_lower = sym["name"].lower()
        name_stem = _stem(name_lower)
        fp = sym["file_path"].lower()
        doc = (sym.get("docstring") or "").lower()
        sig = (sym.get("signature") or "").lower()
        qual = sym.get("qualified_name", "").lower()

        matched_terms: Set[str] = set()

        for t in terms:
            t_stem = _stem(t)
            # Exact name match
            if t == name_lower:
                score += 45.0
                matched_terms.add(t)
                reasons.append(f"exact name '{t}'")
            # Root stem match on name
            elif t_stem == name_stem or (len(t_stem) >= 4 and name_stem.startswith(t_stem)):
                score += 35.0
                matched_terms.add(t)
                reasons.append(f"name stem '{t}'")
            # Substring in name
            elif t in name_lower:
                score += 20.0
                matched_terms.add(t)
                reasons.append(f"name substring '{t}'")
            # In file path
            elif t in fp or t_stem in fp:
                score += 22.0
                matched_terms.add(t)
                reasons.append(f"file path '{t}'")
            # In signature
            elif t in sig or t_stem in sig:
                score += 15.0
                matched_terms.add(t)
                reasons.append(f"signature match '{t}'")
            # In docstring
            elif t in doc or t_stem in doc:
                score += 12.0
                matched_terms.add(t)
                reasons.append(f"docstring match '{t}'")

        # Term coverage fraction
        coverage = len(matched_terms) / len(terms) if terms else 0.0
        score += coverage * 35.0
        if coverage == 1.0:
            reasons.append("100% term coverage")
        elif coverage >= 0.5:
            reasons.append(f"{int(coverage * 100)}% coverage")

        # Architectural tier bonus
        if "vanguard/packages/kernel/" in fp:
            score += 26.0
            reasons.append("TCB kernel (+26)")
        elif "vanguard/packages/domain/" in fp:
            score += 22.0
            reasons.append("domain contract (+22)")
        elif "vanguard/packages/ports/" in fp:
            score += 18.0
            reasons.append("port interface (+18)")
        elif "vanguard/packages/agency/" in fp:
            score += 16.0
            reasons.append("agency engine (+16)")
        elif "vanguard/packages/runtime/" in fp:
            score += 14.0
            reasons.append("runtime composition (+14)")
        elif "vanguard/packages/adapters/" in fp:
            score += 12.0
            reasons.append("adapter (+12)")
        elif ("test/" in fp or "benchmarks/" in fp) and not wants_test:
            score -= 35.0

        # Graph centrality: in-degree callers
        try:
            c_cur = con.execute(
                'SELECT COUNT(*) FROM relations WHERE kind = "calls" AND (target_id = ? OR target_id = ?)',
                (cid, f"name:{sym['name']}"),
            )
            callers = c_cur.fetchone()[0]
        except Exception:
            callers = 0

        if callers > 0:
            call_boost = min(15.0, 3.0 * math.log2(1 + callers))
            score += call_boost
            reasons.append(f"{callers} callers (+{call_boost:.1f})")

        # Prefer class/function over tiny methods named __init__ or helper
        if sym["kind"] in ("class", "function"):
            score += 5.0
        if sym["name"] in ("__init__", "setUp", "tearDown"):
            score -= 15.0

        confidence = round(max(0.01, min(1.0, score / 125.0)), 3)

        scored.append({
            "symbol_id": cid,
            "name": sym["name"],
            "qualified_name": sym.get("qualified_name", ""),
            "kind": sym.get("kind", "symbol"),
            "language": sym.get("language", "python"),
            "file_path": sym["file_path"],
            "start_line": sym.get("start_line", 1),
            "end_line": sym.get("end_line", 1),
            "signature": sym.get("signature") or f"{sym['name']}()",
            "docstring": (sym.get("docstring") or "").strip().split("\n\n")[0][:200],
            "confidence_score": confidence,
            "callers_count": callers,
            "reason": ", ".join(reasons),
            "_raw_score": score,
        })

    # Sort descending by raw score
    scored.sort(key=lambda x: x["_raw_score"], reverse=True)

    # Deduplicate by qualified_name / locator
    seen_quals: Set[str] = set()
    deduped: List[Dict[str, Any]] = []
    for item in scored:
        key = (item["file_path"], item["name"], item["start_line"])
        if key in seen_quals:
            continue
        seen_quals.add(key)
        item.pop("_raw_score", None)
        deduped.append(item)
        if len(deduped) >= top_k:
            break

    return deduped
