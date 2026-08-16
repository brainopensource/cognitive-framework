#!/usr/bin/env python3
"""Mechanical presence and safeguard audit for the Sprint 0 artifacts."""

from __future__ import annotations

import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import docs_agile, docs_main_v4, repo_path, repo_root


def _checks() -> dict[Path, list[str]]:
    return {
        docs_main_v4("09_vanguard_decision_register_v040.md"): [
            "Append-only",
            "reversal condition",
            "GTS-13C is the sole active programme plan",
        ],
        repo_path(".github", "pull_request_template.md"): [
            "No production code imports `spike/` or `slice/`",
            "Controlled bootstrap",
        ],
    }


def main() -> int:
    failures: list[str] = []
    repo_root()
    checks = _checks()
    for path, phrases in checks.items():
        if not path.is_file():
            failures.append(f"missing {path.relative_to(repo_root()) if path.is_relative_to(repo_root()) else path}")
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root()) if path.is_relative_to(repo_root()) else path
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{rel}: missing safeguard {phrase!r}")
    for failure in failures:
        print(f"GOVERNANCE FAIL: {failure}")
    if failures:
        return 1
    print(f"GOVERNANCE PASS: {len(checks)} artifacts checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
