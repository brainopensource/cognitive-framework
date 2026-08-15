#!/usr/bin/env python3
"""Mechanical presence and safeguard audit for the Sprint 0 artifacts."""

from __future__ import annotations

import sys
from pathlib import Path


CHECKS = {
    Path("docs/v4/09_vanguard_decision_register_v040.md"): [
        "Append-only",
        "## 7. Sprint 0 adoption decisions",
        "reversal condition",
        "GTS-13C is the sole active programme plan",
    ],
    Path("docs/sprint0/system-architecture-icd.md"): [
        "domain <- ports <- kernel <- agency <- runtime -> adapters",
        "runtime/governance",
        "spike/",
        "slice/",
    ],
    Path("docs/sprint0/verification-threat-evaluation-plan.md"): [
        "## 3. Must-fail suite",
        "descriptor substitution",
        "verifier–deployment gap",
        "DEV",
        "SEALED",
    ],
    Path("docs/sprint0/active-mvp-contract.json"): [
        "the only merge-gating requirement-to-evidence map",
        "baseline_assignment_coverage",
        "merged_scope_evidence_coverage",
    ],
    Path(".github/pull_request_template.md"): [
        "valid Active MVP Contract `req_id`",
        "No production code imports `spike/` or `slice/`",
        "GTS-13C has not been used as a substitute",
        "Controlled bootstrap",
    ],
    Path("docs/sprint0/schema-archaeology/field-inventory.md"): [
        "Three real repository bugs traced",
        "Independent third-engineer reconstruction signed",
        "roleAtAction",
    ],
    Path("docs/sprint1/README.md"): [
        "CONDITIONAL GO",
        "REQ-SCHEMA-001..012",
        "No schema may be marked locked",
    ],
    Path("docs/sprint1/backlog.md"): [
        "S1-D1-001",
        "S1-D4-004",
        "S1-PL-001",
    ],
}


def main() -> int:
    failures: list[str] = []
    for path, phrases in CHECKS.items():
        if not path.is_file():
            failures.append(f"missing {path}")
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{path}: missing safeguard {phrase!r}")
    for failure in failures:
        print(f"GOVERNANCE FAIL: {failure}")
    if failures:
        return 1
    print(f"GOVERNANCE PASS: {len(CHECKS)} artifacts checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
