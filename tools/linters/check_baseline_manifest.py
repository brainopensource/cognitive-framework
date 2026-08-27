#!/usr/bin/env python3
"""Fail closed until the accepted successor baseline manifest is available and verified (ADR-0102).

WP-B1 provides the full ``aether.baseline/1`` verifier.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from repo_paths import repo_root
from vanguard.packages.domain.evidence.baseline import (
    BASELINE_DISPOSITION_ACCEPTED_CONTROL,
    BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED,
    classify_ref_disposition,
    verify_baseline_manifest,
)

def _local_git(args: Sequence[str], cwd: Path) -> tuple[int, str]:
    import subprocess

    proc = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return proc.returncode, proc.stdout


def _local_git_output(args: Sequence[str], cwd: Path) -> str:
    code, output = _local_git(args, cwd)
    return output if code == 0 else ""


DEFAULT_MANIFEST = repo_root() / "evidence" / "baselines" / "CONVERGENCE-BASE-v1.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an aether.baseline/1 manifest.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to baseline manifest JSON file.",
    )
    parser.add_argument(
        "--skip-remote",
        action="store_true",
        help="Skip remote git ls-remote verification (for local/offline testing).",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Configured remote name to check (default: origin).",
    )
    args = parser.parse_args()
    root = repo_root()
    manifest_path = args.manifest

    if not manifest_path.is_file():
        print(
            f"BASELINE FAIL: accepted successor manifest is absent: {manifest_path}",
            file=sys.stderr,
        )
        print(
            "BASELINE FAIL: CONVERGENCE-BASE-v1 must be created, pushed, and verified with aether.baseline/1",
            file=sys.stderr,
        )
        return 1

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(
            f"BASELINE FAIL: malformed JSON in manifest {manifest_path}: {exc}",
            file=sys.stderr,
        )
        return 1

    git_tag = data.get("git_tag")
    if isinstance(git_tag, str) and classify_ref_disposition(
        root,
        git_tag,
        git_runner=lambda command: _local_git_output(command, root),
    ) == BASELINE_DISPOSITION_CONTAMINATED_UNPUBLISHED:
        print("BASELINE FAIL: manifest names the contaminated historical ref", file=sys.stderr)
        return 1

    result = verify_baseline_manifest(
        data,
        root,
        skip_remote=args.skip_remote,
        remote_name=args.remote,
        git_runner=_local_git,
    )

    if not result.valid:
        print(
            f"BASELINE FAIL: manifest verification failed (disposition: {result.disposition})",
            file=sys.stderr,
        )
        for reason in result.rejection_reasons:
            print(f"  - {reason}", file=sys.stderr)
        return 1

    print(
        f"BASELINE PASS: manifest verified ({result.disposition}): {result.details.get('baseline_id')}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
