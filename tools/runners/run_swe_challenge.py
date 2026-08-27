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
from vanguard.packages.runtime.compose import TaskContext
from vanguard.packages.runtime.root import Runtime
from vanguard.packages.runtime.autonomous_grant import create_autonomous_grant
from vanguard.packages.runtime.governance.approvals import OperatorSigner
from vanguard.packages.adapters.models.openrouter import OpenRouterModel
from vanguard.packages.adapters.stores.blob_store import FileBlobStore


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
        
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        
        task = TaskContext(
            brief=challenge.brief,
            repo_path=scratch_dir,
            run_id=f"run-{challenge_id}",
            episode_id=f"episode-{challenge_id}",
            project_id="swe-challenge",
            max_turns=20,
        )
        
        seed_key = b"vanguard-autonomous-operator-seed-key"
        grant = create_autonomous_grant(
            scratch_dir,
            allowed_verbs=("fs.read", "fs.search", "patch.apply", "proc.exec"),
            max_turns=20,
            max_attempts=1,
            seed_key=seed_key,
        )
        signer = OperatorSigner(seed_key)
        model_obj = OpenRouterModel(model=model, stream=False, environ={"OPENROUTER_API_KEY": api_key})
        manifest_path = _REPO_ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"
        db_path = scratch_dir / ".vanguard" / "events.sqlite3"
        blob_path = scratch_dir / ".vanguard" / "blobs"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        blob_path.mkdir(parents=True, exist_ok=True)

        print(f"Running Vanguard engine with model {model}...")
        t0 = time.time()
        
        result = Runtime.execute_profiled(
            manifest_path,
            task,
            profile_id="product",
            model=model_obj,
            store_path=str(db_path),
            blobs=FileBlobStore(blob_path),
            interactive=True,
            approver=lambda challenge: signer.approve(challenge, reviewer=grant.reviewer),
            approval_key=signer.public_bytes,
        )
        
        elapsed = time.time() - t0
        
        # Parse result
        turns = 0
        tokens = 0
        cost = 0
        if result and getattr(result, "telemetry", None):
            turns = getattr(result.telemetry, "turns", 0)
            tokens = getattr(result.telemetry, "total_tokens", None) or 0
            cost = getattr(result.telemetry, "usd_micros", None) or 0

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


