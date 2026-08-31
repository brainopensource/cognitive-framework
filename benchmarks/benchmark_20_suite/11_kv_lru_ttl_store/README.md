# Greenfield PRD: Thread-Safe In-Memory KV Store with LRU and TTL

## Objective
Implement `LRUTTLStore` in `src/store.py`.

## Requirements
- `LRUTTLStore(capacity: int, default_ttl: float | None = None)`
- `put(key: str, value: Any, ttl: float | None = None) -> None`: Inserts or updates a key. If size exceeds `capacity`, evicts the least recently used item.
- `get(key: str) -> Any | None`: Retrieves value. Returns `None` if key does not exist or has expired. Updates LRU order on hit.
- `delete(key: str) -> bool`: Deletes a key, returning `True` if found.
- `size() -> int`: Returns current count of unexpired keys.
- `clear() -> None`: Clears all entries.
- Thread-safe using `threading.RLock`.
- Monotonic time calculation using `time.monotonic()`.
