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


@dataclass(frozen=True, slots=True)
class VerificationReceipt:
    """Minimal local-verification identity bound to the current workspace."""

    exit_code: int
    executed_test_count: int
    workspace_digest: str
    task_digest: str = ""
    receipt_digest: str = ""
    composition_digest: str = ""
    verification_command: str = ""
    verification_subject_digest: str = ""

    @property
    def passed(self) -> bool:
        return self.exit_code == 0 and self.executed_test_count > 0


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
        verification: VerificationReceipt | Mapping[str, Any] | None = None,
        current_workspace_digest: str | None = None,
        current_task_digest: str | None = None,
        current_composition_digest: str | None = None,
        current_verification_command: str | None = None,
        current_verification_subject_digest: str | None = None,
        current_receipt_digest: str | None = None,
        task_requirements_satisfied: bool | None = None,
        model_requested_finish: bool = True,
        inspected_files: Sequence[str] = (),
        **_: Any,
    ) -> AdmissionVerdict:
        is_write_preset = any(prefix in preset_name for prefix in ("code", "bugfix", "write"))
        is_read_only = any(prefix in preset_name for prefix in ("tutor", "research", "read"))

        if not model_requested_finish:
            return AdmissionVerdict(False, "MODEL_DID_NOT_REQUEST_FINISH")

        # Read-only policy is explicit: no source patch is required, but task
        # requirements still must be satisfied. This keeps Tutor/Research
        # separate from coding/bugfix completion semantics.
        if is_read_only or not self.require_patch_for_write_presets:
            if task_requirements_satisfied is False:
                return AdmissionVerdict(False, "TASK_REQUIREMENTS_UNSATISFIED")
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

        # Every changed file is itself part of the evidence surface. This is
        # the runtime fallback for packs that do not bind a richer repository
        # completion policy, and prevents a write receipt from standing in for
        # an inspection receipt.
        if any(path not in set(inspected_files) for path in changed_files):
            return AdmissionVerdict(False, "MODIFIED_FILE_NOT_INSPECTED")

        if task_requirements_satisfied is False:
            return AdmissionVerdict(False, "TASK_REQUIREMENTS_UNSATISFIED")

        receipt = verification
        if isinstance(receipt, Mapping):
            receipt = VerificationReceipt(
                exit_code=int(receipt.get("exit_code", receipt.get("exitCode", -1))),
                executed_test_count=int(receipt.get("executed_test_count", receipt.get("executedTestCount", 0))),
                workspace_digest=str(receipt.get("workspace_digest", receipt.get("workspaceDigest", ""))),
                task_digest=str(receipt.get("task_digest", receipt.get("taskDigest", ""))),
                composition_digest=str(receipt.get("composition_digest", receipt.get("compositionDigest", ""))),
                receipt_digest=str(receipt.get("receipt_digest", receipt.get("receiptDigest", ""))),
                verification_command=str(receipt.get("verification_command", receipt.get("verificationCommand", receipt.get("command", "")))),
                verification_subject_digest=str(receipt.get("verification_subject_digest", receipt.get("verificationSubjectDigest", ""))),
            )
        elif receipt is None and verification_passed is not None:
            # Legacy callers may provide only a boolean; it is deliberately
            # insufficient for strict admission because subject freshness is
            # not observable.
            if verification_passed is False:
                return AdmissionVerdict(False, "VERIFICATION_FAILED")
            receipt = None
        if receipt is None:
            return AdmissionVerdict(False, "VERIFICATION_REQUIRED")
        if not receipt.passed:
            return AdmissionVerdict(False, "VERIFICATION_FAILED")
        if current_workspace_digest is None or receipt.workspace_digest != current_workspace_digest:
            return AdmissionVerdict(False, "VERIFICATION_STALE")
        if current_task_digest is not None:
            if not receipt.task_digest:
                return AdmissionVerdict(False, "VERIFICATION_UNBOUND_TASK")
            if receipt.task_digest != current_task_digest:
                return AdmissionVerdict(False, "VERIFICATION_FOREIGN_TASK")
        if current_composition_digest is not None:
            if not receipt.composition_digest:
                return AdmissionVerdict(False, "VERIFICATION_UNBOUND_COMPOSITION")
            if receipt.composition_digest != current_composition_digest:
                return AdmissionVerdict(False, "VERIFICATION_FOREIGN_COMPOSITION")
        if current_verification_command is not None:
            if not receipt.verification_command:
                return AdmissionVerdict(False, "VERIFICATION_UNBOUND_SUBJECT")
            if receipt.verification_command != current_verification_command:
                return AdmissionVerdict(False, "VERIFICATION_FOREIGN_SUBJECT")
        if current_verification_subject_digest is not None:
            if not receipt.verification_subject_digest:
                return AdmissionVerdict(False, "VERIFICATION_UNBOUND_SUBJECT")
            if receipt.verification_subject_digest != current_verification_subject_digest:
                return AdmissionVerdict(False, "VERIFICATION_FOREIGN_SUBJECT")
        if current_receipt_digest is not None:
            if not receipt.receipt_digest:
                return AdmissionVerdict(False, "VERIFICATION_UNBOUND_RECEIPT")
            if receipt.receipt_digest != current_receipt_digest:
                return AdmissionVerdict(False, "VERIFICATION_FOREIGN_RECEIPT")

        return AdmissionVerdict(admissible=True, reason="completion_admissible")
