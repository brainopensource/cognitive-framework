#!/usr/bin/env python3
"""
Atomic Skill: Test Runner
Executes tests in an isolated, timeout-bounded subprocess, capturing exit code,
durations, stdout, stderr, and structured test failure/error diagnostics.
"""

import sys
import os
import re
import json
import time
import argparse
import subprocess
from typing import Dict, Any, List

def run_isolated_test(command: str, timeout: float = 15.0, cwd: str = ".") -> Dict[str, Any]:
    start_time = time.time()
    timed_out = False
    stdout_str = ""
    stderr_str = ""
    exit_code = -1

    try:
        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        try:
            stdout_str, stderr_str = proc.communicate(timeout=timeout)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            stdout_str, stderr_str = proc.communicate()
            exit_code = 124
    except Exception as exc:
        stderr_str = f"Execution failed to launch: {exc}"
        exit_code = 127

    duration = time.time() - start_time
    combined_output = f"{stdout_str}\n{stderr_str}".strip()

    # Parse failure details
    failures: List[Dict[str, str]] = []
    
    # Match unittest/pytest style failures with optional multiline docstrings
    fail_matches = re.findall(
        r"(FAIL|ERROR):\s+([^\s]+)\s+\(([^)]+)\)\n.*?\n[-=]{40,}\n(Traceback.*?(?:\n[A-Z][a-zA-Z0-9_]*Error:.*?(?=\n\n|\n=|\n-|$)|$))",
        combined_output,
        re.DOTALL
    )
    for kind, method, cls, tb in fail_matches:
        failures.append({
            "kind": kind,
            "test": f"{cls}.{method}",
            "traceback": tb.strip()
        })

    # Summary regex
    failed_summary_match = re.search(r"FAILED\s*\((?:failures=(\d+))?(?:,\s*)?(?:errors=(\d+))?\)", combined_output)
    failures_count = int(failed_summary_match.group(1) or 0) if failed_summary_match else (len(failures) if exit_code != 0 else 0)
    errors_count = int(failed_summary_match.group(2) or 0) if failed_summary_match else 0

    success = (exit_code == 0) and not timed_out

    return {
        "command": command,
        "success": success,
        "exit_code": exit_code,
        "duration_seconds": round(duration, 3),
        "timed_out": timed_out,
        "failures_count": failures_count,
        "errors_count": errors_count,
        "failures": failures,
        "stdout": stdout_str,
        "stderr": stderr_str,
        "summary": "OK" if success else (
            f"TIMED_OUT ({timeout}s)" if timed_out else f"FAILED (failures={failures_count}, errors={errors_count})"
        )
    }

def main():
    parser = argparse.ArgumentParser(description="Atomic Test Runner for Hermetic Verification")
    parser.add_argument("test_cmd", nargs="?", default="", help="Command to execute")
    parser.add_argument("--test-cmd", dest="cmd_opt", help="Command to execute")
    parser.add_argument("--timeout", type=float, default=15.0, help="Timeout in seconds (default 15.0)")
    parser.add_argument("--cwd", default=".", help="Current working directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    cmd = args.cmd_opt or args.test_cmd
    if not cmd:
        parser.print_help()
        sys.exit(1)

    result = run_isolated_test(cmd, timeout=args.timeout, cwd=args.cwd)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status_sym = "✅" if result["success"] else "❌"
        print(f"{status_sym} Command: {result['command']}")
        print(f"Status: {result['summary']} (exit {result['exit_code']}) in {result['duration_seconds']}s")
        if not result["success"]:
            for f in result["failures"]:
                print(f"\n--- {f['kind']}: {f['test']} ---")
                print(f['traceback'])
            if not result["failures"] and result["stderr"]:
                print("\nStderr output:\n" + result["stderr"][:1000])

    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()
