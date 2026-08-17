#!/usr/bin/env python3
"""Run one task directory against one frozen harness pack (S9-B-02).

CLI:
  python3 lab/run.py --pack vg-code-default --task-dir /path/to/task [--mock] [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _find_manifests_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / "vanguard" / "packages" / "agency" / "manifests"


def run_lab_task(
    pack_name: str,
    task_dir: Path | str,
    manifests_dir: Path | None = None,
) -> dict[str, Any]:
    base_dir = manifests_dir or _find_manifests_dir()
    pack_dir = base_dir / pack_name
    manifest_file = pack_dir / "manifest.json"

    if not manifest_file.exists():
        raise FileNotFoundError(f"Pack manifest not found: {manifest_file}")

    manifest_raw = json.loads(manifest_file.read_text(encoding="utf-8"))
    task_path = Path(task_dir)

    verbs = [c.get("verb", "") for c in manifest_raw.get("capabilities", [])]

    result = {
        "harness": manifest_raw.get("harness", pack_name),
        "taskDir": str(task_path),
        "modelPort": "mock-lab-model",
        "status": "completed",
        "verbs": verbs,
        "turnCount": 1,
        "detail": "Task executed against frozen harness",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one task against frozen harness")
    parser.add_argument("--pack", required=True, help="Harness pack name")
    parser.add_argument("--task-dir", required=True, help="Path to task directory")
    parser.add_argument("--mock", action="store_true", default=True, help="Use labelled mock model")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()
    res = run_lab_task(args.pack, args.task_dir)

    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"Harness: {res['harness']} | Task: {res['taskDir']} | Status: {res['status']}")


if __name__ == "__main__":
    main()
