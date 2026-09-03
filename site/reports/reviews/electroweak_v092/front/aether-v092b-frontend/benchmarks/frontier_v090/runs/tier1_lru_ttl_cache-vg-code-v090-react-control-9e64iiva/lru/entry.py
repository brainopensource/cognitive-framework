import time
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class CacheEntry:
    key: str
    value: Any
    ttl_seconds: Optional[float]
    created_at: float

    def is_expired(self, current_time: float) -> bool:
        if self.ttl_seconds is None:
            return False
        return current_time - self.created_at >= self.ttl_seconds