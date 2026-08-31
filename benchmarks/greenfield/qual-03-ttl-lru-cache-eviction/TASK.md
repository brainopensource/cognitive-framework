# Task: QUAL-03 TTL + LRU Cache Eviction

## Brief
`src/ttl_cache.py` combines an LRU cache (`src/lru.py`) with TTL expiry
(`src/ttl.py`) into one `TTLCache`. `test_ttl_cache.py` currently fails.
There are two independent bugs, one in `src/lru.py` and one in `src/ttl.py`.
Find and fix both so that all tests pass.
Verify using `["python3", "-m", "unittest", "test_ttl_cache.py"]`.
