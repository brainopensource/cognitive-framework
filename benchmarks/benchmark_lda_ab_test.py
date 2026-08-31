"""A/B Benchmark: Evaluating Codebase Navigation Performance WITH vs WITHOUT LDA (LLM Docs Atlas).

This benchmark tests an agent's ability to navigate a large, complex multi-file
codebase with ZERO file-path hints given in the task brief.

Metrics compared:
1. Discovery Latency (Time taken to locate & fix target)
2. Search / Navigation Turns (Turns spent exploring vs executing)
3. Total Token Consumption & Cache Efficiency
4. Total Cost ($ USD)
5. Oracle Ground-Truth Pass / Fail
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any, Mapping

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

OUT_DIR = ROOT / "benchmarks/artifacts/lda_ab_test"

# Task Brief with ZERO file path hints:
TASK_BRIEF_NO_LDA = """We have an issue in our enterprise benchmark engine.

PROBLEM DESCRIPTION:
In the benchmark budget subsystem, the function `compute_dynamic_headroom` has a regression:
It currently fails to apply the safety dampening factor (0.85) when `burst_mode` is enabled,
and improperly allows negative remaining headroom when `spent_micros` exceeds `allocated_micros` (it should clamp to 0).

YOUR TASK:
1. Search the workspace to locate `compute_dynamic_headroom` and its associated unit test suite.
2. Fix `compute_dynamic_headroom` so that:
   - When `burst_mode` is True: `headroom = int((allocated_micros - spent_micros) * 0.85)`
   - When `burst_mode` is False: `headroom = allocated_micros - spent_micros`
   - Headroom must NEVER be negative (clamp minimum to 0).
3. Run tests using `test` with `{"argv": ["python3", "-m", "unittest", "discover", "-s", "."]}`.
4. Once all tests pass, call `finish` with a summary of changes.
"""

TASK_BRIEF_WITH_LDA = """We have an issue in our enterprise benchmark engine.

PROBLEM DESCRIPTION:
In the benchmark budget subsystem, the function `compute_dynamic_headroom` has a regression:
It currently fails to apply the safety dampening factor (0.85) when `burst_mode` is enabled,
and improperly allows negative remaining headroom when `spent_micros` exceeds `allocated_micros` (it should clamp to 0).

LDA ACCELERATION HINT:
Use `test` with `{"argv": ["python3", "-c", "import lda_index; print(lda_index.lookup('compute_dynamic_headroom'))"]}` or run `python3 tools/docs_rag_v0.py "compute_dynamic_headroom"` to instantly resolve the exact file and line numbers.

YOUR TASK:
1. Locate `compute_dynamic_headroom` using LDA or direct search.
2. Fix `compute_dynamic_headroom` so that:
   - When `burst_mode` is True: `headroom = int((allocated_micros - spent_micros) * 0.85)`
   - When `burst_mode` is False: `headroom = allocated_micros - spent_micros`
   - Headroom must NEVER be negative (clamp minimum to 0).
3. Run tests using `test` with `{"argv": ["python3", "-m", "unittest", "discover", "-s", "."]}`.
4. Once all tests pass, call `finish` with a summary of changes.
"""

ORACLE_TEST_CODE = """import unittest
from benchmarks.baac.lib.budget import compute_dynamic_headroom

class TestHeadroomOracle(unittest.TestCase):
    def test_normal_mode(self):
        self.assertEqual(compute_dynamic_headroom(1000, 200, burst_mode=False), 800)
        self.assertEqual(compute_dynamic_headroom(500, 500, burst_mode=False), 0)

    def test_burst_mode_dampening(self):
        # (1000 - 200) * 0.85 = 800 * 0.85 = 680
        self.assertEqual(compute_dynamic_headroom(1000, 200, burst_mode=True), 680)

    def test_negative_clamping(self):
        # Spent > allocated must clamp to 0 in both modes
        self.assertEqual(compute_dynamic_headroom(500, 800, burst_mode=False), 0)
        self.assertEqual(compute_dynamic_headroom(500, 800, burst_mode=True), 0)

if __name__ == "__main__":
    unittest.main()
