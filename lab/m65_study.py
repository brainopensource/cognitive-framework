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
import sys
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.runtime.paired_evaluation import RunMetrics, paired_report

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from telemetry.statistics import mcnemar_exact, paired_bootstrap_ci  # noqa: E402

__all__ = [
    "ComparabilityError",
    "DegenerateFloorError",
    "AANoiseFloor",
    "M65StudyReport",
    "aa_noise_floor",
    "holm_bonferroni",
    "run_study",
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
            "verdict": self.verdict,
            "rationale": self.rationale,
            "controllerEnabledByDefault": self.controller_enabled_by_default,
        }
        body["reportDigest"] = self.report_digest or digest_of(body)
        return body


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
) -> M65StudyReport:
    """Compute the full M-6.5 study, refusing every shortcut to a claim.

    `family` is the pre-registered declaration (`M-06`): hypotheses, primary
    metrics, alpha, correction and stopping rule, hashed before any arm ran.
    It is carried into the report so a reader can check that the family was
    not chosen after seeing the data -- the one form of p-hacking that is
    undetectable after the fact.
    """
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

    verdict, rationale, promote = _decide(
        reduction=reduction, shared=shared, b=b, c=c, test=test,
        holm=holm, floor=noise_floor, alpha=alpha)

    report = M65StudyReport(
        family=dict(family), reduction=reduction.to_dict(),
        discordant_baseline_only=b, discordant_treatment_only=c,
        mcnemar=test.to_dict(), effect_intervals=intervals,
        noise_floor=noise_floor.to_dict() if noise_floor else None,
        holm=holm, verdict=verdict, rationale=rationale,
        controller_enabled_by_default=promote,
    )
    # The digest covers the report body, so it is computed from a report that
    # does not yet carry it -- a digest over itself would not be checkable.
    return replace(report, report_digest=digest_of(report.to_dict()))


def _decide(*, reduction, shared, b, c, test, holm, floor, alpha):
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
    if c > b:
        return ("improvement",
                f"treatment won {c} discordant pairs to {b}, p={test.p_value}, "
                f"risk difference {test.risk_difference:+.3f}", True)
    return ("regression",
            f"treatment lost {b} discordant pairs to {c}, p={test.p_value}, "
            f"risk difference {test.risk_difference:+.3f}", False)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage: python3 lab/m65_study.py STUDY.json", file=sys.stderr)
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
