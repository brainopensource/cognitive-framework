#!/usr/bin/env python3
"""Prove each registered must-fail test rejects a broken counterpart."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import repo_root

MANIFEST = repo_root() / "test" / "broken" / "manifest.json"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False, cwd=repo_root())


def main() -> int:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BROKEN HARNESS FAIL: cannot load {MANIFEST}: {exc}")
        return 1
    cases = data.get("cases")
    if data.get("schema_version") != "gts.broken-test-manifest.v1" or not isinstance(cases, list) or not cases:
        print("BROKEN HARNESS FAIL: invalid or empty manifest")
        return 1

    failures: list[str] = []
    seen: set[str] = set()
    receipts: list[dict[str, object]] = []
    for case in cases:
        test_id = case.get("test_id")
        control = case.get("control")
        broken = case.get("broken")
        expected = case.get("expected_failure")
        if not isinstance(test_id, str) or not test_id or test_id in seen:
            failures.append(f"invalid or duplicate test_id: {test_id!r}")
            continue
        seen.add(test_id)
        if not all(isinstance(value, list) and all(isinstance(arg, str) for arg in value) for value in (control, broken)):
            failures.append(f"{test_id}: commands must be string arrays")
            continue
        if not isinstance(expected, str) or not expected:
            failures.append(f"{test_id}: expected_failure is required")
            continue

        reference_run = run(control)
        broken_run = run(broken)
        broken_output = broken_run.stdout + broken_run.stderr
        ok = reference_run.returncode == 0 and broken_run.returncode != 0 and expected in broken_output
        if reference_run.returncode != 0:
            failures.append(f"{test_id}: reference failed unexpectedly: {reference_run.stdout}{reference_run.stderr}")
        if broken_run.returncode == 0:
            failures.append(f"{test_id}: broken counterpart passed")
        elif expected not in broken_output:
            failures.append(f"{test_id}: broken counterpart failed for the wrong reason; expected {expected!r}; got {broken_output!r}")
        receipts.append(
            {
                "test_id": test_id,
                "reference_exit": reference_run.returncode,
                "broken_exit": broken_run.returncode,
                "expected_failure_observed": expected in broken_output,
                "result": "pass" if ok else "fail",
            }
        )

    for receipt in receipts:
        print(json.dumps(receipt, sort_keys=True))
    for failure in failures:
        print(f"BROKEN HARNESS FAIL: {failure}")
    if failures:
        return 1
    print(f"BROKEN HARNESS PASS: {len(receipts)} broken counterparts observed failing")
    return 0


if __name__ == "__main__":
    sys.exit(main())

