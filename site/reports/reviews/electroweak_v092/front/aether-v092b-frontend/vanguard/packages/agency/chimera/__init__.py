"""Vanguard CHIMERA: Neuro-Symbolic Adaptive Meta-Harness.

Exports the facade, configuration, cognitive blackboard, governor, router,
and execution engine for the decoupled `vg-chimera-v1` / `vg-code-chimera` agent.
"""

from __future__ import annotations

from .blackboard import (
    CalibratedConfidence,
    CognitiveBlackboard,
    CognitiveBudget,
    CognitiveDirective,
    CognitiveDirectiveKind,
    Fact,
    Hypothesis,
    PatchCandidate,
    RankedFile,
    RankedSymbol,
    RankedTest,
    TaskFeatures,
    TrajectorySummary,
    UncertaintyProfile,
    VerificationRecord,
)
from .compiler import (
    CHIMERA_SYSTEM_PROMPT,
    CHIMERA_TOOLS_SCHEMA,
    ChimeraContextCompiler,
)
from .engine import ChimeraEngine, ChimeraOutcome
from .facade import (
    CHIMERA_PRESET_CODE,
    CHIMERA_PRESET_V1,
    ChimeraConfig,
    ChimeraFacade,
)
from .governor import GovernorPolicy, MetaCognitiveGovernor
from .patcher import ChimeraAtomicPatcher, PatcherResult
from .retrieval import RetrievalBid, RetrievalMarket
from .router import BanditArm, CognitiveRouter
from .search import BestFirstEngineeringSearch, EngineeringState, SearchNode
from .skills import BUILTIN_SKILLS, Skill, SkillRegistry
from .symbolic import InvariantSolution, SymbolicCortex, SyntaxCheckResult
from .verification import (
    PatchRiskAssessment,
    VerificationCortex,
    VerificationLevel,
)

__all__ = [
    "CHIMERA_PRESET_CODE",
    "CHIMERA_PRESET_V1",
    "BUILTIN_SKILLS",
    "BanditArm",
    "BestFirstEngineeringSearch",
    "CalibratedConfidence",
    "ChimeraAtomicPatcher",
    "ChimeraConfig",
    "ChimeraContextCompiler",
    "ChimeraEngine",
    "ChimeraFacade",
    "ChimeraOutcome",
    "CognitiveBlackboard",
    "CognitiveBudget",
    "CognitiveDirective",
    "CognitiveDirectiveKind",
    "CognitiveRouter",
    "EngineeringState",
    "Fact",
    "GovernorPolicy",
    "Hypothesis",
    "InvariantSolution",
    "MetaCognitiveGovernor",
    "PatchCandidate",
    "PatchRiskAssessment",
    "PatcherResult",
    "RankedFile",
    "RankedSymbol",
    "RankedTest",
    "RetrievalBid",
    "RetrievalMarket",
    "SearchNode",
    "Skill",
    "SkillRegistry",
    "SymbolicCortex",
    "SyntaxCheckResult",
    "TaskFeatures",
    "TrajectorySummary",
    "UncertaintyProfile",
    "VerificationCortex",
    "VerificationLevel",
    "VerificationRecord",
]
