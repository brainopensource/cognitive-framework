"""Least-recently-used eviction order tracker."""

from __future__ import annotations

from collections import OrderedDict


class LRUOrder:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self._order: OrderedDict[str, None] = OrderedDict()

    def touch(self, key: str) -> None:
        """Mark key as most recently used."""
        if key in self._order:
            self._order.move_to_end(key)
        else:
            self._order[key] = None

    def observe_get(self, key: str) -> None:
        # BUG: reading a key should also count as a use and move it to the
        # most-recently-used end, but this is a no-op, so a hot key can still
        # be evicted as if it were never read.
        pass

    def evict_candidate(self) -> str | None:
        if not self._order:
            return None
        return next(iter(self._order))

    def remove(self, key: str) -> None:
        self._order.pop(key, None)

    def is_full(self) -> bool:
        return len(self._order) >= self.capacity
