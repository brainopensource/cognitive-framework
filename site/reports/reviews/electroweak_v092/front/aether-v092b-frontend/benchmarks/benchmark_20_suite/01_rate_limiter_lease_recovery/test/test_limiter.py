import unittest
import time
from src.rate_limiter import RateLimiter
from src.governor import ConcurrencyGovernor

class TestRateLimiter(unittest.TestCase):
    def test_acquire_and_release(self):
        limiter = RateLimiter(capacity=100)
        self.assertTrue(limiter.acquire("lease-1", 40))
        self.assertEqual(limiter.available, 60)
        self.assertTrue(limiter.release("lease-1"))
        self.assertEqual(limiter.available, 100)

    def test_clean_expired_refunds_tokens(self):
        limiter = RateLimiter(capacity=100)
        self.assertTrue(limiter.acquire("lease-exp", 40, ttl_seconds=1.0))
        self.assertEqual(limiter.available, 60)
        
        # Fast forward time to expire lease
        future_time = time.time() + 10.0
        cleaned = limiter.clean_expired(future_time)
        self.assertEqual(cleaned, 1)
        # Falsifier Assertion: available capacity MUST be refunded back to 100
        self.assertEqual(limiter.available, 100, f"Leakage detected: expected 100 available, got {limiter.available}")

if __name__ == "__main__":
    unittest.main()
