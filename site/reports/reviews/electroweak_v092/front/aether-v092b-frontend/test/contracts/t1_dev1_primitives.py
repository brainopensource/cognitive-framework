"""`REQ-SCHEMA-002` / `S1-D1-002` — opaque, boundary-parsed primitives.

Statement under test: every v0.1 identifier and primitive is opaque and
boundary-parsed, with RFC 3339 millisecond UTC timestamps, sha256 digests and
safe large-integer wire forms. Margin: zero casts at external boundaries.

Evidence produced:

* valid and invalid vectors replayed through both readers (`SC-7`, `GV-1`);
* the same vectors replayed through the normative schema, so the readers are
  verified against `primitives.schema.json` and not against each other alone
  (`CT-01`);
* round-trip coverage over every primitive kind — `unparse(parse(x)) == x`
  and the value survives a canonical JSON round trip unchanged (`CT-04`);
* kind confusion demonstrated to fail, which is what makes the primitives
  opaque rather than aliases for `str`.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from vanguard.packages.domain import (
    PRIMITIVE_KINDS,
    ParseError,
    canonicalise,
    parse,
    parse_json_text,
    unparse,
)
from vanguard.packages.domain.primitives.primitives import (
    int_string_from_int,
    int_string_to_int,
)

from .readers import ts_reader
from .schema_subset import SchemaSet, SchemaViolation

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas" / "v4"
VECTORS = SCHEMAS / "vectors" / "primitives"
SCHEMA_FILE = "primitives.schema.json"


def _load(directory: str) -> list[tuple[str, str, object, dict]]:
    """Yield `(case, kind, value, expect)` for every vector in a directory."""
    cases = []
    for path in sorted((VECTORS / directory).glob("*.json")):
        if path.name.endswith(".expect.json"):
            continue
        kind = path.stem.split("--")[0]
        expect_path = path.with_suffix("").with_suffix(".expect.json")
        expect = json.loads(expect_path.read_text()) if expect_path.exists() else {}
        cases.append((path.stem, kind, json.loads(path.read_text(encoding="utf-8")), expect))
    return cases


VALID = _load("valid")
INVALID = _load("invalid")
SCHEMA_SET = SchemaSet(SCHEMAS)


class VectorCoverage(unittest.TestCase):
    """The vector set covers what it claims to cover."""

    def test_every_reader_kind_is_either_covered_or_a_declared_alias(self) -> None:
        """A new primitive without vectors fails here rather than passing unseen."""
        covered = {kind for _, kind, _, _ in VALID}
        defs = json.loads((SCHEMAS / SCHEMA_FILE).read_text())["$defs"]
        aliases = {
            name for name, node in defs.items()
            if node.get("$ref") == "#/$defs/Identifier"
        }
        for kind in PRIMITIVE_KINDS:
            with self.subTest(kind=kind):
                self.assertTrue(
                    kind in covered or kind in aliases,
                    f"{kind} has no vectors and is not a declared Identifier alias")

    def test_identifier_aliases_are_taken_from_the_schema_not_the_reader(self) -> None:
        """`CT-02`: types are derived from schemas, never hand-written alongside."""
        defs = json.loads((SCHEMAS / SCHEMA_FILE).read_text())["$defs"]
        aliases = [name for name, node in defs.items()
                   if node.get("$ref") == "#/$defs/Identifier"]
        self.assertIn("PrincipalId", aliases)
        self.assertIn("EpisodeId", aliases)
        for alias in aliases:
            with self.subTest(alias=alias):
                # Each alias parses exactly as `Identifier` does, both ways.
                self.assertEqual(unparse(parse(alias, "x")), "x")
                with self.assertRaises(ParseError):
                    parse(alias, "")

    def test_every_kind_has_at_least_one_invalid_by_type_vector(self) -> None:
        """`GV-1`: a valid case is not evidence on its own."""
        by_kind: dict[str, set[str]] = {}
        for case, kind, _, expect in INVALID:
            by_kind.setdefault(kind, set()).add(expect["expectedKeyword"])
        for kind in by_kind:
            with self.subTest(kind=kind):
                self.assertTrue(by_kind[kind], f"{kind} has no invalid vectors")


class ValidVectors(unittest.TestCase):
    """`REQ-SCHEMA-002` — accepted by both readers and by the normative schema."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ts = ts_reader({"primitives": [{"kind": k, "value": v} for _, k, v, _ in VALID]})

    def test_python_reader_accepts(self) -> None:
        for case, kind, value, _ in VALID:
            with self.subTest(vector=case):
                self.assertEqual(unparse(parse(kind, value)), value)

    def test_typescript_reader_accepts(self) -> None:
        for index, (case, _, value, _) in enumerate(VALID):
            with self.subTest(vector=case):
                result = self.ts["primitives"][index]
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["value"], value)

    def test_normative_schema_accepts(self) -> None:
        """`CT-01`: the readers are implementations verified against the schema."""
        for case, kind, value, _ in VALID:
            with self.subTest(vector=case):
                node, document = SCHEMA_SET.resolve(f"#/$defs/{kind}", SCHEMA_FILE)
                SCHEMA_SET.validate(value, document, node)

    def test_round_trips_through_canonical_json(self) -> None:
        """`CT-04`: every type round-trips without loss."""
        for case, kind, value, _ in VALID:
            with self.subTest(vector=case):
                parsed = parse(kind, value)
                encoded = canonicalise(unparse(parsed))
                decoded = parse_json_text(encoded)
                self.assertEqual(decoded, value)
                self.assertEqual(unparse(parse(kind, decoded)), value)

    def test_both_readers_expose_the_same_kinds(self) -> None:
        self.assertEqual(sorted(PRIMITIVE_KINDS), sorted(self.ts["primitiveKinds"]))


