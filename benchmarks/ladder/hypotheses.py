"""T-95 hypothesis registry. One varied dimension per treatment."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "hypotheses.json"

__all__ = ["HypothesisError", "load_registry", "require_hypothesis", "assert_single_dimension"]


class HypothesisError(ValueError):
    """An unregistered or multi-dimension comparison."""


def load_registry(path: Path | None = None) -> dict[str, Any]:
    target = path or REGISTRY_PATH
    data = json.loads(target.read_text(encoding="utf-8"))
    if data.get("schema") != "aether.hypothesis-registry/1":
        raise HypothesisError("invalid hypothesis registry schema")
    return data


def require_hypothesis(hypothesis_id: str, registry: Mapping[str, Any] | None = None) -> dict[str, Any]:
    data = registry or load_registry()
    rows = data.get("hypotheses") or {}
    if hypothesis_id == "control":
        return {"id": "control", "varied_dimension": None}
    if hypothesis_id not in rows:
        raise HypothesisError(f"unregistered treatment {hypothesis_id!r}")
    row = dict(rows[hypothesis_id])
    if not row.get("control_digest") or not row.get("varied_dimension"):
        raise HypothesisError(f"{hypothesis_id} must bind a control digest and one varied dimension")
    return row


def assert_single_dimension(
    control: Mapping[str, Any],
    treatment: Mapping[str, Any],
    *,
    varied_dimension: str,
) -> None:
    """Refuse paired comparisons that vary more than the preregistered dimension."""
    keys = sorted(set(control) | set(treatment))
    changed = [key for key in keys if control.get(key) != treatment.get(key)]
    if changed != [varied_dimension]:
        raise HypothesisError(
            f"comparison varies {changed}; preregistered dimension is {varied_dimension!r}")
