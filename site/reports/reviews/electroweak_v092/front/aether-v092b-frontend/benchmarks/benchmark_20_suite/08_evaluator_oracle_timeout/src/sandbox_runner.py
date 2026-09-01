import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ExecutionResult:
    status: str  # "OK" | "TIMEOUT" | "ERROR"
    return_code: int
    stdout: str
    stderr: str

class SandboxRunner:
    @staticmethod
    def run_command(cmd: List[str], timeout_seconds: float = 2.0) -> ExecutionResult:
        try:
            # BUG: Does not set start_new_session=True and swallows TimeoutExpired without
            # reporting status='TIMEOUT'
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            return ExecutionResult(status="OK" if proc.returncode == 0 else "ERROR", return_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
        except subprocess.TimeoutExpired as exc:
            # BUG: Returns status="ERROR" with return_code=0 instead of status="TIMEOUT" and return_code=-1
            return ExecutionResult(status="ERROR", return_code=0, stdout="", stderr="timed out")
