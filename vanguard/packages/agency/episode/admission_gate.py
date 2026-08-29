"""Closed-Loop Admission Gate for Episode Completion.

Prevents models from terminating coding episodes with conversational summaries unless required
source patches and verification assertions have been generated and satisfied.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class AdmissionVerdict:
    """Verdict returned by the Admission Gate."""

    admissible: bool
    reason: str
    rejection_feedback: str | None = None


class AdmissionGate:
    """Validates whether an episode termination proposal meets work completion criteria."""

    def __init__(self, require_patch_for_write_presets: bool = True) -> None:
        self.require_patch_for_write_presets = require_patch_for_write_presets

    def evaluate(
        self,
        preset_name: str,
        changed_files: Sequence[str],
        proposal: Mapping[str, Any],
        *,
        verification_passed: bool | None = None,
    ) -> AdmissionVerdict:
        is_write_preset = any(prefix in preset_name for prefix in ("code", "bugfix", "write"))
        is_read_only = any(prefix in preset_name for prefix in ("tutor", "research", "read"))

        # Read-only presets (Tutor/Research) exit cleanly on conversational completion
        if is_read_only or not self.require_patch_for_write_presets:
            return AdmissionVerdict(admissible=True, reason="read_only_preset_admissible")

        # Write-capable presets MUST produce at least one changed file
        if is_write_preset and not changed_files:
            return AdmissionVerdict(
                admissible=False,
                reason="MISSING_SOURCE_PATCH",
                rejection_feedback=(
                    "ADMISSION GATE REJECTION: Episode completion was rejected because no source code "
                    "changes were detected. You MUST use `patch.apply` or `fs.write` to modify the source "
                    "files before issuing completion."
                ),
            )

        # Verification check if suite execution occurred
        if verification_passed is False:
            return AdmissionVerdict(
                admissible=False,
                reason="VERIFICATION_FAILED",
                rejection_feedback=(
                    "ADMISSION GATE REJECTION: The test verification suite is failing. "
                    "Inspect the test output and fix the remaining failures before completing."
                ),
            )

        return AdmissionVerdict(admissible=True, reason="completion_admissible")
