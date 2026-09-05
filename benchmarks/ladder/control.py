"""T-26 frozen-control preregistration. UNFROZEN until the first paid L2 call."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

__all__ = ["CONTROL_ARM", "load_preregistration", "require_frozen"]

ROOT = Path(__file__).resolve().parent
CONTROL_PATH = ROOT / "control_preregistration.json"

CONTROL_ARM = {
    "harness": "vg-code-balanced",
    "preset": "balanced",
    "workers": 1,
    "product_path": "vanguard.packages.runtime.entrypoint.execute",
}


class ControlNotFrozen(ValueError):
    """L2 scoring attempted before T-26 froze the subject SHA."""


def load_preregistration(path: Path | None = None) -> dict[str, Any]:
    target = path or CONTROL_PATH
    data = json.loads(target.read_text(encoding="utf-8"))
    if data.get("schema") != "aether.control-preregistration/1":
        raise ValueError("invalid control preregistration schema")
    return data


def require_frozen(record: Mapping[str, Any] | None = None) -> dict[str, Any]:
    data = dict(record or load_preregistration())
    if data.get("status") != "FROZEN" or not data.get("subject_sha"):
        raise ControlNotFrozen(
            "T-26: freeze subject_sha, suite_digest, and model_id before the first paid L2 call")
    arm = data.get("arm") or {}
    if arm.get("harness") != CONTROL_ARM["harness"] or arm.get("workers") != 1:
        raise ControlNotFrozen(
            "MS-CONTROL qualifies only single-worker vg-code-balanced on the product path")
    return data
