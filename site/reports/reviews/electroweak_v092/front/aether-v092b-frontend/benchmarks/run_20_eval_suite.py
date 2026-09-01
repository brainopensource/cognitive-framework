"""20-Challenge Multi-Tier Benchmark Runner for DeepSeek V4 Flash.

Evaluates 10 Easy, 5 Medium, and 5 Hard multi-file coding challenges.
Measures pass rates, turns, token consumption, cost, and latency.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vanguard.packages.runtime.root import (
    # Keep this benchmark on the public runtime boundary; the concrete
    # application service remains the composition root's client seam.
    Runtime,
    application_service,
)

env_file = ROOT / ".env"
if env_file.is_file() and not os.environ.get("OPENROUTER_API_KEY"):
    for env_line in env_file.read_text(encoding="utf-8").splitlines():
        env_line = env_line.strip()
        if env_line and not env_line.startswith("#") and "=" in env_line:
            k, v = env_line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k in {"OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "VANGUARD_ALLOW_PAID"}:
                os.environ[k] = v

from benchmarks.swe_bench.challenges import CHALLENGES, SWEProChallenge
from benchmarks.swe_bench.domain_challenges import DOMAIN_CHALLENGES

ALL_CHALLENGES: dict[str, SWEProChallenge] = {}
ALL_CHALLENGES.update(CHALLENGES)
ALL_CHALLENGES.update(DOMAIN_CHALLENGES)

EASY_TIER_KEYS = [
    "tier1_lru_ttl_cache",
    "tier1_ring_buffer_stream",
    "tier1_version_semver_parser",
    "tier2_event_bus",
    "tier2_fsm_workflow_engine",
    "tier2_retry_exponential_backoff",
    "tier2_web_reactive_signals",
    "tier3_token_bucket",
    "tier3_api_idempotency_middleware",
    "tier4_dag_resolver",
]

MEDIUM_TIER_KEYS = [
    "tier4_ds_feature_scaler_imputer",
    "tier4_web_vdom_reconciler",
    "tier4_lcb_lazy_segment_tree",
    "tier5_jsonpath_query_compiler",
    "tier5_sql_micro_planner",
]

HARD_TIER_KEYS = [
    "tier5_swe_schema_migration_engine",
    "tier5_ds_autograd_engine",
    "tier6_hle_quantum_statevector_sim",
    "tier7_hle_zk_poly_commitment_verifier",
    "tier5_datalog_engine",
]


@dataclass
class ChallengeResult:
    challenge_id: str
    tier_label: str  # Easy | Medium | Hard
    title: str
    status: str  # PASS | FAIL | ABANDONED | ERROR | INVALID_BASELINE
    turns: int
    prompt_tokens: int
    completion_tokens: int
    cached_tokens: int
    cost_usd: float
    latency_seconds: float
    error_message: str = ""
    baseline_failed: bool = True
    patch_applied: bool = False


def setup_workspace(target_dir: Path, challenge: SWEProChallenge) -> None:
    for rel_path, content in challenge.files.items():
        file_p = target_dir / rel_path
        file_p.parent.mkdir(parents=True, exist_ok=True)
        file_p.write_text(content, encoding="utf-8")


def run_oracle_test(workspace_dir: Path, oracle_code: str) -> tuple[bool, str]:
    import subprocess

    test_file = workspace_dir / "_oracle_test.py"
    test_file.write_text(oracle_code, encoding="utf-8")
    env = dict(os.environ)
    env["PYTHONPATH"] = str(workspace_dir)

    try:
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "_oracle_test.py"],
            cwd=str(workspace_dir),
            env=env,
            capture_output=True,
            text=True,
            timeout=30.0,
        )
        passed = proc.returncode == 0
        output = proc.stdout + "\n" + proc.stderr
        return passed, output
    except Exception as exc:
        return False, str(exc)
    finally:
        if test_file.exists():
            test_file.unlink(missing_ok=True)


def evaluate_challenge(
    challenge_key: str,
    tier_label: str,
    model_name: str = "deepseek/deepseek-v4-flash-0731",
    model_port: str = "openrouter",
    allow_paid: bool = True,
    dry_run: bool = False,
    max_turns: int = 15,
) -> ChallengeResult:
    challenge = ALL_CHALLENGES[challenge_key]
    with tempfile.TemporaryDirectory(prefix=f"swe_eval_{challenge_key}_") as temp_dir:
        ws_path = Path(temp_dir)
        setup_workspace(ws_path, challenge)

        # 1. Preflight: Verify baseline FAILS oracle before agent touches it
        baseline_pass, baseline_out = run_oracle_test(ws_path, challenge.oracle_code)
        if baseline_pass:
            return ChallengeResult(
                challenge_id=challenge_key,
                tier_label=tier_label,
                title=challenge.title,
                status="INVALID_BASELINE",
                turns=0,
                prompt_tokens=0,
                completion_tokens=0,
                cached_tokens=0,
                cost_usd=0.0,
                latency_seconds=0.0,
                error_message="Baseline already passed oracle before run",
                baseline_failed=False,
            )

        start_t = time.monotonic()
        app = application_service(workspace=ws_path)

        manifest_p = (
            ROOT
            / "vanguard/packages/agency/manifests/vg-code-max-v2/manifest.json"
        )

        try:
            if dry_run:
                run_res = app.run(
                    brief=challenge.brief,
                    manifest_path=manifest_p,
                    profile_id="fast",
                    interactive=True,
                    autonomous_approval=True,
                    max_turns=max_turns,
                )
            else:
                run_res = app.run(
                    brief=challenge.brief,
                    manifest_path=manifest_p,
                    model_port=model_port,
                    planner_model=model_name,
                    allow_paid=allow_paid,
                    interactive=True,
                    autonomous_approval=True,
                    max_turns=max_turns,
                )

            elapsed = time.monotonic() - start_t
            turns = run_res.turns
            
            # Extract token and cost telemetry
            cost_info = app.cost(run_res.run_id)
            cost_dict = cost_info.to_dict() if hasattr(cost_info, "to_dict") else (cost_info if isinstance(cost_info, dict) else {})
            usd_micros = cost_dict.get("usd_micros", 0)
            cost_usd = usd_micros / 1_000_000.0 if isinstance(usd_micros, (int, float)) else 0.0

            token_usage = run_res.token_usage or {}

            # 2. External Oracle Evaluation
            oracle_passed, oracle_output = run_oracle_test(ws_path, challenge.oracle_code)
            status = "PASS" if oracle_passed else ("ABANDONED" if run_res.terminal_state == "abandoned" else "FAIL")

            return ChallengeResult(
                challenge_id=challenge_key,
                tier_label=tier_label,
                title=challenge.title,
                status=status,
                turns=turns,
                prompt_tokens=token_usage.get("prompt", 0),
                completion_tokens=token_usage.get("completion", 0),
                cached_tokens=token_usage.get("cached", 0),
                cost_usd=cost_usd,
                latency_seconds=round(elapsed, 2),
                error_message=oracle_output if not oracle_passed else "",
                baseline_failed=True,
                patch_applied=oracle_passed,
            )
        except Exception as exc:
            elapsed = time.monotonic() - start_t
            return ChallengeResult(
                challenge_id=challenge_key,
                tier_label=tier_label,
                title=challenge.title,
                status="ERROR",
                turns=0,
                prompt_tokens=0,
                completion_tokens=0,
                cached_tokens=0,
                cost_usd=0.0,
                latency_seconds=round(elapsed, 2),
                error_message=str(exc),
            )


def run_full_suite(
    model_name: str = "deepseek/deepseek-v4-flash-0731",
    dry_run: bool = False,
) -> dict[str, Any]:
    results: list[ChallengeResult] = []
    print(f"=== Running 20-Challenge Benchmark Suite (Model: {model_name}, DryRun: {dry_run}) ===")

    all_specs = (
        [(k, "Easy") for k in EASY_TIER_KEYS]
        + [(k, "Medium") for k in MEDIUM_TIER_KEYS]
        + [(k, "Hard") for k in HARD_TIER_KEYS]
    )

    for idx, (key, tier) in enumerate(all_specs, 1):
        print(f"[{idx}/20] ({tier}) Evaluating {key}...")
        res = evaluate_challenge(key, tier, model_name=model_name, dry_run=dry_run)
        results.append(res)
        print(f"       -> {res.status} in {res.turns} turns, {res.latency_seconds}s (Cost: ${res.cost_usd:.5f})")

    # Aggregate Statistics
    easy_results = [r for r in results if r.tier_label == "Easy"]
    med_results = [r for r in results if r.tier_label == "Medium"]
    hard_results = [r for r in results if r.tier_label == "Hard"]

    easy_pass = sum(1 for r in easy_results if r.status == "PASS")
    med_pass = sum(1 for r in med_results if r.status == "PASS")
    hard_pass = sum(1 for r in hard_results if r.status == "PASS")
    total_pass = easy_pass + med_pass + hard_pass
    total_cost = sum(r.cost_usd for r in results)

    summary = {
        "model": model_name,
        "total_challenges": len(results),
        "total_passed": total_pass,
        "total_pass_rate": f"{(total_pass / len(results)) * 100:.1f}%",
        "easy_pass_rate": f"{easy_pass}/{len(easy_results)} ({(easy_pass/len(easy_results))*100:.1f}%)",
        "medium_pass_rate": f"{med_pass}/{len(med_results)} ({(med_pass/len(med_results))*100:.1f}%)",
        "hard_pass_rate": f"{hard_pass}/{len(hard_results)} ({(hard_pass/len(hard_results))*100:.1f}%)",
        "total_cost_usd": f"${total_cost:.5f}",
        "results": [asdict(r) for r in results],
    }

    out_path = ROOT / "benchmarks/artifacts/benchmark_20_deepseek_v4_flash.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved benchmark results to {out_path}")
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run with hermetic fake model")
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash-0731")
    args = parser.parse_args()

    run_full_suite(model_name=args.model, dry_run=args.dry_run)
