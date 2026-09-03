"""Booking scheduler that rejects overlapping (including touching) bookings."""

from __future__ import annotations

from src.intervals import merge_intervals


class Scheduler:
    def __init__(self):
        self._bookings: list[tuple[float, float]] = []

    def has_conflict(self, start: float, end: float) -> bool:
        candidate = self._bookings + [(start, end)]
        merged = merge_intervals(candidate)
        return len(merged) < len(candidate)

    def book(self, start: float, end: float) -> bool:
        if self.has_conflict(start, end):
            return False
        self._bookings.append((start, end))
        return True
