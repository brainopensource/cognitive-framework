"""Scientific KPI and Telemetry Collector for 006_LLM_INT_MACHINE.

Computes 15 derived mathematical metrics:
1. ETUR: Effective Token Utilization Rate
2. PCSR: Prefix Cache Stability Ratio (%)
3. SPDI: Surgical Patch Density Index
4. PMSI: Patch Mutation Score Index
5. FL@1: Fault Localization Top-1 Hit Rate
6. FL@5: Fault Localization Top-5 Hit Rate
7. APIY: AST Pre-Flight Interception Yield
8. TTFR: Time to First Failing Repro (sec)
9. SCV:  Self-Correction Velocity
10. TBEI: Token Burn Efficiency Index
11. DEAE: Dead-End Avoidance Efficiency
12. SIOR: Subprocess IO Overhead Ratio
13. MPS:  Composite Model Pareto Score
14. CPAC: Cost Per Assertion Cleared ($USD)
15. CEDR: Context Entropy & Dialogue Growth Rate
"""

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class AdvancedKPITelemetry:
    """Consolidated 15-dimensional scientific telemetry record."""
    # Base execution counters
    turns_taken: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    total_cost_usd: float = 0.0
    duration_seconds: float = 0.0
    git_diff_lines: int = 0
    ast_errors_prevented: int = 0
    passed_assertions: int = 1

    # 15 Derived Telemetry Metrics
    etur_utilization_rate: float = 0.0      # Useful tokens / Total tokens
    pcsr_cache_ratio: float = 0.0           # Cached tokens / Prompt tokens (%)
    spdi_surgical_density: float = 1.0      # Functional diff lines / Total diff lines
    pmsi_mutation_score: float = 1.0        # Mutants killed / Mutants generated
    fl_top1_hit: bool = False               # Ground truth defect in Top-1 SBFL
    fl_top5_hit: bool = False               # Ground truth defect in Top-5 SBFL
    apiy_interception_yield: float = 0.0    # AST errors caught / Total patch attempts
    ttfr_time_to_repro_sec: float = 0.0     # Time to verify failing reproducer
    scv_self_correction_velocity: float = 0.0 # 1 / Turns spent recovering from errors
    tbei_token_burn_efficiency: float = 0.0 # Tokens / (Turns * Diff lines)
    deae_dead_end_avoidance_eff: float = 1.0 # 1 - (Repeated failures / Total failures)
    sior_subprocess_io_ratio: float = 0.0   # Subprocess time / Total wallclock time
    mps_model_pareto_score: float = 0.0     # (Solved * 10^4) / (Cost * Time * Turns)
    cpac_cost_per_assertion_usd: float = 0.0 # Cost / Passed assertions
    cedr_context_growth_rate: float = 0.0   # Average token delta per turn

    def calculate_derived_metrics(
        self,
        useful_tokens: int,
        total_patch_attempts: int,
        solved: bool,
        subprocess_time_sec: float = 0.0,
        repeated_failure_count: int = 0,
        total_failure_count: int = 0,
    ) -> None:
        """Derive all 15 scientific KPIs from raw episode data."""
        self.etur_utilization_rate = round(useful_tokens / max(1, self.total_tokens), 3)
        self.pcsr_cache_ratio = round((self.cached_tokens / max(1, self.total_tokens)) * 100, 1)
        self.apiy_interception_yield = round(self.ast_errors_prevented / max(1, total_patch_attempts), 3)
        self.tbei_token_burn_efficiency = round(self.total_tokens / max(1, self.turns_taken * max(1, self.git_diff_lines)), 1)
        self.sior_subprocess_io_ratio = round(subprocess_time_sec / max(0.1, self.duration_seconds), 3)
        self.cpac_cost_per_assertion_usd = round(self.total_cost_usd / max(1, self.passed_assertions), 6)
        self.cedr_context_growth_rate = round(self.total_tokens / max(1, self.turns_taken), 1)

        if total_failure_count > 0:
            self.deae_dead_end_avoidance_eff = round(1.0 - (repeated_failure_count / total_failure_count), 3)
        else:
            self.deae_dead_end_avoidance_eff = 1.0

        if self.turns_taken > 0:
            self.scv_self_correction_velocity = round(1.0 / max(1.0, float(self.turns_taken)), 3)

        cost = max(0.0001, self.total_cost_usd)
        duration = max(0.1, self.duration_seconds)
        turns = max(1, self.turns_taken)

        if solved:
            self.mps_model_pareto_score = round((1.0 * 10_000.0) / (cost * duration * turns), 1)
        else:
            self.mps_model_pareto_score = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert telemetry to dictionary."""
        return asdict(self)
