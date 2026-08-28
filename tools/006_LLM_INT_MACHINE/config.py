"""Configuration and Feature Flag Matrix for 006_LLM_INT_MACHINE.

Enables scientific ablation studies by toggling individual cognitive and execution features.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping, Any


@dataclass(frozen=True)
class HarnessConfig:
    """Feature flag matrix for ablation benchmarking."""
    # Identification
    config_name: str = "sota_full"
    
    # Feature 1: Context Stability & Prefix Caching (Vanguard L1-L5 model)
    use_l1_l5_prefix_stability: bool = True
    
    # Feature 2: Surgical AST Pre-Flight Syntax Check
    use_ast_preflight: bool = True
    
    # Feature 3: Gated Dual-Loop Reproducer (Hypothesis -> Failing Repro -> Patch -> Green)
    use_reproduce_first: bool = True
    
    # Feature 4: Speculative Git Checkpoint Branching & Rollback on test regressions
    use_speculative_rollback: bool = True
    
    # Feature 5: Dialogue Compaction & Result Eviction
    use_dialogue_compaction: bool = True
    
    # Feature 6: Structured Dead-Ends Tracking (Prevents repeating failed attempts)
    use_dead_ends_tracking: bool = True
    
    # Feature 7: Paged Output Truncation (Head/Tail log preservation)
    use_paged_output: bool = True
    max_output_lines: int = 80
    head_lines: int = 25
    tail_lines: int = 50
    
    # Execution & Model Settings
    model: str = "openrouter/free"
    temperature: float = 0.0
    max_turns: int = 15
    token_ceiling: int = 64_000
    timeout_per_command_sec: int = 30
    
    # Cost & Rate Limits
    max_api_calls: int = 50
    max_cost_usd: float = 0.30


# Preset configurations for scientific ablation benchmarking
CONFIG_BASELINE_REACT = HarnessConfig(
    config_name="Baseline_Naive_ReAct",
    use_l1_l5_prefix_stability=False,
    use_ast_preflight=False,
    use_reproduce_first=False,
    use_speculative_rollback=False,
    use_dialogue_compaction=False,
    use_dead_ends_tracking=False,
    use_paged_output=False,
    max_turns=12,
)

CONFIG_VANGUARD_CORE = HarnessConfig(
    config_name="Vanguard_Core_Substrate",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=False,
    use_reproduce_first=False,
    use_speculative_rollback=False,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=False,
    max_turns=12,
)

CONFIG_SOTA_FULL = HarnessConfig(
    config_name="SOTA_Full_Intelligent_Machine",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    max_turns=12,
)
