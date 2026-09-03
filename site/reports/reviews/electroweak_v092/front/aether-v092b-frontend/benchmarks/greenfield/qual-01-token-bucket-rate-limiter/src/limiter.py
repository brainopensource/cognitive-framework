"""Rate limiter built on top of TokenBucket."""

from __future__ import annotations

from src.token_bucket import TokenBucket


class RateLimiter:
    def __init__(self, capacity: float, refill_rate_per_sec: float, clock=None):
        self.bucket = TokenBucket(capacity, refill_rate_per_sec, clock=clock)

    def allow(self) -> bool:
        return self.bucket.try_consume(1.0)
