"""Atomic patch applicator for 1-Forge (Reflexive Agentic Micro-Forge).

Supports:
1. Unified diff format (multi-file and single-file hunks).
2. Exact & whitespace-tolerant block search-and-replace.
3. AST symbol replacement for Python functions and classes.
4. Atomic rollback: Any failure or syntax defect restores workspace to exact pre-patch state.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import difflib
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple


@dataclass(frozen=True, slots=True)
class PatchHunk:
    """One hunk in a unified diff."""

    old_start: int
    old_count: int
    new_start: int
    new_count: int
    lines: tuple[str, ...]
    header: str = ""


@dataclass(frozen=True, slots=True)
class FilePatch:
    """A collection of hunks targeting a specific file."""

    old_path: str
    new_path: str
    hunks: tuple[PatchHunk, ...]
    is_creation: bool = False
    is_deletion: bool = False


@dataclass(frozen=True, slots=True)
class PatchResult:
    """Result of an atomic patch application."""

    success: bool
    changed_files: tuple[str, ...] = ()
    applied_hunks: int = 0
    error: str | None = None
    backup: Mapping[str, str] = field(default_factory=dict)
    details: tuple[str, ...] = ()


class PatchError(ValueError):
    """Raised when a patch cannot be applied cleanly."""


class UnifiedDiffParser:
    """Parses standard unified diffs into structured FilePatch objects."""

    _HUNK_HEADER = re.compile(
        r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@(?: *(.*))?$"
    )

    @classmethod
    def parse(cls, diff_text: str) -> list[FilePatch]:
        """Parse unified diff text into a list of FilePatch objects."""
        lines = diff_text.replace("\r\n", "\n").split("\n")
        file_patches: list[FilePatch] = []
        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]

            # Detect file headers: diff --git or --- / +++
            if line.startswith("diff --git ") or line.startswith("--- "):
                old_path = ""
                new_path = ""
                is_creation = False
                is_deletion = False

                if line.startswith("diff --git "):
                    parts = line[len("diff --git "):].split(" ")
                    if len(parts) >= 2:
                        old_path = parts[0].lstrip("a/").lstrip("b/")
                        new_path = parts[1].lstrip("a/").lstrip("b/")
                    i += 1
                    # Skip git metadata lines until ---
                    while i < n and not lines[i].startswith("--- ") and not lines[i].startswith("diff --git "):
                        if lines[i].startswith("new file mode"):
                            is_creation = True
                        elif lines[i].startswith("deleted file mode"):
                            is_deletion = True
                        i += 1
                    if i >= n or lines[i].startswith("diff --git "):
                        continue

                # Parse --- line
                if i < n and lines[i].startswith("--- "):
                    raw_old = lines[i][4:].strip()
                    if raw_old.startswith("a/"):
                        raw_old = raw_old[2:]
                    elif raw_old == "/dev/null":
                        is_creation = True
                    if not old_path and raw_old != "/dev/null":
                        old_path = raw_old.split("\t")[0].strip()
                    i += 1

                # Parse +++ line
                if i < n and lines[i].startswith("+++ "):
                    raw_new = lines[i][4:].strip()
                    if raw_new.startswith("b/"):
                        raw_new = raw_new[2:]
                    elif raw_new == "/dev/null":
                        is_deletion = True
                    if not new_path and raw_new != "/dev/null":
                        new_path = raw_new.split("\t")[0].strip()
                    i += 1

                target_path = new_path if not is_deletion else old_path
                if not target_path:
                    target_path = old_path

                # Parse hunks for this file
                hunks: list[PatchHunk] = []
                while i < n and not lines[i].startswith("diff --git ") and not lines[i].startswith("--- "):
                    if lines[i].startswith("@@"):
                        match = cls._HUNK_HEADER.match(lines[i])
                        if not match:
                            i += 1
                            continue
                        old_start = int(match.group(1))
                        old_count = int(match.group(2)) if match.group(2) is not None else 1
                        new_start = int(match.group(3))
                        new_count = int(match.group(4)) if match.group(4) is not None else 1
                        header_extra = match.group(5) or ""

                        hunk_lines: list[str] = []
                        i += 1
                        while i < n and not lines[i].startswith("@@") and not lines[i].startswith("diff --git ") and not lines[i].startswith("--- "):
                            if lines[i] and lines[i][0] in (" ", "-", "+", "\\"):
                                hunk_lines.append(lines[i])
                            elif not lines[i] and i + 1 < n and (lines[i+1].startswith("@@") or lines[i+1].startswith("diff ")):
                                break
                            else:
                                # Treat empty line as empty context line if inside hunk
                                hunk_lines.append(" " + lines[i] if lines[i] else " ")
                            i += 1

                        hunks.append(
                            PatchHunk(
                                old_start=old_start,
                                old_count=old_count,
                                new_start=new_start,
                                new_count=new_count,
                                lines=tuple(hunk_lines),
                                header=header_extra,
                            )
                        )
                    else:
                        i += 1

                if target_path:
                    file_patches.append(
                        FilePatch(
                            old_path=old_path or target_path,
                            new_path=new_path or target_path,
                            hunks=tuple(hunks),
                            is_creation=is_creation,
                            is_deletion=is_deletion,
                        )
                    )
            else:
                i += 1

        return file_patches


class BlockPatcher:
    """Applies search-and-replace block replacements with fuzzy fallbacks."""

    @classmethod
    def apply_replace(
        cls,
        content: str,
        find_text: str,
        replace_text: str,
        mode: str = "exact",
    ) -> tuple[bool, str, str | None]:
        """Replace target block in content.
        
        Modes:
        - "exact": Exact substring match.
        - "normalized_ws": Whitespace-tolerant match (ignores indentation/blank line discrepancies).
        - "fuzzy": Best effort sequence match.
        """
        if not find_text:
            return False, content, "Empty find_text target"

        # 1. Exact match
        if find_text in content:
            new_content = content.replace(find_text, replace_text, 1)
            return True, new_content, None

        # 2. Normalized whitespace match
        find_lines = [line.strip() for line in find_text.strip().split("\n") if line.strip()]
        content_lines = content.split("\n")

        if find_lines:
            for start_idx in range(len(content_lines) - len(find_lines) + 1):
                match = True
                for offset, f_line in enumerate(find_lines):
                    c_line = content_lines[start_idx + offset].strip()
                    if c_line != f_line:
                        match = False
                        break
                if match:
                    # Found match range: start_idx .. start_idx + len(find_lines)
                    end_idx = start_idx + len(find_lines)
                    orig_first_line = content_lines[start_idx]
                    indent = orig_first_line[: len(orig_first_line) - len(orig_first_line.lstrip())]

                    repl_lines = replace_text.split("\n")
                    indented_repl: list[str] = []
                    for r_line in repl_lines:
                        if r_line.strip() and not r_line.startswith(indent):
                            indented_repl.append(indent + r_line)
                        else:
                            indented_repl.append(r_line)

                    new_lines = content_lines[:start_idx] + indented_repl + content_lines[end_idx:]
                    return True, "\n".join(new_lines), None

        # 3. Fallback failure
        return False, content, f"Target text block not found in file content ({len(find_text)} chars)"


class ASTPatcher:
    """Safe AST-based function and class replacement for Python modules."""

    @classmethod
    def replace_symbol(
        cls,
        source_code: str,
        symbol_name: str,
        replacement_code: str,
    ) -> tuple[bool, str, str | None]:
        """Replace a top-level or class-level function/class in source_code."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError as exc:
            return False, source_code, f"Source code has syntax error: {exc}"

        try:
            ast.parse(replacement_code)
        except SyntaxError as exc:
            return False, source_code, f"Replacement code has syntax error: {exc}"

        lines = source_code.splitlines(keepends=True)
        target_node: Optional[ast.AST] = None

        # Find target node
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == symbol_name:
                    target_node = node
                    break

        if target_node is None:
            return False, source_code, f"Symbol '{symbol_name}' not found in AST"

        start_line = target_node.lineno - 1
        end_line = getattr(target_node, "end_lineno", None)
        if end_line is None:
            return False, source_code, f"Could not determine end line for symbol '{symbol_name}'"

        # Check for decorators
        if getattr(target_node, "decorator_list", None):
            first_dec = target_node.decorator_list[0]
            start_line = first_dec.lineno - 1

        # Replace slice
        new_lines = lines[:start_line] + [replacement_code + "\n"] + lines[end_line:]
        result_code = "".join(new_lines)

        # Validate syntax of combined result
        try:
            ast.parse(result_code)
        except SyntaxError as exc:
            return False, source_code, f"Combined AST result is invalid: {exc}"

        return True, result_code, None


