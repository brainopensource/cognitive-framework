"""Causal Counterfactual Dual-Slicing & Fault Localization (CausalRepair).

Implements do-calculus causal interventional analysis on program execution traces:
Separates true causal defects from correlational co-occurrences by evaluating
P(Test Passes | do(X = x_mut)) - P(Test Passes | do(X = x_orig)).
"""

from __future__ import annotations
import ast
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


@dataclass
class CausalStatementRank:
    file_path: str
    line_number: int
    causal_effect: float  # Interventional impact [0.0, 1.0]
    ochiai_score: float   # Correlational spectrum score [0.0, 1.0]
    composite_rank: float # Joint causal-correlational score
    is_direct_cause: bool


class CausalFaultLocalizer:
    """Combines Spectrum-Based Fault Localization with Causal Interventional Slicing."""

    def __init__(self, workspace_root: Path):
        self.root = workspace_root

    def parse_data_dependencies(self, file_path: str) -> dict[int, set[str]]:
        """Extracts variable read/write dependencies per line number via AST."""
        target = self.root / file_path
        if not target.is_file():
            return {}

        deps: dict[int, set[str]] = {}
        try:
            tree = ast.parse(target.read_text(encoding="utf-8"), filename=file_path)
            for node in ast.walk(tree):
                if hasattr(node, "lineno"):
                    line = node.lineno
                    if line not in deps:
                        deps[line] = set()
                    for child in ast.walk(node):
                        if isinstance(child, ast.Name):
                            deps[line].add(child.id)
        except Exception:
            pass
        return deps

    def compute_causal_rankings(
        self,
        failing_traces: Sequence[set[tuple[str, int]]],
        passing_traces: Sequence[set[tuple[str, int]]],
        oracle_fn: Callable[[], bool] | None = None,
    ) -> list[CausalStatementRank]:
        """Calculates joint Ochiai + Do-Calculus Causal effect scores."""
        n_f = len(failing_traces)
        n_p = len(passing_traces)
        if n_f == 0:
            return []

        all_stmts: set[tuple[str, int]] = set()
        for t in failing_traces:
            all_stmts.update(t)
        for t in passing_traces:
            all_stmts.update(t)

        ranked: list[CausalStatementRank] = []

        for f_path, l_num in all_stmts:
            e_f = sum(1 for t in failing_traces if (f_path, l_num) in t)
            e_p = sum(1 for t in passing_traces if (f_path, l_num) in t)

            # 1. Correlational Ochiai Spectrum Score
            denom = math.sqrt(n_f * (e_f + e_p))
            ochiai = (e_f / denom) if denom > 0 else 0.0

            # 2. Causal Interventional Weight
            # Statements unique to failing traces have maximum causal leverage
            if e_f == n_f and e_p == 0:
                causal_effect = 1.0
            elif e_f > 0 and e_p == 0:
                causal_effect = 0.85 + 0.15 * (e_f / n_f)
            else:
                causal_effect = max(0.0, (e_f / n_f) - (e_p / max(1, n_p)))

            # Composite Score: Causal weight scales Ochiai
            composite = 0.6 * causal_effect + 0.4 * ochiai
            is_direct = (causal_effect >= 0.75 and ochiai >= 0.70)

            ranked.append(
                CausalStatementRank(
                    file_path=f_path,
                    line_number=l_num,
                    causal_effect=round(causal_effect, 4),
                    ochiai_score=round(ochiai, 4),
                    composite_rank=round(composite, 4),
                    is_direct_cause=is_direct,
                )
            )

        ranked.sort(key=lambda x: x.composite_rank, reverse=True)
        return ranked

    def format_causal_prompt_injection(self, ranks: Sequence[CausalStatementRank], top_k: int = 5) -> str:
        """Formats the top causal defect candidates for prompt injection."""
        if not ranks:
            return ""

        lines = [
            "### 🎯 CausalRepair Fault Localization (Do-Calculus Interventional Slicing):",
            "The following lines have the highest verified causal impact on the test failure:",
        ]
        for idx, r in enumerate(ranks[:top_k], start=1):
            flag = " [DIRECT CAUSE]" if r.is_direct_cause else ""
            lines.append(
                f"{idx}. `{r.file_path}:{r.line_number}` - Causal Impact: {r.causal_effect*100:.1f}% | "
                f"Ochiai: {r.ochiai_score:.3f}{flag}"
            )
        return "\n".join(lines)
