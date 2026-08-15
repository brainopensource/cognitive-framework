#!/usr/bin/env python3
"""Execute every distinct test command registered by the Active MVP Contract."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CONTRACT = Path("docs/sprint0/active-mvp-contract.json")


def main() -> int:
    try:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"CONTRACT TEST FAIL: cannot load {CONTRACT}: {exc}")
        return 1

    registry = data.get("test_registry")
    if not isinstance(registry, list) or not registry:
        print("CONTRACT TEST FAIL: empty test_registry")
        return 1

    covered_test_ids = {
        row.get("test_id")
        for row in data.get("requirements", [])
        if isinstance(row, dict) and row.get("status") == "covered"
    }
    commands: dict[tuple[str, ...], list[str]] = {}
    for entry in registry:
        if not isinstance(entry, dict):
            print("CONTRACT TEST FAIL: registry entry is not an object")
            return 1
        test_id = entry.get("test_id")
        command = entry.get("command")
        if not isinstance(test_id, str) or not isinstance(command, list) or not command:
            print(f"CONTRACT TEST FAIL: malformed registry entry {entry!r}")
            return 1
        if test_id in covered_test_ids:
            commands.setdefault(tuple(command), []).append(test_id)

    failures = 0
    for command, test_ids in commands.items():
        print(f"CONTRACT TEST RUN: {','.join(sorted(test_ids))} -> {' '.join(command)}")
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
        if result.returncode != 0:
            failures += 1
            print(f"CONTRACT TEST FAIL: exit={result.returncode}; test_ids={','.join(sorted(test_ids))}")

    if failures:
        return 1
    print(
        f"CONTRACT TEST PASS: {len(covered_test_ids)} covered test IDs executed through "
        f"{len(commands)} distinct commands; open-row commands were not run"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
