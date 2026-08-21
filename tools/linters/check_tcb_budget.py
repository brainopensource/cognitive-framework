#!/usr/bin/env python3
"""Measure the policy-kernel source inventory and alarm on unreviewed growth."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import kernel_tcb_budget, repo_root


def logical_lines(path: Path) -> int:
    """Count stable physical logic lines; blanks and comment-only lines do not count."""

    return sum(
        bool(line.strip()) and not line.lstrip().startswith("#")
        for line in path.read_text(encoding="utf-8").splitlines()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--budget", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve() if args.root is not None else repo_root()
    if args.budget is None:
        budget_path = kernel_tcb_budget()
    else:
        budget_path = args.budget if args.budget.is_absolute() else root / args.budget
    if not budget_path.exists() and (root / "docs/agile/sprint2/kernel-tcb-budget.json").exists():
        budget_path = root / "docs/agile/sprint2/kernel-tcb-budget.json"

    try:
        budget = json.loads(budget_path.read_text(encoding="utf-8"))
        source_root = root / budget["source_root"]
        baseline = int(budget["baseline_logical_loc"])
        alarm_delta = int(budget["alarm_delta_lines"])
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"TCB FAIL: invalid budget: {exc}")
        return 2

    files = sorted(source_root.glob("*.py"))
    if not files:
        print(f"TCB FAIL: no kernel sources under {source_root}")
        return 2
    inventory = {str(path.relative_to(root)): logical_lines(path) for path in files}
    current = sum(inventory.values())
    threshold = baseline + alarm_delta
    receipt = {
        "alarm_delta_lines": alarm_delta,
        "baseline_logical_loc": baseline,
        "current_logical_loc": current,
        "files": inventory,
        "threshold": threshold,
    }
    print(json.dumps(receipt, sort_keys=True))
    if current > threshold:
        print(f"TCB ALARM: kernel grew to {current} logical lines; reviewed threshold is {threshold}")
        return 1
    print(f"TCB PASS: {current} logical lines across {len(files)} files (alarm above {threshold})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
