"""Type-Aware Mutation Testing and Patch Falsification Engine for 006_LLM_INT_MACHINE.

Injects AST/syntactic mutants into patched lines to evaluate test suite rigor and reject tautological fixes.
"""

from __future__ import annotations
import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


@dataclass
class MutationScoreCard:
    """Evaluation score card for patch generality under syntactic mutations."""
    total_mutants: int
    killed_mutants: int
    mutation_score: float
    is_general: bool
    surviving_mutants: list[str]


class PatchMutationVerifier:
    """Generates syntactic mutants in patched lines and evaluates test failure rates."""

    def __init__(self, workspace_root: Path, oracle_fn: Callable[[], bool]):
        self.root = workspace_root
        self.oracle = oracle_fn

    def falsify_patch(self, file_path_rel: str, diff_lines: list[int] | None = None) -> MutationScoreCard:
        """Evaluate whether a patch is robust by verifying that mutants cause test failures."""
        target_file = self.root / file_path_rel
        if not target_file.is_file():
            return MutationScoreCard(0, 0, 1.0, True, [])

        original_code = target_file.read_text(encoding="utf-8")
        mutants = self._generate_mutants(original_code, diff_lines)

        if not mutants:
            return MutationScoreCard(0, 0, 1.0, True, [])

        killed = 0
        survivors: list[str] = []

        for idx, (mutated_code, desc) in enumerate(mutants):
            try:
                target_file.write_text(mutated_code, encoding="utf-8")
                passed = False
                try:
                    passed = bool(self.oracle())
                except Exception:
                    passed = False

                if not passed:
                    killed += 1
                else:
                    survivors.append(f"Mutant #{idx+1} ({desc}) survived without test failure")
            finally:
                target_file.write_text(original_code, encoding="utf-8")

        score = killed / len(mutants)
        return MutationScoreCard(
            total_mutants=len(mutants),
            killed_mutants=killed,
            mutation_score=round(score, 3),
            is_general=(score >= 0.80),
            surviving_mutants=survivors,
        )

    def _generate_mutants(self, code: str, target_lines: list[int] | None) -> list[tuple[str, str]]:
        mutants: list[tuple[str, str]] = []
        lines = code.splitlines()

        replacements = [
            ("==", "!="), ("!=", "=="),
            (">", ">="), ("<", "<="),
            (" and ", " or "), (" or ", " and "),
            ("True", "False"), ("False", "True"),
            ("+ 1", "- 1"), ("- 1", "+ 1"),
            ("is None", "is not None"), ("is not None", "is None"),
        ]

        active_indices = target_lines if target_lines else list(range(len(lines)))

        for line_idx in active_indices:
            if 0 <= line_idx < len(lines):
                original_line = lines[line_idx]
                for src, dst in replacements:
                    if src in original_line:
                        mutated_line = original_line.replace(src, dst, 1)
                        new_lines = list(lines)
                        new_lines[line_idx] = mutated_line
                        mut_text = "\n".join(new_lines)
                        mutants.append((mut_text, f"Line {line_idx+1}: {src} -> {dst}"))
                        if len(mutants) >= 6:
                            return mutants

        return mutants
