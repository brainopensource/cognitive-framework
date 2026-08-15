"""Telemetry metrics calculation and data structures.

Owning contract: REQ-BENCH-001, VG-07 §5.6, §5.8.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

__all__ = [
    "calculate_percentiles",
    "LatencySummary",
    "EffectOverheadSummary",
    "TokenCostSummary",
    "TelemetryReport",
]


def calculate_percentiles(
    samples: Sequence[float],
    percentiles: Sequence[float] = (50.0, 95.0, 99.0),
) -> dict[str, float]:
    """Calculate exact percentiles using linear interpolation (nearest rank method).
    
    Returns a mapping like {"p50": ..., "p95": ..., "p99": ..., "min": ..., "max": ..., "mean": ..., "count": ...}.
    """
    if not samples:
        res = {f"p{int(p) if p.is_integer() else p}": 0.0 for p in percentiles}
        res.update({"min": 0.0, "max": 0.0, "mean": 0.0, "count": 0.0})
        return res

    sorted_samples = sorted(samples)
    n = len(sorted_samples)
    mean_val = sum(sorted_samples) / n
    res = {
        "min": float(sorted_samples[0]),
        "max": float(sorted_samples[-1]),
        "mean": round(mean_val, 4),
        "count": float(n),
    }

    for p in percentiles:
        key = f"p{int(p) if p.is_integer() else p}"
        if n == 1:
            res[key] = float(sorted_samples[0])
            continue
        # Standard percentile with linear interpolation
        rank = (p / 100.0) * (n - 1)
        low = int(math.floor(rank))
        high = int(math.ceil(rank))
        fraction = rank - low
        val = sorted_samples[low] + fraction * (sorted_samples[high] - sorted_samples[low])
        res[key] = round(float(val), 4)

    return res


@dataclass
class LatencySummary:
    """Latency distribution summary across streaming turns."""

    ttft_samples_ms: list[float] = field(default_factory=list)
    ttlt_samples_ms: list[float] = field(default_factory=list)
    turn_duration_samples_ms: list[float] = field(default_factory=list)

    def add_turn(
        self,
        ttft_ms: float,
        ttlt_ms: float = 0.0,
        turn_duration_ms: float = 0.0,
    ) -> None:
        if ttft_ms > 0:
            self.ttft_samples_ms.append(float(ttft_ms))
        if ttlt_ms > 0:
            self.ttlt_samples_ms.append(float(ttlt_ms))
        if turn_duration_ms > 0:
            self.turn_duration_samples_ms.append(float(turn_duration_ms))

    def to_dict(self) -> dict[str, Any]:
        return {
            "ttft": calculate_percentiles(self.ttft_samples_ms),
            "ttlt": calculate_percentiles(self.ttlt_samples_ms),
            "turnDuration": calculate_percentiles(self.turn_duration_samples_ms),
            "sampleCount": len(self.ttft_samples_ms),
        }


@dataclass
class EffectOverheadSummary:
    """Breakdown of sandbox and effect execution overhead."""

    mount_samples_ms: list[float] = field(default_factory=list)
    probe_samples_ms: list[float] = field(default_factory=list)
    exec_samples_ms: list[float] = field(default_factory=list)
    teardown_samples_ms: list[float] = field(default_factory=list)
    effect_count: int = 0

    def add_effect(
        self,
        mount_ms: float = 0.0,
        probe_ms: float = 0.0,
        exec_ms: float = 0.0,
        teardown_ms: float = 0.0,
    ) -> None:
        self.effect_count += 1
        self.mount_samples_ms.append(float(mount_ms))
        self.probe_samples_ms.append(float(probe_ms))
        self.exec_samples_ms.append(float(exec_ms))
        self.teardown_samples_ms.append(float(teardown_ms))

    def to_dict(self) -> dict[str, Any]:
        total_mount = sum(self.mount_samples_ms)
        total_probe = sum(self.probe_samples_ms)
        total_exec = sum(self.exec_samples_ms)
        total_teardown = sum(self.teardown_samples_ms)
        total_overhead = total_mount + total_probe + total_teardown
        return {
            "effectCount": self.effect_count,
            "mount": calculate_percentiles(self.mount_samples_ms),
            "probe": calculate_percentiles(self.probe_samples_ms),
            "execution": calculate_percentiles(self.exec_samples_ms),
            "teardown": calculate_percentiles(self.teardown_samples_ms),
            "totalsMs": {
                "mount": round(total_mount, 4),
                "probe": round(total_probe, 4),
                "execution": round(total_exec, 4),
                "teardown": round(total_teardown, 4),
                "overheadTotal": round(total_overhead, 4),
            },
        }


@dataclass
class TokenCostSummary:
    """Cumulative token counts and priced USD cost accounting."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    by_model: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        cached_tokens: int = 0,
        cost_usd: float = 0.0,
        model: str = "default",
    ) -> None:
        self.prompt_tokens += int(prompt_tokens)
        self.completion_tokens += int(completion_tokens)
        self.cached_tokens += int(cached_tokens)
        self.total_tokens += int(prompt_tokens + completion_tokens)
        self.total_cost_usd = round(self.total_cost_usd + float(cost_usd), 8)

        if model not in self.by_model:
            self.by_model[model] = {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cached_tokens": 0,
                "total_tokens": 0,
                "cost_usd": 0.0,
            }
        m = self.by_model[model]
        m["prompt_tokens"] += int(prompt_tokens)
        m["completion_tokens"] += int(completion_tokens)
        m["cached_tokens"] += int(cached_tokens)
        m["total_tokens"] += int(prompt_tokens + completion_tokens)
        m["cost_usd"] = round(m["cost_usd"] + float(cost_usd), 8)

    def to_dict(self) -> dict[str, Any]:
        return {
            "promptTokens": self.prompt_tokens,
            "completionTokens": self.completion_tokens,
            "cachedTokens": self.cached_tokens,
            "totalTokens": self.total_tokens,
            "totalCostUsd": self.total_cost_usd,
            "byModel": {k: dict(v) for k, v in sorted(self.by_model.items())},
        }


@dataclass
class TelemetryReport:
    """Complete summary report for a task or benchmark execution."""

    run_id: str
    task_id: str = ""
    status: str = "completed"
    turn_count: int = 0
    latency: LatencySummary = field(default_factory=LatencySummary)
    effect_overhead: EffectOverheadSummary = field(default_factory=EffectOverheadSummary)
    token_cost: TokenCostSummary = field(default_factory=TokenCostSummary)
    started_at: str = ""
    completed_at: str = ""
    instrument_tuple: Mapping[str, Any] = field(default_factory=dict)
    custom_metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        res: dict[str, Any] = {
            "runId": self.run_id,
            "taskId": self.task_id,
            "status": self.status,
            "turnCount": self.turn_count,
            "startedAt": self.started_at,
            "completedAt": self.completed_at,
            "latency": self.latency.to_dict(),
            "effectOverhead": self.effect_overhead.to_dict(),
            "tokenCost": self.token_cost.to_dict(),
        }
        if self.instrument_tuple:
            res["instrumentTuple"] = dict(self.instrument_tuple)
        if self.custom_metrics:
            res["customMetrics"] = dict(self.custom_metrics)
        return res
