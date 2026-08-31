"""Vanguard 1-Forge (Reflexive Agentic Micro-Forge) subsystem.

A high-performance reflexive agency substrate with fast-cycle TDD,
closed-loop admission gate, atomic patching, and structured compaction.
"""

from __future__ import annotations

from .compiler import (
    FORGE_SYSTEM_PROMPT,
    FORGE_TOOLS_SCHEMA,
    ForgeContextCompiler,
    ForgeDistillStrategy,
    ForgeWorkingState,
)
from .engine import (
    AdmissionVerdict,
    FailureFingerprint,
    ForgeAdmissionGate,
    ForgeEngine,
    ForgeOutcome,
    GoalContract,
    NoProgressRule,
    RepeatedFailureRule,
    StrategyDirective,
    VerificationReceipt,
    compute_workspace_digest,
    parse_test_output,
)
from .facade import FORGE_PRESET_NAME, ForgeConfig, ForgeFacade
from .patcher import (
    ASTPatcher,
    BlockPatcher,
    FilePatch,
    ForgeAtomicPatcher,
    PatchError,
    PatchHunk,
    PatchResult,
    UnifiedDiffParser,
)

__all__ = [
    # Facade & Preset
    "FORGE_PRESET_NAME",
    "ForgeConfig",
    "ForgeFacade",
    # Engine & Admission
    "AdmissionVerdict",
    "FailureFingerprint",
    "ForgeAdmissionGate",
    "ForgeEngine",
    "ForgeOutcome",
    "GoalContract",
    "NoProgressRule",
    "RepeatedFailureRule",
    "StrategyDirective",
    "VerificationReceipt",
    "compute_workspace_digest",
    "parse_test_output",
    # Context & Compiler
    "FORGE_SYSTEM_PROMPT",
    "FORGE_TOOLS_SCHEMA",
    "ForgeContextCompiler",
    "ForgeDistillStrategy",
    "ForgeWorkingState",
    # Patcher
    "ASTPatcher",
    "BlockPatcher",
    "FilePatch",
    "ForgeAtomicPatcher",
    "PatchError",
    "PatchHunk",
    "PatchResult",
    "UnifiedDiffParser",
]
