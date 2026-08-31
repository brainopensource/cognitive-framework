"""Meta-Cognitive Governor for CHIMERA.

Decides *how* to compute rather than generating code directly.
Allocates compute budgets, selects cognitive routes, triggers search / replays,
and prevents unproductive loops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from .blackboard import (
    CognitiveBlackboard,
    CognitiveDirective,
    CognitiveDirectiveKind,
)


@dataclass(frozen=True, slots=True)
class GovernorPolicy:
    """Configurable thresholds for the meta-cognitive governor."""

    max_failed_attempts_before_escalate: int = 2
    max_turns_without_verification: int = 3
    search_uncertainty_threshold: float = 0.65
    cheap_route_cost_ceiling_usd: float = 0.05
    enable_symbolic_solving: bool = True
    enable_branch_search: bool = True


class MetaCognitiveGovernor:
    """Meta-Cognitive Governor managing computational phases and routing directives."""

    def __init__(self, policy: GovernorPolicy | None = None) -> None:
        self.policy = policy or GovernorPolicy()

    def decide(
        self,
        board: CognitiveBlackboard,
        failure_streak: int = 0,
        turns_since_progress: int = 0,
    ) -> CognitiveDirective:
        """Evaluate blackboard state and output next cognitive directive."""
        # 1. Terminal Check: If all tests pass and verification is fresh -> FINISH
        if board.verifications and board.verifications[-1].passed and board.patches:
            return CognitiveDirective(
                kind=CognitiveDirectiveKind.FINISH,
                objective="Complete task with verified green test suite",
                route="RULE",
                rationale_code="VERIFIED_PASSING",
            )

        # 2. Budget Depletion Check -> STOP
        if not board.budget.available:
            return CognitiveDirective(
                kind=CognitiveDirectiveKind.STOP,
                objective="Cognitive budget exhausted",
                route="RULE",
                rationale_code="BUDGET_EXHAUSTED",
            )

        # 3. Phase: Mathematical / Algorithmic / Invariants Analysis
        if board.task_features.mathematical_invariants and not any(f.kind == "invariant" for f in board.facts):
            return CognitiveDirective(
                kind=CognitiveDirectiveKind.SOLVE,
                objective="Extract and solve mathematical constraints and invariants",
                route="SYMBOLIC_SOLVER",
                rationale_code="SOLVE_INVARIANTS",
            )

        # 4. Phase: Exploration / Localization if candidate files unknown
        if not board.candidate_files or board.uncertainty.localization_uncertainty > 0.7:
            return CognitiveDirective(
                kind=CognitiveDirectiveKind.RETRIEVE,
                objective="Identify target files and inspect relevant source symbols",
                route="LDA_AST",
                rationale_code="LOCALIZE_WORKSPACE",
            )

        # 5. Anti-Loop / Search Fork: Repeated failures trigger search or escalation
        if failure_streak >= self.policy.max_failed_attempts_before_escalate:
            if self.policy.enable_branch_search and board.budget.used_search_nodes < board.budget.max_search_nodes:
                return CognitiveDirective(
                    kind=CognitiveDirectiveKind.FORK,
                    objective=f"Branch alternative hypothesis after {failure_streak} test failures",
                    route="SEARCH",
                    rationale_code="FAILURE_STREAK_FORK",
                )
            else:
                return CognitiveDirective(
                    kind=CognitiveDirectiveKind.ESCALATE,
                    objective="Escalate to frontier reasoning for surgical diagnosis",
                    route="FRONTIER_LLM",
                    rationale_code="FAILURE_STREAK_ESCALATE",
                )

        # 6. Greenfield Scaffold Phase
        if board.task_features.kind == "greenfield" and not board.patches:
            return CognitiveDirective(
                kind=CognitiveDirectiveKind.GENERATE,
                objective="Scaffold project structure, entrypoint, and test suite",
                route="FRONTIER_LLM",
                rationale_code="GREENFIELD_SCAFFOLD",
            )

        # 7. Unverified Patch: Need verification
        if board.patches and (not board.verifications or turns_since_progress >= self.policy.max_turns_without_verification):
            return CognitiveDirective(
                kind=CognitiveDirectiveKind.VERIFY,
                objective="Execute test suite to obtain deterministic verification receipt",
                route="RULE",
                rationale_code="VERIFY_PATCH",
            )

        # 8. High Uncertainty / Complex Code Generation -> Frontier LLM
        if board.uncertainty.patch_uncertainty >= self.policy.search_uncertainty_threshold or board.task_features.multi_file:
            return CognitiveDirective(
                kind=CognitiveDirectiveKind.GENERATE,
                objective="Synthesize atomic multi-file patch resolving failing tests",
                route="FRONTIER_LLM",
                rationale_code="FRONTIER_PATCH_SYNTHESIS",
            )

        # 9. Default Action: Refine patch using cheap/direct generation
        return CognitiveDirective(
            kind=CognitiveDirectiveKind.ACT,
            objective="Apply minimal implementation and run test suite",
            route="CHEAP_LLM",
            rationale_code="DEFAULT_TDD_STEP",
        )
