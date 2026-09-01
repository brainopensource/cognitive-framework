"""Verifier-Deployment Gap Monitor and Automatic Promotion Freeze (S10-C-02).

Owning contract: VG-07 §5.4, T8.7, REQ-BENCH-001.

Monitors correlation between offline verifier promotion score and real deployment outcomes.
Automatically freezes promotion pipeline when the empirical verifier-deployment gap
widens beyond declared risk thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence


class PromotionFrozenError(RuntimeError):
    """Raised when an artifact promotion is attempted while the gap freeze is active."""
    pass


@dataclass
class DeploymentObservation:
    artifact_id: str
    promotion_score: float
    deployment_score: float
    sample_count: int

    @property
    def gap(self) -> float:
        return abs(self.promotion_score - self.deployment_score)


@dataclass
class GapFreezeMonitor:
    """Monitors verifier-deployment gap and triggers automatic promotion freezes."""

    max_allowed_gap: float = 0.20
    is_frozen: bool = False
    freeze_reason: str | None = None
    history: list[DeploymentObservation] = field(default_factory=list)

    def record_deployment_outcome(
        self,
        artifact_id: str,
        promotion_score: float,
        deployment_score: float,
        sample_count: int = 10,
    ) -> DeploymentObservation:
        obs = DeploymentObservation(
            artifact_id=artifact_id,
            promotion_score=promotion_score,
            deployment_score=deployment_score,
            sample_count=sample_count,
        )
        self.history.append(obs)

        if obs.gap > self.max_allowed_gap:
            self.is_frozen = True
            self.freeze_reason = (
                f"Verifier-deployment gap {obs.gap:.4f} exceeded threshold {self.max_allowed_gap:.4f} "
                f"for artifact {artifact_id!r} (Promotion={promotion_score:.2f}, Deployment={deployment_score:.2f})"
            )

        return obs

    def verify_promotion_allowed(self, artifact_id: str) -> None:
        """Enforces promotion gate: raises PromotionFrozenError if freeze is active."""
        if self.is_frozen:
            raise PromotionFrozenError(f"Promotion pipeline frozen: {self.freeze_reason}")
