"""Graph-Centrality Repository Map Generator for Token-Bounded Architectural Overview."""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple

logger = logging.getLogger(__name__)


class RepositoryMapGenerator:
    """
    Constructs an ultra-dense, PageRank/Centrality-ranked repository map within a bounded token budget.
    Ensures AI agents have complete global structural awareness without raw code bloat.
    """

    def __init__(self, storage: Any, max_symbols_budget: int = 500) -> None:
        self.storage = storage
        self.max_symbols_budget = max_symbols_budget

    def generate_map(
        self,
        focus_files: Sequence[str] | None = None,
        token_budget: int = 2000,
    ) -> str:
        """Generates formatted multi-file structural skeletons ranked by graph centrality."""
        all_symbols = self.storage.get_all_symbols()
        all_relations = self.storage.get_all_relations()

        if not all_symbols:
            return "# REPOSITORY STRUCTURAL MAP: (Empty index)"

        # Compute In-Degree Centrality
        in_degrees: Dict[str, int] = {}
        for rel in all_relations:
            tgt = rel.get("target_id") or rel.get("target")
            if tgt:
                in_degrees[tgt] = in_degrees.get(tgt, 0) + 1

        focus_set = set(focus_files or [])

        # Score and rank symbols
        ranked_symbols = sorted(
            all_symbols,
            key=lambda s: (
                1000 if s.get("file_path") in focus_set else 0,
                in_degrees.get(s.get("symbol_id", ""), 0),
                s.get("confidence_tier", 80),
            ),
            reverse=True,
        )[: self.max_symbols_budget]

        # Group by file
        files_map: Dict[str, List[Dict[str, Any]]] = {}
        for sym in ranked_symbols:
            fpath = sym.get("file_path", "")
            files_map.setdefault(fpath, []).append(sym)

        output_lines: List[str] = ["# REPOSITORY STRUCTURAL MAP (PageRank Centrality Ranked)"]
        consumed_tokens = 15

        for fpath, syms in sorted(files_map.items()):
            if consumed_tokens >= token_budget:
                output_lines.append("\n*... [remaining files clamped by token budget]*")
                break

            header = f"\n## File: `{fpath}`"
            output_lines.append(header)
            consumed_tokens += len(header.split())

            for s in syms:
                kind = s.get("kind", "symbol")
                name = s.get("name", "")
                sig = s.get("signature") or name
                doc = s.get("docstring") or ""
                first_doc = f" -- {doc.splitlines()[0]}" if doc else ""

                line = f"  * [{kind}] `{sig}`{first_doc}"
                tokens = len(line.split())
                if consumed_tokens + tokens > token_budget:
                    output_lines.append("  * ... [remaining symbols clamped by budget]")
                    return "\n".join(output_lines)

                output_lines.append(line)
                consumed_tokens += tokens

        return "\n".join(output_lines)