"""


def build_complex_workspace(ws: Path) -> None:
    """Build a realistic multi-package codebase with dozens of modules, nested folders, and decoys."""
    # 1. Create dozens of benchmark directories & files
    dirs = [
        "benchmarks/baac/lib",
        "benchmarks/baac/runners",
        "benchmarks/swe_bench/core",
        "benchmarks/swe_bench/evaluators",
        "benchmarks/ladder/sota",
        "benchmarks/matrix/harness",
        "benchmarks/matrix/reporters",
        "packages/domain/models",
        "packages/kernel/dispatch",
        "packages/adapters/storage",
        "tests/unit",
        "tests/integration",
    ]
    for d in dirs:
        (ws / d).mkdir(parents=True, exist_ok=True)
        (ws / d / "__init__.py").write_text("", encoding="utf-8")

    # 2. Add decoy files
    for i in range(25):
        (ws / f"benchmarks/swe_bench/core/runner_{i}.py").write_text(
            f"# Runner module {i}\ndef run_suite_{i}(): return {i}\n", encoding="utf-8"
        )
        (ws / f"benchmarks/matrix/harness/matrix_{i}.py").write_text(
            f"# Matrix config {i}\nMATRIX_WEIGHT_{i} = {i * 10}\n", encoding="utf-8"
        )

    # 3. Add target file with the bug
    buggy_budget_code = '''"""Benchmark budget and resource accounting subsystem."""

from __future__ import annotations
from dataclasses import dataclass

@dataclass
class BudgetSnapshot:
    allocated_micros: int
    spent_micros: int
    burst_enabled: bool

def compute_dynamic_headroom(allocated_micros: int, spent_micros: int, burst_mode: bool = False) -> int:
    """Calculates remaining budget headroom."""
    # BUG: Missing 0.85 burst dampening factor and missing 0 clamp on overspend!
    return allocated_micros - spent_micros
'''
    (ws / "benchmarks/baac/lib/budget.py").write_text(buggy_budget_code, encoding="utf-8")

    # 4. Add existing public test file
    public_test_code = '''import unittest
from benchmarks.baac.lib.budget import compute_dynamic_headroom

class TestBudgetPublic(unittest.TestCase):
    def test_basic_headroom(self):
        self.assertEqual(compute_dynamic_headroom(1000, 200), 800)

if __name__ == "__main__":
    unittest.main()
'''
    (ws / "tests/unit/test_budget.py").write_text(public_test_code, encoding="utf-8")

    # 5. Add minimal LDA index helper inside workspace for the LDA configuration
    lda_helper = '''"""LDA Repository Intelligence Mock Index."""
INDEX = {
    "compute_dynamic_headroom": {
        "file": "benchmarks/baac/lib/budget.py",
        "line": 12,
        "kind": "function",
        "tests": ["tests/unit/test_budget.py"]
    }
}
def lookup(symbol: str):
    return INDEX.get(symbol, {"error": "symbol not found"})
'''
    (ws / "lda_index.py").write_text(lda_helper, encoding="utf-8")


def run_eval(
    *,
    mode: str,
    manifest: str,
    model: str,
    max_turns: int = 15,
) -> dict[str, Any]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = f"lda_ab__{mode}__{manifest}__{re.sub(r'[^A-Za-z0-9_.-]+', '_', model)}"
    tape_path = OUT_DIR / f"{stem}.cassette.json"

    with tempfile.TemporaryDirectory(prefix=f"lda_ab_{mode}_") as td:
        ws = Path(td)
        build_complex_workspace(ws)

        cassette = Cassette()
        live_model = OpenRouterModel(model=model, stream=False, reasoning_effort="none")
        recorder = CassetteRecorder(cassette, delegate=live_model, output_path=tape_path)

        app = application_service(workspace=ws)
        manifest_p = ROOT / f"vanguard/packages/agency/manifests/{manifest}/manifest.json"

        brief = TASK_BRIEF_WITH_LDA if mode == "WITH_LDA" else TASK_BRIEF_NO_LDA

        start_time = time.monotonic()
        err = ""
        run_res = None
        try:
            run_res = app.run(
                brief=brief,
                manifest_path=manifest_p,
                model=recorder,
                interactive=True,
                autonomous_approval=True,
                max_turns=max_turns,
            )
        except Exception as exc:
            err = f"{type(exc).__name__}: {exc}\n{traceback.format_exc()[-1000:]}"
        elapsed = round(time.monotonic() - start_time, 2)

        # Run Oracle Test
        oracle_file = ws / "_oracle_test.py"
        oracle_file.write_text(ORACLE_TEST_CODE, encoding="utf-8")
        import subprocess
        proc = subprocess.run(
            [sys.executable, "-m", "unittest", "_oracle_test.py"],
            cwd=str(ws),
            capture_output=True,
            text=True,
            timeout=30,
        )
        oracle_pass = proc.returncode == 0

        prompt_tokens = sum(int(r.proposal.get("usage", {}).get("prompt_tokens") or 0) for r in cassette.records)
        completion_tokens = sum(int(r.proposal.get("usage", {}).get("completion_tokens") or 0) for r in cassette.records)
        cached_tokens = sum(int(r.proposal.get("usage", {}).get("cached_tokens") or 0) for r in cassette.records)
        total_tokens = prompt_tokens + completion_tokens
        spend = sum(float(r.proposal.get("cost_usd") or 0) for r in cassette.records)

        # Categorize turns into search/read vs patching/testing
        search_turns = 0
        execution_turns = 0
        for r in cassette.records:
            action = r.proposal.get("action", "")
            if action in {"fs.search", "fs.read", "search", "read"}:
                search_turns += 1
            else:
                execution_turns += 1

        tokens_per_sec = round(total_tokens / elapsed, 1) if elapsed > 0 else 0.0
        status = "PASS" if oracle_pass else ("ERROR" if err else "FAIL")

        return {
            "mode": mode,
            "manifest": manifest,
            "model": model,
            "status": status,
            "oracle_pass": oracle_pass,
            "total_time_s": elapsed,
            "turns": getattr(run_res, "turns", 0) if run_res else len(cassette.records),
            "search_turns": search_turns,
            "execution_turns": execution_turns,
            "llm_calls": len(cassette.records),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
            "tokens_per_sec": tokens_per_sec,
            "cost_usd": round(spend, 6),
            "terminal_state": getattr(run_res, "terminal_state", None) if run_res else None,
            "cassette": str(tape_path.relative_to(ROOT)),
        }


def main():
    ap = argparse.ArgumentParser(description="LDA A/B Performance Benchmark")
    ap.add_argument("--manifest", default="vg-code-max-v3luna", help="Harness manifest")
    ap.add_argument("--model", default="deepseek/deepseek-v4-flash-0731", help="Model ID")
    ap.add_argument("--max-turns", type=int, default=15, help="Max turns allowed")
    args = ap.parse_args()

    print("\n================================================================================")
    print(" LDA REPOSITORY INTELLIGENCE A/B BENCHMARK")
    print(f" Target Harness: {args.manifest}")
    print(f" Target Model:   {args.model}")
    print(" Test Mode:      Blind Multi-File Navigation (No File Path Hints)")
    print("================================================================================\n")

    print(">>> [1/2] Running Configuration A: WITHOUT LDA (Manual Search) ...", flush=True)
    res_no_lda = run_eval(
        mode="WITHOUT_LDA",
        manifest=args.manifest,
        model=args.model,
        max_turns=args.max_turns,
    )
    print(f"    Result: {res_no_lda['status']} | Time: {res_no_lda['total_time_s']}s | Search Turns: {res_no_lda['search_turns']} | Cost: ${res_no_lda['cost_usd']:.6f}\n")

    print(">>> [2/2] Running Configuration B: WITH LDA (Index/AST Accelerated) ...", flush=True)
    res_with_lda = run_eval(
        mode="WITH_LDA",
        manifest=args.manifest,
        model=args.model,
        max_turns=args.max_turns,
    )
    print(f"    Result: {res_with_lda['status']} | Time: {res_with_lda['total_time_s']}s | Search Turns: {res_with_lda['search_turns']} | Cost: ${res_with_lda['cost_usd']:.6f}\n")

    report = {"without_lda": res_no_lda, "with_lda": res_with_lda}
    report_path = OUT_DIR / f"lda_ab_report__{args.manifest}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote full A/B report to: {report_path.relative_to(ROOT)}\n")


if __name__ == "__main__":
    main()
