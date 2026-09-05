"""M-6.5 paired-run evaluation (`B-M65`).

The M-6.5 question is not "does a meta-controller exist" but "does it help".
That is a measurement, and the measurement is the deliverable -- so this module
is built to make a *negative* result as easy to report as a positive one.

Three rules keep it honest:

* **Metrics come from the ledger, never from live objects** (`S9-A-04`). An
  in-memory counter measures the process that produced it; the ledger measures
  what durably happened, which is the only thing a second reader can check.
* **Identical arms must report `no_effect`.** A harness that finds improvement
  between two identical configurations is measuring its own noise, so that is
  the first thing the tests pin.
* **The verdict is bounded by what was paired.** Runs are paired by
  `(task_id, seed)`; an arm missing a pair cannot be compared, and the report
  says `inconclusive` rather than averaging over whatever it happens to have.

`ADR-0096` and `milestones.md` both bind the outcome: if benefit is not
established the controller remains **disabled by default** and the negative
result is recorded. That is a successful milestone, not a failed one.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence

__all__ = [
    "ArmSummary",
    "PairedReport",
    "RunMetrics",
    "measure_run",
    "paired_report",
    "assert_single_varied_dimension",
]

#: Effect-settling kinds. A tool call is counted where it *settled*, not where
#: it was proposed: a proposal the kernel refused cost the model a turn but did
#: no work, and conflating the two flatters whichever arm proposes more.
_SETTLED = frozenset({"EffectCompleted", "EffectFailed", "EffectReconciled"})
_REJECTED = frozenset({"EffectRejected", "AuthorizationDenied"})
_RECOVERY = frozenset({"RunRecovered", "EffectReconciled"})


@dataclass(frozen=True, slots=True)
class RunMetrics:
    """One run of one task under one arm, reduced from its ledger."""

    task_id: str
    seed: int
    arm: str  # "controller_off" | "controller_on"
    success: bool
    turns: int = 0
    tool_calls: int = 0
    rejected_calls: int = 0
    repeat_loops: int = 0
    cost_usd_micros: int = 0
    latency_millis: int = 0
    recoveries: int = 0
    directives: int = 0
    wasted_loops: int = 0
    signed_passes: int = 0
    signed_verdicts: int = 0

    @property
    def signed_pass_rate(self) -> float:
        """Passes among *signed* verdicts only.

        An unsigned verdict is not a fail -- it is an absence of evidence, and
        folding it into the denominator as a failure would penalise the arm
        whose evaluator was unreachable rather than the arm that did worse.
        A run with no signed verdict at all contributes nothing here, and the
        arm summary reports how many verdicts were actually signed so the
        reader can see how thin the base is.
        """
        return self.signed_passes / self.signed_verdicts if self.signed_verdicts else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "taskId": self.task_id, "seed": self.seed, "arm": self.arm,
            "success": self.success, "turns": self.turns,
            "toolCalls": self.tool_calls, "rejectedCalls": self.rejected_calls,
            "repeatLoops": self.repeat_loops,
            "wastedLoops": self.wasted_loops,
            "costUsdMicros": self.cost_usd_micros,
            "latencyMillis": self.latency_millis,
            "recoveries": self.recoveries, "directives": self.directives,
            "signedPasses": self.signed_passes,
            "signedVerdicts": self.signed_verdicts,
            "signedPassRate": round(self.signed_pass_rate, 6),
        }


def measure_run(
    events: Sequence[Any],
    *,
    task_id: str,
    seed: int,
    arm: str,
    success: bool,
    latency_millis: int = 0,
) -> RunMetrics:
    """Reduce one run's durable events into the M-6.5 metric vector."""
    turns = tool_calls = rejected = cost = recoveries = directives = 0
    signed_passes = signed_verdicts = wasted = 0
    descriptors: list[str] = []
    #: Whether the turn currently open has settled any effect yet. A turn that
    #: closes without one burned a model call and produced nothing durable --
    #: the "wasted loop" M-6.5 exists to reduce.
    turn_open = False
    turn_settled = False

    for event in events:
        payload = getattr(event, "payload", None) or {}
        kind = payload.get("kind")
        if kind == "ProposalProduced":
            if turn_open and not turn_settled:
                wasted += 1
            turn_open, turn_settled = True, False
            turns += 1
            diagnostics = payload.get("diagnostics")
            if isinstance(diagnostics, Mapping):
                usage = diagnostics.get("usage")
                source = usage if isinstance(usage, Mapping) else diagnostics
                micros = source.get("usd_micros")
                if isinstance(micros, int) and not isinstance(micros, bool):
                    cost += micros
        elif kind in _SETTLED:
            tool_calls += 1
            turn_settled = True
            descriptor = payload.get("descriptorDigest")
            if isinstance(descriptor, str):
                descriptors.append(descriptor)
        elif kind in _REJECTED:
            rejected += 1
        if kind == "VerdictRecorded":
            # Only the evaluator daemon's own signed body counts. A verdict
            # with no signature is not evidence of anything (`ADR-0076 §5`),
            # so it moves neither numerator nor denominator.
            body = payload.get("signedVerdict")
            if isinstance(body, Mapping) and body.get("signature"):
                signed_verdicts += 1
                signed_passes += int(body.get("verdict") == "pass")
        if kind in _RECOVERY:
            recoveries += 1
        if kind == "StrategyChanged" or payload.get("controllerId"):
            directives += 1

    return RunMetrics(
        task_id=task_id, seed=seed, arm=arm, success=success, turns=turns,
        tool_calls=tool_calls, rejected_calls=rejected,
        repeat_loops=_repeat_loops(descriptors), cost_usd_micros=cost,
        latency_millis=latency_millis, recoveries=recoveries,
        directives=directives,
        wasted_loops=wasted + int(turn_open and not turn_settled),
        signed_passes=signed_passes, signed_verdicts=signed_verdicts,
    )


