from __future__ import annotations

import unittest

from rate_limit import RateLimiter


class RateLimiterTests(unittest.TestCase):
    def test_independent_keys(self) -> None:
        limiter = RateLimiter(max_requests=1, window_seconds=10)
        self.assertTrue(limiter.allow("alpha", 0.0))
        self.assertTrue(limiter.allow("beta", 0.0))
        self.assertFalse(limiter.allow("alpha", 1.0))

    def test_rejects_when_the_window_is_still_occupied(self) -> None:
        limiter = RateLimiter(max_requests=2, window_seconds=10)
        self.assertTrue(limiter.allow("api", 0.0))
        self.assertTrue(limiter.allow("api", 9.0))
        self.assertFalse(limiter.allow("api", 10.0))

    def test_admits_after_the_oldest_request_leaves_the_interval(self) -> None:
        limiter = RateLimiter(max_requests=2, window_seconds=10)
        self.assertTrue(limiter.allow("api", 0.0))
        self.assertTrue(limiter.allow("api", 9.0))
        self.assertTrue(limiter.allow("api", 10.1))
        self.assertFalse(limiter.allow("api", 10.2))


if __name__ == "__main__":
    unittest.main()
