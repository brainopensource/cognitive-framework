"""Speculative Multi-Branch Language Agent Tree Search (LATS / SWE-Search) with Process Reward Models (ThinkPRM).

Samples multiple candidate patch trajectories in parallel git snapshots, computes step-level PRM scores,
and executes UCT-based best-of-N tree search with automated rollback.
"""

from __future__ import annotations
import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence


@dataclass
class CandidateBranch:
    """Represents a speculative exploratory patch branch."""
    branch_id: str
    checkpoint_id: str
    patch_proposal: dict[str, str]
    oracle_passed: bool = False
    prm_score: float = 0.0
    composite_score: float = 0.0
    ast_valid: bool = True
    error_msg: str = ""
    diff_lines_count: int = 0


class ProcessRewardVerifier:
    """Evaluates the intermediate step quality of a proposed patch before full regression."""

    def evaluate_step_quality(
        self,
        patch_proposal: dict[str, str],
        ast_valid: bool,
        test_output: str,
        test_passed: bool,
    ) -> float:
        if not ast_valid:
            return 0.0
        if test_passed:
            return 1.0

        score = 0.3  # Base score for valid AST

        # 1. Compactness reward (penalize massive sprawling diffs)
        rep_lines = len(patch_proposal.get("replacement_chunk", "").splitlines())
        if 1 <= rep_lines <= 10:
            score += 0.25
        elif rep_lines <= 30:
            score += 0.10

        # 2. Traceback reduction reward
        if "FAILED" in test_output or "ERROR" in test_output:
            fail_count = len(re.findall(r"FAILED\s+", test_output))
            if fail_count == 1:
                score += 0.20  # Isolated to only 1 failing test
            elif fail_count <= 3:
                score += 0.10

        # 3. Absence of internal crash errors (e.g. UnboundLocalError, NameError)
        if not any(err in test_output for err in ("UnboundLocalError", "NameError", "AttributeError")):
            score += 0.15

        return round(min(0.95, score), 4)


class SpeculativeMCTSSearch:
    """Manages speculative multi-candidate patch search with ThinkPRM step scoring."""

    def __init__(self, workspace, branching_factor: int = 4, c_puct: float = 1.414):
        self.ws = workspace
        self.k = branching_factor
        self.c = c_puct
        self.prm_verifier = ProcessRewardVerifier()

    def explore_candidates(
        self,
        sample_fn: Callable[[float], dict[str, str]],
        oracle_eval: Callable[[], bool],
        test_runner_fn: Callable[[], tuple[bool, str]] | None = None,
    ) -> tuple[dict[str, str] | None, list[CandidateBranch]]:
        """Explore K candidate patch variations and return winning patch if found."""
        candidates: list[CandidateBranch] = []

        for i in range(self.k):
            chk_id = self.ws.git_checkpoint(f"mcts_branch_{i}")
            temp = 0.1 + (0.15 * i)
            proposal = sample_fn(temp)

            if not proposal.get("path"):
                self.ws.git_rollback()
                continue

            res = self.ws.patch_apply(
                path=proposal.get("path", ""),
                target_chunk=proposal.get("target_chunk", ""),
                replacement_chunk=proposal.get("replacement_chunk", ""),
            )

            passed = False
            test_out = ""
            if res.ok:
                if test_runner_fn:
                    passed, test_out = test_runner_fn()
                else:
                    try:
                        passed = oracle_eval()
                    except Exception as e:
                        passed = False
                        test_out = str(e)

            prm = self.prm_verifier.evaluate_step_quality(
                patch_proposal=proposal,
                ast_valid=res.ok,
                test_output=test_out,
                test_passed=passed,
            )

            diff_lines = len(proposal.get("replacement_chunk", "").splitlines())
            # UCT-inspired composite score: 1.0 if passed, else scaled PRM score
            composite = 1.0 if passed else prm

            candidates.append(
                CandidateBranch(
                    branch_id=f"branch_{i}",
                    checkpoint_id=chk_id,
                    patch_proposal=proposal,
                    oracle_passed=passed,
                    prm_score=prm,
                    composite_score=composite,
                    ast_valid=res.ok,
                    error_msg=res.output if not res.ok else test_out,
                    diff_lines_count=diff_lines,
                )
            )
            self.ws.git_rollback()

            # Early exit if an exact pass is found
            if passed and res.ok:
                self.ws.patch_apply(
                    path=proposal["path"],
                    target_chunk=proposal["target_chunk"],
                    replacement_chunk=proposal["replacement_chunk"],
                )
                return proposal, candidates

        # Rerank candidates by composite score
        candidates.sort(key=lambda c: c.composite_score, reverse=True)

        # If any candidate passed oracle, apply top winner
        top_cand = candidates[0] if candidates else None
        if top_cand and top_cand.oracle_passed and top_cand.ast_valid:
            self.ws.patch_apply(
                path=top_cand.patch_proposal["path"],
                target_chunk=top_cand.patch_proposal["target_chunk"],
                replacement_chunk=top_cand.patch_proposal["replacement_chunk"],
            )
            return top_cand.patch_proposal, candidates

        return None, candidates
