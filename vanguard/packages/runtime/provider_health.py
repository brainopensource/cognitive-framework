"""Provider health tracking, error attribution, and rotation policies (REQ-TRUST-001, S31).

Tracks provider availability, malformed response counts, timeouts, and cooldowns
to make deterministic rotation and fallback choices without inventing live provider calls.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Mapping, Sequence

__all__ = [
    "ProviderHealthStats",
    "ProviderHealthTracker",
]


@dataclass
class ProviderHealthStats:
    """Telemetry and health state for one provider or model ID."""

    provider_id: str
    successful_calls: int = 0
    tool_call_successes: int = 0
    malformed_calls: int = 0
    timeouts: int = 0
    consecutive_failures: int = 0
    cooldown_until: float = 0.0

    @property
    def is_in_cooldown(self) -> bool:
        return time.monotonic() < self.cooldown_until

    def to_dict(self) -> dict[str, Any]:
        return {
            "providerId": self.provider_id,
            "successfulCalls": self.successful_calls,
            "toolCallSuccesses": self.tool_call_successes,
            "malformedCalls": self.malformed_calls,
            "timeouts": self.timeouts,
            "consecutiveFailures": self.consecutive_failures,
            "inCooldown": self.is_in_cooldown,
        }


class ProviderHealthTracker:
    """Manages provider health records and deterministic rotation policies."""

    def __init__(self) -> None:
        self._stats: dict[str, ProviderHealthStats] = {}

    def get_stats(self, provider_id: str) -> ProviderHealthStats:
        if provider_id not in self._stats:
            self._stats[provider_id] = ProviderHealthStats(provider_id=provider_id)
        return self._stats[provider_id]

    def record_success(self, provider_id: str, is_tool_call: bool = False) -> None:
        stats = self.get_stats(provider_id)
        stats.successful_calls += 1
        if is_tool_call:
            stats.tool_call_successes += 1
        stats.consecutive_failures = 0

    def record_malformed(self, provider_id: str, cooldown_seconds: float = 60.0) -> None:
        stats = self.get_stats(provider_id)
        stats.malformed_calls += 1
        stats.consecutive_failures += 1
        stats.cooldown_until = time.monotonic() + cooldown_seconds

    def record_timeout(self, provider_id: str, cooldown_seconds: float = 120.0) -> None:
        stats = self.get_stats(provider_id)
        stats.timeouts += 1
        stats.consecutive_failures += 1
        stats.cooldown_until = time.monotonic() + cooldown_seconds

    def record_failure(self, provider_id: str) -> None:
        stats = self.get_stats(provider_id)
        stats.consecutive_failures += 1

    def is_healthy(self, provider_id: str) -> bool:
        stats = self.get_stats(provider_id)
        return not stats.is_in_cooldown and stats.consecutive_failures < 3

    def rotate_provider(
        self,
        candidates: Sequence[str],
        current: str | None = None,
    ) -> str | None:
        """Select next healthiest candidate from the list, avoiding current and cooldowns."""
        if not candidates:
            return None

        # Filter out current and in-cooldown providers
        healthy = [
            c for c in candidates
            if c != current and not self.get_stats(c).is_in_cooldown
        ]
        if healthy:
            # Sort by least consecutive failures, then highest tool call successes
            healthy.sort(
                key=lambda c: (
                    self.get_stats(c).consecutive_failures,
                    -self.get_stats(c).tool_call_successes,
                )
            )
            return healthy[0]

        # If all in cooldown, pick the candidate whose cooldown expires earliest
        if candidates:
            sorted_by_cooldown = sorted(
                [c for c in candidates if c != current] or list(candidates),
                key=lambda c: self.get_stats(c).cooldown_until,
            )
            return sorted_by_cooldown[0]

        return None
