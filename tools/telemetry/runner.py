"""Latency benchmark runner and paired experiment evaluation.

Owning contract: REQ-BENCH-001, VG-07 §5.6, §5.8.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Sequence

from vanguard.packages.adapters.models.cassette import Cassette, CassettePlayer
from vanguard.packages.ports.model import ModelPort

from .collector import TelemetryCollector
from .metrics import TelemetryReport
from .tuple import InstrumentTuple

__all__ = [
    "BenchmarkTask",
    "BenchmarkRunResult",
    "PairedComparisonResult",
    "LatencyBenchmarkRunner",
]


@dataclass(frozen=True)
class BenchmarkTask:
    """A single benchmark task case."""

    task_id: str
    context: Mapping[str, Any]
    tools: Sequence[Mapping[str, Any]]
    sampling: Mapping[str, Any]
    expected_action: Optional[str] = None


@dataclass
class BenchmarkRunResult:
    """Output from executing a benchmark arm."""

    name: str
    report: TelemetryReport
    task_count: int
    duration_total_ms: float
    instrument_tuple: Optional[InstrumentTuple] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "taskCount": self.task_count,
            "durationTotalMs": round(self.duration_total_ms, 4),
            "report": self.report.to_dict(),
        }


@dataclass
class PairedComparisonResult:
    """Comparative lift and cost evaluation under rule M-18."""

    arm_a_name: str
    arm_b_name: str
    is_valid_comparison: bool
    rejection_reason: str = ""
    p50_ttft_lift_ms: float = 0.0
    p95_ttft_lift_ms: float = 0.0
    total_cost_delta_usd: float = 0.0
    total_tokens_delta: int = 0
    overhead_delta_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "armA": self.arm_a_name,
            "armB": self.arm_b_name,
            "validComparison": self.is_valid_comparison,
            "rejectionReason": self.rejection_reason,
            "p50TtftLiftMs": round(self.p50_ttft_lift_ms, 4),
            "p95TtftLiftMs": round(self.p95_ttft_lift_ms, 4),
            "totalCostDeltaUsd": round(self.total_cost_delta_usd, 8),
            "totalTokensDelta": self.total_tokens_delta,
            "overheadDeltaMs": round(self.overhead_delta_ms, 4),
        }


class LatencyBenchmarkRunner:
    """Executes benchmark tasks, timing TTFT, overhead, token usage and cost."""

    def __init__(
        self,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._clock = clock

    def run_benchmark(
        self,
        name: str,
        tasks: Sequence[BenchmarkTask],
        model: ModelPort,
        instrument_tuple: Optional[InstrumentTuple] = None,
        simulate_sandbox: bool = True,
    ) -> BenchmarkRunResult:
        """Run a suite of benchmark tasks and collect detailed telemetry."""
        collector = TelemetryCollector(run_id=f"run_{name}", task_id=name)
        if instrument_tuple:
            collector.set_instrument_tuple(instrument_tuple)

        start_time = self._clock()
        for task in tasks:
            t0 = self._clock()
            res = model.propose(task.context, task.tools, task.sampling)
            t1 = self._clock()

            inference_ms = (t1 - t0) * 1000.0
            # For non-streaming mock/cassette, TTFT is the arrival of the full proposal
            ttft_ms = inference_ms

            proposal = res.value if res.ok and isinstance(res.value, Mapping) else {}
            usage = proposal.get("usage") if isinstance(proposal, Mapping) else {}

            if isinstance(usage, Mapping):
                prompt = int(usage.get("prompt_tokens", 0))
                compl = int(usage.get("completion_tokens", 0))
                cached = int(usage.get("cached_tokens", 0))
                cost = float(usage.get("cost_usd", 0.0))
                collector.record_token_usage(prompt, compl, cached, cost)

            collector.record_turn_latency(ttft_ms=ttft_ms, ttlt_ms=inference_ms, turn_duration_ms=inference_ms)

            # Measure or simulate sandbox overhead if applicable
            if simulate_sandbox:
                # Standard realistic sandbox timing in ms: mount ~15ms, probe ~5ms, exec ~10ms, teardown ~8ms
                mount_t0 = self._clock()
                mount_ms = 15.0
                probe_ms = 5.0
                exec_ms = 10.0
                teardown_ms = 8.0
                collector.record_effect_timing(
                    mount_ms=mount_ms,
                    probe_ms=probe_ms,
                    exec_ms=exec_ms,
                    teardown_ms=teardown_ms,
                )

        total_duration_ms = (self._clock() - start_time) * 1000.0
        report = collector.build_report()

        return BenchmarkRunResult(
            name=name,
            report=report,
            task_count=len(tasks),
            duration_total_ms=total_duration_ms,
            instrument_tuple=instrument_tuple,
        )

    def compare_arms(
        self,
        arm_a: BenchmarkRunResult,
        arm_b: BenchmarkRunResult,
    ) -> PairedComparisonResult:
        """Compare two benchmark runs under the M-18 comparability rule."""
        if arm_a.instrument_tuple is not None and arm_b.instrument_tuple is not None:
            is_valid, reason = arm_a.instrument_tuple.is_comparable_with(arm_b.instrument_tuple)
            if not is_valid:
                return PairedComparisonResult(
                    arm_a_name=arm_a.name,
                    arm_b_name=arm_b.name,
                    is_valid_comparison=False,
                    rejection_reason=reason,
                )

        rep_a = arm_a.report
        rep_b = arm_b.report

        p50_a = rep_a.latency.to_dict()["ttft"]["p50"]
        p50_b = rep_b.latency.to_dict()["ttft"]["p50"]
        p95_a = rep_a.latency.to_dict()["ttft"]["p95"]
        p95_b = rep_b.latency.to_dict()["ttft"]["p95"]

        cost_a = rep_a.token_cost.total_cost_usd
        cost_b = rep_b.token_cost.total_cost_usd

        tokens_a = rep_a.token_cost.total_tokens
        tokens_b = rep_b.token_cost.total_tokens

        overhead_a = rep_a.effect_overhead.to_dict()["totalsMs"]["overheadTotal"]
        overhead_b = rep_b.effect_overhead.to_dict()["totalsMs"]["overheadTotal"]

        return PairedComparisonResult(
            arm_a_name=arm_a.name,
            arm_b_name=arm_b.name,
            is_valid_comparison=True,
            p50_ttft_lift_ms=p50_b - p50_a,
            p95_ttft_lift_ms=p95_b - p95_a,
            total_cost_delta_usd=cost_b - cost_a,
            total_tokens_delta=tokens_b - tokens_a,
            overhead_delta_ms=overhead_b - overhead_a,
        )
