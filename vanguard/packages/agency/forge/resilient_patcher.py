"""Unified 9-Strategy Resilient Patcher for Autonomous Coding Agents.

Implements cascading fuzzy matching strategies to eliminate mechanical string,
whitespace, indentation, Unicode, and formatting patch failures:
1. exact_match: Direct substring match.
2. line_trimmed: Strip leading/trailing whitespace per line.
3. whitespace_normalized: Collapse multiple spaces/tabs into a single space.
4. indent_flexible: Detect base indentation of target site and re-indent replacement chunk accordingly.
5. unicode_normalized: Map smart quotes, typographic dashes, NBSP, and Unicode punctuation.
6. boundary_trimmed: Match first and last line boundary where all target lines are present.
7. block_anchors: Anchor entry and exit lines; match interior via token similarity (>= 0.75).
8. ast_node: Python AST substitution for matching function/class definitions.
9. context_aware: 50% sequence similarity window.

Includes syntax validation and automatic rollback on SyntaxError.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
import difflib
from pathlib import Path
import re
from typing import Optional, Sequence, Tuple


UNICODE_REPLACEMENTS = {
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
    "\u2014": "--",
    "\u2013": "-",
    "\u2026": "...",
    "\u00a0": " ",
    "\u2212": "-",
    "\ufeff": "",
}


def normalize_unicode(text: str) -> str:
    """Normalize Unicode typographical characters into standard ASCII equivalents."""
    for src, dst in UNICODE_REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text


def collapse_whitespace(text: str) -> str:
    """Collapse consecutive spaces and tabs into a single space."""
    return re.sub(r"[ \t]+", " ", text)


@dataclass(frozen=True, slots=True)
class PatchOutcome:
    """Outcome of a resilient patch attempt."""

    success: bool
    modified_content: str
    strategy_used: str
    error_message: Optional[str] = None


class ResilientPatcher:
    """9-Strategy Resilient File Patcher for Autonomous Coding Agents."""

    @classmethod
    def apply_patch(
        cls,
        original_content: str,
        target_chunk: str,
        replacement_chunk: str,
        file_path: Optional[Path | str] = None,
    ) -> PatchOutcome:
        """Apply a patch to original_content using a cascading 9-strategy evaluation order.

        If a patch introduces a SyntaxError in Python source, it is automatically
        rolled back and the cascade continues or reports the syntax failure.
        """
        if not target_chunk.strip():
            return PatchOutcome(
                success=False,
                modified_content=original_content,
                strategy_used="none",
                error_message="Target chunk is empty.",
            )

        is_python = cls._is_python(original_content, file_path)
        last_syntax_error: Optional[str] = None

        # Strategy 1: Exact Match
        if target_chunk in original_content:
            new_text = original_content.replace(target_chunk, replacement_chunk, 1)
            valid, err = cls._validate_syntax(new_text, is_python)
            if valid:
                return PatchOutcome(True, new_text, "exact_match")
            last_syntax_error = err

        # Strategy 2: Line-Trimmed Match
        res = cls._match_line_trimmed(original_content, target_chunk, replacement_chunk)
        if res.success:
            valid, err = cls._validate_syntax(res.modified_content, is_python)
            if valid:
                return res
            last_syntax_error = err

        # Strategy 3: Whitespace Normalized Match
        res = cls._match_whitespace_normalized(original_content, target_chunk, replacement_chunk)
        if res.success:
            valid, err = cls._validate_syntax(res.modified_content, is_python)
            if valid:
                return res
            last_syntax_error = err

        # Strategy 4: Indentation Flexible Match
        res = cls._match_indentation_flexible(original_content, target_chunk, replacement_chunk)
        if res.success:
            valid, err = cls._validate_syntax(res.modified_content, is_python)
            if valid:
                return res
            last_syntax_error = err

        # Strategy 5: Unicode Normalized Match
        res = cls._match_unicode_normalized(original_content, target_chunk, replacement_chunk)
        if res.success:
            valid, err = cls._validate_syntax(res.modified_content, is_python)
            if valid:
                return res
            last_syntax_error = err

        # Strategy 6: Boundary Trimmed Match
        res = cls._match_boundary_trimmed(original_content, target_chunk, replacement_chunk)
        if res.success:
            valid, err = cls._validate_syntax(res.modified_content, is_python)
            if valid:
                return res
            last_syntax_error = err

        # Strategy 7: Block Anchors Match (>= 0.75 interior similarity)
        res = cls._match_block_anchors(original_content, target_chunk, replacement_chunk)
        if res.success:
            valid, err = cls._validate_syntax(res.modified_content, is_python)
            if valid:
                return res
            last_syntax_error = err

        # Strategy 8: AST Node Replacement (Python files only)
        if is_python:
            res = cls._match_ast_node(original_content, target_chunk, replacement_chunk)
            if res.success:
                valid, err = cls._validate_syntax(res.modified_content, is_python)
                if valid:
                    return res
                last_syntax_error = err

        # Strategy 9: Context-Aware Match (>= 50% sequence similarity window)
        res = cls._match_context_aware(original_content, target_chunk, replacement_chunk)
        if res.success:
            valid, err = cls._validate_syntax(res.modified_content, is_python)
            if valid:
                return res
            last_syntax_error = err

        # All strategies failed
        err_msg = (
            f"Syntax validation failed: {last_syntax_error}"
            if last_syntax_error
            else f"Could not locate target chunk in content ({len(original_content.splitlines())} lines). "
                 f"Please verify exact context around the edit."
        )
        return PatchOutcome(
            success=False,
            modified_content=original_content,
            strategy_used="failed_all_strategies",
            error_message=err_msg,
        )

    @classmethod
    def _is_python(cls, content: str, file_path: Optional[Path | str]) -> bool:
        """Determine whether the target is Python source."""
        if file_path is not None:
            return Path(file_path).suffix == ".py"
        try:
            ast.parse(content)
            return True
        except Exception:
            return False

    @classmethod
    def _validate_syntax(cls, code: str, is_python: bool) -> Tuple[bool, Optional[str]]:
        """Validate code syntax using AST parsing for Python files."""
        if not is_python:
            return True, None
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"SyntaxError: {e.msg} at line {e.lineno}"

    @classmethod
    def _match_line_trimmed(
        cls, content: str, target: str, replacement: str
    ) -> PatchOutcome:
        """Strategy 2: Match by stripping leading and trailing whitespace from each line."""
        content_lines = content.splitlines(keepends=True)
        target_lines = [l.strip() for l in target.splitlines() if l.strip()]
        if not target_lines:
            return PatchOutcome(False, content, "line_trimmed", "Target has no non-empty lines")

        m = len(target_lines)
        for i in range(len(content_lines) - m + 1):
            window = [content_lines[i + j].strip() for j in range(m)]
            if window == target_lines:
                prefix = "".join(content_lines[:i])
                suffix = "".join(content_lines[i + m:])
                sep = "\n" if replacement and not replacement.endswith("\n") and suffix else ""
                new_content = prefix + replacement + sep + suffix
                return PatchOutcome(True, new_content, "line_trimmed")

        return PatchOutcome(False, content, "line_trimmed", "No matching trimmed window found")

    @classmethod
    def _match_whitespace_normalized(
        cls, content: str, target: str, replacement: str
    ) -> PatchOutcome:
        """Strategy 3: Match by collapsing multiple spaces/tabs into a single space per line."""
        content_lines = content.splitlines(keepends=True)
        target_lines = [collapse_whitespace(l.strip()) for l in target.splitlines() if collapse_whitespace(l.strip())]
        if not target_lines:
            return PatchOutcome(False, content, "whitespace_normalized", "Target has no non-empty lines")

        m = len(target_lines)
        for i in range(len(content_lines) - m + 1):
            window = [collapse_whitespace(content_lines[i + j].strip()) for j in range(m)]
            if window == target_lines:
                prefix = "".join(content_lines[:i])
                suffix = "".join(content_lines[i + m:])
                sep = "\n" if replacement and not replacement.endswith("\n") and suffix else ""
                new_content = prefix + replacement + sep + suffix
                return PatchOutcome(True, new_content, "whitespace_normalized")

        return PatchOutcome(False, content, "whitespace_normalized", "No whitespace-normalized match found")

    @classmethod
    def _match_indentation_flexible(
        cls, content: str, target: str, replacement: str
    ) -> PatchOutcome:
        """Strategy 4: Match lines stripped, detect base indentation of target site, and re-indent replacement."""
        content_lines = content.splitlines(keepends=True)
        target_raw_lines = target.splitlines()
        target_stripped = [l.strip() for l in target_raw_lines if l.strip()]
        if not target_stripped:
            return PatchOutcome(False, content, "indent_flexible", "Empty target")

        m = len(target_stripped)
        for i in range(len(content_lines) - m + 1):
            window_stripped = [content_lines[i + j].strip() for j in range(m)]
            if window_stripped == target_stripped:
                # Matched indentation at origin site
                orig_indent_match = re.match(r"^[ \t]*", content_lines[i])
                matched_indent = orig_indent_match.group(0) if orig_indent_match else ""

                # Base indentation of target chunk's first non-empty line
                first_target_line = next((l for l in target_raw_lines if l.strip()), "")
                target_indent_match = re.match(r"^[ \t]*", first_target_line)
                target_base_indent = target_indent_match.group(0) if target_indent_match else ""

                # Re-indent replacement lines
                reindented_repl: list[str] = []
                for r_line in replacement.splitlines():
                    if not r_line.strip():
                        reindented_repl.append("")
                        continue
                    curr_indent_match = re.match(r"^[ \t]*", r_line)
                    curr_indent = curr_indent_match.group(0) if curr_indent_match else ""
                    rel_indent_len = max(0, len(curr_indent) - len(target_base_indent))
                    new_line = matched_indent + (" " * rel_indent_len) + r_line.strip()
                    reindented_repl.append(new_line)

                prefix = "".join(content_lines[:i])
                suffix = "".join(content_lines[i + m:])
                repl_body = "\n".join(reindented_repl)
                sep = "\n" if repl_body and not repl_body.endswith("\n") and suffix else ""
                new_content = prefix + repl_body + sep + suffix
                return PatchOutcome(True, new_content, "indent_flexible")

        return PatchOutcome(False, content, "indent_flexible", "No indentation-flexible match found")

    @classmethod
    def _match_unicode_normalized(
        cls, content: str, target: str, replacement: str
    ) -> PatchOutcome:
        """Strategy 5: Normalize smart quotes, dashes, NBSP, and Unicode punctuation."""
        norm_orig = normalize_unicode(content)
        norm_target = normalize_unicode(target)
        norm_repl = normalize_unicode(replacement)

        # Only apply if Unicode characters actually differed
        if norm_orig == content and norm_target == target and norm_repl == replacement:
            return PatchOutcome(False, content, "unicode_normalized", "No Unicode normalization delta")

        if norm_target in norm_orig:
            new_content = norm_orig.replace(norm_target, norm_repl, 1)
            return PatchOutcome(True, new_content, "unicode_normalized")

        # Line-trimmed fallback on normalized content
        orig_lines = norm_orig.splitlines(keepends=True)
        target_lines = [l.strip() for l in norm_target.splitlines() if l.strip()]
        m = len(target_lines)
        if m > 0:
            for i in range(len(orig_lines) - m + 1):
                window = [orig_lines[i + j].strip() for j in range(m)]
                if window == target_lines:
                    prefix = "".join(orig_lines[:i])
                    suffix = "".join(orig_lines[i + m:])
                    sep = "\n" if norm_repl and not norm_repl.endswith("\n") and suffix else ""
                    new_content = prefix + norm_repl + sep + suffix
                    return PatchOutcome(True, new_content, "unicode_normalized")

        return PatchOutcome(False, content, "unicode_normalized", "No Unicode normalized match found")

    @classmethod
    def _match_boundary_trimmed(
        cls, content: str, target: str, replacement: str
    ) -> PatchOutcome:
        """Strategy 6: Match first and last line boundary where all target lines are present in the range."""
        content_lines = content.splitlines(keepends=True)
        target_raw_lines = target.splitlines()
        target_lines = [l.strip() for l in target_raw_lines if l.strip()]
        if len(target_lines) < 2:
            return PatchOutcome(False, content, "boundary_trimmed", "Target requires >= 2 lines for boundary matching")

        first_line = target_lines[0]
        last_line = target_lines[-1]

        for i, c_line in enumerate(content_lines):
            if c_line.strip() == first_line:
                for j in range(i + 1, min(len(content_lines), i + 50)):
                    if content_lines[j].strip() == last_line:
                        block_lines = [content_lines[k].strip() for k in range(i, j + 1)]
                        # Verify all target lines appear in order or subset
                        if all(t in block_lines for t in target_lines):
                            orig_indent_match = re.match(r"^[ \t]*", content_lines[i])
                            matched_indent = orig_indent_match.group(0) if orig_indent_match else ""

                            first_target_line = next((l for l in target_raw_lines if l.strip()), "")
                            target_indent_match = re.match(r"^[ \t]*", first_target_line)
                            target_base_indent = target_indent_match.group(0) if target_indent_match else ""

                            reindented_repl: list[str] = []
                            for r_line in replacement.splitlines():
                                if not r_line.strip():
                                    reindented_repl.append("")
                                    continue
                                curr_indent_match = re.match(r"^[ \t]*", r_line)
                                curr_indent = curr_indent_match.group(0) if curr_indent_match else ""
                                rel_indent_len = max(0, len(curr_indent) - len(target_base_indent))
                                reindented_repl.append(matched_indent + (" " * rel_indent_len) + r_line.strip())

                            prefix = "".join(content_lines[:i])
                            suffix = "".join(content_lines[j + 1:])
                            repl_body = "\n".join(reindented_repl)
                            sep = "\n" if repl_body and not repl_body.endswith("\n") and suffix else ""
                            new_content = prefix + repl_body + sep + suffix
                            return PatchOutcome(True, new_content, "boundary_trimmed")

        return PatchOutcome(False, content, "boundary_trimmed", "No boundary trimmed match found")

    @classmethod
    def _match_block_anchors(
        cls, content: str, target: str, replacement: str
    ) -> PatchOutcome:
        """Strategy 7: Anchor entry and exit lines; match interior via token/line similarity (>= 0.75)."""
        content_lines = content.splitlines(keepends=True)
        target_raw_lines = target.splitlines()
        target_lines = [l.strip() for l in target_raw_lines if l.strip()]
        if len(target_lines) < 3:
            return PatchOutcome(False, content, "block_anchors", "Target too short for anchor matching (requires >= 3 lines)")

        first_line = target_lines[0]
        last_line = target_lines[-1]
        m = len(target_lines)

        for i in range(len(content_lines) - m + 1):
            if content_lines[i].strip() == first_line and content_lines[i + m - 1].strip() == last_line:
                mid_content = "\n".join(content_lines[i + j].strip() for j in range(1, m - 1))
                mid_target = "\n".join(target_lines[1:-1])
                ratio = difflib.SequenceMatcher(None, mid_content, mid_target).ratio()
                if ratio >= 0.75:
                    orig_indent_match = re.match(r"^[ \t]*", content_lines[i])
                    matched_indent = orig_indent_match.group(0) if orig_indent_match else ""

                    first_target_line = next((l for l in target_raw_lines if l.strip()), "")
                    target_indent_match = re.match(r"^[ \t]*", first_target_line)
                    target_base_indent = target_indent_match.group(0) if target_indent_match else ""

                    reindented_repl: list[str] = []
                    for r_line in replacement.splitlines():
                        if not r_line.strip():
                            reindented_repl.append("")
                            continue
                        curr_indent_match = re.match(r"^[ \t]*", r_line)
                        curr_indent = curr_indent_match.group(0) if curr_indent_match else ""
                        rel_indent_len = max(0, len(curr_indent) - len(target_base_indent))
                        new_line = matched_indent + (" " * rel_indent_len) + r_line.strip()
                        reindented_repl.append(new_line)

                    prefix = "".join(content_lines[:i])
                    suffix = "".join(content_lines[i + m:])
                    repl_body = "\n".join(reindented_repl)
                    sep = "\n" if repl_body and not repl_body.endswith("\n") and suffix else ""
                    new_content = prefix + repl_body + sep + suffix
                    return PatchOutcome(True, new_content, "block_anchors")

        return PatchOutcome(False, content, "block_anchors", "No matching block anchors found")

    @classmethod
    def _match_ast_node(
        cls, content: str, target: str, replacement: str
    ) -> PatchOutcome:
        """Strategy 8: Python AST substitution for matching function or class definitions."""
        try:
            orig_tree = ast.parse(content)
            repl_tree = ast.parse(replacement)
        except Exception as exc:
            return PatchOutcome(False, content, "ast_node", f"AST parsing failed: {exc}")

        # If replacement defines a single function or class, replace corresponding node in orig
        if len(repl_tree.body) == 1 and isinstance(
            repl_tree.body[0], (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            target_node_name = repl_tree.body[0].name
            content_lines = content.splitlines(keepends=True)

            for node in ast.walk(orig_tree):
                if (
                    isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    and node.name == target_node_name
                ):
                    start_line = node.lineno - 1
                    if getattr(node, "decorator_list", None):
                        start_line = node.decorator_list[0].lineno - 1

                    end_line = getattr(node, "end_lineno", node.lineno)
                    prefix = "".join(content_lines[:start_line])
                    suffix = "".join(content_lines[end_line:])
                    sep = "\n" if replacement and not replacement.endswith("\n") and suffix else ""
                    new_content = prefix + replacement + sep + suffix
                    return PatchOutcome(True, new_content, "ast_node")

        return PatchOutcome(False, content, "ast_node", "No replaceable AST node found")

    @classmethod
    def _match_context_aware(
        cls, content: str, target: str, replacement: str
    ) -> PatchOutcome:
        """Strategy 9: 50% sequence similarity window match."""
        content_lines = content.splitlines(keepends=True)
        target_raw_lines = target.splitlines()
        target_lines = [l.strip() for l in target_raw_lines if l.strip()]
        if not target_lines:
            return PatchOutcome(False, content, "context_aware", "Empty target lines")

        m = len(target_lines)
        if len(content_lines) < m:
            return PatchOutcome(False, content, "context_aware", "Content shorter than target window")

        best_ratio = 0.0
        best_i = -1
        target_str = "\n".join(target_lines)

        for i in range(len(content_lines) - m + 1):
            window_str = "\n".join(content_lines[i + j].strip() for j in range(m))
            ratio = difflib.SequenceMatcher(None, window_str, target_str).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_i = i

        if best_ratio >= 0.50 and best_i >= 0:
            orig_indent_match = re.match(r"^[ \t]*", content_lines[best_i])
            matched_indent = orig_indent_match.group(0) if orig_indent_match else ""

            first_target_line = next((l for l in target_raw_lines if l.strip()), "")
            target_indent_match = re.match(r"^[ \t]*", first_target_line)
            target_base_indent = target_indent_match.group(0) if target_indent_match else ""

            reindented_repl: list[str] = []
            for r_line in replacement.splitlines():
                if not r_line.strip():
                    reindented_repl.append("")
                    continue
                curr_indent_match = re.match(r"^[ \t]*", r_line)
                curr_indent = curr_indent_match.group(0) if curr_indent_match else ""
                rel_indent_len = max(0, len(curr_indent) - len(target_base_indent))
                reindented_repl.append(matched_indent + (" " * rel_indent_len) + r_line.strip())

            prefix = "".join(content_lines[:best_i])
            suffix = "".join(content_lines[best_i + m:])
            repl_body = "\n".join(reindented_repl)
            sep = "\n" if repl_body and not repl_body.endswith("\n") and suffix else ""
            new_content = prefix + repl_body + sep + suffix
            return PatchOutcome(True, new_content, "context_aware")

        return PatchOutcome(False, content, "context_aware", f"Best sequence similarity ratio ({best_ratio:.2f}) < 0.50")
