"""REL-02 frozen single-attempt canary: content-addressed manifest integrity.

The canary is a data artifact (`artifacts/canary_manifest.json`).  This module
is the only reader that may admit it for live execution, and it fails closed:
any drift between the reviewed manifest digest and the file contents, any
denominator or missingness ambiguity, and any attempt-count or ceiling drift is
a typed refusal -- never a warning, never a silent substitution.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

__all__ = [
    "CANARY_SCHEMA",
    "CANARY_DISPOSITIONS",
    "CanaryIntegrityError",
    "CanaryVerification",
    "compute_manifest_digest",
    "digest_of",
    "verify_canary",
    "load_canary",
]

CANARY_SCHEMA = "aether.m8-canary/1"

#: Closed disposition vocabulary.  Missingness is never collapsed into failure
#: and failure is never collapsed into zero; only ``PASSED`` is task success.
CANARY_DISPOSITIONS = (
    "NOT_RUN",
    "INVALID_TASK",
    "PROVIDER_UNAVAILABLE",
    "BUDGET_EXHAUSTED",
    "TIMED_OUT",
    "MODEL_PROTOCOL_ERROR",
    "NO_PATCH",
    "PATCH_REJECTED",
    "EVALUATOR_UNAVAILABLE",
    "EVALUATOR_FAILED",
    "PASSED",
)

_DIGEST_KEY = "manifest_digest"


def digest_of(obj: Any) -> str:
    """Canonical digest using the benchmark-runner convention (sorted-key JSON)."""
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CanaryIntegrityError(RuntimeError):
    """The canary manifest failed content-addressed verification."""


@dataclass(frozen=True, slots=True)
class CanaryVerification:
    ok: bool
    reason: str = "CANARY_VERIFIED"
    failures: tuple[str, ...] = field(default=())


def compute_manifest_digest(manifest: Mapping[str, Any]) -> str:
    """Digest over the RFC 8785 canonical form minus the self-digest key."""
    payload = {k: v for k, v in manifest.items() if k != _DIGEST_KEY}
    return digest_of(payload)


def verify_canary(manifest: Mapping[str, Any]) -> CanaryVerification:
    """Fail-closed verification of the frozen canary manifest."""
    failures: list[str] = []

    if manifest.get("schema") != CANARY_SCHEMA:
        failures.append(f"SCHEMA_MISMATCH:{manifest.get('schema')!r}")

    claimed = manifest.get(_DIGEST_KEY)
    computed = compute_manifest_digest(manifest)
    if not isinstance(claimed, str) or claimed != computed:
        failures.append(f"DIGEST_MISMATCH:claimed={claimed!r},computed={computed}")

    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != manifest.get("task_count"):
        failures.append("TASK_COUNT_MISMATCH")
    else:
        ids = [t.get("id") for t in tasks if isinstance(t, Mapping)]
        if len(ids) != len(tasks) or len(set(ids)) != len(ids):
            failures.append("TASK_IDS_NOT_UNIQUE")
        for task in tasks:
            if not isinstance(task.get("payload_digest"), str) or not task["payload_digest"].startswith("sha256:"):
                failures.append(f"TASK_PAYLOAD_UNPINNED:{task.get('id')!r}")
            if task.get("max_attempts") != 1:
                failures.append(f"ATTEMPT_POLICY_DRIFT:{task.get('id')!r}")

    policy = manifest.get("attempt_policy") or {}
    if policy.get("max_attempts") != 1:
        failures.append("MAX_ATTEMPTS_NOT_ONE")

    budget = manifest.get("resource_budget") or {}
    for key in ("global_cost_usd_ceiling", "per_task_cost_usd_ceiling",
                "global_token_ceiling", "per_task_token_ceiling",
                "per_task_timeout_seconds"):
        value = budget.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            failures.append(f"CEILING_MISSING:{key}")

    if manifest.get("denominator") != manifest.get("task_count"):
        failures.append("DENOMINATOR_MISMATCH")

    missingness = manifest.get("missingness_policy") or {}
    declared = missingness.get("dispositions") or ()
    if set(declared) != set(CANARY_DISPOSITIONS):
        failures.append("DISPOSITION_VOCABULARY_DRIFT")
    if missingness.get("success_disposition") != "PASSED":
        failures.append("SUCCESS_DISPOSITION_NOT_PASSED")

    if not isinstance(manifest.get("expected_artifact_schema"), Mapping) or \
            not manifest["expected_artifact_schema"].get("required_fields"):
        failures.append("ARTIFACT_SCHEMA_UNDECLARED")

    if not isinstance(manifest.get("base_commit"), str) or not manifest["base_commit"]:
        failures.append("BASE_COMMIT_UNPINNED")
    if not isinstance(manifest.get("workload_digest"), str) or not manifest["workload_digest"].startswith("sha256:"):
        failures.append("WORKLOAD_DIGEST_UNPINNED")

    if failures:
        return CanaryVerification(False, failures[0], tuple(failures))
    return CanaryVerification(True)


def load_canary(path: str | Path | None = None) -> Mapping[str, Any]:
    """Load and verify the frozen canary; refuse live execution on any drift."""
    if path is None:
        path = Path(__file__).resolve().parent / "artifacts" / "canary_manifest.json"
    manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    verification = verify_canary(manifest)
    if not verification.ok:
        raise CanaryIntegrityError(
            "canary manifest refused for live execution: "
            + "; ".join(verification.failures)
        )
    return manifest
