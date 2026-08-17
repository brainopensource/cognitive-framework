"""Periodic re-grounding policy (S10-B-04).

Owning contract: VG-03 §6.1, §10.4, REQ-BENCH-001.

Periodically requests authorized observation effects through Kernel.dispatch
to refresh environment truth and prevent FT-11 goal drift and silent error compounding.
Not a privileged side channel: requires explicit capability grant.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from vanguard.packages.ports.environment import EffectRequest


@dataclass(frozen=True, slots=True)
class RegroundPolicy:
    """Configures cadence and target verb for periodic re-grounding observations."""

    interval_turns: int = 5
    observation_verb: str = "fs.read"
    target_selector: Mapping[str, Any] | None = None

    def should_reground(self, turn_number: int) -> bool:
        """Returns True if the current turn matches the re-grounding cadence."""
        if self.interval_turns <= 0:
            return False
        return (turn_number > 0) and (turn_number % self.interval_turns == 0)

    def create_effect_request(self, episode_id: str, turn_index: int) -> EffectRequest:
        """Construct standard EffectRequest to be dispatched through Kernel."""
        return EffectRequest(
            verb=self.observation_verb,
            action="read",
            args={
                "path": "STATUS.md",
                "purpose": "periodic_regrounding",
                "turn": turn_index,
                "episode_id": episode_id,
            },
        )
