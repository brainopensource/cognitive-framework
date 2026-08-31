#!/usr/bin/env python3
"""Autonomous Vanguard Benchmark 20 Execution Harness & Scientific Matrix Analyzer.

Executes 20 decoupled coding challenges (10 Brownfield + 10 Greenfield) using
Vanguard's agentic loop and OpenRouter AI models (e.g. DeepSeek V3/V4 / GLM-4).

Features:
- Silent API key handling (from .env / env vars)
- Cryptographic cassette capture in tools/002_LLM_API_MOCK/runs/benchmark_20_captures/
- Provenance recording in tools/002_LLM_API_MOCK/lam.sqlite
- Complete empirical telemetry: PASS/FAIL, Tokens, USD Cost, Latency, Turns, Diagnosis
- ASCII Matrix comparison report
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
SUITE_ROOT = ROOT / "benchmarks" / "benchmark_20_suite"
CAPTURES_DIR = ROOT / "tools" / "002_LLM_API_MOCK" / "runs" / "benchmark_20_captures"
LAM_SQLITE_PATH = ROOT / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tools" / "002_LLM_API_MOCK") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools" / "002_LLM_API_MOCK"))

try:
    from recorder import MockRecorder
except ImportError:
    MockRecorder = None  # type: ignore


def load_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if key and not key.startswith("your_"):
        return key.strip()
    env_file = ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if val and not val.startswith("your_"):
                    return val
    return ""


# Tool definitions for LLM function calling
HARNESS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "view_file",
            "description": "Read the text contents of a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Write or overwrite the full content of a file in the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."},
                    "content": {"type": "string", "description": "Complete new content to write to the file."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command (e.g. run tests or python scripts) inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to execute."}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files and subdirectories in a directory of the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative directory path (default: '.')."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "Indicate that the task has been completed and all tests pass.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Brief explanation of the resolution."}
                },
                "required": ["summary"]
            }
        }
    }
]


SYSTEM_PROMPT = """You are Vanguard Autonomous Software Engineer operating inside an isolated repository workspace.
Your mission is to resolve the assigned coding challenge strictly following the specification.

Operational Workflow:
1. Inspect the workspace: check README.md / docs/SPEC.md, source files, and test files using `view_file` or `list_dir`.
2. Run the test suite using `run_command` (e.g. `python3 test/test_*.py` or `python3 -m unittest`) to reproduce the failure.
3. Apply surgical, robust modifications using `edit_file`.
4. Re-run tests using `run_command` until ALL test assertions pass (100% GREEN).
5. Call `finish_task` to complete your mission.

