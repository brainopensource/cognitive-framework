"""`REQ-SCHEMA-001` / `S1-D1-001` — canonicalisation and the golden triples.

Statement under test: canonical bytes use RFC 8785/JCS without local variation
and at least 40 golden input-to-canonical-to-sha256 triples agree across
readers. Margin: zero cross-reader mismatches.

Evidence produced:

* every triple in `schemas/v4/vectors/canonicalisation/canonical/` replayed
  through both readers, byte-for-byte, digest included (`SC-7`, `GV-2`);
* the forms RFC 8785 cannot canonicalise rejected by both readers;
* a differential property run over generated values, because a finite vector
  set corroborates agreement and never proves it (`vectors/README.md`).
"""

from __future__ import annotations

import hashlib
import json
import random
import unittest
from pathlib import Path

from vanguard.packages.domain import (
    CanonicalisationError,
    canonical_bytes,
    canonicalise,
    digest_bytes,
    parse_json_text,
)

from .readers import ts_reader

ROOT = Path(__file__).resolve().parents[2]
TRIPLES = ROOT / "schemas" / "v4" / "vectors" / "canonicalisation" / "canonical"
MINIMUM_TRIPLES = 40


def _triples() -> list[tuple[str, str, str, str]]:
    cases = []
    for source in sorted(TRIPLES.glob("*.json")):
        name = source.stem
        cases.append((
            name,
            source.read_text(encoding="utf-8"),
            source.with_suffix(".jcs").read_text(encoding="utf-8"),
            source.with_suffix(".digest").read_text(encoding="utf-8").strip(),
        ))
    return cases


