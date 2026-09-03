#!/usr/bin/env python3
"""Deterministic Local RAG V0 Retrieval Prototype for AETHER.

Performs structured exact-ID, authority-boosted, metadata-filtered keyword ranking
and context bundle construction over .generated/knowledge/ without vector databases or embeddings.

Supports three agent-facing modes:
  * Query mode      : authority-ranked document routing for a task string.
  * Reverse lookup  : given a production code path, return its canonical owner
                      documentation, subsystem, and defined symbols (code -> doc).
  * Budgeted packing: pack ranked results under a token budget using the
                      per-entry `estimated_tokens` catalog metadata.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = ROOT / ".generated" / "knowledge"


def load_jsonl(filename: str, knowledge_dir: Path | None = None) -> list[dict[str, str]]:
    path = (knowledge_dir or KNOWLEDGE_DIR) / filename
    if not path.exists():
        return []
    rows: list[dict[str, str]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def retrieve(
    query: str,
    include_non_canonical: bool = False,
    limit: int = 5,
    knowledge_dir: Path | None = None,
    budget: int | None = None,
) -> dict[str, object]:
    catalog = load_jsonl("catalog.jsonl", knowledge_dir)
    ownership = load_jsonl("ownership.jsonl", knowledge_dir)
    links = load_jsonl("links.jsonl", knowledge_dir)
    code_map = load_jsonl("code-map.jsonl", knowledge_dir)
    symbols = load_jsonl("symbols.jsonl", knowledge_dir)
    code_owners = {row.get("canonical_owner", "") for row in code_map}

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

        # Location demotion: docs/research/, docs/reports/, and docs/theory/ are
        # non-canonical by repository convention (AGENTS.md authority tiers) even
        # when their frontmatter does not say `authority: non-canonical` exactly.
        if path.startswith(("docs/research/", "docs/reports/", "docs/theory/")):
            score *= 0.3

        # Canonical-owner boost: documents that own a production subsystem in
        # code-map.jsonl are the routing targets agents actually need.
        if path in code_owners:
            score *= 1.4

        if score > 0.0:
            results.append({
                "canonical_id": doc_id,
                "title": title,
                "path": path,
                "authority": authority,
                "estimated_tokens": int(entry.get("estimated_tokens", 0) or 0),
                "score": round(score, 2),
            })

    results.sort(key=lambda x: float(x["score"]), reverse=True)
    top_results = results[:limit]

    # Token-budget packing: always keep the top hit, then add further hits while
    # the cumulative estimated token count stays inside the requested budget.
    if budget is not None and budget > 0:
        packed: list[dict[str, object]] = []
        used = 0
        for row in top_results:
            tokens = int(row.get("estimated_tokens", 0) or 0)
            if not packed or used + tokens <= budget:
                packed.append(row)
                used += tokens
        top_results = packed

    # Find related code mappings and symbols for the top result
    top_code = []
    top_symbols = []
    top_ownerships = []
    top_links = []
    if top_results:
        top_id = str(top_results[0]["canonical_id"])
        top_path = str(top_results[0]["path"])
        top_code = [c for c in code_map if c.get("canonical_owner") == top_path]
        top_symbols = [s for s in symbols if s.get("canonical_owner") == top_path]
        top_ownerships = [o for o in ownership if o.get("canonical_id") == top_id]
        top_links = [
            l for l in links
            if l.get("source_path") == top_path or l.get("target_path") == top_path
        ][:10]

    return {
        "query": query,
        "include_non_canonical": include_non_canonical,
        "budget": budget,
        "total_matches": len(results),
        "bounded_context": {
            "documents": top_results,
            "code_mappings": top_code,
            "symbols": top_symbols,
            "ownerships": top_ownerships,
            "related_links": top_links,
        },
    }


def lookup_file(file_path: str, knowledge_dir: Path | None = None) -> dict[str, object]:
    """Reverse routing: production code path -> canonical owner documentation.

    Answers the agent question "I am about to edit this file — which documents
    must I read and keep synchronized?"
    """
    normalized = file_path.replace("\\", "/").lstrip("./")
    normalized_dir = normalized if normalized.endswith("/") else normalized + "/"

    code_map = load_jsonl("code-map.jsonl", knowledge_dir)
    symbols = load_jsonl("symbols.jsonl", knowledge_dir)

    # Longest-prefix subsystem match (exact file rows beat directory rows).
    best_row: dict[str, str] | None = None
    best_len = -1
    for row in code_map:
        prefix = row.get("package_path", "")
        if normalized.startswith(prefix) or normalized_dir.startswith(prefix):
            if len(prefix) > best_len:
                best_len = len(prefix)
                best_row = row

    owner_doc = best_row.get("canonical_owner") if best_row else None
    catalog = {row.get("path"): row for row in load_jsonl("catalog.jsonl", knowledge_dir)}
    owner_entry = catalog.get(owner_doc, {}) if owner_doc else {}

    return {
        "file": file_path,
        "subsystem": best_row.get("subsystem") if best_row else None,
        "package_path": best_row.get("package_path") if best_row else None,
        "canonical_owner": owner_doc,
        "owner_title": owner_entry.get("title"),
        "owner_authority": owner_entry.get("authority"),
        "owner_estimated_tokens": int(owner_entry.get("estimated_tokens", 0) or 0),
        "symbols_defined_here": [s for s in symbols if s.get("defined_in") == normalized],
    }


def main() -> int:
    args = [a for a in sys.argv[1:]]
    include_non_canonical = "--include-non-canonical" in args
    args = [a for a in args if a != "--include-non-canonical"]

    budget: int | None = None
    if "--budget" in args:
        idx = args.index("--budget")
        budget = int(args[idx + 1])
        del args[idx:idx + 2]

    file_target: str | None = None
    if "--file" in args:
        idx = args.index("--file")
        file_target = args[idx + 1]
        del args[idx:idx + 2]

    query = " ".join(args) if args else "dispatch microkernel budget"

    if file_target:
        res: dict[str, object] = lookup_file(file_target)
    else:
        res = retrieve(query, include_non_canonical=include_non_canonical, budget=budget)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