Do NOT add unrelated files. Write clean, production-grade Python adhering strictly to the specifications."""


@dataclass
class ChallengeResult:
    challenge_id: str
    kind: str  # "Brownfield" | "Greenfield"
    model: str
    status: str  # "PASS" | "FAIL"
    turns: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_seconds: float
    diagnosis: str
    trajectory: List[Dict[str, Any]] = field(default_factory=list)


class BenchmarkRunner:
    def __init__(
        self,
        model_name: str = "deepseek/deepseek-chat",
        max_turns: int = 8,
        budget_limit_usd: float = 0.20,
        recorder: Optional[Any] = None,
    ):
        self.model_name = model_name
        self.max_turns = max_turns
        self.budget_limit_usd = budget_limit_usd
        self.total_cost_usd = 0.0
        self.api_key = load_openrouter_key()
        self.recorder = recorder
        CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    def execute_tool(self, tool_name: str, args: Dict[str, Any], workspace: Path) -> str:
        try:
            if tool_name == "view_file":
                p = (workspace / args["path"]).resolve()
                if not str(p).startswith(str(workspace.resolve())):
                    return "Error: Path outside workspace"
                if not p.is_file():
                    return f"Error: File not found: {args['path']}"
                return p.read_text(encoding="utf-8")

            elif tool_name == "edit_file":
                p = (workspace / args["path"]).resolve()
                if not str(p).startswith(str(workspace.resolve())):
                    return "Error: Path outside workspace"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(args["content"], encoding="utf-8")
                return f"Successfully wrote {len(args['content'])} characters to {args['path']}"

            elif tool_name == "run_command":
                cmd = args["command"]
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                output = (proc.stdout + "\n" + proc.stderr).strip()
                return f"Exit Code: {proc.returncode}\nOutput:\n{output}"

            elif tool_name == "list_dir":
                rel = args.get("path", ".") or "."
                target = (workspace / rel).resolve()
                if not target.is_dir():
                    return f"Error: Not a directory: {rel}"
                entries = []
                for child in sorted(target.iterdir()):
                    entries.append(f"{'[DIR] ' if child.is_dir() else '[FILE]'} {child.name}")
                return "\n".join(entries) if entries else "(Empty directory)"

            elif tool_name == "finish_task":
                return f"Task marked complete: {args.get('summary', 'Done')}"

            else:
                return f"Error: Unknown tool {tool_name}"

        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 20 seconds."
        except Exception as exc:
            return f"Error executing {tool_name}: {exc}"

    def call_model(
        self,
        messages: List[Dict[str, Any]],
        scenario_key: str,
        turn: int,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], float]:
        """Calls OpenRouter API, records cassette, and updates telemetry."""
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not configured in .env or environment")

        payload = {
            "model": self.model_name,
            "messages": messages,
            "tools": HARNESS_TOOLS,
            "tool_choice": "auto",
            "temperature": 0.0,
            "max_tokens": 1500,
        }
        req_bytes = json.dumps(payload).encode("utf-8")
        req_sha256 = hashlib.sha256(req_bytes).hexdigest()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=req_bytes,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://vanguard.ai",
                "X-Title": "Vanguard-Benchmark-20",
            },
        )

        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_bytes = resp.read()
                millis = int((time.perf_counter() - t0) * 1000)
                resp_json = json.loads(resp_bytes.decode("utf-8"))
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenRouter HTTP {err.code}: {err_body}")

        reply_sha256 = hashlib.sha256(resp_bytes).hexdigest()
        usage = resp_json.get("usage", {})
        cost = usage.get("cost", 0.0) or 0.0
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        # Record to LAM SQLite if available
        if self.recorder is not None:
            try:
                self.recorder.record_call(
                    request_sha256=req_sha256,
                    scenario_key=scenario_key,
                    tier=1,
                    requested_turn=turn,
                    returned_turn=turn,
                    reply_sha256=reply_sha256,
                    source_label=self.model_name,
                    run_id=scenario_key,
                    prompt=str(messages[-1].get("content", ""))[:200],
                    response=str(resp_json.get("choices", [{}])[0].get("message", {}).get("content", ""))[:200],
                    evidence_label="benchmark_20_live",
                    tokens=prompt_tokens + completion_tokens,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost_usd=cost,
                    millis=millis,
                )
            except Exception:
                pass

        cassette_entry = {
            "turn": turn,
            "request_sha256": req_sha256,
            "response_sha256": reply_sha256,
            "status_code": 200,
            "response_b64": base64.b64encode(resp_bytes).decode("ascii"),
            "cost_usd": cost,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "duration_ms": millis,
        }

        return resp_json, cassette_entry, cost

    def run_challenge(self, challenge_dir: Path) -> ChallengeResult:
        cname = challenge_dir.name
        is_brownfield = challenge_dir.name.startswith(("01", "02", "03", "04", "05", "06", "07", "08", "09", "10"))
        kind = "Brownfield" if is_brownfield else "Greenfield"

        print(f"\n>>> Running [{kind}] Challenge: {cname}")
        t_start = time.perf_counter()

        # Create isolated temporary workspace to avoid mutating root suite files directly
        with tempfile.TemporaryDirectory(prefix=f"bench-run-{cname}-") as tmp_ws:
            ws_path = Path(tmp_ws)
            # Copy challenge files into tmp workspace
            for item in challenge_dir.iterdir():
                if item.name in ("initial_state.sha256", "__pycache__", ".vanguard"):
                    continue
                if item.is_dir():
                    shutil.copytree(item, ws_path / item.name)
                else:
                    shutil.copy2(item, ws_path / item.name)

            # Build initial user message
            if is_brownfield:
                spec_content = (ws_path / "docs" / "SPEC.md").read_text() if (ws_path / "docs" / "SPEC.md").exists() else ""
                user_brief = (
                    f"Fix the bug in the project under `{cname}`.\n"
                    f"Specification:\n{spec_content}\n\n"
                    "Your goal: Inspect the code, run tests, fix the bug in `src/`, and verify all tests pass."
                )
            else:
                readme_content = (ws_path / "README.md").read_text() if (ws_path / "README.md").exists() else ""
                user_brief = (
                    f"Implement the greenfield project under `{cname}` based on this PRD:\n\n{readme_content}\n\n"
                    "Your goal: Implement the required module(s) in `src/` so that the predefined test suite passes 100%."
                )

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_brief}
            ]

            trajectory = []
            cassettes = []
            total_prompt_tok = 0
            total_comp_tok = 0
            challenge_cost = 0.0
            finished = False
            turn = 0

            while turn < self.max_turns and not finished:
                turn += 1
                if self.total_cost_usd + challenge_cost > self.budget_limit_usd:
                    print(f"Budget limit reached (${self.budget_limit_usd})")
                    break

                try:
                    resp_json, cassette_step, call_cost = self.call_model(messages, cname, turn)
                except Exception as exc:
                    trajectory.append({"turn": turn, "error": str(exc)})
                    print(f"Turn {turn} API Error: {exc}")
                    break

                challenge_cost += call_cost
                cassettes.append(cassette_step)
                total_prompt_tok += cassette_step["prompt_tokens"]
                total_comp_tok += cassette_step["completion_tokens"]

                choice = resp_json.get("choices", [{}])[0]
                message = choice.get("message", {})
                tool_calls = message.get("tool_calls") or []

                # Append assistant message to history
                messages.append(message)

                if not tool_calls:
                    # Model provided text without tool calls
                    trajectory.append({
                        "turn": turn,
                        "assistant_text": message.get("content", "")
                    })
                    # If it says done or finished without calling tool, check oracle
                    break

                # Execute tool calls
                turn_actions = []
                for tc in tool_calls:
                    fn_name = tc.get("function", {}).get("name")
                    raw_args = tc.get("function", {}).get("arguments", "{}")
                    try:
                        args = json.loads(raw_args)
                    except Exception:
                        args = {}

                    tool_res = self.execute_tool(fn_name, args, ws_path)
                    turn_actions.append({
                        "tool": fn_name,
                        "args": args,
                        "result_snippet": tool_res[:150],
                    })

                    # Append tool response message
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id"),
                        "content": tool_res
                    })

                    if fn_name == "finish_task":
                        finished = True

                trajectory.append({
                    "turn": turn,
                    "actions": turn_actions
                })
                print(f"  Turn {turn}: Executed {[a['tool'] for a in turn_actions]} (Cost: ${call_cost:.5f})")

            # Final Oracle Evaluation
            test_files = list((ws_path / "test").glob("test_*.py"))
            oracle_passed = True
            oracle_logs = []

            if not test_files:
                oracle_passed = False
                oracle_logs.append("No test files found in test/")
            else:
                for tf in test_files:
                    p = subprocess.run([sys.executable, str(tf)], cwd=ws_path, capture_output=True, text=True)
                    if p.returncode != 0:
                        oracle_passed = False
                        oracle_logs.append(f"{tf.name} FAILED:\n{p.stderr}\n{p.stdout}")
                    else:
                        oracle_logs.append(f"{tf.name} PASSED")

            status = "PASS" if oracle_passed else "FAIL"
            diagnosis = "All falsifiers green" if oracle_passed else (oracle_logs[0][:120].replace("\n", " ") if oracle_logs else "Unknown failure")

            total_latency = time.perf_counter() - t_start
            self.total_cost_usd += challenge_cost

            # Save Cassette for replay
            cassette_file = CAPTURES_DIR / f"{cname}_cassette.json"
            cassette_file.write_text(json.dumps(cassettes, indent=2), encoding="utf-8")

            print(f"  Result: [{status}] in {turn} turns | {total_prompt_tok + total_comp_tok} tokens | ${challenge_cost:.5f} | {total_latency:.2f}s")

            return ChallengeResult(
                challenge_id=cname,
                kind=kind,
                model=self.model_name,
                status=status,
                turns=turn,
                prompt_tokens=total_prompt_tok,
                completion_tokens=total_comp_tok,
                total_tokens=total_prompt_tok + total_comp_tok,
                cost_usd=challenge_cost,
                latency_seconds=round(total_latency, 2),
                diagnosis=diagnosis,
                trajectory=trajectory,
            )


def print_results_matrix(results: List[ChallengeResult], total_cost: float, total_duration: float):
    print("\n" + "=" * 120)
    print("VANGUARD HARNESS BENCHMARK 20 — EMPIRICAL EVALUATION MATRIX")
    print("=" * 120)

    header = (
        f"{'ID':<34} | {'Type':<6} | {'Turns':<5} | {'Tokens':<8} | {'Cost ($)':<8} | {'Time (s)':<8} | {'Status':<6} | {'Diagnosis'}"
    )
    print(header)
    print("-" * 120)

    pass_count = 0
    brownfield_pass = 0
    greenfield_pass = 0
    total_tokens = 0

    for r in results:
        if r.status == "PASS":
            pass_count += 1
            if r.kind == "Brownfield":
                brownfield_pass += 1
            else:
                greenfield_pass += 1
        total_tokens += r.total_tokens

        diag_snippet = r.diagnosis[:45]
        row = (
            f"{r.challenge_id:<34} | {r.kind[:5]:<6} | {r.turns:<5} | {r.total_tokens:<8} | "
            f"${r.cost_usd:<7.5f} | {r.latency_seconds:<8.2f} | {r.status:<6} | {diag_snippet}"
        )
        print(row)

    print("-" * 120)
    pass_rate = (pass_count / len(results)) * 100 if results else 0.0
    print(f"TOTALS & SUMMARY METRICS:")
    print(f"  * Overall Pass Rate:       {pass_count}/{len(results)} ({pass_rate:.1f}%)")
    print(f"  * Brownfield Pass Rate:    {brownfield_pass}/10 ({(brownfield_pass/10)*100:.1f}%)")
    print(f"  * Greenfield Pass Rate:    {greenfield_pass}/10 ({(greenfield_pass/10)*100:.1f}%)")
    print(f"  * Total Tokens Consumed:   {total_tokens:,}")
    print(f"  * Total Cost (USD):        ${total_cost:.5f} (Budget: $0.20000)")
    print(f"  * Total Suite Duration:    {total_duration:.2f} seconds")
    print("=" * 120 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run Benchmark 20 Suite")
    parser.add_argument("--model", default="deepseek/deepseek-chat", help="OpenRouter model identifier")
    parser.add_argument("--max-turns", type=int, default=8, help="Max turns per challenge")
    parser.add_argument("--budget", type=float, default=0.20, help="Max USD budget")
    parser.add_argument("--single", default=None, help="Run single challenge name for debugging")
    args = parser.parse_args()

    recorder = MockRecorder(LAM_SQLITE_PATH) if MockRecorder else None
    runner = BenchmarkRunner(
        model_name=args.model,
        max_turns=args.max_turns,
        budget_limit_usd=args.budget,
        recorder=recorder,
    )

    challenge_dirs = sorted([d for d in SUITE_ROOT.iterdir() if d.is_dir()])
    if args.single:
        challenge_dirs = [d for d in challenge_dirs if d.name == args.single]
        if not challenge_dirs:
            print(f"Challenge {args.single} not found in {SUITE_ROOT}")
            sys.exit(1)

    t_suite_start = time.perf_counter()
    results = []

    for cdir in challenge_dirs:
        res = runner.run_challenge(cdir)
        results.append(res)

    total_duration = time.perf_counter() - t_suite_start
    print_results_matrix(results, runner.total_cost_usd, total_duration)

    # Save summary report JSON
    report_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model,
        "harness": "vanguard-vg-code-max",
        "pass_rate_pct": round((sum(1 for r in results if r.status == 'PASS') / len(results)) * 100, 1),
        "total_cost_usd": round(runner.total_cost_usd, 6),
        "total_duration_seconds": round(total_duration, 2),
        "results": [
            {
                "id": r.challenge_id,
                "kind": r.kind,
                "status": r.status,
                "turns": r.turns,
                "tokens": r.total_tokens,
                "cost_usd": round(r.cost_usd, 6),
                "latency_s": r.latency_seconds,
                "diagnosis": r.diagnosis,
            }
            for r in results
        ]
    }
    (SUITE_ROOT / "benchmark_20_results.json").write_text(json.dumps(report_data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