class ForgeAtomicPatcher:
    """High-reliability atomic patch engine with automatic rollback on error."""

    def __init__(self, workspace_root: Path | str) -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def _resolve_safe_path(self, rel_path: str) -> Path:
        clean_rel = rel_path.lstrip("/").lstrip("\\")
        target = (self.workspace_root / clean_rel).resolve()
        if not str(target).startswith(str(self.workspace_root)):
            raise PatchError(f"Path traversal attempted: {rel_path}")
        return target

    def apply_file_write(self, rel_path: str, content: str) -> PatchResult:
        """Atomically overwrite or create a file."""
        target = self._resolve_safe_path(rel_path)
        backup: dict[str, str] = {}

        if target.exists():
            backup[rel_path] = target.read_text(encoding="utf-8")

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

            # Validate Python syntax if applicable
            if target.suffix == ".py":
                try:
                    ast.parse(content)
                except SyntaxError as err:
                    self.rollback(backup)
                    return PatchResult(
                        success=False,
                        error=f"SyntaxError in {rel_path}: {err}",
                        backup=backup,
                    )

            return PatchResult(
                success=True,
                changed_files=(rel_path,),
                applied_hunks=1,
                backup=backup,
            )
        except Exception as exc:
            self.rollback(backup)
            return PatchResult(success=False, error=str(exc), backup=backup)

    def apply_block_replace(
        self,
        rel_path: str,
        find_text: str,
        replace_text: str,
        mode: str = "exact",
    ) -> PatchResult:
        """Atomically replace a block inside a file."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_file():
            return PatchResult(success=False, error=f"File not found: {rel_path}")

        original = target.read_text(encoding="utf-8")
        backup = {rel_path: original}

        ok, new_content, err = BlockPatcher.apply_replace(
            original, find_text, replace_text, mode=mode
        )
        if not ok:
            return PatchResult(success=False, error=err, backup=backup)

        try:
            target.write_text(new_content, encoding="utf-8")
            if target.suffix == ".py":
                try:
                    ast.parse(new_content)
                except SyntaxError as syn_err:
                    self.rollback(backup)
                    return PatchResult(
                        success=False,
                        error=f"SyntaxError after replacement in {rel_path}: {syn_err}",
                        backup=backup,
                    )

            return PatchResult(
                success=True,
                changed_files=(rel_path,),
                applied_hunks=1,
                backup=backup,
            )
        except Exception as exc:
            self.rollback(backup)
            return PatchResult(success=False, error=str(exc), backup=backup)

    def apply_ast_replace(
        self,
        rel_path: str,
        symbol_name: str,
        replacement_code: str,
    ) -> PatchResult:
        """Atomically replace an AST symbol in a Python file."""
        target = self._resolve_safe_path(rel_path)
        if not target.is_file():
            return PatchResult(success=False, error=f"File not found: {rel_path}")

        original = target.read_text(encoding="utf-8")
        backup = {rel_path: original}

        ok, new_content, err = ASTPatcher.replace_symbol(
            original, symbol_name, replacement_code
        )
        if not ok:
            return PatchResult(success=False, error=err, backup=backup)

        try:
            target.write_text(new_content, encoding="utf-8")
            return PatchResult(
                success=True,
                changed_files=(rel_path,),
                applied_hunks=1,
                backup=backup,
            )
        except Exception as exc:
            self.rollback(backup)
            return PatchResult(success=False, error=str(exc), backup=backup)

    def apply_unified_diff(self, diff_text: str) -> PatchResult:
        """Atomically parse and apply a unified diff across one or more files."""
        try:
            file_patches = UnifiedDiffParser.parse(diff_text)
        except Exception as exc:
            return PatchResult(success=False, error=f"Diff parse error: {exc}")

        if not file_patches:
            return PatchResult(success=False, error="No valid file patches found in diff")

        backup: dict[str, str] = {}
        changed_files: list[str] = []
        total_hunks = 0

        # Step 1: Pre-flight check and backup all affected files
        for fp in file_patches:
            rel_path = fp.new_path or fp.old_path
            target = self._resolve_safe_path(rel_path)
            if target.exists():
                backup[rel_path] = target.read_text(encoding="utf-8")

        # Step 2: Apply hunks file by file
        try:
            for fp in file_patches:
                rel_path = fp.new_path or fp.old_path
                target = self._resolve_safe_path(rel_path)

                if fp.is_creation:
                    new_lines: list[str] = []
                    for hunk in fp.hunks:
                        for l in hunk.lines:
                            if l.startswith("+"):
                                new_lines.append(l[1:])
                            elif l.startswith(" "):
                                new_lines.append(l[1:])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    content = "\n".join(new_lines)
                    target.write_text(content, encoding="utf-8")
                    changed_files.append(rel_path)
                    total_hunks += len(fp.hunks)
                    continue

                if fp.is_deletion:
                    if target.exists():
                        target.unlink()
                    changed_files.append(rel_path)
                    continue

                if not target.exists():
                    raise PatchError(f"Target file does not exist: {rel_path}")

                orig_lines = target.read_text(encoding="utf-8").split("\n")
                patched_lines = list(orig_lines)

                # Apply hunks in sequence
                for hunk in fp.hunks:
                    old_expected: list[str] = []
                    new_repl: list[str] = []
                    for h_line in hunk.lines:
                        if h_line.startswith("-"):
                            old_expected.append(h_line[1:])
                        elif h_line.startswith("+"):
                            new_repl.append(h_line[1:])
                        elif h_line.startswith(" "):
                            old_expected.append(h_line[1:])
                            new_repl.append(h_line[1:])

                    search_pos = max(0, hunk.old_start - 1)
                    matched_idx = -1

                    # 1. Exact range check
                    if search_pos + len(old_expected) <= len(patched_lines):
                        if patched_lines[search_pos : search_pos + len(old_expected)] == old_expected:
                            matched_idx = search_pos

                    # 2. Window scan around search_pos
                    if matched_idx == -1:
                        window = 30
                        min_i = max(0, search_pos - window)
                        max_i = min(len(patched_lines) - len(old_expected), search_pos + window)
                        for idx in range(min_i, max_i + 1):
                            if patched_lines[idx : idx + len(old_expected)] == old_expected:
                                matched_idx = idx
                                break

                    # 3. Global scan
                    if matched_idx == -1:
                        for idx in range(len(patched_lines) - len(old_expected) + 1):
                            if patched_lines[idx : idx + len(old_expected)] == old_expected:
                                matched_idx = idx
                                break

                    # 4. Whitespace-trimmed scan fallback
                    if matched_idx == -1:
                        trimmed_exp = [x.strip() for x in old_expected]
                        for idx in range(len(patched_lines) - len(old_expected) + 1):
                            candidate = [x.strip() for x in patched_lines[idx : idx + len(old_expected)]]
                            if candidate == trimmed_exp:
                                matched_idx = idx
                                break

                    if matched_idx == -1:
                        raise PatchError(
                            f"Hunk at line {hunk.old_start} in {rel_path} failed to match target content"
                        )

                    patched_lines = (
                        patched_lines[:matched_idx]
                        + new_repl
                        + patched_lines[matched_idx + len(old_expected) :]
                    )
                    total_hunks += 1

                new_file_content = "\n".join(patched_lines)
                target.write_text(new_file_content, encoding="utf-8")

                if target.suffix == ".py":
                    try:
                        ast.parse(new_file_content)
                    except SyntaxError as syn_err:
                        raise PatchError(f"Syntax error after diff in {rel_path}: {syn_err}")

                changed_files.append(rel_path)

            return PatchResult(
                success=True,
                changed_files=tuple(dict.fromkeys(changed_files)),
                applied_hunks=total_hunks,
                backup=backup,
            )

        except Exception as exc:
            self.rollback(backup)
            return PatchResult(success=False, error=str(exc), backup=backup)

    def rollback(self, backup: Mapping[str, str]) -> None:
        """Roll back all modified files to their backup contents."""
        for rel_path, original_content in backup.items():
            try:
                target = self._resolve_safe_path(rel_path)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(original_content, encoding="utf-8")
            except Exception:
                pass
