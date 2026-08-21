#!/usr/bin/env python3
"""Validate the Active MVP Contract and emit its two non-interchangeable metrics."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import active_mvp_contract, repo_root, rewrite_legacy_doc_path, stale_path_matches

CONTRACT = active_mvp_contract()
REQUIRED_FIELDS = {
    "req_id",
    "source",
    "statement",
    "rationale",
    "component",
    "owner",
    "test_owner",
    "dependencies",
    "verification_family",
    "test_id",
    "acceptance_evidence",
    "margin",
    "status",
    "justification",
    "compensating_assurance",
}
FAMILIES = {"architecture", "must-fail", "property", "conformance", "fault-injection", "adversarial"}
STATUSES = {"open", "covered", "justified"}
CONTRACT_STATUSES = {
    "closure-in-progress",
    "approved-phase2-closed",
    "approved",
    "approved-s0-s4-closed",
}
COMPONENT_ALIASES = {"adapters/model": "adapters/models"}
BROAD_COMMANDS = {("true",), ("echo", "ok"), ("exit", "0")}


def percentage(numerator: int, denominator: int) -> float:
    return 100.0 if denominator == 0 else numerator * 100.0 / denominator


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release",
        action="store_true",
        help="R10 mode: fail unless every merged row is covered/justified with structured receipts.",
    )
    args = parser.parse_args()
    errors: list[str] = []
    root = repo_root()
    try:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"CONTRACT FAIL: cannot load {CONTRACT}: {exc}")
        return 1

    if data.get("schema_version") != "gts.active-mvp-contract.v1":
        errors.append("unsupported schema_version")
    contract_status = data.get("status")
    if contract_status not in CONTRACT_STATUSES:
        errors.append(f"unsupported contract status {contract_status!r}")
    if contract_status == "approved-phase2-closed" and not args.release:
        errors.append("approved-phase2-closed is invalid while Sprint 6B closure is in progress; use closure-in-progress")
    requirements = data.get("requirements")
    identities = data.get("owner_identities")
    merged = data.get("merged_components")
    registry = data.get("test_registry")
    deferred = data.get("deferred_activation")
    if not isinstance(requirements, list) or not requirements:
        errors.append("requirements must be a non-empty array")
        requirements = []
    if not isinstance(identities, dict) or not identities:
        errors.append("owner_identities must be a non-empty object")
        identities = {}
    if not isinstance(merged, list) or any(not isinstance(item, str) for item in merged):
        errors.append("merged_components must be a string array")
        merged = []
    if not isinstance(deferred, list):
        errors.append("deferred_activation must be an array")
    if not isinstance(registry, list) or not registry:
        errors.append("test_registry must be a non-empty array")
        registry = []

    registered_tests: set[str] = set()
    for entry in registry:
        if not isinstance(entry, dict):
            errors.append("test_registry entries must be objects")
            continue
        test_id, command = entry.get("test_id"), entry.get("command")
        if not isinstance(test_id, str) or not re.fullmatch(r"TEST-[A-Z]+-[0-9]{3}", test_id):
            errors.append(f"invalid registered test_id: {test_id!r}")
        elif test_id in registered_tests:
            errors.append(f"duplicate registered test_id: {test_id}")
        else:
            registered_tests.add(test_id)
        if not isinstance(command, list) or not command or any(not isinstance(arg, str) or not arg for arg in command):
            errors.append(f"{test_id}: command must be a non-empty string array")
        elif tuple(command) in BROAD_COMMANDS:
            errors.append(f"{test_id}: command is too broad to be falsifiable")

    req_ids: set[str] = set()
    test_ids: set[str] = set()
    baseline_complete = 0
    merged_rows = 0
    merged_complete = 0
    for index, row in enumerate(requirements, start=1):
        label = row.get("req_id", f"row-{index}") if isinstance(row, dict) else f"row-{index}"
        if not isinstance(row, dict):
            errors.append(f"{label}: requirement must be an object")
            continue
        missing = REQUIRED_FIELDS - row.keys()
        extra = row.keys() - REQUIRED_FIELDS - {"evidence_receipt"}
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
        if extra:
            errors.append(f"{label}: unknown fields {sorted(extra)}")
        req_id = row.get("req_id")
        test_id = row.get("test_id")
        if not isinstance(req_id, str) or not re.fullmatch(r"REQ-[A-Z]+-[0-9]{3}", req_id):
            errors.append(f"{label}: invalid req_id")
        elif req_id in req_ids:
            errors.append(f"{label}: duplicate req_id")
        else:
            req_ids.add(req_id)
        if not isinstance(test_id, str) or test_id not in registered_tests:
            errors.append(f"{label}: test_id is not registered")
        elif test_id in test_ids:
            errors.append(f"{label}: test_id must be unique")
        else:
            test_ids.add(test_id)
        for owner_field in ("owner", "test_owner"):
            if row.get(owner_field) not in identities:
                errors.append(f"{label}: {owner_field} is not a named owner identity")
        if row.get("verification_family") not in FAMILIES:
            errors.append(f"{label}: invalid verification_family")
        if row.get("status") not in STATUSES:
            errors.append(f"{label}: invalid status")
        if not isinstance(row.get("dependencies"), list):
            errors.append(f"{label}: dependencies must be an array")
        text_fields = ("source", "statement", "rationale", "component", "acceptance_evidence", "margin")
        assigned = all(isinstance(row.get(field), str) and row[field].strip() for field in text_fields)
        assigned = assigned and row.get("owner") in identities and row.get("test_owner") in identities
        assigned = assigned and isinstance(test_id, str) and test_id in registered_tests and isinstance(row.get("dependencies"), list)
        baseline_complete += int(assigned)

        component = row.get("component")
        if isinstance(component, str) and component in COMPONENT_ALIASES:
            errors.append(f"{label}: component {component!r} must be normalized to {COMPONENT_ALIASES[component]!r}")
        if stale_path_matches(str(row.get("acceptance_evidence", ""))):
            errors.append(f"{label}: acceptance_evidence cites a stale documentation path")
        status = row.get("status")
        if status == "covered" and not row.get("acceptance_evidence", "").strip():
            errors.append(f"{label}: covered row lacks acceptance evidence")
        receipt = row.get("evidence_receipt")
        if status == "covered":
            if not isinstance(receipt, str) or not receipt.strip():
                errors.append(f"{label}: covered row lacks structured evidence_receipt")
            else:
                live_receipt = rewrite_legacy_doc_path(receipt)
                receipt_path = root / live_receipt
                if not receipt_path.is_file():
                    errors.append(f"{label}: evidence_receipt missing: {receipt}")
        if status == "justified" and not (row.get("justification", "").strip() and row.get("compensating_assurance", "").strip()):
            errors.append(f"{label}: justified row needs reason and compensating assurance")
        if row.get("component") in merged or COMPONENT_ALIASES.get(str(row.get("component"))) in merged:
            merged_rows += 1
            if status in {"covered", "justified"}:
                merged_complete += 1
            elif args.release or contract_status == "approved-phase2-closed":
                errors.append(f"{label}: merged component requirement remains open")

    for row in requirements:
        if isinstance(row, dict):
            for dependency in row.get("dependencies", []):
                if dependency not in req_ids:
                    errors.append(f"{row.get('req_id')}: unknown dependency {dependency}")

    baseline = percentage(baseline_complete, len(requirements))
    evidence = percentage(merged_complete, merged_rows)
    if baseline != 100.0:
        errors.append("baseline_assignment_coverage must equal 100%")
    if evidence != 100.0 and (args.release or contract_status == "approved-phase2-closed"):
        errors.append("merged_scope_evidence_coverage must equal 100%")
    print(f"contract_status={contract_status}")
    print(f"baseline_assignment_coverage={baseline:.1f}% ({baseline_complete}/{len(requirements)})")
    print(f"merged_scope_evidence_coverage={evidence:.1f}% ({merged_complete}/{merged_rows})")
    for error in errors:
        print(f"CONTRACT FAIL: {error}")
    if errors:
        return 1
    if args.release:
        print("CONTRACT RELEASE PASS")
    else:
        print(
            f"CONTRACT PASS: {len(requirements)} active requirements; "
            f"{len(deferred or [])} deferred activation record(s); "
            f"closure-in-progress allows open merged rows"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
