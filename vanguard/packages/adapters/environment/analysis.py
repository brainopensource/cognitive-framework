"""Candidate-bound structural analysis at the environment adapter boundary.

This module is shared by transaction preflight and completion-time inspection.
It parses only workspace content supplied to the adapter boundary; it neither
executes code nor decides whether a candidate satisfies a task.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

__all__ = ["CandidateStructure", "analyze_candidate", "python_syntax_error"]


@dataclass(frozen=True, slots=True)
class CandidateStructure:
    """Structural facts about one exact candidate file set."""

    valid: bool
    contains_stub: bool


def python_syntax_error(content: str, *, path: str) -> str | None:
    """Return a stable syntax diagnostic without executing candidate code."""
    try:
        ast.parse(content, filename=path)
    except SyntaxError as exc:
        return f"SyntaxError at {path}:{exc.lineno}: {exc.msg}"
    return None


def _contains_stub(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = list(node.body)
        if body and all(
            isinstance(item, ast.Pass)
            or (
                isinstance(item, ast.Raise)
                and isinstance(item.exc, (ast.Name, ast.Call))
                and (
                    getattr(item.exc, "id", "") == "NotImplementedError"
                    or getattr(getattr(item.exc, "func", None), "id", "")
                    == "NotImplementedError"
                )
            )
            for item in body
        ):
            return True
    return False


def analyze_candidate(root: Path, paths: Iterable[str]) -> CandidateStructure:
    """Check exact changed files for presence, syntax, and vacuous Python bodies."""
    resolved = tuple(sorted(set(str(path) for path in paths)))
    if not resolved:
        return CandidateStructure(valid=False, contains_stub=False)
    contains_stub = False
    for relative in resolved:
        candidate = Path(root) / relative
        if not candidate.is_file():
            return CandidateStructure(valid=False, contains_stub=False)
        if candidate.suffix != ".py":
            continue
        try:
            content = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return CandidateStructure(valid=False, contains_stub=False)
        if python_syntax_error(content, path=relative) is not None:
            return CandidateStructure(valid=False, contains_stub=False)
        contains_stub = contains_stub or _contains_stub(
            ast.parse(content, filename=relative))
    return CandidateStructure(valid=True, contains_stub=contains_stub)
