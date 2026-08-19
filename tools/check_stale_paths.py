#!/usr/bin/env python3
"""Fail when live tools, CI, manifests or indexes still cite obsolete docs paths."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import repo_root, stale_path_matches

SCAN_GLOBS = (
    ".github/**/*",
    "tools/**/*",
    "README.md",
    "docs/README.md",
    "docs/agile/sprint0/active-mvp-contract.json",
    "docs/agile/sprint0/baseline-manifest.json",
    "docs/**/*.md",
    "test/test_repo_paths.py",
    "test/contracts/__init__.py",
)

SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".svg", ".woff", ".woff2"}
SKIP_PARTS = {".git", "__pycache__", "node_modules", ".venv"}
# docs/archive/v045/** is evidence, not law (docs/archive/v045/README.md) — its
# pre-lock prose still cites the doc-move-era paths this gate exists to reject
# in *living* docs. Excluding it keeps the gate meaningful without editing history.
SKIP_DOCS_DIRS = {"archive"}
# The registry and its unit tests must name obsolete prefixes in order to reject them.
SKIP_NAMES = {"repo_paths.py", "test_repo_paths.py"}
# docs/05_adr/00NN-*.md are the VG-09 decision register migrated verbatim (append-only,
# docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md §1.12) — some entries quote
# doc-move-era paths inside historical "Evidence"/"Links" fields. That is archaeology,
# not a live citation; the ADR-M0-* namespace (new decisions) is not exempted.
_LEGACY_ADR_NAME = re.compile(r"^\d{4}-")


def iter_scan_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for pattern in SCAN_GLOBS:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            if set(path.parts) & SKIP_PARTS:
                continue
            if set(path.parts) & SKIP_DOCS_DIRS:
                continue
            if path.name in SKIP_NAMES:
                continue
            if ("adr" in path.parts or "05_adr" in path.parts) and _LEGACY_ADR_NAME.match(path.name):
                continue
            files.add(path)
    return sorted(files)


def check(root: Path) -> list[str]:
    errors: list[str] = []
    scanned = iter_scan_files(root)
    if not scanned:
        return [f"no files matched scan globs under {root}"]
    for path in scanned:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        matches = stale_path_matches(text)
        if matches:
            rel = path.relative_to(root) if path.is_relative_to(root) else path
            unique = ", ".join(sorted(set(matches)))
            errors.append(f"{rel}: stale path(s) {unique}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve() if args.root is not None else repo_root()
    errors = check(root)
    if errors:
        for error in errors:
            print(f"STALE PATH FAIL: {error}")
        return 1
    print(f"STALE PATH PASS: {len(iter_scan_files(root))} files scanned; no obsolete docs/ layout tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
