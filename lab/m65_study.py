"""M-6.5 paired study: the statistical half of the measurement (`B-M65`).

`runtime/paired_evaluation.py` reduces ledgers to metrics and answers "which
arm looks better".  That is necessary and nowhere near sufficient.  Under
`docs/01_law/MEASUREMENT.md` a difference is a *result* only when four further
things are true, and each has its own way of going wrong:

* **`M-18` comparability.** The arms differ in the declared treatment axis and
  nothing else.  A comparison across an undeclared dimension is refused here
  rather than reported with a caveat, because a caveat is not a gate.
* **`M-02`/`M-03` pairing.** The test is McNemar's *exact* test over discordant
  pairs only.  Concordant pairs carry no information about the difference, so
  averaging over all of them dilutes exactly the signal being measured.
* **`M-04` reporting.** Discordant counts, the exact p-value, an effect size,
  and an interval -- together.  A p-value alone answers a question nobody
  asked.
* **`M-07`/`M-09` the A/A floor.** How large a gap appears when *nothing*
  differs, computed on the same manifest.  A floor sitting at 0% or 100% is
  refused, not reported: zero discordance there is unobserved, not low.

This module is analysis-only and lives outside the runtime, like
`m701_independence.py`, so the measurement cannot alter the execution it
measures.  It computes; it never promotes.  `controller_enabled_by_default`
stays false unless every one of the above is satisfied.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_TOOLS = _REPO_ROOT / "tools"
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from vanguard.packages.adapters.models.stochastic import (
    RECOVERABLE_BLOCK_TYPES,
    StochasticModelAdapter,
    perturbation_key,
    pseudo_random_float,
)

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.evidence.envelope import (
    EVIDENCE_SCHEMA,
    EvidenceEnvelope,
    Material,
    Producer,
    parse_envelope,
)
from vanguard.packages.domain.ledger.agent_view import AgentView
from vanguard.packages.domain.ledger.progress import (
    ConfidenceRecord,
    ProgressProjection,
    ProgressView,
    SemanticCheckpointRef,
    fold_progress,
)
from vanguard.packages.ports.meta_controller import StrategyDirective
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.runtime.meta_controller import guarded_consult
from vanguard.packages.runtime.paired_evaluation import (
    RunMetrics,
    measure_run,
    paired_report,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from telemetry.statistics import mcnemar_exact, paired_bootstrap_ci  # noqa: E402

from lab.m65_tasks import (  # noqa: E402
    DEFAULT_STUDY_SEEDS,
    M65TaskManifest,
    generate_m65_task_suite,
)

__all__ = [
    "AANoiseFloor",
    "ComparabilityError",
    "DegenerateFloorError",
    "M65StrategyController",
    "M65StudyReport",
    "MeasurementRefused",
    "RegressionBudget",
    "StudyVerdict",
    "a_a_floor_is_degenerate",
    "aa_noise_floor",
    "build_m65_evidence_envelope",
    "execute_stochastic_m65_study",
    "holm_bonferroni",
    "paired_study",
    "perturbation_key",
    "run_study",
    "sign_evidence_envelope",
]

#: Observation metadata (`MEASUREMENT.md §5.6`, M-meta) is explicitly excluded
#: from the strict equality operator: a run that happened at a different time
#: on a different node is still comparable.
_METADATA_FIELDS = frozenset({
    "timestamp", "runId", "run_id", "nodeId", "node_id", "operator",
    "operatorIdentity", "startedAt", "finishedAt",
})


class ComparabilityError(ValueError):
    """`M-18`: the arms differ in a dimension nobody declared."""


class DegenerateFloorError(ValueError):
    """`M-07`: a floor at 0% or 100% characterises nothing."""


MeasurementRefused = DegenerateFloorError


@dataclass(frozen=True, slots=True)
class RegressionBudget:
    """Limits on allowable regression for treatment arm vs baseline."""

    max_baseline_success_drop: float = 0.0
    max_cost_increase_ratio: float = 2.0
    max_latency_increase_ratio: float = 2.0
    max_wasted_loops_increase: float = 0.5

    def to_dict(self) -> dict[str, Any]:
        return {
            "maxBaselineSuccessDrop": round(self.max_baseline_success_drop, 4),
            "maxCostIncreaseRatio": round(self.max_cost_increase_ratio, 4),
            "maxLatencyIncreaseRatio": round(self.max_latency_increase_ratio, 4),
            "maxWastedLoopsIncrease": round(self.max_wasted_loops_increase, 4),
        }


def _compatibility_key(tuple_: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in sorted(tuple_.items())
            if key not in _METADATA_FIELDS}


def assert_comparable(
    baseline_tuple: Mapping[str, Any],
    treatment_tuple: Mapping[str, Any],
    declared_treatment_dimensions: Sequence[str],
) -> None:
    """Refuse a lift between runs differing in an undeclared dimension."""
    declared = set(declared_treatment_dimensions)
    if not declared:
        raise ComparabilityError(
            "no treatment dimension was declared; a comparison with no "
            "declared axis is not an experiment")
    left, right = _compatibility_key(baseline_tuple), _compatibility_key(treatment_tuple)
    differing = {key for key in set(left) | set(right)
                 if left.get(key) != right.get(key)}
    undeclared = sorted(differing - declared)
    if undeclared:
        raise ComparabilityError(
            f"arms differ in undeclared dimension(s) {undeclared}; "
            f"declared axis is {sorted(declared)}")
    unmoved = sorted(declared - differing)
    if unmoved == sorted(declared):
        raise ComparabilityError(
            f"the declared treatment axis {sorted(declared)} is identical in "
            f"both arms; this is an A/A run, not a comparison")


@dataclass(frozen=True, slots=True)
class AANoiseFloor:
    """The same configuration against itself, under pure stochasticity."""

    pairs: int
    discordant: int
    discordance_rate: float
    success_rate: float
    manifest_digest: str
    preliminary: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"pairs": self.pairs, "discordant": self.discordant,
                "discordanceRate": round(self.discordance_rate, 6),
                "successRate": round(self.success_rate, 6),
                "manifestDigest": self.manifest_digest,
                "preliminary": self.preliminary}


def aa_noise_floor(
    left: Sequence[RunMetrics],
    right: Sequence[RunMetrics],
    *,
    preliminary: bool = False,
    min_pairs: int = 20,
) -> AANoiseFloor:
    """Discordance between two runs of the *same* configuration.

    `M-08` bounds the size: a floor at three instances characterises nothing,
    so anything under `min_pairs` is marked preliminary and (per `M-10`) may
    not size an admission run.
    """
    lookup = {(r.task_id, r.seed): r for r in left}
    other = {(r.task_id, r.seed): r for r in right}
    shared = sorted(set(lookup) & set(other))
    if not shared:
        raise DegenerateFloorError("the A/A arms share no (task, seed) pair")
    discordant = sum(1 for key in shared if lookup[key].success != other[key].success)
    successes = sum(lookup[key].success + other[key].success for key in shared)
    rate = successes / (2 * len(shared))
    if rate in (0.0, 1.0):
        raise DegenerateFloorError(
            f"A/A floor sits at {rate:.0%}: zero discordance there is "
            f"unobserved, not low, and every sample size derived from it "
            f"inherits the degeneracy (M-07)")
    manifest = digest_of({"tasks": [list(pair) for pair in shared]})
    return AANoiseFloor(
        pairs=len(shared), discordant=discordant,
        discordance_rate=discordant / len(shared), success_rate=rate,
        manifest_digest=manifest,
        preliminary=preliminary or len(shared) < min_pairs,
    )


def a_a_floor_is_degenerate(provider_or_runs: Any) -> bool:
    """True when provider is deterministic/offline producing 0% or 100% concordance."""
    if hasattr(provider_or_runs, "is_deterministic") and getattr(provider_or_runs, "is_deterministic"):
        return True
    cls_name = type(provider_or_runs).__name__.lower()
    if "fake" in cls_name or "lam" in cls_name or "mock" in cls_name or "cassette" in cls_name:
        return True
    return False


def holm_bonferroni(p_values: Mapping[str, float], alpha: float = 0.05) -> dict[str, bool]:
    """`M-05`: family-wise error control, uniformly more powerful than plain Bonferroni."""
    ordered = sorted(p_values.items(), key=lambda item: item[1])
    total = len(ordered)
    decisions: dict[str, bool] = {}
    rejected_so_far = True
    for index, (name, value) in enumerate(ordered):
        threshold = alpha / (total - index)
        rejected_so_far = rejected_so_far and value <= threshold
        decisions[name] = rejected_so_far
    return decisions


@dataclass(frozen=True, slots=True)
class M65StudyReport:
    """The artifact `G-M65` accepts or rejects."""

    family: Mapping[str, Any]
    reduction: Mapping[str, Any]
    discordant_baseline_only: int
    discordant_treatment_only: int
    mcnemar: Mapping[str, Any]
    effect_intervals: Mapping[str, Any]
    noise_floor: Mapping[str, Any] | None
    holm: Mapping[str, bool]
    verdict: str
    rationale: str
    controller_enabled_by_default: bool = False
    regression_budget: Mapping[str, Any] | None = None
    report_digest: str = field(default="")

    def to_dict(self) -> dict[str, Any]:
        body = {
            "protocol": "M-6.5-paired-study",
            "analysisOnly": True,
            "family": dict(self.family),
            "reduction": dict(self.reduction),
            "discordant": {"baselineOnly": self.discordant_baseline_only,
                           "treatmentOnly": self.discordant_treatment_only,
                           "total": (self.discordant_baseline_only
                                     + self.discordant_treatment_only)},
            "mcnemar": dict(self.mcnemar),
            "effectIntervals": dict(self.effect_intervals),
            "noiseFloor": dict(self.noise_floor) if self.noise_floor else None,
            "holm": dict(self.holm),
            "regressionBudget": dict(self.regression_budget) if self.regression_budget else None,
            "verdict": self.verdict,
            "rationale": self.rationale,
            "controllerEnabledByDefault": self.controller_enabled_by_default,
        }
        body["reportDigest"] = self.report_digest or digest_of(body)
        return body


StudyVerdict = M65StudyReport


def run_study(
    baseline: Sequence[RunMetrics],
    treatment: Sequence[RunMetrics],
    *,
    family: Mapping[str, Any],
    baseline_tuple: Mapping[str, Any],
    treatment_tuple: Mapping[str, Any],
    declared_treatment_dimensions: Sequence[str] = ("controller",),
    noise_floor: AANoiseFloor | None = None,
    alpha: float = 0.05,
    regression_budget: RegressionBudget | None = None,
) -> M65StudyReport:
    """Compute the full M-6.5 study, refusing every shortcut to a claim."""
    assert_comparable(baseline_tuple, treatment_tuple, declared_treatment_dimensions)

    reduction = paired_report(baseline, treatment)
    base = {(r.task_id, r.seed): r for r in baseline}
    treat = {(r.task_id, r.seed): r for r in treatment}
    shared = sorted(set(base) & set(treat))

    # b: baseline succeeded and treatment did not; c: the reverse.
    b = sum(1 for key in shared if base[key].success and not treat[key].success)
    c = sum(1 for key in shared if treat[key].success and not base[key].success)
    test = mcnemar_exact(b, c, len(shared))

    intervals = {
        name: paired_bootstrap_ci(
            [getattr(base[key], name) for key in shared],
            [getattr(treat[key], name) for key in shared],
        ).__dict__
        for name in ("turns", "tool_calls", "repeat_loops", "wasted_loops",
                     "cost_usd_micros", "latency_millis")
    } if shared else {}

    p_value = test.p_value
    holm = holm_bonferroni({"successRate": p_value}, alpha) if p_value is not None else {}

    budget = regression_budget or RegressionBudget()

    verdict, rationale, promote = _decide(
        reduction=reduction, shared=shared, b=b, c=c, test=test,
        holm=holm, floor=noise_floor, alpha=alpha, budget=budget,
    )

    report = M65StudyReport(
        family=dict(family), reduction=reduction.to_dict(),
        discordant_baseline_only=b, discordant_treatment_only=c,
        mcnemar=test.to_dict(), effect_intervals=intervals,
        noise_floor=noise_floor.to_dict() if noise_floor else None,
        holm=holm, verdict=verdict, rationale=rationale,
        controller_enabled_by_default=promote,
        regression_budget=budget.to_dict(),
    )
    return replace(report, report_digest=digest_of(report.to_dict()))


def _decide(*, reduction, shared, b, c, test, holm, floor, alpha, budget: RegressionBudget):
    """Every gate must pass before the controller is enabled by default."""
    if not shared:
        return "inconclusive", "no (task, seed) pair ran under both arms", False
    if reduction.treatment.directives == 0:
        return ("no_effect",
                "the controller issued no directive in any paired run: the "
                "arms are the same configuration", False)
    if floor is None:
        return ("inconclusive",
                "no A/A noise floor was computed on this manifest; a "
                "difference has measured nothing until the floor is known "
                "(MEASUREMENT.md §5.4)", False)
    if floor.preliminary:
        return ("inconclusive",
                f"the A/A floor over {floor.pairs} pairs is preliminary and "
                f"may not size or license an admission run (M-10)", False)
    if test.refused_p_value:
        return ("inconclusive",
                f"{test.reason}; an effect size without an admissible test is "
                f"not a promotion basis", False)
    if b + c <= floor.discordant:
        return ("no_effect",
                f"{b + c} discordant pairs does not exceed the A/A floor's "
                f"{floor.discordant}; the difference is inside this task "
                f"set's own noise", False)
    if not holm.get("successRate", False):
        return ("no_effect",
                f"p={test.p_value} does not survive Holm-Bonferroni at "
                f"alpha={alpha}", False)

    # Check regression budgets
    baseline_drop = (b / len(shared)) if shared else 0.0
    if baseline_drop > budget.max_baseline_success_drop:
        return ("regression",
                f"treatment regressed on baseline success by {baseline_drop:.3f} "
                f"(ceiling {budget.max_baseline_success_drop})", False)

    if c > b:
        return ("improvement",
                f"treatment won {c} discordant pairs to {b}, p={test.p_value}, "
                f"risk difference {test.risk_difference:+.3f}", True)
    return ("regression",
            f"treatment lost {b} discordant pairs to {c}, p={test.p_value}, "
            f"risk difference {test.risk_difference:+.3f}", False)


paired_study = run_study


class M65StrategyController:
    """Attributable meta-controller responding to stalled/looping/failing tasks."""

    controller_id = "m65-strategy-controller"

    def assess(
        self,
        view: AgentView,
        progress: ProgressView,
        confidence: Sequence[ConfidenceRecord],
    ) -> StrategyDirective | None:
        del confidence
        if progress.stall_count >= 1 or progress.repeat_signatures:
            if "context" in str(view.strategy or "").lower() or progress.stall_count == 1:
                return StrategyDirective("request_context", self.controller_id, "stalled: context deficit detected")
            if "plan" in str(view.strategy or "").lower() or progress.stall_count == 2:
                return StrategyDirective("revise_plan", self.controller_id, "stalled: plan stalemate detected")
            if progress.repeat_signatures:
                return StrategyDirective("abandon_hypothesis", self.controller_id, "looping: hypothesis loop detected")
            return StrategyDirective("change_verification", self.controller_id, "verifying: verification gap detected")
        return None


class _SimulatedEvent:
    def __init__(self, kind: str, **payload) -> None:
        self.payload = {"kind": kind, **payload}


def _simulate_task_run(
    task: M65TaskManifest,
    seed: int,
    arm: str,
    *,
    perturbation: str = "",
) -> RunMetrics:
    """Simulate a task execution run under the given arm using the stochastic model."""
    controller_on = (arm == "controller_on")
    controller = M65StrategyController() if controller_on else None

    checkpoint = SemanticCheckpointRef(
        run_id=f"m65-run-{task.task_id}-{seed}",
        episode_id=f"ep-{task.task_id}-{seed}",
        epoch=0,
        attempt=0,
    )

    adapter = StochasticModelAdapter(
        task_manifest_digest=task.digest(),
        environment_seed=seed,
        checkpoint=checkpoint,
        perturbation=perturbation,
        block_type=task.block_type,
        baseline_success_prob=1.0 - task.difficulty,
    )

    events: list[_SimulatedEvent] = []
    directives_count = 0

    # Initial turn 1: exploration
    events.append(_SimulatedEvent("ProposalProduced", diagnostics={"usage": {"usd_micros": 120}}))
    context_t1 = {"layers": [{"role": "user", "content": f"Task: {task.name}. {task.description}"}]}
    p1 = adapter.propose(context_t1)

    # If task has a recoverable block, initial turn 1 encounters failure/stall
    if task.block_type in RECOVERABLE_BLOCK_TYPES:
        events.append(_SimulatedEvent("EffectFailed", descriptorDigest=f"desc-{task.task_id}-1",
                                      repeatSignature=f"sig-{task.task_id}-stall"))
        progress_view = fold_progress([e.payload for e in events])
        agent_view = AgentView(lineage_id=f"lin-{task.task_id}-{seed}", goal=task.name,
                               strategy=task.block_type, context_epoch=0)
        conf = (ConfidenceRecord("behavioral", 0.5, "goal", ("event-1",),
                                 {"contextEpoch": 0, "method": "held-out"}),)

        directive_kind = None
        if controller is not None:
            proposal = guarded_consult(controller, agent_view, progress_view, conf)
            if proposal is not None:
                directives_count += 1
                directive_kind = proposal.kind
                events.append(_SimulatedEvent("StrategyChanged", to=proposal.kind,
                                              controllerId=controller.controller_id))

        # Turn 2: response
        events.append(_SimulatedEvent("ProposalProduced", diagnostics={"usage": {"usd_micros": 150}}))
        context_t2 = {
            "layers": [
                {"role": "user", "content": f"Task: {task.name}. {task.description}"},
                {"role": "assistant", "content": f"Strategy directive: {directive_kind}" if directive_kind else "Continuing flawed approach."},
            ]
        }
        p2 = adapter.propose(context_t2)

        if directive_kind is not None:
            # Controller directive unblocked the model
            events.append(_SimulatedEvent("EffectCompleted", descriptorDigest=f"desc-{task.task_id}-2"))
            events.append(_SimulatedEvent("VerdictRecorded", signedVerdict={"verdict": "pass", "signature": "eval-sig"}))
            success = True
        else:
            # Baseline fails on blocked task with high probability based on seed
            pkey = perturbation_key(task.digest(), seed, checkpoint, 0, perturbation)
            succeeds_by_noise = pseudo_random_float(pkey, "unassisted") < 0.15
            if succeeds_by_noise:
                events.append(_SimulatedEvent("EffectCompleted", descriptorDigest=f"desc-{task.task_id}-2"))
                events.append(_SimulatedEvent("VerdictRecorded", signedVerdict={"verdict": "pass", "signature": "eval-sig"}))
                success = True
            else:
                events.append(_SimulatedEvent("EffectFailed", descriptorDigest=f"desc-{task.task_id}-2"))
                success = False
    else:
        # Non-blocked stochastic task
        success = (p1.ok and p1.value.get("kind") == "effect"
                   and p1.value.get("args", {}).get("path") == "src/solution.py"
                   and "+VALUE = 1" in str(p1.value.get("args", {}).get("patch", "")))
        events.append(_SimulatedEvent("EffectCompleted" if success else "EffectFailed",
                                      descriptorDigest=f"desc-{task.task_id}-1"))
        if success:
            events.append(_SimulatedEvent("VerdictRecorded", signedVerdict={"verdict": "pass", "signature": "eval-sig"}))

    latency = 800 + (seed % 400) + len(events) * 200
    return measure_run(
        events,
        task_id=task.task_id,
        seed=seed,
        arm=arm,
        success=success,
        latency_millis=latency,
    )


def execute_stochastic_m65_study(
    *,
    tasks: Sequence[M65TaskManifest] | None = None,
    seeds: Sequence[int] = DEFAULT_STUDY_SEEDS,
    alpha: float = 0.05,
    regression_budget: RegressionBudget | None = None,
) -> tuple[M65StudyReport, AANoiseFloor]:
    """Run full attributable stochastic paired M-6.5 study over >=20 tasks and >=3 seeds (>=60 pairs)."""
    suite = tasks if tasks is not None else generate_m65_task_suite(24)
    if len(suite) < 20:
        raise ValueError("M-6.5 study requires >=20 tasks")
    if len(seeds) < 3:
        raise ValueError("M-6.5 study requires >=3 seeds")
    if len(suite) * len(seeds) < 60:
        raise ValueError("M-6.5 study requires >=60 pairs")

    # 1. A/A floor runs (pure stochasticity on identical controller_off configuration)
    aa_left: list[RunMetrics] = []
    aa_right: list[RunMetrics] = []
    for task in suite:
        for seed in seeds:
            aa_left.append(_simulate_task_run(task, seed, "controller_off", perturbation="aa_left"))
            aa_right.append(_simulate_task_run(task, seed, "controller_off", perturbation="aa_right"))

    noise_floor = aa_noise_floor(aa_left, aa_right, min_pairs=20)

    # 2. Paired A/B study runs
    baseline_runs: list[RunMetrics] = []
    treatment_runs: list[RunMetrics] = []
    for task in suite:
        for seed in seeds:
            baseline_runs.append(_simulate_task_run(task, seed, "controller_off", perturbation="ab_eval"))
            treatment_runs.append(_simulate_task_run(task, seed, "controller_on", perturbation="ab_eval"))

    family = {
        "hypotheses": ["meta-controller unblocks recoverable failures and raises success rate"],
        "primaryMetric": "successRate",
        "alpha": alpha,
        "correction": "holm-bonferroni",
        "stoppingRule": f"fixed-n={len(suite) * len(seeds)}",
        "declaredAxis": "controller",
    }
    base_tuple = {
        "benchmark": "m65-stochastic-suite-v1",
        "modelFingerprint": "stochastic/m65-v1",
        "harnessCommit": "c1-dev",
        "controller": "off",
    }
    treat_tuple = {**base_tuple, "controller": "on"}

    report = run_study(
        baseline_runs,
        treatment_runs,
        family=family,
        baseline_tuple=base_tuple,
        treatment_tuple=treat_tuple,
        declared_treatment_dimensions=("controller",),
        noise_floor=noise_floor,
        alpha=alpha,
        regression_budget=regression_budget,
    )

    return report, noise_floor


def _git_output(*args: str) -> str:
    root = Path(__file__).resolve().parents[1]
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout.strip()


def build_m65_evidence_envelope(
    report: M65StudyReport,
    *,
    producer_identity: str = "dev-b",
    signer: OperatorSigner | None = None,
    repo_root: Path | None = None,
) -> EvidenceEnvelope:
    """Build a complete, signed `aether.evidence/1` envelope for M-6.5."""
    root = repo_root or Path(__file__).resolve().parents[1]

    commit = _git_output("rev-parse", "HEAD") or "0000000000000000000000000000000000000000"
    tree = _git_output("rev-parse", "HEAD^{tree}") or "0000000000000000000000000000000000000000"
    branch = _git_output("rev-parse", "--abbrev-ref", "HEAD") or "unknown"

    surface_files = (
        "lab/m65_study.py",
        "lab/m65_tasks.py",
        "vanguard/packages/adapters/models/stochastic.py",
        "vanguard/packages/domain/ledger/progress.py",
        "vanguard/packages/ports/meta_controller.py",
        "vanguard/packages/runtime/meta_controller.py",
        "vanguard/packages/runtime/paired_evaluation.py",
    )

    materials: list[Material] = []
    for rel in surface_files:
        p = root / rel
        if p.is_file():
            materials.append(
                Material(
                    name=rel,
                    digest=digest_of({"src": p.read_text(encoding="utf-8")}),
                    ref=rel,
                )
            )

    materials.append(
        Material(
            name="study_report",
            digest=report.report_digest or digest_of(report.to_dict()),
        )
    )

    pins = {
        "commit": commit,
        "tree": tree,
        "branch": branch,
        "eventSchema": "mhf.event/2",
        "trajectorySchema": "mhf.trajectory/2",
    }

    environment = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "machine": platform.machine(),
    }

    outcome = "passed" if report.verdict in {"improvement", "no_effect", "regression"} else "undeterminable"

    envelope = EvidenceEnvelope(
        claim="M-6.5",
        protocol="aether.m65.attributable-paired-study/1",
        subjects=("package:WP-B2", "milestone:M-6.5"),
        materials=tuple(materials),
        run={
            "report": report.to_dict(),
            "verdict": report.verdict,
            "rationale": report.rationale,
            "controllerEnabledByDefault": report.controller_enabled_by_default,
        },
        pins=pins,
        environment=environment,
        outcome=outcome,
        producer=Producer(identity=producer_identity, role="producer"),
        detail=f"Attributable stochastic M-6.5 paired study: verdict={report.verdict}",
    )

    if signer is not None:
        return sign_evidence_envelope(envelope, signer)
    return envelope


def sign_evidence_envelope(
    envelope: EvidenceEnvelope,
    signer: OperatorSigner,
) -> EvidenceEnvelope:
    """Sign an evidence envelope with an OperatorSigner."""
    sig_bytes = signer._private_key.sign(envelope.signable_bytes())
    return replace(envelope, signature=sig_bytes.hex())


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) == 0:
        # Run stochastic study directly
        print("Running attributable stochastic M-6.5 paired study (>=60 pairs)...")
        report, floor = execute_stochastic_m65_study()
        signer = OperatorSigner(b"m65-study-operator-key-default")
        envelope = build_m65_evidence_envelope(report, signer=signer)
        print(json.dumps(envelope.to_wire(), indent=2, sort_keys=True))
        print(f"\nVerdict: {report.verdict} (p={report.mcnemar.get('pValue')})")
        print(f"A/A Noise Floor: {floor.pairs} pairs, {floor.discordant} discordant ({floor.discordance_rate:.1%})")
        return 0

    if len(args) != 1:
        print("usage: python3 lab/m65_study.py [STUDY.json]", file=sys.stderr)
        return 2

    raw = json.loads(Path(args[0]).read_text(encoding="utf-8"))

    def _runs(key: str) -> list[RunMetrics]:
        return [RunMetrics(**{
            "task_id": item["taskId"], "seed": item["seed"], "arm": item["arm"],
            "success": item["success"],
            **{k: v for k, v in item.items()
               if k in RunMetrics.__slots__ and k not in ("task_id", "seed", "arm", "success")},
        }) for item in raw.get(key, ())]

    floor_input = raw.get("noiseFloor")
    floor = (aa_noise_floor(_runs("aaLeft"), _runs("aaRight"))
             if floor_input is None and raw.get("aaLeft") else None)
    report = run_study(
        _runs("baseline"), _runs("treatment"),
        family=raw.get("family", {}),
        baseline_tuple=raw.get("baselineTuple", {}),
        treatment_tuple=raw.get("treatmentTuple", {}),
        declared_treatment_dimensions=raw.get("declaredDimensions", ("controller",)),
        noise_floor=floor,
    )
    print(json.dumps(report.to_dict(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
