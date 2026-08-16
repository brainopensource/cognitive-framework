from __future__ import annotations

import unittest

from rate_limit import RateLimiter


class RateLimiterOracle(unittest.TestCase):
    def test_dense_arrivals_near_the_trailing_edge(self) -> None:
        limiter = RateLimiter(max_requests=3, window_seconds=5)
        self.assertTrue(limiter.allow("k", 0.0))
        self.assertTrue(limiter.allow("k", 2.0))
        self.assertTrue(limiter.allow("k", 4.9))
        self.assertFalse(limiter.allow("k", 5.0))
        self.assertTrue(limiter.allow("k", 5.1))

    def test_idle_key_does_not_inherit_quota(self) -> None:
        limiter = RateLimiter(max_requests=1, window_seconds=3)
        self.assertTrue(limiter.allow("one", 0.0))
        self.assertFalse(limiter.allow("one", 2.9))
        self.assertTrue(limiter.allow("two", 2.9))


if __name__ == "__main__":
    unittest.main()
