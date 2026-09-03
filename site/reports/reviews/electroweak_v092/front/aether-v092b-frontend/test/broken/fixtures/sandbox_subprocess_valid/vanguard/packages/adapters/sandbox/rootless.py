"""The one place the host shell is reachable: the sandbox adapter itself."""

from __future__ import annotations

import subprocess


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, check=False).returncode
