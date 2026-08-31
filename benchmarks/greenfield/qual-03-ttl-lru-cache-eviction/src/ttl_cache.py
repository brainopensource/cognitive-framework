"""TTL + LRU cache combining src/lru.py and src/ttl.py."""

from __future__ import annotations

from typing import Any

from src.lru import LRUOrder
from src.ttl import TTLClock


class TTLCache:
    def __init__(self, capacity: int, ttl_seconds: float, clock=None):
        self._data: dict[str, Any] = {}
        self._order = LRUOrder(capacity)
        self._ttl = TTLClock(ttl_seconds, clock=clock)

    def put(self, key: str, value: Any) -> None:
        if key not in self._data and self._order.is_full():
            victim = self._order.evict_candidate()
            if victim is not None:
                self._data.pop(victim, None)
                self._order.remove(victim)
                self._ttl.discard(victim)
        self._data[key] = value
        self._order.touch(key)
        self._ttl.set(key)

    def get(self, key: str) -> Any:
        if key not in self._data:
            return None
        if self._ttl.is_expired(key):
            self._data.pop(key, None)
            self._order.remove(key)
            self._ttl.discard(key)
            return None
        self._order.observe_get(key)
        return self._data[key]
