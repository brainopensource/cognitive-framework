"""M-8 governed skill evaluation and promotion (`B-M8`).

`skill_lifecycle.py` declares the shape: generator, evaluator and promoter as
three protocols, and a registry that can roll back.  This module supplies the
concrete implementations and, more importantly, the *refusals* -- because the
failure mode M-8 is built against is not a bad skill, it is a good-looking one.

Three separations do the work:

**Generator ≠ Evaluator ≠ Promoter.**  An agent may propose a skill; it may not
declare it better.  So the generator holds no evaluation method, the evaluator
holds no signing key, and the promoter refuses a report it did not receive from
a distinct authority.  The check is on identity, not on politeness: a promoter
whose id matches the generator's is refused outright.

**Candidate ≠ promotion unit.**  `MEASUREMENT.md` is explicit that the unit of
promotion is the versioned composition containing the skill, never the skill in
isolation -- otherwise "this skill helps" is measured on one axis and shipped on
another.

**Present ≠ used ≠ grounded ≠ verified.**  A skill can be retrieved and never
invoked; invoked and ungrounded; grounded and unverified.  Each is a separate
recorded dimension, and `promotable` requires all of them, because collapsing
them is exactly how a presence-only effect becomes a reported lift.

The rollback path is executable, not documented: `rollback` restores the prior
composition and the caller recomputes `reproducibility_current`, since a
promotion changes what a later reader can reproduce.

No lifecycle event kind is introduced here. ADR-0100 has not been accepted, so
this module returns values; ledgering them is a decision, not an implementation
detail.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from ..domain.canonicalisation.digest import digest_of
from ..domain.canonicalisation.jcs import canonical_bytes
from .skill_lifecycle import (
    CompositionRegistry,
    EvaluationReport,
    PromotionEvidence,
    SkillCandidate,
)

__all__ = [
    "AuthoritySeparationError",
    "EvaluationWorkload",
    "HeldOutEvaluator",
    "PromotionRefused",
    "PromoterSigner",
    "SignedSkillPromoter",
    "SkillEvaluationDetail",
    "TrajectorySkillGenerator",
    "verify_promotion_evidence",
]

#: Held-out lift below this is not a result: it is inside the range a fixed
#: task set moves under ordinary stochasticity. Callers may raise it; the
#: promoter never lowers it.
DEFAULT_MIN_HELD_OUT_LIFT = 0.05
#: `MEASUREMENT.md` risk-based regression budget: how much previously-passing
#: behaviour a promotion may break. Zero would refuse every real change; this
#: is deliberately small and deliberately not zero.
DEFAULT_REGRESSION_BUDGET = 0.02


class AuthoritySeparationError(PermissionError):
    """A single authority tried to occupy two of the three lifecycle roles."""


class PromotionRefused(ValueError):
    """The candidate did not survive evaluation, or its evidence does not bind."""


# --------------------------------------------------------------------------
# Generator -- proposes, and can do nothing else
# --------------------------------------------------------------------------


class TrajectorySkillGenerator:
    """Derives candidates from analysed trajectories.

    Deliberately anaemic. It has no `evaluate` and no `promote`, and it holds
    no key: the separation is structural, so an agent driving this object
    cannot reach a promotion path even by mistake.
    """

    def __init__(self, generator_id: str) -> None:
        if not generator_id:
            raise ValueError("generator id is required")
        self.generator_id = generator_id

    def generate(
        self,
        trajectory_digest: str,
        failure_digests: Sequence[str] = (),
        *,
        composition_version: str,
    ) -> SkillCandidate:
        if not trajectory_digest or not composition_version:
            raise ValueError("a candidate must name its source trajectory and composition")
        body = digest_of({"generator": self.generator_id,
                          "trajectory": trajectory_digest,
                          "failures": sorted(str(item) for item in failure_digests)})
        return SkillCandidate(
            candidate_id=f"cand-{body[7:19]}",
            source_trajectory_digest=trajectory_digest,
            body_digest=body,
            composition_version=composition_version,
        )


# --------------------------------------------------------------------------
# Evaluator -- decides, and cannot sign
# --------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EvaluationWorkload:
    """A fixed task set split into what may be optimised against and what may not.

    `MEASUREMENT.md §5.7`: contamination is one-directional. A held-out task
    that appears in `dev` is refused at construction rather than quietly
    scored, because a sealed set used for iteration is a development set
    forever and no later care undoes it.
    """

    dev: tuple[str, ...]
    held_out: tuple[str, ...]
    adversarial: tuple[str, ...] = ()
    transfer: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.held_out:
            raise ValueError("a held-out split is required")
        splits = {
            "dev": self.dev,
            "held-out": self.held_out,
            "adversarial": self.adversarial,
            "transfer": self.transfer,
        }
        for name, tasks in splits.items():
            if any(not isinstance(task, str) or not task for task in tasks):
                raise ValueError(f"{name} task ids must be non-empty strings")
            if len(set(tasks)) != len(tasks):
                raise ValueError(f"{name} split contains duplicate task ids")
        names = tuple(splits)
        for index, left_name in enumerate(names):
            for right_name in names[index + 1:]:
                overlap = sorted(set(splits[left_name]) & set(splits[right_name]))
                if overlap:
                    raise ValueError(
                        f"tasks {overlap} are contaminated across {left_name} and "
                        f"{right_name} splits")

    def digest(self) -> str:
        return digest_of({"dev": sorted(self.dev), "heldOut": sorted(self.held_out),
                          "adversarial": sorted(self.adversarial),
                          "transfer": sorted(self.transfer)})


@dataclass(frozen=True, slots=True)
class SkillEvaluationDetail:
    """The decomposition `MEASUREMENT.md` requires of promotion evidence."""

    candidate_id: str
    workload_digest: str
    baseline_passes: int
    candidate_passes: int
    held_out_total: int
    gross_gains: tuple[str, ...]
    regressions: tuple[str, ...]
    residual_failures: tuple[str, ...]
    invoked_on: tuple[str, ...]
    grounded_on: tuple[str, ...]
    verified_on: tuple[str, ...]
    adversarial_present_only: tuple[str, ...]
    transfer_passes: int
    regression_budget: float
    min_held_out_lift: float

    @property
    def held_out_lift(self) -> float:
        total = self.held_out_total or 1
        return (self.candidate_passes - self.baseline_passes) / total

    @property
    def regression_rate(self) -> float:
        return len(self.regressions) / (self.held_out_total or 1)

    @property
    def presence_only(self) -> bool:
        """One or more reported gains lack an invocation of the candidate.

        The classic false positive: the skill was in context, the score moved,
        and the two facts are unrelated.
        """
        return bool(set(self.gross_gains) - set(self.invoked_on))

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidateId": self.candidate_id,
            "workloadDigest": self.workload_digest,
            "baselinePasses": self.baseline_passes,
            "candidatePasses": self.candidate_passes,
            "heldOutTotal": self.held_out_total,
            "heldOutLift": round(self.held_out_lift, 6),
            "grossGains": list(self.gross_gains),
            "regressions": list(self.regressions),
            "regressionRate": round(self.regression_rate, 6),
            "residualFailures": list(self.residual_failures),
            "invokedOn": list(self.invoked_on),
            "groundedOn": list(self.grounded_on),
            "verifiedOn": list(self.verified_on),
            "adversarialPresentOnly": list(self.adversarial_present_only),
            "transferPasses": self.transfer_passes,
            "presenceOnly": self.presence_only,
            "regressionBudget": self.regression_budget,
            "minHeldOutLift": self.min_held_out_lift,
        }

    def digest(self) -> str:
        return digest_of(self.to_dict())


#: `run(task_id, composition_version)` -> per-task observation.
#: `passed` is the outcome; `invoked`/`grounded`/`verified` are the separate
#: dimensions that keep a presence-only effect from reading as a lift.
TaskOutcome = Mapping[str, bool]
TaskRunner = Callable[[str, str], TaskOutcome]


def _observation(value: Any, task: str, version: str) -> TaskOutcome:
    if not isinstance(value, Mapping):
        raise TypeError(f"runner observation for {task!r}/{version!r} must be an object")
    allowed = frozenset({"passed", "invoked", "grounded", "verified"})
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"runner observation has unknown fields: {unknown}")
    if not isinstance(value.get("passed"), bool):
        raise TypeError(f"runner observation for {task!r}/{version!r} needs boolean passed")
    for field in ("invoked", "grounded", "verified"):
        if field in value and not isinstance(value[field], bool):
            raise TypeError(f"runner observation field {field!r} must be boolean")
    return value


class HeldOutEvaluator:
    """Scores a candidate on a held-out split it never optimised against.

    Holds no signing key by construction: `promote` does not exist here, so
    an evaluator cannot promote even if a caller asks it to.
    """

    def __init__(
        self,
        evaluator_id: str,
        workload: EvaluationWorkload,
        runner: TaskRunner,
        *,
        min_held_out_lift: float = DEFAULT_MIN_HELD_OUT_LIFT,
        regression_budget: float = DEFAULT_REGRESSION_BUDGET,
    ) -> None:
        if not evaluator_id:
            raise ValueError("evaluator id is required")
        if not 0.0 < min_held_out_lift <= 1.0:
            raise ValueError("minimum held-out lift must be in (0, 1]")
        if not 0.0 <= regression_budget <= 1.0:
            raise ValueError("regression budget must be in [0, 1]")
        self.evaluator_id = evaluator_id
        self._workload = workload
        self._runner = runner
        self._min_lift = min_held_out_lift
        self._budget = regression_budget

    def evaluate(
        self,
        candidate: SkillCandidate,
        *,
        baseline_version: str,
        candidate_version: str,
    ) -> tuple[EvaluationReport, SkillEvaluationDetail]:
        if baseline_version == candidate_version:
            raise ValueError("baseline and candidate compositions must differ")
        if candidate.composition_version != baseline_version:
            raise ValueError("candidate was not generated from the evaluated baseline")

        gains: list[str] = []
        regressions: list[str] = []
        residual: list[str] = []
        invoked: list[str] = []
        grounded: list[str] = []
        verified: list[str] = []
        baseline_passes = candidate_passes = 0

        for task in sorted(self._workload.held_out):
            before_obs = _observation(self._runner(task, baseline_version), task, baseline_version)
            after_obs = _observation(self._runner(task, candidate_version), task, candidate_version)
            before = before_obs["passed"]
            after = after_obs["passed"]
            baseline_passes += int(before)
            candidate_passes += int(after)
            if after and not before:
                gains.append(task)
            elif before and not after:
                regressions.append(task)
            elif not after:
                residual.append(task)
            if after_obs.get("invoked"):
                invoked.append(task)
            if after_obs.get("grounded"):
                grounded.append(task)
            if after_obs.get("verified"):
                verified.append(task)

        # Adversarial tasks are checked for *presence only*: the candidate may
        # be retrieved, but a task it was never supposed to affect must not
        # start passing because of it.
        present_only = [
            task for task in sorted(self._workload.adversarial)
            if _observation(
                self._runner(task, candidate_version), task, candidate_version
            ).get("invoked")
        ]
        transfer_passes = sum(
            1 for task in sorted(self._workload.transfer)
            if _observation(
                self._runner(task, candidate_version), task, candidate_version
            ).get("passed"))

        detail = SkillEvaluationDetail(
            candidate_id=candidate.candidate_id,
            workload_digest=self._workload.digest(),
            baseline_passes=baseline_passes, candidate_passes=candidate_passes,
            held_out_total=len(self._workload.held_out),
            gross_gains=tuple(gains), regressions=tuple(regressions),
            residual_failures=tuple(residual), invoked_on=tuple(invoked),
            grounded_on=tuple(grounded), verified_on=tuple(verified),
            adversarial_present_only=tuple(present_only),
            transfer_passes=transfer_passes,
            regression_budget=self._budget, min_held_out_lift=self._min_lift,
        )

        report = EvaluationReport(
            candidate_id=candidate.candidate_id,
            held_out_pass=detail.held_out_lift >= self._min_lift,
            affected_context_pass=detail.regression_rate <= self._budget,
            adversarial_pass=not present_only and not detail.presence_only,
            grounded=bool(gains) and set(gains) <= set(grounded),
            verified=bool(gains) and set(gains) <= set(verified),
            report_digest=detail.digest(),
        )
        return report, detail


# --------------------------------------------------------------------------
# Promoter -- signs, and cannot evaluate
# --------------------------------------------------------------------------


class PromoterSigner:
    """Promotion authority's Ed25519 key. Distinct from the evaluator's."""

    def __init__(self, private_key: bytes, key_id: str) -> None:
        if not isinstance(private_key, bytes) or len(private_key) != 32:
            raise ValueError("promoter private key must be 32 raw bytes")
        if not key_id:
            raise ValueError("promoter key id is required")
        self._key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key)
        self.key_id = key_id

    @property
    def public_bytes(self) -> bytes:
        return self._key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    def sign(self, body: Mapping[str, Any]) -> str:
        return base64.b64encode(self._key.sign(canonical_bytes(dict(body)))).decode("ascii")


def promotion_body(
    candidate: SkillCandidate,
    report: EvaluationReport,
    detail: SkillEvaluationDetail,
    *,
    promoter_id: str,
    previous_version: str,
    promoted_version: str,
) -> dict[str, Any]:
    """The bytes a promotion signature covers.

    Everything that could be swapped after the fact is inside: the candidate,
    the report digest, the workload it was scored on, and both composition
    versions. A signature over less than this would authenticate a decision
    without binding what the decision was about.
    """
    return {
        "candidateId": candidate.candidate_id,
        "bodyDigest": candidate.body_digest,
        "sourceTrajectoryDigest": candidate.source_trajectory_digest,
        "reportDigest": report.report_digest,
        "workloadDigest": detail.workload_digest,
        "heldOutLift": round(detail.held_out_lift, 6),
        "promoterId": promoter_id,
        "previousVersion": previous_version,
        "promotedVersion": promoted_version,
    }


def verify_promotion_evidence(
    evidence: PromotionEvidence,
    candidate: SkillCandidate,
    report: EvaluationReport,
    detail: SkillEvaluationDetail,
    public_key: bytes,
) -> bool:
    """Re-check a promotion signature without holding the promoter's key."""
    if (
        evidence.candidate_id != candidate.candidate_id
        or evidence.report_digest != report.report_digest
        or report.candidate_id != candidate.candidate_id
        or detail.candidate_id != candidate.candidate_id
        or report.report_digest != detail.digest()
        or candidate.composition_version != evidence.previous_version
    ):
        return False
    body = promotion_body(candidate, report, detail,
                          promoter_id=evidence.promoter_id,
                          previous_version=evidence.previous_version,
                          promoted_version=evidence.promoted_version)
    try:
        key = ed25519.Ed25519PublicKey.from_public_bytes(public_key)
        key.verify(base64.b64decode(evidence.signature, validate=True), canonical_bytes(body))
        return True
    except Exception:
        return False


