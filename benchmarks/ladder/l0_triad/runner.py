"""L0 smoke triad (T-92). Public product path; Wave 1 smoke only."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from benchmarks.product_path import execute_product
from vanguard.packages.domain.canonicalisation.digest import digest_of

ROOT = Path(__file__).resolve().parent
TASKS = ("P0-FIB", "P0-CSV", "P0-BUG")


def _digest_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def task_dir(task_id: str) -> Path:
    return ROOT / task_id.lower().replace("-", "_")


def materialize(task_id: str, workspace: Path) -> dict[str, str]:
    source = task_dir(task_id)
    workspace.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        if path.is_file() and path.name != "TASK.md":
            target = workspace / path.name
            target.write_bytes(path.read_bytes())
    brief = (source / "TASK.md").read_text(encoding="utf-8")
    (workspace / "TASK.md").write_text(brief, encoding="utf-8")
    oracle = source / "test_oracle.py"
    return {
        "task_id": task_id,
        "brief": brief.strip(),
        "fixture_digest": digest_of({
            "files": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(source.iterdir()) if p.is_file()
            }
        }),
        "oracle_digest": _digest_file(oracle) if oracle.is_file() else "",
        "oracle_path": str(oracle),
    }


def run_task(
    task_id: str,
    workspace: Path,
    *,
    fake_backend: str | None = "greenfield-adaptive",
    preset: str = "balanced",
) -> dict[str, Any]:
    meta = materialize(task_id, workspace)
    frame = execute_product(
        workspace=workspace,
        brief=meta["brief"],
        preset=preset,
        fake_backend=fake_backend,
        profile_id="local",
        interactive=False,
    )
    receipt = frame.get("result") or {}
    return {
        **meta,
        "run_id": receipt.get("runId"),
        "terminal_status": receipt.get("outcome"),
        "detail": receipt.get("detail"),
        "turns": receipt.get("turns"),
        "projections": receipt.get("projections") or [],
        "patch_digest": next(
            (item.get("text") for item in receipt.get("projections") or ()
             if isinstance(item, dict) and item.get("kind") == "write"),
            None,
        ),
    }


def refuse_patchless_completion(row: dict[str, Any]) -> dict[str, Any]:
    if row.get("terminal_status") == "completed" and not row.get("patch_digest"):
        raise ValueError("completed outcome refused: missing patch digest")
    return row
