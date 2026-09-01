import time
import threading
from collections import OrderedDict
from typing import Any, Optional
from .entry import CacheEntry

class LRUCache:
    def __init__(self, capacity: int, default_ttl: Optional[float] = None):
        if capacity <= 0:
            raise ValueError('Capacity must be positive')
        self.capacity = capacity
        self.default_ttl = default_ttl
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()

    def _purge_stale(self, now: float) -> None:
        """Remove all expired entries from the store."""
        stale_keys = [
            key for key, entry in self._store.items()
            if entry.is_expired(now)
        ]
        for key in stale_keys:
            del self._store[key]

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            now = time.monotonic()
            self._purge_stale(now)
            if key not in self._store:
                return None
            entry = self._store[key]
            self._store.move_to_end(key)
            return entry.value

    def put(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        with self._lock:
            now = time.monotonic()
            self._purge_stale(now)
            effective_ttl = ttl if ttl is not None else self.default_ttl
            if key in self._store:
                self._store.move_to_end(key)
            self._store[key] = CacheEntry(key, value, effective_ttl, now)
            while len(self._store) > self.capacity:
                self._store.popitem(last=False)