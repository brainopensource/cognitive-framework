"""Golden, negative, and malformed vectors for the vg.4 command contract.

Covers `vanguard/packages/runtime/service/contract.py`, the hand-written
mirror of `schemas/v4/runtime-service.schema.json`'s discriminated command
union. Not yet wired into `RuntimeService.execute_command` (tracked as a
follow-up); these tests pin the vocabulary and rules on their own.
"""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.service.contract import (
    ContractError,
    ERROR_CODES,
    error_code_for_exception,
    validate_command,
    validate_frame_envelope,
)


def _decision(**overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "approvalId": "appr-1",
        "resolution": "approved",
        "reviewer": "operator",
        "argsDigest": "sha256:" + "a" * 64,
        "descriptorDigest": "sha256:" + "b" * 64,
        "expiresAt": "2026-08-27T12:00:00.000Z",
        "keyId": "operator-key-default",
        "signature": "deadbeef",
    }
    base.update(overrides)
    return base


class TestErrorVocabulary(unittest.TestCase):
    def test_canonical_error_codes_match_ten_entry_table(self) -> None:
        self.assertEqual(
            ERROR_CODES,
            frozenset(
                {
                    "invalid_request",
                    "unauthenticated",
                    "permission_denied",
                    "not_found",
                    "conflict",
                    "incompatible_version",
                    "frame_too_large",
                    "rate_limited",
                    "not_available",
                    "internal",
                }
            ),
        )

    def test_contract_error_rejects_unknown_code(self) -> None:
        with self.assertRaises(ValueError):
            ContractError("bogus_code", "message")

    def test_error_code_for_value_error_is_invalid_request(self) -> None:
        self.assertEqual(error_code_for_exception(ValueError("x")), "invalid_request")

    def test_error_code_for_generic_exception_is_internal(self) -> None:
        self.assertEqual(error_code_for_exception(RuntimeError("x")), "internal")

    def test_error_code_for_contract_error_is_its_own_code(self) -> None:
        self.assertEqual(error_code_for_exception(ContractError("not_found", "x")), "not_found")


class TestFrameEnvelope(unittest.TestCase):
    def test_golden_command_frame_envelope(self) -> None:
        validate_frame_envelope({"version": "vg.4", "frameType": "command", "frameId": "f-1"})

    def test_wrong_version_is_incompatible_version(self) -> None:
        with self.assertRaises(ContractError) as ctx:
            validate_frame_envelope({"version": "vg.3", "frameType": "command", "frameId": "f-1"})
        self.assertEqual(ctx.exception.code, "incompatible_version")

    def test_missing_frame_id_is_invalid_request(self) -> None:
        with self.assertRaises(ContractError) as ctx:
            validate_frame_envelope({"version": "vg.4", "frameType": "command", "frameId": ""})
        self.assertEqual(ctx.exception.code, "invalid_request")

    def test_non_object_frame_is_invalid_request(self) -> None:
        with self.assertRaises(ContractError) as ctx:
            validate_frame_envelope("not a frame")
        self.assertEqual(ctx.exception.code, "invalid_request")


class TestCommandGoldenVectors(unittest.TestCase):
    def test_start_run_golden(self) -> None:
        cmd = validate_command(
            {
                "name": "StartRun",
                "commandId": "c-1",
                "idempotencyKey": "i-1",
                "runId": "run-1",
                "payload": {"manifestPath": "m.json", "repoPath": ".", "brief": "do it"},
            }
        )
        self.assertEqual(cmd.name, "StartRun")
        self.assertEqual(cmd.run_id, "run-1")

    def test_list_runs_golden_with_empty_run_id(self) -> None:
        cmd = validate_command(
            {"name": "ListRuns", "commandId": "c-2", "idempotencyKey": "i-2", "runId": "", "payload": {}}
        )
        self.assertEqual(cmd.run_id, "")

    def test_get_capabilities_golden_without_run_id_key(self) -> None:
        validate_command({"name": "GetCapabilities", "commandId": "c-3", "idempotencyKey": "i-3"})

    def test_resolve_approval_golden(self) -> None:
        validate_command(
            {
                "name": "ResolveApproval",
                "commandId": "c-4",
                "idempotencyKey": "i-4",
                "runId": "run-1",
                "payload": {"decision": _decision()},
            }
        )

    def test_explain_artifact_golden_run_id_optional(self) -> None:
        validate_command(
            {"name": "ExplainArtifact", "commandId": "c-5", "idempotencyKey": "i-5", "payload": {"artifactId": "art-1"}}
        )
        validate_command(
            {
                "name": "ExplainArtifact",
                "commandId": "c-6",
                "idempotencyKey": "i-6",
                "runId": "run-1",
                "payload": {"artifactId": "art-1"},
            }
        )


