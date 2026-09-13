"""EXP-01 evidence row schema (§EW-9.4). Append-only; refuse incomplete rows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.evidence.disposition import TaskDisposition

__all__ = [
    "EVIDENCE_LABELS",
    "LIVE_LABELS",
    "REQUIRED_GROUPS",
    "EvidenceError",
    "append_row",
    "reconcile_population",
    "suite_digest",
]

EVIDENCE_LABELS = frozenset({
    "REPLAY", "LIVE-HISTORICAL", "STATIC", "UNDETERMINABLE",
    "LIVE-LOCAL", "LIVE-HOSTED",
})
LIVE_LABELS = frozenset({"LIVE-LOCAL", "LIVE-HOSTED"})

REQUIRED_GROUPS: dict[str, tuple[str, ...]] = {
    "identity": (
        "subject_sha", "dirty_flag", "suite_digest", "n", "task_id",
        "task_digest", "oracle_digest", "run_id",
    ),
    "arm": (
        "manifest_digest", "preset", "model_id", "provider", "server_build",
        "gguf_digest", "quantization", "context_size", "sampling_digest",
        "prompt_digest", "tool_schema_digest",
    ),
    "execution": (
        "evidence_label", "raw_response_digest", "valid_tool_calls",
        "malformed_tool_calls", "recovery_attempts", "turns",
        "time_to_first_valid_action_s", "latency_s",
    ),
    "change": ("patch_digest", "postimage_digest", "files_changed", "no_op"),
    "verification": (
        "tests_discovered", "tests_executed", "tests_passed", "tests_failed",
        "tamper_digest", "tamper_verdict",
    ),
    "settlement": ("terminal_status", "disposition", "undeterminable_reason"),
    "economics": (
        "prompt_tokens", "completion_tokens", "cache_read_tokens",
        "cache_write_tokens", "cost_usd_micros", "local_time_proxy_s",
    ),
    "provenance": ("hypothesis_id", "control_digest", "varied_dimension"),
}


class EvidenceError(ValueError):
    """A row or table that cannot be admitted into a published report."""


def suite_digest(task_ids: Sequence[str]) -> str:
    return digest_of({"tasks": list(task_ids)})


def _missing_fields(row: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []
    for group, fields in REQUIRED_GROUPS.items():
        payload = row.get(group)
        if not isinstance(payload, Mapping):
            missing.append(group)
            continue
        for field in fields:
            if field not in payload:
                missing.append(f"{group}.{field}")
    return missing


def _validate_row(row: Mapping[str, Any]) -> None:
    missing = _missing_fields(row)
    if missing:
        raise EvidenceError(f"incomplete evidence row: {missing}")
    label = str(row["execution"]["evidence_label"])
    if label not in EVIDENCE_LABELS:
        raise EvidenceError(f"unknown evidence_label {label!r}")
    terminal = str(row["settlement"]["terminal_status"])
    patch = row["change"].get("patch_digest")
    if terminal == "completed" and not patch:
        raise EvidenceError("completed outcome refused: missing patch digest")
    disposition = str(row["settlement"]["disposition"])
    legal = {item.value for item in TaskDisposition}
    if disposition not in legal:
        raise EvidenceError(f"illegal disposition {disposition!r}")
    if disposition == "undeterminable" and not row["settlement"].get("undeterminable_reason"):
        raise EvidenceError("undeterminable rows require a reason")


def append_row(table: list[dict[str, Any]], row: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Append one immutable row, refusing mixed replay/live populations."""
    _validate_row(row)
    labels = {str(item["execution"]["evidence_label"]) for item in table}
    labels.add(str(row["execution"]["evidence_label"]))
    live = labels & LIVE_LABELS
    replay = labels & {"REPLAY", "LIVE-HISTORICAL"}
    if live and replay:
        raise EvidenceError("a table cannot mix REPLAY/LIVE-HISTORICAL with current LIVE-* rows")
    table.append(dict(row))
    return table


#: Row fields whose value must equal the frozen manifest, per row.
_IDENTITY_BINDINGS = ("subject_sha", "suite_digest")
_ARM_BINDINGS = (
    "manifest_digest", "preset", "provider", "sampling_digest", "prompt_digest",
    "tool_schema_digest",
)
_MISSING_DISPOSITIONS = frozenset({"undeterminable", "not_run"})


def reconcile_population(
    rows: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Any],
) -> dict[str, Any]:
    """Join evidence rows to a frozen manifest, refusing anything unbound.

    Every scheduled slot must appear exactly once, bound to the frozen subject,
    suite, task/oracle identity and arm configuration. Missingness is counted
    separately from binary failure; it never shrinks the denominator.
    """
    suite = manifest.get("suite") or {}
    tasks = list(suite.get("tasks") or ())
    if not tasks:
        raise EvidenceError("the manifest declares no frozen membership")
    scheduled = set(tasks)
    task_digests = suite.get("task_digests") or {}
    oracle_digests = suite.get("oracle_digests") or {}
    arm = manifest.get("arm") or {}

    seen: dict[str, int] = {}
    labels: set[str] = set()
    passes = evaluated = 0
    for index, row in enumerate(rows):
        _validate_row(row)
        identity = row["identity"]
        task_id = str(identity["task_id"])
        if task_id not in scheduled:
            raise EvidenceError(
                f"row {index} scores {task_id!r}, which is not in the frozen membership")
        if task_id in seen:
            raise EvidenceError(
                f"duplicate attempt for {task_id!r}: rows {seen[task_id]} and {index}")
        seen[task_id] = index
        for field in _IDENTITY_BINDINGS:
            if identity.get(field) != manifest.get(field):
                raise EvidenceError(
                    f"row {index} identity.{field} does not match the frozen record")
        if identity.get("n") != len(tasks):
            raise EvidenceError(
                f"row {index} declares denominator {identity.get('n')!r}; "
                f"the frozen sample is {len(tasks)}")
        if identity.get("task_digest") != task_digests.get(task_id):
            raise EvidenceError(f"row {index} task_digest does not match the frozen task")
        if identity.get("oracle_digest") != oracle_digests.get(task_id):
            raise EvidenceError(f"row {index} oracle_digest does not match the frozen oracle")
        row_arm = row["arm"]
        if row_arm.get("model_id") != manifest.get("model_id"):
            raise EvidenceError(f"row {index} arm.model_id does not match the frozen model")
        for field in _ARM_BINDINGS:
            if row_arm.get(field) != arm.get(field):
                raise EvidenceError(
                    f"row {index} arm.{field} does not match the frozen configuration")
        label = str(row["execution"]["evidence_label"])
        labels.add(label)
        disposition = str(row["settlement"]["disposition"])
        if label in LIVE_LABELS and disposition not in _MISSING_DISPOSITIONS:
            evaluated += 1
            if disposition == "passed":
                passes += 1

    if labels & LIVE_LABELS and labels & {"REPLAY", "LIVE-HISTORICAL"}:
        raise EvidenceError("a control population cannot mix replay and current LIVE-* rows")
    absent = [task for task in tasks if task not in seen]
    if absent:
        raise EvidenceError(f"missing scheduled slots: {absent}")

    return {
        "n_scheduled": len(tasks),
        "n_rows": len(rows),
        "n_evaluable": evaluated,
        "n_passed": passes,
        "n_missing": len(tasks) - evaluated,
        "evidence_labels": sorted(labels),
    }
