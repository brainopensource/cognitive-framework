"""Compaction strategy protocol and registry (S8-B-02, VG-03 §10.3).

Provides pluggable dialogue compaction strategies selected by manifest context_policy
and frozen at composition time.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from .layers import Block, Layer


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
            if not block.evictable:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        while total() > ceiling and dialogue:
            removed = dialogue.pop(0)
            dropped.append(removed.label)
            if removed.label in elided:
                elided.remove(removed.label)

        while total() > ceiling and notes:
            dropped.append(notes.pop(0).label)

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

        # 1. Truncate dialogue to the recency window limit
        while len(dialogue) > max_items:
            removed = dialogue.pop(0)
            dropped.append(removed.label)

        def total() -> int:
            return floor + sum(b.token_estimate for b in notes) + sum(b.token_estimate for b in dialogue)

        # 2. Result eviction over remaining dialogue
        for index, block in enumerate(dialogue):
            if total() <= ceiling:
                break
            if not block.evictable:
                continue
            dialogue[index] = _receipt_for(block)
            elided.append(block.label)

        # 3. If still exceeding ceiling, drop oldest dialogue items
        while total() > ceiling and dialogue:
            removed = dialogue.pop(0)
            dropped.append(removed.label)
            if removed.label in elided:
                elided.remove(removed.label)

        # 4. If still exceeding ceiling, drop oldest notes
        while total() > ceiling and notes:
            dropped.append(notes.pop(0).label)

        return elided, dropped


COMPACTION_REGISTRY: dict[str, CompactionStrategy] = {
    "result_eviction": ResultEvictionStrategy(),
    "result-eviction": ResultEvictionStrategy(),
    "recency_window": RecencyWindowStrategy(),
    "recency-window": RecencyWindowStrategy(),
}


def resolve_compaction_strategy(
    policy: Mapping[str, Any] | str | None,
) -> tuple[CompactionStrategy, Mapping[str, Any]]:
    """Resolve compaction strategy and options from manifest context_policy dict or name."""
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
        strategy = COMPACTION_REGISTRY["recency-window"]
    return strategy, options
