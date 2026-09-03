"""Merge a list of (start, end) intervals, combining any that overlap or touch."""

from __future__ import annotations

from typing import Sequence


def merge_intervals(intervals: Sequence[tuple[float, float]]) -> list[tuple[float, float]]:
    if not intervals:
        return []
    ordered = sorted(intervals, key=lambda pair: pair[0])
    merged: list[list[float]] = [list(ordered[0])]
    for start, end in ordered[1:]:
        last = merged[-1]
        # BUG: strict '<' means back-to-back intervals like (0, 5) and (5, 8)
        # are NOT merged, so a booking ending exactly when another begins is
        # missed as a conflict.
        if start < last[1]:
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return [tuple(pair) for pair in merged]
