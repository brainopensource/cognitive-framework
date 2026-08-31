# rate_governor.py - Concurrency & Lease Token Governor
import time
from typing import Dict, Optional, Tuple

class RateGovernor:
    """Manages rate limits, token reservations, and lease lifecycles."""
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.available_tokens = capacity
        self.active_leases: Dict[str, Dict[str, Any]] = {}

    def reserve(self, lease_id: str, tokens: int, ttl_seconds: float = 10.0) -> bool:
        if tokens > self.available_tokens:
            return False
        self.available_tokens -= tokens
        self.active_leases[lease_id] = {
            "tokens": tokens,
            "expires_at": time.time() + ttl_seconds
        }
        return True

    def commit(self, lease_id: str) -> bool:
        if lease_id in self.active_leases:
            del self.active_leases[lease_id]
            return True
        return False

    def clean_expired(self, current_time: Optional[float] = None) -> int:
        """Removes expired leases and restores their tokens to the available pool."""
        now = current_time if current_time is not None else time.time()
        # BUG: Finds expired leases, deletes them from the dictionary,
        # but fails to increment self.available_tokens by the lease's token count!
        expired_ids = [lid for lid, data in self.active_leases.items() if data["expires_at"] <= now]
        for lid in expired_ids:
            data = self.active_leases.pop(lid, None)
            if data:
                self.available_tokens += data["tokens"]
        return len(expired_ids)
