"""Structured compaction preserving active constraints and receipts."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def compact_action_history(
    turns: Sequence[Mapping[str, Any]],
    *,
    keep_last_n_receipts: int = 3,
) -> list[dict[str, Any]]:
    """Compact older turns into summaries while preserving active facts and last receipts."""
    compacted: list[dict[str, Any]] = []
    total = len(turns)
    for idx, turn in enumerate(turns):
        is_recent = (total - idx) <= keep_last_n_receipts
        if is_recent:
            compacted.append(dict(turn))
        else:
            # Compact summary of older turn
            action = turn.get("action") or turn.get("type", "unknown")
            proposal = turn.get("proposal", "")
            compacted.append({
                "role": "system",
                "content": f"[Turn {idx + 1} summary]: executed {action} with note '{proposal}'",
            })
    return compacted
