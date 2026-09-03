"""BaaC Library Package."""

from .budget import BudgetCapConfig, BudgetExceededError, BudgetTracker, MODEL_PRICING_TABLE
from .cache import clean_scratch_directories, purge_bytecode_caches, reset_environment
from .eval_judge import AIJudgeScore, EvaluationOutcome, evaluate_challenge
from .models import LAMModelPort, OllamaModelPort, OpenRouterModelPort
from .oracle import OracleResult, run_external_oracle
from .report import BaaCReport, ChallengeExecutionResult, classify_attribution
from .runner import BaaCRunner
from .state import (
    clean_scratch_workspace,
    compute_directory_manifest,
    compute_file_sha256,
    generate_challenge_manifest,
    materialize_scratch_workspace,
    parse_manifest_file,
    verify_challenge_zero_state,
    write_manifest_file,
)

__all__ = [
    "AIJudgeScore",
    "BaaCReport",
    "BaaCRunner",
    "BudgetCapConfig",
    "BudgetExceededError",
    "BudgetTracker",
    "ChallengeExecutionResult",
    "EvaluationOutcome",
    "LAMModelPort",
    "MODEL_PRICING_TABLE",
    "OllamaModelPort",
    "OpenRouterModelPort",
    "OracleResult",
    "clean_scratch_directories",
    "clean_scratch_workspace",
    "classify_attribution",
    "compute_directory_manifest",
    "compute_file_sha256",
    "evaluate_challenge",
    "generate_challenge_manifest",
    "materialize_scratch_workspace",
    "parse_manifest_file",
    "purge_bytecode_caches",
    "reset_environment",
    "run_external_oracle",
    "verify_challenge_zero_state",
    "write_manifest_file",
]
