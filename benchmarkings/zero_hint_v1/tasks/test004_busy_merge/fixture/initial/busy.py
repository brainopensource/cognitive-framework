"""Busy-period coverage for closed integer intervals."""

from __future__ import annotations


def merge_busy(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    ordered = sorted(intervals)
    merged: list[tuple[int, int]] = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start >= last_end:
            merged.append((start, end))
        else:
            merged[-1] = (last_start, max(last_end, end))
    return merged