def run_verified_challenge(instance_id: str, model: str, keep_dir: bool) -> dict[str, Any]:
    """Run a real SWE-bench Verified instance."""
    verified_repo = _REPO_ROOT / "tools/005_SWE_VERIFIED_REPO" / instance_id
    if not verified_repo.exists():
        raise ValueError(f"Verified repo {verified_repo} does not exist.")
        
    scratch_dir = Path(tempfile.mkdtemp(prefix=f"vanguard_verified_{instance_id}_"))
    print(f"Setting up {instance_id} in {scratch_dir}...")
    
    try:
        # Copy public contents
        public_dir = verified_repo / "public"
        shutil.copytree(public_dir, scratch_dir, dirs_exist_ok=True)
        
        # Read context.md
        context_path = verified_repo / "context.md"
        brief = ""
        if context_path.exists():
            brief = context_path.read_text("utf-8")
            task_path = scratch_dir / "TASK.md"
            task_path.write_text(f"# {instance_id}\n\n{brief}\n", encoding="utf-8")
            
        # Init Git
        subprocess.run(["git", "init"], cwd=scratch_dir, capture_output=True, check=True)
        subprocess.run(["git", "add", "."], cwd=scratch_dir, capture_output=True, check=True)
        subprocess.run(
            ["git", "commit", "-m", "init"],
            cwd=scratch_dir,
            capture_output=True,
            check=True,
            env={**os.environ, "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@test.com", "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@test.com"}
        )
        
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        
        task = TaskContext(
            brief=brief if brief else f"Fix {instance_id}",
            repo_path=scratch_dir,
            run_id=f"run-{instance_id}",
            episode_id=f"episode-{instance_id}",
            project_id="swe-verified",
            max_turns=20,
        )
        
        seed_key = b"vanguard-autonomous-operator-seed-key"
        grant = create_autonomous_grant(
            scratch_dir,
            allowed_verbs=("fs.read", "fs.search", "patch.apply", "proc.exec"),
            max_turns=20,
            max_attempts=1,
            seed_key=seed_key,
        )
        signer = OperatorSigner(seed_key)
        model_obj = OpenRouterModel(model=model, stream=False, environ={"OPENROUTER_API_KEY": api_key})
        manifest_path = _REPO_ROOT / "vanguard/packages/agency/manifests/vg-code-default/manifest.json"
        db_path = scratch_dir / ".vanguard" / "events.sqlite3"
        blob_path = scratch_dir / ".vanguard" / "blobs"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        blob_path.mkdir(parents=True, exist_ok=True)

        print(f"Running Vanguard engine with model {model}...")
        t0 = time.time()
        
        result = Runtime.execute_profiled(
            manifest_path,
            task,
            profile_id="product",
            model=model_obj,
            store_path=str(db_path),
            blobs=FileBlobStore(blob_path),
            interactive=True,
            approver=lambda challenge: signer.approve(challenge, reviewer=grant.reviewer),
            approval_key=signer.public_bytes,
        )
        
        elapsed = time.time() - t0
        
        turns = 0
        tokens = 0
        cost = 0
        if result and getattr(result, "telemetry", None):
            turns = getattr(result.telemetry, "turns", 0)
            tokens = getattr(result.telemetry, "total_tokens", None) or 0
            cost = getattr(result.telemetry, "usd_micros", None) or 0

        # Evaluate oracle
        passed = False
        print("Evaluating oracle...")
        if instance_id == "pallets__flask-5014":
            oracle_code = """import unittest
from flask.blueprints import Blueprint

class TestFlask(unittest.TestCase):
    def test_blueprint_empty_name(self):
        with self.assertRaises(ValueError):
            Blueprint("", "test")
        
        # should work
        Blueprint("valid", "test")

if __name__ == "__main__":
    unittest.main()
"""
            oracle_path = scratch_dir / "oracle_test.py"
            oracle_path.write_text(oracle_code, encoding="utf-8")
            test_env = {**os.environ, "PYTHONPATH": f"{scratch_dir}/src:{scratch_dir}"}
            res = subprocess.run([sys.executable, "-m", "unittest", "oracle_test.py"], cwd=scratch_dir, capture_output=True, text=True, env=test_env)
            passed = (res.returncode == 0)
            if not passed:
                print("Oracle failure stderr:", res.stderr)
                print("Oracle failure stdout:", res.stdout)
        elif instance_id == "psf__requests-1142":
            oracle_code = """import unittest
from requests.models import PreparedRequest

class TestRequests(unittest.TestCase):
    def test_get_content_length(self):
        p = PreparedRequest()
        p.prepare_content_length('')
        self.assertNotIn("Content-Length", p.headers)

if __name__ == "__main__":
    unittest.main()
"""
            oracle_path = scratch_dir / "oracle_test.py"
            oracle_path.write_text(oracle_code, encoding="utf-8")
            test_env = {**os.environ, "PYTHONPATH": f"{scratch_dir}/src:{scratch_dir}"}
            res = subprocess.run([sys.executable, "-m", "unittest", "oracle_test.py"], cwd=scratch_dir, capture_output=True, text=True, env=test_env)
            passed = (res.returncode == 0)
            if not passed:
                print("Oracle failure stderr:", res.stderr)
                print("Oracle failure stdout:", res.stdout)
        else:
            print(f"No oracle defined for {instance_id}")

        diff_size = get_diff_size(scratch_dir)
        print("\n=== GIT DIFF ===")
        res_diff = subprocess.run(["git", "diff"], cwd=scratch_dir, capture_output=True, text=True)
        print(res_diff.stdout)
        
        print("\n=== TELEMETRY ===")
        if result and getattr(result, "telemetry", None):
            print(result.telemetry)
            
        return {
            "challenge": instance_id,
            "tier": "VERIFIED",
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
    parser.add_argument("--verified", type=str, default=None, help="Run a real SWE-bench Verified instance from tools/005_SWE_VERIFIED_REPO (e.g. pallets__flask-5014, psf__requests-1142)")
    parser.add_argument("--model", type=str, default="openrouter/free", help="Model to use (default: openrouter/free)")
    parser.add_argument("--keep-dir", action="store_true", help="Keep temporary scratch directories")
    args = parser.parse_args()

    # Load API key
    res = load_api_key(_REPO_ROOT)
    if res.ok and res.value:
        os.environ["OPENROUTER_API_KEY"] = res.value
    else:
        print(f"Warning: Failed to load OPENROUTER_API_KEY from .env: {res.error}", file=sys.stderr)

    results = []
    
    if args.verified:
        print(f"\n{'=' * 60}\nRunning VERIFIED {args.verified}...\n{'=' * 60}")
        res_data = run_verified_challenge(args.verified, args.model, args.keep_dir)
        results.append(res_data)
    else:
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
            print("Error: Must specify either --challenge, --tiers, or --verified", file=sys.stderr)
            return 1
    
        if not to_run:
            print("No challenges matched criteria.", file=sys.stderr)
            return 0
    
        print(f"Running {len(to_run)} challenges...")
        
        for cid in to_run:
            print(f"\n{'=' * 60}\nRunning {cid}...\n{'=' * 60}")
            res_data = run_challenge(cid, args.model, args.keep_dir)
            results.append(res_data)

    # Print summary report
    print("\n\n" + "=" * 80)
    print(f"{'Challenge':<35} | {'Tier':<8} | {'Score':<6} | {'Time(s)':<8} | {'Turns':<6} | {'Tokens':<8} | {'Cost(µ$)':<9} | {'Diff':<6}")
    print("-" * 80)
    for r in results:
        score = "PASS" if r["passed"] else "FAIL"
        print(f"{r['challenge']:<35} | {str(r['tier']):<8} | {score:<6} | {r['elapsed']:<8.1f} | {r['turns']:<6} | {r['tokens']:<8} | {r['cost_micros']:<9} | {r['diff_size']:<6}")
    
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
