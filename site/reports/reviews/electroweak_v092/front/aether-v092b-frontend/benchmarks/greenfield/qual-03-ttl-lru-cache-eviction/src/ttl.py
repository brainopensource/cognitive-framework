"""Time-to-live expiry tracking."""

from __future__ import annotations


class TTLClock:
    def __init__(self, ttl_seconds: float, clock=None):
        self.ttl_seconds = ttl_seconds
        self._clock = clock or (lambda: 0.0)
        self._expires_at: dict[str, float] = {}

    def set(self, key: str) -> None:
        self._expires_at[key] = self._clock() + self.ttl_seconds

    def is_expired(self, key: str) -> bool:
        expires_at = self._expires_at.get(key)
        if expires_at is None:
            return True
        # BUG: strict '>' means a key checked at the exact instant it expires
        # is treated as still valid for one more read.
        return self._clock() > expires_at

    def discard(self, key: str) -> None:
        self._expires_at.pop(key, None)
