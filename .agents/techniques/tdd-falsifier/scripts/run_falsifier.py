#!/usr/bin/env python3
"""
Technique 2: TDD Falsifier
Combines lda-navigator (graph-indexed test lookup) with test-runner (atomic isolated execution)
to locate and execute targeted test falsifiers for any code target, returning a DiagnosticReport.
"""

import sys
import os
import json
import time
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import atomic test-runner
TEST_RUNNER_DIR = Path(__file__).resolve().parents[3] / "skills" / "test-runner" / "scripts"
sys.path.insert(0, str(TEST_RUNNER_DIR))
try:
    from run_test import run_isolated_test
except ImportError:
    # Fallback inline if module path issues
    def run_isolated_test(cmd, timeout=15.0, cwd="."):
        t0 = time.time()
        p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return {
            "command": cmd,
            "success": p.returncode == 0,
            "exit_code": p.returncode,
            "duration_seconds": round(time.time() - t0, 3),
            "timed_out": False,
            "stdout": p.stdout,
            "stderr": p.stderr,
            "failures": []
        }

def find_falsifiers_via_lda(target_path: str) -> List[str]:
    """Queries LDA index for correlated test suites, prioritizing native repository tests."""
    candidates = []
    try:
        res = subprocess.run(
            ["uv", "run", "lda", "tests", target_path, "--json"],
            capture_output=True,
            text=True
        )
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            candidates = data.get("suggested_commands", [])
    except Exception:
        pass

    # Heuristic fallback: maps vanguard/packages/<subsystem>/<name>.py -> test/<subsystem>/test_<name>.py
    clean_path = target_path.replace("\\", "/")
    parts = clean_path.split("/")
    if "vanguard" in parts and "packages" in parts:
        try:
            subsystem_idx = parts.index("packages") + 1
            subsystem = parts[subsystem_idx]
            filename = parts[-1]
            if filename.endswith(".py"):
                mod_name = filename[:-3]
                test_candidate = f"test/{subsystem}/test_{mod_name}.py"
                if os.path.exists(test_candidate):
                    candidates.append(f"python3 -m unittest test.{subsystem}.test_{mod_name} -v")
        except Exception:
            pass

    def rank_test(cmd: str) -> int:
        score = 0
        if "test.broken" in cmd or "fixtures" in cmd or "fakes" in cmd:
            score -= 100
        if "benchmarks." in cmd:
            score -= 50
        # Give highest boost to test matching file name directly
        target_name = parts[-1].replace(".py", "")
        if f"test_{target_name}" in cmd or f".{target_name}" in cmd:
            score += 150
        for part in clean_path.split("/"):
            if len(part) > 3 and part in cmd:
                score += 20
        if "test.kernel." in cmd or "test.agency." in cmd or "test.domain." in cmd or "test.packs." in cmd:
            score += 15
        return score

    if candidates:
        candidates.sort(key=rank_test, reverse=True)
        return candidates

    return []

def run_falsifier(
    target_path: Optional[str] = None,
    explicit_cmd: Optional[str] = None,
    timeout: float = 15.0,
    cwd: str = "."
) -> Dict[str, Any]:
    test_cmd = explicit_cmd

    if not test_cmd and target_path:
        suggested = find_falsifiers_via_lda(target_path)
        if suggested:
            test_cmd = suggested[0]

    if not test_cmd:
        return {
            "status": "NO_TESTS_FOUND",
            "success": False,
            "target": target_path,
            "test_command": None,
            "duration_seconds": 0.0,
            "failure_summary": f"No test falsifier mapped to {target_path}",
            "failures": []
        }

    # Execute isolated test
    test_res = run_isolated_test(test_cmd, timeout=timeout, cwd=cwd)

    # Derive status
    if test_res.get("timed_out"):
        status = "TIMEOUT"
        summary = f"Test timed out after {timeout}s"
    elif test_res.get("success"):
        status = "PASS"
        summary = "All tests passed successfully"
    else:
        status = "FAIL"
        err_msg = ""
        if test_res.get("failures"):
            f = test_res["failures"][0]
            err_msg = f"{f['test']}: {f['traceback'].splitlines()[-1]}"
        elif test_res.get("stderr"):
            err_msg = test_res["stderr"].strip().splitlines()[-1]
        summary = err_msg or f"Test failed with exit code {test_res.get('exit_code')}"

    return {
        "status": status,
        "success": status == "PASS",
        "target": target_path,
        "test_command": test_cmd,
        "duration_seconds": test_res.get("duration_seconds", 0.0),
        "failure_summary": summary,
        "failures": test_res.get("failures", []),
        "raw_stdout": test_res.get("stdout", ""),
        "raw_stderr": test_res.get("stderr", "")
    }

def main():
    parser = argparse.ArgumentParser(description="Technique 2: TDD Falsifier")
    parser.add_argument("target", nargs="?", help="Target file path to falsify")
    parser.add_argument("--target", dest="target_opt", help="Target file path to falsify")
    parser.add_argument("--test-cmd", help="Explicit test command to execute")
    parser.add_argument("--timeout", type=float, default=15.0, help="Execution timeout in seconds")
    parser.add_argument("--cwd", default=".", help="Working directory")
    parser.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()
    target = args.target_opt or args.target
    if not target and not args.test_cmd:
        parser.print_help()
        sys.exit(1)

    result = run_falsifier(
        target_path=target,
        explicit_cmd=args.test_cmd,
        timeout=args.timeout,
        cwd=args.cwd
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        sym = "✅" if result["success"] else "❌"
        print(f"{sym} Status: {result['status']}")
        print(f"Command: {result['test_command']}")
        print(f"Duration: {result['duration_seconds']}s")
        print(f"Summary: {result['failure_summary']}")

    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()
