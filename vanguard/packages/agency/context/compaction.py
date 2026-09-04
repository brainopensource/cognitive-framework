"""Compaction strategy protocol and registry (S8-B-02, VG-03 §10.3).

Provides pluggable dialogue compaction strategies selected by manifest context_policy
and frozen at composition time.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .layers import Block, Layer, GOAL_ECHO_SOURCE, PINNED_L4_SOURCES


def _receipt_for(block: Block) -> Block:
    """What `result_eviction` leaves behind: the fact, without the body.

    `VG-03 §10.3` — "keep that a file was read; drop the body once superseded".
    """
    return Block(
        layer=block.layer,
        source=block.source,
        label=block.label,
        text=f"[{block.label} from {block.source}: {block.byte_length} bytes elided after use]",
        evictable=False,
    )


def _drop_flexible_notes(notes: list[Block], dropped: list[str], total, ceiling: int) -> None:
    """T-15: drop flexible L4 notes under pressure; never FEATURE_SPEC pinned sources."""
    while total() > ceiling and notes:
        index = next((i for i, block in enumerate(notes) if block.source not in PINNED_L4_SOURCES), None)
        if index is None:
            break
        dropped.append(notes.pop(index).label)


def _drop_flexible_dialogue(dialogue: list[Block], dropped: list[str], elided: list[str], total, ceiling: int) -> None:
    """T-36: drop L5 under pressure; the goal echo at the tail is not evictable."""
    while total() > ceiling and dialogue:
        index = next((i for i, block in enumerate(dialogue) if block.source != GOAL_ECHO_SOURCE), None)
        if index is None:
            break
        removed = dialogue.pop(index)
        dropped.append(removed.label)
        if removed.label in elided:
            elided.remove(removed.label)


@runtime_checkable
class CompactionStrategy(Protocol):
    """Protocol for bringing context within token ceilings (S8-B-02)."""

    def compact(
        self,
        floor: int,
        ceiling: int,
        notes: list[Block],
        dialogue: list[Block],
        options: Mapping[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        """Compacts notes and dialogue in-place to fit within ceiling.

        Returns (elided_labels, dropped_labels).
        """
        ...


class ResultEvictionStrategy:
    """Default result eviction strategy (VG-03 §10.3).

    1. Elides evictable dialogue blocks into compact receipts (oldest first).
    2. Drops oldest dialogue blocks if still over ceiling.
    3. Drops oldest notes if still over ceiling.
    """

    def compact(
        self,
        floor: int,
        ceiling: int,
        notes: list[Block],
        dialogue: list[Block],
        options: Mapping[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        elided: list[str] = []
        dropped: list[str] = []

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        for index, block in enumerate(dialogue):
            if total() <= ceiling:
                break
            if not block.evictable or block.source == GOAL_ECHO_SOURCE:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        _drop_flexible_dialogue(dialogue, dropped, elided, total, ceiling)

        _drop_flexible_notes(notes, dropped, total, ceiling)

        return elided, dropped


class RecencyWindowStrategy:
    """Recency window compaction strategy (S8-B-02).

    1. Retains at most `maxItems` recent dialogue entries, dropping older entries.
    2. Elides evictable dialogue bodies into receipts to fit within token ceiling.
    3. Drops oldest dialogue fragments if still over ceiling.
    4. Drops oldest notes if still over ceiling.
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
        max_items = opts.get("maxItems") or opts.get("max_items") or 64
        try:
            max_items = int(max_items)
        except (ValueError, TypeError):
            max_items = 64

        elided: list[str] = []
        dropped: list[str] = []

        # 1. Truncate dialogue to the recency window limit; keep the goal echo.
        while len([b for b in dialogue if b.source != GOAL_ECHO_SOURCE]) > max_items:
            index = next((i for i, block in enumerate(dialogue) if block.source != GOAL_ECHO_SOURCE), None)
            if index is None:
                break
            removed = dialogue.pop(index)
            dropped.append(removed.label)

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        # 2. Result eviction over remaining dialogue
        for index, block in enumerate(dialogue):
            if total() <= ceiling:
                break
            if not block.evictable or block.source == GOAL_ECHO_SOURCE:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        # 3. If still exceeding ceiling, drop oldest flexible dialogue items
        _drop_flexible_dialogue(dialogue, dropped, elided, total, ceiling)

        # 4. If still exceeding ceiling, drop oldest flexible notes
        _drop_flexible_notes(notes, dropped, total, ceiling)

        return elided, dropped


