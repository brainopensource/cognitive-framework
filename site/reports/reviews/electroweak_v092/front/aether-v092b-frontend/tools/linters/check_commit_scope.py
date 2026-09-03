#!/usr/bin/env python3
"""Reject documentation-only commit labels on production or schema changes."""

from __future__ import annotations

import argparse
import os
import re
import subprocess


DOC_ONLY = re.compile(r"^(?:docs|chore)(?:\([^)]*\))?:", re.IGNORECASE)
PROTECTED_PREFIXES = ("vanguard/packages/", "schemas/")


def is_mislabelled(subject: str, paths: list[str]) -> bool:
    return bool(DOC_ONLY.match(subject.strip())) and any(
        path.startswith(PROTECTED_PREFIXES) for path in paths
    )


def violations(base: str, head: str = "HEAD") -> list[str]:
    commits = subprocess.check_output(
        ["git", "rev-list", "--reverse", f"{base}..{head}"], text=True
    ).splitlines()
    errors: list[str] = []
    for commit in commits:
        subject = subprocess.check_output(
            ["git", "show", "-s", "--format=%s", commit], text=True
        ).strip()
        paths = subprocess.check_output(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", commit], text=True
        ).splitlines()
        if is_mislabelled(subject, paths):
            protected = sorted(path for path in paths if path.startswith(PROTECTED_PREFIXES))
            errors.append(f"{commit} {subject!r} touches {protected}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default=os.environ.get("GITHUB_BASE_SHA", ""))
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args()
    if not args.base:
        print("COMMIT SCOPE NOT APPLICABLE: no comparison base supplied")
        return 0
    errors = violations(args.base, args.head)
    for error in errors:
        print(f"COMMIT SCOPE FAIL: {error}")
    if errors:
        return 1
    print("COMMIT SCOPE PASS: production/schema commits use non-documentation labels")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
