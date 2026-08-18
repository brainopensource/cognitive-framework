#!/usr/bin/env python3
"""Archive a v0.4.5 coding run into the sprint34 evidence layout (S34-A-04).

Does not invent ledger contents. Copies or writes only what the caller supplies.
Never archives .env, provider keys, authorization headers, or sealed oracle source.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any, Mapping


REQUIRED = (
    "command.txt",
    "task-manifest.json",
    "coding-plan.json",
    "plan-revisions.json",
    "model-routes.json",
    "ledger.jsonl",
    "coding-session.json",
    "workspace.diff",
    "verification.json",
    "budget.json",
    "summary.md",
)


def archive_run(dest: Path, artifacts: Mapping[str, Any | Path | str]) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED:
        if name not in artifacts:
            raise ValueError(f"missing required evidence artifact: {name}")
    for name, value in artifacts.items():
        target = dest / name
        if isinstance(value, Path):
            if value.is_file():
                shutil.copy2(value, target)
            else:
                raise FileNotFoundError(value)
        elif isinstance(value, str) and name.endswith((".txt", ".md", ".diff", ".jsonl")):
            target.write_text(value if value.endswith("\n") else value + "\n", encoding="utf-8")
        else:
            target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dest


def main() -> int:
    parser = argparse.ArgumentParser(description="Project/archive one coding run")
    parser.add_argument("--dest", required=True, help="docs/scrum/sprints/sprint34/evidence/<run-id>")
    parser.add_argument("--manifest", required=True, help="JSON map of artifact name -> path or inline")
    args = parser.parse_args()
    mapping = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    resolved: dict[str, Any] = {}
    for key, value in mapping.items():
        if isinstance(value, str) and Path(value).exists():
            resolved[key] = Path(value)
        else:
            resolved[key] = value
    archive_run(Path(args.dest), resolved)
    print(args.dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
