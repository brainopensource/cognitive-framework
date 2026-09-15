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
import signal
from typing import Dict, Any, List

def run_isolated_test(command: str, timeout: float = 15.0, cwd: str = ".") -> Dict[str, Any]:
    start_time = time.time()
    timed_out = False
    stdout_str = ""
    stderr_str = ""
    exit_code = -1

    try:
        env = dict(os.environ)
        resolved_cwd = os.path.abspath(cwd)
        curr_pp = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = f"{resolved_cwd}:{curr_pp}" if curr_pp else resolved_cwd

        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout_str, stderr_str = proc.communicate(timeout=timeout)
            exit_code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                proc.terminate()
            try:
                stdout_str, stderr_str = proc.communicate(timeout=min(1.0, max(0.1, timeout)))
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except (ProcessLookupError, PermissionError):
                    proc.kill()
                try:
                    stdout_str, stderr_str = proc.communicate(timeout=2.0)
                except subprocess.TimeoutExpired:
                    stderr_str = f"{stderr_str}\n[runner] process group survived SIGKILL".strip()
            exit_code = 124
    except Exception as exc:
        stderr_str = f"Execution failed to launch: {exc}"
        exit_code = 127

    duration = time.time() - start_time
    combined_output = f"{stdout_str}\n{stderr_str}".strip()

    # Parse failure details one separator-delimited block at a time. This
    # prevents a traceback from one test consuming the next test's header.
    failures: List[Dict[str, str]] = []
    block_re = re.compile(
        r"^(FAIL|ERROR):\s+([^\s]+)\s+\(([^)]+)\)(?:\s+.*)?$",
        re.MULTILINE,
    )
    headers = list(block_re.finditer(combined_output))
    for index, header in enumerate(headers):
        kind, method, owner = header.groups()
        test_name = owner if owner.endswith("." + method) else f"{owner}.{method}"
        end = headers[index + 1].start() if index + 1 < len(headers) else len(combined_output)
        body = combined_output[header.end():end].strip()
        body = re.sub(r"(?m)^[-=]{40,}\s*$", "", body).strip()
        footer = re.search(r"(?m)^Ran\s+\d+\s+tests?\s+in\b", body)
        if footer:
            body = body[:footer.start()].strip()
        failures.append({
            "kind": kind,
            "test": test_name,
            "traceback": body,
        })

    # The final unittest summary is the only authoritative count. Parse its
    # comma-separated name=count bag without relying on key ordering.
    summary_matches = list(re.finditer(
        r"(?m)^(?P<status>OK|FAILED)(?:\s*\((?P<details>[^)]*)\))?\s*$",
        combined_output,
    ))
    counts: Dict[str, int] = {}
    counts_parsed = bool(summary_matches)
    total_match = list(re.finditer(r"(?m)^Ran\s+(\d+)\s+tests?\s+in\s+", combined_output))
    total_count = int(total_match[-1].group(1)) if total_match else None
    if summary_matches:
        details = summary_matches[-1].group("details") or ""
        pairs = re.findall(r"([A-Za-z][A-Za-z ]*?)\s*=\s*(\d+)", details)
        remainder = re.sub(r"([A-Za-z][A-Za-z ]*?)\s*=\s*(\d+)", "", details)
        keys = [key.strip() for key, _ in pairs]
        if details and (not pairs or remainder.replace(",", "").strip() or len(keys) != len(set(keys))):
            counts_parsed = False
        else:
            counts = {key.strip(): int(value) for key, value in pairs}
    if counts_parsed:
        failures_count = counts.get("failures", 0)
        errors_count = counts.get("errors", 0)
        skipped_count = counts.get("skipped", 0)
    else:
        # A parse miss never reads as zero. Infer only the kinds actually seen
        # as blocks; a kind with no block is unknown, not proven absent.
        observed_failures = [f for f in failures if f["kind"] == "FAIL"]
        observed_errors = [f for f in failures if f["kind"] == "ERROR"]
        failures_count = len(observed_failures) or None
        errors_count = len(observed_errors) or None
        skipped_count = None

    success = (exit_code == 0) and not timed_out

    parsed_summary = "unknown"
    if counts_parsed:
        fields = ", ".join(f"{key}={value}" for key, value in counts.items())
        parsed_summary = fields or "none"
    if total_count is not None:
        parsed_summary = f"total={total_count}; {parsed_summary}"

    return {
        "command": command,
        "success": success,
        "exit_code": exit_code,
        "duration_seconds": round(duration, 3),
        "timed_out": timed_out,
        "failures_count": failures_count,
        "errors_count": errors_count,
        "skipped_count": skipped_count,
        "total_count": total_count,
        "counts": counts,
        "counts_parsed": counts_parsed,
        "failures": failures,
        "stdout": stdout_str,
        "stderr": stderr_str,
        "summary": (
            f"OK ({parsed_summary})" if success else
            f"TIMED_OUT ({timeout}s; {parsed_summary})" if timed_out else
            f"FAILED ({parsed_summary})"
        ),
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
