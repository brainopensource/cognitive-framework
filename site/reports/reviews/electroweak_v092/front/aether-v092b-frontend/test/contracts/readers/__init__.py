"""Access to the second reader.

`SC-7`: two independent implementations — TypeScript and Python — must agree
on every vector before a schema is considered locked. The Python suite drives
the TypeScript reader through `ts_reader.mjs` rather than reimplementing its
assertions, so a disagreement surfaces as a failing vector and not as two
suites that were never compared.

If Node is missing or too old to run the reader, the suite **fails**. It does
not skip: an unavailable reader means the two-reader evidence `REQ-SCHEMA-001`
asks for was not produced, and a green run would say otherwise.
"""

from __future__ import annotations

import json
import subprocess
from functools import lru_cache
from pathlib import Path
from typing import Any

READER = Path(__file__).resolve().parent / "ts_reader.mjs"

#: Node strips TypeScript types without a build step from 22.18 / 23.6 on. The
#: readers are checked in as `.ts` because VG-04 `CT-02` derives types from
#: schemas; adding a compiler to the loop would add a second artifact that can
#: drift from the source.
MINIMUM_NODE = (22, 18)


class ReaderUnavailable(RuntimeError):
    """The second reader could not run. Never treated as a pass."""


@lru_cache(maxsize=1)
def _node_version() -> tuple[int, ...]:
    try:
        out = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReaderUnavailable(
            "node is required: SC-7 evidence needs both readers, and a run without "
            "the TypeScript reader proves nothing about cross-language agreement"
        ) from exc
    return tuple(int(part) for part in out.stdout.strip().lstrip("v").split(".")[:3])


def ts_reader(request: dict[str, Any]) -> dict[str, Any]:
    """Ask the TypeScript reader one batch of questions."""
    version = _node_version()
    if version < MINIMUM_NODE:
        raise ReaderUnavailable(
            f"node {'.'.join(map(str, version))} cannot run the reader; "
            f"{'.'.join(map(str, MINIMUM_NODE))}+ is required for type stripping"
        )
    result = subprocess.run(
        ["node", str(READER)],
        input=json.dumps(request),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ReaderUnavailable(f"TypeScript reader failed:\n{result.stderr}")
    return json.loads(result.stdout)
