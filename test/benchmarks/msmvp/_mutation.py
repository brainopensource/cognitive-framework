"""The DIR-5.5 / §7.4 mutation-proof engine, shared by every probe table.

`docs/execution/main/mvp_delivery_protocol.md` §7.4: a test that passes both
with and without the guard it claims to prove is evidence of nothing. For each
negative control, disable exactly one guard, run the focused suite, and require
it to red **on the control that names that guard**; then restore and confirm
green.

This module performs that procedure. It edits production source in place and
restores the original bytes in a `finally`, so it repairs nothing and leaves
nothing changed. It is a review instrument for an acceptor, not a test, which
is why it lives under `test/benchmarks/` rather than beside the controls it probes.

A probe table declares `Probe` rows; `main` runs them and exits non-zero if any
guard's control stayed green -- which §6 records as a **rejection**, not a nit.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = REPO_ROOT / "vanguard/packages/runtime/workspace.py"
CHILD_RUNTIME = REPO_ROOT / "vanguard/packages/runtime/child_runtime.py"
SESSION = REPO_ROOT / "vanguard/packages/runtime/session.py"
ENTRYPOINT = REPO_ROOT / "vanguard/packages/runtime/entrypoint.py"
ENGINE = REPO_ROOT / "vanguard/packages/agency/episode/engine.py"


@dataclass(frozen=True)
class Probe:
    """One guard, the edit that disables it, and the control that must red."""

    key: str
    clause: str
    guard: str
    edits: tuple[tuple[Path, str, str], ...]
    expects: tuple[str, ...]
    """Substrings; at least one failing control name must contain one."""


def run_suite(suite: tuple[str, ...]) -> tuple[bool, tuple[str, ...], str]:
    """Returns (green, failing control names, last line of output)."""
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", *suite, "-v"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=1800,
    )
    # The summary block is the reliable source: in verbose mode a docstring
    # line separates the test name from its `... FAIL`, so the per-test lines
    # cannot be matched in one pass.
    failures = tuple(sorted(set(re.findall(
        r"^(?:FAIL|ERROR): (test_\w+)", proc.stderr, re.MULTILINE))))
    tail = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else ""
    return proc.returncode == 0, failures, tail


def run_probe(probe: Probe, suite: tuple[str, ...]) -> dict[str, object]:
    originals = {path: path.read_text(encoding="utf-8") for path, _, _ in probe.edits}
    try:
        for path, old, new in probe.edits:
            text = path.read_text(encoding="utf-8")
            if text.count(old) != 1:
                return {
                    "probe": probe.key, "clause": probe.clause, "guard": probe.guard,
                    "verdict": "PROBE_STALE",
                    "detail": f"guard text not uniquely present in {path.name} "
                              f"({text.count(old)} occurrences); the probe, not "
                              "the guard, is out of date",
                    "failing_controls": [],
                }
            path.write_text(text.replace(old, new), encoding="utf-8")
        green, failures, tail = run_suite(suite)
    finally:
        for path, text in originals.items():
            path.write_text(text, encoding="utf-8")

    named = tuple(f for f in failures
                  if any(token in f.lower() for token in probe.expects))
    if green:
        verdict, detail = "REJECTION", "suite stayed GREEN with the guard disabled"
    elif named:
        verdict = "RED_ON_NAMING_CONTROL"
        detail = f"{len(failures)} control(s) red; naming: {', '.join(named)}"
    else:
        verdict = "RED_UNNAMED"
        detail = (f"{len(failures)} control(s) red, none naming the guard: "
                  f"{', '.join(failures)}")
    return {
        "probe": probe.key, "clause": probe.clause, "guard": probe.guard,
        "verdict": verdict, "detail": detail,
        "failing_controls": list(failures), "suite_tail": tail,
    }


def main(probes: tuple[Probe, ...], suite: tuple[str, ...],
         argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="DIR-5.5 mutation probes")
    parser.add_argument("--probe", nargs="*", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    baseline_green, baseline_failures, _ = run_suite(suite)
    if not baseline_green:
        print("BASELINE IS NOT GREEN; probes would be meaningless. "
              f"Failing: {baseline_failures}", file=sys.stderr)
        return 2

    selected = [p for p in probes if not args.probe or p.key in args.probe]
    results = [run_probe(probe, suite) for probe in selected]

    restored_green, restored_failures, _ = run_suite(suite)

    if args.json:
        print(json.dumps({
            "baseline": "GREEN",
            "restored": "GREEN" if restored_green else f"RED {restored_failures}",
            "probes": results,
        }, indent=2))
    else:
        print("baseline: GREEN\n")
        for row in results:
            print(f"{row['probe']:<3}{str(row['clause']):<40}{row['verdict']}")
            print(f"     guard: {row['guard']}")
            print(f"     -> {row['detail']}\n")
        print(f"restored: {'GREEN' if restored_green else f'RED {restored_failures}'}")
    bad = [r for r in results if r["verdict"] != "RED_ON_NAMING_CONTROL"]
    return 1 if bad or not restored_green else 0
