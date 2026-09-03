"""Token bucket: refills over time, capped at capacity."""

from __future__ import annotations


class TokenBucket:
    def __init__(self, capacity: float, refill_rate_per_sec: float, clock=None):
        self.capacity = capacity
        self.refill_rate_per_sec = refill_rate_per_sec
        self.tokens = capacity
        self._clock = clock or (lambda: 0.0)
        self._last = self._clock()

    def _refill(self) -> None:
        now = self._clock()
        elapsed = now - self._last
        # BUG: refill amount is not capped at capacity, so tokens can grow
        # without bound if _refill is called after a long idle period.
        self.tokens = self.tokens + elapsed * self.refill_rate_per_sec
        self._last = now

    def try_consume(self, amount: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= amount:
            self.tokens -= amount
            return True
        return False
