"""BaaC Command-Line Interface.

Usage:
  python3 -m benchmarks.baac.cli verify [--tier TIER]
  python3 -m benchmarks.baac.cli run [--preset PRESET] [--mode {lam,live}] [--tier TIER] [--single NAME]
  python3 -m benchmarks.baac.cli reset
  python3 -m benchmarks.baac.cli cycle [--preset PRESET] [--mode {lam,live}]
  python3 -m benchmarks.baac.cli report [--run-id RUN_ID]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time
from typing import List, Optional

from .lib import (
    BaaCReport,
    BaaCRunner,
    BudgetCapConfig,
    generate_challenge_manifest,
    verify_challenge_zero_state,
)

ROOT = Path(__file__).resolve().parents[2]
CHALLENGES_DIR = ROOT / "benchmarks" / "baac" / "challenges"
RUNS_DIR = ROOT / "benchmarks" / "baac" / "runs"


def discover_challenges(tier: Optional[str] = None, single: Optional[str] = None) -> List[Path]:
    """Find challenge directories matching tier/single filters."""
    challenges: List[Path] = []
    if not CHALLENGES_DIR.exists():
        return challenges

    tier_dirs = [d for d in CHALLENGES_DIR.iterdir() if d.is_dir()]
    if tier and tier.lower() != "all":
        tier_dirs = [d for d in tier_dirs if d.name.lower() == tier.lower()]

    for t_dir in sorted(tier_dirs):
        for c_dir in sorted(t_dir.iterdir()):
            if c_dir.is_dir() and (c_dir / "TASK.md").is_file():
                if single and c_dir.name != single:
                    continue
                challenges.append(c_dir)

    return challenges


def cmd_verify(args: argparse.Namespace) -> int:
    """Verify zero-state against committed sha256 manifests."""
    challenges = discover_challenges(tier=args.tier, single=args.single)
    if not challenges:
        print(f"No challenges found in {CHALLENGES_DIR}")
        return 1

    print(f"Verifying zero-state for {len(challenges)} challenge(s)...")
    failures = 0

    for c in challenges:
        ok, drifts = verify_challenge_zero_state(c)
        if ok:
            print(f"  [OK] {c.parent.name}/{c.name} (Zero-state clean)")
        else:
            failures += 1
            print(f"  [FAIL] {c.parent.name}/{c.name}")
            for d in drifts:
                print(f"         - {d}")

    if failures == 0:
        print("\nALL CHALLENGES PASSED ZERO-STATE VERIFICATION.")
        return 0
    else:
        print(f"\nFAILED: {failures} challenge(s) drifted from committed manifest.")
        return 1


def cmd_reset(args: argparse.Namespace) -> int:
    """Clean all temporary scratch directories and reset challenges."""
    import shutil
    import tempfile
    
    # Clean temporary scratch dirs matching baac-scratch-*
    tmp = Path(tempfile.gettempdir())
    cleaned = 0
    for p in tmp.glob("baac-scratch-*"):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
            cleaned += 1

    print(f"BaaC Reset complete: cleaned {cleaned} scratch workspace(s).")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run BaaC benchmarks."""
    challenges = discover_challenges(tier=args.tier, single=args.single)
    if not challenges:
        print(f"No challenges matched filters (tier={args.tier}, single={args.single})")
        return 1

    run_id = f"baac-{args.preset}-{args.mode}-{int(time.time())}"
    budget_cfg = BudgetCapConfig(
        max_requests=args.max_requests,
        max_cost_usd=args.budget,
        max_turns=args.max_turns,
    )

    runner = BaaCRunner(
        preset=args.preset,
        model_name=args.model,
        mode=args.mode,
        budget_config=budget_cfg,
        run_id=run_id,
    )

    print("=" * 100)
    print(f"BaaC RUN LAUNCHED: {run_id}")
    print(f"Preset: {args.preset} | Mode: {args.mode} | Model: {runner.model_name}")
    print(f"Challenges to execute: {len(challenges)}")
    print("=" * 100)

    report = BaaCReport(
        run_id=run_id,
        preset=args.preset,
        model=runner.model_name,
        mode=args.mode,
    )

    for c in challenges:
        print(f"\n>>> Executing [{c.parent.name}] {c.name}...")
        res = runner.run_challenge(c, keep_scratch=args.keep_scratch)
        report.results.append(res)
        print(f"    Result: [{res.status}] in {res.turns} turns | Attribution: {res.attribution} | Cost: ${res.cost_usd:.5f} | Time: {res.duration_seconds:.2f}s")

    print("\n" + "=" * 100)
    print(report.to_markdown_table())
    print("=" * 100)

    # Save summary report
    report_file = runner.run_dir / "report.json"
    report_file.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    report_md = runner.run_dir / "report.md"
    report_md.write_text(report.to_markdown_table(), encoding="utf-8")
    print(f"\nArtifacts saved to {runner.run_dir}")

    return 0 if report.pass_count == report.total_count else 1


