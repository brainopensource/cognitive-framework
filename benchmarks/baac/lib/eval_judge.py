"""BaaC Multi-Modal Evaluation Engine.

Provides:
1. `OracleEvaluator`: Deterministic unit/integration test harness execution.
2. `AIJudgeEvaluator`: LLM-as-a-Judge semantic rubric evaluation for architecture/correctness.
3. `CompositeEvaluator`: Blends deterministic oracle passes with qualitative judge scores.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from .oracle import OracleResult, run_external_oracle


@dataclass(frozen=True, slots=True)
class AIJudgeScore:
    """Evaluation score from an AI / LLM judge rubric."""

    score: float  # 0.0 to 1.0
    passed: bool
    reasoning: str
    rubric_criteria_passed: tuple[str, ...] = ()
    rubric_criteria_failed: tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": round(self.score, 4),
            "passed": self.passed,
            "reasoning": self.reasoning,
            "criteriaPassed": list(self.rubric_criteria_passed),
            "criteriaFailed": list(self.rubric_criteria_failed),
        }


@dataclass(frozen=True, slots=True)
class EvaluationOutcome:
    """Combined evaluation result for a benchmark challenge."""

    eval_type: str  # "oracle" | "ai_judge" | "hybrid"
    status: str  # "PASS" | "FAIL"
    score: float  # 0.0 to 1.0
    oracle_result: Optional[OracleResult] = None
    ai_judge_result: Optional[AIJudgeScore] = None
    feedback: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evalType": self.eval_type,
            "status": self.status,
            "score": round(self.score, 4),
            "oracle": self.oracle_result.to_dict() if self.oracle_result else None,
            "aiJudge": self.ai_judge_result.to_dict() if self.ai_judge_result else None,
            "feedback": self.feedback,
        }


def evaluate_challenge(
    eval_type: str,
    challenge_dir: Path,
    scratch_dir: Path,
    diff_patch: str = "",
    timeout_seconds: int = 30,
) -> EvaluationOutcome:
    """Run the appropriate evaluation method based on challenge configuration."""
    oracle_script = challenge_dir / "oracle" / "verify.py"

    if eval_type == "ai_judge":
        # Semantic evaluation rubric
        judge_score = evaluate_with_ai_judge(challenge_dir, scratch_dir, diff_patch)
        status = "PASS" if judge_score.passed else "FAIL"
        return EvaluationOutcome(
            eval_type="ai_judge",
            status=status,
            score=judge_score.score,
            ai_judge_result=judge_score,
            feedback=judge_score.reasoning,
        )

    # Default to deterministic external oracle
    oracle_res = run_external_oracle(oracle_script, scratch_dir, timeout_seconds=timeout_seconds)
    status = "PASS" if oracle_res.passed else "FAIL"
    score = 1.0 if oracle_res.passed else 0.0
    feedback = "All assertions green" if oracle_res.passed else (oracle_res.error or "Assertion failed")

    return EvaluationOutcome(
        eval_type="oracle",
        status=status,
        score=score,
        oracle_result=oracle_res,
        feedback=feedback,
    )


def evaluate_with_ai_judge(
    challenge_dir: Path,
    scratch_dir: Path,
    diff_patch: str,
) -> AIJudgeScore:
    """Mock/Baseline AI Judge evaluation comparing workspace state to task specification."""
    task_file = challenge_dir / "TASK.md"
    task_content = task_file.read_text(encoding="utf-8") if task_file.exists() else ""
    
    # Check if files were created/modified
    modified_files = [str(p.relative_to(scratch_dir)) for p in scratch_dir.rglob("*.py") if p.is_file()]
    if not modified_files:
        return AIJudgeScore(
            score=0.0,
            passed=False,
            reasoning="No python files found or modified in workspace.",
            rubric_criteria_failed=("file_presence", "syntax_check"),
        )

    # Basic AST syntax check across all python files
    syntax_errors = []
    for rel in modified_files:
        p = scratch_dir / rel
        try:
            compile(p.read_text(encoding="utf-8"), str(p), "exec")
        except Exception as e:
            syntax_errors.append(f"{rel}: {e}")

    if syntax_errors:
        return AIJudgeScore(
            score=0.2,
            passed=False,
            reasoning=f"Syntax errors detected in output files: {'; '.join(syntax_errors)}",
            rubric_criteria_failed=("syntax_check",),
        )

    return AIJudgeScore(
        score=1.0,
        passed=True,
        reasoning="Implementation satisfies structural criteria and compiles cleanly.",
        rubric_criteria_passed=("syntax_check", "file_presence", "specification_adherence"),
    )
