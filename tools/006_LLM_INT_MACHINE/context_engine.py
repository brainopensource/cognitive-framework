"""Context compilation, prefix caching stability, and dialogue compaction for 006_LLM_INT_MACHINE."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

try:
    from .config import HarnessConfig
except ImportError:
    from config import HarnessConfig


class ContextLayer(str, Enum):
    SYSTEM = "L1_SYSTEM"
    TOOLS = "L2_TOOLS"
    ENVIRONMENT = "L3_ENVIRONMENT"
    TASK = "L4_TASK"
    DIALOGUE = "L5_DIALOGUE"


@dataclass
class ContextBlock:
    layer: ContextLayer
    source: str
    label: str
    text: str
    evictable: bool = False
    
    @property
    def token_estimate(self) -> int:
        if not self.text:
            return 0
        return max(1, (len(self.text) + 3) // 4)


@dataclass
class StructuredConsolidationRecord:
    decisions: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    dead_ends: list[str] = field(default_factory=list)
    
    def render(self) -> str:
        lines = ["[Structured Context Consolidation]"]
        if self.decisions:
            lines.append("Decisions: " + "; ".join(self.decisions))
        if self.invariants:
            lines.append("Invariants: " + "; ".join(self.invariants))
        if self.dead_ends:
            lines.append("Dead-Ends (DO NOT REPEAT): " + "; ".join(self.dead_ends))
        return "\n".join(lines)


class ContextEngine:
    def __init__(self, config: HarnessConfig, system_prompt: str, task_brief: str) -> None:
        self.config = config
        self.system_prompt = system_prompt
        self.task_brief = task_brief
        self.dialogue_blocks: list[ContextBlock] = []
        self.structured_record = StructuredConsolidationRecord()
        self.elided_count = 0

    def add_turn_user(self, text: str, label: str = "user_input") -> None:
        block = ContextBlock(
            layer=ContextLayer.DIALOGUE,
            source="user",
            label=label,
            text=text,
            evictable=False,
        )
        self.dialogue_blocks.append(block)

    def add_turn_assistant(self, text: str, label: str = "model_proposal") -> None:
        block = ContextBlock(
            layer=ContextLayer.DIALOGUE,
            source="assistant",
            label=label,
            text=text,
            evictable=False,
        )
        self.dialogue_blocks.append(block)

    def add_tool_receipt(self, tool_name: str, output: str, is_large: bool = False) -> None:
        block = ContextBlock(
            layer=ContextLayer.DIALOGUE,
            source="tool",
            label=f"receipt_{tool_name}",
            text=f"[{tool_name} output]:\n{output}",
            evictable=is_large or len(output) > 800,
        )
        self.dialogue_blocks.append(block)

    def record_dead_end(self, reason: str) -> None:
        if self.config.use_dead_ends_tracking:
            self.structured_record.dead_ends.append(reason)

    def compact(self, ceiling_tokens: int | None = None) -> int:
        ceiling = ceiling_tokens or self.config.token_ceiling
        
        def total_tokens() -> int:
            return sum(b.token_estimate for b in self.dialogue_blocks)

        if total_tokens() <= ceiling or not self.config.use_dialogue_compaction:
            return 0

        elided = 0
        # 1. Result Eviction on evictable tool blocks (oldest first)
        for i, block in enumerate(self.dialogue_blocks):
            if total_tokens() <= ceiling:
                break
            if block.evictable:
                old_bytes = len(block.text)
                self.dialogue_blocks[i] = ContextBlock(
                    layer=ContextLayer.DIALOGUE,
                    source=block.source,
                    label=block.label,
                    text=f"[{block.label}: {old_bytes} bytes elided after consumption]",
                    evictable=False,
                )
                elided += 1
                self.elided_count += 1

        # 2. Structured consolidation if still exceeding ceiling
        if total_tokens() > ceiling and len(self.dialogue_blocks) > 2:
            oldest_blocks = self.dialogue_blocks[:-2]
            for b in oldest_blocks:
                if "fail" in b.text.lower() or "error" in b.text.lower():
                    self.structured_record.dead_ends.append(f"{b.label}: {b.text[:80].strip()}")
                elif "decision" in b.text.lower() or "fix" in b.text.lower():
                    self.structured_record.decisions.append(f"{b.label}: {b.text[:80].strip()}")
            
            summary_block = ContextBlock(
                layer=ContextLayer.DIALOGUE,
                source="system",
                label="structured_summary",
                text=self.structured_record.render(),
                evictable=False,
            )
            self.dialogue_blocks = [summary_block] + self.dialogue_blocks[-2:]

        return elided

    def compile_messages(self) -> list[dict[str, str]]:
        self.compact()
        messages: list[dict[str, str]] = []

        messages.append({"role": "system", "content": self.system_prompt})

        task_msg = f"# TASK BRIEF\n{self.task_brief}"
        if self.structured_record.dead_ends and self.config.use_dead_ends_tracking:
            task_msg += f"\n\n## AVOIDED DEAD ENDS:\n" + "\n".join(f"- {d}" for d in self.structured_record.dead_ends[-5:])
        
        messages.append({"role": "user", "content": task_msg})

        for block in self.dialogue_blocks:
            role = "assistant" if block.source == "assistant" else "user"
            messages.append({"role": role, "content": block.text})

        return messages
