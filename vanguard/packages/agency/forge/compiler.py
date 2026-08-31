"""Forge context compiler and structured distillation strategy.

Complies with:
- RFC 8785 (JCS) deterministic canonicalization for state and digests.
- Strict token budgeting and semantic token pruning.
- Loss-bounded distillation preserving goal, hypothesis, facts, rejected paths, and test evidence.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ...domain.canonicalisation.digest import digest_of
from ...domain.canonicalisation.jcs import canonicalise, canonical_bytes
from ..context.compaction import CompactionStrategy, _receipt_for
from ..context.layers import Block, Layer, estimate_tokens


FORGE_SYSTEM_PROMPT = """You are Vanguard 1-Forge (Reflexive Agentic Micro-Forge).
You operate inside an isolated repository workspace under a fast-cycle TDD strategy.

Operational Directives:
1. Fast-Cycle TDD:
   - First, inspect test and source files using `view_file` or `run_command`.
   - Run the relevant test suite using `run_command` (e.g. `python3 -m unittest discover -s test` or `pytest`) to observe failures and stack traces.
   - Formulate a precise hypothesis and apply targeted minimal changes using `edit_file` or `patch_unified`.
   - Re-run tests immediately. If tests fail, inspect the exact traceback and adapt without repeating the same failed approach.
2. Atomic Verification:
   - Episode completion (`finish_task`) is strictly gated: you cannot finish without a fresh, passing verification run against the current workspace.
   - Do NOT emit conversational summaries without applying code changes and verifying them with tests.
3. Patch Discipline:
   - Write clean, idiomatic code adhering strictly to specifications.
   - Keep patches focused and minimal. Avoid unrelated refactorings or file churn.
