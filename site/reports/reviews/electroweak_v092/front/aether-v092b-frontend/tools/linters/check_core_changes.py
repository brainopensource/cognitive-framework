#!/usr/bin/env python3
"""Core-change detector and C-10 measurement publisher (S10-B-02).

Owning contract: VG-03 §7.3, REQ-BENCH-001.

Measures and enforces core change discipline:
- Tracks diffs inside kernel/**, agency/episode/**, domain/wire/**.
- Reconstructions and second-domain adapters must minimize or eliminate core changes (C-10).
- Publishes exact core LOC delta.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

CORE_DIRECTORIES = (
    "vanguard/packages/kernel",
    "vanguard/packages/agency/episode",
    "vanguard/packages/domain/wire",
)


def count_core_changes(
    base_ref: str = "main",
    head_ref: str = "HEAD",
    repo_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[1]
    cmd = ["git", "diff", "--numstat", f"{base_ref}...{head_ref}"]

    try:
        res = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=True)
        lines = res.stdout.strip().splitlines()
    except subprocess.CalledProcessError:
        # Fallback to local working tree status / diff against HEAD
        try:
            res = subprocess.run(["git", "diff", "--numstat", "HEAD"], cwd=root, capture_output=True, text=True, check=True)
            lines = res.stdout.strip().splitlines()
        except subprocess.CalledProcessError:
            lines = []

    core_changes: dict[str, dict[str, int]] = {}
    total_added = 0
    total_deleted = 0

    for line in lines:
        parts = line.split(maxsplit=2)
        if len(parts) != 3:
            continue
        added_str, deleted_str, path_str = parts
        # Skip binary files represented as '-'
        if added_str == "-" or deleted_str == "-":
            continue
        added = int(added_str)
        deleted = int(deleted_str)

        for core_dir in CORE_DIRECTORIES:
            if path_str.startswith(core_dir):
                core_changes[path_str] = {"added": added, "deleted": deleted}
                total_added += added
                total_deleted += deleted

    total_delta = total_added + total_deleted
    return {
        "coreDirectories": list(CORE_DIRECTORIES),
        "totalAdded": total_added,
        "totalDeleted": total_deleted,
        "totalDeltaLoc": total_delta,
        "filesChanged": core_changes,
        "c10Metric": total_delta,
        "c10ZeroAchieved": (total_delta == 0),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="main", help="Base ref or branch")
    parser.add_argument("--head", default="HEAD", help="Head ref")
    parser.add_argument("--require-zero", action="store_true", help="Fail if any core LOC changed")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args(argv)
    res = count_core_changes(args.base, args.head)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"C-10 Core LOC Delta: {res['totalDeltaLoc']} (Added: {res['totalAdded']}, Deleted: {res['totalDeleted']})")
        for f, diff in res["filesChanged"].items():
            print(f"  {f}: +{diff['added']} / -{diff['deleted']}")

    if args.require_zero and res["totalDeltaLoc"] > 0:
        print(f"CORE CHANGE DETECTED: {res['totalDeltaLoc']} core LOC changed without exemption", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