class TestCommandNegativeVectors(unittest.TestCase):
    def test_unknown_command_name_rejected(self) -> None:
        with self.assertRaises(ContractError) as ctx:
            validate_command({"name": "DeleteEverything", "commandId": "c-1", "idempotencyKey": "i-1"})
        self.assertEqual(ctx.exception.code, "invalid_request")

    def test_unknown_top_level_field_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command(
                {
                    "name": "GetCapabilities",
                    "commandId": "c-1",
                    "idempotencyKey": "i-1",
                    "sneaky": "field",
                }
            )

    def test_missing_run_id_on_run_scoped_command_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command({"name": "GetRun", "commandId": "c-1", "idempotencyKey": "i-1"})

    def test_non_empty_run_id_on_forbidden_scope_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command(
                {"name": "ListRuns", "commandId": "c-1", "idempotencyKey": "i-1", "runId": "run-1"}
            )
        with self.assertRaises(ContractError):
            validate_command(
                {"name": "GetCapabilities", "commandId": "c-1", "idempotencyKey": "i-1", "runId": "run-1"}
            )

    def test_start_run_missing_required_payload_field_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command(
                {
                    "name": "StartRun",
                    "commandId": "c-1",
                    "idempotencyKey": "i-1",
                    "runId": "run-1",
                    "payload": {"manifestPath": "m.json", "repoPath": "."},
                }
            )

    def test_resolve_approval_missing_decision_object_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command(
                {
                    "name": "ResolveApproval",
                    "commandId": "c-1",
                    "idempotencyKey": "i-1",
                    "runId": "run-1",
                    "payload": {},
                }
            )

    def test_resolve_approval_flat_string_decision_rejected(self) -> None:
        """The historical gateway bug: a bare 'approve' string is not a decision object."""
        with self.assertRaises(ContractError):
            validate_command(
                {
                    "name": "ResolveApproval",
                    "commandId": "c-1",
                    "idempotencyKey": "i-1",
                    "runId": "run-1",
                    "payload": {"decision": "approve"},
                }
            )

    def test_resolve_approval_incomplete_decision_rejected(self) -> None:
        incomplete = _decision()
        del incomplete["signature"]
        with self.assertRaises(ContractError):
            validate_command(
                {
                    "name": "ResolveApproval",
                    "commandId": "c-1",
                    "idempotencyKey": "i-1",
                    "runId": "run-1",
                    "payload": {"decision": incomplete},
                }
            )

    def test_resolve_approval_bad_resolution_enum_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command(
                {
                    "name": "ResolveApproval",
                    "commandId": "c-1",
                    "idempotencyKey": "i-1",
                    "runId": "run-1",
                    "payload": {"decision": _decision(resolution="maybe")},
                }
            )

    def test_empty_command_id_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command({"name": "GetCapabilities", "commandId": "", "idempotencyKey": "i-1"})

    def test_empty_idempotency_key_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command({"name": "GetCapabilities", "commandId": "c-1", "idempotencyKey": ""})

    def test_non_object_payload_rejected(self) -> None:
        with self.assertRaises(ContractError):
            validate_command(
                {"name": "GetRun", "commandId": "c-1", "idempotencyKey": "i-1", "runId": "run-1", "payload": "nope"}
            )


if __name__ == "__main__":
    unittest.main()
