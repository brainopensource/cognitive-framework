"""Symbolic Cortex for CHIMERA.

Provides exact constraint solving, equation solving, AST syntax verification,
and mathematical invariant extraction without invoking generative LLMs.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import json
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True, slots=True)
class SyntaxCheckResult:
    valid: bool
    language: str
    error_message: str | None = None
    line_number: int | None = None


@dataclass(frozen=True, slots=True)
class InvariantSolution:
    success: bool
    solution_text: str
    extracted_equations: tuple[str, ...]
    variable_assignments: Mapping[str, Any]


class SymbolicCortex:
    """Deterministic symbolic and AST reasoning engine."""

    @classmethod
    def validate_code_syntax(
        cls,
        code_content: str,
        file_path: str = "snippet.py",
    ) -> SyntaxCheckResult:
        """Validate code syntax across Python, JS/TS, Rust, and JSON."""
        # Determine language from extension
        ext = file_path.rsplit(".", 1)[-1].lower() if "." in file_path else "py"

        if ext == "py":
            try:
                ast.parse(code_content, filename=file_path)
                return SyntaxCheckResult(valid=True, language="python")
            except SyntaxError as exc:
                return SyntaxCheckResult(
                    valid=False,
                    language="python",
                    error_message=f"{exc.msg} at line {exc.lineno}: {exc.text}",
                    line_number=exc.lineno,
                )

        elif ext == "json":
            try:
                json.loads(code_content)
                return SyntaxCheckResult(valid=True, language="json")
            except json.JSONDecodeError as exc:
                return SyntaxCheckResult(
                    valid=False,
                    language="json",
                    error_message=f"JSONDecodeError: {exc.msg} at line {exc.lineno}",
                    line_number=exc.lineno,
                )

        elif ext in ("js", "ts", "rs", "svelte", "html"):
            # Check balanced brackets, braces, parentheses
            stack: list[tuple[str, int]] = []
            matching = {")": "(", "}": "{", "]": "["}
            for line_idx, line in enumerate(code_content.splitlines(), start=1):
                # Skip comments and strings approximately
                cleaned = re.sub(r'//.*$|/\*.*?\*/|".*?"|\'.*?\'|`.*?`', '', line)
                for ch in cleaned:
                    if ch in "({[":
                        stack.append((ch, line_idx))
                    elif ch in matching:
                        if not stack or stack[-1][0] != matching[ch]:
                            return SyntaxCheckResult(
                                valid=False,
                                language=ext,
                                error_message=f"Unmatched closing delimiter '{ch}' at line {line_idx}",
                                line_number=line_idx,
                            )
                        stack.pop()

            if stack:
                unclosed, l_idx = stack[-1]
                return SyntaxCheckResult(
                    valid=False,
                    language=ext,
                    error_message=f"Unclosed opening delimiter '{unclosed}' opened at line {l_idx}",
                    line_number=l_idx,
                )

            return SyntaxCheckResult(valid=True, language=ext)

        return SyntaxCheckResult(valid=True, language=ext)

    @classmethod
    def extract_and_solve_invariants(cls, task_text: str) -> InvariantSolution:
        """Extract explicit equations or numeric constraints from problem description."""
        # Find explicit equality / inequality equations
        eq_patterns = re.findall(r"([a-zA-Z0-9_\s\+\-\*\/\^]+=[a-zA-Z0-9_\s\+\-\*\/\^]+)", task_text)
        cleaned_eqs = [eq.strip() for eq in eq_patterns if len(eq.strip()) > 3]

        # Try SymPy if available
        try:
            import sympy  # type: ignore

            vars_found = set(re.findall(r"\b([a-zA-Z][a-zA-Z0-9_]*)\b", " ".join(cleaned_eqs)))
            symbols_map = {v: sympy.Symbol(v) for v in vars_found if v not in ("sin", "cos", "exp", "log")}
            sympy_eqs = []
            for eq_str in cleaned_eqs:
                if "=" in eq_str:
                    lhs, rhs = eq_str.split("=", 1)
                    sympy_eqs.append(sympy.Eq(sympy.sympify(lhs, locals=symbols_map), sympy.sympify(rhs, locals=symbols_map)))

            if sympy_eqs:
                sol = sympy.solve(sympy_eqs)
                return InvariantSolution(
                    success=True,
                    solution_text=str(sol),
                    extracted_equations=tuple(cleaned_eqs),
                    variable_assignments={str(k): str(v) for k, v in (sol.items() if isinstance(sol, dict) else {})}
                )
        except Exception:
            pass

        return InvariantSolution(
            success=len(cleaned_eqs) > 0,
            solution_text=f"Extracted {len(cleaned_eqs)} potential equations: {cleaned_eqs}",
            extracted_equations=tuple(cleaned_eqs),
            variable_assignments={},
        )
