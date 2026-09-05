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
