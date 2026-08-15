"""Runtime telemetry collector for non-invasive performance tracking.

Owning contract: REQ-BENCH-001, VG-07 §5.6, §5.8.
Invariant: Telemetry code is non-invasive and does not alter kernel dispatch timings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, TextIO

from .metrics import (
    EffectOverheadSummary,
    LatencySummary,
    TelemetryReport,
    TokenCostSummary,
)
from .tuple import InstrumentTuple

__all__ = ["TelemetryCollector"]


class TelemetryCollector:
    """Non-invasive telemetry collector accumulating latency, overhead, tokens and costs."""

    def __init__(self, run_id: str = "run_default", task_id: str = "") -> None:
        self.run_id = run_id
        self.task_id = task_id
        self.turn_count = 0
        self.latency = LatencySummary()
        self.effect_overhead = EffectOverheadSummary()
        self.token_cost = TokenCostSummary()
        self.started_at: str = ""
        self.completed_at: str = ""
        self.status: str = "pending"
        self._instrument_tuple: Optional[InstrumentTuple] = None
        self._custom_metrics: dict[str, Any] = {}

    def set_instrument_tuple(self, inst_tuple: InstrumentTuple) -> None:
        self._instrument_tuple = inst_tuple

    def record_turn_latency(
        self,
        ttft_ms: float,
        ttlt_ms: float = 0.0,
        turn_duration_ms: float = 0.0,
    ) -> None:
        """Record turn latency to first token (TTFT) and total turn duration in ms."""
        self.turn_count += 1
        self.latency.add_turn(ttft_ms, ttlt_ms, turn_duration_ms)

    def record_effect_timing(
        self,
        mount_ms: float = 0.0,
        probe_ms: float = 0.0,
        exec_ms: float = 0.0,
        teardown_ms: float = 0.0,
        effect_kind: str = "",
    ) -> None:
        """Record sandbox mount, double-probe, execution and teardown overhead in ms."""
        self.effect_overhead.add_effect(mount_ms, probe_ms, exec_ms, teardown_ms)

    def record_token_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        cached_tokens: int = 0,
        cost_usd: float = 0.0,
        model: str = "default",
    ) -> None:
        """Record token usage and USD cost for a model interaction."""
        self.token_cost.add_usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cached_tokens=cached_tokens,
            cost_usd=cost_usd,
            model=model,
        )

    def record_custom_metric(self, key: str, value: Any) -> None:
        self._custom_metrics[key] = value

    def ingest_event(self, event: Any) -> None:
        """Non-invasively ingest an event envelope or mapping without altering runtime state."""
        payload = getattr(event, "payload", None)
        if payload is None and isinstance(event, Mapping):
            payload = event.get("payload", event)
        if not isinstance(payload, Mapping):
            return

        occurred_at = getattr(event, "occurred_at", "") or str(payload.get("occurredAt", ""))
        kind = payload.get("kind", "")

        if kind == "EpisodeStarted":
            self.status = "active"
            if not self.started_at:
                self.started_at = occurred_at
        elif kind == "EpisodeCompleted":
            self.status = "completed"
            self.completed_at = occurred_at
        elif kind == "ProposalProduced":
            self.turn_count += 1
            # Extract proposal usage if present
            proposal = payload.get("proposal") or payload
            usage = proposal.get("usage") or {}
            if isinstance(usage, Mapping):
                self.token_cost.add_usage(
                    prompt_tokens=usage.get("prompt_tokens") or usage.get("promptTokens") or 0,
                    completion_tokens=usage.get("completion_tokens") or usage.get("completionTokens") or 0,
                    cached_tokens=usage.get("cached_tokens") or usage.get("cachedTokens") or 0,
                    cost_usd=usage.get("cost_usd") or usage.get("costUsd") or proposal.get("cost_usd") or 0.0,
                    model=payload.get("model", "default"),
                )
            # Latency if recorded in event
            timing = payload.get("timing") or {}
            if isinstance(timing, Mapping):
                ttft = timing.get("ttftMs") or timing.get("ttft_ms") or 0.0
                ttlt = timing.get("ttltMs") or timing.get("ttlt_ms") or 0.0
                dur = timing.get("durationMs") or timing.get("duration_ms") or 0.0
                if ttft > 0 or dur > 0:
                    self.latency.add_turn(ttft, ttlt, dur)

        elif kind in ("EffectStarted", "EffectCompleted", "EffectReconciled"):
            timing = payload.get("timing") or {}
            if isinstance(timing, Mapping):
                mount = timing.get("mountMs") or timing.get("mount_ms") or 0.0
                probe = timing.get("probeMs") or timing.get("probe_ms") or 0.0
                exec_time = timing.get("execMs") or timing.get("exec_ms") or 0.0
                teardown = timing.get("teardownMs") or timing.get("teardown_ms") or 0.0
                if any(v > 0 for v in (mount, probe, exec_time, teardown)):
                    self.effect_overhead.add_effect(mount, probe, exec_time, teardown)

    def build_report(self) -> TelemetryReport:
        """Build the aggregate TelemetryReport."""
        return TelemetryReport(
            run_id=self.run_id,
            task_id=self.task_id,
            status=self.status,
            turn_count=self.turn_count,
            latency=self.latency,
            effect_overhead=self.effect_overhead,
            token_cost=self.token_cost,
            started_at=self.started_at,
            completed_at=self.completed_at,
            instrument_tuple=self._instrument_tuple.to_dict() if self._instrument_tuple else {},
            custom_metrics=self._custom_metrics,
        )

    def to_jsonl(self) -> str:
        """Format report as a single-line JSON string (JSON Lines)."""
        report_dict = self.build_report().to_dict()
        return json.dumps(report_dict, separators=(",", ":"), ensure_ascii=False)

    def export_jsonl(self, target: str | Path | TextIO) -> str:
        """Export JSON Lines report to a file path or stream."""
        line = self.to_jsonl() + "\n"
        if isinstance(target, (str, Path)):
            path = Path(target)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as f:
                f.write(line)
        else:
            target.write(line)
        return line
