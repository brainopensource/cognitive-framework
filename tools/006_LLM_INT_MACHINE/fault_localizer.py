"""Spectrum-Based Fault Localization (SBFL) Engine for 006_LLM_INT_MACHINE.

Computes statement-level Ochiai, Tarantula, and DStar suspiciousness coefficients from execution traces.
"""

from __future__ import annotations
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping, Sequence, Set, Tuple


@dataclass
class LineSuspiciousness:
    """Statement-level fault suspiciousness ranking record."""
    file_path: str
    line_number: int
    ochiai_score: float
    tarantula_score: float
    dstar_score: float
    failing_executions: int
    passing_executions: int


class SBFLEngine:
    """Computes SBFL suspiciousness coefficients from passing and failing execution traces."""

    def __init__(self, workspace_root: Path):
        self.root = workspace_root
        self.current_trace: set[tuple[str, int]] = set()

    def _trace_hook(self, frame, event, arg):
        if event == "line":
            filename = frame.f_code.co_filename
            if str(self.root) in filename and not any(p in filename for p in [".git", "__pycache__", ".pytest_cache"]):
                try:
                    rel_p = Path(filename).relative_to(self.root).as_posix()
                    self.current_trace.add((rel_p, frame.f_lineno))
                except ValueError:
                    pass
        return self._trace_hook

    def record_execution(self, test_callable: Callable[[], bool]) -> tuple[bool, set[tuple[str, int]]]:
        """Execute callable while capturing line statement execution traces."""
        self.current_trace = set()
        old_trace = sys.gettrace()
        sys.settrace(self._trace_hook)
        passed = False
        try:
            passed = bool(test_callable())
        except Exception:
            passed = False
        finally:
            sys.settrace(old_trace)
        return passed, set(self.current_trace)

    def compute_rankings(
        self,
        coverage_failing: Sequence[set[tuple[str, int]]],
        coverage_passing: Sequence[set[tuple[str, int]]],
    ) -> list[LineSuspiciousness]:
        """Calculate Ochiai, Tarantula, and DStar scores across statement sets."""
        n_f = len(coverage_failing)
        n_p = len(coverage_passing)
        
        if n_f == 0:
            return []

        all_lines: set[tuple[str, int]] = set()
        for c in coverage_failing:
            all_lines.update(c)
        for c in coverage_passing:
            all_lines.update(c)

        results: list[LineSuspiciousness] = []

        for f_path, l_num in all_lines:
            e_f = sum(1 for cov in coverage_failing if (f_path, l_num) in cov)
            e_p = sum(1 for cov in coverage_passing if (f_path, l_num) in cov)

            # Ochiai: e_f / sqrt(n_f * (e_f + e_p))
            denom_ochiai = math.sqrt(n_f * (e_f + e_p))
            ochiai = (e_f / denom_ochiai) if denom_ochiai > 0 else 0.0

            # Tarantula: (e_f / n_f) / ((e_f / n_f) + (e_p / n_p))
            t_f = e_f / n_f
            t_p = (e_p / n_p) if n_p > 0 else 0.0
            tarantula = (t_f / (t_f + t_p)) if (t_f + t_p) > 0 else 0.0

            # DStar: e_f^2 / (e_p + (n_f - e_f))
            denom_dstar = e_p + (n_f - e_f)
            dstar = (e_f ** 2 / denom_dstar) if denom_dstar > 0 else 0.0

            results.append(
                LineSuspiciousness(
                    file_path=f_path,
                    line_number=l_num,
                    ochiai_score=round(ochiai, 4),
                    tarantula_score=round(tarantula, 4),
                    dstar_score=round(dstar, 4),
                    failing_executions=e_f,
                    passing_executions=e_p,
                )
            )

        results.sort(key=lambda x: (x.ochiai_score, x.dstar_score), reverse=True)
        return results

    def format_for_prompt(self, rankings: list[LineSuspiciousness], top_k: int = 5) -> str:
        """Render top-k suspicious statements for prompt Layer 3 injection."""
        if not rankings:
            return ""
        lines = ["[SBFL Fault Localization: Top Suspicious Statements]"]
        for r in rankings[:top_k]:
            lines.append(f"- {r.file_path}:{r.line_number} (Ochiai: {r.ochiai_score:.3f} | Failing Runs: {r.failing_executions}/{r.failing_executions + r.passing_executions})")
        return "\n".join(lines)
