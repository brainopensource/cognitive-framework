"""Surgical Editor ported from LEX to Vanguard.
Provides 5-tier fallback patching: Exact -> Whitespace-Tolerant -> Fuzzy Anchor -> Line Replacement -> Unified Diff.
"""

from __future__ import annotations
import re
from typing import Optional, Tuple


class LexSurgicalEditor:
    """Multi-strategy surgical code editor for robust LLM patch application."""

    @staticmethod
    def replace_exact(source: str, target: str, replacement: str) -> Optional[str]:
        """Replaces exact target substring if uniquely present."""
        if not target or source.count(target) != 1:
            return None
        return source.replace(target, replacement, 1)

    @staticmethod
    def replace_whitespace_tolerant(source: str, target: str, replacement: str) -> Optional[str]:
        """Matches target lines against source ignoring trailing whitespace and indentation differences."""
        src_lines = source.splitlines(keepends=True)
        tgt_lines = [l.strip() for l in target.splitlines() if l.strip()]

        if not tgt_lines or len(tgt_lines) > len(src_lines):
            return None

        candidates = []
        for i in range(len(src_lines) - len(tgt_lines) + 1):
            match = True
            for j, t_line in enumerate(tgt_lines):
                if src_lines[i + j].strip() != t_line:
                    match = False
                    break
            if match:
                candidates.append((i, i + len(tgt_lines)))

        if len(candidates) == 1:
            start_idx, end_idx = candidates[0]
            prefix = "".join(src_lines[:start_idx])
            suffix = "".join(src_lines[end_idx:])
            out = prefix + replacement + ("\n" if not replacement.endswith("\n") and suffix else "") + suffix
            return out
        return None

    @staticmethod
    def replace_fuzzy_anchors(source: str, target: str, replacement: str) -> Optional[str]:
        """Sliding window anchor matching for target chunks with approximate middle lines."""
        src_lines = source.splitlines(keepends=True)
        tgt_lines = [l.strip() for l in target.splitlines() if l.strip()]

        if len(tgt_lines) < 2 or len(tgt_lines) > len(src_lines):
            return None

        first_target = tgt_lines[0]
        last_target = tgt_lines[-1]

        candidates = []
        for i in range(len(src_lines)):
            if src_lines[i].strip() == first_target:
                search_max = min(i + len(tgt_lines) + 15, len(src_lines))
                for j in range(i + 1, search_max):
                    if src_lines[j].strip() == last_target:
                        candidates.append((i, j + 1))

        if len(candidates) == 1:
            start_idx, end_idx = candidates[0]
            prefix = "".join(src_lines[:start_idx])
            suffix = "".join(src_lines[end_idx:])
            out = prefix + replacement + ("\n" if not replacement.endswith("\n") and suffix else "") + suffix
            return out
        return None

    @staticmethod
    def replace_lines(source: str, start_line: int, end_line: int, replacement: str) -> Optional[str]:
        """1-indexed inclusive line range replacement."""
        lines = source.splitlines(keepends=True)
        if start_line < 1 or end_line < start_line or start_line > len(lines) + 1:
            return None

        start_idx = start_line - 1
        end_idx = min(end_line, len(lines))

        prefix = "".join(lines[:start_idx])
        suffix = "".join(lines[end_idx:])
        out = prefix + replacement + ("\n" if not replacement.endswith("\n") and suffix else "") + suffix
        return out

    @classmethod
    def apply_surgical_edit(
        cls,
        source: str,
        target_chunk: Optional[str] = None,
        replacement_chunk: Optional[str] = None,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> Tuple[bool, str, str]:
        """Applies the highest-confidence surgical edit strategy."""
        rep = replacement_chunk or ""

        # Strategy 1: Line-indexed replacement
        if start_line is not None and end_line is not None:
            res = cls.replace_lines(source, start_line, end_line, rep)
            if res is not None:
                return True, res, "line_indexed"

        if not target_chunk:
            return False, source, "no_target_specified"

        # Strategy 2: Exact substring match
        res = cls.replace_exact(source, target_chunk, rep)
        if res is not None:
            return True, res, "exact_match"

        # Strategy 3: Whitespace-tolerant line match
        res = cls.replace_whitespace_tolerant(source, target_chunk, rep)
        if res is not None:
            return True, res, "whitespace_tolerant"

        # Strategy 4: Sliding window fuzzy anchor match
        res = cls.replace_fuzzy_anchors(source, target_chunk, rep)
        if res is not None:
            return True, res, "fuzzy_anchors"

        return False, source, "exhausted_all_strategies"
