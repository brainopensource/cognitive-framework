"""Statistical inference, paired testing, bootstrap, and survival analysis (S9-C-04).

Owning contract: VG-07 §5.3, REQ-BENCH-001.

Implements rigorous experimental statistics:
- McNemar exact test for paired binary evaluation.
- Paired bootstrap for continuous cost and latency metrics.
- Right-censored survival estimation (Kaplan-Meier) for timeouts.
- Fail-closed refusal of p-values when n < 20 (M-28).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


class SampleSizeInsufficientError(ValueError):
    """Raised when inferential testing is attempted on n < 20."""
    pass


@dataclass
class McNemarResult:
    """Exact paired binary test outcome."""

    b: int
    c: int
    n_paired: int
    odds_ratio: float | None
    risk_difference: float
    p_value: float | None
    refused_p_value: bool
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "b": self.b,
            "c": self.c,
            "nPaired": self.n_paired,
            "oddsRatio": round(self.odds_ratio, 4) if self.odds_ratio is not None else None,
            "riskDifference": round(self.risk_difference, 4),
            "pValue": round(self.p_value, 6) if self.p_value is not None else None,
            "refusedPValue": self.refused_p_value,
            "reason": self.reason,
        }


def mcnemar_exact(
    b: int,
    c: int,
    n_total: int,
    min_n_for_p_value: int = 20,
) -> McNemarResult:
    """Calculate exact two-sided McNemar test with M-28 n<20 p-value refusal."""
    discordant = b + c
    risk_diff = (b - c) / n_total if n_total > 0 else 0.0
    odds_ratio = (b / c) if c > 0 else (float("inf") if b > 0 else 1.0)

    if n_total < min_n_for_p_value:
        return McNemarResult(
            b=b,
            c=c,
            n_paired=n_total,
            odds_ratio=odds_ratio if math.isfinite(odds_ratio) else None,
            risk_difference=risk_diff,
            p_value=None,
            refused_p_value=True,
            reason=f"sample size n={n_total} < {min_n_for_p_value} insufficient for inferential p-value (M-28)",
        )

    if discordant == 0:
        return McNemarResult(
            b=0,
            c=0,
            n_paired=n_total,
            odds_ratio=1.0,
            risk_difference=0.0,
            p_value=1.0,
            refused_p_value=False,
            reason="zero discordant pairs",
        )

    k = min(b, c)
    tail = sum(math.comb(discordant, i) for i in range(k + 1))
    p_val = min(1.0, 2.0 * tail / (2 ** discordant))

    return McNemarResult(
        b=b,
        c=c,
        n_paired=n_total,
        odds_ratio=odds_ratio if math.isfinite(odds_ratio) else None,
        risk_difference=risk_diff,
        p_value=p_val,
        refused_p_value=False,
    )


@dataclass
class BootstrapResult:
    """Paired bootstrap confidence interval for continuous variables."""

    mean_diff: float
    ci_lower: float
    ci_upper: float
    confidence_level: float
    n_iterations: int


def paired_bootstrap_ci(
    samples_a: Sequence[float],
    samples_b: Sequence[float],
    n_iterations: int = 1000,
    confidence_level: float = 0.95,
    seed: int = 42,
) -> BootstrapResult:
    """Compute paired percentile bootstrap confidence interval for B - A."""
    if len(samples_a) != len(samples_b):
        raise ValueError("samples_a and samples_b must have equal length")
    n = len(samples_a)
    if n == 0:
        return BootstrapResult(0.0, 0.0, 0.0, confidence_level, n_iterations)

    diffs = [b - a for a, b in zip(samples_a, samples_b)]
    observed_mean = sum(diffs) / n

    rng = random.Random(seed)
    boot_means: list[float] = []
    for _ in range(n_iterations):
        resample = [diffs[rng.randint(0, n - 1)] for _ in range(n)]
        boot_means.append(sum(resample) / n)

    boot_means.sort()
    alpha = 1.0 - confidence_level
    low_idx = int((alpha / 2.0) * n_iterations)
    high_idx = int((1.0 - alpha / 2.0) * n_iterations)

    return BootstrapResult(
        mean_diff=round(observed_mean, 4),
        ci_lower=round(boot_means[min(low_idx, n_iterations - 1)], 4),
        ci_upper=round(boot_means[min(high_idx, n_iterations - 1)], 4),
        confidence_level=confidence_level,
        n_iterations=n_iterations,
    )


@dataclass
class SurvivalCurvePoint:
    time_ms: int
    survival_prob: float
    at_risk: int
    events: int
    censored: int


def kaplan_meier_survival(
    times_ms: Sequence[int],
    event_observed: Sequence[bool],
) -> list[SurvivalCurvePoint]:
    """Compute non-parametric Kaplan-Meier survival curve with right-censoring for timeouts.
    
    event_observed=True means task completed successfully at time_ms.
    event_observed=False means task timed out / was censored at time_ms.
    """
    if len(times_ms) != len(event_observed):
        raise ValueError("times_ms and event_observed must have equal length")
    if not times_ms:
        return []

    # Sort events by time
    combined = sorted(zip(times_ms, event_observed), key=lambda x: x[0])
    
    unique_times = sorted(set(t for t, _ in combined))
    curve: list[SurvivalCurvePoint] = []
    
    n_total = len(combined)
    s_t = 1.0
    
    current_idx = 0
    at_risk = n_total
    
    for t in unique_times:
        events_at_t = 0
        censored_at_t = 0
        
        while current_idx < n_total and combined[current_idx][0] == t:
            if combined[current_idx][1]:
                events_at_t += 1
            else:
                censored_at_t += 1
            current_idx += 1
            
        if at_risk > 0:
            s_t = s_t * (1.0 - (events_at_t / at_risk))
            
        curve.append(SurvivalCurvePoint(
            time_ms=t,
            survival_prob=round(s_t, 4),
            at_risk=at_risk,
            events=events_at_t,
            censored=censored_at_t,
        ))
        
        at_risk -= (events_at_t + censored_at_t)
        
    return curve