"""

FORGE_TOOLS_SCHEMA = [
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
            "description": "Write or overwrite the full content of a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."},
                    "content": {"type": "string", "description": "Full new content to write to the file."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "patch_unified",
            "description": "Apply a unified diff patch atomically to one or more files in the workspace.",
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
            "description": "Execute a shell command (e.g. run test suite) in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The command line to execute."}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and directories in a workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative directory path (default: '.')."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "Signal task completion after confirming that all test assertions pass.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Summary of the resolution and evidence."}
                },
                "required": ["summary"]
            }
        }
    }
]


@dataclass(frozen=True, slots=True)
class ForgeWorkingState:
    """Structured cognitive and environment state preserved across turns and compaction."""

    task_brief: str
    active_hypothesis: str | None = None
    confirmed_facts: tuple[str, ...] = field(default_factory=tuple)
    rejected_hypotheses: tuple[str, ...] = field(default_factory=tuple)
    inspected_files: tuple[str, ...] = field(default_factory=tuple)
    changed_files: tuple[str, ...] = field(default_factory=tuple)
    verification_evidence: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)
    dead_ends: tuple[str, ...] = field(default_factory=tuple)
    next_action: str | None = None
    raw_artifact_refs: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        """Deterministic canonical representation."""
        return {
            "taskBrief": self.task_brief,
            "activeHypothesis": self.active_hypothesis or "",
            "confirmedFacts": list(self.confirmed_facts),
            "rejectedHypotheses": list(self.rejected_hypotheses),
            "inspectedFiles": list(self.inspected_files),
            "changedFiles": list(self.changed_files),
            "verificationEvidence": [dict(v) for v in self.verification_evidence],
            "deadEnds": list(self.dead_ends),
            "nextAction": self.next_action or "",
            "rawArtifactRefs": list(self.raw_artifact_refs),
        }

    def digest(self) -> str:
        """RFC 8785 (JCS) canonical digest."""
        return digest_of(self.to_dict())

    def to_context_block(self) -> str:
        """Render dense, markdown-formatted working state for model context."""
        lines = ["## 1-Forge Working State"]
        lines.append(f"**Task Objective**: {self.task_brief.strip()}")
        if self.active_hypothesis:
            lines.append(f"**Current Hypothesis**: {self.active_hypothesis.strip()}")
        if self.confirmed_facts:
            lines.append("**Confirmed Facts**:\n" + "\n".join(f"- {f}" for f in self.confirmed_facts))
        if self.rejected_hypotheses:
            lines.append("**Rejected Hypotheses / Dead Ends**:\n" + "\n".join(f"- {r}" for r in self.rejected_hypotheses))
        if self.changed_files:
            lines.append("**Modified Files**: " + ", ".join(self.changed_files))
        if self.verification_evidence:
            latest_v = self.verification_evidence[-1]
            status = "PASS" if latest_v.get("exit_code") == 0 else f"FAIL (exit {latest_v.get('exit_code')})"
            lines.append(f"**Latest Test Status**: {status} (tests: {latest_v.get('executed_test_count', 0)}, digest: {latest_v.get('workspace_digest', '')[:12]})")
        if self.next_action:
            lines.append(f"**Next Action**: {self.next_action.strip()}")
        return "\n\n".join(lines)


class ForgeDistillStrategy:
    """`forge-distill` Compaction Strategy.

    Brings context within token ceilings while preserving:
    1. Constitutional floor & task brief.
    2. Structured working state (hypothesis, facts, rejected dead ends, changed files, verification).
    3. Most recent turns for immediate continuity.
    4. Elides bulk outputs into compact receipts with digests.
    """

    def compact(
        self,
        floor: int,
        ceiling: int,
        notes: list[Block],
        dialogue: list[Block],
        options: Mapping[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        opts = options or {}
        keep_recent = int(opts.get("keep_recent_turns", 4))
        elided: list[str] = []
        dropped: list[str] = []

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        if total() <= ceiling:
            return elided, dropped

        # 1. Elide evictable bodies into receipts (oldest first, except recent turns)
        evictable_boundary = max(0, len(dialogue) - (keep_recent * 2))
        for index in range(min(evictable_boundary, len(dialogue))):
            if total() <= ceiling:
                break
            block = dialogue[index]
            if not block.evictable:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        # 2. Extract structured notes & dead ends from older dialogue before dropping
        extracted_dead_ends: list[str] = []
        extracted_facts: list[str] = []

        while total() > ceiling and len(dialogue) > (keep_recent * 2):
            removed = dialogue.pop(0)
            dropped.append(removed.label)
            if removed.label in elided:
                elided.remove(removed.label)

            text_lower = removed.text.lower()
            if "error" in text_lower or "failed" in text_lower or "traceback" in text_lower:
                summary = removed.text[:120].replace("\n", " ").strip()
                extracted_dead_ends.append(f"{removed.label}: {summary}")
            elif "passed" in text_lower or "fixed" in text_lower or "created" in text_lower:
                summary = removed.text[:120].replace("\n", " ").strip()
                extracted_facts.append(f"{removed.label}: {summary}")

        # If any dead ends were extracted, inject a compact structured summary block at the top of dialogue
        if extracted_dead_ends or extracted_facts:
            summary_lines = ["[1-Forge Distillation Summary]"]
            if extracted_facts:
                summary_lines.append("Confirmed: " + " | ".join(extracted_facts[:5]))
            if extracted_dead_ends:
                summary_lines.append("Disproven/Dead Ends: " + " | ".join(extracted_dead_ends[:5]))

            summary_block = Block(
                layer=Layer.DIALOGUE,
                source="forge_distill",
                label="distill_summary",
                text="\n".join(summary_lines),
                evictable=False,
            )
            dialogue.insert(0, summary_block)
            elided.append("distill_summary")

        # 3. If still exceeding ceiling, drop oldest notes
        while total() > ceiling and notes:
            dropped.append(notes.pop(0).label)

        # 4. If still exceeding ceiling, aggressively drop oldest dialogue
        while total() > ceiling and dialogue:
            removed = dialogue.pop(0)
            dropped.append(removed.label)

        return elided, dropped


class ForgeContextCompiler:
    """L1-L5 Prefix-Stable Context Compiler for 1-Forge."""

    def __init__(
        self,
        token_ceiling: int = 64_000,
        system_prompt: str = FORGE_SYSTEM_PROMPT,
        tool_schemas: Sequence[Mapping[str, Any]] = FORGE_TOOLS_SCHEMA,
        environment_map: str = "",
        compaction_strategy: CompactionStrategy | None = None,
    ) -> None:
        self.token_ceiling = token_ceiling
        self.system_prompt = system_prompt
        self.tool_schemas = tool_schemas
        self.environment_map = environment_map
        self.compaction_strategy = compaction_strategy or ForgeDistillStrategy()

    def build_system_block(self) -> Block:
        return Block(
            layer=Layer.SYSTEM,
            source="forge",
            label="system_prompt",
            text=self.system_prompt,
            evictable=False,
        )

    def build_tools_block(self) -> Block:
        # RFC 8785 canonical JSON serialization
        text = canonicalise([dict(t) for t in self.tool_schemas])
        return Block(
            layer=Layer.TOOLS,
            source="forge",
            label="tool_schemas",
            text=text,
            evictable=False,
        )

    def build_environment_block(self) -> Block:
        return Block(
            layer=Layer.ENVIRONMENT,
            source="forge",
            label="environment_map",
            text=self.environment_map,
            evictable=False,
        )

    def compile(
        self,
        brief: str,
        working_state: ForgeWorkingState | None = None,
        notes: Sequence[Block] = (),
        dialogue: Sequence[Block] = (),
        reflex_directive: str | None = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Compile structured context into model-ready chat messages and metadata."""
        l1 = self.build_system_block()
        l2 = self.build_tools_block()
        l3 = self.build_environment_block() if self.environment_map else None

        prefix_blocks = [l1, l2] + ([l3] if l3 else [])
        prefix_tokens = sum(b.token_estimate for b in prefix_blocks)

        task_text = brief
        if working_state:
            task_text = f"{brief}\n\n{working_state.to_context_block()}"
        if reflex_directive:
            task_text = f"{task_text}\n\n[STRATEGY DIRECTIVE]\n{reflex_directive}"

        l4 = Block(
            layer=Layer.TASK,
            source="operator",
            label="task_brief",
            text=task_text,
            evictable=False,
        )
        task_tokens = l4.token_estimate
        floor = prefix_tokens + task_tokens

        notes_list = list(notes)
        dialogue_list = list(dialogue)

        # Apply compaction strategy
        elided, dropped = self.compaction_strategy.compact(
            floor=floor,
            ceiling=self.token_ceiling,
            notes=notes_list,
            dialogue=dialogue_list,
            options={"keep_recent_turns": 4},
        )

        all_blocks = prefix_blocks + [l4] + notes_list + dialogue_list
        total_tokens = sum(b.token_estimate for b in all_blocks)

        # Assemble chat messages for ModelPort
        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": self.system_prompt}
        ]

        user_content_parts = []
        if self.environment_map:
            user_content_parts.append(f"Workspace Environment:\n{self.environment_map}")
        user_content_parts.append(task_text)

        messages.append({"role": "user", "content": "\n\n".join(user_content_parts)})

        # Append dialogue blocks
        for b in dialogue_list:
            if b.source == "model":
                messages.append({"role": "assistant", "content": b.text})
            elif b.source in ("tool", "environment"):
                messages.append({"role": "user", "content": f"[Tool Output - {b.label}]\n{b.text}"})
            else:
                messages.append({"role": "user", "content": b.text})

        context_meta = {
            "total_tokens": total_tokens,
            "token_ceiling": self.token_ceiling,
            "prefix_digest": digest_of([b.identity() for b in prefix_blocks]),
            "context_digest": digest_of([b.identity() for b in all_blocks]),
            "elided_count": len(elided),
            "dropped_count": len(dropped),
            "working_state_digest": working_state.digest() if working_state else "",
        }

        return messages, context_meta
