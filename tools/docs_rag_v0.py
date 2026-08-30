#!/usr/bin/env python3
"""Deterministic Local RAG V0 Retrieval Prototype for AETHER.

Performs structured exact-ID, authority-boosted, metadata-filtered keyword ranking
and context bundle construction over .generated/knowledge/ without vector databases or embeddings.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / ".generated" / "knowledge"


def load_jsonl(filename: str) -> list[dict[str, str]]:
    path = KNOWLEDGE_DIR / filename
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def retrieve(query: str, include_non_canonical: bool = False, limit: int = 5) -> dict[str, object]:
    catalog = load_jsonl("catalog.jsonl")
    ownership = load_jsonl("ownership.jsonl")
    links = load_jsonl("links.jsonl")
    code_map = load_jsonl("code-map.jsonl")
    symbols = load_jsonl("symbols.jsonl")

    query_terms = [t.lower() for t in query.split()]
    results: list[dict[str, object]] = []

    for entry in catalog:
        authority = entry.get("authority", "descriptive")
        if authority == "non-canonical" and not include_non_canonical:
            continue

        score = 0.0
        doc_id = entry.get("canonical_id", "")
        title = entry.get("title", "")
        path = entry.get("path", "")

        # Exact ID match
        if doc_id.lower() in query.lower():
            score += 100.0

        # Term matching against ID, title, path, and body content
        file_path = ROOT / path
        body_text = file_path.read_text(encoding="utf-8").lower() if file_path.is_file() else ""

        for term in query_terms:
            if term in doc_id.lower():
                score += 20.0
            if term in title.lower():
                score += 10.0
            if term in path.lower():
                score += 5.0
            if term in body_text:
                score += 1.0 + min(body_text.count(term) * 0.1, 5.0)

        # Authority ranking boost
        if authority == "normative":
            score *= 1.5
        elif authority == "binding-decision":
            score *= 1.3
        elif authority == "execution":
            score *= 1.2

        if score > 0.0:
            results.append({
                "canonical_id": doc_id,
                "title": title,
                "path": path,
                "authority": authority,
                "score": round(score, 2),
            })

    results.sort(key=lambda x: float(x["score"]), reverse=True)
    top_results = results[:limit]

    # Find related code mappings and symbols for top result
    top_code = []
    top_symbols = []
    if top_results:
        top_id = str(top_results[0]["canonical_id"])
        top_path = str(top_results[0]["path"])
        top_code = [c for c in code_map if c.get("canonical_owner") == top_path]
        top_symbols = [s for s in symbols if s.get("canonical_owner") == top_path]

    return {
        "query": query,
        "include_non_canonical": include_non_canonical,
        "total_matches": len(results),
        "bounded_context": {
            "documents": top_results,
            "code_mappings": top_code,
            "symbols": top_symbols,
        },
    }


def main() -> int:
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "dispatch microkernel budget"
    res = retrieve(query)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
