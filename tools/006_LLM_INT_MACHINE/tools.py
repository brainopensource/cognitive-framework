"""Tool execution bindings, AST pre-flight verification, and paged truncation for 006_LLM_INT_MACHINE."""

from __future__ import annotations
import ast
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

try:
    from .config import HarnessConfig
except ImportError:
    from config import HarnessConfig


@dataclass
class ToolExecutionResult:
    ok: bool
    output: str
    is_ast_error: bool = False
    bytes_produced: int = 0


class ToolWorkspace:
    def __init__(self, workspace_root: Path | str, config: HarnessConfig) -> None:
        self.root = Path(workspace_root).resolve()
        self.config = config
        self.ast_errors_caught: int = 0
        self.checkpoints: dict[str, str] = {}

    def _resolve(self, relative_path: str) -> Path:
        target = (self.root / relative_path).resolve()
        try:
            target.relative_to(self.root)
        except ValueError:
            raise PermissionError(f"Access denied: path '{relative_path}' escapes workspace root.")
        return target

    def fs_read(self, path: str, start_line: int = 1, line_count: int = 120) -> ToolExecutionResult:
        try:
            target = self._resolve(path)
            if not target.is_file():
                return ToolExecutionResult(ok=False, output=f"Error: file '{path}' does not exist.")
            
            lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
            total = len(lines)
            start_idx = max(0, start_line - 1)
            end_idx = min(total, start_idx + line_count)
            
            slice_lines = lines[start_idx:end_idx]
            formatted = [f"{i + 1:4d} | {line}" for i, line in enumerate(slice_lines, start=start_idx)]
            header = f"[File: {path} (Lines {start_idx + 1} to {end_idx} of {total})]\n"
            content = header + "\n".join(formatted)
            return ToolExecutionResult(ok=True, output=content, bytes_produced=len(content))
        except Exception as e:
            return ToolExecutionResult(ok=False, output=f"fs_read error: {str(e)}")

    def fs_search(self, pattern: str, path: str = ".") -> ToolExecutionResult:
        try:
            target_dir = self._resolve(path)
            regex = re.compile(pattern, re.IGNORECASE)
            matches: list[str] = []
            
            for file_path in target_dir.rglob("*"):
                if not file_path.is_file() or ".git" in file_path.parts or "__pycache__" in file_path.parts:
                    continue
                try:
                    rel_p = file_path.relative_to(self.root).as_posix()
                    lines = file_path.read_text(encoding="utf-8", errors="replace").splitlines()
                    for idx, line in enumerate(lines, start=1):
                        if regex.search(line):
                            matches.append(f"{rel_p}:{idx}: {line.strip()[:140]}")
                            if len(matches) >= 50:
                                break
                except Exception:
                    continue
                if len(matches) >= 50:
                    break

            if not matches:
                return ToolExecutionResult(ok=True, output=f"No matches found for pattern: '{pattern}'")
            
            out = f"[Search matches for '{pattern}'] (Top {len(matches)}):\n" + "\n".join(matches)
            return ToolExecutionResult(ok=True, output=out, bytes_produced=len(out))
        except Exception as e:
            return ToolExecutionResult(ok=False, output=f"fs_search error: {str(e)}")

    def fs_list(self, path: str = ".") -> ToolExecutionResult:
        try:
            target_dir = self._resolve(path)
            entries: list[str] = []
            for item in sorted(target_dir.iterdir()):
                if item.name.startswith(".git") or item.name == "__pycache__":
                    continue
                kind = "DIR " if item.is_dir() else "FILE"
                entries.append(f"[{kind}] {item.relative_to(self.root).as_posix()}")
            out = f"[Directory Listing of '{path}']:\n" + "\n".join(entries)
            return ToolExecutionResult(ok=True, output=out, bytes_produced=len(out))
        except Exception as e:
            return ToolExecutionResult(ok=False, output=f"fs_list error: {str(e)}")

    def patch_apply(self, path: str, target_chunk: str, replacement_chunk: str) -> ToolExecutionResult:
        try:
            target = self._resolve(path)
            if not target.is_file():
                if not target_chunk.strip():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(replacement_chunk, encoding="utf-8")
                    return ToolExecutionResult(ok=True, output=f"Created new file: '{path}' ({len(replacement_chunk)} bytes)")
                return ToolExecutionResult(ok=False, output=f"Error: file '{path}' does not exist.")

            original_text = target.read_text(encoding="utf-8")
            
            norm_orig = original_text.replace("\r\n", "\n")
            norm_target = target_chunk.replace("\r\n", "\n")
            norm_repl = replacement_chunk.replace("\r\n", "\n")

            if norm_target not in norm_orig:
                stripped_target = "\n".join(line.strip() for line in norm_target.splitlines() if line.strip())
                if stripped_target and stripped_target not in "\n".join(line.strip() for line in norm_orig.splitlines()):
                    return ToolExecutionResult(
                        ok=False,
                        output=f"Patch Error: target_chunk not found in '{path}'. Make sure the target text matches exactly.",
                    )

            new_text = norm_orig.replace(norm_target, norm_repl, 1)

            if self.config.use_ast_preflight and path.endswith(".py"):
                try:
                    ast.parse(new_text, filename=path)
                except SyntaxError as syn_err:
                    self.ast_errors_caught += 1
                    err_msg = (
                        f"AST PRE-FLIGHT SYNTAX ERROR in '{path}' at line {syn_err.lineno}, col {syn_err.offset}: {syn_err.msg}\n"
                        f"File NOT modified. Please fix syntax and re-apply."
                    )
                    return ToolExecutionResult(ok=False, output=err_msg, is_ast_error=True)

            target.write_text(new_text, encoding="utf-8")
            return ToolExecutionResult(
                ok=True,
                output=f"Successfully patched '{path}' ({len(norm_target)} chars replaced with {len(norm_repl)} chars).",
                bytes_produced=len(new_text),
            )
        except Exception as e:
            return ToolExecutionResult(ok=False, output=f"patch_apply error: {str(e)}")

    def proc_exec(self, command: str, timeout_sec: int | None = None) -> ToolExecutionResult:
        timeout = timeout_sec or self.config.timeout_per_command_sec
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = res.stdout
            stderr = res.stderr
            combined = ""
            if stdout:
                combined += f"[STDOUT]\n{stdout}\n"
            if stderr:
                combined += f"[STDERR]\n{stderr}\n"
            combined += f"[EXIT CODE: {res.returncode}]"

            if self.config.use_paged_output:
                combined = self._truncate_output(combined)

            ok = (res.returncode == 0)
            return ToolExecutionResult(ok=ok, output=combined, bytes_produced=len(combined))
        except subprocess.TimeoutExpired:
            return ToolExecutionResult(ok=False, output=f"Command timed out after {timeout} seconds: '{command}'")
        except Exception as e:
            return ToolExecutionResult(ok=False, output=f"proc_exec error: {str(e)}")

    def _truncate_output(self, text: str) -> str:
        lines = text.splitlines()
        if len(lines) <= self.config.max_output_lines:
            return text
        
        head = lines[:self.config.head_lines]
        tail = lines[-self.config.tail_lines:]
        omitted = len(lines) - self.config.head_lines - self.config.tail_lines
        
        summary = f"\n... [{omitted} lines truncated for token efficiency. Showing top {self.config.head_lines} and last {self.config.tail_lines} lines] ...\n"
        return "\n".join(head) + summary + "\n".join(tail)

    def git_checkpoint(self, label: str) -> str:
        try:
            res = subprocess.run(
                ["git", "stash", "create"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                check=False,
            )
            stash_hash = res.stdout.strip()
            checkpoint_id = stash_hash or f"chk_{len(self.checkpoints) + 1}"
            self.checkpoints[label] = checkpoint_id
            return checkpoint_id
        except Exception:
            return "chk_fallback"

    def git_rollback(self) -> bool:
        try:
            subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=str(self.root), capture_output=True, check=True)
            subprocess.run(["git", "clean", "-fd"], cwd=str(self.root), capture_output=True, check=True)
            return True
        except Exception:
            return False


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "fs_read",
            "description": "Read lines from a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                    "start_line": {"type": "integer", "description": "1-indexed starting line", "default": 1},
                    "line_count": {"type": "integer", "description": "Number of lines to read", "default": 100}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fs_search",
            "description": "Search for a regex pattern across codebase files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex search pattern"},
                    "path": {"type": "string", "description": "Starting directory", "default": "."}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fs_list",
            "description": "List files and subdirectories in a folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path", "default": "."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "patch_apply",
            "description": "Surgically replace an exact code chunk with new code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Target file path"},
                    "target_chunk": {"type": "string", "description": "Exact text in file to replace (empty if creating file)"},
                    "replacement_chunk": {"type": "string", "description": "New replacement text"}
                },
                "required": ["path", "target_chunk", "replacement_chunk"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "proc_exec",
            "description": "Run shell commands in workspace (e.g. pytest, python3 -m unittest).",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"}
                },
                "required": ["command"]
            }
        }
    }
]