@dataclass
class StructuredRecord:
    """Structured compaction state tracking (S10-B-03, VG-03 §10.4)."""

    decisions: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    open_items: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    dead_ends: list[str] = field(default_factory=list)

    def to_summary_text(self) -> str:
        lines = ["[Structured Consolidation Record]"]
        if self.decisions:
            lines.append("Decisions: " + "; ".join(self.decisions))
        if self.invariants:
            lines.append("Invariants: " + "; ".join(self.invariants))
        if self.open_items:
            lines.append("Open: " + "; ".join(self.open_items))
        if self.artifacts:
            lines.append("Artifacts: " + "; ".join(self.artifacts))
        if self.dead_ends:
            lines.append("DeadEnds (abandoned paths): " + "; ".join(self.dead_ends))
        return "\n".join(lines)


class StructuredConsolidateStrategy:
    """Consolidates dialogue into a StructuredRecord with deadEnds tracking (S10-B-03).
    
    Prevents re-exploring abandoned paths by preserving explicit deadEnds while reducing transcript tokens.
    """

    def compact(
        self,
        floor: int,
        ceiling: int,
        notes: list[Block],
        dialogue: list[Block],
        options: Mapping[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        elided: list[str] = []
        dropped: list[str] = []

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        if total() <= ceiling:
            return elided, dropped

        # Extract structured information from dialogue blocks to be consolidated
        rec = StructuredRecord()
        to_consolidate: list[Block] = []

        while total() > ceiling and dialogue:
            index = next((i for i, block in enumerate(dialogue) if block.source != GOAL_ECHO_SOURCE), None)
            if index is None:
                break
            b = dialogue.pop(index)
            dropped.append(b.label)
            to_consolidate.append(b)
            # Scan text for dead ends / decisions
            if "failed" in b.text.lower() or "error" in b.text.lower() or "dead end" in b.text.lower():
                rec.dead_ends.append(f"{b.label}: {b.text[:60].strip()}")
            elif "decision" in b.text.lower() or "selected" in b.text.lower():
                rec.decisions.append(f"{b.label}: {b.text[:60].strip()}")

        if to_consolidate:
            summary_block = Block(
                layer=Layer.DIALOGUE,
                source="structured_consolidate",
                label="structured_record",
                text=rec.to_summary_text(),
                evictable=False,
            )
            dialogue.insert(0, summary_block)
            elided.append("structured_record")

            # If inserting summary_block pushed total over ceiling, drop remaining un-consolidated blocks
            while total() > ceiling and len(dialogue) > 1:
                index = next(
                    (i for i, block in enumerate(dialogue)
                     if block.source != GOAL_ECHO_SOURCE and block.label != "structured_record"),
                    None,
                )
                if index is None:
                    break
                b = dialogue.pop(index)
                dropped.append(b.label)

        _drop_flexible_notes(notes, dropped, total, ceiling)

        return elided, dropped


class UnknownCompactionStrategyError(ValueError):
    """Raised when an unknown compaction strategy is requested (EVO-13 fail-closed)."""


COMPACTION_REGISTRY: dict[str, CompactionStrategy] = {
    "result_eviction": ResultEvictionStrategy(),
    "result-eviction": ResultEvictionStrategy(),
    "recency_window": RecencyWindowStrategy(),
    "recency-window": RecencyWindowStrategy(),
    "structured_consolidate": StructuredConsolidateStrategy(),
    "structured-consolidate": StructuredConsolidateStrategy(),
}


def resolve_compaction_strategy(
    policy: Mapping[str, Any] | str | None,
) -> tuple[CompactionStrategy, Mapping[str, Any]]:
    """Resolve compaction strategy and options from manifest context_policy dict or name.

    Fails closed if the strategy identifier is unknown.
    """
    if policy is None:
        return COMPACTION_REGISTRY["recency-window"], {}

    if isinstance(policy, str):
        kind = policy
        options: Mapping[str, Any] = {}
    elif isinstance(policy, Mapping):
        kind = str(policy.get("kind") or policy.get("strategy") or "recency-window")
        options = policy
    else:
        return COMPACTION_REGISTRY["recency-window"], {}

    strategy = COMPACTION_REGISTRY.get(kind)
    if strategy is None:
        raise UnknownCompactionStrategyError(
            f"unknown compaction strategy {kind!r}; registered: {sorted(COMPACTION_REGISTRY)}"
        )
    return strategy, options
