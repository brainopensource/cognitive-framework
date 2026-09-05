"""Head-to-head harness KPI comparison benchmark.

Runs multiple Vanguard manifests against identical coding challenges to measure:
- Pass / Fail status (Hidden Oracle Verification)
- Latency (Total Time in seconds)
- Total Tokens (Prompt, Completion, Cached, Total)
- Throughput (Tokens / second)
- Execution Turns & LLM Calls
- Total Cost ($ USD)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from vanguard.packages.runtime.root import (
    application_service,
    Cassette,
    CassetteRecorder,
    OpenRouterModel,
)
from benchmarks.ladder_runner import ALL_CHALLENGES, setup_workspace, run_oracle_test
from benchmarks._env import load_benchmark_env

OUT_DIR = ROOT / "benchmarks/artifacts/comparison"


def run_single_harness_eval(
    manifest_name: str,
    challenge_id: str,
    model_name: str,
    max_turns: int = 15,
) -> dict[str, Any]:
    if challenge_id not in ALL_CHALLENGES:
        raise ValueError(f"Unknown challenge: {challenge_id}")

    ch = ALL_CHALLENGES[challenge_id]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"comp__{challenge_id}__{manifest_name}__{re.sub(r'[^A-Za-z0-9_.-]+', '_', model_name)}"
    tape_path = OUT_DIR / f"{stem}.cassette.json"

    with tempfile.TemporaryDirectory(prefix=f"comp_{manifest_name}_") as td:
        ws = Path(td)
        setup_workspace(ws, ch)

        cassette = Cassette()
        live_model = OpenRouterModel(model=model_name, stream=False, reasoning_effort="none")
        recorder = CassetteRecorder(cassette, delegate=live_model, output_path=tape_path)

        app = application_service(workspace=ws)
        manifest_p = ROOT / f"vanguard/packages/agency/manifests/{manifest_name}/manifest.json"

        start_time = time.monotonic()
        err = ""
        run_res = None
        try:
            run_res = app.run(
                brief=ch.brief,
                manifest_path=manifest_p,
                model=recorder,
                interactive=True,
                autonomous_approval=True,
                max_turns=max_turns,
            )
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-1000:]}"
        elapsed = round(time.monotonic() - start_time, 2)

        oracle_pass, oracle_out = run_oracle_test(ws, ch.oracle_code)
        modified = sorted(
            str(p.relative_to(ws))
            for p in ws.rglob("*.py")
            if p.is_file() and not p.name.startswith("_oracle")
        )

        prompt_tokens = sum(int(r.proposal.get("usage", {}).get("prompt_tokens") or 0) for r in cassette.records)
        completion_tokens = sum(int(r.proposal.get("usage", {}).get("completion_tokens") or 0) for r in cassette.records)
        cached_tokens = sum(int(r.proposal.get("usage", {}).get("cached_tokens") or 0) for r in cassette.records)
        total_tokens = prompt_tokens + completion_tokens
        spend = sum(float(r.proposal.get("cost_usd") or 0) for r in cassette.records)

        tokens_per_sec = round(total_tokens / elapsed, 1) if elapsed > 0 else 0.0

        status = "PASS" if oracle_pass else ("ERROR" if err else "FAIL")

        result = {
            "harness": manifest_name,
            "challenge": challenge_id,
            "tier": ch.tier,
            "model": model_name,
            "status": status,
            "oracle_pass": oracle_pass,
            "total_time_s": elapsed,
            "turns": getattr(run_res, "turns", 0) if run_res else 0,
            "llm_calls": len(cassette.records),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
            "tokens_per_sec": tokens_per_sec,
            "cost_usd": round(spend, 6),
            "files_modified": modified,
            "terminal_state": getattr(run_res, "terminal_state", None) if run_res else None,
            "error": err,
        }
        return result


def main():
    ap = argparse.ArgumentParser(description="Multi-harness KPI benchmark comparison")
    ap.add_argument("--challenge", default="sota_easy_config_precedence", help="Challenge ID")
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash-0731", help="Model ID")
    ap.add_argument(
        "--manifests",
        nargs="+",
        default=["vg-code-max-v3luna", "vg-code-max-v2b", "vg-code-chimera", "vg-1-forge-v2"],
        help="List of manifest harnesses to benchmark",
    )
    ap.add_argument("--max-turns", type=int, default=15, help="Max turns per run")
    args = ap.parse_args()

    print(f"\n================================================================================")
    print(f" MULTI-HARNESS KPI COMPARISON BENCHMARK")
    print(f" Challenge: {args.challenge}")
    print(f" Model:     {args.model}")
    print(f" Harnesses: {', '.join(args.manifests)}")
    print(f"================================================================================\n")

    results = []
    for manifest in args.manifests:
        print(f"--> Running harness: {manifest} ...", flush=True)
        res = run_single_harness_eval(
            manifest_name=manifest,
            challenge_id=args.challenge,
            model_name=args.model,
            max_turns=args.max_turns,
        )
        results.append(res)
        print(
            f"    [{res['status']}] Time: {res['total_time_s']}s | "
            f"Turns: {res['turns']} | Calls: {res['llm_calls']} | "
            f"Tokens: {res['total_tokens']} ({res['tokens_per_sec']} tok/s) | "
            f"Cost: ${res['cost_usd']:.6f}\n"
        )

    report_path = OUT_DIR / f"kpi_comparison__{args.challenge}.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote full KPI report to: {report_path.relative_to(ROOT)}\n")


if __name__ == "__main__":
    load_benchmark_env()
    main()
