"""Personalized PageRank (PPR) Graph Diffusion Engine for LDA.

Implements stationary Markov diffusion over heterogeneous code-document relations
to enable multi-hop associative recall (HippoRAG) in single matrix operations.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping, Sequence, Set, Tuple

logger = logging.getLogger(__name__)


class PPREngine:
    """High-performance sparse graph diffusion engine for code knowledge graphs."""

    def __init__(
        self,
        gamma: float = 0.15,
        max_iter: int = 40,
        tol: float = 1e-6,
    ) -> None:
        self.gamma = gamma
        self.max_iter = max_iter
        self.tol = tol

    def build_adjacency(
        self,
        entity_ids: Sequence[str],
        relations: Sequence[Mapping[str, Any]],
        relation_weights: Mapping[str, float] | None = None,
    ) -> Tuple[Dict[int, List[Tuple[int, float]]], Dict[str, int], Dict[int, float]]:
        """Construct an adjacency list and out-degree map from entities and relations."""
        id_to_idx = {eid: idx for idx, eid in enumerate(entity_ids)}
        weights_map = relation_weights or {
            "calls": 1.0,
            "defines": 0.8,
            "implements": 1.1,
            "inherits": 0.9,
            "tests": 1.2,
            "falsifies": 1.2,
            "specified_by": 1.1,
            "documents": 0.8,
            "imports": 0.5,
            "references": 0.6,
        }

        adj: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(len(entity_ids))}
        out_degrees: Dict[int, float] = {i: 0.0 for i in range(len(entity_ids))}

        for rel in relations:
            src = rel.get("source_id") or rel.get("source")
            tgt = rel.get("target_id") or rel.get("target")
            kind = rel.get("kind", "references")

            if src in id_to_idx and tgt in id_to_idx:
                u, v = id_to_idx[src], id_to_idx[tgt]
                weight = weights_map.get(kind, 0.5)
                adj[u].append((v, weight))
                out_degrees[u] += weight

        return adj, id_to_idx, out_degrees

    def diffuse(
        self,
        num_nodes: int,
        adj: Dict[int, List[Tuple[int, float]]],
        out_degrees: Dict[int, float],
        seed_indices: Sequence[int],
        seed_weights: Sequence[float] | None = None,
    ) -> List[float]:
        """Execute Power Iteration Markov diffusion over the graph."""
        if num_nodes == 0 or not seed_indices:
            return [0.0] * num_nodes

        # Construct personalization distribution p_q
        p_q = [0.0] * num_nodes
        if seed_weights is None:
            w_val = 1.0 / max(len(seed_indices), 1)
            for idx in seed_indices:
                if 0 <= idx < num_nodes:
                    p_q[idx] = w_val
        else:
            total_w = sum(seed_weights)
            denom = total_w if total_w > 0 else 1.0
            for idx, w in zip(seed_indices, seed_weights):
                if 0 <= idx < num_nodes:
                    p_q[idx] = w / denom

        # Try vectorized numpy/scipy if available for sub-millisecond execution
        try:
            return self._diffuse_numpy(num_nodes, adj, out_degrees, p_q)
        except Exception:
            return self._diffuse_pure_python(num_nodes, adj, out_degrees, p_q)

    def _diffuse_numpy(
        self,
        num_nodes: int,
        adj: Dict[int, List[Tuple[int, float]]],
        out_degrees: Dict[int, float],
        p_q_list: List[float],
    ) -> List[float]:
        import numpy as np
        import scipy.sparse as sp

        rows, cols, data = [], [], []
        for u, neighbors in adj.items():
            deg = out_degrees.get(u, 0.0)
            if deg > 0:
                for v, weight in neighbors:
                    rows.append(u)
                    cols.append(v)
                    data.append(weight / deg)

        P = sp.csr_matrix((data, (rows, cols)), shape=(num_nodes, num_nodes), dtype=np.float64)
        P_T = P.transpose().tocsr()

        p_q = np.array(p_q_list, dtype=np.float64)
        r = p_q.copy()
        nonzero_degrees = np.array([out_degrees.get(i, 0.0) > 0 for i in range(num_nodes)])
        dangling_nodes = ~nonzero_degrees

        for _ in range(self.max_iter):
            r_prev = r.copy()
            dangling_sum = float(np.sum(r_prev[dangling_nodes]))
            r = (1.0 - self.gamma) * (P_T.dot(r_prev) + dangling_sum * p_q) + self.gamma * p_q
            if float(np.sum(np.abs(r - r_prev))) < self.tol:
                break

        return r.tolist()

    def _diffuse_pure_python(
        self,
        num_nodes: int,
        adj: Dict[int, List[Tuple[int, float]]],
        out_degrees: Dict[int, float],
        p_q: List[float],
    ) -> List[float]:
        r = list(p_q)
        gamma = self.gamma
        one_minus_gamma = 1.0 - gamma

        for _ in range(self.max_iter):
            r_next = [gamma * p_q[i] for i in range(num_nodes)]
            dangling_sum = 0.0

            for u in range(num_nodes):
                deg = out_degrees.get(u, 0.0)
                if deg == 0.0:
                    dangling_sum += r[u]
                else:
                    prob_u = r[u] / deg
                    for v, weight in adj.get(u, []):
                        r_next[v] += one_minus_gamma * prob_u * weight

            if dangling_sum > 0.0:
                for i in range(num_nodes):
                    r_next[i] += one_minus_gamma * dangling_sum * p_q[i]

            diff = sum(abs(r_next[i] - r[i]) for i in range(num_nodes))
            r = r_next
            if diff < self.tol:
                break

        return r
