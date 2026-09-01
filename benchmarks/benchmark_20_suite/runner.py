#!/usr/bin/env python3
"""Autonomous Vanguard Benchmark 20 Execution Harness & Scientific Matrix Analyzer.

Executes 20 decoupled coding challenges (10 Brownfield + 10 Greenfield) using
Vanguard's agentic loop and Centralized Model Configuration.

POLICY:
- Model identities, defaults, and pricing MUST be loaded from the centralized
  unified model registry: `vanguard/packages/adapters/models/config.py` & `models_registry.json`.
- Zero hardcoded model literals in runner code.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
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

# Centralized Model Registry Configuration
from vanguard.packages.runtime.root import (
    get_default_model,
    get_default_paid_model,
    get_pricing_usd_table,
    resolve_model,
    load_model_registry,
    FORGE_PRESET_NAME,
    ForgeConfig,
    ForgeFacade,
    GoalContract,
)

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
            "description": "Execute a shell command (e.g. run unit tests) inside the workspace.",
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
1. Inspect the workspace: check README.md / docs/SPEC.md, source files in `src/`, and test files in `test/`.
2. Run the test suite using `run_command` (e.g. `python3 -m unittest` or `python3 test/test_suite.py`) to observe test behavior.
3. Edit the implementation in `src/` using `edit_file` to fix the bug or implement the requirements.
4. Re-run tests with `run_command` until ALL test assertions pass (100% GREEN).
5. Call `finish_task` only after confirming that all tests pass.

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


def extract_tool_calls_from_content(content: str) -> List[Dict[str, Any]]:
    calls = []
    if not content:
        return calls

    parts = re.split(r"<[|｜]tool[^>|｜]*[|｜]>function<[|｜]tool[^>|｜]*[|｜]>", content)
    if len(parts) > 1:
        for part in parts[1:]:
            lines = part.strip().split("\n", 1)
            name = lines[0].strip()
            rest = lines[1] if len(lines) > 1 else ""
            j_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", rest, re.DOTALL)
            if j_match:
                args_str = j_match.group(1)
            else:
                j_match = re.search(r"(\{.*\})", rest, re.DOTALL)
                args_str = j_match.group(1) if j_match else "{}"
            try:
                args = json.loads(args_str)
                calls.append({"name": name, "arguments": args})
            except Exception:
                pass

    return calls


class BenchmarkOpenRouterModelPort:
    """ModelPort adapter for BenchmarkRunner executing via OpenRouter."""

    def __init__(self, runner: BenchmarkRunner, scenario_key: str, cassettes: list[dict[str, Any]]) -> None:
        self.runner = runner
        self.scenario_key = scenario_key
        self.cassettes = cassettes
        self.turn_counter = 0
        self.total_cost = 0.0
        self.total_prompt_tok = 0
        self.total_comp_tok = 0

    def propose(self, context: Any, tools: Any, sampling: Any) -> Any:
        self.turn_counter += 1
        messages = list(context.get("messages", []))
        resp_json, cassette_entry, cost = self.runner.call_model(
            messages=messages,
            scenario_key=self.scenario_key,
            turn=self.turn_counter,
        )
        self.cassettes.append(cassette_entry)
        self.total_cost += cost
        choice = resp_json.get("choices", [{}])[0]
        msg = choice.get("message", {})
        usage = resp_json.get("usage", {})
        p_tok = usage.get("prompt_tokens", 0)
        c_tok = usage.get("completion_tokens", 0)
        self.total_prompt_tok += p_tok
        self.total_comp_tok += c_tok
        usage["cost"] = cost
        return {
            "message": msg,
            "usage": usage,
        }


class BenchmarkRunner:
    def __init__(
        self,
        model_name: Optional[str] = None,
        preset: str = "vg-code-max",
        max_turns: int = 8,
        budget_limit_usd: float = 0.20,
        recorder: Optional[Any] = None,
    ):
        # Use Centralized Config as authoritative source
        self.model_name = resolve_model(model_name) if model_name else get_default_paid_model()
        self.preset = preset
        self.max_turns = max_turns
        self.budget_limit_usd = budget_limit_usd
        self.total_cost_usd = 0.0
        self.api_key = load_openrouter_key()
        self.recorder = recorder
        self.pricing_table = get_pricing_usd_table()
        self.ledger_path = ROOT / "benchmarks" / "sota_spend_ledger.json"
        self.ledger = json.loads(self.ledger_path.read_text(encoding="utf-8"))
        if self.ledger.get("status") not in {"FROZEN_NO_PAID_CALLS", "RUNNING"}:
            raise RuntimeError("SOTA spend ledger is closed")
        self.ledger["status"] = "RUNNING"
        self._persist_ledger()
        CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

    def _persist_ledger(self) -> None:
        self.ledger_path.write_text(json.dumps(self.ledger, indent=2) + "\n", encoding="utf-8")

    def _reserve_provider_call(self) -> None:
        auth = self.ledger["authorization"]
        if self.model_name not in set(auth["models"]):
            raise RuntimeError(f"model is outside frozen SOTA authorization: {self.model_name}")
        if (self.ledger["total_calls"] >= auth["max_calls"] or
                self.ledger["total_tokens"] >= auth["max_tokens"] or
                self.ledger["total_usd"] >= auth["max_usd"]):
            raise RuntimeError("frozen SOTA spend ledger exhausted")

    def _record_provider_call(self, *, usage: Dict[str, Any], cost: float,
                              model_resolved: str, latency_ms: int) -> None:
        prompt = usage.get("prompt_tokens")
        completion = usage.get("completion_tokens")
        if not isinstance(prompt, int) or not isinstance(completion, int):
            self.ledger["status"] = "BLOCKED_UNKNOWN_USAGE"
            self._persist_ledger()
            raise RuntimeError("provider usage missing; paid routing blocked")
        tokens = prompt + completion
        auth = self.ledger["authorization"]
        if (self.ledger["total_tokens"] + tokens > auth["max_tokens"] or
                self.ledger["total_usd"] + cost > auth["max_usd"]):
            self.ledger["status"] = "CLOSED_BUDGET"
            self._persist_ledger()
            raise RuntimeError("provider response would exceed frozen SOTA budget")
        self.ledger["calls"].append({
            "call_index": self.ledger["total_calls"] + 1,
            "model_resolved": model_resolved,
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "tokens": tokens,
            "usd": cost,
            "latency_ms": latency_ms,
        })
        self.ledger["total_calls"] += 1
        self.ledger["total_tokens"] += tokens
        self.ledger["total_usd"] = round(self.ledger["total_usd"] + cost, 9)
        self._persist_ledger()

    def check_workspace_tests(self, workspace: Path) -> Tuple[bool, str]:
        env = {
            **os.environ,
            "PYTHONPATH": f"{str(workspace.resolve())}:{str((workspace / 'src').resolve())}",
        }
        test_files = list((workspace / "test").glob("test_*.py"))
        if not test_files:
            return False, "No test files found in test/"

        all_ok = True
        outputs = []
        for tf in test_files:
            p = subprocess.run([sys.executable, str(tf)], cwd=workspace, env=env, capture_output=True, text=True)
            if p.returncode != 0:
                all_ok = False
                outputs.append(f"{tf.name} FAILED:\n{p.stderr}\n{p.stdout}")
            else:
                outputs.append(f"{tf.name} PASSED")

        return all_ok, "\n".join(outputs)

    def execute_tool(self, tool_name: str, args: Dict[str, Any], workspace: Path) -> Tuple[str, bool]:
        try:
            env = {
                **os.environ,
                "PYTHONPATH": f"{str(workspace.resolve())}:{str((workspace / 'src').resolve())}",
            }

            if tool_name == "view_file":
                p = (workspace / args["path"]).resolve()
                if not str(p).startswith(str(workspace.resolve())):
                    return "Error: Path outside workspace", False
                if not p.is_file():
                    return f"Error: File not found: {args['path']}", False
                return p.read_text(encoding="utf-8"), False

            elif tool_name == "edit_file":
                p = (workspace / args["path"]).resolve()
                if not str(p).startswith(str(workspace.resolve())):
                    return "Error: Path outside workspace", False
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(args["content"], encoding="utf-8")
                return f"Successfully wrote {len(args['content'])} characters to {args['path']}", False

            elif tool_name == "run_command":
                cmd = args["command"]
                proc = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=workspace,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                output = (proc.stdout + "\n" + proc.stderr).strip()
                return f"Exit Code: {proc.returncode}\nOutput:\n{output}", False

            elif tool_name == "list_dir":
                rel = args.get("path", ".") or "."
                target = (workspace / rel).resolve()
                if not target.is_dir():
                    return f"Error: Not a directory: {rel}", False
                entries = []
                for child in sorted(target.iterdir()):
                    entries.append(f"{'[DIR] ' if child.is_dir() else '[FILE]'} {child.name}")
                return "\n".join(entries) if entries else "(Empty directory)", False

            elif tool_name == "finish_task":
                tests_passed, test_log = self.check_workspace_tests(workspace)
                if not tests_passed:
                    return f"Cannot finish task yet: Tests are currently failing.\n{test_log}\nPlease fix the implementation using edit_file and run tests again.", False
                return f"Task marked complete: {args.get('summary', 'All tests green.')}", True

            else:
                return f"Error: Unknown tool {tool_name}", False

        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 20 seconds.", False
        except Exception as exc:
            return f"Error executing {tool_name}: {exc}", False

    def call_model(
        self,
        messages: List[Dict[str, Any]],
        scenario_key: str,
        turn: int,
    ) -> Tuple[Dict[str, Any], Dict[str, Any], float]:
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not configured in .env or environment")
        self._reserve_provider_call()

        payload = {
            "model": self.model_name,
            "messages": messages,
            "tools": HARNESS_TOOLS,
            "tool_choice": "auto",
            "temperature": 0.0,
            "max_tokens": 2048,
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

        last_err = None
        for attempt in range(3):
            t0 = time.perf_counter()
            try:
                with urllib.request.urlopen(req, timeout=35) as resp:
                    resp_bytes = resp.read()
                    millis = int((time.perf_counter() - t0) * 1000)
                    resp_json = json.loads(resp_bytes.decode("utf-8"))

                choice = resp_json.get("choices", [{}])[0]
                msg = choice.get("message", {})
                if not msg.get("tool_calls") and not msg.get("content"):
                    if attempt < 2:
                        time.sleep(1.5 * (attempt + 1))
                        continue

                reply_sha256 = hashlib.sha256(resp_bytes).hexdigest()
                usage = resp_json.get("usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)

                # Use centralized pricing table if available or upstream reported cost
                if self.model_name in self.pricing_table:
                    p_rate, c_rate, _ = self.pricing_table[self.model_name]
                    cost = ((prompt_tokens * p_rate) + (completion_tokens * c_rate)) / 1_000_000.0
                else:
                    cost = usage.get("cost", 0.0) or 0.0

                self._record_provider_call(
                    usage=usage, cost=cost,
                    model_resolved=str(resp_json.get("model") or self.model_name),
                    latency_ms=millis)

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
                            response=str(msg.get("content", ""))[:200],
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

            except urllib.error.HTTPError as err:
                err_body = err.read().decode("utf-8", errors="replace")
                last_err = RuntimeError(f"OpenRouter HTTP {err.code}: {err_body}")
                time.sleep(2.0 * (attempt + 1))
            except Exception as exc:
                last_err = exc
                time.sleep(2.0 * (attempt + 1))

        raise last_err or RuntimeError("Max retries exceeded")

    def run_challenge(self, challenge_dir: Path) -> ChallengeResult:
        cname = challenge_dir.name
        is_brownfield = challenge_dir.name.startswith(("01", "02", "03", "04", "05", "06", "07", "08", "09", "10"))
        kind = "Brownfield" if is_brownfield else "Greenfield"

        print(f"\n>>> Running [{kind}] Challenge: {cname} (Model: {self.model_name})")
        t_start = time.perf_counter()

        with tempfile.TemporaryDirectory(prefix=f"bench-run-{cname}-") as tmp_ws:
            ws_path = Path(tmp_ws)
            for item in challenge_dir.iterdir():
                if item.name in ("initial_state.sha256", "__pycache__", ".vanguard"):
                    continue
                if item.is_dir():
                    shutil.copytree(item, ws_path / item.name)
                else:
                    shutil.copy2(item, ws_path / item.name)

            file_list = []
            for root, dirs, files in os.walk(ws_path):
                for f in files:
                    rel = str(Path(root, f).relative_to(ws_path))
                    if not rel.startswith((".", "__")):
                        file_list.append(rel)

            file_list_str = "\n".join(f"- `{f}`" for f in sorted(file_list))

            if is_brownfield:
                spec_file = ws_path / "docs" / "SPEC.md"
                spec_content = spec_file.read_text(encoding="utf-8") if spec_file.exists() else ""
                user_brief = (
                    f"Task: Fix the bug in challenge `{cname}`.\n\n"
                    f"Workspace Files:\n{file_list_str}\n\n"
                    f"Specification (`docs/SPEC.md`):\n{spec_content}\n\n"
                    "Instructions:\n"
                    "1. View the source files in `src/` and test files in `test/`.\n"
                    "2. Run the test suite with `run_command` (e.g. `python3 -m unittest discover -s test`).\n"
                    "3. Edit `src/` files using `edit_file` to fix the bug according to the specification.\n"
                    "4. Re-run tests with `run_command` until 100% PASS.\n"
                    "5. Call `finish_task`."
                )
            else:
                readme_file = ws_path / "README.md"
                readme_content = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""
                user_brief = (
                    f"Task: Implement greenfield challenge `{cname}`.\n\n"
                    f"Workspace Files:\n{file_list_str}\n\n"
                    f"PRD Requirements (`README.md`):\n{readme_content}\n\n"
                    "Instructions:\n"
                    "1. View the test file in `test/` to see expected classes, methods, and behaviors.\n"
                    "2. Implement the required module(s) in `src/` using `edit_file`.\n"
                    "3. Run the test suite with `run_command` (e.g. `python3 -m unittest discover -s test`) until 100% PASS.\n"
                    "4. Call `finish_task`."
                )

            if self.preset in (FORGE_PRESET_NAME, "vg-1-forge"):
                cassettes = []
                model_adapter = BenchmarkOpenRouterModelPort(self, cname, cassettes)

                def local_command_runner(cmd: str, cwd: Path) -> Tuple[int, str]:
                    env = {
                        **os.environ,
                        "PYTHONPATH": f"{str(cwd.resolve())}:{str((cwd / 'src').resolve())}",
                        "PYTHONDONTWRITEBYTECODE": "1",
                    }
                    proc = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=cwd,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    return proc.returncode, (proc.stdout + "\n" + proc.stderr).strip()

                cfg = ForgeConfig(
                    max_turns=self.max_turns,
                    budget_limit_usd=max(0.0, self.budget_limit_usd - self.total_cost_usd),
                    require_patch_for_write=True,
                    model_name=self.model_name,
                )
                goal = GoalContract(
                    task_digest=hashlib.sha256(cname.encode()).hexdigest(),
                    mode="bugfix" if is_brownfield else "greenfield",
                )
                engine = ForgeFacade.create_engine(
                    workspace_root=ws_path,
                    model_port=model_adapter,
                    config=cfg,
                    command_runner=local_command_runner,
                )
                outcome = engine.run_episode(task_brief=user_brief, goal_contract=goal)

                # Final Oracle Evaluation
                oracle_passed, test_summary = self.check_workspace_tests(ws_path)
                status = "PASS" if oracle_passed else "FAIL"
                diagnosis = "All falsifiers green" if oracle_passed else (test_summary[:120].replace("\n", " ") if test_summary else "Unknown failure")

                total_latency = time.perf_counter() - t_start
                challenge_cost = model_adapter.total_cost
                self.total_cost_usd += challenge_cost

                # Save Cassette
                cassette_file = CAPTURES_DIR / f"{cname}_cassette.json"
                cassette_file.write_text(json.dumps(cassettes, indent=2), encoding="utf-8")

                print(f"  Result [1-Forge]: [{status}] in {outcome.turns} turns | {model_adapter.total_prompt_tok + model_adapter.total_comp_tok} tokens | ${challenge_cost:.5f} | {total_latency:.2f}s")

                return ChallengeResult(
                    challenge_id=cname,
                    kind=kind,
                    model=self.model_name,
                    status=status,
                    turns=outcome.turns,
                    prompt_tokens=model_adapter.total_prompt_tok,
                    completion_tokens=model_adapter.total_comp_tok,
                    total_tokens=model_adapter.total_prompt_tok + model_adapter.total_comp_tok,
                    cost_usd=challenge_cost,
                    latency_seconds=round(total_latency, 2),
                    diagnosis=diagnosis,
                    trajectory=outcome.trajectory,
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
                raw_tool_calls = message.get("tool_calls") or []
                content_str = message.get("content") or ""

                cleaned_content = re.sub(r"Use the results below to formulate an answer to the user question[^\.]*\.", "", content_str).strip()

                parsed_calls = []
                if raw_tool_calls:
                    seen_calls = set()
                    for idx, tc in enumerate(raw_tool_calls):
                        fn_name = tc.get("function", {}).get("name")
                        raw_args = tc.get("function", {}).get("arguments", "{}")
                        call_key = (fn_name, raw_args if isinstance(raw_args, str) else json.dumps(raw_args, sort_keys=True))
                        if call_key in seen_calls:
                            continue
                        seen_calls.add(call_key)

                        try:
                            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                        except Exception:
                            args = {}
                        parsed_calls.append({"id": tc.get("id", f"call_{idx}"), "name": fn_name, "arguments": args})
                else:
                    extracted = extract_tool_calls_from_content(content_str)
                    for idx, ec in enumerate(extracted):
                        parsed_calls.append({"id": f"extracted_{idx}", "name": ec["name"], "arguments": ec["arguments"]})

                parsed_calls = parsed_calls[:4]

                clean_assistant_msg = {
                    "role": "assistant",
                    "content": cleaned_content if not parsed_calls else None,
                }
                if parsed_calls:
                    clean_assistant_msg["tool_calls"] = [
                        {
                            "id": pc["id"],
                            "type": "function",
                            "function": {
                                "name": pc["name"],
                                "arguments": json.dumps(pc["arguments"])
                            }
                        }
                        for pc in parsed_calls
                    ]

                messages.append(clean_assistant_msg)

                if not parsed_calls:
                    trajectory.append({
                        "turn": turn,
                        "assistant_text": cleaned_content
                    })
                    tests_ok, _ = self.check_workspace_tests(ws_path)
                    if tests_ok:
                        finished = True
                        break

                    if turn < self.max_turns:
                        messages.append({
                            "role": "user",
                            "content": "Please proceed by using tools (edit_file, run_command, finish_task) to complete the implementation and ensure all tests pass."
                        })
                    continue

                turn_actions = []
                for pc in parsed_calls:
                    fn_name = pc["name"]
                    args = pc["arguments"]
                    tool_res, is_fin = self.execute_tool(fn_name, args, ws_path)
                    turn_actions.append({
                        "tool": fn_name,
                        "args": args,
                        "result_snippet": tool_res[:150],
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": pc["id"],
                        "content": tool_res
                    })

                    if is_fin:
                        finished = True

                trajectory.append({
                    "turn": turn,
                    "actions": turn_actions
                })
                tools_run = [a["tool"] for a in turn_actions]
                print(f"  Turn {turn}: Executed {tools_run} (Cost: ${call_cost:.5f})")

            # Final Oracle Evaluation
            oracle_passed, test_summary = self.check_workspace_tests(ws_path)
            status = "PASS" if oracle_passed else "FAIL"
            diagnosis = "All falsifiers green" if oracle_passed else (test_summary[:120].replace("\n", " ") if test_summary else "Unknown failure")

            total_latency = time.perf_counter() - t_start
            self.total_cost_usd += challenge_cost

            # Save Cassette
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
    parser.add_argument("--model", default=None, help="Model identifier or alias (defaults to centralized config: get_default_paid_model())")
    parser.add_argument("--preset", default="vg-code-max", choices=["vg-code-max", "vg-1-forge"], help="Harness preset (vg-code-max or vg-1-forge)")
    parser.add_argument("--max-turns", type=int, default=8, help="Max turns per challenge")
    parser.add_argument("--budget", type=float, default=0.20, help="Max USD budget")
    parser.add_argument("--single", default=None, help="Run single challenge name for debugging")
    args = parser.parse_args()

    recorder = MockRecorder(LAM_SQLITE_PATH) if MockRecorder else None
    runner = BenchmarkRunner(
        model_name=args.model,
        preset=args.preset,
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

    report_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": runner.model_name,
        "harness": f"vanguard-{runner.preset}",
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
    out_file = SUITE_ROOT / f"benchmark_20_results_{runner.preset.replace('-', '_')}.json"
    out_file.write_text(json.dumps(report_data, indent=2), encoding="utf-8")
    if runner.preset == "vg-code-max":
        (SUITE_ROOT / "benchmark_20_results.json").write_text(json.dumps(report_data, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
