"""Preregistered statistics for paired benchmark campaigns.

Missing evaluator verdicts are excluded from every denominator. These helpers
are deterministic and intentionally have no provider or evaluator dependency.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

__all__ = ["wilson_interval", "mcnemar_exact", "PairedResult", "cost_adjusted_success"]


def wilson_interval(passes: int, evaluated: int, *, z: float = 1.96) -> tuple[float, float]:
    """Return the Wilson score interval, rejecting absorbed missingness."""
    if evaluated <= 0 or passes < 0 or passes > evaluated or z <= 0:
        raise ValueError("passes/evaluated must define a non-empty binary sample")
    p = passes / evaluated
    denominator = 1.0 + z * z / evaluated
    centre = (p + z * z / (2 * evaluated)) / denominator
    radius = z * math.sqrt(p * (1 - p) / evaluated + z * z / (4 * evaluated * evaluated)) / denominator
    return (max(0.0, centre - radius), min(1.0, centre + radius))


def mcnemar_exact(control: Sequence[bool | None], treatment: Sequence[bool | None]) -> dict[str, float | int | bool]:
    """Compute paired lift and two-sided exact McNemar p-value.

    A pair containing ``None`` is missing and excluded, never scored as zero.
    """
    if len(control) != len(treatment):
        raise ValueError("paired arms must have equal task membership")
    a = b = c = d = missing = 0
    for left, right in zip(control, treatment):
        if left is None or right is None:
            missing += 1
        elif left and right:
            a += 1
        elif left and not right:
            b += 1
        elif not left and right:
            c += 1
        else:
            d += 1
    discordant = b + c
    if discordant == 0:
        p_value = 1.0
    else:
        tail = sum(math.comb(discordant, k) for k in range(max(b, c), discordant + 1)) / (2 ** discordant)
        p_value = min(1.0, 2.0 * tail)
    evaluated = a + b + c + d
    return {"a": a, "b": b, "c": c, "d": d, "n_evaluated": evaluated,
            "n_missing": missing, "lift": (c - b) / evaluated if evaluated else 0.0,
            "p_value": p_value, "significant": bool(p_value < 0.05)}


@dataclass(frozen=True, slots=True)
class PairedResult:
    passes: int
    evaluated: int
    missing: int = 0

    def __post_init__(self) -> None:
        if self.evaluated <= 0 or self.passes < 0 or self.passes > self.evaluated or self.missing < 0:
            raise ValueError("invalid evaluated/missing result")

    @property
    def rate(self) -> float:
        return self.passes / self.evaluated

    @property
    def wilson(self) -> tuple[float, float]:
        return wilson_interval(self.passes, self.evaluated)


def cost_adjusted_success(result: PairedResult, total_usd: float, lambda_usd: float) -> float:
    """Compute preregistered utility; cost is averaged over evaluated tasks."""
    if total_usd < 0 or lambda_usd < 0:
        raise ValueError("cost and lambda must be non-negative")
    return result.rate - lambda_usd * (total_usd / result.evaluated)
