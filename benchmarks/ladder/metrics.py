"""EXP-01 metric set. False-completion rate = 0 is a hard veto."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from benchmarks.ladder.control import ControlAdmissionError, require_frozen
from benchmarks.ladder.evidence import LIVE_LABELS, reconcile_population
from benchmarks.statistics import wilson_interval

__all__ = [
    "CANARY_DISPOSITIONS",
    "MetricVeto",
    "false_completion_rate",
    "live_oracle_pass",
    "publish_control_report",
    "score_metrics",
]

CANARY_DISPOSITIONS = frozenset({"POSITIVE", "NEGATIVE", "UNDETERMINABLE", "INVALID"})


class MetricVeto(ValueError):
    """A published capability claim that the metric set refuses."""


def false_completion(row: Mapping[str, Any]) -> bool:
    """Terminal completed without the evidence the completion gate requires."""
    settlement = row.get("settlement") or {}
    if str(settlement.get("terminal_status")) != "completed":
        return False
    change = row.get("change") or {}
    verification = row.get("verification") or {}
    if not change.get("patch_digest"):
        return True
    executed = verification.get("tests_executed")
    return executed in (None, 0)


def false_completion_rate(rows: Sequence[Mapping[str, Any]]) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if false_completion(row)) / len(rows)


def live_oracle_pass(rows: Sequence[Mapping[str, Any]]) -> tuple[int, int]:
    """Wilson denominator: current LIVE-* rows with a binary oracle, only."""
    passes = evaluated = 0
    for row in rows:
        label = str((row.get("execution") or {}).get("evidence_label") or "")
        if label not in LIVE_LABELS:
            continue
        disposition = str((row.get("settlement") or {}).get("disposition") or "")
        if disposition in {"undeterminable", "not_run"}:
            continue
        evaluated += 1
        if disposition == "passed":
            passes += 1
    return passes, evaluated


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def score_metrics(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Emit the §EW-9.4 metric set. False-completion vetoes every claim."""
    fc = false_completion_rate(rows)
    if fc > 0:
        raise MetricVeto(f"false-completion rate {fc} vetoes every capability claim")
    passes, evaluated = live_oracle_pass(rows)
    wilson = wilson_interval(passes, evaluated) if evaluated > 0 else None
    first_valid = sum(
        1 for row in rows
        if int((row.get("execution") or {}).get("valid_tool_calls") or 0) > 0
    )
    malformed = sum(int((row.get("execution") or {}).get("malformed_tool_calls") or 0) for row in rows)
    recovery = sum(int((row.get("execution") or {}).get("recovery_attempts") or 0) for row in rows)
    no_ops = sum(1 for row in rows if (row.get("change") or {}).get("no_op"))
    turns = [int((row.get("execution") or {}).get("turns") or 0) for row in rows]
    valid_calls = [int((row.get("execution") or {}).get("valid_tool_calls") or 0) for row in rows]
    waste = [
        max(0, turn - call) for turn, call in zip(turns, valid_calls)
    ]
    tokens = []
    for row in rows:
        economics = row.get("economics") or {}
        prompt = economics.get("prompt_tokens")
        completion = economics.get("completion_tokens")
        if isinstance(prompt, int) and isinstance(completion, int) and (prompt + completion) > 0:
            tokens.append((prompt + completion, int((row.get("execution") or {}).get("turns") or 0)))
    kappa = None
    if tokens:
        kappa = sum(t[0] for t in tokens) / max(1, sum(t[1] for t in tokens))
    first_action = [
        row["execution"]["time_to_first_valid_action_s"]
        for row in rows
        if isinstance((row.get("execution") or {}).get("time_to_first_valid_action_s"), (int, float))
    ]
    return {
        "false_completion_rate": fc,
        "n_rows": len(rows),
        "n_live_evaluated": evaluated,
        "n_live_passed": passes,
        "wilson": wilson,
        "valid_first_tool_call_rate": _rate(first_valid, len(rows)),
        "malformed_tool_calls": malformed,
        "recovery_attempts": recovery,
        "no_op_rate": _rate(no_ops, len(rows)),
        "mean_time_to_first_valid_action_s": (
            sum(first_action) / len(first_action) if first_action else None),
        "turn_waste_W": sum(waste) / len(waste) if waste else None,
        "token_efficiency_kappa": kappa,
    }


def canary_disposition(
    *,
    metrics: Mapping[str, Any] | None,
    n_evaluable: int,
    n_min: int = 30,
    wilson_lb_min: float = 0.40,
    record: Mapping[str, Any] | None,
) -> str:
    """T-27 closed vocabulary. Does not close MS-CONTROL by itself.

    ``record`` is the preregistration itself: the freeze is derived here through
    the admission boundary, never accepted as a caller-supplied flag.
    """
    if record is None:
        return "INVALID"
    try:
        require_frozen(record)
    except ControlAdmissionError:
        return "INVALID"
    if n_evaluable <= 0:
        return "UNDETERMINABLE"
    if metrics is None:
        return "UNDETERMINABLE"
    wilson = metrics.get("wilson")
    if n_evaluable < n_min or wilson is None:
        return "UNDETERMINABLE"
    if wilson[0] >= wilson_lb_min and metrics.get("false_completion_rate") == 0:
        return "POSITIVE"
    return "NEGATIVE"


def publish_control_report(
    *,
    record: Mapping[str, Any] | None,
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """The single admission boundary for a publishable control report (RUN-02).

    Refuses before scoring: an unfrozen or incompletely bound manifest
    (``ControlNotFrozen`` / ``ControlManifestError``), an evidence population
    that does not reconcile with that manifest (``EvidenceError``), and any
    observed false completion (``MetricVeto``). Pure fixture diagnostics stay
    available through :func:`score_metrics`, which reads no record and no file.
    """
    manifest = require_frozen(record)
    reconciliation = reconcile_population(rows, manifest)
    metrics = score_metrics(rows)
    sample = manifest["sample"]
    disposition = canary_disposition(
        metrics=metrics,
        n_evaluable=reconciliation["n_evaluable"],
        n_min=int(sample["n_min"]),
        wilson_lb_min=float(sample["wilson_lb_min"]),
        record=manifest,
    )
    return {
        "subject_sha": manifest["subject_sha"],
        "suite_digest": manifest["suite_digest"],
        "model_id": manifest["model_id"],
        "disposition": disposition,
        "metrics": metrics,
        **reconciliation,
    }
