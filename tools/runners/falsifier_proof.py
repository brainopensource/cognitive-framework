#!/usr/bin/env python3
"""Observe a falsifier suite running in a fresh process, and report what happened.

Owning contract: ADR-0101.

Evidence about a suite must be an *observation* of that suite, not a summary
supplied by whoever wants the milestone to close. So the suite runs as a
subprocess, and every field here is derived from its exit status and output.
There is deliberately no parameter that sets the outcome, and no parameter that
asserts a marker was seen: markers are searched for in the captured output.

A marker that is absent is reported absent. The builder that consumes this
report decides `passed` only when the markers its milestone actually requires
are present, so a suite that silently stops covering a required behaviour
degrades the claim instead of closing it.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def run_suite(
    root: Path,
    modules: Sequence[str],
    *,
    schema: str,
    markers: Mapping[str, str],
) -> dict[str, object]:
    """Run `modules` in a fresh interpreter and observe the result.

    `markers` maps a report field to the test-class or method name whose
    presence in the verbose output demonstrates that behaviour was exercised.
    """
    command = [sys.executable, "-m", "unittest", *modules, "-v"]
    process = subprocess.run(
        command, cwd=root, capture_output=True, text=True, check=False,
        # A bare environment: an evidence run must not inherit provider keys or
        # local configuration that the pinned commit does not describe.
        env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(root)},
    )
    output = process.stdout + process.stderr
    ran = re.search(r"Ran (\d+) tests?", output)
    tests = int(ran.group(1)) if ran else 0
    # `unittest` reports failures and errors separately; both are negatives.
    tallies = re.search(r"failures=(\d+)", output), re.search(r"errors=(\d+)", output)
    failures = sum(int(m.group(1)) for m in tallies if m)
    if process.returncode != 0 and failures == 0:
        # A nonzero exit with no parsed tally (a crash, an import error) is a
        # negative we must not round down to zero.
        failures = 1

    report: dict[str, object] = {
        "schema": schema,
        "command": command,
        "cwd": ".",
        "modules": list(modules),
        "returncode": process.returncode,
        "tests": tests,
        "failures": failures,
        "fresh_process": True,
        "stdout_digest": digest(process.stdout.encode()),
        "stderr_digest": digest(process.stderr.encode()),
        "output_digest": digest(output.encode()),
    }
    report["markers"] = {field: (needle in output) for field, needle in markers.items()}
    return report


def emit(report: Mapping[str, object], out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["returncode"] == 0 else 1