def cmd_cycle(args: argparse.Namespace) -> int:
    """Run full BaaC Cycle: verify -> run -> reset -> verify."""
    print(">>> STAGE 1: Pre-run Zero-State Verification")
    v1 = cmd_verify(args)
    if v1 != 0:
        print("Cycle aborted: challenge source has drifted.")
        return v1

    print("\n>>> STAGE 2: Execute Benchmark Harness & External Oracle")
    r_code = cmd_run(args)

    print("\n>>> STAGE 3: Post-run Ephemeral Workspace Reset")
    cmd_reset(args)

    print("\n>>> STAGE 4: Post-reset Zero-State Invariant Verification")
    v2 = cmd_verify(args)
    if v2 != 0:
        print("Cycle post-verification failed: workspace mutation leaked into pristine sources!")
        return 1

    print("\nBaaC CYCLE COMPLETE: 100% Hermetic and Zero-Drift Verified.")
    return r_code


def cmd_report(args: argparse.Namespace) -> int:
    """Display latest or specific BaaC run report."""
    if args.run_id:
        target_dir = RUNS_DIR / args.run_id
    else:
        runs = sorted([d for d in RUNS_DIR.iterdir() if d.is_dir()])
        if not runs:
            print("No BaaC runs found in", RUNS_DIR)
            return 1
        target_dir = runs[-1]

    report_file = target_dir / "report.json"
    if not report_file.is_file():
        print(f"Missing report.json in {target_dir}")
        return 1

    data = json.loads(report_file.read_text(encoding="utf-8"))
    print(json.dumps(data, indent=2))
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Vanguard Benchmarking as Code (BaaC) CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify zero-state manifests")
    p_verify.add_argument("--tier", default="all", help="Challenge tier filter (easy, medium, hard, greenfield, all)")
    p_verify.add_argument("--single", default=None, help="Single challenge name")

    # reset
    p_reset = subparsers.add_parser("reset", help="Clean scratch workspaces")

    # run
    p_run = subparsers.add_parser("run", help="Run BaaC challenges")
    p_run.add_argument("--preset", default="vg-1-forge", choices=["vg-1-forge", "vg-code-max", "vg-code-max-v2", "vg-herbs", "vg-hermes"])
    p_run.add_argument("--mode", default="lam", choices=["lam", "live"], help="Execution mode (default: lam)")
    p_run.add_argument("--model", default=None, help="Model identifier (defaults to centralized policy)")
    p_run.add_argument("--tier", default="all", help="Challenge tier (easy, medium, hard, greenfield, all)")
    p_run.add_argument("--single", default=None, help="Single challenge name")
    p_run.add_argument("--max-turns", type=int, default=8, help="Max turns per challenge")
    p_run.add_argument("--max-requests", type=int, default=300, help="Max requests cap")
    p_run.add_argument("--budget", type=float, default=0.10, help="Max USD budget cap")
    p_run.add_argument("--keep-scratch", action="store_true", help="Do not delete scratch workspace on exit")

    # cycle
    p_cycle = subparsers.add_parser("cycle", help="Run full cycle: verify -> run -> reset -> verify")
    p_cycle.add_argument("--preset", default="vg-1-forge", choices=["vg-1-forge", "vg-code-max", "vg-code-max-v2", "vg-herbs", "vg-hermes"])
    p_cycle.add_argument("--mode", default="lam", choices=["lam", "live"])
    p_cycle.add_argument("--model", default=None)
    p_cycle.add_argument("--tier", default="all")
    p_cycle.add_argument("--single", default=None)
    p_cycle.add_argument("--max-turns", type=int, default=8)
    p_cycle.add_argument("--max-requests", type=int, default=300)
    p_cycle.add_argument("--budget", type=float, default=0.10)
    p_cycle.add_argument("--keep-scratch", action="store_true")

    # report
    p_report = subparsers.add_parser("report", help="Display run reports")
    p_report.add_argument("--run-id", default=None, help="Specific run ID to display")

    args = parser.parse_args()

    dispatch = {
        "verify": cmd_verify,
        "reset": cmd_reset,
        "run": cmd_run,
        "cycle": cmd_cycle,
        "report": cmd_report,
    }

    sys.exit(dispatch[args.command](args))


if __name__ == "__main__":
    main()
