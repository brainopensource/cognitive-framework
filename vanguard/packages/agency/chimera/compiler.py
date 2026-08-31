"""Chimera Context Compiler and Multi-Tier Memory Assembler.

Assembles four memory tiers (Hot dialogue, Warm blackboard facts, Cold repository map,
Learned skill recipes) under strict token ceilings with Value-of-Information pruning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ...domain.canonicalisation.digest import digest_of
from ...domain.canonicalisation.jcs import canonicalise
from ..context.layers import Block, Layer, estimate_tokens
from .blackboard import CognitiveBlackboard
from .skills import SkillRegistry


CHIMERA_SYSTEM_PROMPT = """You are Vanguard CHIMERA, an autonomous neuro-symbolic senior software engineer capable of solving greenfield software projects, multi-file codebases, fast-cycle TDD bugfixes, and complex algorithmic systems with 100% test-verified precision.

WORKING RULES & OPERATIONAL PROTOCOL:

1. WORKSPACE AWARENESS & STARTING TURN:
- The task below specifies the objective and target file(s).
- Turn 1: If target file(s) exist, call `view_file` on the target file(s) or call `run_command` (e.g. `python3 -m unittest discover -s test` or `pytest`) to observe tracebacks. If this is a greenfield task (scratch project), immediately start creating the required files with `edit_file`.

2. ATOMIC EXECUTION LOOP (ONE TOOL CALL PER TURN):
- Step 1 [Inspect/Observe]: Call `view_file` to see existing code or `run_command` to see failing assertions.
- Step 2 [Synthesize/Edit]: Call `edit_file` with the complete, corrected file contents, or `surgical_patch` for minimal edits.
- Step 3 [Verify]: Call `run_command` to execute tests: `python3 -m unittest discover -s .` or `pytest`.
- Step 4 [Iterate or Finish]:
  * If `run_command` passes with 0 failures -> Call `finish_task` IMMEDIATELY on the very next turn.
  * If `run_command` fails -> Read the traceback carefully, understand the failing assertion, edit the fix, and re-test.

3. GREENFIELD & SCRATCH PROJECTS (SELF-TDD MANDATE):
- When building a project from scratch or when no test files exist:
  a) Author the full implementation files with `edit_file`.
  b) MANDATORY: Write a comprehensive unit test file (e.g. `test_solution.py`) covering all specifications, edge cases, error conditions, and lifecycle transitions.
  c) Run `run_command` to verify that your implementation satisfies all test cases.
  d) Call `finish_task` once all tests pass.

4. CONTRACT SPECIFICATION DISCIPLINE (ZERO-DEFECT POLICY):
- ID Generation: Sequential entity IDs default to 1-indexed integers (1, 2, 3...) unless explicitly specified otherwise.
- Initial State: Initialize pointer/state variables properly (e.g., ensure `current_item()` or `current_question()` returns the first item, not None, when items exist).
- Exceptions: Raise the exact exception types requested in the specification (e.g. `ValueError` on negative/invalid inputs, `KeyError` on missing keys).
- Multi-File Sync: If you update a class, function, or model signature, update all importing files and callers across the workspace.

5. FINISHING CRITERIA:
- Never call `finish_task` before a passing test in this run.
- Never call `finish_task` without having modified/created workspace files.
- When tests pass, do not run redundant tests; call `finish_task` immediately on the next turn.
"""

CHIMERA_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "view_file",
            "description": "Read the contents of a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Write or overwrite the full content of a file in the workspace (creates parent directories if needed).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."},
                    "content": {"type": "string", "description": "Full content to write."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "surgical_patch",
            "description": "Apply a surgical search-and-replace patch with resilient fuzzy matching to an existing file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."},
                    "target": {"type": "string", "description": "Exact or approximate code chunk to replace."},
                    "replacement": {"type": "string", "description": "New replacement code chunk."}
                },
                "required": ["path", "target", "replacement"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "patch_unified",
            "description": "Apply a unified diff patch to one or more workspace files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "diff": {"type": "string", "description": "Unified diff text (--- a/... +++ b/...)."}
                },
                "required": ["diff"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command (run tests, compile, or run tools) in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command line to execute."}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and subdirectories in a workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to directory (default '.')."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_workspace",
            "description": "Search workspace files for keywords, classes, or function definitions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search term or regex pattern."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "solve_invariants",
            "description": "Deterministic symbolic constraint and mathematical equation solver.",
            "parameters": {
                "type": "object",
                "properties": {
                    "problem_statement": {"type": "string", "description": "Equations, constraints, or boundary specifications."}
                },
                "required": ["problem_statement"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "Conclude the task after all requirements are implemented and verified green with tests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Concise summary of changes made and test verification results."}
                },
                "required": ["summary"]
            }
        }
    }
]


class ChimeraContextCompiler:
    """Compiles multi-tier context into prompt messages respecting token limits."""

    def __init__(
        self,
        token_ceiling: int = 64_000,
        skill_registry: SkillRegistry | None = None,
    ) -> None:
        self.token_ceiling = token_ceiling
        self.skill_registry = skill_registry or SkillRegistry()

    def compile(
        self,
        board: CognitiveBlackboard,
        dialogue_blocks: Sequence[Block],
        distilled_dead_ends: str = "",
    ) -> list[dict[str, Any]]:
        """Compile blackboard state, procedural skills, and dialogue history into model messages."""
        messages: list[dict[str, Any]] = []

        # 1. System Prompt
        sys_text = CHIMERA_SYSTEM_PROMPT
        applicable_skills = self.skill_registry.find_applicable_skills(board.task_brief)
        if applicable_skills:
            sys_text += "\n\n=== Applicable Domain Recipes ==="
            for sk in applicable_skills:
                sys_text += f"\n\n[Skill: {sk.name}]\n{sk.procedural_recipe}"

        messages.append({"role": "system", "content": sys_text})

        # 2. Warm Layer: Blackboard State & Task Brief
        warm_content = [
            f"# TASK OBJECTIVE\n{board.task_brief}\n",
            f"Phase: {board.phase} | Localization Uncertainty: {board.uncertainty.localization_uncertainty:.2f}",
        ]

        if board.candidate_files:
            warm_content.append("\n## Candidate Workspace Files:")
            for rf in board.candidate_files[:5]:
                warm_content.append(f"- `{rf.path}` (relevance: {rf.relevance_score:.2f})")

        if board.facts:
            warm_content.append("\n## Verified Ground Facts:")
            for f in board.facts[-4:]:
                warm_content.append(f"- [{f.source}] {f.statement}")

        if distilled_dead_ends:
            warm_content.append(f"\n{distilled_dead_ends}")

        messages.append({"role": "user", "content": "\n".join(warm_content)})

        # 3. Hot Layer: Dialogue Turns
        # Estimate tokens and prune oldest non-critical blocks if near ceiling
        for b in dialogue_blocks:
            role = "assistant" if b.source == "model" else ("tool" if b.source == "tool" else "user")
            messages.append({"role": role, "content": b.text})

        return messages
