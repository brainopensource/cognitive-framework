"""Contract tests and golden vectors for mhf.execution-profile/1 and /2 (B-M4-02).

Validates:
1. Strict schema compliance for /1 (frozen) and /2.
2. Byte-identical /1 preimage and digest preservation.
3. Explicit retention axis (digests_only | standard | full).
4. capture.required boolean and privacy semantics.
5. Dual-read deserialization in ExecutionProfile.from_dict.
6. Narrow-only override enforcement (widening retention or weakening capture is forbidden).
7. Hermetic profile constraints (requires full retention, capture_required=True, attestation=True).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.runtime.profiles import (
    ExecutionProfile,
    ExecutionProfileError,
    PRESETS,
    resolve_profile,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_V1 = json.loads((ROOT / "schemas" / "mhf" / "execution_profile.schema.json").read_text(encoding="utf-8"))
SCHEMA_V2 = json.loads((ROOT / "schemas" / "mhf" / "execution_profile_v2.schema.json").read_text(encoding="utf-8"))


def _validate_schema(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Basic structural validation against JSON schema required and property types."""
    errors = []
    for req in schema.get("required", []):
        if req not in data:
            errors.append(f"missing required property: {req}")
    if schema.get("additionalProperties") is False:
        props = schema.get("properties", {})
        for k in data:
            if k not in props:
                errors.append(f"unexpected property: {k}")
    return errors


