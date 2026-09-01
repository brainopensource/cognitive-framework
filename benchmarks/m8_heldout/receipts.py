"""Data-only independent M-8 promotion and rollback receipt values."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

_PREREG = Path(__file__).resolve().parent / "artifacts" / "preregistration.json"


def _threshold() -> float:
    return float(json.loads(_PREREG.read_text(encoding="utf-8"))["min_held_out_lift"])


@dataclass(frozen=True, slots=True)
class PromotionReceipt:
    run_id: str
    subject_sha: str
    lift: float
    control_success: float
    treatment_success: float
    cost_per_solved_task: float | None = None
    signer_id: str = "independent-evaluator"
    minimum_lift: float = field(init=False)

    def __post_init__(self) -> None:
        minimum = _threshold()
        object.__setattr__(self, "minimum_lift", minimum)
        if self.lift < minimum:
            raise ValueError(f"lift {self.lift} is below preregistered threshold {minimum}")

    def to_dict(self) -> dict[str, object]:
        return {"result": "PROMOTED", "run_id": self.run_id, "subject_sha": self.subject_sha, "lift": self.lift,
                "control_success": self.control_success, "treatment_success": self.treatment_success,
                "cost_per_solved_task": self.cost_per_solved_task, "minimum_lift": self.minimum_lift, "signer_id": self.signer_id}


@dataclass(frozen=True, slots=True)
class RollbackReceipt:
    run_id: str
    subject_sha: str
    reason: str
    signer_id: str = "independent-evaluator"
    result: str = field(default="NEGATIVE", init=False)

    def to_dict(self) -> dict[str, object]:
        return {"result": self.result, "run_id": self.run_id, "subject_sha": self.subject_sha,
                "reason": self.reason, "signer_id": self.signer_id}
