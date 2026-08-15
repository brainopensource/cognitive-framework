"""REQ-SCHEMA-004..012: normative T1 wire contracts and two readers."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from vanguard.packages.domain import WIRE_KINDS, WireError, parse_wire
from vanguard.packages.domain.ledger import initial_state, parse_event_envelope, reduce_event

from .readers import ts_reader
from .schema_subset import SchemaSet, SchemaViolation

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas" / "v4"
SCHEMA_SET = SchemaSet(SCHEMAS)

CONTRACTS = {
    "EffectDescriptor": ("effect-descriptor.schema.json", "effect-descriptor"),
    "CapabilityGrant": ("capability-grant.schema.json", "capability-grant"),
    "Receipt": ("receipt.schema.json", "receipt"),
    "EventEnvelope": ("event-envelope.schema.json", "event-envelope"),
    "Artifact": ("artifact.schema.json", "artifact"),
    "EvidenceClaim": ("evidence-claim.schema.json", "evidence-claim"),
    "CorrectionRecord": ("correction-record.schema.json", "correction-record"),
    "Recording": ("recording.schema.json", "recording"),
    "ProcessDefinition": ("process-definition.schema.json", "process-definition"),
    "ProcessInstance": ("process-instance.schema.json", "process-instance"),
}


def _load(directory: str) -> list[tuple[str, str, object, dict]]:
    cases: list[tuple[str, str, object, dict]] = []
    for kind, (_, vector_name) in CONTRACTS.items():
        for path in sorted((SCHEMAS / "vectors" / vector_name / directory).glob("*.json")):
            if path.name.endswith(".expect.json"):
                continue
            expect_path = path.with_name(f"{path.stem}.expect.json")
            expect = json.loads(expect_path.read_text()) if expect_path.exists() else {}
            cases.append((f"{vector_name}/{path.stem}", kind,
                          json.loads(path.read_text()), expect))
    return cases


VALID = _load("valid")
INVALID = _load("invalid")


class WireVectorCoverage(unittest.TestCase):
    def test_both_readers_cover_exactly_the_active_contracts(self) -> None:
        self.assertEqual(set(WIRE_KINDS), set(CONTRACTS))
        response = ts_reader({"wire": []})
        self.assertEqual(set(response["wireKinds"]), set(CONTRACTS))

    def test_every_contract_has_valid_omission_and_type_vectors(self) -> None:
        for kind in CONTRACTS:
            with self.subTest(kind=kind):
                self.assertTrue(any(case_kind == kind for _, case_kind, _, _ in VALID))
                keywords = {expect.get("expectedKeyword") for _, case_kind, _, expect in INVALID
                            if case_kind == kind}
                self.assertIn("required", keywords)
                self.assertTrue("type" in keywords or "enum" in keywords)


class ValidWireVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ts = ts_reader({"wire": [{"kind": kind, "value": value}
                                     for _, kind, value, _ in VALID]})

    def test_normative_schemas_accept(self) -> None:
        for case, kind, value, _ in VALID:
            with self.subTest(vector=case):
                SCHEMA_SET.validate(value, CONTRACTS[kind][0])

    def test_python_reader_accepts_losslessly(self) -> None:
        for case, kind, value, _ in VALID:
            with self.subTest(vector=case):
                self.assertEqual(parse_wire(kind, value), value)

    def test_typescript_reader_accepts_losslessly(self) -> None:
        for index, (case, _, value, _) in enumerate(VALID):
            with self.subTest(vector=case):
                result = self.ts["wire"][index]
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["value"], value)


class InvalidWireVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ts = ts_reader({"wire": [{"kind": kind, "value": value}
                                     for _, kind, value, _ in INVALID]})

    def test_all_three_validators_reject(self) -> None:
        for index, (case, kind, value, expect) in enumerate(INVALID):
            with self.subTest(vector=case):
                with self.assertRaises(SchemaViolation) as schema_error:
                    SCHEMA_SET.validate(value, CONTRACTS[kind][0])
                self.assertEqual(schema_error.exception.keyword, expect["expectedKeyword"])
                with self.assertRaises(WireError):
                    parse_wire(kind, value)
                self.assertFalse(self.ts["wire"][index]["ok"])


class ReaderProfileAndMigration(unittest.TestCase):
    def test_writer_rejects_but_both_readers_preserve_minor_additions(self) -> None:
        value = json.loads((SCHEMAS / "vectors" / "recording" / "valid" / "minimal.json").read_text())
        value["vg41FutureField"] = {"nested": [1, 2, 3]}
        with self.assertRaises(SchemaViolation) as caught:
            SCHEMA_SET.validate(value, "recording.schema.json")
        self.assertEqual(caught.exception.keyword, "additionalProperties")
        SCHEMA_SET.validate(value, "recording.reader.schema.json")
        self.assertEqual(parse_wire("Recording", value), value)
        result = ts_reader({"wire": [{"kind": "Recording", "value": value}]})["wire"][0]
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["value"], value)

    def test_minor_event_addition_preserves_old_event_reduction(self) -> None:
        old_event = json.loads((SCHEMAS / "vectors" / "event-envelope" / "valid" /
                                "evolution-scope.json").read_text())
        old_state = reduce_event(initial_state(), parse_event_envelope(old_event))
        bumped = dict(old_event)
        bumped["schemaMinor"] = 1
        new_state = reduce_event(initial_state(), parse_event_envelope(bumped))
        self.assertEqual(old_state.digest(), new_state.digest())
        self.assertEqual(parse_event_envelope(bumped).unknown_fields["schemaMinor"], 1)


class SemanticWireRules(unittest.TestCase):
    def _valid(self, directory: str) -> object:
        return json.loads((SCHEMAS / "vectors" / directory / "valid" / "minimal.json").read_text())

    def test_grant_requires_budget_lease_and_binds_optional_authority_fields(self) -> None:
        grant = self._valid("capability-grant")
        grant["constraints"] = {}
        with self.assertRaises(WireError):
            parse_wire("CapabilityGrant", grant)
        full = self._valid("capability-grant")
        full.update({"parentGrantId": "parent-1", "approvalRef": "approval-1",
                     "authenticator": "mac-v1"})
        self.assertEqual(parse_wire("CapabilityGrant", full), full)

    def test_receipt_preserves_all_three_outcomes(self) -> None:
        base = self._valid("receipt")
        for outcome in ("ok", "failed"):
            with self.subTest(outcome=outcome):
                value = {**base, "outcome": outcome}
                self.assertEqual(parse_wire("Receipt", value), value)
        uncertain = {**base, "outcome": "undeterminable",
                     "uncertainty": {"scope": "effect_occurrence", "reason": "timeout"}}
        self.assertEqual(parse_wire("Receipt", uncertain), uncertain)

    def test_local_preferences_cannot_be_promoted_to_general_scope(self) -> None:
        correction = self._valid("correction-record")
        correction["reasonCodes"] = ["architecture_preference"]
        correction["scope"] = "general"
        with self.assertRaisesRegex(WireError, "remain local"):
            parse_wire("CorrectionRecord", correction)

    def test_process_definition_rejects_nondeterministic_transitions(self) -> None:
        definition = self._valid("process-definition")
        definition["transitions"] = [*definition["transitions"],
                                     {"from": "pending", "eventKind": "ApprovalResolved", "to": "pending"}]
        with self.assertRaisesRegex(WireError, "nondeterministic"):
            parse_wire("ProcessDefinition", definition)


if __name__ == "__main__":
    unittest.main()