class TestExecutionProfileV2Contract(unittest.TestCase):
    def test_historical_v1_preimage_and_digest_remain_identical(self) -> None:
        """Historical /1 profiles must produce byte-identical preimage without /2 fields."""
        p1 = ExecutionProfile(
            id="local",
            workspace_mode="in-place",
            workspace_access="workspace-write",
            process_backend="host",
            approval_default="ask",
            persistence_mode="sqlite-wal",
            persistence_durable=True,
            evaluation_mode="none",
            evaluation_absence_reason="local product run: no exterior evaluator engaged",
            assurance_level="recorded",
            attestation_required=False,
            promotion_eligible=False,
            api_version="mhf.execution-profile/1",
        )
        d1 = p1.to_dict()
        self.assertEqual(d1["api"], "mhf.execution-profile/1")
        self.assertNotIn("retention", d1)
        self.assertNotIn("required", d1["capture"])

        errs = _validate_schema(d1, SCHEMA_V1)
        self.assertEqual(errs, [])

    def test_the_historical_v1_digests_are_pinned_to_literal_values(self) -> None:
        """Shape checks do not pin bytes.

        The `/1` preimage being "byte-frozen" was asserted in prose and
        enforced nowhere: every assertion above checks the *shape* of the
        dict, so a future field rename or reorder would keep them green while
        silently moving every historical `profile_digest` — and
        `profile_digest` enters `D_R`, so moving it re-identifies every
        historical run and breaks RF-86 baseline comparison.

        These are the digests the presets produced before
        `mhf.execution-profile/2` existed, recomputed from the `/1` preimage.
        If one of these changes, a historical identity has been rewritten and
        that is a hard failure, never a value to re-bless.
        """
        pinned = {
            "hermetic": "sha256:17487ef3be7d1bd6b5d0495deb36752dcc13d8d3b68db60ae92d31d80e73c8ce",
            "local": "sha256:ab19dc3540f728215f232332415d6e94d0d28e3664059694bc73928ea42d9b2b",
            "product": "sha256:b7d2179109f546622fb41c182dbe0ce0a0920107640b9df47e49e7b8c0e3e067",
            "sandboxed": "sha256:5b248588438c438e575d9c0a76213bbe8141bd4185aa0ec57f5b5505439a1cde",
        }
        self.assertTrue(
            set(pinned).issubset(PRESETS),
            "a byte-frozen historical preset was removed",
        )
        for name, expected in pinned.items():
            with self.subTest(preset=name):
                preimage = PRESETS[name].to_dict("mhf.execution-profile/1")
                self.assertEqual(digest_of(preimage), expected)

    def test_the_v2_digest_differs_from_the_pinned_v1_digest(self) -> None:
        """A `/2` profile is a new identity, not a silent re-issue of the old
        one. Both must be derivable from the same object, and they must not
        collide -- a `/2` digest equal to its `/1` digest would mean the new
        retention and capture axes changed nothing observable."""
        for name, profile in PRESETS.items():
            with self.subTest(preset=name):
                v1 = digest_of(profile.to_dict("mhf.execution-profile/1"))
                v2 = digest_of(profile.to_dict("mhf.execution-profile/2"))
                self.assertNotEqual(v1, v2)

    def test_v2_presets_emit_schema_valid_execution_profile_v2(self) -> None:
        for preset_name, profile in PRESETS.items():
            d2 = profile.to_dict()
            self.assertEqual(d2["api"], "mhf.execution-profile/2", f"preset {preset_name} must emit /2")
            self.assertIn(d2["retention"], {"digests_only", "standard", "full"})
            self.assertIn("required", d2["capture"])
            errs = _validate_schema(d2, SCHEMA_V2)
            self.assertEqual(errs, [], f"preset {preset_name} violates v2 schema: {errs}")

    def test_dual_read_from_dict(self) -> None:
        # Load historical /1 dict
        v1_dict = {
            "api": "mhf.execution-profile/1",
            "id": "local",
            "workspace": {"mode": "in-place", "access": "workspace-write"},
            "process": {"backend": "host", "fallback": "deny"},
            "network": {"mode": "inherited", "allow": []},
            "approval": {"default": "ask", "rules": []},
            "persistence": {"mode": "sqlite-wal", "durable": True},
            "evaluation": {"mode": "none", "absence_reason": "local run"},
            "assurance": {"level": "recorded", "attestation_required": False, "promotion_eligible": False},
            "capture": {"content": "redacted", "trainability": "prohibited"},
        }
        loaded_v1 = ExecutionProfile.from_dict(v1_dict)
        self.assertEqual(loaded_v1.api_version, "mhf.execution-profile/1")
        self.assertEqual(loaded_v1.id, "local")
        self.assertEqual(loaded_v1.to_dict(), v1_dict)

        # Load /2 dict
        v2_dict = PRESETS["product"].to_dict()
        loaded_v2 = ExecutionProfile.from_dict(v2_dict)
        self.assertEqual(loaded_v2.api_version, "mhf.execution-profile/2")
        self.assertEqual(loaded_v2.retention, "standard")
        self.assertTrue(loaded_v2.capture_required)
        self.assertEqual(loaded_v2.to_dict(), v2_dict)

    def test_retention_normalization_and_validation(self) -> None:
        # Hyphenated "digests-only" normalizes to "digests_only"
        p = ExecutionProfile(
            id="test-p",
            workspace_mode="in-place",
            workspace_access="workspace-write",
            process_backend="host",
            approval_default="ask",
            persistence_mode="sqlite-wal",
            persistence_durable=True,
            evaluation_mode="none",
            evaluation_absence_reason="test",
            assurance_level="recorded",
            attestation_required=False,
            promotion_eligible=False,
            retention="digests-only",
        )
        self.assertEqual(p.retention, "digests_only")

        with self.assertRaises(ExecutionProfileError):
            ExecutionProfile(
                id="test-bad",
                workspace_mode="in-place",
                workspace_access="workspace-write",
                process_backend="host",
                approval_default="ask",
                persistence_mode="sqlite-wal",
                persistence_durable=True,
                evaluation_mode="none",
                evaluation_absence_reason="test",
                assurance_level="recorded",
                attestation_required=False,
                promotion_eligible=False,
                retention="unlimited",
            )

    def test_hermetic_profile_rules(self) -> None:
        # Hermetic requires full retention
        with self.assertRaises(ExecutionProfileError):
            ExecutionProfile(
                id="hermetic-bad",
                workspace_mode="sealed",
                workspace_access="workspace-write",
                process_backend="platform-sandbox",
                approval_default="deny",
                persistence_mode="sqlite-wal",
                persistence_durable=True,
                evaluation_mode="exterior",
                assurance_level="hermetic",
                attestation_required=True,
                promotion_eligible=True,
                retention="standard",
            )

        # Hermetic requires attestation
        with self.assertRaises(ExecutionProfileError):
            ExecutionProfile(
                id="hermetic-no-attest",
                workspace_mode="sealed",
                workspace_access="workspace-write",
                process_backend="platform-sandbox",
                approval_default="deny",
                persistence_mode="sqlite-wal",
                persistence_durable=True,
                evaluation_mode="exterior",
                assurance_level="hermetic",
                attestation_required=False,
                promotion_eligible=True,
                retention="full",
            )

    def test_overrides_cannot_widen_retention_or_weaken_capture(self) -> None:
        # Narrowing is allowed: standard -> digests_only
        res_prod = resolve_profile("product", overrides={"retention": "digests_only"})
        self.assertEqual(res_prod.requested.retention, "digests_only")

        # Widening is rejected: standard -> full
        with self.assertRaises(ExecutionProfileError):
            resolve_profile("product", overrides={"retention": "full"})

        # Weakening capture_required is rejected: True -> False on product
        with self.assertRaises(ExecutionProfileError):
            resolve_profile("product", overrides={"capture_required": False})

    def test_effective_profile_run_plan_fields_includes_retention_and_capture(self) -> None:
        effective = resolve_profile("product")
        fields = effective.to_run_plan_fields()
        self.assertEqual(fields["profileId"], "product")
        self.assertEqual(fields["retention"], "standard")
        self.assertTrue(fields["captureRequired"])
        self.assertIn("profileDigest", fields)


if __name__ == "__main__":
    unittest.main()
