import unittest
from src.ttl_cache import TTLCache


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def advance(self, seconds: float) -> None:
        self.now += seconds

    def __call__(self) -> float:
        return self.now


class TestTTLCache(unittest.TestCase):
    def test_get_refreshes_lru_position(self):
        clock = FakeClock()
        cache = TTLCache(capacity=2, ttl_seconds=100, clock=clock)
        cache.put("a", 1)
        cache.put("b", 2)
        # Touch "a" so it becomes the most recently used.
        self.assertEqual(cache.get("a"), 1)
        # Inserting "c" should evict "b" (least recently used), not "a".
        cache.put("c", 3)
        self.assertEqual(cache.get("a"), 1)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("c"), 3)

    def test_key_expires_at_exact_ttl_boundary(self):
        clock = FakeClock()
        cache = TTLCache(capacity=2, ttl_seconds=10, clock=clock)
        cache.put("a", 1)
        clock.advance(10.0)
        # At the exact TTL boundary the key must be treated as expired.
        self.assertIsNone(cache.get("a"))

    def test_key_valid_before_ttl_boundary(self):
        clock = FakeClock()
        cache = TTLCache(capacity=2, ttl_seconds=10, clock=clock)
        cache.put("a", 1)
        clock.advance(9.0)
        self.assertEqual(cache.get("a"), 1)


if __name__ == "__main__":
    unittest.main()