def _repeat_loops(descriptors: Sequence[str]) -> int:
    """Settled effects that repeat a descriptor already settled in this run.

    The signal M-6.5 exists to move: an agent re-running the identical effect
    is looping rather than progressing. Counting *repeats* rather than
    *distinct repeated descriptors* keeps a run that loops ten times from
    scoring the same as one that loops twice.
    """
    seen: set[str] = set()
    repeats = 0
    for descriptor in descriptors:
        if descriptor in seen:
            repeats += 1
        else:
            seen.add(descriptor)
    return repeats


@dataclass(frozen=True, slots=True)
class ArmSummary:
    arm: str
    runs: int
    successes: int
    success_rate: float
    mean_turns: float
    mean_tool_calls: float
    mean_repeat_loops: float
    mean_cost_usd_micros: float
    mean_latency_millis: float
    recoveries: int
    directives: int
    mean_wasted_loops: float = 0.0
    signed_passes: int = 0
    signed_verdicts: int = 0

    @property
    def signed_pass_rate(self) -> float:
        return self.signed_passes / self.signed_verdicts if self.signed_verdicts else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm, "runs": self.runs, "successes": self.successes,
            "successRate": round(self.success_rate, 6),
            "meanTurns": round(self.mean_turns, 6),
            "meanToolCalls": round(self.mean_tool_calls, 6),
            "meanRepeatLoops": round(self.mean_repeat_loops, 6),
            "meanWastedLoops": round(self.mean_wasted_loops, 6),
            "meanCostUsdMicros": round(self.mean_cost_usd_micros, 6),
            "meanLatencyMillis": round(self.mean_latency_millis, 6),
            "recoveries": self.recoveries, "directives": self.directives,
            "signedPasses": self.signed_passes,
            "signedVerdicts": self.signed_verdicts,
            "signedPassRate": round(self.signed_pass_rate, 6),
        }


def _summarise(arm: str, runs: Sequence[RunMetrics]) -> ArmSummary:
    count = len(runs) or 1
    return ArmSummary(
        arm=arm,
        runs=len(runs),
        successes=sum(1 for run in runs if run.success),
        success_rate=sum(1 for run in runs if run.success) / count,
        mean_turns=sum(r.turns for r in runs) / count,
        mean_tool_calls=sum(r.tool_calls for r in runs) / count,
        mean_repeat_loops=sum(r.repeat_loops for r in runs) / count,
        mean_cost_usd_micros=sum(r.cost_usd_micros for r in runs) / count,
        mean_latency_millis=sum(r.latency_millis for r in runs) / count,
        recoveries=sum(r.recoveries for r in runs),
        directives=sum(r.directives for r in runs),
        mean_wasted_loops=sum(r.wasted_loops for r in runs) / count,
        signed_passes=sum(r.signed_passes for r in runs),
        signed_verdicts=sum(r.signed_verdicts for r in runs),
    )


