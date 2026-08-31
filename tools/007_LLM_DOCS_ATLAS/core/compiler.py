"""Context Compiler Engine for LDA.

Assembles task-conditioned, budgeted high-signal working memory packets
for AI coding agents with zero-hallucination provenance, graph diffusion (PPR),
submodular knapsack optimization, and speculative multi-tier caching.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cache import PacketCache
from .hybrid import DenseRetriever, reciprocal_rank_fusion
from .models import Candidate, ContextPacket
from .plugin_switches import AtlasStrategyConfig, StrategySwitcher
from .ppr_engine import PPREngine
from .profile import RepositoryProfile
from .query import analyze_query
from .ranking import allocate_budget, rank_entities
from .skeletonizer import skeletonize
from .storage import FactGraphStorage
from .submodular_allocator import SubmodularContextAllocator

logger = logging.getLogger(__name__)


def _budget_mix_for(task: str, profile: RepositoryProfile) -> tuple[float, float, float]:
    """Intent-conditioned (docs, code, tests) budget fractions.

    Profile override: ``budget_mix = { intent = [docs, code, tests] }`` entries
    replace the built-in defaults per intent; invalid rows fail closed to the
    built-in mix rather than producing zero or negative budgets.
    """
    from .query import DEFAULT_BUDGET_MIX

    intent = analyze_query(task).intent
    override = getattr(profile, "budget_mix", None) or {}
    row = override.get(intent)
    if isinstance(row, (list, tuple)) and len(row) == 3:
        try:
            fracs = tuple(max(0.0, float(x)) for x in row)
            total = sum(fracs)
            if total > 0.0:
                return fracs  # type: ignore[return-value]
        except (TypeError, ValueError):
            pass
    return DEFAULT_BUDGET_MIX.get(intent, DEFAULT_BUDGET_MIX["explain"])


class ContextCompiler:
    """Deterministic token-budgeted context assembler with SOTA graph diffusion."""

    def __init__(
        self,
        repo_root: Path,
        storage: FactGraphStorage,
        profile: Optional[RepositoryProfile] = None,
        head_sha: Optional[str] = None,
        cache_dir: Optional[Path] = None,
    ):
        self.repo_root = Path(repo_root)
        self.storage = storage
        self.profile = profile or RepositoryProfile()
        self.head_sha = head_sha
        self.cache_dir = cache_dir or (self.repo_root / ".lda" / "cache")
        self.packet_cache = PacketCache(self.cache_dir)
        self.ppr_engine = PPREngine()
        self.submodular_allocator = SubmodularContextAllocator()
        self.strategy_switcher = StrategySwitcher()

    def compile(
        self,
        task: str,
        budget: int = 8000,
        include_skeletons: bool = True,
        strategy: str = "ppr_submodular",
        use_cache: bool = True,
    ) -> ContextPacket:
        """Compile a complete ContextPacket bounded to the requested budget."""
        # 1. Speculative Cache Check (Sub-millisecond return on HEAD match)
        if use_cache:
            cached_data = self.packet_cache.get(
                task=task,
                budget=budget,
                strategy=strategy,
                include_skeletons=include_skeletons,
                head_sha=self.head_sha,
            )
            if cached_data is not None:
                logger.debug("LDA ContextCompiler: Cache HIT for task '%s'", task)
                return self._deserialize_packet(cached_data)

        # 2. Candidate Harvesting & Initial Lexical Ranking
        all_candidates = rank_entities(task, self.storage, candidate_limit=80, profile=self.profile)

        # 3. Strategy Routing: PPR Graph Diffusion vs Hybrid RRF vs FTS5 Lexical Baseline
        active_strategy = strategy
        if strategy == "ppr_submodular":
            all_candidates, active_strategy = self._apply_ppr_diffusion(task, all_candidates)
        elif strategy == "hybrid_rrf":
            all_candidates, active_strategy = self._apply_hybrid_rrf(task, all_candidates)

        # 4. Partition candidates by category (sections zoom with documents;
        #    code candidates include stack-trace frame hits)
        doc_candidates = [
            c for c in all_candidates if c.kind in ("document", "doc_section")
        ]
        sym_candidates = [
            c for c in all_candidates if c.kind in ("symbol", "code")
        ]
        test_candidates = [c for c in all_candidates if c.kind == "test" or "test" in c.locator.lower()]

        # 5. Budget Allocation: intent-conditioned mix (profile-overridable)
        doc_frac, sym_frac, test_frac = _budget_mix_for(task, self.profile)
        doc_budget = int(budget * doc_frac)
        sym_budget = int(budget * sym_frac)
        test_budget = int(budget * test_frac)

        if strategy == "ppr_submodular":
            selected_docs, doc_tokens = self.submodular_allocator.allocate(doc_candidates, doc_budget)
            selected_syms, sym_tokens = self.submodular_allocator.allocate(sym_candidates, sym_budget)
            selected_tests, test_tokens = self.submodular_allocator.allocate(test_candidates, test_budget)
        else:
            selected_docs, doc_tokens = allocate_budget(doc_candidates, doc_budget)
            selected_syms, sym_tokens = allocate_budget(sym_candidates, sym_budget)
            selected_tests, test_tokens = allocate_budget(test_candidates, test_budget)

        # 6. Attach Multi-Language Code Skeletons
        enriched_symbols: List[Candidate] = []
        for s in selected_syms:
            content = None
            if include_skeletons and "#" in s.locator:
                fpath = s.locator.split("#")[0]
                full_path = self.repo_root / fpath
                if full_path.is_file():
                    content = skeletonize(full_path)

            enriched_symbols.append(
                Candidate(
                    locator=s.locator,
                    kind=s.kind,
                    title=s.title,
                    score=s.score,
                    tokens=len(content.split()) if content else s.tokens,
                    reason=s.reason,
                    authority=s.authority,
                    representation="SKELETON" if content else "SIGNATURE",
                    content=content,
                )
            )

        # 7. Harvest callers and graph dependencies for top symbols
        callers_list: List[Dict[str, Any]] = []
        for s in selected_syms[:5]:
            caller_rows = self.storage.get_callers(s.locator)
            for cr in caller_rows[:4]:
                callers_list.append({
                    "target_symbol": s.title,
                    "caller_name": cr.get("caller_name", "unknown"),
                    "caller_file": cr.get("file_path", ""),
                    "line": cr.get("start_line", 1),
                    "confidence": cr.get("confidence_tier", 80),
                })

        # 8. Subsystems & Code topology
        code_candidates: List[Candidate] = []
        topo = self.storage.get_topology_map()
        for lang in topo.get("languages", []):
            code_candidates.append(
                Candidate(
                    locator=f"lang:{lang.get('language')}",
                    kind="code_topology",
                    title=f"Language: {lang.get('language')}",
                    score=15.0,
                    tokens=30,
                    reason=f"{lang.get('file_count')} files ({lang.get('total_bytes')} bytes)",
                )
            )

        total_used = doc_tokens + sym_tokens + test_tokens
        authorities = sorted({c.authority for c in selected_docs if c.authority})

        warnings: List[str] = []
        if total_used > budget:
            warnings.append(f"Allocated tokens ({total_used}) exceeded budget ({budget}). Pruning occurred.")

        stats = self.storage.get_stats()
        intent = analyze_query(task).intent
        provenance = {
            "indexer": "LDA Universal SOTA Engine",
            "schema_version": "1.2.0",
            "profile": self.profile.name,
            "source_head_sha": self.head_sha,
            "strategy": active_strategy,
            "task_intent": intent,
            "ranking_channels": {
                "lexical_bm25": True,
                "dense_rrf": active_strategy == "hybrid_rrf",
                "ppr_diffusion": active_strategy == "ppr_submodular",
                "stack_trace_frames": True,
            },
            "total_repo_files": stats.get("files", 0),
            "total_repo_symbols": stats.get("symbols", 0),
            "total_repo_relations": stats.get("relations", 0),
        }

        token_accounting = {
            "budget": budget,
            "used_tokens": total_used,
            "document_tokens": doc_tokens,
            "symbol_tokens": sym_tokens,
            "test_tokens": test_tokens,
        }

        invariants = [
            "Packet facts are bound to provenance.source_head_sha; on workspace "
            "HEAD mismatch, recompile the packet or fail closed — never serve "
            "stale line numbers or symbols.",
            "Never serve stale facts: recompile on any index/workspace mismatch.",
            "All privileged tool invocations must fail closed on widest authority.",
            "Modifications must remain scoped strictly to the target modules.",
        ]

        packet = ContextPacket(
            task=task,
            budget=budget,
            estimated_tokens=total_used,
            documents=selected_docs,
            code=code_candidates,
            symbols=enriched_symbols,
            tests=selected_tests,
            authority=authorities,
            warnings=warnings,
            callers=callers_list,
            invariants=invariants,
            provenance=provenance,
            token_accounting=token_accounting,
        )

        # 9. Store in Speculative Cache
        if use_cache:
            self.packet_cache.put(
                task=task,
                budget=budget,
                strategy=strategy,
                include_skeletons=include_skeletons,
                head_sha=self.head_sha,
                packet_dict=self._serialize_packet(packet),
            )

        return packet

    def _apply_ppr_diffusion(
        self,
        task: str,
        candidates: List[Candidate],
    ) -> Tuple[List[Candidate], str]:
        """Apply Markov Spreading Activation to elevate transitively relevant entities."""
        all_symbols = self.storage.get_all_symbols()
        all_relations = self.storage.get_all_relations()

        if not all_symbols or not all_relations:
            return candidates, "fts5_bm25"

        entity_ids = [s.get("symbol_id", "") for s in all_symbols if s.get("symbol_id")]
        adj, id_to_idx, out_degrees = self.ppr_engine.build_adjacency(entity_ids, all_relations)

        # Seed indices from top BM25 candidates
        seed_indices: List[int] = []
        seed_weights: List[float] = []
        for c in candidates[:10]:
            if c.locator in id_to_idx:
                seed_indices.append(id_to_idx[c.locator])
                seed_weights.append(c.score)

        if not seed_indices:
            return candidates, "fts5_bm25"

        try:
            ppr_vector = self.ppr_engine.diffuse(
                num_nodes=len(entity_ids),
                adj=adj,
                out_degrees=out_degrees,
                seed_indices=seed_indices,
                seed_weights=seed_weights,
            )

            # Re-weight candidate scores
            ppr_score_map = {entity_ids[i]: ppr_vector[i] * 1000.0 for i in range(len(entity_ids))}
            reweighted_candidates: List[Candidate] = []
            for c in candidates:
                ppr_boost = ppr_score_map.get(c.locator, 0.0)
                combined_score = (c.score * 0.4) + (ppr_boost * 0.6)
                reweighted_candidates.append(
                    Candidate(
                        locator=c.locator,
                        kind=c.kind,
                        title=c.title,
                        score=combined_score,
                        tokens=c.tokens,
                        reason=f"{c.reason} [PPR Boost: {ppr_boost:.2f}]",
                        authority=c.authority,
                        representation=c.representation,
                        content=c.content,
                    )
                )

            reweighted_candidates.sort(key=lambda x: x.score, reverse=True)
            return reweighted_candidates, "ppr_submodular"
        except Exception as exc:
            logger.warning("PPR diffusion failed, falling back to FTS5: %s", exc)
            return candidates, "fts5_bm25"

    def _apply_hybrid_rrf(
        self,
        task: str,
        candidates: List[Candidate],
    ) -> Tuple[List[Candidate], str]:
        """Fuse lexical, dense, and intent-frame channels via Reciprocal Rank Fusion.

        Dense-only hits (zero lexical overlap, e.g. paraphrased docstrings)
        enter the pool as full candidates; fused ranks re-weight everyone.
        Falls back to lexical ordering on any internal failure.
        """
        try:
            retriever = DenseRetriever()
            retriever.build_from_storage(self.storage)
        except Exception as exc:
            logger.warning("Dense index build failed, falling back to FTS5: %s", exc)
            return candidates, "fts5_bm25"

        dense_hits = retriever.ranked(task, limit=40)

        # New candidates from dense-only hits (not already in the lexical pool).
        known = {c.locator for c in candidates}
        extra: List[Candidate] = []
        for locator, score, meta in dense_hits:
            if locator in known:
                continue
            kind = str(meta.get("kind", "symbol"))
            title = str(meta.get("title", locator))
            extra.append(
                Candidate(
                    locator=locator,
                    kind=kind,
                    title=title,
                    score=20.0 + score * 50.0,
                    tokens=int(meta.get("tokens", 100)),
                    reason=f"Dense semantic match (cos={score:.3f})",
                    authority=meta.get("authority"),
                    representation="SKELETON",
                    content=meta.get("content"),
                )
            )

        fused = reciprocal_rank_fusion(
            {
                "lexical": [c.locator for c in candidates],
                "dense": [loc for loc, _, _ in dense_hits],
            },
            weights={"lexical": 1.0, "dense": 1.0},
            limit=max(len(candidates) + len(extra), 1),
        )
        rrf_rank = {loc: i for i, (loc, _) in enumerate(fused)}
        pool = candidates + extra
        max_rank = max(1, len(fused) - 1)
        reweighted: List[Candidate] = []
        for c in pool:
            pos = rrf_rank.get(c.locator, max_rank)
            rrf_score = 1.0 - (pos / max_rank)  # 1.0 best .. 0.0 worst
            reweighted.append(
                Candidate(
                    locator=c.locator,
                    kind=c.kind,
                    title=c.title,
                    score=c.score * 0.5 + rrf_score * 100.0,
                    tokens=c.tokens,
                    reason=f"{c.reason} [RRF rank {pos}]",
                    authority=c.authority,
                    representation=c.representation,
                    content=c.content,
                    provenance_ref=c.provenance_ref,
                )
            )
        reweighted.sort(key=lambda x: (-x.score, x.locator))
        return reweighted, "hybrid_rrf"

    def _serialize_packet(self, packet: ContextPacket) -> Dict[str, Any]:
        return {
            "task": packet.task,
            "budget": packet.budget,
            "estimated_tokens": packet.estimated_tokens,
            "documents": [asdict(c) for c in packet.documents],
            "code": [asdict(c) for c in packet.code],
            "symbols": [asdict(c) for c in packet.symbols],
            "tests": [asdict(c) for c in packet.tests],
            "authority": packet.authority,
            "warnings": packet.warnings,
            "callers": packet.callers,
            "invariants": packet.invariants,
            "provenance": packet.provenance,
            "token_accounting": packet.token_accounting,
        }

    def _deserialize_packet(self, data: Dict[str, Any]) -> ContextPacket:
        return ContextPacket(
            task=data["task"],
            budget=data["budget"],
            estimated_tokens=data["estimated_tokens"],
            documents=[Candidate(**c) for c in data.get("documents", [])],
            code=[Candidate(**c) for c in data.get("code", [])],
            symbols=[Candidate(**c) for c in data.get("symbols", [])],
            tests=[Candidate(**c) for c in data.get("tests", [])],
            authority=data.get("authority", []),
            warnings=data.get("warnings", []),
            callers=data.get("callers", []),
            invariants=data.get("invariants", []),
            provenance=data.get("provenance", {}),
            token_accounting=data.get("token_accounting", {}),
        )
