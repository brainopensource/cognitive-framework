"""Run 3 Hard Challenges using vg-code-max-v3luna accelerated with LDA navigation.

Challenges:
1. sota_hard_large_catalog_collision (Tier 6 - SOTA Hard)
2. sota_hard_atomic_quota (Tier 7 - SOTA Hard)
3. tier5_swe_schema_migration_engine (Tier 5 - SWE Hard)
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
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

env_file = ROOT / ".env"
if env_file.is_file():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip().strip("'\"")
            if k in {"OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "VANGUARD_ALLOW_PAID"}:
                os.environ[k] = v

from vanguard.packages.runtime.root import (
    application_service,
    Cassette,
    CassetteRecorder,
    OpenRouterModel,
)
from benchmarks.ladder_runner import ALL_CHALLENGES, setup_workspace, run_oracle_test

OUT_DIR = ROOT / "benchmarks/artifacts/hard_lda"

HARD_CHALLENGES = [
    "sota_hard_large_catalog_collision",
    "sota_hard_atomic_quota",
    "tier5_swe_schema_migration_engine",
]


def run_hard_challenge(
    challenge_id: str,
    manifest: str = "vg-code-max-v3luna",
    model: str = "deepseek/deepseek-v4-flash-0731",
    max_turns: int = 15,
    tag: str = "hard_eval",
) -> dict[str, Any]:
    if challenge_id not in ALL_CHALLENGES:
        raise ValueError(f"Challenge '{challenge_id}' not found in ALL_CHALLENGES")

    ch = ALL_CHALLENGES[challenge_id]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"{tag}__{challenge_id}__{manifest}__{re.sub(r'[^A-Za-z0-9_.-]+', '_', model)}"
    tape_path = OUT_DIR / f"{stem}.cassette.json"

    print(f"\n================================================================================")
    print(f" HARD CHALLENGE: {challenge_id} (Tier {ch.tier})")
    print(f" Title:          {ch.title}")
    print(f" Manifest:       {manifest}")
    print(f" Model:          {model}")
    print(f"================================================================================\n")

    with tempfile.TemporaryDirectory(prefix=f"hard_{challenge_id}_") as td:
        ws = Path(td)
        setup_workspace(ws, ch)

        cassette = Cassette()
        live_model = OpenRouterModel(model=model, stream=False, reasoning_effort="none")
        recorder = CassetteRecorder(cassette, delegate=live_model, output_path=tape_path)

        app = application_service(workspace=ws)
        manifest_p = ROOT / f"vanguard/packages/agency/manifests/{manifest}/manifest.json"

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
            err = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-1500:]}"
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
            "challenge_id": challenge_id,
            "title": ch.title,
            "tier": ch.tier,
            "manifest": manifest,
            "model": model,
            "status": status,
            "oracle_pass": oracle_pass,
            "total_time_s": elapsed,
            "turns": getattr(run_res, "turns", 0) if run_res else len(cassette.records),
            "llm_calls": len(cassette.records),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
            "tokens_per_sec": tokens_per_sec,
            "cost_usd": round(spend, 6),
            "files_modified": modified,
            "terminal_state": getattr(run_res, "terminal_state", None) if run_res else None,
            "oracle_output": oracle_out[-2000:] if not oracle_pass else "ALL ORACLE ASSERTIONS PASSED",
            "error": err,
            "cassette": str(tape_path.relative_to(ROOT)),
        }

        print(f"[{status}] Latency: {elapsed}s | Turns: {result['turns']} | Calls: {result['llm_calls']} | Tokens: {total_tokens} ({tokens_per_sec} tok/s) | Cost: ${spend:.6f}")
        return result


def main():
    ap = argparse.ArgumentParser(description="Run 3 Hard Challenges on vg-code-max-v3luna")
    ap.add_argument("--manifest", default="vg-code-max-v3luna", help="Harness manifest")
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash-0731", help="Model ID")
    ap.add_argument("--max-turns", type=int, default=15, help="Max turns per challenge")
    ap.add_argument("--tag", default="hard_3_run", help="Run tag")
    args = ap.parse_args()

    results = []
    for ch_id in HARD_CHALLENGES:
        res = run_hard_challenge(
            challenge_id=ch_id,
            manifest=args.manifest,
            model=args.model,
            max_turns=args.max_turns,
            tag=args.tag,
        )
        results.append(res)

    report_path = OUT_DIR / f"report_3_hard_challenges__{args.manifest}.json"
    report_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    total_pass = sum(1 for r in results if r["status"] == "PASS")
    total_spend = sum(r["cost_usd"] for r in results)
    total_time = sum(r["total_time_s"] for r in results)

    print("\n================================================================================")
    print(f" 3 HARD CHALLENGES SUMMARY SCORECARD: {total_pass}/{len(results)} PASSED")
    print(f" Total Elapsed: {total_time:.2f}s | Total Spend: ${total_spend:.6f}")
    print(f" Artifact:      {report_path.relative_to(ROOT)}")
    print("================================================================================\n")


if __name__ == "__main__":
    main()
