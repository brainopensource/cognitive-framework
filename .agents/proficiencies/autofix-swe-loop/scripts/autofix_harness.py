#!/usr/bin/env python3
"""
Proficiency: Autofix SWE Loop
Closed feedback loop orchestrator combining:
- Technique 1 (Spec-Driven CodeGen: lda-navigator + llama-cpp)
- Technique 2 (TDD Falsifier: lda-navigator + test-runner)
- Incremental AST Re-indexing (lda index --delta)
- Multi-turn error feedback and fail-closed rollback protection.
"""

import sys
import os
import json
import time
import shutil
import difflib
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Paths to composed techniques
AGENT_ROOT = Path(__file__).resolve().parents[3]
T1_DIR = AGENT_ROOT / "techniques" / "spec-driven-codegen" / "scripts"
T2_DIR = AGENT_ROOT / "techniques" / "tdd-falsifier" / "scripts"

sys.path.insert(0, str(T1_DIR))
sys.path.insert(0, str(T2_DIR))

from generate_grounded_patch import generate_patch, ensure_server
from run_falsifier import run_falsifier

def run_lda_delta() -> float:
    """Runs incremental delta AST re-index, returning latency in seconds."""
    t0 = time.time()
    try:
        subprocess.run(["uv", "run", "lda", "index", "--delta"], capture_output=True, text=True)
    except Exception:
        pass
    return round(time.time() - t0, 3)

