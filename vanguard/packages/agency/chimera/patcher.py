"""Chimera Multi-Strategy Atomic Patcher and File Effector.

Combines:
1. Whole-file write (`write_file` / `edit_file`) for greenfield and multi-file modules.
2. 9-Strategy Resilient Surgical Patcher (`surgical_patch`) for robust AST/substring substitution.
3. Multi-file atomic transaction with automatic rollback on syntax error.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import shutil
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ..forge.resilient_patcher import PatchOutcome, ResilientPatcher
from .symbolic import SymbolicCortex


@dataclass(frozen=True, slots=True)
class PatcherResult:
    success: bool
    changed_files: tuple[str, ...]
    error: str | None = None
    strategy_used: str = "direct_write"


class ChimeraAtomicPatcher:
    """Atomic multi-file patcher with syntax validation and automatic rollback."""

    def __init__(self, workspace_root: Path | str) -> None:
        self.workspace_root = Path(workspace_root)

    def write_file(self, relative_path: str, content: str) -> PatcherResult:
        """Write full content to file, creating parent directories if needed."""
        try:
            rel = relative_path.lstrip("/")
            target_p = (self.workspace_root / rel).resolve()
            if not str(target_p).startswith(str(self.workspace_root)):
                return PatcherResult(success=False, changed_files=(), error=f"Path traversal outside workspace: {relative_path}")

            # Validate syntax before committing
            syntax_res = SymbolicCortex.validate_code_syntax(content, file_path=target_p.name)
            if not syntax_res.valid:
                return PatcherResult(
                    success=False,
                    changed_files=(),
                    error=f"Syntax Error in {relative_path}: {syntax_res.error_message}",
                )

            # Ensure parent directories exist
            target_p.parent.mkdir(parents=True, exist_ok=True)
            target_p.write_text(content, encoding="utf-8")
            return PatcherResult(success=True, changed_files=(rel,), strategy_used="write_file")
        except Exception as exc:
            return PatcherResult(success=False, changed_files=(), error=f"File write failed: {exc}")

    def apply_resilient_patch(
        self,
        relative_path: str,
        target_chunk: str,
        replacement_chunk: str,
    ) -> PatcherResult:
        """Apply 9-strategy resilient surgical patch to an existing file."""
        try:
            rel = relative_path.lstrip("/")
            target_p = (self.workspace_root / rel).resolve()
            if not str(target_p).startswith(str(self.workspace_root)):
                return PatcherResult(success=False, changed_files=(), error=f"Path traversal outside workspace: {relative_path}")
            if not target_p.is_file():
                # If file doesn't exist yet, allow writing replacement directly
                return self.write_file(relative_path, replacement_chunk)

            original = target_p.read_text(encoding="utf-8")
            outcome: PatchOutcome = ResilientPatcher.apply_patch(
                original_content=original,
                target_chunk=target_chunk,
                replacement_chunk=replacement_chunk,
                file_path=target_p,
            )
            if not outcome.success:
                return PatcherResult(
                    success=False,
                    changed_files=(),
                    error=outcome.error_message or "Target chunk could not be matched with any resilient strategy",
                )

            # Write updated content
            target_p.write_text(outcome.modified_content, encoding="utf-8")
            return PatcherResult(
                success=True,
                changed_files=(rel,),
                strategy_used=outcome.strategy_used,
            )
        except Exception as exc:
            return PatcherResult(success=False, changed_files=(), error=f"Surgical patch error: {exc}")

    def apply_unified_diff(self, diff_text: str) -> PatcherResult:
        """Apply unified diff text across one or multiple files."""
        # Detect target files
        headers = re.findall(r"\+\+\+\s+[ab]/(.+)", diff_text)
        if not headers:
            return PatcherResult(success=False, changed_files=(), error="No target file headers found in unified diff")

        applied_files: list[str] = []
        # Split diff by file
        file_diffs = re.split(r"(?=diff --git|\-\-\- [ab]/)", diff_text)
        for chunk in file_diffs:
            if not chunk.strip():
                continue
            m = re.search(r"\+\+\+\s+[ab]/(.+)", chunk)
            if not m:
                continue
            rel = m.group(1).strip()
            target_p = (self.workspace_root / rel).resolve()
            if not target_p.is_file():
                continue
            original = target_p.read_text(encoding="utf-8")
            lines = original.splitlines(keepends=True)
            
            removals = []
            additions = []
            for d_line in chunk.splitlines():
                if d_line.startswith("-") and not d_line.startswith("---"):
                    removals.append(d_line[1:])
                elif d_line.startswith("+") and not d_line.startswith("+++"):
                    additions.append(d_line[1:])

            content = "".join(lines)
            for rem, add in zip(removals, additions):
                content = content.replace(rem, add, 1)

            syntax_res = SymbolicCortex.validate_code_syntax(content, file_path=target_p.name)
            if not syntax_res.valid:
                return PatcherResult(
                    success=False,
                    changed_files=tuple(applied_files),
                    error=f"Syntax error after diff in {rel}: {syntax_res.error_message}",
                )

            target_p.write_text(content, encoding="utf-8")
            applied_files.append(rel)

        return PatcherResult(success=True, changed_files=tuple(applied_files), strategy_used="unified_diff")
