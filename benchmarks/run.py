#!/usr/bin/env python3
"""Thin CLI shim. The driver itself lives in the runtime (`W14-A`).

`lab/` must import nothing -- `check_boundaries.py` enforces it, because `lab/`
is disposable and nothing disposable may become load-bearing. That rule is also
why this file used to fabricate: unable to reach the runtime, it returned a
literal `{"status": "completed", "turnCount": 1}` for every task regardless of
what happened. A driver that cannot call the thing it drives can only lie
about it.

So the real driver is `vanguard.packages.runtime.lab_driver`, and this is a
stdlib-only launcher that hands its arguments over unchanged. It computes
nothing, reports nothing of its own, and cannot claim an outcome.

  python3 lab/run.py --pack vg-code-default --task-dir DIR [--model mock|...]
"""

from __future__ import annotations

import subprocess
import sys

MODULE = "vanguard.packages.runtime.lab_driver"


def main(argv: list[str] | None = None) -> int:
    """Delegate to the runtime driver and pass its exit status through."""
    args = list(sys.argv[1:] if argv is None else argv)
    completed = subprocess.run([sys.executable, "-m", MODULE, *args], check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
