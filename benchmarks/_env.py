"""Lazy provider-credential loading for the benchmark drivers.

Benchmarks used to parse ``.env`` and write ``os.environ`` at *import* time.
That made merely importing a driver -- which the unit tests do, to reach the
pure helpers next to it -- bind a live provider key onto the interpreter for
every test that ran afterwards.  A hermetic assertion such as "no provider key
is set" then passed or failed depending on collection order.

Loading is a side effect of *running* a benchmark, not of importing one, so it
lives behind a call the ``__main__`` guards make explicitly.
"""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["load_benchmark_env"]

ROOT = Path(__file__).resolve().parents[1]

# The only keys a benchmark driver is allowed to lift out of ``.env``.
_ALLOWED_KEYS = frozenset(
    {"OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "VANGUARD_ALLOW_PAID"}
)


def load_benchmark_env(root: Path | None = None) -> frozenset[str]:
    """Bind allowed ``.env`` keys onto ``os.environ``; return the names set.

    Never overwrites a value already present in the environment, so an
    explicit export still wins over the file.  Returns names only -- a secret
    must not travel back through a return value or a log line.
    """
    env_file = (root or ROOT) / ".env"
    if not env_file.is_file():
        return frozenset()

    applied: set[str] = set()
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in _ALLOWED_KEYS or os.environ.get(key):
            continue
        os.environ[key] = value.strip().strip("'\"")
        applied.add(key)
    return frozenset(applied)
