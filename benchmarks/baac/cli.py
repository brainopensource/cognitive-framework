"""BaaC Command-Line Interface.

Usage:
  python3 -m benchmarks.baac.cli catalog [--tier TIER] [--scope SCOPE]
  python3 -m benchmarks.baac.cli verify [--tier TIER] [--single NAME]
  python3 -m benchmarks.baac.cli generate-manifest [--tier TIER] [--single NAME]
  python3 -m benchmarks.baac.cli run [--preset PRESET] [--mode {lam,live,ollama}] [--model MODEL] [--tier TIER] [--single NAME]
  python3 -m benchmarks.baac.cli cycle [--preset PRESET] [--mode {lam,live,ollama}] [--model MODEL] [--tier TIER]
  python3 -m benchmarks.baac.cli matrix [--preset PRESET] [--tiers TIERS]
  python3 -m benchmarks.baac.cli clean
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
    clean_scratch_directories,
    generate_challenge_manifest,
    reset_environment,
    verify_challenge_zero_state,
)
from .membership import enumerate_baac_challenges

ROOT = Path(__file__).resolve().parents[2]
CHALLENGES_DIR = ROOT / "benchmarks" / "baac" / "challenges"
RUNS_DIR = ROOT / "benchmarks" / "baac" / "runs"


def discover_challenges(
    tier: Optional[str] = None,
    single: Optional[str] = None,
    scope: Optional[str] = None,
) -> List[Path]:
    """Find schema-valid challenge directories matching tier, single, or scope."""
    challenges = list(enumerate_baac_challenges(CHALLENGES_DIR))
    if tier and tier.lower() != "all":
        challenges = [
            path for path in challenges
            if path.parent.name.lower() == tier.lower()
            or path.parent.name.lower().endswith(tier.lower())
        ]
    if single:
        challenges = [
            path for path in challenges
            if path.name == single or single in path.name
        ]
    if scope:
        challenges = [
            path for path in challenges
            if scope.lower() in path.name.lower()
        ]
    return challenges


def cmd_catalog(args: argparse.Namespace) -> int:
    """List all available standardized challenges."""
    challenges = discover_challenges(tier=args.tier, scope=args.scope)
    print("=" * 110)
    print(f"BaaC STANDARDIZED CHALLENGE CATALOG ({len(challenges)} challenges found)")
    print("=" * 110)
    print(f"{'Tier':<8} | {'Scope':<10} | {'Context':<8} | {'Challenge ID':<45} | {'Tags'}")
    print("-" * 110)

    runner = BaaCRunner()
    for c in challenges:
        meta = runner.load_challenge_metadata(c)
        tags_str = ", ".join(meta.tags[:3])
        print(f"{meta.tier:<8} | {meta.scope:<10} | {meta.context_bracket:<8} | {meta.id:<45} | {tags_str}")

    print("=" * 110)
    return 0


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
        print(f"\nALL {len(challenges)} CHALLENGES PASSED ZERO-STATE VERIFICATION.")
        return 0
    else:
        print(f"\nFAILED: {failures} challenge(s) drifted from committed manifest.")
        return 1


def cmd_generate_manifest(args: argparse.Namespace) -> int:
    """Generate and write manifest.sha256 for challenges."""
    challenges = discover_challenges(tier=args.tier, single=args.single)
    if not challenges:
        print(f"No challenges found in {CHALLENGES_DIR}")
        return 1

    for c in challenges:
        m_path = generate_challenge_manifest(c)
        print(f"Generated manifest: {c.parent.name}/{c.name} -> {m_path.name}")

    print(f"\nGenerated manifests for {len(challenges)} challenge(s).")
    return 0


def cmd_clean(args: argparse.Namespace) -> int:
    """Purge temporary scratch workspaces, pycache bytecode, and WAL state."""
    res = reset_environment(ROOT / "benchmarks" / "baac")
    print(f"BaaC Reset Clean complete:")
    print(f"  - Scratch workspaces cleaned: {res['scratch_workspaces_cleaned']}")
    print(f"  - Bytecode artifacts purged: {res['bytecode_artifacts_purged']}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run BaaC benchmarks."""
    challenges = discover_challenges(tier=args.tier, single=args.single)
    if not challenges:
        print(f"No challenges matched filters (tier={args.tier}, single={args.single})")
        return 1

    model_display = args.model or ("lam-mock" if args.mode == "lam" else "deepseek/deepseek-v4-flash-0731")
    run_id = f"baac-{args.preset}-{args.mode}-{int(time.time())}"
    budget_cfg = BudgetCapConfig(
        max_requests=args.max_requests,
        max_cost_usd=args.budget,
        max_turns=args.max_turns,
        allowed_models=None,
    )

    runner = BaaCRunner(
        preset=args.preset,
        model_name=args.model,
        mode=args.mode,
        budget_config=budget_cfg,
        run_id=run_id,
        extra_metadata={"cli_args": vars(args)},
    )

    print("=" * 110)
    print(f"BaaC SCIENTIFIC BENCHMARK LAUNCHED: {run_id}")
    print(f"Preset: {args.preset} | Mode: {args.mode} | Subject Model: {runner.model_name}")
    print(f"Challenges to execute: {len(challenges)}")
    print("=" * 110)

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
        print(
            f"    Result: [{res.status}] in {res.turns} turns | "
            f"Attribution: {res.attribution} | "
            f"Cost: ${res.cost_usd:.5f} | "
            f"Time: {res.duration_seconds:.2f}s"
        )

    print("\n" + "=" * 110)
    print(report.to_markdown_table())
    print("=" * 110)

    # Save summary reports
    report_file = runner.run_dir / "report.json"
    report_file.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    report_md = runner.run_dir / "report.md"
    report_md.write_text(report.to_markdown_table(), encoding="utf-8")
    print(f"\nReport artifacts saved to {runner.run_dir}")

    return 0 if report.pass_count == report.total_count else 1


