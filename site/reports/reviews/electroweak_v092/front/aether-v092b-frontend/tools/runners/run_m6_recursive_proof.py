#!/usr/bin/env python3
"""Run the canonical M-6 recursion falsifiers in a fresh Python process.

The report is an observation of a subprocess, not caller-supplied counters.
It is intentionally small and digestable; the evidence builder binds the
report and the protected source surface to the exact candidate commit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def run_falsifiers(root: Path) -> dict[str, object]:
    command = [
        sys.executable, "-m", "unittest",
        "test.falsifiers.test_rf101_rf112_canonical_recursion", "-v",
    ]
    process = subprocess.run(
        command, cwd=root, capture_output=True, text=True, check=False,
        env={"PATH": __import__("os").environ.get("PATH", ""),
             "PYTHONPATH": str(root)},
    )
    output = process.stdout + process.stderr
    match = re.search(r"Ran (\d+) tests?", output)
    tests = int(match.group(1)) if match else 0
    return {
        "schema": "aether.m6-falsifier-report/1",
        "command": command,
        "cwd": ".",
        "returncode": process.returncode,
        "tests": tests,
        "failures": 0 if process.returncode == 0 else 1,
        "fresh_process": True,
        "depth_3": "RF107DeepTreesColdFold" in output,
        "kill_tree": "RF111KillTreeAppendsAndErasesNothing" in output,
        "stdout_digest": digest(process.stdout.encode()),
        "stderr_digest": digest(process.stderr.encode()),
        "output_digest": digest(output.encode()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = run_falsifiers(args.root.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["returncode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
