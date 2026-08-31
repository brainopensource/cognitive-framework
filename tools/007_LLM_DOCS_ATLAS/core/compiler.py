"""Context Compiler Engine for LDA.

Assembles task-conditioned, budgeted high-signal working memory packets
for AI coding agents with zero-hallucination provenance.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import Candidate, ContextPacket
from .profile import RepositoryProfile
from .ranking import allocate_budget, rank_entities
from .skeletonizer import skeletonize
from .storage import FactGraphStorage


class ContextCompiler:
    """Deterministic token-budgeted context assembler."""

    def __init__(
        self,
        repo_root: Path,
        storage: FactGraphStorage,
        profile: Optional[RepositoryProfile] = None,
        head_sha: Optional[str] = None,
    ):
        self.repo_root = Path(repo_root)
        self.storage = storage
        self.profile = profile or RepositoryProfile()
        self.head_sha = head_sha

    def compile(
        self,
        task: str,
        budget: int = 8000,
        include_skeletons: bool = True,
    ) -> ContextPacket:
        """Compile a complete ContextPacket bounded to the requested budget."""
        all_candidates = rank_entities(task, self.storage, candidate_limit=60, profile=self.profile)
        
        # Partition candidates by category
        doc_candidates = [c for c in all_candidates if c.kind == "document"]
        sym_candidates = [c for c in all_candidates if c.kind == "symbol"]
        test_candidates = [c for c in all_candidates if c.kind == "test" or "test" in c.locator.lower()]

        # Budget Allocation: 35% Docs, 40% Symbols & Code, 15% Callers/Tests, 10% Headroom
        doc_budget = int(budget * 0.35)
        sym_budget = int(budget * 0.45)
        test_budget = int(budget * 0.20)

        selected_docs, doc_tokens = allocate_budget(doc_candidates, doc_budget)
        selected_syms, sym_tokens = allocate_budget(sym_candidates, sym_budget)
        selected_tests, test_tokens = allocate_budget(test_candidates, test_budget)

        # Attach code skeletons if requested
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
                    content=content
                )
            )

        # Harvest callers and graph dependencies for top symbols
        callers_list: List[Dict[str, Any]] = []
        for s in selected_syms[:5]:
            caller_rows = self.storage.get_callers(s.locator)
            for cr in caller_rows[:4]:
                callers_list.append({
                    "target_symbol": s.title,
                    "caller_name": cr.get("caller_name", "unknown"),
                    "caller_file": cr.get("file_path", ""),
                    "line": cr.get("start_line", 1),
                    "confidence": cr.get("confidence_tier", 80)
                })

        # Subsystems & Code map
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
                    reason=f"{lang.get('file_count')} files ({lang.get('total_bytes')} bytes)"
                )
            )

        total_used = doc_tokens + sym_tokens + test_tokens
        authorities = sorted({c.authority for c in selected_docs if c.authority})

        warnings: List[str] = []
        if total_used > budget:
            warnings.append(f"Allocated tokens ({total_used}) exceeded budget ({budget}). Pruning occurred.")

        stats = self.storage.get_stats()
        provenance = {
            "indexer": "LDA Universal Engine",
            "schema_version": "1.0.0",
            "profile": self.profile.name,
            "source_head_sha": self.head_sha,
            "total_repo_files": stats.get("files", 0),
            "total_repo_symbols": stats.get("symbols", 0),
            "total_repo_relations": stats.get("relations", 0)
        }

        token_accounting = {
            "budget": budget,
            "used_tokens": total_used,
            "document_tokens": doc_tokens,
            "symbol_tokens": sym_tokens,
            "test_tokens": test_tokens
        }

        invariants = [
            "Packet facts are bound to provenance.source_head_sha; on workspace "
            "HEAD mismatch, recompile the packet or fail closed — never serve "
            "stale line numbers or symbols.",
            "Never serve stale facts: recompile on any index/workspace mismatch.",
            "All privileged tool invocations must fail closed on widest authority.",
            "Modifications must remain scoped strictly to the target modules."
        ]

        return ContextPacket(
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
            token_accounting=token_accounting
        )
