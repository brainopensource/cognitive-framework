"""BaaC External Oracle Verification Engine.

CRITICAL INVARIANTS:
1. Oracle verification scripts live in `challenges/<tier>/<challenge>/oracle/verify.py`.
2. Oracle files are NEVER copied to the agent scratch workspace.
3. The oracle is executed strictly after the agent finishes its episode to compute the ground truth score.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True, slots=True)
class OracleResult:
    """Ground-truth evaluation outcome from external oracle."""

    passed: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    error: str | None = None
    assertion_count: int = 0
    failing_assertions: tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "exitCode": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "durationSeconds": self.duration_seconds,
            "error": self.error,
            "assertionCount": self.assertion_count,
            "failingAssertions": list(self.failing_assertions),
        }


def parse_oracle_output(stdout: str, stderr: str, exit_code: int) -> Tuple[int, tuple[str, ...]]:
    """Extract assertion count and failed test names from oracle output."""
    failing: List[str] = []
    assertion_count = 0

    combined = stdout + "\n" + stderr

    # Check for unittest Ran X tests
    ran_m = re.search(r"Ran (\d+) tests?", combined)
    if ran_m:
        assertion_count = int(ran_m.group(1))

    # Check for pytest X passed, Y failed
    pyt_passed = re.search(r"(\d+) passed", combined)
    pyt_failed = re.search(r"(\d+) failed", combined)
    if pyt_passed or pyt_failed:
        p_c = int(pyt_passed.group(1)) if pyt_passed else 0
        f_c = int(pyt_failed.group(1)) if pyt_failed else 0
        assertion_count = max(assertion_count, p_c + f_c)

    if assertion_count == 0 and exit_code == 0:
        assertion_count = 1

    for line in combined.splitlines():
        fail_m = re.match(r"^(?:FAIL|ERROR):\s+([^\s]+)", line)
        if fail_m:
            failing.append(fail_m.group(1))
        pyt_fail = re.search(r"FAILED\s+([^\s]+)", line)
        if pyt_fail:
            failing.append(pyt_fail.group(1))

    return assertion_count, tuple(dict.fromkeys(failing))


def run_external_oracle(
    oracle_script_path: Path,
    target_workspace_path: Path,
    timeout_seconds: int = 30,
) -> OracleResult:
    """Execute external oracle test against the target workspace."""
    if not oracle_script_path.is_file():
        return OracleResult(
            passed=False,
            exit_code=1,
            stdout="",
            stderr=f"Oracle script missing at {oracle_script_path}",
            duration_seconds=0.0,
            error=f"Oracle script missing: {oracle_script_path}",
        )

    env = {
        **os.environ,
        "PYTHONPATH": f"{str(target_workspace_path.resolve())}:{str((target_workspace_path / 'src').resolve())}",
        "PYTHONDONTWRITEBYTECODE": "1",
        "BAAC_TARGET_WORKSPACE": str(target_workspace_path.resolve()),
    }

    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, str(oracle_script_path.resolve()), "--workspace", str(target_workspace_path.resolve())],
            cwd=target_workspace_path,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        duration = round(time.perf_counter() - t0, 3)

        a_count, failing = parse_oracle_output(proc.stdout, proc.stderr, proc.returncode)
        passed = (proc.returncode == 0)

        return OracleResult(
            passed=passed,
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_seconds=duration,
            error=None if passed else (proc.stderr.strip()[:200] or proc.stdout.strip()[:200]),
            assertion_count=a_count,
            failing_assertions=failing,
        )

    except subprocess.TimeoutExpired:
        duration = round(time.perf_counter() - t0, 3)
        return OracleResult(
            passed=False,
            exit_code=124,
            stdout="",
            stderr=f"Oracle timed out after {timeout_seconds} seconds",
            duration_seconds=duration,
            error=f"TimeoutExpired ({timeout_seconds}s)",
        )
    except Exception as exc:
        duration = round(time.perf_counter() - t0, 3)
        return OracleResult(
            passed=False,
            exit_code=1,
            stdout="",
            stderr=str(exc),
            duration_seconds=duration,
            error=str(exc),
        )