def cmd_cycle(args: argparse.Namespace) -> int:
    """Run full BaaC Cycle: verify -> run -> reset -> verify."""
    print(">>> STAGE 1: Pre-run Zero-State Manifest Verification")
    v1 = cmd_verify(args)
    if v1 != 0:
        print("Cycle aborted: challenge source has drifted or is invalid.")
        return v1

    print("\n>>> STAGE 2: Execute Benchmark Harness & Ground-Truth Oracle")
    r_code = cmd_run(args)

    print("\n>>> STAGE 3: Post-run Ephemeral Workspace Reset")
    cmd_clean(args)

    print("\n>>> STAGE 4: Post-reset Zero-State Invariant Verification")
    v2 = cmd_verify(args)
    if v2 != 0:
        print("Cycle post-verification failed: workspace mutation leaked into pristine sources!")
        return 1

    print("\nBaaC CYCLE COMPLETE: 100% Hermetic, Zero-Drift, and Scientifically Verified.")
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
    parser = argparse.ArgumentParser(description="Vanguard Benchmark as Code (BaaC) 2.0 CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # catalog
    p_cat = subparsers.add_parser("catalog", help="List all available challenges")
    p_cat.add_argument("--tier", default="all", help="Tier filter (tier-1, tier-2, etc.)")
    p_cat.add_argument("--scope", default=None, help="Scope filter (single, multi, greenfield, etc.)")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify zero-state manifests")
    p_verify.add_argument("--tier", default="all", help="Tier filter (tier-1, tier-2, all)")
    p_verify.add_argument("--single", default=None, help="Single challenge name")

    # generate-manifest
    p_gen = subparsers.add_parser("generate-manifest", help="Generate SHA256 manifests")
    p_gen.add_argument("--tier", default="all")
    p_gen.add_argument("--single", default=None)

    # clean
    p_clean = subparsers.add_parser("clean", help="Clean scratch workspaces and bytecode caches")

    # run
    p_run = subparsers.add_parser("run", help="Run BaaC challenges")
    p_run.add_argument("--preset", default="vg-1-forge", help="Agent harness preset")
    p_run.add_argument("--mode", default="lam", choices=["lam", "live", "ollama"], help="Execution mode (default: lam)")
    p_run.add_argument("--model", default=None, help="Model identifier (e.g. anthropic/claude-3.7-sonnet, lam-mock)")
    p_run.add_argument("--tier", default="all", help="Challenge tier (tier-1 to tier-6, all)")
    p_run.add_argument("--single", default=None, help="Single challenge name")
    p_run.add_argument("--max-turns", type=int, default=10, help="Max turns per challenge")
    p_run.add_argument("--max-requests", type=int, default=500, help="Max requests cap")
    p_run.add_argument("--budget", type=float, default=0.10, help="Max USD budget cap")
    p_run.add_argument("--keep-scratch", action="store_true", help="Do not delete scratch workspace on exit")

    # cycle
    p_cycle = subparsers.add_parser("cycle", help="Run full scientific cycle: verify -> run -> clean -> verify")
    p_cycle.add_argument("--preset", default="vg-1-forge")
    p_cycle.add_argument("--mode", default="lam", choices=["lam", "live", "ollama"])
    p_cycle.add_argument("--model", default=None)
    p_cycle.add_argument("--tier", default="all")
    p_cycle.add_argument("--single", default=None)
    p_cycle.add_argument("--max-turns", type=int, default=10)
    p_cycle.add_argument("--max-requests", type=int, default=500)
    p_cycle.add_argument("--budget", type=float, default=0.10)
    p_cycle.add_argument("--keep-scratch", action="store_true")

    # report
    p_report = subparsers.add_parser("report", help="Display run reports")
    p_report.add_argument("--run-id", default=None, help="Specific run ID to display")

    args = parser.parse_args()

    dispatch = {
        "catalog": cmd_catalog,
        "verify": cmd_verify,
        "generate-manifest": cmd_generate_manifest,
        "clean": cmd_clean,
        "run": cmd_run,
        "cycle": cmd_cycle,
        "report": cmd_report,
    }

    sys.exit(dispatch[args.command](args))


if __name__ == "__main__":
    main()
