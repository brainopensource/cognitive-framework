"""Governed exterior skill lifecycle (M-8 preparation).

Generator, evaluator, and promoter are separate protocols.  Promotion is an
explicit signed operation and rollback restores the previous composition; an
agent has no method to promote itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

from ..domain.canonicalisation.digest import digest_of

__all__ = ["SkillCandidate", "EvaluationReport", "PromotionEvidence", "SkillGenerator", "SkillEvaluator", "SkillPromoter", "CompositionRegistry"]


@dataclass(frozen=True, slots=True)
class SkillCandidate:
    candidate_id: str
    source_trajectory_digest: str
    body_digest: str
    composition_version: str


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    candidate_id: str
    held_out_pass: bool
    affected_context_pass: bool
    adversarial_pass: bool
    grounded: bool
    verified: bool
    report_digest: str

    @property
    def promotable(self) -> bool:
        return all((self.held_out_pass, self.affected_context_pass, self.adversarial_pass,
                    self.grounded, self.verified))


@dataclass(frozen=True, slots=True)
class PromotionEvidence:
    candidate_id: str
    report_digest: str
    promoter_id: str
    signature: str
    previous_version: str
    promoted_version: str


class SkillGenerator(Protocol):
    def generate(self, trajectory_digest: str, failure_digests: Sequence[str]) -> SkillCandidate: ...


class SkillEvaluator(Protocol):
    def evaluate(self, candidate: SkillCandidate) -> EvaluationReport: ...


class SkillPromoter(Protocol):
    def promote(self, candidate: SkillCandidate, report: EvaluationReport, signature: str) -> PromotionEvidence: ...


class CompositionRegistry:
    def __init__(self, initial_version: str) -> None:
        if not initial_version: raise ValueError("initial composition version required")
        self._current = initial_version
        self._history: list[str] = [initial_version]

    @property
    def current(self) -> str: return self._current

    def _apply_verified(self, evidence: PromotionEvidence, report: EvaluationReport) -> str:
        """Apply evidence only after the concrete promoter verifies its signature."""
        if not report.promotable or evidence.report_digest != report.report_digest:
            raise ValueError("promotion evidence is not valid")
        if evidence.previous_version != self._current or not evidence.signature:
            raise ValueError("promotion authority or base version invalid")
        self._current = evidence.promoted_version
        self._history.append(self._current)
        return self._current

    def promote(self, evidence: PromotionEvidence, report: EvaluationReport) -> str:
        raise PermissionError(
            "unsigned registry promotion is forbidden; use promote_and_register")

    def rollback(self) -> str:
        if len(self._history) < 2: raise ValueError("no promoted composition to roll back")
        self._history.pop()
        self._current = self._history[-1]
        return self._current
