import unittest
from src.token_bucket import TokenBucket
from src.limiter import RateLimiter


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def advance(self, seconds: float) -> None:
        self.now += seconds

    def __call__(self) -> float:
        return self.now


class TestTokenBucket(unittest.TestCase):
    def test_refill_is_capped_at_capacity(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=5, refill_rate_per_sec=1, clock=clock)
        # Drain nothing, then idle for a very long time: tokens must not
        # exceed capacity even though refill math would otherwise overshoot.
        clock.advance(1000.0)
        bucket.try_consume(0.0)  # trigger a refill without consuming
        self.assertLessEqual(bucket.tokens, bucket.capacity)

    def test_consume_denied_when_empty(self):
        clock = FakeClock()
        bucket = TokenBucket(capacity=2, refill_rate_per_sec=1, clock=clock)
        self.assertTrue(bucket.try_consume(2))
        self.assertFalse(bucket.try_consume(1))

    def test_limiter_allows_then_denies_then_recovers(self):
        clock = FakeClock()
        limiter = RateLimiter(capacity=1, refill_rate_per_sec=1, clock=clock)
        self.assertTrue(limiter.allow())
        self.assertFalse(limiter.allow())
        clock.advance(1.0)
        self.assertTrue(limiter.allow())


if __name__ == "__main__":
    unittest.main()
