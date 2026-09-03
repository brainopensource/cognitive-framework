"""M-7 Pareto measurement package & profile telemetry structures (ADR-0083).

Provides attribution models, WAL contention measurements, and cost-per-signed-pass
telemetry without enabling concurrent runtime execution before M-7 activation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from ..domain.canonicalisation.digest import digest_of


class ParetoProfile(str, Enum):
    """Reference execution profiles from ADR-0083."""
    ALPHA = "alpha"  # Minimize latency/cost under required witness floor
    BETA = "beta"    # Minimize expected cost per signed pass
    GAMMA = "gamma"  # Maximize assurance within authorized ceiling
    DELTA = "delta"  # Cheapest feasible policy with evidence-driven re-planning


@dataclass(frozen=True, slots=True)
class WalContentionMetrics:
    """Measures WAL lock contention, lease acquisition latency, and commit overhead."""
    claims_count: int = 0
    contention_events: int = 0
    total_wait_millis: int = 0
    max_wait_millis: int = 0
    lease_conflicts: int = 0


@dataclass(frozen=True, slots=True)
class ParetoMeasurementReport:
    """ Attributable measurement record for an episode strategy execution."""
    profile: ParetoProfile
    model_calls: int = 0
    coordination_envelopes: int = 0
    retries: int = 0
    bytes_transferred: int = 0
    critical_path_millis: int = 0
    usd_micros: int = 0
    tokens: int = 0
    signed_passes: int = 0
    wal_contention: WalContentionMetrics = field(default_factory=WalContentionMetrics)
    independence_waves: int = 1
    max_wave_width: int = 1

    @property
    def cost_per_signed_pass_micros(self) -> int | None:
        """Cost in micros per verified exterior signed pass, or None if zero passes."""
        if self.signed_passes <= 0:
            return None
        return self.usd_micros // self.signed_passes

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile": self.profile.value,
            "model_calls": self.model_calls,
            "coordination_envelopes": self.coordination_envelopes,
            "retries": self.retries,
            "bytes_transferred": self.bytes_transferred,
            "critical_path_millis": self.critical_path_millis,
            "usd_micros": self.usd_micros,
            "tokens": self.tokens,
            "signed_passes": self.signed_passes,
            "cost_per_signed_pass_micros": self.cost_per_signed_pass_micros,
            "wal_contention": {
                "claims_count": self.wal_contention.claims_count,
                "contention_events": self.wal_contention.contention_events,
                "total_wait_millis": self.wal_contention.total_wait_millis,
                "max_wait_millis": self.wal_contention.max_wait_millis,
                "lease_conflicts": self.wal_contention.lease_conflicts,
            },
            "independence_waves": self.independence_waves,
            "max_wave_width": self.max_wave_width,
        }

    def measurement_digest(self) -> str:
        return digest_of(self.to_dict())
