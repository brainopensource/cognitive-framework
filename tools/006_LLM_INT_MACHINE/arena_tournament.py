"""Multi-Agent Arena Tournament & Adversarial Jury Debate Engine (Grok Build Style).

Executes competitive side-by-side evaluation of candidate patches:
Proposers submit candidate solutions; an Adversarial Critic generates attack tests;
a Jury Evaluator ranks surviving patches by resilience and parsimony.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Sequence


@dataclass
class ArenaCandidate:
    candidate_id: str
    proposer_role: str  # 'minimal_diff', 'defensive_guard', 'architectural_refactor'
    patch_proposal: dict[str, str]
    oracle_passed: bool = False
    adversarial_attacks_survived: int = 0
    total_attacks_faced: int = 0
    ast_valid: bool = True
    jury_score: float = 0.0


@dataclass
class ArenaTournamentReport:
    winner_candidate_id: str | None
    winner_patch: dict[str, str] | None
    candidates_evaluated: list[ArenaCandidate] = field(default_factory=list)
    adversarial_tests_generated: int = 0
    consensus_confidence: float = 0.0


class ArenaTournament:
    """Orchestrates multi-candidate competitive tournaments with adversarial critic attacks."""

    def __init__(self, workspace):
        self.ws = workspace

    def run_tournament(
        self,
        candidate_proposals: Sequence[dict[str, Any]],
        oracle_evaluator: Callable[[], bool],
        adversarial_tests: Sequence[Callable[[], bool]] | None = None,
    ) -> ArenaTournamentReport:
        if not candidate_proposals:
            return ArenaTournamentReport(winner_candidate_id=None, winner_patch=None)

        candidates: list[ArenaCandidate] = []
        adv_tests = list(adversarial_tests or [])

        for idx, prop in enumerate(candidate_proposals):
            c_id = f"arena_cand_{idx+1}"
            role = prop.get("role", "general_proposer")
            patch = prop.get("patch", {})

            # 1. Apply patch in isolated git checkpoint
            chk_id = self.ws.git_checkpoint(f"arena_eval_{idx}")
            res = self.ws.patch_apply(
                path=patch.get("path", ""),
                target_chunk=patch.get("target_chunk", ""),
                replacement_chunk=patch.get("replacement_chunk", ""),
            )

            passed_oracle = False
            survived_attacks = 0

            if res.ok:
                try:
                    passed_oracle = oracle_evaluator()
                except Exception:
                    passed_oracle = False

                # 2. Run adversarial attacks
                for test in adv_tests:
                    try:
                        if test():
                            survived_attacks += 1
                    except Exception:
                        pass

            self.ws.git_rollback()

            # 3. Compute Jury Score:
            # 60% Oracle + 30% Adversarial resilience + 10% AST compactness
            diff_lines = len(patch.get("replacement_chunk", "").splitlines())
            compactness_bonus = max(0.0, 0.10 - (diff_lines * 0.005))
            adv_ratio = (survived_attacks / len(adv_tests)) if adv_tests else 1.0

            jury_score = 0.0
            if res.ok and passed_oracle:
                jury_score = 0.60 + (0.30 * adv_ratio) + compactness_bonus

            candidates.append(
                ArenaCandidate(
                    candidate_id=c_id,
                    proposer_role=role,
                    patch_proposal=patch,
                    oracle_passed=passed_oracle,
                    adversarial_attacks_survived=survived_attacks,
                    total_attacks_faced=len(adv_tests),
                    ast_valid=res.ok,
                    jury_score=round(jury_score, 4),
                )
            )

        # Rank candidates by jury score
        candidates.sort(key=lambda c: c.jury_score, reverse=True)
        winner = candidates[0] if candidates and candidates[0].oracle_passed else None

        if winner:
            # Apply winning patch to workspace
            self.ws.patch_apply(
                path=winner.patch_proposal.get("path", ""),
                target_chunk=winner.patch_proposal.get("target_chunk", ""),
                replacement_chunk=winner.patch_proposal.get("replacement_chunk", ""),
            )
            return ArenaTournamentReport(
                winner_candidate_id=winner.candidate_id,
                winner_patch=winner.patch_proposal,
                candidates_evaluated=candidates,
                adversarial_tests_generated=len(adv_tests),
                consensus_confidence=winner.jury_score,
            )

        return ArenaTournamentReport(
            winner_candidate_id=None,
            winner_patch=None,
            candidates_evaluated=candidates,
            adversarial_tests_generated=len(adv_tests),
            consensus_confidence=0.0,
        )
