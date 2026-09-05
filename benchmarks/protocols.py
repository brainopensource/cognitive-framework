"""Normalized, offline benchmark protocol contracts.

These values describe benchmark inputs and receipts; they do not execute a
provider or evaluator.  A receipt is admissible only when its subject digest
matches the normalized task and submission identities supplied by the caller.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence

from vanguard.packages.runtime.root import TaskDisposition

SUPPORTED_PROTOCOLS = frozenset({"SWE-bench Verified", "SWE-Bench Pro", "DeepSWE v1.1"})

__all__ = ["BenchmarkTask", "BenchmarkSubmission", "BenchmarkReceipt",
           "SUPPORTED_PROTOCOLS", "PROTOCOL_SPECS", "ProtocolSpec",
           "EvaluatorAdapter", "normalize", "B20MembershipError",
           "B20Membership", "B20TaskRecord", "B20_MEMBERSHIP_SCHEMA",
           "B20_REPORT_SCHEMA", "RESULT_DISPOSITIONS", "DirtySubjectError",
           "task_set_digest", "is_rejected_b20_name",
           "enumerate_b20_membership", "write_b20_report",
           "classify_disposition", "require_clean_subject"]

B20_MEMBERSHIP_SCHEMA = "aether.b20.membership/1"
B20_REPORT_SCHEMA = "aether.b20.report/1"
RESULT_DISPOSITIONS = frozenset(item.value for item in TaskDisposition)
_UNDETERMINABLE_MARKERS = (
    "provider_error",
    "provider_unavailable",
    "harness_error",
    "instrument_error",
    "dataset_invalid",
    "budget_exhausted",
    "traceback",
)
_REJECTED_B20_NAMES = frozenset({
    "__pycache__",
    ".pytest_cache",
    ".vanguard",
    "tmp",
    "temp",
})


class EvaluatorAdapter(Protocol):
    """Port for an exterior evaluator; implementations stay outside contracts."""

    protocol_name: str

    def evaluate(self, submission: BenchmarkSubmission) -> str | None:
        """Return PASS/FAIL, or None when the exterior verdict is missing."""


@dataclass(frozen=True, slots=True)
class ProtocolSpec:
    """Metadata for a published protocol, with no evaluator implementation."""

    name: str
    version: str
    official: bool = True


PROTOCOL_SPECS = {
    "SWE-bench Verified": ProtocolSpec("SWE-bench Verified", "published"),
    "SWE-Bench Pro": ProtocolSpec("SWE-Bench Pro", "published"),
    "DeepSWE v1.1": ProtocolSpec("DeepSWE v1.1", "1.1"),
}


def normalize(value: Any) -> Any:
    """Return JSON-compatible normalized data with stable object ordering."""
    if isinstance(value, Mapping):
        return {str(k): normalize(value[k]) for k in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [normalize(item) for item in value]
    return value


def _digest(value: Any) -> str:
    raw = json.dumps(normalize(value), ensure_ascii=False, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class BenchmarkTask:
    task_id: str
    benchmark: str
    split: str
    problem: str = ""
    base_commit: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value for value in
                   (self.task_id, self.benchmark, self.split)):
            raise ValueError("task_id, benchmark, and split are required")
        if self.benchmark not in SUPPORTED_PROTOCOLS:
            raise ValueError(f"unsupported benchmark protocol: {self.benchmark}")

    def to_wire(self) -> dict[str, Any]:
        return normalize({"taskId": self.task_id, "benchmark": self.benchmark,
                          "split": self.split, "problem": self.problem,
                          "baseCommit": self.base_commit,
                          "metadata": self.metadata})

    @property
    def digest(self) -> str:
        return _digest(self.to_wire())


@dataclass(frozen=True, slots=True)
class BenchmarkSubmission:
    task_digest: str
    patch: str
    model: str
    harness: str
    attempt: int = 1

    def __post_init__(self) -> None:
        if not self.task_digest or not self.patch or not self.model or not self.harness:
            raise ValueError("submission requires task, patch, model, and harness identities")
        if self.attempt < 1:
            raise ValueError("submission attempt must be positive")

    def to_wire(self) -> dict[str, Any]:
        return normalize({"taskDigest": self.task_digest, "patch": self.patch,
                          "model": self.model, "harness": self.harness,
                          "attempt": self.attempt})

    @property
    def digest(self) -> str:
        return _digest(self.to_wire())


@dataclass(frozen=True, slots=True)
class BenchmarkReceipt:
    """Exact-subject result; empirical fields are null when not run."""

    benchmark: str
    task_digest: str
    submission_digest: str
    harness: str
    model: str
    evaluator: str
    outcome: str | None = None
    reason: str = ""
    subject_sha: str = ""
    usage: Mapping[str, int] | None = None
    split: str = ""
    patch_digest: str = ""

    def __post_init__(self) -> None:
        if not str(self.subject_sha or "").strip():
            raise ValueError("receipt refused: missing subject_sha")
        if _is_pass_outcome(self.outcome) and not str(self.patch_digest or "").strip():
            raise ValueError("receipt refused: PASS row missing patch digest")

    def to_wire(self) -> dict[str, Any]:
        return normalize({
            "schema": "aether.benchmark.receipt/1",
            "benchmark": self.benchmark,
            "taskDigest": self.task_digest,
            "submissionDigest": self.submission_digest,
            "harness": self.harness,
            "model": self.model,
            "evaluator": self.evaluator,
            "outcome": self.outcome,
            "reason": self.reason,
            "subjectSha": self.subject_sha,
            "usage": self.usage,
            "split": self.split,
            "patchDigest": self.patch_digest,
        })

    def validate_subject(self, task: BenchmarkTask,
                         submission: BenchmarkSubmission) -> None:
        if self.benchmark != task.benchmark or self.task_digest != task.digest:
            raise ValueError("receipt is bound to a foreign task")
        if self.split != task.split:
            raise ValueError("receipt is bound to a foreign split")
        if self.submission_digest != submission.digest:
            raise ValueError("receipt is bound to a foreign submission")
        if self.harness != submission.harness or self.model != submission.model:
            raise ValueError("receipt identity does not match submission")
        if self.outcome is None and not self.reason:
            raise ValueError("dry-run or missing empirical result requires a reason")
        if not str(self.subject_sha or "").strip():
            raise ValueError("receipt refused: missing subject_sha")


class B20MembershipError(ValueError):
    """B20 membership is invalid; the campaign must stop."""


@dataclass(frozen=True, slots=True)
class B20TaskRecord:
    task_id: str
    oracle: str
    kind: str = ""


@dataclass(frozen=True, slots=True)
class B20Membership:
    tasks: tuple[B20TaskRecord, ...]
    digest: str

    @property
    def task_ids(self) -> tuple[str, ...]:
        return tuple(record.task_id for record in self.tasks)


def is_rejected_b20_name(name: str) -> bool:
    """Return True when a directory or id cannot be a B20 task."""
    if not name or name.startswith(".") or name.startswith("__"):
        return True
    lowered = name.lower()
    return (
        lowered in _REJECTED_B20_NAMES
        or lowered.startswith("tmp")
        or lowered.endswith((".tmp", ".temp"))
    )


def task_set_digest(task_ids: Sequence[str]) -> str:
    """Return an order-independent digest of the admitted task ids."""
    return _digest(sorted(str(task_id) for task_id in task_ids))


def enumerate_b20_membership(suite_root: Path) -> B20Membership:
    """Admit B20 tasks from a schema-valid manifest only.

    Directory names are never sufficient. ``__pycache__``, hidden, and tmp
    entries are not tasks. Missing oracles, duplicate ids, and digest
    mismatch fail closed.
    """
    root = Path(suite_root)
    manifest_path = root / "membership.json"
    if not manifest_path.is_file():
        raise B20MembershipError(
            "schema-valid task manifest required; directory names are insufficient"
        )
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise B20MembershipError("task manifest is not valid JSON") from exc
    if not isinstance(payload, Mapping) or payload.get("schema") != B20_MEMBERSHIP_SCHEMA:
        raise B20MembershipError(f"task manifest schema must be {B20_MEMBERSHIP_SCHEMA}")
    raw_tasks = payload.get("tasks")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise B20MembershipError("task manifest must list at least one task")

    seen: set[str] = set()
    records: list[B20TaskRecord] = []
    for item in raw_tasks:
        if not isinstance(item, Mapping):
            raise B20MembershipError("each task record must be an object")
        task_id = str(item.get("id") or "").strip()
        oracle = str(item.get("oracle") or "").strip()
        kind = str(item.get("kind") or "").strip()
        if not task_id or not oracle:
            raise B20MembershipError("each task requires id and oracle")
        if is_rejected_b20_name(task_id):
            raise B20MembershipError(f"rejected task id: {task_id}")
        if task_id in seen:
            raise B20MembershipError(f"duplicate task id: {task_id}")
        seen.add(task_id)
        task_dir = root / task_id
        if not task_dir.is_dir():
            raise B20MembershipError(f"missing task directory: {task_id}")
        if not (task_dir / oracle).exists():
            raise B20MembershipError(f"missing oracle for {task_id}: {oracle}")
        records.append(B20TaskRecord(task_id, oracle, kind))

    records.sort(key=lambda record: record.task_id)
    digest = task_set_digest([record.task_id for record in records])
    declared = str(payload.get("task_set_digest") or "")
    if declared != digest:
        raise B20MembershipError("task-set digest mismatch")
    return B20Membership(tuple(records), digest)


def write_b20_report(
    path: Path | None,
    *,
    subject_sha: str,
    dry_run: bool = False,
    task_ids: Sequence[str] | None = None,
    results: Sequence[Mapping[str, Any]] | None = None,
    model: str = "",
    harness: str = "",
    total_cost_usd: float | None = None,
    total_duration_seconds: float | None = None,
) -> dict[str, Any]:
    """Write a B20 JSON receipt. Missing subject_sha is refused.

    Dry-run receipts keep pass/cost/oracle/oracle_passed null and do not
    invent empirical outcomes.
    """
    sha = str(subject_sha or "").strip()
    if not sha:
        raise ValueError("B20 receipt refused: missing subject_sha")
    ids = [str(task_id) for task_id in (task_ids or [])]
    if dry_run:
        payload: dict[str, Any] = {
            "schema": B20_REPORT_SCHEMA,
            "subject_sha": sha,
            "dry_run": True,
            "model": model,
            "harness": harness,
            "pass": None,
            "cost": None,
            "oracle": None,
            "oracle_passed": None,
            "pass_rate_pct": None,
            "total_cost_usd": None,
            "total_duration_seconds": None,
            "missingness": {
                "passed": 0,
                "failed": 0,
                "undeterminable": 0,
                "not_run": len(ids),
            },
            "results": [
                {
                    "id": task_id,
                    "kind": None,
                    "status": None,
                    "turns": None,
                    "tokens": None,
                    "cost_usd": None,
                    "latency_s": None,
                    "diagnosis": None,
                    "oracle_passed": None,
                    "disposition": "not_run",
                }
                for task_id in ids
            ],
        }
    else:
        rows = [_normalize_empirical_row(row) for row in (results or [])]
        missingness = {name: 0 for name in sorted(RESULT_DISPOSITIONS)}
        for row in rows:
            missingness[str(row["disposition"])] = missingness.get(str(row["disposition"]), 0) + 1
        passed = missingness.get("passed", 0)
        payload = {
            "schema": B20_REPORT_SCHEMA,
            "subject_sha": sha,
            "dry_run": False,
            "model": model,
            "harness": harness,
            "pass": passed,
            "cost": total_cost_usd,
            "oracle": passed,
            "oracle_passed": passed,
            "pass_rate_pct": round((passed / len(rows)) * 100, 1) if rows else 0.0,
            "total_cost_usd": total_cost_usd,
            "total_duration_seconds": total_duration_seconds,
            "missingness": missingness,
            "results": rows,
        }
    if path is not None:
        Path(path).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


class DirtySubjectError(ValueError):
    """A qualifying empirical run cannot bind a dirty Git subject."""


def require_clean_subject(repo_root: Path) -> str:
    """Return HEAD SHA only when the subject tree is clean."""
    root = Path(repo_root)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    sha = (head.stdout or "").strip()
    if head.returncode != 0 or not sha:
        raise DirtySubjectError("qualifying run refused: missing subject_sha")
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if status.returncode != 0 or (status.stdout or "").strip():
        raise DirtySubjectError("qualifying run refused: dirty subject")
    return sha


def classify_disposition(
    *,
    status: Any = None,
    attribution: Any = None,
    diagnosis: Any = None,
    dry_run: bool = False,
) -> str:
    """Map a runner row onto the closed missingness vocabulary."""
    if dry_run:
        return "not_run"
    status_text = "" if status is None else str(status).strip()
    attribution_text = "" if attribution is None else str(attribution).strip()
    diagnosis_text = "" if diagnosis is None else str(diagnosis).strip()
    if not status_text and not attribution_text and not diagnosis_text:
        return "not_run"
    combined = " ".join((attribution_text, diagnosis_text, status_text)).lower()
    if any(marker in combined for marker in _UNDETERMINABLE_MARKERS):
        return "undeterminable"
    status_upper = status_text.upper()
    if status_upper in {"PASS", "PASSED"} or attribution_text == "PASS":
        return "passed"
    if status_upper in {"FAIL", "FAILED"} or attribution_text == "LLM_COGNITIVE_ERROR":
        return "failed"
    if status_upper in {"NOT_RUN", "NONE"}:
        return "not_run"
    return "undeterminable"


def _is_pass_outcome(outcome: Any) -> bool:
    return str(outcome or "").strip().upper() in {"PASS", "PASSED"}


def _row_patch_digest(row: Mapping[str, Any]) -> str:
    return str(row.get("patch_digest") or row.get("patchDigest") or "").strip()


def _normalize_empirical_row(row: Mapping[str, Any]) -> dict[str, Any]:
    item = dict(row)
    diagnosis = str(item.get("diagnosis") or "")
    if "traceback" in diagnosis.lower():
        item["diagnosis"] = "harness_error"
        item["status"] = "UNDETERMINABLE"
    disposition = classify_disposition(
        status=item.get("status"),
        attribution=item.get("attribution"),
        diagnosis=item.get("diagnosis"),
    )
    if disposition == "passed" and not _row_patch_digest(item):
        raise ValueError("PASS row refused: missing patch digest")
    if disposition == "undeterminable" and str(item.get("status") or "").upper() == "FAIL":
        item["status"] = "UNDETERMINABLE"
    item["disposition"] = disposition
    return item
