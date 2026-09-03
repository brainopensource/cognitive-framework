#!/usr/bin/env python3
"""Audit documentation context budgets and token metrics.

Scans all Markdown documents under docs/ and repository root to measure:
- File size (bytes)
- Line count
- Word count
- Estimated token count (~4 chars / token heuristic)
- Token classification (SMALL, NORMAL, LARGE, VERY_LARGE, OVERSIZED)
- Canonical vs Non-canonical breakdown
- Task packet token budget estimates for 16K/32K contexts
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)


def estimate_tokens(text: str) -> int:
    """Estimates token count deterministically based on character and word bounds."""
    # Standard LLM heuristic: ~4 characters per token or ~0.75 words per token
    char_count = len(text)
    word_count = len(text.split())
    # Blend character and word heuristics
    return int(math.ceil((char_count / 4.0 + word_count / 0.75) / 2.0))


def classify_size(tokens: int) -> str:
    if tokens < 4000:
        return "SMALL"
    elif tokens < 8000:
        return "NORMAL"
    elif tokens < 12000:
        return "LARGE"
    elif tokens < 16000:
        return "VERY_LARGE"
    else:
        return "OVERSIZED"


def audit_docs() -> dict[str, object]:
    doc_files = sorted(list((ROOT / "docs").rglob("*.md")))
    root_docs = [ROOT / f for f in ["README.md", "AGENTS.md", "VISION.md", "milestones.md"]]
    all_docs = sorted(set(doc_files + [f for f in root_docs if f.exists()]))

    inventory: list[dict[str, object]] = []
    class_counts = {"SMALL": 0, "NORMAL": 0, "LARGE": 0, "VERY_LARGE": 0, "OVERSIZED": 0}
    total_bytes = 0
    total_lines = 0
    total_words = 0
    total_tokens = 0

    for path in all_docs:
        rel_path = str(path.relative_to(ROOT))
        bytes_size = path.stat().st_size
        text = path.read_text(encoding="utf-8")
        lines = len(text.splitlines())
        words = len(text.split())
        tokens = estimate_tokens(text)
        size_class = classify_size(tokens)

        class_counts[size_class] += 1
        total_bytes += bytes_size
        total_lines += lines
        total_words += words
        total_tokens += tokens

        fm_match = FRONTMATTER_RE.match(text)
        meta: dict[str, str] = {}
        if fm_match:
            for line in fm_match.group(1).splitlines():
                line = line.strip()
                if ":" in line and not line.startswith("-") and not line.startswith("#"):
                    k, _, v = line.partition(":")
                    meta[k.strip()] = v.strip().strip("\"").strip("'")

        doc_id = meta.get("id") or meta.get("canonical_id") or path.stem
        title_match = HEADING_RE.search(text)
        title = title_match.group(1).strip() if title_match else path.stem
        title = re.sub(r"[`*_~]", "", title)

        inventory.append({
            "path": rel_path,
            "id": doc_id,
            "title": title,
            "bytes": bytes_size,
            "lines": lines,
            "words": words,
            "tokens": tokens,
            "class": size_class,
            "kind": meta.get("class", "standard"),
            "authority": meta.get("authority", "descriptive"),
            "status": meta.get("status", "living"),
            "owner": meta.get("owner", "repository-governance"),
        })

    inventory.sort(key=lambda x: int(x["tokens"]), reverse=True)

    return {
        "summary": {
            "total_documents": len(all_docs),
            "total_bytes": total_bytes,
            "total_lines": total_lines,
            "total_words": total_words,
            "total_estimated_tokens": total_tokens,
            "classifications": class_counts,
        },
        "inventory": inventory,
    }


if __name__ == "__main__":
    data = audit_docs()
    summary = data["summary"]
    print(f"DOCUMENTATION CONTEXT AUDIT SUMMARY:")
    print(f"Total Documents: {summary['total_documents']}")
    print(f"Total Bytes: {summary['total_bytes']:,}")
    print(f"Total Lines: {summary['total_lines']:,}")
    print(f"Total Words: {summary['total_words']:,}")
    print(f"Total Tokens (Est): {summary['total_estimated_tokens']:,}")
    print(f"Class Breakdown: {summary['classifications']}")
    print("\nTOP 15 LARGEST MARKDOWN FILES:")
    for doc in data["inventory"][:15]:
        print(f" - {doc['path']} ({doc['tokens']:,} tokens, {doc['class']}, {doc['authority']})")
