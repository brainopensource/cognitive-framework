#!/usr/bin/env python3
"""AUTO-GENERATED: SWE Challenge Runner

Executes SWE challenges against the Vanguard coding engine.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from benchmarks.swe_bench.challenges import CHALLENGES
from vanguard.packages.adapters.models.env_loader import load_api_key


def setup_challenge(challenge_id: str, scratch_dir: Path) -> None:
    """Set up the challenge files and initialize a git repo."""
    challenge = CHALLENGES[challenge_id]
    
    # Write files
    for filepath, content in challenge.files.items():
        full_path = scratch_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")
        
    # Write TASK.md
    task_path = scratch_dir / "TASK.md"
    task_path.write_text(f"# {challenge.title}\n\n{challenge.brief}\n", encoding="utf-8")
    
    # Initialize Git to track diffs
    subprocess.run(["git", "init"], cwd=scratch_dir, capture_output=True, check=True)
    subprocess.run(["git", "add", "."], cwd=scratch_dir, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=scratch_dir,
        capture_output=True,
        check=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@test.com", "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@test.com"}
    )


def evaluate_oracle(challenge_id: str, scratch_dir: Path) -> bool:
    """Run the oracle test code to evaluate the challenge."""
    challenge = CHALLENGES[challenge_id]
    oracle_path = scratch_dir / "oracle_test.py"
    oracle_path.write_text(challenge.oracle_code, encoding="utf-8")
    
    # Run the oracle test
    res = subprocess.run(
        [sys.executable, "-m", "unittest", "oracle_test.py"],
        cwd=scratch_dir,
        capture_output=True,
        text=True,
    )
    return res.returncode == 0


def get_diff_size(scratch_dir: Path) -> int:
    """Get the size of the git diff in lines."""
    res = subprocess.run(
        ["git", "diff"],
        cwd=scratch_dir,
        capture_output=True,
        text=True,
        check=True
    )
    diff = res.stdout
    return len(diff.splitlines())


def run_challenge(challenge_id: str, model: str, keep_dir: bool) -> dict[str, Any]:
    """Run a single SWE challenge."""
    challenge = CHALLENGES[challenge_id]
    scratch_dir = Path(tempfile.mkdtemp(prefix=f"vanguard_swe_{challenge_id}_"))
    print(f"Setting up {challenge_id} in {scratch_dir}...")
    
    try:
        setup_challenge(challenge_id, scratch_dir)
        
        # Prepare request for entrypoint
        req = {
            "command": "code",
            "brief": f"Please complete the task defined in TASK.md.",
            "workspace": str(scratch_dir),
            "plannerModel": model,
            "profile": "product",
            "interactive": False,
        }
        
        print(f"Running Vanguard engine with model {model}...")
        t0 = time.time()
        
        proc = subprocess.Popen(
            [sys.executable, "-m", "vanguard.packages.runtime.entrypoint", "--stdin-json"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True,
            cwd=_REPO_ROOT
        )
        out, _ = proc.communicate(json.dumps(req) + "\n")
        
        elapsed = time.time() - t0
        
        # Parse result
        turns = 0
        tokens = 0
        cost = 0
        if out:
            try:
                result_data = json.loads(out.strip().splitlines()[-1])
                res = result_data.get("result", {})
                turns = res.get("turns", 0)
                tokens = res.get("promptTokens") or 0
                tokens += res.get("completionTokens") or 0
                cost = res.get("spentUsdMicros") or 0
            except Exception as e:
                print(f"Failed to parse output: {e}", file=sys.stderr)

        print("Evaluating oracle...")
        passed = evaluate_oracle(challenge_id, scratch_dir)
        diff_size = get_diff_size(scratch_dir)
        
        return {
            "challenge": challenge_id,
            "tier": challenge.tier,
            "passed": passed,
            "elapsed": elapsed,
            "turns": turns,
            "tokens": tokens,
            "cost_micros": cost,
            "diff_size": diff_size,
            "scratch_dir": str(scratch_dir),
        }
    finally:
        if not keep_dir:
            shutil.rmtree(scratch_dir, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run SWE challenges against Vanguard.")
    parser.add_argument("--challenge", type=str, help="Specific challenge ID to run")
    parser.add_argument("--tiers", type=str, help="Comma-separated list of tiers to run (e.g. 1,2,3)")
    parser.add_argument("--model", type=str, default="openrouter/free", help="Model to use (default: openrouter/free)")
    parser.add_argument("--keep-dir", action="store_true", help="Keep temporary scratch directories")
    args = parser.parse_args()

    # Load API key
    res = load_api_key(_REPO_ROOT)
    if res.ok and res.value:
        os.environ["OPENROUTER_API_KEY"] = res.value
    else:
        print(f"Warning: Failed to load OPENROUTER_API_KEY from .env: {res.error}", file=sys.stderr)

    # Determine which challenges to run
    to_run = []
    if args.challenge:
        if args.challenge not in CHALLENGES:
            print(f"Error: Unknown challenge {args.challenge}", file=sys.stderr)
            return 1
        to_run.append(args.challenge)
    elif args.tiers:
        try:
            tiers = {int(t.strip()) for t in args.tiers.split(",")}
        except ValueError:
            print("Error: --tiers must be a comma-separated list of integers", file=sys.stderr)
            return 1
        to_run = [c for c, obj in CHALLENGES.items() if obj.tier in tiers]
    else:
        print("Error: Must specify either --challenge or --tiers", file=sys.stderr)
        return 1

    if not to_run:
        print("No challenges matched criteria.", file=sys.stderr)
        return 0

    print(f"Running {len(to_run)} challenges...")
    
    results = []
    for cid in to_run:
        print(f"\n{'=' * 60}\nRunning {cid}...\n{'=' * 60}")
        res_data = run_challenge(cid, args.model, args.keep_dir)
        results.append(res_data)

    # Print summary report
    print("\n\n" + "=" * 80)
    print(f"{'Challenge':<35} | {'Tier':<5} | {'Score':<6} | {'Time(s)':<8} | {'Turns':<6} | {'Tokens':<8} | {'Cost(µ$)':<9} | {'Diff':<6}")
    print("-" * 80)
    for r in results:
        score = "PASS" if r["passed"] else "FAIL"
        print(f"{r['challenge']:<35} | {r['tier']:<5} | {score:<6} | {r['elapsed']:<8.1f} | {r['turns']:<6} | {r['tokens']:<8} | {r['cost_micros']:<9} | {r['diff_size']:<6}")
    
    passed_count = sum(1 for r in results if r["passed"])
    print("=" * 80)
    print(f"Total Passed: {passed_count}/{len(results)} ({(passed_count/len(results))*100:.1f}%)")
    
    if args.keep_dir:
        print("\nScratch directories kept:")
        for r in results:
            print(f"  {r['challenge']}: {r['scratch_dir']}")

    return 0 if passed_count == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
