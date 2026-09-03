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
        # BUG: Fails to check expiration properly
        if self.ttl_seconds is None:
            return False
        return False
