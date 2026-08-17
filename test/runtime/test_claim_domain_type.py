"""`Claim` as a domain type. Format lock (`L-1`).

S8-A-05. Every run after this records evidence in the final shape; every run
before it needs migration. The shape is not invented here -- `VG-04 §10.2` and
`schemas/v4/evidence-claim.schema.json` already own it, and `GTS-13C T1.9` says
to keep it exactly as v4 wrote it. This adds the pure, no-I/O domain type and
the two rules a schema cannot express:

  - `INV-1` an empty `invalidationConditions` array fails at parse;
  - `C-12` / `INV-2` a claim whose `substrateProfile` digest has moved is stale
    **without human review**.
"""

from __future__ import annotations

import unittest

from vanguard.packages.domain.evidence.claim import (
    Claim,
    ClaimError,
    InvalidationCondition,
    parse_claim,
)

DIGEST_A = "sha256:" + "a" * 64
DIGEST_B = "sha256:" + "b" * 64
DIGEST_C = "sha256:" + "c" * 64
DIGEST_D = "sha256:" + "d" * 64


def wire(**overrides: object) -> dict:
    base = {
        "id": "claim-1",
        "subject": "artifact-1",
        "predicate": "repairs.single_file_bug",
        "value": 0.62,
        "protocol": DIGEST_A,
        "evaluator": {
            "evaluatorId": "evaluator-suite-1",
            "class": "mechanically_reproducible",
            "imageDigest": DIGEST_B,
        },
        "environmentProfile": DIGEST_C,
        "substrateProfile": DIGEST_D,
        "taskDistribution": DIGEST_A,
        "uncertainty": {"kind": "interval", "lower": 0.51, "upper": 0.73, "n": 40},
        "validity": {"domains": ["python", "single-file"]},
        "invalidationConditions": [
            {
                "condition": "the oracle suite fails",
                "checkKind": "automatic",
                "checkRef": "evaluator-suite-1",
            }
        ],
    }
    base.update(overrides)
    return base


class InvalidationIsNotOptional(unittest.TestCase):
    def test_an_empty_invalidation_array_fails_at_parse(self) -> None:
        """INV-1: a claim that cannot state what would refute it is not a claim."""

        with self.assertRaises(ClaimError) as caught:
            parse_claim(wire(invalidationConditions=[]))
        self.assertIn("invalidationConditions", str(caught.exception))

    def test_a_missing_invalidation_key_fails_at_parse(self) -> None:
        payload = wire()
        del payload["invalidationConditions"]
        with self.assertRaises(ClaimError):
            parse_claim(payload)

    def test_at_least_one_condition_must_be_automatic(self) -> None:
        """C-12: staleness only a human can notice is staleness never noticed."""

        with self.assertRaises(ClaimError) as caught:
            parse_claim(wire(invalidationConditions=[
                {"condition": "a reviewer disagrees", "checkKind": "manual"},
                {"condition": "quarterly review", "checkKind": "scheduled"},
            ]))
        self.assertIn("automatic", str(caught.exception))

    def test_an_automatic_condition_must_name_its_check(self) -> None:
        with self.assertRaises(ClaimError):
            parse_claim(wire(invalidationConditions=[
                {"condition": "the oracle suite fails", "checkKind": "automatic"},
            ]))

    def test_a_valid_claim_round_trips_to_the_wire_shape(self) -> None:
        claim = parse_claim(wire())
        self.assertEqual(claim.to_wire(), wire())


class SubstrateDriftIsAutomaticStaleness(unittest.TestCase):
    def test_an_unchanged_substrate_leaves_the_claim_live(self) -> None:
        claim = parse_claim(wire())
        self.assertFalse(claim.is_stale_under(substrate_profile=DIGEST_D))

    def test_a_changed_substrate_makes_the_claim_stale(self) -> None:
        """INV-2: the model moved, so the measurement no longer describes it."""

        claim = parse_claim(wire())
        self.assertTrue(claim.is_stale_under(substrate_profile=DIGEST_A))

    def test_staleness_needs_no_human_review(self) -> None:
        """The determination is a pure function of two digests."""

        claim = parse_claim(wire())
        self.assertTrue(claim.is_stale_under(substrate_profile=DIGEST_A))
        self.assertEqual(claim.staleness_reason(substrate_profile=DIGEST_A),
                         "substrate_profile_changed")
        self.assertIsNone(claim.staleness_reason(substrate_profile=DIGEST_D))


class UncertaintyIsAnIntervalNotAPoint(unittest.TestCase):
    def test_an_interval_claim_keeps_both_bounds(self) -> None:
        claim = parse_claim(wire())
        self.assertEqual(claim.uncertainty.lower, 0.51)
        self.assertEqual(claim.uncertainty.upper, 0.73)

    def test_an_interval_with_inverted_bounds_fails(self) -> None:
        with self.assertRaises(ClaimError):
            parse_claim(wire(uncertainty={"kind": "interval", "lower": 0.9, "upper": 0.1}))

    def test_an_interval_missing_a_bound_fails(self) -> None:
        with self.assertRaises(ClaimError):
            parse_claim(wire(uncertainty={"kind": "interval", "lower": 0.5}))


class RecordedNotConsumed(unittest.TestCase):
    """`T4.11`'s argument: recording now costs nothing, retrofitting costs a corpus."""

    def test_the_three_fields_default_to_recorded_absence(self) -> None:
        claim = parse_claim(wire())
        self.assertEqual(claim.support_count, 0)
        self.assertIsNone(claim.last_corroborated_at)
        self.assertEqual(claim.protection_class, "none")

    def test_they_are_carried_when_supplied(self) -> None:
        claim = parse_claim(wire(), support_count=3,
                            last_corroborated_at="2026-08-16T00:00:00.000Z",
                            protection_class="load_bearing")
        self.assertEqual(claim.support_count, 3)
        self.assertEqual(claim.protection_class, "load_bearing")

    def test_they_do_not_leak_into_the_wire_shape(self) -> None:
        """`VG-04` sets additionalProperties:false; Joint owns the amendment.

        Until `S8-J-01` lands, emitting these would produce a claim the
        normative reader rejects. They are recorded on the domain type and
        withheld from the wire.
        """

        claim = parse_claim(wire(), support_count=3, protection_class="load_bearing")
        emitted = claim.to_wire()
        for field in ("supportCount", "lastCorroboratedAt", "protectionClass"):
            self.assertNotIn(field, emitted)

    def test_nothing_reads_them_to_decide_anything(self) -> None:
        """Recorded, not consumed: they must not move staleness or validity."""

        plain = parse_claim(wire())
        supported = parse_claim(wire(), support_count=99,
                                protection_class="load_bearing")
        self.assertEqual(plain.is_stale_under(substrate_profile=DIGEST_A),
                         supported.is_stale_under(substrate_profile=DIGEST_A))
        self.assertEqual(plain.to_wire(), supported.to_wire())


class ClaimIsPure(unittest.TestCase):
    def test_the_module_imports_nothing_outside_domain(self) -> None:
        """`domain/` is stdlib-only and depends on nothing else in the tree."""

        import ast
        from pathlib import Path

        source = Path(
            "vanguard/packages/domain/evidence/claim.py"
        ).read_text(encoding="utf-8")
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom) and node.module:
                self.assertNotIn("adapters", node.module)
                self.assertNotIn("runtime", node.module)
                self.assertNotIn("kernel", node.module)
                self.assertNotIn("agency", node.module)

    def test_a_claim_is_frozen(self) -> None:
        claim = parse_claim(wire())
        with self.assertRaises(Exception):
            claim.value = 0.9  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