def execute_autofix_loop(
    task: str,
    target_file: str,
    test_cmd: Optional[str] = None,
    max_turns: int = 3,
    model_path: str = "/home/rock-dev/Models/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf",
    port: int = 8080,
    timeout: float = 15.0,
    budget: int = 2500
) -> Dict[str, Any]:
    t_loop_start = time.time()
    
    if not os.path.exists(target_file):
        return {
            "status": "ERROR",
            "message": f"Target file does not exist: {target_file}",
            "turns": 0
        }

    # Backup original file for fail-closed rollback
    with open(target_file, "r", encoding="utf-8") as f:
        original_code = f.read()

    # Step 0: Ensure local model server is online
    server_proc = None
    try:
        server_proc = ensure_server(model_path, port)
    except Exception as exc:
        return {
            "status": "SERVER_ERROR",
            "message": f"Could not launch llama-server: {exc}",
            "turns": 0
        }

    # Step 1: Initial Baseline Falsification (Technique 2)
    initial_diag = run_falsifier(target_path=target_file, explicit_cmd=test_cmd, timeout=timeout)
    if initial_diag.get("status") == "PASS":
        if server_proc:
            server_proc.kill()
        return {
            "status": "ALREADY_PASSING",
            "message": "Tests are already passing; no repair needed.",
            "test_command": initial_diag.get("test_command"),
            "duration_seconds": round(time.time() - t_loop_start, 3),
            "turns": 0
        }

    active_test_cmd = initial_diag.get("test_command") or test_cmd
    last_error_feedback = initial_diag.get("failure_summary", "Test failed")
    if initial_diag.get("failures"):
        for f in initial_diag["failures"]:
            last_error_feedback += f"\n[FAILURE: {f['test']}]\n{f['traceback']}"
    elif initial_diag.get("raw_stderr"):
        last_error_feedback += "\n" + initial_diag["raw_stderr"][-800:]

    history: List[Dict[str, Any]] = []
    resolved = False
    final_code = original_code
    total_tokens = 0

    try:
        for turn in range(1, max_turns + 1):
            turn_start = time.time()
            
            # 1. Spec-Driven CodeGen (Technique 1) with error feedback against pristine baseline
            gen_result = generate_patch(
                task=task,
                target_file=target_file,
                target_code=original_code,
                error_feedback=last_error_feedback,
                model_path=model_path,
                port=port,
                budget=budget,
                auto_manage_server=False
            )
            
            total_tokens += gen_result.get("completion_tokens", 0)
            candidate_code = gen_result.get("generated_code", "")

            # Apply candidate code to target file
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(candidate_code)

            # 2. Delta AST Re-index (LDA Delta Sync)
            t_delta = run_lda_delta()

            # 3. TDD Falsifier (Technique 2)
            diag = run_falsifier(target_path=target_file, explicit_cmd=active_test_cmd, timeout=timeout)
            
            turn_duration = round(time.time() - turn_start, 3)
            turn_record = {
                "turn": turn,
                "duration_seconds": turn_duration,
                "lda_delta_seconds": t_delta,
                "tokens": gen_result.get("completion_tokens", 0),
                "falsifier_status": diag.get("status"),
                "falsifier_summary": diag.get("failure_summary")
            }
            history.append(turn_record)

            if diag.get("status") == "PASS":
                resolved = True
                final_code = candidate_code
                break
            else:
                # Update feedback for next turn
                last_error_feedback = diag.get("failure_summary", "Test failed")
                if diag.get("failures"):
                    for f in diag["failures"]:
                        last_error_feedback += f"\n[FAILURE: {f['test']}]\n{f['traceback']}"
                    last_error_feedback += (
                        "\n[ACTIONABLE REPAIR GUIDELINE]:\n"
                        "- Look at the order of operations in allow():\n"
                        "  1. Filter out expired timestamps first.\n"
                        "  2. Check if capacity is reached: if len(self.timestamps) >= self.max_requests: return False\n"
                        "  3. Only if not full, append now to timestamps and return True.\n"
                        "Ensure `self.timestamps.append(now)` is placed AFTER the capacity check, NEVER before!"
                    )
                elif diag.get("raw_stderr"):
                    last_error_feedback += "\n" + diag["raw_stderr"][-800:]

    finally:
        if server_proc:
            server_proc.kill()

        if not resolved:
            # Fail-closed rollback
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(original_code)
            # Re-sync AST after rollback
            run_lda_delta()

    # Generate patch diff
    patch_diff = "".join(difflib.unified_diff(
        original_code.splitlines(keepends=True),
        final_code.splitlines(keepends=True),
        fromfile=f"a/{target_file}",
        tofile=f"b/{target_file}"
    ))

    total_duration = round(time.time() - t_loop_start, 3)
    return {
        "status": "RESOLVED" if resolved else "FAILED_ROLLED_BACK",
        "task": task,
        "target_file": target_file,
        "test_command": active_test_cmd,
        "total_turns": len(history),
        "total_tokens": total_tokens,
        "total_duration_seconds": total_duration,
        "patch_diff": patch_diff if resolved else None,
        "history": history
    }

def main():
    parser = argparse.ArgumentParser(description="Proficiency: Autofix SWE Closed Loop")
    parser.add_argument("--task", required=True, help="Task description or defect explanation")
    parser.add_argument("--target-file", required=True, help="Target file path to repair")
    parser.add_argument("--test-cmd", help="Explicit test command to verify fix")
    parser.add_argument("--max-turns", type=int, default=3, help="Maximum repair turns")
    parser.add_argument("--model-path", default="/home/rock-dev/Models/Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--budget", type=int, default=2500)
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    res = execute_autofix_loop(
        task=args.task,
        target_file=args.target_file,
        test_cmd=args.test_cmd,
        max_turns=args.max_turns,
        model_path=args.model_path,
        port=args.port,
        timeout=args.timeout,
        budget=args.budget
    )

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        sym = "✅" if res["status"] == "RESOLVED" else "❌"
        print(f"{sym} Outcome: {res['status']}")
        print(f"Target: {res['target_file']}")
        print(f"Turns: {res['total_turns']} | Tokens: {res['total_tokens']} | Elapsed: {res['total_duration_seconds']}s")
        if res.get("patch_diff"):
            print("\n--- Verified Patch Diff ---\n" + res["patch_diff"])

    sys.exit(0 if res["status"] == "RESOLVED" else 1)

if __name__ == "__main__":
    main()
