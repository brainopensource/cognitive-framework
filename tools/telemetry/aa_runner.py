"""A/A runner and noise floor calibration (S9-C-03).

Owning contract: VG-07 §5.1, §5.3, REQ-BENCH-001.

Measures the intrinsic execution variance (noise floor) by evaluating identical manifests
against each other over repeated runs across multiple task classes.
Refuses to report when the design is degenerate (0% or 100% ceiling/floor),
when the variance is exactly zero, or when run against deterministic replay.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from vanguard.packages.domain.canonicalisation.digest import digest_of


class AARunnerRefusalError(ValueError):
    """Raised when an A/A run is degenerate or invalid for floor calibration."""
    pass


@dataclass
class AAResult:
    """Outcome of an A/A noise floor measurement."""

    refused: bool
    reason: str | None
    n_repeats: int
    task_classes: Sequence[str]
    manifest: str
    temperature: float
    is_replay: bool
    pass_rate_arm1: float = 0.0
    pass_rate_arm2: float = 0.0
    discordant_b: int = 0
    discordant_c: int = 0
    floor_variance: float = 0.0
    instrument_error_rate_arm1: float = 0.0
    instrument_error_rate_arm2: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "refused": self.refused,
            "reason": self.reason,
            "nRepeats": self.n_repeats,
            "taskClasses": list(self.task_classes),
            "manifest": self.manifest,
            "temperature": self.temperature,
            "isReplay": self.is_replay,
            "passRateArm1": self.pass_rate_arm1,
            "passRateArm2": self.pass_rate_arm2,
            "discordantB": self.discordant_b,
            "discordantC": self.discordant_c,
            "floorVariance": round(self.floor_variance, 6),
            "instrumentErrorRateArm1": round(self.instrument_error_rate_arm1, 4),
            "instrumentErrorRateArm2": round(self.instrument_error_rate_arm2, 4),
        }


class AARunner:
    """Executes identical manifest A/A calibration and calculates noise floor."""

    def __init__(
        self,
        manifest: str = "vg-shell-only",
        temperature: float = 0.2,
        is_replay: bool = False,
    ) -> None:
        self.manifest = manifest
        self.temperature = temperature
        self.is_replay = is_replay

    def run_calibration(
        self,
        task_classes: Sequence[str],
        arm1_evaluator: Callable[[str, int], dict[str, Any]],
        arm2_evaluator: Callable[[str, int], dict[str, Any]],
        n_repeats: int = 20,
    ) -> AAResult:
        """Run A/A calibration across task classes and N repeats.
        
        Evaluators return: {"passed": bool, "instrument_error": bool}
        """
        if len(task_classes) < 3:
            return AAResult(
                refused=True,
                reason=f"At least 3 task classes required for A/A calibration; got {len(task_classes)}",
                n_repeats=n_repeats,
                task_classes=task_classes,
                manifest=self.manifest,
                temperature=self.temperature,
                is_replay=self.is_replay,
            )

        if self.is_replay:
            return AAResult(
                refused=True,
                reason="A/A floor cannot be measured from deterministic replay (variance ≈ 0 is an artifact)",
                n_repeats=n_repeats,
                task_classes=task_classes,
                manifest=self.manifest,
                temperature=self.temperature,
                is_replay=self.is_replay,
            )

        arm1_passes = 0
        arm2_passes = 0
        arm1_errors = 0
        arm2_errors = 0
        discordant_b = 0
        discordant_c = 0
        total_evaluations = 0

        paired_deltas: list[float] = []

        for task in task_classes:
            for rep in range(n_repeats):
                total_evaluations += 1
                res1 = arm1_evaluator(task, rep)
                res2 = arm2_evaluator(task, rep)

                p1 = bool(res1.get("passed", False))
                p2 = bool(res2.get("passed", False))
                e1 = bool(res1.get("instrument_error", False))
                e2 = bool(res2.get("instrument_error", False))

                if p1:
                    arm1_passes += 1
                if p2:
                    arm2_passes += 1
                if e1:
                    arm1_errors += 1
                if e2:
                    arm2_errors += 1

                if p1 and not p2:
                    discordant_b += 1
                    paired_deltas.append(1.0)
                elif not p1 and p2:
                    discordant_c += 1
                    paired_deltas.append(-1.0)
                else:
                    paired_deltas.append(0.0)

        rate1 = arm1_passes / total_evaluations if total_evaluations else 0.0
        rate2 = arm2_passes / total_evaluations if total_evaluations else 0.0
        err_rate1 = arm1_errors / total_evaluations if total_evaluations else 0.0
        err_rate2 = arm2_errors / total_evaluations if total_evaluations else 0.0

        # Calculate sample variance of the paired deltas
        mean_delta = sum(paired_deltas) / len(paired_deltas) if paired_deltas else 0.0
        variance = sum((d - mean_delta) ** 2 for d in paired_deltas) / (len(paired_deltas) - 1) if len(paired_deltas) > 1 else 0.0

        # Refusal check 1: Degenerate arms (100% all-pass or 0% all-fail with zero discordance)
        if (rate1 in (0.0, 1.0)) and (rate2 in (0.0, 1.0)) and (discordant_b + discordant_c == 0):
            return AAResult(
                refused=True,
                reason="Degenerate A/A design: all instances either passed or failed with zero discordance",
                n_repeats=n_repeats,
                task_classes=task_classes,
                manifest=self.manifest,
                temperature=self.temperature,
                is_replay=self.is_replay,
                pass_rate_arm1=rate1,
                pass_rate_arm2=rate2,
                floor_variance=0.0,
                instrument_error_rate_arm1=err_rate1,
                instrument_error_rate_arm2=err_rate2,
            )

        # Refusal check 2: Zero floor variance
        if variance == 0.0 and (discordant_b + discordant_c == 0):
            return AAResult(
                refused=True,
                reason="Zero variance observed in A/A floor; runner refuses degenerate measurement",
                n_repeats=n_repeats,
                task_classes=task_classes,
                manifest=self.manifest,
                temperature=self.temperature,
                is_replay=self.is_replay,
                pass_rate_arm1=rate1,
                pass_rate_arm2=rate2,
                floor_variance=0.0,
                instrument_error_rate_arm1=err_rate1,
                instrument_error_rate_arm2=err_rate2,
            )

        return AAResult(
            refused=False,
            reason=None,
            n_repeats=n_repeats,
            task_classes=task_classes,
            manifest=self.manifest,
            temperature=self.temperature,
            is_replay=self.is_replay,
            pass_rate_arm1=round(rate1, 4),
            pass_rate_arm2=round(rate2, 4),
            discordant_b=discordant_b,
            discordant_c=discordant_c,
            floor_variance=variance,
            instrument_error_rate_arm1=err_rate1,
            instrument_error_rate_arm2=err_rate2,
        )
