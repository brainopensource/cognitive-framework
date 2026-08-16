#!/usr/bin/env python3
"""Execute every distinct test command registered by the Active MVP Contract."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import active_mvp_contract, repo_root

CONTRACT = active_mvp_contract()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run active contract tests")
    parser.add_argument(
        "--candidate",
        action="store_true",
        help="Run both open candidate and covered test rows (non-vacuous candidate gate)",
    )
    args = parser.parse_args()

    try:
        data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"CONTRACT TEST FAIL: cannot load {CONTRACT}: {exc}")
        return 1

    registry = data.get("test_registry")
    if not isinstance(registry, list) or not registry:
        print("CONTRACT TEST FAIL: empty test_registry")
        return 1

    if args.candidate:
        target_test_ids = {
            row.get("test_id")
            for row in data.get("requirements", [])
            if isinstance(row, dict) and row.get("status") in ("covered", "open")
        }
    else:
        target_test_ids = {
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
        if test_id in target_test_ids:
            commands.setdefault(tuple(command), []).append(test_id)

    if args.candidate and not commands:
        print("CONTRACT TEST FAIL: candidate mode executed 0 commands; candidate gates must be non-vacuous")
        return 1

    failures = 0
    for command, test_ids in commands.items():
        print(f"CONTRACT TEST RUN: {','.join(sorted(test_ids))} -> {' '.join(command)}")
        result = subprocess.run(command, text=True, capture_output=True, check=False, cwd=repo_root())
        if result.stdout:
            print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
        if result.returncode != 0:
            failures += 1
            print(f"CONTRACT TEST FAIL: exit={result.returncode}; test_ids={','.join(sorted(test_ids))}")

    if failures:
        return 1
    mode_str = "candidate" if args.candidate else "covered"
    print(
        f"CONTRACT TEST PASS: {len(target_test_ids)} {mode_str} test IDs executed through "
        f"{len(commands)} distinct commands"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
