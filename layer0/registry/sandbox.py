"""POSIX rlimits and isolated log sinks for plugin child processes (SPEC §3)."""

from __future__ import annotations

import os
import resource
from dataclasses import dataclass
from pathlib import Path

__all__ = ["SandboxLimits", "apply_rlimits", "open_log_sink"]


@dataclass(frozen=True, slots=True)
class SandboxLimits:
    cpu_seconds: int = 2
    address_space_bytes: int = 256 * 1024 * 1024
    max_open_files: int = 64
    max_processes: int = 64


def apply_rlimits(limits: SandboxLimits) -> None:
    """Apply ceilings in the *child*. Fail closed on OSError."""
    _set(resource.RLIMIT_CPU, limits.cpu_seconds)
    _set(resource.RLIMIT_AS, limits.address_space_bytes)
    _set(resource.RLIMIT_NOFILE, limits.max_open_files)
    _set(resource.RLIMIT_NPROC, limits.max_processes)


def open_log_sink(path: str | Path):
    """Parent-side sink: child stdout/stderr never join Layer-0 streams."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return open(path, "ab", buffering=0)


def _set(which: int, value: int) -> None:
    resource.setrlimit(which, (value, value))


def preexec(limits: SandboxLimits):
    """subprocess.Popen preexec_fn. Also drops controlling terminal."""

    def _inner() -> None:
        apply_rlimits(limits)
        try:
            os.setsid()
        except OSError:
            pass

    return _inner