@dataclass(frozen=True, slots=True)
class PairedReport:
    """The artifact `G-M65` accepts or rejects."""

    baseline: ArmSummary
    treatment: ArmSummary
    paired_tasks: tuple[tuple[str, int], ...]
    unpaired: tuple[tuple[str, int], ...]
    verdict: str  # "improvement" | "no_effect" | "regression" | "inconclusive"
    rationale: str
    deltas: Mapping[str, float] = field(default_factory=dict)

    @property
    def controller_enabled_by_default(self) -> bool:
        """`milestones.md`: only a demonstrated improvement enables it."""
        return self.verdict == "improvement"

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline": self.baseline.to_dict(),
            "treatment": self.treatment.to_dict(),
            "pairedTasks": [list(pair) for pair in self.paired_tasks],
            "unpaired": [list(pair) for pair in self.unpaired],
            "verdict": self.verdict,
            "rationale": self.rationale,
            "deltas": {k: round(v, 6) for k, v in self.deltas.items()},
            "controllerEnabledByDefault": self.controller_enabled_by_default,
        }


def assert_single_varied_dimension(
    control: Mapping[str, Any],
    treatment: Mapping[str, Any],
    dimension: str,
) -> None:
    """Refuse a paired comparison that varies more than one preregistered key."""
    keys = sorted(set(control) | set(treatment))
    changed = [key for key in keys if control.get(key) != treatment.get(key)]
    if changed != [dimension]:
        raise ValueError(
            f"comparison varies {changed}; preregistered dimension is {dimension!r}")


def paired_report(
    baseline: Iterable[RunMetrics],
    treatment: Iterable[RunMetrics],
    *,
    min_success_gain: float = 0.05,
) -> PairedReport:
    """Compare two arms over the `(task, seed)` pairs they actually share."""
    base = {(r.task_id, r.seed): r for r in baseline}
    treat = {(r.task_id, r.seed): r for r in treatment}
    shared = sorted(set(base) & set(treat))
    unpaired = sorted(set(base) ^ set(treat))

    base_runs = [base[key] for key in shared]
    treat_runs = [treat[key] for key in shared]
    base_summary = _summarise("controller_off", base_runs)
    treat_summary = _summarise("controller_on", treat_runs)

    deltas = {
        "successRate": treat_summary.success_rate - base_summary.success_rate,
        "meanTurns": treat_summary.mean_turns - base_summary.mean_turns,
        "meanToolCalls": treat_summary.mean_tool_calls - base_summary.mean_tool_calls,
        "meanRepeatLoops": treat_summary.mean_repeat_loops - base_summary.mean_repeat_loops,
        "meanWastedLoops": treat_summary.mean_wasted_loops - base_summary.mean_wasted_loops,
        "signedPassRate": treat_summary.signed_pass_rate - base_summary.signed_pass_rate,
        "meanCostUsdMicros": (treat_summary.mean_cost_usd_micros
                              - base_summary.mean_cost_usd_micros),
        "meanLatencyMillis": (treat_summary.mean_latency_millis
                              - base_summary.mean_latency_millis),
    }

    if not shared:
        verdict, rationale = "inconclusive", (
            "no (task, seed) pair ran under both arms; there is nothing to compare")
    elif treat_summary.directives == 0:
        # The decisive check. If no directive was ever issued, the treatment
        # arm *is* the baseline arm, and any difference between them is noise
        # that a report must not dress up as an effect.
        verdict, rationale = "no_effect", (
            "the controller issued no directive in any paired run: the arms are "
            "the same configuration, so no effect is attributable to it")
    elif deltas["successRate"] >= min_success_gain:
        verdict, rationale = "improvement", (
            f"success rate rose by {deltas['successRate']:.3f} over "
            f"{len(shared)} paired runs")
    elif deltas["successRate"] <= -min_success_gain:
        verdict, rationale = "regression", (
            f"success rate fell by {abs(deltas['successRate']):.3f} over "
            f"{len(shared)} paired runs")
    else:
        verdict, rationale = "no_effect", (
            f"success rate moved by {deltas['successRate']:.3f}, inside the "
            f"{min_success_gain} band deemed indistinguishable")

    return PairedReport(
        baseline=base_summary, treatment=treat_summary,
        paired_tasks=tuple(shared), unpaired=tuple(unpaired),
        verdict=verdict, rationale=rationale, deltas=deltas,
    )
