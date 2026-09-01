"""BaaC Core Library Components."""

from __future__ import annotations

from .budget import BudgetCapConfig, BudgetExceededError, BudgetTracker, DisallowedModelError
from .oracle import OracleResult, run_external_oracle
from .report import BaaCReport, ChallengeExecutionResult, classify_attribution
from .runner import BaaCRunner, LamMockModelPort, OpenRouterLiveModelPort
from .state import (
    clean_scratch_workspace,
    compute_directory_manifest,
    generate_challenge_manifest,
    materialize_scratch_workspace,
    verify_challenge_zero_state,
)

__all__ = [
    "BudgetCapConfig",
    "BudgetExceededError",
    "BudgetTracker",
    "DisallowedModelError",
    "OracleResult",
    "run_external_oracle",
    "BaaCReport",
    "ChallengeExecutionResult",
    "classify_attribution",
    "BaaCRunner",
    "LamMockModelPort",
    "OpenRouterLiveModelPort",
    "clean_scratch_workspace",
    "compute_directory_manifest",
    "generate_challenge_manifest",
    "materialize_scratch_workspace",
    "verify_challenge_zero_state",
]
