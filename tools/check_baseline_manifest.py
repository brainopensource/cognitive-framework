#!/usr/bin/env python3
"""Verify the local Sprint 0 integrity manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import baseline_manifest, repo_root, stale_path_matches


MANIFEST = baseline_manifest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release",
        action="store_true",
        help="Fail unless git tag and branch protection are verified (R10).",
    )
    args = parser.parse_args()
    root = repo_root()
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"BASELINE FAIL: cannot load {MANIFEST}: {exc}")
        return 1
    failures: list[str] = []
    files = data.get("files")
    if data.get("schema_version") != "gts.sprint0-baseline-manifest.v1" or not isinstance(files, dict) or not files:
        print("BASELINE FAIL: malformed manifest")
        return 1
    for name in files:
        if stale_path_matches(name):
            failures.append(f"stale path in manifest key: {name}")
    for name, expected in sorted(files.items()):
        path = root / name
        if not path.is_file():
            failures.append(f"missing {name}")
            continue
        actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(f"digest drift {name}: expected={expected} actual={actual}")
    for failure in failures:
        print(f"BASELINE FAIL: {failure}")
    if failures:
        return 1
    print(f"BASELINE PASS: {len(files)} local artifacts match APPROVAL-0002 manifest")
    external_open = data.get("git_tag_status") != "created" or data.get("branch_protection_status") != "verified"
    if external_open:
        print("BASELINE EXTERNAL GATES OPEN: Git tag and/or branch protection are not established")
        if args.release:
            print("BASELINE FAIL: --release requires verified git tag and branch protection")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
