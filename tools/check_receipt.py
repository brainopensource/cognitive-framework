#!/usr/bin/env python3
"""Validate Sprint 6B machine receipts (S6B-EVID-001 / S6B-QA-003)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import docs_agile, repo_root, stale_path_matches

SCHEMA_PATH = docs_agile("sprint6B", "gate-receipt.schema.json")
GATES = {f"R{i}" for i in range(11)}
RESULTS = {"PASS", "FAIL", "BLOCKED"}
RELATIONS = {"same-commit", "ci-artifact", "follow-up-commit"}


def validate_receipt(data: object, *, path: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{path}: receipt must be an object"]
    if data.get("schema_version") != "gts.gate-receipt.v1":
        errors.append(f"{path}: unsupported schema_version")
    if data.get("gate") not in GATES:
        errors.append(f"{path}: invalid gate {data.get('gate')!r}")
    if data.get("result") not in RESULTS:
        errors.append(f"{path}: invalid result {data.get('result')!r}")
    if data.get("result") == "pending" or "pending" in json.dumps(data).lower() and data.get("result") not in RESULTS:
        errors.append(f"{path}: pending values are forbidden")
    subject = data.get("subject_sha")
    if not isinstance(subject, str) or len(subject) != 40 or any(c not in "0123456789abcdef" for c in subject):
        errors.append(f"{path}: subject_sha must be a 40-char lowercase hex SHA")
    if data.get("evidence_commit_relation") not in RELATIONS:
        errors.append(f"{path}: invalid evidence_commit_relation")
    if data.get("evidence_commit_relation") == "same-commit" and data.get("evidence_commit") != subject:
        errors.append(f"{path}: same-commit relation requires evidence_commit == subject_sha")
    signer = data.get("signer")
    implementer = data.get("implementer")
    countersigner = data.get("countersigner")
    if not all(isinstance(v, str) and v.strip() for v in (signer, implementer, countersigner)):
        errors.append(f"{path}: implementer, signer and countersigner are required")
    elif signer == implementer:
        errors.append(f"{path}: signer cannot be the implementer (self-approval)")
    elif countersigner in {signer, implementer}:
        errors.append(f"{path}: countersigner must be independent of implementer and signer")
    commands = data.get("commands")
    if not isinstance(commands, list) or not commands:
        errors.append(f"{path}: commands must be a non-empty array")
    else:
        seen: set[tuple[str, ...]] = set()
        for index, command in enumerate(commands):
            if not isinstance(command, dict):
                errors.append(f"{path}: command {index} must be an object")
                continue
            argv = command.get("argv")
            if not isinstance(argv, list) or not argv:
                errors.append(f"{path}: command {index} argv is required")
                continue
            key = tuple(argv)
            if key in seen:
                errors.append(f"{path}: duplicate evidence command {argv}")
            seen.add(key)
            if argv[:1] == ["true"] or argv == ["echo", "ok"]:
                errors.append(f"{path}: command {index} is too broad")
            for digest_field in ("stdout_sha256", "stderr_sha256"):
                value = command.get(digest_field)
                if not isinstance(value, str) or not value.startswith("sha256:") or len(value) != 71:
                    errors.append(f"{path}: command {index} {digest_field} digest missing or malformed")
    rendered = json.dumps(data)
    if stale_path_matches(rendered):
        errors.append(f"{path}: receipt cites a stale documentation path")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipts", nargs="*", type=Path)
    args = parser.parse_args()
    root = repo_root()
    paths = args.receipts or sorted((root / "docs/agile/sprint6B/evidence").glob("R*/receipt.json"))
    if not paths:
        print("RECEIPT FAIL: no receipts provided and no docs/agile/sprint6B/evidence/R*/receipt.json files")
        return 1
    errors: list[str] = []
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: cannot load: {exc}")
            continue
        errors.extend(validate_receipt(data, path=path))
    for error in errors:
        print(f"RECEIPT FAIL: {error}")
    if errors:
        return 1
    print(f"RECEIPT PASS: {len(paths)} receipt(s) structurally valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
