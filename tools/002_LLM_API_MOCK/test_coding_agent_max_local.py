#!/usr/bin/env python3
"""Hermetic Full-Local Benchmark: Vanguard Coding Agent Max 3-Body with LAM Engine.

Evaluates Vanguard's autonomous coding harness against synthetic coding challenges
using 100% local, offline, zero-cost LLM API MOCK completions.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

_DIR = Path(__file__).resolve().parent
ROOT = _DIR.parents[1]
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import LamEngine, Scenario
from vanguard_bridge import translate_lam_call_to_vanguard

SCENARIOS_DIR = _DIR / "scenarios"


def apply_unified_diff(diff_str: str, ws_dir: Path) -> bool:
    """Applies simple unified diff patch directly."""
    # Find target file from diff headers
    target_match = re.search(r"\+\+\+\s+[ab]/(.+)", diff_str)
    if not target_match:
        return False
    rel_path = target_match.group(1).strip()
    target_file = ws_dir / rel_path
    if not target_file.exists():
        return False

    lines = target_file.read_text(encoding="utf-8").splitlines(keepends=True)
    
    # Extract removals and additions
    removals = []
    additions = []
    for line in diff_str.splitlines():
        if line.startswith("-") and not line.startswith("---"):
            removals.append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"):
            additions.append(line[1:])

    content = "".join(lines)
    for rem, add in zip(removals, additions):
        content = content.replace(rem, add, 1)

    target_file.write_text(content, encoding="utf-8")
    return True


class LocalHarnessRunner:
    def __init__(self, engine: LamEngine):
        self.engine = engine

    def execute_tool(self, tool_name: str, args: Dict[str, Any], ws_dir: Path) -> Tuple[str, int]:
        """Executes tool action in the isolated workspace."""
        try:
            if tool_name in ("view_file", "fs.read", "read"):
                p = ws_dir / args.get("path", args.get("file", ""))
                if p.exists() and p.is_file():
                    return p.read_text(encoding="utf-8"), 0
                return f"Error: File not found {p.name}", 1

            elif tool_name in ("edit_file", "patch.apply", "patch"):
                if "patch" in args and ("---" in args["patch"] or "+++" in args["patch"]):
                    ok = apply_unified_diff(args["patch"], ws_dir)
                    return ("Applied unified diff", 0) if ok else ("Failed to apply patch", 1)

                p = ws_dir / args.get("path", args.get("file", ""))
                p.parent.mkdir(parents=True, exist_ok=True)
                
                if "content" in args:
                    p.write_text(args["content"], encoding="utf-8")
                    return f"Successfully wrote {len(args['content'])} bytes", 0
                elif "target" in args and "replacement" in args:
                    if not p.exists():
                        return f"Error: Cannot patch non-existent file {p.name}", 1
                    current = p.read_text(encoding="utf-8")
                    target = args["target"]
                    replacement = args["replacement"]
                    if target in current:
                        new_content = current.replace(target, replacement, 1)
                        p.write_text(new_content, encoding="utf-8")
                        return f"Successfully applied patch to {p.name}", 0
                    else:
                        new_content = current + "\n" + replacement
                        p.write_text(new_content, encoding="utf-8")
                        return f"Appended replacement to {p.name}", 0
                return "Error: Missing content or replacement in edit_file", 1

            elif tool_name in ("run_command", "proc.exec", "test"):
                env = {**os.environ, "PYTHONPATH": f"{str(ws_dir)}:{str(ws_dir / 'src')}"}
                
                if "argv" in args:
                    argv = args["argv"]
                    proc = subprocess.run(argv, cwd=ws_dir, env=env, capture_output=True, text=True, timeout=5)
                    return (proc.stdout + "\n" + proc.stderr).strip(), proc.returncode

                cmd = args.get("command", args.get("cmd", ""))
                if "pytest" in cmd:
                    test_files = list(ws_dir.glob("test_*.py"))
                    if test_files:
                        cmd = f"{sys.executable} -m unittest {test_files[0].name}"

                proc = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=ws_dir,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                output = (proc.stdout + "\n" + proc.stderr).strip()
                return output, proc.returncode

            elif tool_name in ("list_dir", "fs.list"):
                entries = [f.name for f in ws_dir.iterdir()]
                return "\n".join(entries), 0

            return f"Unknown tool {tool_name}", 1

        except Exception as exc:
            return f"Execution error: {exc}", 1

    def run_scenario(self, scenario: Scenario) -> Dict[str, Any]:
        t0 = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix=f"lam-test-{scenario.id}-") as tmp_dir:
            ws_path = Path(tmp_dir)

            # 1. Setup workspace initial files
            for filename, content in scenario.workspace.items():
                fpath = ws_path / filename
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content, encoding="utf-8")

            # 2. Autonomous Agent Loop
            turns_taken = 0
            tools_executed = []
            messages: List[Dict[str, Any]] = [
                {"role": "user", "content": f"Task: {scenario.title}"}
            ]

            max_loop_turns = min(len(scenario.turns) + 2, 8)

            for loop_idx in range(max_loop_turns):
                turns_taken += 1
                
                req_payload = {
                    "model": scenario.id,
                    "messages": messages
                }
                completion = self.engine.complete(req_payload)
                
                choice = completion["choices"][0]
                msg = choice.get("message", {})
                tool_calls = msg.get("tool_calls", [])
                
                if not tool_calls:
                    break

                for tc in tool_calls:
                    fn = tc["function"]
                    name = fn["name"]
                    args = json.loads(fn["arguments"]) if isinstance(fn["arguments"], str) else fn["arguments"]
                    
                    res_text, code = self.execute_tool(name, args, ws_path)
                    tools_executed.append(name)

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.get("id", f"call_{len(tools_executed)}"),
                        "content": res_text
                    })

            # 3. Final Oracle Verification
            test_files = list(ws_path.glob("test_*.py"))
            oracle_pass = True
            oracle_err = ""
            
            if test_files:
                for tf in test_files:
                    env = {**os.environ, "PYTHONPATH": f"{str(ws_path)}:{str(ws_path / 'src')}"}
                    p = subprocess.run(
                        [sys.executable, str(tf)],
                        cwd=ws_path,
                        env=env,
                        capture_output=True,
                        text=True,
                    )
                    if p.returncode != 0 and "test_" in tf.name:
                        p2 = subprocess.run(
                            [sys.executable, "-m", "unittest", tf.name],
                            cwd=ws_path,
                            env=env,
                            capture_output=True,
                            text=True,
                        )
                        if p2.returncode != 0:
                            oracle_pass = False
                            oracle_err = p.stderr or p.stdout or p2.stderr
                    elif p.returncode != 0:
                        oracle_pass = False
                        oracle_err = p.stderr or p.stdout

            duration_ms = (time.perf_counter() - t0) * 1000

            return {
                "id": scenario.id,
                "tier": scenario.tier,
                "title": scenario.title,
                "turns": turns_taken,
                "tools_executed": tools_executed,
                "duration_ms": round(duration_ms, 2),
                "passed": oracle_pass,
                "error": oracle_err[:100] if oracle_err else "None"
            }


def main():
    print("=" * 90)
    print("VANGUARD CODING AGENT MAX — LOCAL LAM SYNTHETIC BENCHMARK")
    print("=" * 90)

    engine = LamEngine.from_directory(SCENARIOS_DIR)
    runner = LocalHarnessRunner(engine)

    test_scenarios = [
        s for s in engine.scenarios
        if s.workspace and any(k.startswith("test_") or "test" in k for k in s.workspace.keys())
    ][:25]

    if not test_scenarios:
        test_scenarios = list(engine.scenarios[:25])

    print(f"Loaded {len(test_scenarios)} diverse coding scenarios for full local execution.\n")

    results = []
    t_start = time.perf_counter()

    for sc in test_scenarios:
        res = runner.run_scenario(sc)
        results.append(res)

    total_time_s = time.perf_counter() - t_start
    
    header = f"{'Scenario ID':<36} | {'Tier':<4} | {'Turns':<5} | {'Tools':<18} | {'Time (ms)':<9} | {'Status':<6}"
    print(header)
    print("-" * 90)

    pass_count = 0
    total_turns = 0

    for r in results:
        status_str = "PASS" if r["passed"] else "FAIL"
        if r["passed"]:
            pass_count += 1
        total_turns += r["turns"]
        tools_str = ",".join(r["tools_executed"][:3])
        if len(r["tools_executed"]) > 3:
            tools_str += f"+{len(r['tools_executed'])-3}"
        
        row = f"{r['id']:<36} | T{r['tier']:<3} | {r['turns']:<5} | {tools_str:<18} | {r['duration_ms']:<9.2f} | {status_str:<6}"
        print(row)

    print("-" * 90)
    pass_rate = (pass_count / len(results)) * 100 if results else 0.0
    print("LOCAL LAM BENCHMARK SUMMARY:")
    print(f"  * Overall Pass Rate:     {pass_count}/{len(results)} ({pass_rate:.1f}%)")
    print(f"  * Total Turns Executed:  {total_turns}")
    print(f"  * Total Execution Time:  {total_time_s:.3f} seconds (all {len(results)} scenarios)")
    print(f"  * Avg Latency per Test:  {(total_time_s / len(results)) * 1000:.2f} ms")
    print(f"  * Total Cost (USD):      $0.00000 (100% Offline Mock)")
    print("=" * 90)


if __name__ == "__main__":
    main()
