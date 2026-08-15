#!/usr/bin/env python3
"""Validate manual T0 traces and report, without concealing human-review gaps."""

from __future__ import annotations

import csv
import sys
from pathlib import Path


TRACE_DIR = Path("docs/sprint0/schema-archaeology/traces")
EXPECTED = {"BUG-01.tsv", "BUG-02.tsv", "BUG-03.tsv", "NONCODE-01.tsv"}
KINDS = {"observation", "proposal", "effect", "receipt", "judgement"}
REQUIRED_COLUMNS = {
    "trace_id", "step_id", "previous_step_id", "step_kind", "actor_id",
    "started_at", "ended_at", "elapsed_ms", "hands_on_ms", "environment_snapshot",
    "resource_selector", "content_or_args_ref", "purpose_or_hypothesis",
    "observed_or_proposed_outcome", "result_or_receipt_ref", "uncertainty",
    "provenance", "acceptance_condition_ref", "next_step_reason", "correction_of",
    "redaction_note",
}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    present = {path.name for path in TRACE_DIR.glob("*.tsv")}
    if present != EXPECTED:
        errors.append(f"trace set mismatch: expected={sorted(EXPECTED)} present={sorted(present)}")

    total = 0
    for path in sorted(TRACE_DIR.glob("*.tsv")):
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            if set(reader.fieldnames or []) != REQUIRED_COLUMNS:
                errors.append(f"{path}: columns do not match the template")
                continue
            seen: set[str] = set()
            expected_trace = path.stem
            for line, row in enumerate(reader, start=2):
                total += 1
                label = f"{path}:{line}"
                if row["trace_id"] != expected_trace:
                    errors.append(f"{label}: trace_id must equal {expected_trace}")
                if not row["step_id"] or row["step_id"] in seen:
                    errors.append(f"{label}: missing or duplicate step_id")
                previous = row["previous_step_id"]
                if previous and previous not in seen:
                    errors.append(f"{label}: previous_step_id does not name an earlier step")
                if row["step_kind"] not in KINDS:
                    errors.append(f"{label}: invalid step_kind {row['step_kind']!r}")
                for field in REQUIRED_COLUMNS - {"previous_step_id", "correction_of"}:
                    if not row[field].strip():
                        errors.append(f"{label}: empty {field}")
                if row["hands_on_ms"] == "unmeasured":
                    warnings.append(f"{label}: retrospective trace has no human hands-on timing")
                seen.add(row["step_id"])

    for warning in warnings:
        print(f"ARCHAEOLOGY WARNING: {warning}")
    for error in errors:
        print(f"ARCHAEOLOGY FAIL: {error}")
    if errors:
        return 1
    print(f"ARCHAEOLOGY STRUCTURE PASS: {len(EXPECTED)} traces, {total} append-only steps")
    print("ARCHAEOLOGY HUMAN GATES OPEN: independent third-engineer reconstruction and human hands-on timing are not machine-certifiable")
    return 0


if __name__ == "__main__":
    sys.exit(main())

