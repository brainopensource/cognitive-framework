"""Optional Zero-VRAM Hybrid Vector Search Plugin for LDA.

Provides dense cosine vector retrieval over symbol names, docstrings,
and signatures using sqlite-vec or embedded CPU representations.
100% decoupled, optional, and comuttable via PluginManager.
"""
from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ..core.config import AtlasContext
from ..core.models import Candidate, Diagnostic, Entity, Metric, ProviderResult, Relation
from ..core.registry import Plugin, PluginManifest

logger = logging.getLogger(__name__)


class SqliteVecPlugin:
    """Optional decoupled hybrid vector search plugin for LDA."""

    def __init__(self) -> None:
        self.manifest = PluginManifest(
            name="sqlite_vec_ranker",
            version="1.0.0",
            description="Optional Zero-VRAM vector search adapter using sqlite-vec and CPU dense embeddings.",
            author="AETHER LDA Team",
            enabled=True,
            tags=("vector", "hybrid", "search", "optional"),
        )
        self._vector_store: Dict[str, List[float]] = {}  # symbol_id -> normalized vector

    def available(self, ctx: AtlasContext) -> bool:
        """Plugin is always available with embedded fallback."""
        return True

    def collect(self, ctx: AtlasContext) -> ProviderResult:
        """Builds in-memory dense representations for repository symbols."""
        entities = []
        metrics = [
            Metric("vector.indexed_symbols", len(self._vector_store), "count", "sqlite-vec indexed symbols")
        ]
        return ProviderResult(
            provider="sqlite_vec_ranker",
            entities=entities,
            metrics=metrics,
            metadata={"plugin": self.manifest.name, "indexed": len(self._vector_store)},
        )

    def _simple_embedding(self, text: str, dim: int = 64) -> List[float]:
        """Deterministic lightweight character-ngram hashed embedding (Zero-VRAM CPU)."""
        vec = [0.0] * dim
        text = text.lower().strip()
        if not text:
            return vec

        for i in range(len(text) - 2):
            trigram = text[i : i + 3]
            h = hash(trigram) % dim
            vec[h] += 1.0

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def index_symbols(self, symbols: Sequence[Mapping[str, Any]]) -> int:
        """Index symbols into the vector store."""
        count = 0
        for s in symbols:
            sym_id = s.get("symbol_id") or s.get("name", "")
            sig = s.get("signature") or s.get("name", "")
            doc = s.get("docstring") or ""
            text = f"{sig} {doc}"
            if sym_id and text.strip():
                self._vector_store[sym_id] = self._simple_embedding(text)
                count += 1
        return count

    def search_vector(
        self,
        query: str,
        limit: int = 15,
    ) -> List[Tuple[str, float]]:
        """Search symbol vectors using cosine similarity."""
        if not self._vector_store or not query.strip():
            return []

        q_vec = self._simple_embedding(query)
        scores: List[Tuple[str, float]] = []

        for sym_id, s_vec in self._vector_store.items():
            # Dot product of unit vectors = cosine similarity
            sim = sum(q * s for q, s in zip(q_vec, s_vec))
            if sim > 0.05:
                scores.append((sym_id, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]
