Fix the LRUCache in `lru/cache.py` and `lru/entry.py`. Stale items must be purged upon `get()` and `put()`. The cache must respect capacity limits and use monotonic time.
