#!/usr/bin/env python3
"""Block A deterministic repository inventory generator.

Reads the working tree at the current HEAD and emits
.generated/knowledge/repository-inventory.jsonl with one record per relevant
repository entity, sorted deterministically by path. Read-only; does not
modify production code or active docs. Confined to .generated/knowledge/ for
output per docs/_archive/reviews/backend/director_review_v6/DOC_migration_process.md.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

EXCLUDE_DIR_PARTS = {
    ".git", "__pycache__", "node_modules", ".venv", ".vanguard",
    "vanguard_runtime.egg-info", "lab", "output",
}

LANG_BY_SUFFIX = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".json": "json",
    ".md": "markdown",
    ".sh": "shell",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
}


def git_files() -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        check=True, capture_output=True, text=True,
    ).stdout
    return sorted(out.splitlines())


def classify(path: str) -> dict:
    p = Path(path)
    suffix = p.suffix
    language = LANG_BY_SUFFIX.get(suffix, "other")
    parts = p.parts

    role = "other"
    package = None
    entry_point = False
    method = "path-heuristic"

    if parts[:2] == ("vanguard", "packages") and len(parts) > 2:
        role = "production-code"
        package = f"vanguard.packages.{parts[2]}"
    elif parts[:2] == ("vanguard", "clients"):
        role = "production-code-client"
        package = f"vanguard.clients.{parts[2]}" if len(parts) > 2 else "vanguard.clients"
    elif parts[0] == "packs":
        role = "domain-pack"
        package = f"packs.{parts[1]}" if len(parts) > 1 else "packs"
    elif parts[0] == "test":
        role = "test"
        package = f"test.{parts[1]}" if len(parts) > 1 else "test"
    elif parts[0] == "schemas":
        role = "schema"
    elif parts[0] == "docs":
        role = "documentation"
    elif parts[0] == "tools":
        role = "tooling"
        if len(parts) > 1 and parts[1] == "linters":
            role = "linter"
        elif len(parts) > 1 and parts[1] == "runners":
            role = "runner"
    elif parts[0] == ".github":
        role = "ci"
    elif parts[0] == "ci":
        role = "release-tooling"
    elif parts[0] == "containers":
        role = "container-image"
    elif parts[0] == "benchmarks":
        role = "benchmark"
    elif parts[0] in ("evidence",):
        role = "evidence-artifact"
    elif suffix == ".md" and len(parts) == 1:
        role = "root-documentation"

    if path in ("pyproject.toml", "package.json", "requirements.lock", "uv.lock", "pnpm-lock.yaml"):
        role = "manifest"

    if suffix == ".py" and (p.name == "cli.py" or p.name == "server.py" or p.name == "daemon.py" or p.name == "main.py"):
        entry_point = True

    return {
        "path": path,
        "entity_type": "file",
        "language": language,
        "package": package,
        "role": role,
        "entry_point": entry_point,
        "extraction_method": method,
    }


def is_excluded(path: str) -> bool:
    parts = Path(path).parts
    return any(part in EXCLUDE_DIR_PARTS for part in parts)


def main() -> int:
    out_path = ROOT / ".generated" / "knowledge" / "repository-inventory.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    files = [f for f in git_files() if not is_excluded(f)]
    records = [classify(f) for f in files]
    records.sort(key=lambda r: r["path"])
    with out_path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    print(f"wrote {len(records)} records to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
