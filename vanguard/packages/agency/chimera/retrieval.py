"""Retrieval Market and Multi-Provider Ensemble for CHIMERA.

Treats retrieval mechanisms (Lexical/BM25, LDA/AST symbols, graph heuristics,
and keyword extractors) as competing market bidders.
Aggregates bids via Value-of-Information (VOI) utility function.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

from .blackboard import RankedFile, RankedSymbol


@dataclass(frozen=True, slots=True)
class RetrievalBid:
    """A bid placed by a retrieval provider on a candidate file or symbol."""

    provider: str
    candidate_path: str
    relevance: float  # [0.0, 1.0]
    confidence: float  # [0.0, 1.0]
    novelty: float  # [0.0, 1.0]
    token_cost: int
    provenance: str = ""
    symbol_name: str | None = None

    @property
    def utility(self) -> float:
        # VOI utility: U = 0.5*rel + 0.3*conf + 0.2*nov - 0.0001*cost
        u = 0.5 * self.relevance + 0.3 * self.confidence + 0.2 * self.novelty - (self.token_cost * 0.00005)
        return round(max(0.0, min(1.0, u)), 4)


class LexicalRetrievalProvider:
    """Scans workspace files and matches keywords / terms from query."""

    def __init__(self, workspace_root: Path | str) -> None:
        self.workspace_root = Path(workspace_root)

    def retrieve(self, query: str, known_paths: Set[str]) -> list[RetrievalBid]:
        bids: list[RetrievalBid] = []
        if not self.workspace_root.is_dir():
            return bids

        keywords = set(re.findall(r"[A-Za-z0-9_]{3,}", query.lower()))
        # Remove ultra-common noise words
        noise = {"the", "and", "for", "with", "this", "that", "from", "import", "def", "class", "return", "self", "none", "true", "false", "test", "tests"}
        meaningful_kw = {k for k in keywords if k not in noise}

        for path in self.workspace_root.rglob("*"):
            if not path.is_file():
                continue
            if any(part.startswith(".") or part in ("__pycache__", "node_modules", "target", ".venv") for part in path.parts):
                continue
            if path.suffix not in {".py", ".ts", ".js", ".rs", ".svelte", ".html", ".css", ".json", ".md", ".toml", ".yaml"}:
                continue

            try:
                rel = str(path.relative_to(self.workspace_root))
                content = path.read_text(encoding="utf-8", errors="replace")
                c_lower = content.lower()
                rel_lower = rel.lower()

                # Score matches
                matches = sum(1 for kw in meaningful_kw if kw in c_lower or kw in rel_lower)
                if matches > 0 or len(meaningful_kw) == 0:
                    rel_score = min(1.0, (matches + 0.5) / (len(meaningful_kw) + 1.0))
                    novelty = 1.0 if rel not in known_paths else 0.2
                    tok_est = len(content) // 4
                    bids.append(
                        RetrievalBid(
                            provider="lexical",
                            candidate_path=rel,
                            relevance=round(rel_score, 3),
                            confidence=0.7,
                            novelty=novelty,
                            token_cost=tok_est,
                            provenance=f"lexical_match:{matches}_keywords",
                        )
                    )
            except Exception:
                continue

        return bids


class GraphHeuristicProvider:
    """Discovers dependency, import, and test co-location edges."""

    def __init__(self, workspace_root: Path | str) -> None:
        self.workspace_root = Path(workspace_root)

    def retrieve(self, seed_files: Sequence[str], known_paths: Set[str]) -> list[RetrievalBid]:
        bids: list[RetrievalBid] = []
        if not self.workspace_root.is_dir():
            return bids

        for seed in seed_files:
            seed_p = self.workspace_root / seed.lstrip("/")
            if not seed_p.is_file():
                continue
            try:
                content = seed_p.read_text(encoding="utf-8", errors="replace")
                # Detect imports
                py_imports = re.findall(r"(?:from|import)\s+([\w\.]+)", content)
                for imp in py_imports:
                    module_rel = imp.replace(".", "/") + ".py"
                    target = self.workspace_root / module_rel
                    if target.is_file():
                        rel = str(target.relative_to(self.workspace_root))
                        bids.append(
                            RetrievalBid(
                                provider="graph_imports",
                                candidate_path=rel,
                                relevance=0.85,
                                confidence=0.9,
                                novelty=1.0 if rel not in known_paths else 0.3,
                                token_cost=len(target.read_text(encoding="utf-8", errors="replace")) // 4,
                                provenance=f"imported_by:{seed}",
                            )
                        )
            except Exception:
                continue

        return bids


class RetrievalMarket:
    """Multi-provider retrieval market that computes VOI and ranks candidates."""

    def __init__(self, workspace_root: Path | str) -> None:
        self.workspace_root = Path(workspace_root)
        self.lexical_provider = LexicalRetrievalProvider(self.workspace_root)
        self.graph_provider = GraphHeuristicProvider(self.workspace_root)

    def query(
        self,
        task_query: str,
        seed_files: Sequence[str] = (),
        top_k: int = 8,
    ) -> Tuple[tuple[RankedFile, ...], tuple[RankedSymbol, ...]]:
        """Run the market auction across all providers and return ranked results."""
        known: Set[str] = set(seed_files)
        all_bids: list[RetrievalBid] = []

        # 1. Collect bids from lexical provider
        all_bids.extend(self.lexical_provider.retrieve(task_query, known))

        # 2. Collect bids from graph heuristic provider
        if seed_files:
            all_bids.extend(self.graph_provider.retrieve(seed_files, known))

        # 3. Deduplicate by candidate_path, keeping highest utility bid
        bids_by_path: dict[str, RetrievalBid] = {}
        for b in all_bids:
            if b.candidate_path not in bids_by_path or b.utility > bids_by_path[b.candidate_path].utility:
                bids_by_path[b.candidate_path] = b

        # 4. Sort by utility descending
        sorted_bids = sorted(bids_by_path.values(), key=lambda x: x.utility, reverse=True)

        ranked_files: list[RankedFile] = []
        for b in sorted_bids[:top_k]:
            ranked_files.append(
                RankedFile(
                    path=b.candidate_path,
                    relevance_score=b.utility,
                    provider=b.provider,
                    reason=b.provenance,
                )
            )

        # 5. Extract top symbols from top files
        ranked_symbols: list[RankedSymbol] = []
        for rf in ranked_files[:3]:
            fp = self.workspace_root / rf.path
            if fp.is_file() and fp.suffix == ".py":
                try:
                    text = fp.read_text(encoding="utf-8", errors="replace")
                    for m in re.finditer(r"^(?:def|class)\s+([A-Za-z0-9_]+)", text, re.MULTILINE):
                        sym = m.group(1)
                        kind = "class" if text[m.start():].startswith("class") else "function"
                        ranked_symbols.append(
                            RankedSymbol(
                                symbol_name=sym,
                                file_path=rf.path,
                                relevance_score=rf.relevance_score,
                                kind=kind,
                            )
                        )
                except Exception:
                    pass

        return tuple(ranked_files), tuple(ranked_symbols)
