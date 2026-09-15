"""Bridge to .agents/skills/test-runner/ for isolated, timeout-bounded execution."""
from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def run_test_isolated(
    command: str,
    timeout: float = 15.0,
    cwd: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute a test command in an isolated subprocess via test-runner skill.
    
    Falls back gracefully to in-process isolated runner logic if the external
    script is unavailable.
    """
    repo_root = cwd or Path.cwd()
    runner_script = repo_root / ".agents" / "skills" / "test-runner" / "scripts" / "run_test.py"
    
    if runner_script.exists():
        try:
            cmd = ["python3", str(runner_script), command, "--timeout", str(timeout), "--cwd", str(repo_root), "--json"]
            proc = subprocess.run(
                cmd,
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                timeout=timeout + 5.0,
            )
            if proc.stdout.strip():
                try:
                    return json.loads(proc.stdout)
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.warning(f"Error invoking run_test.py: {e}")

    # Fallback to direct subprocess execution with timeout
    start_time = time.time()
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = time.time() - start_time
        return {
            "command": command,
            "success": proc.returncode == 0,
            "exit_code": proc.returncode,
            "duration_seconds": round(duration, 3),
            "timed_out": False,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "failures": [],
            "summary": "OK" if proc.returncode == 0 else f"FAILED (exit {proc.returncode})",
        }
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        return {
            "command": command,
            "success": False,
            "exit_code": 124,
            "duration_seconds": round(duration, 3),
            "timed_out": True,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "failures": [],
            "summary": f"TIMED_OUT ({timeout}s)",
        }