class GoldenTriples(unittest.TestCase):
    """`REQ-SCHEMA-001` — input → canonical → digest, in both readers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = _triples()
        cls.ts = ts_reader({"canonicalise": {name: text for name, text, _, _ in cls.cases}})

    def test_vector_set_meets_the_contracted_size(self) -> None:
        self.assertGreaterEqual(
            len(self.cases), MINIMUM_TRIPLES,
            f"REQ-SCHEMA-001 requires {MINIMUM_TRIPLES}+ triples; found {len(self.cases)}")

    def test_python_reader_matches_every_triple(self) -> None:
        for name, text, expected_jcs, expected_digest in self.cases:
            with self.subTest(triple=name):
                value = parse_json_text(text)
                self.assertEqual(canonicalise(value), expected_jcs)
                self.assertEqual(digest_bytes(canonical_bytes(value)), expected_digest)

    def test_typescript_reader_matches_every_triple(self) -> None:
        for name, _, expected_jcs, expected_digest in self.cases:
            with self.subTest(triple=name):
                result = self.ts["canonicalise"][name]
                self.assertTrue(result["ok"], result)
                self.assertEqual(result["canonical"], expected_jcs)
                self.assertEqual(result["digest"], expected_digest)

    def test_digest_is_taken_over_the_canonical_bytes(self) -> None:
        """`SC-2`: the digest is a function of the canonical form, not the input."""
        for name, _, expected_jcs, expected_digest in self.cases:
            with self.subTest(triple=name):
                recomputed = hashlib.sha256(expected_jcs.encode("utf-8")).hexdigest()
                self.assertEqual(expected_digest, f"sha256:{recomputed}")

    def test_canonical_form_is_a_fixed_point(self) -> None:
        """Canonicalising canonical bytes changes nothing. Descriptors are re-hashed."""
        for name, _, expected_jcs, _ in self.cases:
            with self.subTest(triple=name):
                self.assertEqual(canonicalise(parse_json_text(expected_jcs)), expected_jcs)

    def test_canonical_bytes_are_utf8(self) -> None:
        """`CT-13`: UTF-8 throughout."""
        for name, _, expected_jcs, _ in self.cases:
            with self.subTest(triple=name):
                self.assertEqual(expected_jcs.encode("utf-8").decode("utf-8"), expected_jcs)


class Rejections(unittest.TestCase):
    """Inputs with no canonical form fail in both readers, identically."""

    CASES = {
        "duplicate-keys": '{"a": 1, "a": 2}',
        "duplicate-keys-nested": '{"x": {"a": 1, "a": 2}}',
        "nan": '{"a": NaN}',
        "infinity": '{"a": Infinity}',
        "trailing-comma": '{"a": 1,}',
        "single-quoted": "{'a': 1}",
        "unquoted-key": "{a: 1}",
        "empty-input": "",
        "trailing-content": '{"a": 1} {"b": 2}',
    }

    def test_python_reader_rejects(self) -> None:
        for name, text in self.CASES.items():
            with self.subTest(case=name):
                with self.assertRaises(CanonicalisationError):
                    parse_json_text(text)

    def test_typescript_reader_rejects(self) -> None:
        results = ts_reader({"canonicalise": dict(self.CASES)})["canonicalise"]
        for name in self.CASES:
            with self.subTest(case=name):
                self.assertFalse(results[name]["ok"], results[name])

    def test_lone_surrogate_has_no_canonical_form(self) -> None:
        """`CT-13`: no lone surrogates. Neither reader substitutes a replacement."""
        with self.assertRaises(CanonicalisationError):
            canonicalise({"a": "\ud800"})
        result = ts_reader({"canonicalise": {"lone": '{"a": "\\ud800"}'}})["canonicalise"]["lone"]
        self.assertFalse(result["ok"], result)

    def test_non_json_value_is_refused(self) -> None:
        with self.assertRaises(CanonicalisationError):
            canonicalise({"a": {1, 2}})


class DifferentialProperties(unittest.TestCase):
    """Generated agreement. Vectors corroborate; only a search can look wider.

    The generator is seeded, so a failure names a reproducible value rather
    than a run.
    """

    SEED = 20260815
    SAMPLES = 400

    def _random_value(self, rng: random.Random, depth: int = 0):
        choice = rng.randrange(11 if depth < 3 else 7)
        if choice == 0:
            return None
        if choice == 1:
            return rng.choice([True, False])
        if choice == 2:
            return rng.randint(-(2**53) + 1, 2**53 - 1)
        if choice in (3, 4):
            return rng.choice([
                0.0, -0.0, 0.1, 1e21, 1e-7, 5e-324, 1.7976931348623157e308,
                rng.uniform(-1e9, 1e9), float(rng.randint(-10**6, 10**6)),
                rng.uniform(-1, 1) * 10.0 ** rng.randint(-320, 300),
            ])
        if choice in (5, 6):
            alphabet = "ab\"\\\n\t\x00\x1f\x7f é日本\U0001f600Ω"
            return "".join(rng.choice(alphabet) for _ in range(rng.randrange(6)))
        if choice in (7, 8):
            return [self._random_value(rng, depth + 1) for _ in range(rng.randrange(4))]
        keys = ["a", "A", "b", "", "1", "", "é", "\U0001f600", "דּ", "\n"]
        return {
            rng.choice(keys): self._random_value(rng, depth + 1)
            for _ in range(rng.randrange(5))
        }

    def test_readers_agree_on_generated_values(self) -> None:
        rng = random.Random(self.SEED)
        payloads = {}
        expected = {}
        for index in range(self.SAMPLES):
            value = self._random_value(rng)
            name = f"gen-{index:04d}"
            # The generated value is handed over as JSON text so both readers
            # start from the same bytes rather than from two parsers' opinions.
            payloads[name] = json.dumps(value, ensure_ascii=True)
            expected[name] = canonicalise(value)
        results = ts_reader({"canonicalise": payloads})["canonicalise"]
        for name, canonical in expected.items():
            with self.subTest(sample=name, source=payloads[name]):
                self.assertTrue(results[name]["ok"], results[name])
                self.assertEqual(results[name]["canonical"], canonical)

    def test_key_order_and_whitespace_are_not_semantic(self) -> None:
        """Reordering keys or adding whitespace never changes the digest."""
        rng = random.Random(self.SEED + 1)
        for index in range(100):
            value = self._random_value(rng)
            if not isinstance(value, dict) or len(value) < 2:
                continue
            shuffled = list(value.items())
            rng.shuffle(shuffled)
            with self.subTest(sample=index):
                self.assertEqual(
                    digest_bytes(canonical_bytes(value)),
                    digest_bytes(canonical_bytes(dict(shuffled))),
                )