@dataclass(frozen=True, slots=True)
class SignedSkillPromoter:
    """Promotes a *composition*, on someone else's evidence, under its own key."""

    promoter_id: str
    signer: PromoterSigner
    generator_id: str
    evaluator_id: str
    _: Any = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if not self.promoter_id:
            raise ValueError("promoter id is required")
        if self.promoter_id in {self.generator_id, self.evaluator_id}:
            raise AuthoritySeparationError(
                f"{self.promoter_id!r} is also the generator or evaluator; a "
                f"candidate may propose evidence but may not self-promote")
        if self.generator_id == self.evaluator_id:
            raise AuthoritySeparationError(
                "generator and evaluator must be distinct authorities")

    def promote(
        self,
        candidate: SkillCandidate,
        report: EvaluationReport,
        detail: SkillEvaluationDetail,
        *,
        previous_version: str,
        promoted_version: str,
    ) -> PromotionEvidence:
        if report.candidate_id != candidate.candidate_id:
            raise PromotionRefused("the report does not describe this candidate")
        if detail.candidate_id != candidate.candidate_id:
            raise PromotionRefused("the detail does not describe this candidate")
        if report.report_digest != detail.digest():
            raise PromotionRefused(
                "the report digest does not match its own decomposition; the "
                "evidence and the summary disagree")
        if not report.promotable:
            raise PromotionRefused(
                "candidate failed held-out, regression, adversarial, grounding "
                "or verification evaluation")
        if previous_version == promoted_version:
            raise PromotionRefused("a promotion must change the composition version")
        if candidate.composition_version != previous_version:
            raise PromotionRefused("candidate was generated from another composition version")
        body = promotion_body(candidate, report, detail, promoter_id=self.promoter_id,
                              previous_version=previous_version,
                              promoted_version=promoted_version)
        return PromotionEvidence(
            candidate_id=candidate.candidate_id,
            report_digest=report.report_digest,
            promoter_id=self.promoter_id,
            signature=self.signer.sign(body),
            previous_version=previous_version,
            promoted_version=promoted_version,
        )


def promote_and_register(
    registry: CompositionRegistry,
    evidence: PromotionEvidence,
    report: EvaluationReport,
    candidate: SkillCandidate,
    detail: SkillEvaluationDetail,
    public_key: bytes,
) -> str:
    """Verify signed evidence, then apply it with rollback still available."""
    if not verify_promotion_evidence(
        evidence, candidate, report, detail, public_key
    ):
        raise PromotionRefused("promotion signature or evidence binding is invalid")
    return registry._apply_verified(evidence, report)
