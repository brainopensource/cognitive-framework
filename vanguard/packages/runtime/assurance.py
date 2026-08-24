"""Assurance policy selection for W3D-10.

Execution profiles determine whether a run is merely recorded or eligible for
the hermetic foundation evidence collector. The policy is exterior to the
kernel and never turns missing evidence into success.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class AssurancePolicy:
    level: str
    evaluation_mode: str
    promotion_eligible: bool

    @classmethod
    def from_profile(cls, profile: Any | None) -> "AssurancePolicy":
        if profile is None:
            # Legacy release callers retain the existing explicit release gate.
            return cls("legacy", "exterior", False)
        requested = profile.requested
        return cls(
            requested.assurance_level,
            requested.evaluation_mode,
            bool(requested.promotion_eligible),
        )

    @property
    def records_runtime_facts(self) -> bool:
        return True

    @property
    def collects_foundation_evidence(self) -> bool:
        return self.level in {"hermetic", "legacy"}

    @property
    def promotional(self) -> bool:
        return self.level == "hermetic" and self.evaluation_mode == "exterior" and self.promotion_eligible
