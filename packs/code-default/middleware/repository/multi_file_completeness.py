"""Cross-file completeness verification for coding admission.

This module is deliberately a value-only policy.  Repository search is bounded
and therefore an estimate is never allowed to masquerade as a closed change
surface.  The extra facts are optional so older callers can keep using the
small three-list API while the live admission path can supply the stronger
evidence.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

_VACUOUS_VERIFICATION_COMMAND = re.compile(
    r"^\s*(?:true|/bin/true|/usr/bin/true|echo\b|printf\b)\b",
    re.IGNORECASE,
)

try:
    from .task_classifier import classify_task
except ImportError:  # Loaded by the pack entrypoint as a standalone module.
    import importlib.util
    import sys
    from pathlib import Path
    _classifier_path = Path(__file__).with_name("task_classifier.py")
    _classifier_spec = importlib.util.spec_from_file_location(
        "code_default_task_classifier", _classifier_path)
    if _classifier_spec is None or _classifier_spec.loader is None:
        raise ImportError(f"cannot load {_classifier_path}")
    _classifier_module = importlib.util.module_from_spec(_classifier_spec)
    sys.modules[_classifier_spec.name] = _classifier_module
    _classifier_spec.loader.exec_module(_classifier_module)
    classify_task = _classifier_module.classify_task


@dataclass(frozen=True, slots=True)
class CompletenessReport:
    is_complete: bool
    missing_inspections: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    rejections: tuple[str, ...] = ()
    unresolved_callers: tuple[str, ...] = ()
    migration_evidence_missing: tuple[str, ...] = ()
    truncated: bool = False


def check_multi_file_completeness(
    implicated_files: Sequence[str],
    inspected_files: Sequence[str],
    modified_files: Sequence[str],
    *,
    changed_public_symbols: Sequence[str] = (),
    callers_by_symbol: Mapping[str, Sequence[str]] | None = None,
    unresolved_callers: Sequence[str] = (),
    migration_required: bool = False,
    migration_evidence: Mapping[str, Any] | None = None,
    compatibility_evidence: Any = None,
    rollback_evidence: Any = None,
    truncated: bool = False,
    truncation_metadata: Mapping[str, Any] | None = None,
    **observations: Any,
) -> CompletenessReport:
    """Verify that the complete, non-truncated change surface is evidenced.

    ``callers_by_symbol`` accepts the output of an indexer.  Every caller of a
    changed public symbol must be part of the implicated set; callers omitted
    from that set are unresolved even when the directly edited file passes its
    own tests.  Migration evidence is intentionally two-dimensional: a
    compatibility story without rollback evidence is not a closed migration.
    """
    changed_public_symbols = tuple(changed_public_symbols) or tuple(
        observations.get("public_interface_changes", ()))
    callers_by_symbol = callers_by_symbol or observations.get("interface_callers")
    migration_required = bool(migration_required or observations.get("migration"))
    truncated = bool(truncated or observations.get("search_truncated") or observations.get("bounded_search"))
    implicated = tuple(sorted(set(str(path) for path in implicated_files)))
    inspected_set = set(str(path) for path in inspected_files)
    modified = tuple(sorted(set(str(path) for path in modified_files)))
    missing = [f for f in implicated if f not in inspected_set]

    warnings: list[str] = []
    rejections: list[str] = []
    for mod in modified:
        if mod not in inspected_set:
            rejections.append(f"MODIFIED_FILE_NOT_INSPECTED:{mod}")

    if missing:
        rejections.append(f"IMPLICATED_FILES_NOT_INSPECTED:{len(missing)}")

    effective_truncated = bool(truncated)
    if truncation_metadata:
        effective_truncated = effective_truncated or any(
            bool(truncation_metadata.get(key))
            for key in ("truncated", "bounded", "omitted", "incomplete")
        )
    if effective_truncated:
        rejections.append("CHANGE_SURFACE_TRUNCATED")

    caller_map = callers_by_symbol or {}
    unresolved = set(str(path) for path in unresolved_callers)
    implicated_set = set(implicated)
    for symbol in changed_public_symbols:
        for caller in caller_map.get(symbol, ()):
            caller_path = str(caller)
            if caller_path not in implicated_set:
                unresolved.add(caller_path)
    if unresolved:
        rejections.append("PUBLIC_INTERFACE_CALLERS_UNRESOLVED")

    txn_files = observations.get("same_transaction_files")
    if txn_files is not None and changed_public_symbols:
        txn_set = {str(path) for path in txn_files}
        if any(
            str(caller) not in txn_set
            for symbol in changed_public_symbols
            for caller in caller_map.get(symbol, ())
        ):
            rejections.append("CALL_SITES_NOT_IN_SAME_TRANSACTION")

    evidence = dict(migration_evidence or {})
    if compatibility_evidence is not None:
        evidence["compatibility"] = compatibility_evidence
    if rollback_evidence is not None:
        evidence["rollback"] = rollback_evidence
    missing_migration: list[str] = []
    if migration_required:
        for key in ("compatibility", "rollback"):
            value = evidence.get(key)
            if value is None or value is False or value == "":
                missing_migration.append(key)
        if missing_migration:
            rejections.append("MIGRATION_EVIDENCE_INCOMPLETE")

    # An empty implicated set is not proof that a task had no surface.  It is
    # an unresolved observation, including for a greenfield task whose policy
    # must be supplied separately by the scaffold gate.
    if not implicated:
        rejections.append("IMPLICATED_SET_EMPTY")

    primary = tuple(str(path) for path in observations.get("primary_files", ()))
    if observations.get("coverage_ratio") == 1.0 and not primary:
        rejections.append("EMPTY_PRIMARY_VACUOUS_COVERAGE")

    return CompletenessReport(
        is_complete=not rejections,
        missing_inspections=tuple(missing),
        warnings=tuple(warnings),
        rejections=tuple(rejections),
        unresolved_callers=tuple(sorted(unresolved)),
        migration_evidence_missing=tuple(missing_migration),
        truncated=effective_truncated,
    )


class CodeDefaultCompletionPolicy:
    """Pack-owned adapter from runtime observations to an admission verdict."""

    spi_version = "1.0"

    @staticmethod
    def _run_greenfield_control(evidence: Mapping[str, Any]) -> Any:
        """Run the pack's vacuity control on runtime-collected evidence.

        The runtime owns execution and supplies the mediated control counts;
        this pack owns the semantic rule that a green empty-stub control is
        invalid. Keeping the call here makes the production completion path
        use the same gate as the pack contract tests.
        """
        try:
            from oracles.gate import GreenfieldControlOutcome, PackOracleGate
        except ImportError as exc:  # pragma: no cover - broken pack install
            return None, f"greenfield gate unavailable: {exc}"
        control = evidence.get("control")
        if not isinstance(control, Mapping):
            # Compatibility for direct SPI callers. The public runtime always
            # supplies ``control``; older pack callers supplied only the
            # explicit boolean and verification count.
            if isinstance(evidence.get("oracle_failed_on_stub"), bool):
                verification = evidence.get("verification")
                tests_run = getattr(
                    verification, "executed_test_count", 0)
                control = {
                    "tests_run": tests_run,
                    "failures": tests_run if evidence["oracle_failed_on_stub"] else 0,
                    "errors": 0,
                }
            else:
                return None, "greenfield control evidence missing"
        try:
            outcome = GreenfieldControlOutcome(
                tests_run=control.get("tests_run", control.get("testsRun")),
                failures=control.get("failures"),
                errors=control.get("errors", 0),
            )
        except (TypeError, ValueError):
            return None, "greenfield control evidence invalid"
        decision = PackOracleGate().run_greenfield_control(lambda: outcome)
        if hasattr(decision, "value"):
            return decision.value, ""
        return None, str(getattr(decision, "message", getattr(decision, "code", "control rejected")))

    def evaluate(
        self,
        preset_name: str,
        changed_files: Sequence[str],
        proposal: Mapping[str, Any],
        *,
        verification: Any = None,
        current_workspace_digest: str | None = None,
        inspected_files: Sequence[str] = (),
        task_text: str = "",
        implicated_files: Sequence[str] = (),
        **observations: Any,
    ) -> Mapping[str, Any]:
        """Return a serializable verdict; no effect authority is held here."""
        if proposal.get("kind") != "finish":
            return {"admissible": False, "reason": "MODEL_DID_NOT_REQUEST_FINISH"}
        changed = tuple(changed_files)
        if not changed:
            return {"admissible": False, "reason": "MISSING_SOURCE_PATCH"}
        primary = tuple(str(path) for path in observations.get("primary_files", ()))
        if observations.get("coverage_ratio") == 1.0 and not primary:
            return {"admissible": False, "reason": "EMPTY_PRIMARY_VACUOUS_COVERAGE"}
        surface = tuple(implicated_files) or changed
        classification = classify_task(task_text)
        bugfix_brief = classification.kind == "bugfix" or "bugfix" in task_text.lower()
        treat_greenfield = classification.kind == "greenfield" and not bugfix_brief
        if treat_greenfield:
            greenfield = observations.get("greenfield_evidence")
            if not isinstance(greenfield, Mapping):
                return {"admissible": False, "reason": "GREENFIELD_EVIDENCE_REQUIRED"}
            greenfield = dict(greenfield)
            greenfield.setdefault("verification", verification)
            control, control_error = self._run_greenfield_control(greenfield)
            if control is None:
                return {
                    "admissible": False,
                    "reason": (
                        "VACUOUS_ORACLE"
                        if greenfield.get("oracle_failed_on_stub") is False
                        else "GREENFIELD_CONTROL_REQUIRED"
                    ),
                }
            if greenfield.get("oracle_failed_on_stub") is False:
                return {"admissible": False, "reason": "VACUOUS_ORACLE"}
            required = (
                "baseline_recorded",
                "structural_passed",
                "smoke_test_created",
                "behavioral_passed",
                "oracle_failed_on_stub",
            )
            if any(not bool(greenfield.get(key)) for key in required):
                return {"admissible": False, "reason": "GREENFIELD_EVIDENCE_INCOMPLETE"}
        review_required = bool(observations.get("review_required", False))
        review_evidence = observations.get("review_evidence")
        if review_required and not review_evidence:
            return {"admissible": False, "reason": "REVIEW_REQUIRED"}
        if isinstance(review_evidence, Mapping):
            review_passed = bool(review_evidence.get("passed", False))
            review_patch_digest = str(review_evidence.get("patch_digest", review_evidence.get("patchDigest", "")))
            current_patch_digest = observations.get("current_patch_digest") or observations.get("patch_digest")
            if current_patch_digest and review_patch_digest and review_patch_digest != str(current_patch_digest):
                return {"admissible": False, "reason": "REVIEW_STALE"}
            if not review_passed:
                return {"admissible": False, "reason": "REVIEW_FAILED"}
        regression = observations.get("regression_evidence")
        if (isinstance(regression, Mapping)
                and regression.get("direct_passed") is True
                and regression.get("regression_passed") is False):
            return {"admissible": False, "reason": "AFFECTED_REGRESSION_FAILED"}
        report = check_multi_file_completeness(
            surface,
            inspected_files,
            changed,
            changed_public_symbols=observations.get("changed_public_symbols", ()),
            callers_by_symbol=observations.get("callers_by_symbol"),
            unresolved_callers=observations.get("unresolved_callers", ()),
            migration_required=classification.kind == "migration" or bool(observations.get("migration_required")),
            migration_evidence=observations.get("migration_evidence"),
            truncated=bool(observations.get("truncated", False)),
            truncation_metadata=observations.get("truncation_metadata"),
            primary_files=primary,
            coverage_ratio=observations.get("coverage_ratio"),
            same_transaction_files=observations.get("same_transaction_files"),
        )
        if (not treat_greenfield) and not report.is_complete:
            return {
                "admissible": False,
                "reason": report.rejections[0] if report.rejections else "COMPLETENESS_REJECTED",
                "rejections": report.rejections,
            }
        if verification is None:
            return {"admissible": False, "reason": "VERIFICATION_REQUIRED"}
        if isinstance(verification, Mapping):
            exit_code = verification.get("exit_code", verification.get("exitCode", -1))
            test_count = verification.get("executed_test_count", verification.get("executedTestCount", 0))
            workspace_digest = verification.get("workspace_digest", verification.get("workspaceDigest", ""))
            passed = int(exit_code) == 0 and int(test_count) > 0
        else:
            passed = bool(getattr(verification, "passed", False))
            workspace_digest = getattr(verification, "workspace_digest", "")
        if not passed:
            return {"admissible": False, "reason": "VERIFICATION_FAILED"}
        if not current_workspace_digest or workspace_digest != current_workspace_digest:
            return {"admissible": False, "reason": "VERIFICATION_STALE"}
        command = _verification_command(verification, observations)
        if _VACUOUS_VERIFICATION_COMMAND.match(command):
            return {"admissible": False, "reason": "VACUOUS_VERIFICATION_COMMAND"}
        if classification.kind == "bugfix":
            pre_verify = observations.get("pre_verify", observations.get("pre_verification"))
            if pre_verify is None:
                return {"admissible": False, "reason": "FAIL_TO_PASS_REQUIRED"}
            if _blob_passed(pre_verify):
                return {"admissible": False, "reason": "VACUOUS_REPRODUCER"}
            if not _blob_failed(pre_verify):
                return {"admissible": False, "reason": "FAIL_TO_PASS_REQUIRED"}
        task_test_ids = {str(item) for item in (observations.get("task_test_ids") or ())}
        executed_test_ids = {str(item) for item in (observations.get("executed_test_ids") or ())}
        if task_test_ids and task_test_ids.isdisjoint(executed_test_ids):
            return {"admissible": False, "reason": "UNRELATED_SUITE"}
        return {"admissible": True, "reason": "completion_admissible"}


def _verification_command(verification: Any, observations: Mapping[str, Any]) -> str:
    if observations.get("verification_command"):
        return str(observations["verification_command"])
    if isinstance(verification, Mapping):
        return str(
            verification.get("verification_command")
            or verification.get("verificationCommand")
            or verification.get("command")
            or ""
        )
    return str(getattr(verification, "verification_command", "") or "")


def _blob_passed(blob: Any) -> bool:
    if blob is None:
        return False
    if isinstance(blob, Mapping):
        if blob.get("passed") is True:
            return True
        exit_code = int(blob.get("exit_code", blob.get("exitCode", -1)))
        count = int(blob.get("executed_test_count", blob.get("executedTestCount", 0)))
        return exit_code == 0 and count > 0
    return bool(getattr(blob, "passed", False))


def _blob_failed(blob: Any) -> bool:
    if blob is None:
        return False
    if isinstance(blob, Mapping):
        if blob.get("passed") is False:
            return True
        return not _blob_passed(blob)
    return not bool(getattr(blob, "passed", False))


# Friendly aliases used by pack composition and direct policy tests.
CompletionPolicy = CodeDefaultCompletionPolicy
CompletenessPolicy = CodeDefaultCompletionPolicy
