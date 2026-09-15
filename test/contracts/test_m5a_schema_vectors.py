"""M-5a semantic payload schemas and frozen JCS vectors, plus the
DIR-D1 durable carriers (`VerificationRecorded`, `ChangeSurfaceUpdated`)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.domain.canonicalisation.jcs import canonicalise

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_BY_KIND = {
    "GoalDeclared": "goal_declared.schema.json",
    "PlanRevised": "plan_revised.schema.json",
    "StrategyChanged": "strategy_changed.schema.json",
    "ProgressAssessed": "progress_assessed.schema.json",
    "ContextCompacted": "context_compacted.schema.json",
}


ENVELOPE_SCHEMA = ROOT / "schemas/mhf/event_envelope.schema.json"
V2_SCHEMA = ROOT / "schemas/mhf/event_envelope_v2.schema.json"
CARRIER_DEF_BY_KIND = {
    "VerificationRecorded": "VerificationRecordedPayload",
    "ChangeSurfaceUpdated": "ChangeSurfaceUpdatedPayload",
}


def _v2_validator() -> Draft202012Validator:
    """The `/2` envelope validator with its allocation document resolvable.

    `event_envelope_v2` `$ref`s the payload definitions by relative filename,
    so a validator built without the allocation document in its registry would
    fail to resolve and silently never exercise the conditional binding.
    """
    allocation = json.loads(ENVELOPE_SCHEMA.read_text())
    registry = Registry().with_resource(
        "event_envelope.schema.json", Resource.from_contents(allocation))
    return Draft202012Validator(
        json.loads(V2_SCHEMA.read_text()), registry=registry)


class SemanticVectors(unittest.TestCase):
    def test_all_five_payloads_validate_and_have_pinned_jcs_bytes(self) -> None:
        vectors = json.loads((ROOT / "test/fixtures/m5a_semantic_vectors.json").read_text())
        self.assertEqual({item["payload"]["kind"] for item in vectors}, set(SCHEMA_BY_KIND))
        for vector in vectors:
            kind = vector["payload"]["kind"]
            schema = json.loads((ROOT / "schemas/mhf" / SCHEMA_BY_KIND[kind]).read_text())
            payload_fields = {
                key: value for key, value in vector["payload"].items() if key != "kind"
            }
            errors = sorted(Draft202012Validator(schema).iter_errors(payload_fields), key=str)
            self.assertEqual(errors, [], kind)
            self.assertEqual(canonicalise(vector["payload"]), vector["canonical"], kind)
            self.assertEqual(digest_of(vector["payload"]), vector["digest"], kind)


class DirD1CarrierVectors(unittest.TestCase):
    """DIR-D1: typed payloads, `/2` payload validation, frozen JCS bytes."""

    def setUp(self) -> None:
        self.vectors = json.loads(
            (ROOT / "test/fixtures/dir_d1_carrier_vectors.json").read_text())
        self.allocation = json.loads(ENVELOPE_SCHEMA.read_text())

    def _envelope(self, payload: dict) -> dict:
        return {
            "schema_version": "mhf.event/2",
            "event_id": "018f0000-0000-7000-8000-000000000001",
            "kind": payload["kind"],
            "seq": 1,
            "occurred_at": "2026-09-12T00:00:00.000Z",
            "run_id": "run-d1",
            "principal": "agent-1",
            "payload": payload,
            "digest": "sha256:" + "0" * 64,
            "authority_source": "kernel-capability",
            "policy_version": "1",
        }

    def test_both_kinds_are_allocated_in_the_shared_enum(self) -> None:
        enum = self.allocation["$defs"]["EventKind"]["enum"]
        for kind in CARRIER_DEF_BY_KIND:
            self.assertIn(kind, enum)
        # DIR-D1 authorises exactly two. The other sixteen unwritable fold
        # names stay out of the allocation, and none of them is deprecated.
        self.assertEqual(len(enum), len(set(enum)))

    def test_each_vector_validates_against_its_typed_payload(self) -> None:
        self.assertEqual(
            {v["payload"]["kind"] for v in self.vectors}, set(CARRIER_DEF_BY_KIND))
        for vector in self.vectors:
            kind = vector["payload"]["kind"]
            schema = self.allocation["$defs"][CARRIER_DEF_BY_KIND[kind]]
            errors = sorted(
                Draft202012Validator(schema).iter_errors(vector["payload"]), key=str)
            self.assertEqual(errors, [], kind)

    def test_each_vector_has_pinned_canonical_bytes_and_digest(self) -> None:
        for vector in self.vectors:
            kind = vector["payload"]["kind"]
            self.assertEqual(canonicalise(vector["payload"]), vector["canonical"], kind)
            self.assertEqual(digest_of(vector["payload"]), vector["digest"], kind)

    def test_the_v2_envelope_binds_the_typed_payload_by_kind(self) -> None:
        validator = _v2_validator()
        for vector in self.vectors:
            errors = sorted(
                validator.iter_errors(self._envelope(vector["payload"])), key=str)
            self.assertEqual(errors, [], vector["payload"]["kind"])

    def test_the_v2_binding_rejects_an_untyped_carrier_payload(self) -> None:
        """ADVERSARIAL: `/2` validation is not vacuous.

        Before DIR-D1 the envelope's `payload` was an unconstrained object, so
        a carrier could append any shape and replay would trust it. Each
        mutation below must be rejected by the envelope, not merely by the
        standalone payload schema.
        """
        validator = _v2_validator()
        by_kind = {v["payload"]["kind"]: v["payload"] for v in self.vectors}

        missing_binding = dict(by_kind["VerificationRecorded"])
        missing_binding.pop("workspaceDigest")

        wrong_digest_shape = dict(by_kind["VerificationRecorded"])
        wrong_digest_shape["taskDigest"] = "not-a-digest"

        zero_for_unknown = dict(by_kind["VerificationRecorded"])
        zero_for_unknown["observedTestCount"] = "7"

        undeclared_field = dict(by_kind["ChangeSurfaceUpdated"])
        undeclared_field["passed"] = True

        incomplete_surface = dict(by_kind["ChangeSurfaceUpdated"])
        incomplete_surface["changeSurface"] = ["a.py", "a.py"]

        absolute_path = dict(by_kind["ChangeSurfaceUpdated"])
        absolute_path["deletedPaths"] = ["/etc/passwd"]

        missing_deletions = dict(by_kind["ChangeSurfaceUpdated"])
        missing_deletions.pop("deletedPaths")

        for label, payload in (
            ("missing workspace binding", missing_binding),
            ("malformed digest", wrong_digest_shape),
            ("string test count", zero_for_unknown),
            ("undeclared field", undeclared_field),
            ("duplicate surface entry", incomplete_surface),
            ("absolute deleted path", absolute_path),
            ("deletions omitted", missing_deletions),
        ):
            with self.subTest(label):
                errors = list(validator.iter_errors(self._envelope(payload)))
                self.assertNotEqual(errors, [], label)

    def test_the_envelope_still_accepts_an_open_payload_for_other_kinds(self) -> None:
        """Retained compatibility: only these two kinds gained a constraint.

        Retroactively typing kinds whose ledgers already exist would make valid
        history invalid, so every other kind keeps the historical open payload.
        """
        validator = _v2_validator()
        envelope = self._envelope({"kind": "EffectCompleted", "anything": [1, 2]})
        self.assertEqual(list(validator.iter_errors(envelope)), [])


if __name__ == "__main__":
    unittest.main()
