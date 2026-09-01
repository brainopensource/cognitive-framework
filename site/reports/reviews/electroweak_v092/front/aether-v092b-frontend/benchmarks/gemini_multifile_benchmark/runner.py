"""Standalone Runner for Gemini Multi-File and Large-Context Benchmarks.

Evaluates autonomous agent coding performance across multi-file dependencies,
records all trajectories and completions into LAM Store (lam.sqlite), and evaluates
cryptographic oracles with zero network leaks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

LAM_DIR = ROOT / "tools" / "002_LLM_API_MOCK"
if str(LAM_DIR) not in sys.path:
    sys.path.insert(0, str(LAM_DIR))

from benchmarks.gemini_multifile_benchmark.challenges import GEMINI_CHALLENGES, MultifileChallenge
import importlib
LamStore = getattr(importlib.import_module("store"), "LamStore")


def load_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if key and not key.startswith("your_"):
        return key
    env_file = ROOT / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def call_openrouter(model: str, messages: list[dict], api_key: str, max_tokens: int = 1000) -> dict[str, Any]:
    """Call OpenRouter with timeout and return structured completion + telemetry."""
    if not api_key:
        return {"error": "Missing OPENROUTER_API_KEY", "status": "no_key"}

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/aether-d-system",
        "X-Title": "Gemini Multi-File Benchmark",
    }
    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }

    t0 = time.perf_counter()
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            wall_s = round(time.perf_counter() - t0, 3)
            choice = data["choices"][0]
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            comp_tokens = usage.get("completion_tokens", 0)
            cost_usd = float(usage.get("cost", 0.0) or 0.0)
            content = choice["message"].get("content", "")
            return {
                "content": content,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": comp_tokens,
                "total_tokens": prompt_tokens + comp_tokens,
                "cost_usd": cost_usd,
                "wall_s": wall_s,
                "status": "success",
            }
    except Exception as exc:
        wall_s = round(time.perf_counter() - t0, 3)
        return {
            "error": str(exc),
            "content": "",
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "cost_usd": 0.0,
            "wall_s": wall_s,
            "status": "error",
        }


def run_multifile_benchmark(
    challenge: MultifileChallenge,
    model: str,
    api_key: str,
    store: LamStore | None = None,
) -> dict[str, Any]:
    """Execute multi-file benchmark challenge, evaluate oracle, and record trace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Path(tmpdir)
        for rel_path, content in challenge.files.items():
            fpath = repo / rel_path
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8")

        oracle_path = repo / "test_oracle.py"
        oracle_path.write_text(challenge.oracle_code, encoding="utf-8")

        # Initial prompt with all file contents and instructions
        files_dump = "\n\n".join(
            f"--- File: {path} ---\n{content}" for path, content in challenge.files.items()
        )
        prompt = (
            f"You are an expert software engineer.\n\n"
            f"Challenge: {challenge.title}\n"
            f"Task: {challenge.brief}\n\n"
            f"Current Codebase:\n{files_dump}\n\n"
            f"Please provide the complete, corrected code for each modified file in standard markdown codeblocks labeled with the file path (e.g. ```python cluster/node.py ... ```)."
        )

        messages = [
            {"role": "system", "content": "You are an expert autonomous software engineer."},
            {"role": "user", "content": prompt},
        ]

        res = call_openrouter(model, messages, api_key)
        passed = False
        oracle_output = ""

        if res["status"] == "success" and res["content"]:
            # Parse code blocks from model response
            content = res["content"]
            lines = content.splitlines()
            current_file = None
            code_lines: list[str] = []
            inside_block = False

            for line in lines:
                if line.startswith("```"):
                    if inside_block:
                        if current_file and code_lines:
                            target = repo / current_file
                            target.parent.mkdir(parents=True, exist_ok=True)
                            target.write_text("\n".join(code_lines) + "\n", encoding="utf-8")
                        inside_block = False
                        current_file = None
                        code_lines = []
                    else:
                        inside_block = True
                        header = line.lstrip("`").strip()
                        # e.g. python cluster/node.py or cluster/node.py
                        parts = header.split()
                        for p in parts:
                            if "/" in p or p.endswith(".py"):
                                current_file = p
                                break
                elif inside_block:
                    code_lines.append(line)

            # Run oracle
            import subprocess
            proc = subprocess.run(
                [sys.executable, "-m", "unittest", "test_oracle.py"],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=15,
            )
            passed = proc.returncode == 0
            oracle_output = (proc.stdout or "") + (proc.stderr or "")

        # Record into LAM Store (lam.sqlite)
        if store is not None:
            store.upsert_scenario(
                scenario_id=f"gemini/{challenge.challenge_id}",
                tier=challenge.tier,
                title=challenge.title,
                atoms=["multifile", "ast-patch", "oracle-gate"],
                n_files=len(challenge.files),
                n_turns=1,
                created_from="gemini-multifile-bench",
            )
            store.insert_trace(
                scenario_id=f"gemini/{challenge.challenge_id}",
                backend="openrouter",
                model=model,
                passed=passed,
                llm_calls=1,
                prompt_tokens=res.get("prompt_tokens", 0),
                completion_tokens=res.get("completion_tokens", 0),
                usd=res.get("cost_usd", 0.0),
                wall_s=res.get("wall_s", 0.0),
                model_tier=challenge.tier,
                scenario_tier=challenge.tier,
                harness_version="vanguard-v0.9.1",
            )

        return {
            "challenge_id": challenge.challenge_id,
            "title": challenge.title,
            "model": model,
            "passed": passed,
            "wall_s": res.get("wall_s", 0.0),
            "prompt_tokens": res.get("prompt_tokens", 0),
            "completion_tokens": res.get("completion_tokens", 0),
            "total_tokens": res.get("total_tokens", 0),
            "cost_usd": res.get("cost_usd", 0.0),
            "status": res.get("status"),
            "error": res.get("error"),
            "oracle_output": oracle_output.strip() if not passed else "OK",
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Gemini Multi-File Benchmark Runner")
    parser.add_argument("--model", type=str, default="openrouter/free")
    parser.add_argument("--challenge", type=str, default=None)
    args = parser.parse_args()

    api_key = load_api_key()
    store = LamStore()

    target_challenges = (
        [GEMINI_CHALLENGES[args.challenge]]
        if args.challenge and args.challenge in GEMINI_CHALLENGES
        else list(GEMINI_CHALLENGES.values())
    )

    print(f"=== Running Gemini Multi-File Benchmark ({len(target_challenges)} challenges) with {args.model} ===")
    results = []
    for c in target_challenges:
        print(f"-> Executing {c.challenge_id}: {c.title}...")
        res = run_multifile_benchmark(c, args.model, api_key, store=store)
        results.append(res)
        status_str = "PASSED" if res["passed"] else f"FAILED ({res.get('status')})"
        print(f"   [{status_str}] tokens: {res['total_tokens']}, cost: ${res['cost_usd']:.6f}, time: {res['wall_s']}s")

    out_file = ROOT / "benchmarks" / f"gemini_benchmark_{args.model.replace('/', '_').replace(':', '_')}.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nWrote benchmark results to {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
