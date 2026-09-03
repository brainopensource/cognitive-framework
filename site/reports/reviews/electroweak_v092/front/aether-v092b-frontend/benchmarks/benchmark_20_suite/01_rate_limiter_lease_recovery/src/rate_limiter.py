import time
from typing import Dict, Any, Optional

class RateLimiter:
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.available = capacity
        self.active_leases: Dict[str, Dict[str, Any]] = {}

    def acquire(self, lease_id: str, tokens: int, ttl_seconds: float = 30.0) -> bool:
        if tokens > self.available:
            return False
        self.available -= tokens
        self.active_leases[lease_id] = {
            "tokens": tokens,
            "expires_at": time.time() + ttl_seconds
        }
        return True

    def release(self, lease_id: str) -> bool:
        if lease_id in self.active_leases:
            data = self.active_leases.pop(lease_id)
            self.available += data["tokens"]
            return True
        return False

    def clean_expired(self, current_time: float) -> int:
        # BUG: Expired leases are popped from active_leases,
        # but self.available is NOT refunded with the expired tokens!
        expired = [lid for lid, data in self.active_leases.items() if data["expires_at"] <= current_time]
        for lid in expired:
            self.active_leases.pop(lid, None)
        return len(expired)
