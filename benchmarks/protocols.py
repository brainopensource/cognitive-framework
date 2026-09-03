"""Normalized, offline benchmark protocol contracts.

These values describe benchmark inputs and receipts; they do not execute a
provider or evaluator.  A receipt is admissible only when its subject digest
matches the normalized task and submission identities supplied by the caller.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol

SUPPORTED_PROTOCOLS = frozenset({"SWE-bench Verified", "SWE-Bench Pro", "DeepSWE v1.1"})

__all__ = ["BenchmarkTask", "BenchmarkSubmission", "BenchmarkReceipt",
           "SUPPORTED_PROTOCOLS", "PROTOCOL_SPECS", "ProtocolSpec",
           "EvaluatorAdapter", "normalize"]


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
