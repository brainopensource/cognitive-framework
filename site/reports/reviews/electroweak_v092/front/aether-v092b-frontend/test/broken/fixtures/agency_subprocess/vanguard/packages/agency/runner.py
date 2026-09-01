"""Cognition reaching the host shell directly, bypassing the sandbox adapter.

"""

from __future__ import annotations

import subprocess


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, check=False).returncode
