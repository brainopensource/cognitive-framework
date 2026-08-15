#!/usr/bin/env python3
"""Verify the local Sprint 0 integrity manifest."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


MANIFEST = Path("docs/sprint0/baseline-manifest.json")


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    files = data.get("files")
    if data.get("schema_version") != "gts.sprint0-baseline-manifest.v1" or not isinstance(files, dict) or not files:
        print("BASELINE FAIL: malformed manifest")
        return 1
    for name, expected in sorted(files.items()):
        path = Path(name)
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
    if data.get("git_tag_status") != "created" or data.get("branch_protection_status") != "verified":
        print("BASELINE EXTERNAL GATES OPEN: Git tag and/or branch protection are not established")
    return 0


if __name__ == "__main__":
    sys.exit(main())