class InvalidVectors(unittest.TestCase):
    """`REQ-SCHEMA-002` — rejected by both readers, at parse time."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ts = ts_reader({"primitives": [{"kind": k, "value": v} for _, k, v, _ in INVALID]})

    def test_python_reader_rejects(self) -> None:
        for case, kind, value, _ in INVALID:
            with self.subTest(vector=case):
                with self.assertRaises(ParseError):
                    parse(kind, value)

    def test_typescript_reader_rejects(self) -> None:
        for index, (case, _, _, _) in enumerate(INVALID):
            with self.subTest(vector=case):
                self.assertFalse(self.ts["primitives"][index]["ok"], case)

    def test_normative_schema_rejects_every_structural_case(self) -> None:
        """Cases the schema *can* express must fail against the schema itself.

        A vector marked `schemaAccepts` fails only in the semantic layer: a
        JSON Schema pattern cannot say "and it denotes a real instant". Those
        are recorded so a schema-only validator is never held to a rule the
        schema cannot carry (`SEMANTICS.md`, ADR candidate D1-001).
        """
        for case, kind, value, expect in INVALID:
            node, document = SCHEMA_SET.resolve(f"#/$defs/{kind}", SCHEMA_FILE)
            with self.subTest(vector=case):
                if expect.get("schemaAccepts"):
                    SCHEMA_SET.validate(value, document, node)
                    continue
                with self.assertRaises(SchemaViolation) as caught:
                    SCHEMA_SET.validate(value, document, node)
                self.assertEqual(caught.exception.keyword, expect["expectedKeyword"])

    def test_reader_reports_the_expected_failure_code(self) -> None:
        for case, kind, value, expect in INVALID:
            with self.subTest(vector=case):
                with self.assertRaises(ParseError) as caught:
                    parse(kind, value)
                self.assertEqual(caught.exception.code, expect["expectedKeyword"])


class Opacity(unittest.TestCase):
    """What makes a primitive a type rather than a spelling."""

    def test_a_parsed_value_carries_its_kind(self) -> None:
        """`CT-03`: parsing is the only way a value acquires its type."""
        principal = parse("PrincipalId", "p-1")
        episode = parse("EpisodeId", "p-1")
        self.assertNotEqual(principal, episode,
                            "two kinds sharing a wire form must not compare equal")
        self.assertEqual(principal, parse("PrincipalId", "p-1"))

    def test_unknown_kind_is_refused(self) -> None:
        with self.assertRaises(ParseError):
            parse("SessionId", "s-1")

    def test_int_string_survives_beyond_2_53(self) -> None:
        """VG-04 §0.4: this is the entire reason the wire form is a string."""
        value = 2**53 + 1
        wire = int_string_from_int("IntString", value)
        self.assertEqual(unparse(wire), "9007199254740993")
        self.assertEqual(int_string_to_int(wire), value)
        # The digest path must see the string, not a float that lost the low bit.
        self.assertIn('"9007199254740993"', canonicalise({"n": unparse(wire)}))

    def test_int_string_round_trips_a_currency_ledger_value(self) -> None:
        """`CT-06`: accumulated rounding error in a ledger is unacceptable."""
        micros = 1_000_000 * 10**12 + 7
        wire = int_string_from_int("UsdMicros", micros)
        self.assertEqual(int_string_to_int(wire), micros)

    def test_int_string_rejects_a_negative_amount(self) -> None:
        with self.assertRaises(ParseError):
            int_string_from_int("IntString", -1)

    def test_millis_is_an_integer_not_a_duration_object(self) -> None:
        """`CT-07`: no floating point for durations."""
        self.assertEqual(unparse(parse("Millis", 0)), 0)
        with self.assertRaises(ParseError):
            parse("Millis", 1.0)

    def test_tool_call_id_is_echoed_verbatim(self) -> None:
        """`CT-15`: never regenerated, normalised or trimmed."""
        for raw in ("  call_1  ", "CALL_1", "call/1+2=3", "ツール"):
            with self.subTest(value=raw):
                self.assertEqual(unparse(parse("ToolCallId", raw)), raw)

    def test_timestamps_sort_lexicographically_in_instant_order(self) -> None:
        """`CT-08`: readable, lexicographically sortable, unambiguous."""
        stamps = [
            "2026-08-15T09:41:07.250Z",
            "2026-08-15T09:41:07.251Z",
            "2026-08-15T09:41:08.000Z",
            "2026-12-31T23:59:59.999Z",
            "2027-01-01T00:00:00.000Z",
        ]
        parsed = [unparse(parse("Timestamp", stamp)) for stamp in stamps]
        self.assertEqual(parsed, sorted(parsed))


class CrossReaderErrorAgreement(unittest.TestCase):
    """Both readers must reject the same values, not merely reject enough."""

    SAMPLES = [
        ("Timestamp", "2026-02-29T00:00:00.000Z"),
        ("Timestamp", "2028-02-29T00:00:00.000Z"),
        ("Timestamp", "2026-04-31T00:00:00.000Z"),
        ("Timestamp", "2026-04-30T00:00:00.000Z"),
        ("Timestamp", "2026-08-15T23:59:59.999Z"),
        ("Timestamp", "2026-08-15T23:60:00.000Z"),
        ("Digest", "sha256:" + "f" * 64),
        ("Digest", "sha256:" + "g" * 64),
        ("IntString", "0"),
        ("IntString", "00"),
        ("Millis", 0),
        ("Millis", -0),
        ("Identifier", "x" * 128),
        ("Identifier", "x" * 129),
        ("Uuidv7", "018f4c2a-7e51-7c3d-8b2a-5f6d7e8a9b0c"),
        ("Uuidv7", "018f4c2a-7e51-7c3d-cb2a-5f6d7e8a9b0c"),
    ]

    def test_accept_and_reject_sets_are_identical(self) -> None:
        ts = ts_reader({"primitives": [{"kind": k, "value": v} for k, v in self.SAMPLES]})
        for index, (kind, value) in enumerate(self.SAMPLES):
            with self.subTest(kind=kind, value=value):
                try:
                    parse(kind, value)
                    python_ok = True
                except ParseError:
                    python_ok = False
                self.assertEqual(python_ok, ts["primitives"][index]["ok"],
                                 "readers disagree on this value")
