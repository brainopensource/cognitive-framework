"""Hybrid retrieval: deterministic dense embeddings + Reciprocal Rank Fusion.

Two composable pieces:

1. ``stable_embedding`` — feature-hashed n-gram embeddings that are identical
   across interpreter processes (unlike ``hash()``, which is salted per
   process and silently breaks cache/provenance determinism).
2. ``reciprocal_rank_fusion`` — merges multiple ranked locator lists (BM25,
   dense cosine, authority/PPR) into one ranking with the standard RRF
   constant k=60. Fully deterministic.

Both are dependency-free and run on CPU; optional backends (sqlite-vec,
ONNX) can replace the embedder behind the same interface later.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Dict, Iterable, List, Mapping, Sequence

DEFAULT_DIM = 256
RRF_K = 60
_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


def stable_embedding(text: str, dim: int = DEFAULT_DIM) -> List[float]:
    """Deterministic feature-hashed trigram/term embedding (zero-VRAM CPU).

    Uses md5-based bucketing instead of Python's salted ``hash()`` so vectors
    are byte-identical across processes and runs.
    """
    vec = [0.0] * dim
    normalized = (text or "").lower().strip()
    if not normalized:
        return vec
    tokens = _TOKEN_RE.findall(normalized)
    features: List[str] = list(tokens)
    for tok in tokens:
        if len(tok) >= 3:
            features.extend(tok[i: i + 3] for i in range(len(tok) - 2))
    for feature in features:
        digest = hashlib.md5(feature.encode("utf-8")).digest()
        bucket = int.from_bytes(digest[:4], "little") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vec[bucket] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0.0:
        vec = [v / norm for v in vec]
    return vec


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    return sum(x * y for x, y in zip(a, b))


class DenseRetriever:
    """In-memory dense index over symbols and document sections."""

    def __init__(self, dim: int = DEFAULT_DIM) -> None:
        self.dim = dim
        self._vectors: Dict[str, List[float]] = {}
        self._meta: Dict[str, Dict[str, object]] = {}

    def add(self, locator: str, text: str, meta: Dict[str, object] | None = None) -> None:
        if locator and text:
            vec = stable_embedding(text, self.dim)
            if any(vec):
                self._vectors[locator] = vec
                if meta:
                    self._meta[locator] = meta

    def build_from_storage(self, storage) -> int:
        """Index all symbols and doc sections from a FactGraphStorage."""
        self._vectors.clear()
        self._meta.clear()
        try:
            for sym in storage.get_all_symbols():
                text = " ".join(
                    part for part in (
                        sym.get("name", ""),
                        sym.get("qualified_name", ""),
                        sym.get("signature", "") or "",
                        sym.get("docstring", "") or "",
                    ) if part
                )
                locator = f"{sym.get('file_path', '')}#{sym.get('name', '')}"
                self.add(locator, text, {
                    "kind": "symbol",
                    "title": sym.get("name", ""),
                    "tokens": 120,
                })
        except Exception:
            pass
        try:
            for row in storage.get_all_sections():
                text = " ".join(
                    part for part in (
                        row.get("heading", ""),
                        row.get("content", "") or "",
                    ) if part
                )
                path = row.get("file_path", "")
                locator = f"{path}#L{row.get('start_line', 1)}-L{row.get('end_line', 1)}"
                self.add(locator, text, {
                    "kind": "doc_section",
                    "title": row.get("heading", ""),
                    "tokens": int(row.get("estimated_tokens") or 100),
                    "content": (row.get("content") or "")[:1200],
                    "authority": row.get("authority"),
                })
        except Exception:
            pass
        return len(self._vectors)

    def search(self, query: str, limit: int = 30) -> List[str]:
        """Return locator names ranked by dense cosine similarity."""
        return [locator for locator, _, _ in self.ranked(query, limit)]

    def ranked(self, query: str, limit: int = 30) -> List[tuple[str, float, Dict[str, object]]]:
        """Return (locator, cosine_score, metadata) ranked by similarity."""
        qvec = stable_embedding(query, self.dim)
        if not any(qvec):
            return []
        scored = [
            (cosine(qvec, vec), locator)
            for locator, vec in self._vectors.items()
        ]
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        return [
            (locator, score, dict(self._meta.get(locator, {})))
            for score, locator in scored[:limit]
            if score > 0.0
        ]


def reciprocal_rank_fusion(
    rankings: Mapping[str, Sequence[str]],
    k: int = RRF_K,
    weights: Mapping[str, float] | None = None,
    limit: int = 60,
) -> List[tuple[str, float]]:
    """Fuse ranked locator lists into one deterministic ranking.

    Returns ``[(locator, rrf_score)]`` sorted by descending score, ties broken
    by locator for determinism. Channel weights are optional multipliers.
    """
    scores: Dict[str, float] = {}
    for channel, locators in rankings.items():
        weight = float((weights or {}).get(channel, 1.0))
        for rank, locator in enumerate(locators):
            scores[locator] = scores.get(locator, 0.0) + weight / (k + rank + 1)
    fused = sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
    return fused[:limit]


__all__ = [
    "DenseRetriever",
    "RRF_K",
    "cosine",
    "reciprocal_rank_fusion",
    "stable_embedding",
]
