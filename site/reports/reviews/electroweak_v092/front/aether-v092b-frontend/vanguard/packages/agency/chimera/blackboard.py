"""Cognitive Blackboard and Belief Projections for CHIMERA.

Implements typed state projection, approximate Bayesian belief updating,
hypothesis management, ranked entities, and cognitive budget tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
import time
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from ...domain.canonicalisation.digest import digest_of
from ...domain.canonicalisation.jcs import canonicalise


class CognitiveDirectiveKind(str, Enum):
    ACT = "act"
    RETRIEVE = "retrieve"
    SOLVE = "solve"
    GENERATE = "generate"
    VERIFY = "verify"
    FORK = "fork"
    REPLAY = "replay"
    REFINE = "refine"
    COMPACT = "compact"
    ESCALATE = "escalate"
    FINISH = "finish"
    STOP = "stop"


@dataclass(frozen=True, slots=True)
class Fact:
    """Ground truth observation from deterministic environment or models."""

    fact_id: str
    kind: str
    statement: str
    source: str  # "direct_read", "test", "compiler", "git", "lda", "local_model", "frontier_model", "solver"
    confidence: float = 1.0
    freshness: float = field(default_factory=time.time)
    evidence_refs: tuple[str, ...] = ()
    repo_digest: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "factId": self.fact_id,
            "kind": self.kind,
            "statement": self.statement,
            "source": self.source,
            "confidence": self.confidence,
            "freshness": self.freshness,
            "evidenceRefs": list(self.evidence_refs),
            "repoDigest": self.repo_digest,
        }


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """Explicit hypothesis with prior/posterior Bayesian probability."""

    hypothesis_id: str
    statement: str
    status: str = "candidate"  # "candidate" | "active" | "supported" | "rejected" | "resolved"
    prior: float = 0.5
    posterior: float = 0.5
    supporting_evidence: tuple[str, ...] = ()
    contradicting_evidence: tuple[str, ...] = ()
    expected_information_gain: float = 0.5

    def update_evidence(self, support_weight: float = 0.0, contra_weight: float = 0.0, evidence_id: str = "") -> Hypothesis:
        # Approximate Bayesian logit update
        p = max(0.01, min(0.99, self.posterior))
        prior_logit = math.log(p / (1.0 - p))
        post_logit = prior_logit + (support_weight - contra_weight)
        new_post = 1.0 / (1.0 + math.exp(-max(-6.0, min(6.0, post_logit))))

        sup = list(self.supporting_evidence)
        con = list(self.contradicting_evidence)
        if support_weight > 0 and evidence_id and evidence_id not in sup:
            sup.append(evidence_id)
        if contra_weight > 0 and evidence_id and evidence_id not in con:
            con.append(evidence_id)

        status = self.status
        if new_post >= 0.85:
            status = "supported"
        elif new_post <= 0.15:
            status = "rejected"
        else:
            status = "active"

        return Hypothesis(
            hypothesis_id=self.hypothesis_id,
            statement=self.statement,
            status=status,
            prior=self.posterior,
            posterior=round(new_post, 4),
            supporting_evidence=tuple(sup),
            contradicting_evidence=tuple(con),
            expected_information_gain=round(abs(new_post - 0.5) * 2.0, 4),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "hypothesisId": self.hypothesis_id,
            "statement": self.statement,
            "status": self.status,
            "prior": self.prior,
            "posterior": self.posterior,
            "supportingEvidence": list(self.supporting_evidence),
            "contradictingEvidence": list(self.contradicting_evidence),
            "expectedInformationGain": self.expected_information_gain,
        }


@dataclass(frozen=True, slots=True)
class RankedFile:
    path: str
    relevance_score: float
    provider: str
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "relevanceScore": self.relevance_score,
            "provider": self.provider,
            "reason": self.reason,
        }


@dataclass(frozen=True, slots=True)
class RankedSymbol:
    symbol_name: str
    file_path: str
    relevance_score: float
    kind: str = "function"  # "function" | "class" | "method" | "type"

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbolName": self.symbol_name,
            "filePath": self.file_path,
            "relevanceScore": self.relevance_score,
            "kind": self.kind,
        }


@dataclass(frozen=True, slots=True)
class RankedTest:
    test_identifier: str
    file_path: str
    priority_score: float
    estimated_duration_s: float = 0.1

    def to_dict(self) -> dict[str, Any]:
        return {
            "testIdentifier": self.test_identifier,
            "filePath": self.file_path,
            "priorityScore": self.priority_score,
            "estimatedDurationS": self.estimated_duration_s,
        }


@dataclass(frozen=True, slots=True)
class PatchCandidate:
    candidate_id: str
    target_files: tuple[str, ...]
    diff_content: str
    risk_score: float
    verification_status: str = "untested"  # "untested" | "passed" | "failed" | "rolled_back"
    rationale: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "targetFiles": list(self.target_files),
            "diffContent": self.diff_content[:500],
            "riskScore": self.risk_score,
            "verificationStatus": self.verification_status,
            "rationale": self.rationale,
        }


@dataclass(frozen=True, slots=True)
class VerificationRecord:
    verification_id: str
    level: str  # "V0_SYNTAX" | "V1_TARGETED" | "V2_FULL_SUITE" | "V3_STATIC" | "V4_RUBRIC"
    exit_code: int
    executed_tests: int
    passed_tests: int
    failed_tests: tuple[str, ...]
    output_summary: str
    timestamp: float = field(default_factory=time.time)

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and len(self.failed_tests) == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "verificationId": self.verification_id,
            "level": self.level,
            "exitCode": self.exit_code,
            "executedTests": self.executed_tests,
            "passedTests": self.passed_tests,
            "failedTests": list(self.failed_tests),
            "outputSummary": self.output_summary[:400],
            "passed": self.passed,
            "timestamp": self.timestamp,
        }


@dataclass(frozen=True, slots=True)
class CognitiveBudget:
    max_turns: int = 15
    used_turns: int = 0
    token_ceiling: int = 64_000
    used_tokens: int = 0
    max_cost_usd: float = 0.20
    used_cost_usd: float = 0.0
    max_frontier_calls: int = 20
    used_frontier_calls: int = 0
    max_search_nodes: int = 10
    used_search_nodes: int = 0

    @property
    def available(self) -> bool:
        return (
            self.used_turns < self.max_turns
            and self.used_tokens < self.token_ceiling
            and self.used_cost_usd < self.max_cost_usd
        )

    def consume(
        self,
        turns: int = 0,
        tokens: int = 0,
        cost_usd: float = 0.0,
        frontier_calls: int = 0,
        search_nodes: int = 0,
    ) -> CognitiveBudget:
        return CognitiveBudget(
            max_turns=self.max_turns,
            used_turns=self.used_turns + turns,
            token_ceiling=self.token_ceiling,
            used_tokens=self.used_tokens + tokens,
            max_cost_usd=self.max_cost_usd,
            used_cost_usd=round(self.used_cost_usd + cost_usd, 6),
            max_frontier_calls=self.max_frontier_calls,
            used_frontier_calls=self.used_frontier_calls + frontier_calls,
            max_search_nodes=self.max_search_nodes,
            used_search_nodes=self.used_search_nodes + search_nodes,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "maxTurns": self.max_turns,
            "usedTurns": self.used_turns,
            "tokenCeiling": self.token_ceiling,
            "usedTokens": self.used_tokens,
            "maxCostUsd": self.max_cost_usd,
            "usedCostUsd": self.used_cost_usd,
            "maxFrontierCalls": self.max_frontier_calls,
            "usedFrontierCalls": self.used_frontier_calls,
            "maxSearchNodes": self.max_search_nodes,
            "usedSearchNodes": self.used_search_nodes,
            "available": self.available,
        }


@dataclass(frozen=True, slots=True)
class CalibratedConfidence:
    raw_model_confidence: float = 0.5
    historical_calibration_factor: float = 1.0
    evidence_grounding_score: float = 0.5
    verification_factor: float = 0.0

    @property
    def calibrated_score(self) -> float:
        score = (
            0.2 * self.raw_model_confidence * self.historical_calibration_factor
            + 0.3 * self.evidence_grounding_score
            + 0.5 * self.verification_factor
        )
        return round(max(0.0, min(1.0, score)), 3)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rawModelConfidence": self.raw_model_confidence,
            "historicalCalibrationFactor": self.historical_calibration_factor,
            "evidenceGroundingScore": self.evidence_grounding_score,
            "verificationFactor": self.verification_factor,
            "calibratedScore": self.calibrated_score,
        }


@dataclass(frozen=True, slots=True)
class UncertaintyProfile:
    localization_uncertainty: float = 0.8  # 1.0 = high, 0.0 = low
    patch_uncertainty: float = 0.8
    verification_uncertainty: float = 1.0
    entropy_score: float = 0.8

    @property
    def aggregate_uncertainty(self) -> float:
        return round(
            0.35 * self.localization_uncertainty
            + 0.35 * self.patch_uncertainty
            + 0.30 * self.verification_uncertainty,
            3,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "localizationUncertainty": self.localization_uncertainty,
            "patchUncertainty": self.patch_uncertainty,
            "verificationUncertainty": self.verification_uncertainty,
            "entropyScore": self.entropy_score,
            "aggregateUncertainty": self.aggregate_uncertainty,
        }


@dataclass(frozen=True, slots=True)
class TaskFeatures:
    language: str = "python"  # "python" | "javascript" | "typescript" | "rust" | "polyglot"
    kind: str = "bugfix"  # "bugfix" | "feature" | "greenfield" | "algorithmic" | "math_scientific"
    repo_file_count: int = 1
    issue_length: int = 100
    stacktrace_present: bool = False
    tests_present: bool = True
    multi_file: bool = False
    mathematical_invariants: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "language": self.language,
            "kind": self.kind,
            "repoFileCount": self.repo_file_count,
            "issueLength": self.issue_length,
            "stacktracePresent": self.stacktrace_present,
            "testsPresent": self.tests_present,
            "multiFile": self.multi_file,
            "mathematicalInvariants": self.mathematical_invariants,
        }


@dataclass(frozen=True, slots=True)
class TrajectorySummary:
    turn: int
    hypothesis_id: str
    action_type: str
    target_files: tuple[str, ...]
    exit_code: int | None
    progress_made: bool
    summary_text: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "turn": self.turn,
            "hypothesisId": self.hypothesis_id,
            "actionType": self.action_type,
            "targetFiles": list(self.target_files),
            "exitCode": self.exit_code,
            "progressMade": self.progress_made,
            "summaryText": self.summary_text,
        }


@dataclass(frozen=True, slots=True)
class CognitiveDirective:
    kind: CognitiveDirectiveKind
    objective: str
    route: str  # "RULE" | "LDA_AST" | "EMBEDDING" | "SYMBOLIC_SOLVER" | "CHEAP_LLM" | "FRONTIER_LLM" | "SEARCH"
    budget_slice: dict[str, Any] = field(default_factory=dict)
    rationale_code: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind.value,
            "objective": self.objective,
            "route": self.route,
            "budgetSlice": self.budget_slice,
            "rationaleCode": self.rationale_code,
        }


@dataclass(frozen=True, slots=True)
class CognitiveBlackboard:
    """Immutable Typed Cognitive Blackboard Projection for CHIMERA."""

    task_brief: str
    task_features: TaskFeatures
    facts: tuple[Fact, ...] = ()
    hypotheses: tuple[Hypothesis, ...] = ()
    candidate_files: tuple[RankedFile, ...] = ()
    candidate_symbols: tuple[RankedSymbol, ...] = ()
    candidate_tests: tuple[RankedTest, ...] = ()
    patches: tuple[PatchCandidate, ...] = ()
    verifications: tuple[VerificationRecord, ...] = ()
    budget: CognitiveBudget = field(default_factory=CognitiveBudget)
    confidence: CalibratedConfidence = field(default_factory=CalibratedConfidence)
    uncertainty: UncertaintyProfile = field(default_factory=UncertaintyProfile)
    trajectory_summaries: tuple[TrajectorySummary, ...] = ()
    phase: str = "EXPLORATION"  # "EXPLORATION" | "SCAFFOLDING" | "IMPLEMENTATION" | "VERIFICATION" | "REPAIR" | "REFINEMENT"

    @classmethod
    def from_task(
        cls,
        task_brief: str,
        features: TaskFeatures | None = None,
        budget: CognitiveBudget | None = None,
    ) -> CognitiveBlackboard:
        feat = features or TaskFeatures()
        bgt = budget or CognitiveBudget()
        initial_hypothesis = Hypothesis(
            hypothesis_id="h0_initial_understanding",
            statement=f"Initial task objective: {task_brief[:120]}...",
            status="candidate",
            prior=0.5,
            posterior=0.5,
        )
        return cls(
            task_brief=task_brief,
            task_features=feat,
            hypotheses=(initial_hypothesis,),
            budget=bgt,
            uncertainty=UncertaintyProfile(
                localization_uncertainty=0.9 if not feat.multi_file else 0.7,
                patch_uncertainty=0.9,
                verification_uncertainty=1.0,
            ),
        )

    def add_fact(self, fact: Fact) -> CognitiveBlackboard:
        existing = [f for f in self.facts if f.fact_id != fact.fact_id]
        existing.append(fact)
        return self._replace(facts=tuple(existing))

    def update_hypothesis(self, hypothesis: Hypothesis) -> CognitiveBlackboard:
        existing = [h for h in self.hypotheses if h.hypothesis_id != hypothesis.hypothesis_id]
        existing.append(hypothesis)
        return self._replace(hypotheses=tuple(existing))

    def update_candidates(
        self,
        files: Sequence[RankedFile] | None = None,
        symbols: Sequence[RankedSymbol] | None = None,
        tests: Sequence[RankedTest] | None = None,
    ) -> CognitiveBlackboard:
        new_files = tuple(files) if files is not None else self.candidate_files
        new_syms = tuple(symbols) if symbols is not None else self.candidate_symbols
        new_tests = tuple(tests) if tests is not None else self.candidate_tests

        # Update localization uncertainty
        loc_unc = 0.2 if len(new_files) in (1, 2, 3) else (0.5 if len(new_files) > 0 else 0.9)
        new_unc = UncertaintyProfile(
            localization_uncertainty=loc_unc,
            patch_uncertainty=self.uncertainty.patch_uncertainty,
            verification_uncertainty=self.uncertainty.verification_uncertainty,
            entropy_score=round((loc_unc + self.uncertainty.patch_uncertainty) / 2.0, 3),
        )

        return self._replace(
            candidate_files=new_files,
            candidate_symbols=new_syms,
            candidate_tests=new_tests,
            uncertainty=new_unc,
        )

    def record_verification(self, ver: VerificationRecord) -> CognitiveBlackboard:
        v_list = list(self.verifications)
        v_list.append(ver)

        ver_factor = 1.0 if ver.passed else 0.0
        ver_unc = 0.05 if ver.passed else 0.85

        new_conf = CalibratedConfidence(
            raw_model_confidence=self.confidence.raw_model_confidence,
            historical_calibration_factor=self.confidence.historical_calibration_factor,
            evidence_grounding_score=0.9 if ver.executed_tests > 0 else 0.4,
            verification_factor=ver_factor,
        )
        new_unc = UncertaintyProfile(
            localization_uncertainty=self.uncertainty.localization_uncertainty,
            patch_uncertainty=0.1 if ver.passed else 0.6,
            verification_uncertainty=ver_unc,
            entropy_score=0.1 if ver.passed else 0.5,
        )

        return self._replace(
            verifications=tuple(v_list),
            confidence=new_conf,
            uncertainty=new_unc,
            phase="VERIFICATION" if not ver.passed else "REFINEMENT",
        )

    def record_patch(self, patch: PatchCandidate) -> CognitiveBlackboard:
        p_list = list(self.patches)
        p_list.append(patch)
        return self._replace(patches=tuple(p_list), phase="VERIFICATION")

    def advance_phase(self, phase: str) -> CognitiveBlackboard:
        return self._replace(phase=phase)

    def consume_budget(self, **kwargs: Any) -> CognitiveBlackboard:
        return self._replace(budget=self.budget.consume(**kwargs))

    def _replace(self, **kwargs: Any) -> CognitiveBlackboard:
        data = {
            "task_brief": self.task_brief,
            "task_features": self.task_features,
            "facts": self.facts,
            "hypotheses": self.hypotheses,
            "candidate_files": self.candidate_files,
            "candidate_symbols": self.candidate_symbols,
            "candidate_tests": self.candidate_tests,
            "patches": self.patches,
            "verifications": self.verifications,
            "budget": self.budget,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "trajectory_summaries": self.trajectory_summaries,
            "phase": self.phase,
        }
        data.update(kwargs)
        return CognitiveBlackboard(**data)

    def digest(self) -> str:
        d = {
            "task_brief": self.task_brief[:100],
            "phase": self.phase,
            "facts_count": len(self.facts),
            "hypotheses_count": len(self.hypotheses),
            "files": [f.path for f in self.candidate_files],
            "verifications": [v.to_dict() for v in self.verifications[-3:]],
            "budget": self.budget.to_dict(),
        }
        return digest_of(d)

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskBrief": self.task_brief,
            "taskFeatures": self.task_features.to_dict(),
            "facts": [f.to_dict() for f in self.facts],
            "hypotheses": [h.to_dict() for h in self.hypotheses],
            "candidateFiles": [f.to_dict() for f in self.candidate_files],
            "candidateSymbols": [s.to_dict() for s in self.candidate_symbols],
            "candidateTests": [t.to_dict() for t in self.candidate_tests],
            "patches": [p.to_dict() for p in self.patches],
            "verifications": [v.to_dict() for v in self.verifications],
            "budget": self.budget.to_dict(),
            "confidence": self.confidence.to_dict(),
            "uncertainty": self.uncertainty.to_dict(),
            "phase": self.phase,
            "digest": self.digest(),
        }
