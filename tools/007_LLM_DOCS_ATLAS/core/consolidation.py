"""Knowledge consolidation diagnostics for LDA.

Detects duplicate/overlapping documents and conflicting authority claims from
the fact graph. Read-only, deterministic, single-emitter safe.
"""
from __future__ import annotations

from typing import Any, Dict, List, Set

WORD_THRESHOLD = 0.85


def _words(text: str) -> Set[str]:
    return {w for w in (text or "").lower().split() if len(w) > 2}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def detect_duplicates(storage: Any, limit: int = 20) -> List[Dict[str, Any]]:
    """Document pairs whose aggregated section text is near-identical."""
    docs: Dict[str, str] = {}
    try:
        for row in storage.get_all_sections():
            path = row.get("file_path", "")
            docs[path] = (docs.get(path, "") + " " + (row.get("content") or "")).strip()
    except Exception:
        return []
    paths = sorted(docs)
    duplicates: List[Dict[str, Any]] = []
    for i, a in enumerate(paths):
        wa = _words(docs[a])
        for b in paths[i + 1:]:
            score = _jaccard(wa, _words(docs[b]))
            if score >= WORD_THRESHOLD:
                duplicates.append({"a": a, "b": b, "similarity": round(score, 4)})
                if len(duplicates) >= limit:
                    return duplicates
    return duplicates


def find_authority_conflicts(storage: Any) -> List[Dict[str, Any]]:
    """Documents sharing one canonical_id (or file path basename) but claiming
    different authority tiers — a consolidation smell the human owner must
    resolve."""
    by_canon: Dict[str, set] = {}
    con = storage.get_connection()
    try:
        rows = con.execute(
            "SELECT canonical_id, file_path, title, authority FROM documents ORDER BY file_path"
        ).fetchall()
    except Exception:
        return []
    for r in rows:
        key = r["canonical_id"] or r["title"]
        by_canon.setdefault(key, set()).add((r["file_path"], r["authority"]))
    conflicts: List[Dict[str, Any]] = []
    for key, entries in sorted(by_canon.items()):
        authorities = {a for _, a in entries if a}
        if len(authorities) > 1:
            conflicts.append({
                "topic": key,
                "documents": sorted(f"{p} ({a})" for p, a in entries),
                "authorities": sorted(authorities),
            })
    return conflicts


def run_consolidation(storage: Any) -> Dict[str, Any]:
    duplicates = detect_duplicates(storage)
    conflicts = find_authority_conflicts(storage)
    status = "HEALTHY" if not duplicates and not conflicts else "NEEDS_CONSOLIDATION"
    return {
        "status": status,
        "duplicate_documents": duplicates,
        "authority_conflicts": conflicts,
        "summary": (
            f"{len(duplicates)} duplicate document pair(s), "
            f"{len(conflicts)} authority conflict(s)"
        ),
    }


__all__ = ["detect_duplicates", "find_authority_conflicts", "run_consolidation"]
