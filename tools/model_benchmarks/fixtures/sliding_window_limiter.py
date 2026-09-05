"""
Sliding Window Rate Limiter module.
Used as a benchmark fixture for SWE agent self-healing tests.
"""

from typing import List

class SlidingWindowLimiter:
    """
    Limits requests to max_requests within a rolling window_seconds.
    """
    def __init__(self, max_requests: int, window_seconds: float):
        if max_requests <= 0:
            raise ValueError("max_requests must be > 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be > 0")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.timestamps: List[float] = []

    def allow(self, now: float) -> bool:
        """
        Determines whether an action at timestamp `now` is permitted under rate limits.
        Any timestamp t where t <= (now - window_seconds) must be pruned.
        
        [SEEDED BUG]: Uses strict '<' instead of '<=', causing boundary events 
        at exactly (now - window_seconds) to linger and falsely throttle.
        Additionally, appends `now` before checking capacity!
        """
        cutoff = now - self.window_seconds
        # Bug: < instead of <= leaves boundary timestamps in the list
        self.timestamps = [t for t in self.timestamps if t > cutoff]
        
        # Bug: appends before checking length
        self.timestamps.append(now)
        if len(self.timestamps) > self.max_requests:
            return False
        return True

    def reset(self) -> None:
        self.timestamps.clear()
