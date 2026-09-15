"""T-26 frozen-control preregistration. UNFROZEN until the first paid L2 call.

RUN-02: a publishable control report passes exactly one admission boundary that
takes the frozen manifest. ``require_frozen`` is that boundary; a caller-supplied
``frozen=True`` is not a substitute for it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

__all__ = [
    "CONTROL_ARM",
    "ControlAdmissionError",
    "ControlManifestError",
    "ControlNotFrozen",
    "load_preregistration",
    "require_frozen",
]

ROOT = Path(__file__).resolve().parent
CONTROL_PATH = ROOT / "control_preregistration.json"

SCHEMA = "aether.control-preregistration/1"

CONTROL_ARM = {
    "harness": "vg-code-balanced",
    "preset": "balanced",
    "workers": 1,
    "product_path": "vanguard.packages.runtime.entrypoint.execute",
}

#: Configuration identity the arm must pin beyond the four control-arm fields.
ARM_IDENTITY_DIGESTS = (
    "manifest_digest", "sampling_digest", "prompt_digest", "tool_schema_digest",
)

#: RUN-03: no unspecified resource is unlimited.
RESOURCE_CEILINGS = (
    "max_attempts", "max_provider_calls", "max_inference_cost_usd_micros",
    "max_evaluation_cost_usd_micros", "max_wall_time_s",
)

_SHA_RE = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
_DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

_MIN_N = 30
_MIN_WILSON_LB = 0.40


class ControlAdmissionError(ValueError):
    """A control record the publication boundary refuses."""


class ControlNotFrozen(ControlAdmissionError):
    """L2 scoring attempted before T-26 froze the subject SHA."""


class ControlManifestError(ControlAdmissionError):
    """A frozen record whose bindings are incomplete, forged or inconsistent."""


def load_preregistration(path: Path | None = None) -> dict[str, Any]:
    target = path or CONTROL_PATH
    data = json.loads(target.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError("invalid control preregistration schema")
    return data


def _refuse(reason: str) -> None:
    raise ControlManifestError(f"T-26a: {reason}")


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _digest(value: Any) -> str | None:
    return value if isinstance(value, str) and _DIGEST_RE.match(value) else None


def _mapping(data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    payload = data.get(key)
    if not isinstance(payload, Mapping) or not payload:
        _refuse(f"{key} block is missing or empty")
    return payload  # type: ignore[return-value]


def _validate_arm(arm: Mapping[str, Any]) -> None:
    for field, expected in CONTROL_ARM.items():
        if arm.get(field) != expected:
            _refuse(
                f"arm.{field} is {arm.get(field)!r}; MS-CONTROL qualifies only "
                f"single-worker vg-code-balanced on the product path")
    if not _text(arm.get("provider")):
        _refuse("arm.provider must name the serving provider")
    for field in ARM_IDENTITY_DIGESTS:
        if not _digest(arm.get(field)):
            _refuse(f"arm.{field} must pin a sha256 configuration digest")


def _validate_sample(sample: Mapping[str, Any]) -> int:
    n_min = sample.get("n_min")
    if not isinstance(n_min, int) or n_min < _MIN_N:
        _refuse(f"sample.n_min must be an integer >= {_MIN_N}")
    bound = sample.get("wilson_lb_min")
    if not isinstance(bound, (int, float)) or float(bound) < _MIN_WILSON_LB:
        _refuse(f"sample.wilson_lb_min must not fall below {_MIN_WILSON_LB}")
    if not _text(sample.get("confidence")):
        _refuse("sample.confidence must name the interval")
    if sample.get("retries_increase_coverage") is not False:
        _refuse("retries never add coverage")
    if sample.get("attempts_per_task") != 1:
        _refuse("RUN-03 allows exactly one measured attempt per task")
    if sample.get("missing_outcomes_retain_slots") is not True:
        _refuse("failed and missing outcomes must retain their slots")
    if not _text(sample.get("stopping_rule")):
        _refuse("sample.stopping_rule must state the stop and missingness policy")
    return int(n_min)  # type: ignore[arg-type]


def _validate_suite(data: Mapping[str, Any], n_min: int) -> None:
    suite = _mapping(data, "suite")
    tasks = suite.get("tasks")
    if not isinstance(tasks, (list, tuple)) or not tasks:
        _refuse("suite.tasks must list the frozen membership")
    if any(not _text(task) for task in tasks):  # type: ignore[union-attr]
        _refuse("suite.tasks contains a malformed task identifier")
    if len(set(tasks)) != len(tasks):  # type: ignore[arg-type]
        _refuse("suite.tasks contains duplicate task identifiers")
    if len(tasks) != n_min:  # type: ignore[arg-type]
        _refuse(f"suite.tasks holds {len(tasks)} tasks; the frozen sample is {n_min}")  # type: ignore[arg-type]
    for key in ("task_digests", "oracle_digests"):
        digests = suite.get(key)
        if not isinstance(digests, Mapping):
            _refuse(f"suite.{key} must bind every frozen task")
        for task in tasks:  # type: ignore[union-attr]
            if not _digest(digests.get(task)):  # type: ignore[union-attr]
                _refuse(f"suite.{key} is missing or malformed for {task!r}")
    from benchmarks.ladder.evidence import suite_digest

    expected = suite_digest(list(tasks))  # type: ignore[arg-type]
    if data.get("suite_digest") != expected:
        _refuse("suite_digest does not bind the frozen membership")


def _validate_resources(data: Mapping[str, Any], n_min: int) -> None:
    resources = _mapping(data, "resources")
    for ceiling in RESOURCE_CEILINGS:
        value = resources.get(ceiling)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            _refuse(f"resources.{ceiling} must be an explicit non-negative ceiling")
    if int(resources["max_attempts"]) < n_min:
        _refuse("resources.max_attempts cannot cover fewer slots than the frozen sample")


def require_frozen(record: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Admit a control record for scoring, or refuse with a typed signal.

    ``record=None`` reads the checked-in freeze contract. An explicitly supplied
    empty mapping never falls back to that ambient file.
    """
    if record is None:
        data = dict(load_preregistration())
    elif isinstance(record, Mapping):
        data = dict(record)
    else:
        raise ControlManifestError("T-26a: control record must be a mapping")

    if data.get("status") != "FROZEN" or not data.get("subject_sha"):
        raise ControlNotFrozen(
            "T-26: freeze subject_sha, suite_digest, and model_id before the first paid L2 call")

    if data.get("schema") != SCHEMA:
        _refuse(f"unknown preregistration schema {data.get('schema')!r}")
    if not _SHA_RE.match(str(data.get("subject_sha"))):
        _refuse("subject_sha must be a full lowercase commit digest")
    if not _text(data.get("model_id")):
        _refuse("model_id must pin the measured model")
    if not _text(data.get("frozen_at")):
        _refuse("frozen_at must record when the record was frozen")

    _validate_arm(_mapping(data, "arm"))
    n_min = _validate_sample(_mapping(data, "sample"))
    _validate_suite(data, n_min)
    _validate_resources(data, n_min)
    return data
