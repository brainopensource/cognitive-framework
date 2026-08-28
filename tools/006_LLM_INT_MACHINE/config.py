"""Configuration, Feature Flag Matrix, and Centralized Version Registry for 006_LLM_INT_MACHINE.

Enables scientific ablation studies and deterministic replay by toggling individual cognitive
and execution features, computing SHA-256 config hashes, and maintaining versioned presets.
"""

from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Mapping


@dataclass(frozen=True)
class HarnessConfig:
    """Feature flag matrix and parameter specification for ablation benchmarking."""
    # Identification and Versioning
    config_name: str = "v1.2_sota_full"
    version_tag: str = "1.2.0"
    seed: int = 42
    
    # Feature 1: Context Stability & Prefix Caching (L1-L5 model)
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
    
    # Feature 8: AST Symbol Code Graph & Call-Chain Indexer (v2.0)
    use_code_graph: bool = False
    
    # Feature 9: Spectrum-Based Fault Localization (SBFL Ochiai) (v2.0)
    use_sbfl_localization: bool = False
    
    # Feature 10: Speculative Multi-Branch MCTS Search (v2.1)
    use_mcts_search: bool = False
    mcts_branching_factor: int = 3
    mcts_exploration_c: float = 1.414
    
    # Feature 11: Line-Level Mutation Falsification Engine (v2.2)
    use_mutation_testing: bool = False
    mutation_threshold: float = 0.80

    # Feature 12: Causal Counterfactual Dual-Slicing (v3.0 - Pillar 2)
    use_causal_slicing: bool = False

    # Feature 13: Adversarial Invariant Fuzzing & QA Synthesis (v3.1 - Pillar 3)
    use_adversarial_fuzzing: bool = False

    # Feature 14: Agent-RLVR & SWE-RL Verifiable Trajectory Logging (v3.2 - Pillar 4)
    use_rlvr_logging: bool = False

    # Feature 15: SMT-Guided CEGIS Synthesis (v4.0 - 100% Pillar 1)
    use_cegis_verification: bool = False

    # Feature 16: Dynamic Symbolic Execution & Concolic Path Fuzzing (v4.1 - 100% Pillar 2)
    use_concolic_fuzzing: bool = False

    # Feature 17: Grok-Style Multi-Agent Arena Tournament & Adversarial Jury (v4.2 - 100% Pillar 3)
    use_arena_tournament: bool = False

    # Feature 18: Time-Travel Deterministic Record-Replay Debugger (v4.3 - 100% Pillar 4)
    use_time_travel_debugger: bool = False

    # Feature 19: Hermes Closed-Loop Dynamic Skill Compiler (v4.4 - 100% Pillar 5)
    use_dynamic_skills: bool = False

    # Feature 20: Scale-Up Test-Time Compute Cluster MCTS (v4.5 - 100% Pillar 6)
    use_cluster_mcts: bool = False
    cluster_mcts_samples: int = 16
    
    # Feature 21: Autonomous Claude-Style Clean-Slate Subagent Sandbox (v5.0)
    use_subagent_sandboxing: bool = False

    # Feature 22: Lightweight Prompting & XML Tool Fallback for Small/Free Models
    use_lightweight_prompt: bool = False

    # Multi-Model Hierarchical Routing Settings (v5.0)
    planner_model: str = ""
    worker_model: str = ""
    qa_model: str = ""
    enable_hierarchical_routing: bool = False
    
    def resolve_planner(self) -> str:
        return self.planner_model or self.model

    def resolve_worker(self) -> str:
        return self.worker_model or self.model

    def resolve_qa(self) -> str:
        return self.qa_model or self.worker_model or self.model

    # Execution & Model Settings
    model: str = "openrouter/free"
    temperature: float = 0.0
    max_turns: int = 15
    token_ceiling: int = 64_000
    timeout_per_command_sec: int = 30
    
    # Cost & Rate Limits
    max_api_calls: int = 50
    max_cost_usd: float = 0.30

    def config_hash(self) -> str:
        """Compute a deterministic SHA-256 digest of all active parameters."""
        data = asdict(self)
        canonical_json = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()[:16]

    def derive(self, **overrides: Any) -> HarnessConfig:
        """Return a new immutable HarnessConfig with specific overrides applied."""
        current = asdict(self)
        current.update(overrides)
        return HarnessConfig(**current)

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary including hash."""
        d = asdict(self)
        d["config_hash"] = self.config_hash()
        return d


# ==============================================================================
# Centralized Versioned Preset Registry
# ==============================================================================

CONFIG_V1_0_BASELINE = HarnessConfig(
    config_name="v1.0_baseline_react",
    version_tag="1.0.0",
    use_l1_l5_prefix_stability=False,
    use_ast_preflight=False,
    use_reproduce_first=False,
    use_speculative_rollback=False,
    use_dialogue_compaction=False,
    use_dead_ends_tracking=False,
    use_paged_output=False,
    use_code_graph=False,
    use_sbfl_localization=False,
    use_mcts_search=False,
    use_mutation_testing=False,
    max_turns=12,
)

CONFIG_V1_1_VANGUARD_CORE = HarnessConfig(
    config_name="v1.1_vanguard_core",
    version_tag="1.1.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=False,
    use_reproduce_first=False,
    use_speculative_rollback=False,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=False,
    use_code_graph=False,
    use_sbfl_localization=False,
    use_mcts_search=False,
    use_mutation_testing=False,
    max_turns=12,
)

CONFIG_V1_2_SOTA_FULL = HarnessConfig(
    config_name="v1.2_sota_full",
    version_tag="1.2.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=False,
    use_sbfl_localization=False,
    use_mcts_search=False,
    use_mutation_testing=False,
    max_turns=12,
)

CONFIG_V2_0_SBFL_GRAPH = HarnessConfig(
    config_name="v2.0_sbfl_graph",
    version_tag="2.0.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_mcts_search=False,
    use_mutation_testing=False,
    max_turns=12,
)

CONFIG_V2_1_MCTS_SPECULATIVE = HarnessConfig(
    config_name="v2.1_mcts_speculative",
    version_tag="2.1.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_mcts_search=True,
    mcts_branching_factor=3,
    use_mutation_testing=False,
    max_turns=15,
)

CONFIG_V2_2_MUTATION_ROBUST = HarnessConfig(
    config_name="v2.2_mutation_robust",
    version_tag="2.2.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_mcts_search=False,
    use_mutation_testing=True,
    mutation_threshold=0.80,
    max_turns=12,
)

CONFIG_V2_3_COMPOUND_FULL = HarnessConfig(
    config_name="v2.3_compound_full",
    version_tag="2.3.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_mcts_search=True,
    mcts_branching_factor=3,
    use_mutation_testing=True,
    mutation_threshold=0.80,
    max_turns=15,
)

CONFIG_V3_0_CAUSAL_MCTS = HarnessConfig(
    config_name="v3.0_causal_mcts",
    version_tag="3.0.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_mcts_search=True,
    mcts_branching_factor=4,
    use_mutation_testing=True,
    mutation_threshold=0.80,
    max_turns=15,
)

CONFIG_V3_1_ADVERSARIAL_APEX = HarnessConfig(
    config_name="v3.1_adversarial_apex",
    version_tag="3.1.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_mcts_search=True,
    mcts_branching_factor=6,
    use_mutation_testing=True,
    mutation_threshold=0.85,
    use_adversarial_fuzzing=True,
    max_turns=18,
)

CONFIG_V3_2_RLVR_SOTA_90 = HarnessConfig(
    config_name="v3.2_rlvr_sota_90",
    version_tag="3.2.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_mcts_search=True,
    mcts_branching_factor=8,
    use_mutation_testing=True,
    mutation_threshold=0.85,
    use_adversarial_fuzzing=True,
    use_rlvr_logging=True,
    max_turns=20,
)

CONFIG_V4_0_CEGIS_SMT = HarnessConfig(
    config_name="v4.0_cegis_smt",
    version_tag="4.0.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_mcts_search=True,
    mcts_branching_factor=8,
    use_mutation_testing=True,
    mutation_threshold=0.85,
    use_adversarial_fuzzing=True,
    use_cegis_verification=True,
    max_turns=20,
)

CONFIG_V4_1_CONCOLIC_DSE = HarnessConfig(
    config_name="v4.1_concolic_dse",
    version_tag="4.1.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_mcts_search=True,
    mcts_branching_factor=8,
    use_mutation_testing=True,
    use_adversarial_fuzzing=True,
    use_cegis_verification=True,
    use_concolic_fuzzing=True,
    max_turns=20,
)

CONFIG_V4_2_ARENA_DEBATE = HarnessConfig(
    config_name="v4.2_arena_debate",
    version_tag="4.2.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_mcts_search=True,
    use_arena_tournament=True,
    use_mutation_testing=True,
    use_adversarial_fuzzing=True,
    use_cegis_verification=True,
    use_concolic_fuzzing=True,
    max_turns=20,
)

CONFIG_V4_3_TIMETRAVEL_REPLAY = HarnessConfig(
    config_name="v4.3_timetravel_replay",
    version_tag="4.3.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_time_travel_debugger=True,
    use_arena_tournament=True,
    use_mutation_testing=True,
    use_adversarial_fuzzing=True,
    use_cegis_verification=True,
    use_concolic_fuzzing=True,
    max_turns=20,
)

CONFIG_V4_4_HERMES_SKILLS = HarnessConfig(
    config_name="v4.4_hermes_skills",
    version_tag="4.4.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_time_travel_debugger=True,
    use_dynamic_skills=True,
    use_arena_tournament=True,
    use_mutation_testing=True,
    use_adversarial_fuzzing=True,
    use_cegis_verification=True,
    use_concolic_fuzzing=True,
    max_turns=20,
)

CONFIG_V4_5_SOTA_100_APEX = HarnessConfig(
    config_name="v4.5_sota_100_apex",
    version_tag="4.5.0",
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_time_travel_debugger=True,
    use_dynamic_skills=True,
    use_arena_tournament=True,
    use_mutation_testing=True,
    use_adversarial_fuzzing=True,
    use_cegis_verification=True,
    use_concolic_fuzzing=True,
    use_cluster_mcts=True,
    cluster_mcts_samples=32,
    use_rlvr_logging=True,
    max_turns=25,
)


CONFIG_V5_0_HIERARCHICAL_APEX = HarnessConfig(
    config_name="v5.0_hierarchical_apex",
    version_tag="5.0.0",
    model="deepseek/deepseek-v4-flash-0731",
    planner_model="deepseek/deepseek-v4-pro-0813",
    worker_model="deepseek/deepseek-v4-flash-0731",
    qa_model="minimax/minimax-m3:free",
    enable_hierarchical_routing=True,
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_speculative_rollback=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_code_graph=True,
    use_sbfl_localization=True,
    use_causal_slicing=True,
    use_time_travel_debugger=True,
    use_dynamic_skills=True,
    use_arena_tournament=True,
    use_mutation_testing=True,
    use_adversarial_fuzzing=True,
    use_cegis_verification=True,
    use_concolic_fuzzing=True,
    use_mcts_search=True,
    use_subagent_sandboxing=True,
    use_rlvr_logging=True,
    max_turns=25,
    max_cost_usd=0.25,
)

CONFIG_V5_1_FREE_TIER = HarnessConfig(
    config_name="v5.1_free_tier",
    version_tag="5.1.0",
    model="minimax/minimax-m3:free",
    planner_model="z-ai/glm-5.2:free",
    worker_model="minimax/minimax-m3:free",
    qa_model="poolside/laguna-s-2.1:free",
    enable_hierarchical_routing=True,
    use_l1_l5_prefix_stability=True,
    use_ast_preflight=True,
    use_reproduce_first=True,
    use_dialogue_compaction=True,
    use_dead_ends_tracking=True,
    use_paged_output=True,
    use_sbfl_localization=True,
    use_lightweight_prompt=True,
    use_cegis_verification=True,
    max_turns=20,
    max_cost_usd=0.0,
)

# Backwards-compatibility aliases
CONFIG_BASELINE_REACT = CONFIG_V1_0_BASELINE
CONFIG_VANGUARD_CORE = CONFIG_V1_1_VANGUARD_CORE
CONFIG_SOTA_FULL = CONFIG_V1_2_SOTA_FULL

PRESET_REGISTRY: dict[str, HarnessConfig] = {
    "v1.0_baseline_react": CONFIG_V1_0_BASELINE,
    "v1.1_vanguard_core": CONFIG_V1_1_VANGUARD_CORE,
    "v1.2_sota_full": CONFIG_V1_2_SOTA_FULL,
    "v2.0_sbfl_graph": CONFIG_V2_0_SBFL_GRAPH,
    "v2.1_mcts_speculative": CONFIG_V2_1_MCTS_SPECULATIVE,
    "v2.2_mutation_robust": CONFIG_V2_2_MUTATION_ROBUST,
    "v2.3_compound_full": CONFIG_V2_3_COMPOUND_FULL,
    "v3.0_causal_mcts": CONFIG_V3_0_CAUSAL_MCTS,
    "v3.1_adversarial_apex": CONFIG_V3_1_ADVERSARIAL_APEX,
    "v3.2_rlvr_sota_90": CONFIG_V3_2_RLVR_SOTA_90,
    "v4.0_cegis_smt": CONFIG_V4_0_CEGIS_SMT,
    "v4.1_concolic_dse": CONFIG_V4_1_CONCOLIC_DSE,
    "v4.2_arena_debate": CONFIG_V4_2_ARENA_DEBATE,
    "v4.3_timetravel_replay": CONFIG_V4_3_TIMETRAVEL_REPLAY,
    "v4.4_hermes_skills": CONFIG_V4_4_HERMES_SKILLS,
    "v4.5_sota_100_apex": CONFIG_V4_5_SOTA_100_APEX,
    "v5.0_hierarchical_apex": CONFIG_V5_0_HIERARCHICAL_APEX,
    "v5.1_free_tier": CONFIG_V5_1_FREE_TIER,
    "v5.0": CONFIG_V5_0_HIERARCHICAL_APEX,
    "v5.1": CONFIG_V5_1_FREE_TIER,
    "hierarchical": CONFIG_V5_0_HIERARCHICAL_APEX,
    "free_tier": CONFIG_V5_1_FREE_TIER,
    # Aliases
    "baseline": CONFIG_V1_0_BASELINE,
    "vanguard_core": CONFIG_V1_1_VANGUARD_CORE,
    "sota_full": CONFIG_V1_2_SOTA_FULL,
    "compound": CONFIG_V2_3_COMPOUND_FULL,
    "sota_90": CONFIG_V3_2_RLVR_SOTA_90,
    "apex": CONFIG_V3_1_ADVERSARIAL_APEX,
    "sota_100": CONFIG_V4_5_SOTA_100_APEX,
    "cegis": CONFIG_V4_0_CEGIS_SMT,
    "concolic": CONFIG_V4_1_CONCOLIC_DSE,
    "arena": CONFIG_V4_2_ARENA_DEBATE,
    "timetravel": CONFIG_V4_3_TIMETRAVEL_REPLAY,
    "hermes": CONFIG_V4_4_HERMES_SKILLS,
}


def get_preset(name_or_alias: str) -> HarnessConfig:
    """Retrieve preset config by name or alias, raising KeyError if invalid."""
    key = name_or_alias.strip().lower()
    if key in PRESET_REGISTRY:
        return PRESET_REGISTRY[key]
    available = ", ".join(sorted(PRESET_REGISTRY.keys()))
    raise KeyError(f"Unknown config preset '{name_or_alias}'. Available presets: {available}")
