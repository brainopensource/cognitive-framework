"""
Unit tests for SlidingWindowLimiter.
Falsifies rate limit enforcement, boundary expiration, and state isolation.
"""

import unittest
import sys
from pathlib import Path

# Add fixture dir to sys.path
FIXTURE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(FIXTURE_DIR))

from sliding_window_limiter import SlidingWindowLimiter

class TestSlidingWindowLimiter(unittest.TestCase):
    def test_basic_capacity_allowance(self):
        limiter = SlidingWindowLimiter(max_requests=2, window_seconds=10.0)
        self.assertTrue(limiter.allow(1.0))
        self.assertTrue(limiter.allow(2.0))
        self.assertFalse(limiter.allow(3.0), "Third request within 10s should be denied")

    def test_boundary_expiration(self):
        """
        An event at t=0.0 with window=10.0 MUST expire when now=10.0 (cutoff = 10.0 - 10.0 = 0.0).
        At now=10.0, the event at 0.0 is <= cutoff, so it must be evicted, allowing a new request.
        """
        limiter = SlidingWindowLimiter(max_requests=1, window_seconds=10.0)
        self.assertTrue(limiter.allow(0.0), "Initial request at 0.0 should be allowed")
        self.assertFalse(limiter.allow(5.0), "Request at 5.0 should be throttled")
        self.assertTrue(limiter.allow(10.0), "Request at exact boundary 10.0 should be allowed because 0.0 expired")

    def test_denied_request_does_not_consume_quota(self):
        """
        A denied request should NOT permanently occupy a slot in the window.
        """
        limiter = SlidingWindowLimiter(max_requests=1, window_seconds=10.0)
        self.assertTrue(limiter.allow(1.0))
        self.assertFalse(limiter.allow(2.0))
        self.assertFalse(limiter.allow(3.0))
        # Now at t=11.1, the request at 1.0 has expired.
        # If the denied requests at 2.0 and 3.0 were recorded, this would wrongly fail.
        self.assertTrue(limiter.allow(11.1), "At t=11.1, capacity should be restored if denied calls weren't recorded")

if __name__ == "__main__":
    unittest.main()
