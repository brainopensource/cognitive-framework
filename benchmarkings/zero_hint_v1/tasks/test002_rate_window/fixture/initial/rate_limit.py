"""Per-key request admission over a fixed window."""

from __future__ import annotations


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: float) -> None:
        if max_requests < 1:
            raise ValueError("max_requests must be at least 1")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: dict[str, tuple[float, int]] = {}

    def allow(self, key: str, now: float) -> bool:
        if not isinstance(key, str) or not key:
            raise ValueError("key is required")
        origin, used = self._windows.get(key, (now, 0))
        if now - origin >= self.window_seconds:
            origin, used = now, 0
        if used >= self.max_requests:
            return False
        self._windows[key] = (origin, used + 1)
        return True
