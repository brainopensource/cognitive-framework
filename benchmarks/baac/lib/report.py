"""BaaC Scientific Attribution, Telemetry, and KPI Reporting Engine.

Attribution Taxonomy:
1. `PASS`: Ground-truth oracle assertions passed 100% green.
2. `LLM_COGNITIVE_ERROR`: Agent submitted code, but external oracle failed assertions (model hallucination or logic flaw).
3. `HARNESS_ERROR`: Failure due to infrastructure, unhandled exception, malformed tool calls, or max-turns loop abandonment.
4. `BUDGET_EXHAUSTED`: Execution aborted due to exceeding token, turn, or cost caps.
5. `DATASET_INVALID`: Challenge source drifted from manifest or oracle verification script failed to execute.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from benchmarks.protocols import classify_disposition

from .oracle import OracleResult


@dataclass(frozen=True, slots=True)
class ChallengeExecutionResult:
    """Telemetry and outcome of a single BaaC challenge execution."""

    challenge_id: str
    tier: str
    scope: str
    context_bracket: str
    preset: str
    model: str
    mode: str  # "lam" | "live" | "ollama"
    status: str  # "PASS" | "FAIL"
    attribution: str  # "PASS" | "LLM_COGNITIVE_ERROR" | "HARNESS_ERROR" | "BUDGET_EXHAUSTED" | "DATASET_INVALID"
    turns: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    duration_seconds: float
    changed_files: tuple[str, ...] = ()
    diff_patch: str = ""
    oracle_result: Optional[OracleResult] = None
    ai_judge_score: Optional[float] = None
    diagnosis: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    trajectory: tuple[Mapping[str, Any], ...] = ()

    @property
    def disposition(self) -> str:
        return classify_disposition(
            status=self.status,
            attribution=self.attribution,
            diagnosis=self.diagnosis,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "challengeId": self.challenge_id,
            "tier": self.tier,
            "scope": self.scope,
            "contextBracket": self.context_bracket,
            "preset": self.preset,
            "model": self.model,
            "mode": self.mode,
            "status": self.status,
            "disposition": self.disposition,
            "attribution": self.attribution,
            "turns": self.turns,
            "promptTokens": self.prompt_tokens,
            "completionTokens": self.completion_tokens,
            "totalTokens": self.total_tokens,
            "costUsd": round(self.cost_usd, 6),
            "durationSeconds": round(self.duration_seconds, 2),
            "changedFiles": list(self.changed_files),
            "diffPatch": self.diff_patch,
            "oracle": self.oracle_result.to_dict() if self.oracle_result else None,
            "aiJudgeScore": self.ai_judge_score,
            "diagnosis": self.diagnosis,
            "metadata": dict(self.metadata),
        }


def classify_attribution(
    oracle: OracleResult | None,
    harness_status: str,
    turns: int,
    max_turns: int,
    budget_exceeded: bool = False,
    changed_files: Sequence[str] = (),
) -> str:
    """Classify the scientific root cause of an execution outcome."""
    if oracle and oracle.passed:
        return "PASS"

    if oracle and oracle.error and "Oracle script missing" in oracle.error:
        return "DATASET_INVALID"

    if budget_exceeded or harness_status == "BUDGET_EXHAUSTED":
        return "BUDGET_EXHAUSTED"

    if harness_status in ("INSTRUMENT_ERROR", "ERROR", "CRASH"):
        return "HARNESS_ERROR"

    if not changed_files and turns >= max_turns:
        return "HARNESS_ERROR"

    if oracle and not oracle.passed:
        # Agent wrote code, but logic failed ground-truth oracle assertions
        return "LLM_COGNITIVE_ERROR"

    return "HARNESS_ERROR"


def status_for_attribution(attribution: str) -> str:
    """Task fail is only a cognitive oracle miss. Other classes are missingness."""
    if attribution == "PASS":
        return "PASS"
    if attribution == "LLM_COGNITIVE_ERROR":
        return "FAIL"
    return "UNDETERMINABLE"


@dataclass
class BaaCReport:
    """Aggregated BaaC evaluation matrix and attribution report."""

    run_id: str
    preset: str
    model: str
    mode: str
    results: List[ChallengeExecutionResult] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_count(self) -> int:
        return len(self.results)

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.status == "PASS")

    @property
    def overall_pass_rate_pct(self) -> float:
        return round((self.pass_count / self.total_count * 100), 1) if self.total_count else 0.0

    @property
    def total_cost_usd(self) -> float:
        return sum(r.cost_usd for r in self.results)

    @property
    def total_tokens(self) -> int:
        return sum(r.total_tokens for r in self.results)

    @property
    def total_duration_seconds(self) -> float:
        return sum(r.duration_seconds for r in self.results)

    def tier_pass_rate(self, tier: str) -> Tuple[int, int, float]:
        tier_results = [r for r in self.results if r.tier.lower() == tier.lower()]
        passed = sum(1 for r in tier_results if r.status == "PASS")
        total = len(tier_results)
        pct = round((passed / total * 100), 1) if total else 0.0
        return passed, total, pct

    def is_tier_promoted(self, tier: str, *, threshold_pct: float = 80.0) -> bool:
        """Return whether a tier meets the explicit held-out promotion bar."""
        _, total, rate = self.tier_pass_rate(tier)
        return total > 0 and rate >= threshold_pct

    def attribution_breakdown(self) -> Dict[str, int]:
        counts = {
            "PASS": 0,
            "LLM_COGNITIVE_ERROR": 0,
            "HARNESS_ERROR": 0,
            "BUDGET_EXHAUSTED": 0,
            "DATASET_INVALID": 0,
        }
        for r in self.results:
            counts[r.attribution] = counts.get(r.attribution, 0) + 1
        return counts

    def to_dict(self) -> Dict[str, Any]:
        return {
            "runId": self.run_id,
            "timestamp": self.timestamp,
            "preset": self.preset,
            "model": self.model,
            "mode": self.mode,
            "metadata": self.metadata,
            "summary": {
                "totalChallenges": self.total_count,
                "passedCount": self.pass_count,
                "overallPassRatePct": self.overall_pass_rate_pct,
                "totalTokens": self.total_tokens,
                "totalCostUsd": round(self.total_cost_usd, 6),
                "totalDurationSeconds": round(self.total_duration_seconds, 2),
                "attribution": self.attribution_breakdown(),
            },
            "results": [r.to_dict() for r in self.results],
        }

    def to_markdown_table(self) -> str:
        lines = []
        lines.append(f"# BaaC Evaluation Matrix — {self.preset} ({self.model})")
        lines.append(f"**Run ID**: `{self.run_id}` | **Mode**: `{self.mode}` | **Date**: `{self.timestamp}`\n")

        lines.append("| Challenge ID | Scope | Context | Tier | Status | Attribution | Turns | Tokens | Cost ($) | Duration | Diagnosis |")
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")

        for r in self.results:
            diag = r.diagnosis[:35].replace("\n", " ") if r.diagnosis else "All falsifiers green"
            row = (
                f"| `{r.challenge_id}` | `{r.scope}` | `{r.context_bracket}` | `{r.tier}` | **{r.status}** | `{r.attribution}` | "
                f"{r.turns} | {r.total_tokens:,} | ${r.cost_usd:.5f} | {r.duration_seconds:.2f}s | {diag} |"
            )
            lines.append(row)

        lines.append("\n## Summary KPIs")
        lines.append(f"- **Overall Pass Rate**: {self.pass_count}/{self.total_count} ({self.overall_pass_rate_pct}%)")
        for tier in ("tier-1", "tier-2", "tier-3", "tier-4", "tier-5", "tier-6"):
            p, t, pct = self.tier_pass_rate(tier)
            if t > 0:
                lines.append(f"- **{tier.upper()} Pass Rate**: {p}/{t} ({pct}%)")
        lines.append(f"- **Total Tokens**: {self.total_tokens:,}")
        lines.append(f"- **Total Cost**: ${self.total_cost_usd:.5f} USD")
        lines.append(f"- **Total Duration**: {self.total_duration_seconds:.2f}s")
        lines.append(f"- **Attribution Breakdown**: {dict(self.attribution_breakdown())}")

        return "\n".join(lines)
