"""Child resource ceilings and private log sinks."""
from __future__ import annotations
import os, resource
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True, slots=True)
class SandboxLimits:
    cpu_seconds: int = 2
    address_space_bytes: int = 512 * 1024 * 1024
    max_open_files: int = 64
    max_processes: int = 64
def apply_rlimits(limits: SandboxLimits) -> None:
    for kind, value in ((resource.RLIMIT_CPU, limits.cpu_seconds),(resource.RLIMIT_AS, limits.address_space_bytes),(resource.RLIMIT_NOFILE, limits.max_open_files),(resource.RLIMIT_NPROC, limits.max_processes)):
        resource.setrlimit(kind, (value, value))
def open_log_sink(path: str | Path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return open(path, "ab", buffering=0)
def preexec(limits: SandboxLimits):
    def child() -> None:
        apply_rlimits(limits)
        try: os.setsid()
        except OSError: pass
    return child
