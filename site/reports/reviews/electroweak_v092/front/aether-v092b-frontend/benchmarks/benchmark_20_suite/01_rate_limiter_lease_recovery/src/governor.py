from typing import Callable, Any
from .rate_limiter import RateLimiter

class ConcurrencyGovernor:
    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    def execute_with_lease(self, lease_id: str, tokens: int, fn: Callable[[], Any]) -> Any:
        if not self.limiter.acquire(lease_id, tokens):
            raise RuntimeError(f"Insufficient capacity for lease {lease_id}")
        try:
            return fn()
        finally:
            self.limiter.release(lease_id)
