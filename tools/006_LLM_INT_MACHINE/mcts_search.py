"""Speculative Multi-Branch Language Agent Tree Search (LATS) Controller for 006_LLM_INT_MACHINE.

Samples multiple candidate patch trajectories in parallel git snapshots and selects winning paths via UCT.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence


@dataclass
class CandidateBranch:
    """Represents a speculative exploratory patch branch."""
    branch_id: str
    checkpoint_id: str
    patch_proposal: dict[str, str]
    oracle_passed: bool = False
    score: float = 0.0
    ast_valid: bool = True
    error_msg: str = ""


class SpeculativeMCTSSearch:
    """Manages speculative multi-candidate patch search in isolated git checkpoints."""

    def __init__(self, workspace, branching_factor: int = 3, c_puct: float = 1.414):
        self.ws = workspace
        self.k = branching_factor
        self.c = c_puct

    def explore_candidates(
        self,
        sample_fn: Callable[[float], dict[str, str]],
        oracle_eval: Callable[[], bool],
    ) -> tuple[dict[str, str] | None, list[CandidateBranch]]:
        """Explore K candidate patch variations and return winning patch if found."""
        candidates: list[CandidateBranch] = []
        
        for i in range(self.k):
            chk_id = self.ws.git_checkpoint(f"mcts_branch_{i}")
            temp = 0.2 + (0.2 * i)
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
            if res.ok:
                try:
                    passed = oracle_eval()
                except Exception:
                    passed = False

            candidates.append(
                CandidateBranch(
                    branch_id=f"branch_{i}",
                    checkpoint_id=chk_id,
                    patch_proposal=proposal,
                    oracle_passed=passed,
                    score=1.0 if passed else 0.0,
                    ast_valid=res.ok,
                    error_msg=res.output if not res.ok else "",
                )
            )
            self.ws.git_rollback()

        # Check if any candidate passed oracle
        for cand in candidates:
            if cand.oracle_passed and cand.ast_valid:
                self.ws.patch_apply(
                    path=cand.patch_proposal["path"],
                    target_chunk=cand.patch_proposal["target_chunk"],
                    replacement_chunk=cand.patch_proposal["replacement_chunk"],
                )
                return cand.patch_proposal, candidates

        return None, candidates
