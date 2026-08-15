"""`REQ-SCHEMA-003` / `S1-D1-003` — the ResourceSelector inclusion algebra.

Statement under test: `ResourceSelector` uses VG-04's per-kind total inclusion
relation, denies cross-kind and undefined comparisons, and satisfies
reflexivity, transitivity and antisymmetry up to canonical equality. Margin:
zero unknown-as-allow outcomes.

Evidence produced:

* the inclusion vectors, including the must-fail cross-kind and undefined
  pairs, replayed through both readers (`SC-7`, `CT-52`);
* valid and invalid selector instances checked against the normative schema
  as well as the readers (`CT-01`);
* seeded property runs over a generated selector population for reflexivity,
  transitivity, antisymmetry and totality, since a finite vector set cannot
  establish a relation's algebraic shape (`vectors/README.md`).
"""

from __future__ import annotations

import itertools
import json
import random
import unittest
from pathlib import Path

from vanguard.packages.domain import (
    SELECTOR_KINDS,
    SelectorError,
    canonicalise_selector,
    decide,
    includes,
    parse_selector,
)

from .readers import ts_reader
from .schema_subset import SchemaSet, SchemaViolation

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas" / "v4"
VECTORS = SCHEMAS / "vectors" / "resource-selector"
SCHEMA_FILE = "resource-selector.schema.json"
SCHEMA_SET = SchemaSet(SCHEMAS)


def _instances(directory: str) -> list[tuple[str, object, dict]]:
    cases = []
    for path in sorted((VECTORS / directory).glob("*.json")):
        if path.name.endswith(".expect.json"):
            continue
        expect_path = path.with_name(f"{path.stem}.expect.json")
        expect = json.loads(expect_path.read_text()) if expect_path.exists() else {}
        cases.append((path.stem, json.loads(path.read_text(encoding="utf-8")), expect))
    return cases


VALID = _instances("valid")
INVALID = _instances("invalid")
INCLUSION = [
    (path.stem, json.loads(path.read_text(encoding="utf-8")))
    for path in sorted((VECTORS / "inclusion").glob("*.json"))
]


class SelectorInstances(unittest.TestCase):
    """`REQ-SCHEMA-003` — parsing, in both readers and against the schema."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ts_valid = ts_reader({"selectorParse": [value for _, value, _ in VALID]})
        cls.ts_invalid = ts_reader({"selectorParse": [value for _, value, _ in INVALID]})

    def test_every_kind_has_a_valid_vector(self) -> None:
        covered = {value["kind"] for _, value, _ in VALID}
        self.assertEqual(covered, set(SELECTOR_KINDS))

    def test_readers_agree_on_the_canonical_form_of_every_valid_vector(self) -> None:
        for index, (case, value, _) in enumerate(VALID):
            with self.subTest(vector=case):
                result = self.ts_valid["selectorParse"][index]
                self.assertTrue(result["ok"], result)
                self.assertEqual(canonicalise_selector(value), result["canonical"])

    def test_normative_schema_accepts_every_valid_vector(self) -> None:
        for case, value, _ in VALID:
            with self.subTest(vector=case):
                SCHEMA_SET.validate(value, SCHEMA_FILE)

    def test_both_readers_reject_every_invalid_vector(self) -> None:
        for index, (case, value, _) in enumerate(INVALID):
            with self.subTest(vector=case):
                with self.assertRaises(SelectorError):
                    parse_selector(value)
                self.assertFalse(self.ts_invalid["selectorParse"][index]["ok"], case)

    def test_reader_reports_the_expected_failure_code(self) -> None:
        for case, value, expect in INVALID:
            with self.subTest(vector=case):
                with self.assertRaises(SelectorError) as caught:
                    parse_selector(value)
                self.assertEqual(caught.exception.code, expect["expectedKeyword"])

    def test_schema_rejects_the_structural_cases_and_admits_the_semantic_ones(self) -> None:
        """A `schemaAccepts` vector fails only in the semantic layer.

        JSON Schema cannot say "and this path contains no glob" or "and this
        origin carries no path". Recording which vectors the schema accepts
        keeps the two layers honest about who enforces what (`SEMANTICS.md`).
        """
        for case, value, expect in INVALID:
            with self.subTest(vector=case):
                if expect.get("schemaAccepts"):
                    SCHEMA_SET.validate(value, SCHEMA_FILE)
                else:
                    with self.assertRaises(SchemaViolation):
                        SCHEMA_SET.validate(value, SCHEMA_FILE)

    def test_both_readers_expose_the_same_kinds(self) -> None:
        self.assertEqual(list(SELECTOR_KINDS), self.ts_valid["selectorKinds"])


class InclusionVectors(unittest.TestCase):
    """`REQ-SCHEMA-003` — the relation, decision by decision."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ts = ts_reader({
            "selectorDecide": [[case["parent"], case["child"]] for _, case in INCLUSION],
        })

    def test_python_reader_matches_every_expected_decision(self) -> None:
        for case, vector in INCLUSION:
            with self.subTest(vector=case):
                decision = decide(vector["parent"], vector["child"])
                self.assertEqual(decision.included, vector["expected"]["included"])
                self.assertEqual(decision.reason, vector["expected"]["reason"])

    def test_typescript_reader_matches_every_expected_decision(self) -> None:
        for index, (case, vector) in enumerate(INCLUSION):
            with self.subTest(vector=case):
                self.assertEqual(self.ts["selectorDecide"][index], vector["expected"])

    def test_no_vector_allows_an_undecided_pair(self) -> None:
        """The margin: zero unknown-as-allow outcomes (`CT-52`)."""
        for case, vector in INCLUSION:
            with self.subTest(vector=case):
                if vector["expected"]["reason"] in {"cross_kind", "unparsable",
                                                    "undefined_relation"}:
                    self.assertFalse(vector["expected"]["included"])

    def test_must_fail_families_are_all_represented(self) -> None:
        reasons = {vector["expected"]["reason"] for _, vector in INCLUSION}
        for required in ("included", "not_included", "cross_kind", "unparsable"):
            self.assertIn(required, reasons)


# --------------------------------------------------------------------------
# Property tests. The generator is seeded, so a counterexample names a
# reproducible population rather than a run.
# --------------------------------------------------------------------------

SEED = 20260815

HOSTS = ["example.com", "a.example.com", "b.example.com", "a.b.example.com",
         "*.example.com", "*.b.example.com", "münchen.example", "xn--mnchen-3ya.example"]
PATHS = ["/w", "/w/src", "/w/src/lib", "/w/srcold", "/w/docs", "/w/./src", "/w/src/"]
REFS = ["main", "refs/heads/main", "refs/heads/dev", "refs/tags/v1", "HEAD"]
RANGES = ["*", "0..10", "0..100", "5..10", "10..100", "50..150"]
ORIGINS = ["https://a.example.com", "https://a.example.com:443", "https://a.example.com:8443",
           "http://a.example.com", "https://example.com"]
SECRETS = ["vault://a", "vault://b", "vault://prod/db"]
PATTERNS = ["vg://tool/echo", "vg://tool/*", "vg://tool/echo/1"]


def _population(rng: random.Random, size: int) -> list[dict]:
    """A population dense in *near misses*, which is where a relation breaks."""
    out: list[dict] = []
    while len(out) < size:
        kind = rng.choice(SELECTOR_KINDS)
        if kind == "fs":
            candidate = {"kind": "fs", "root": rng.choice(["/w", "/w/", "/other"]),
                         "paths": rng.sample(PATHS, rng.randint(1, 3))}
        elif kind == "network":
            candidate = {"kind": "network", "hosts": rng.sample(HOSTS, rng.randint(1, 3)),
                         "ports": rng.sample([80, 443, 8443], rng.randint(0, 3))}
        elif kind == "secret":
            candidate = {"kind": "secret", "refs": rng.sample(SECRETS, rng.randint(1, 3)),
                         "discloseToModel": False}
        elif kind == "git":
            candidate = {"kind": "git", "repo": rng.choice(["git://h/r.git", "git://h/o.git"]),
                         "refs": rng.sample(REFS, rng.randint(1, 3))}
        elif kind == "table":
            candidate = {"kind": "table", "table": rng.choice(["table://a", "table://b"])}
            if rng.random() < 0.8:
                candidate["ranges"] = rng.sample(RANGES, rng.randint(1, 3))
        elif kind == "browser":
            candidate = {"kind": "browser", "origin": rng.choice(ORIGINS)}
            if rng.random() < 0.5:
                candidate["accountRef"] = rng.choice(["acct-1", "acct-2"])
        else:
            candidate = {"kind": "generic", "uriPattern": rng.choice(PATTERNS)}
        try:
            parse_selector(candidate)
        except SelectorError:
            continue
        out.append(candidate)
    return out


class RelationProperties(unittest.TestCase):
    """The algebra `REQ-SCHEMA-003` names, over a generated population."""

    POPULATION = 120

    @classmethod
    def setUpClass(cls) -> None:
        cls.values = _population(random.Random(SEED), cls.POPULATION)
        cls.canonical = [canonicalise_selector(value) for value in cls.values]
        # The relation over the population, computed once. The algebraic
        # properties below are quantified over triples, and asking the reader
        # 10^6 times would test the machine rather than the algebra.
        cls.relation = [[includes(a, b) for b in cls.values] for a in cls.values]

    def test_reflexive(self) -> None:
        for value in self.values:
            with self.subTest(selector=value):
                self.assertTrue(includes(value, value), "includes(x, x) must hold")

    def test_reflexive_on_the_declared_vectors_too(self) -> None:
        for case, value, _ in VALID:
            with self.subTest(vector=case):
                self.assertTrue(includes(value, value))

    def test_transitive(self) -> None:
        size = len(self.values)
        for i, j, k in itertools.permutations(range(size), 3):
            if self.relation[i][j] and self.relation[j][k]:
                with self.subTest(a=self.values[i], b=self.values[j], c=self.values[k]):
                    self.assertTrue(self.relation[i][k], "transitivity broken")

    def test_antisymmetric_up_to_canonical_equality(self) -> None:
        for i, j in itertools.permutations(range(len(self.values)), 2):
            if self.relation[i][j] and self.relation[j][i]:
                with self.subTest(a=self.values[i], b=self.values[j]):
                    self.assertEqual(self.canonical[i], self.canonical[j],
                                     "mutual inclusion without canonical equality")

    def test_canonical_equality_implies_mutual_inclusion(self) -> None:
        """The converse. Together with antisymmetry this makes the canonical
        form the identity of an authority, which is what a grant compares."""
        for i, j in itertools.permutations(range(len(self.values)), 2):
            if self.canonical[i] == self.canonical[j]:
                with self.subTest(a=self.values[i], b=self.values[j]):
                    self.assertTrue(self.relation[i][j] and self.relation[j][i])

    def test_canonicalisation_is_idempotent(self) -> None:
        for value in self.values:
            with self.subTest(selector=value):
                once = parse_selector(value)
                self.assertEqual(canonicalise_selector(once), canonicalise_selector(value))

    def test_total_and_fail_closed_on_every_pair(self) -> None:
        """`CT-52`: total on the defined pairs, denying everything else."""
        junk = [None, 0, "fs", [], {}, {"kind": "fs"}, {"kind": "process"},
                {"kind": "fs", "root": "/w", "paths": []},
                {"kind": "generic", "uriPattern": None}]
        for a in self.values + junk:
            for b in self.values + junk:
                with self.subTest(a=a, b=b):
                    decision = decide(a, b)
                    self.assertIsInstance(decision.included, bool)
                    if a in junk or b in junk:
                        self.assertFalse(decision.included,
                                         "an undecidable pair was allowed")

    def test_cross_kind_is_always_denied(self) -> None:
        for a, b in itertools.permutations(self.values, 2):
            if a["kind"] != b["kind"]:
                with self.subTest(a=a, b=b):
                    decision = decide(a, b)
                    self.assertFalse(decision.included)
                    self.assertEqual(decision.reason, "cross_kind")

    def test_readers_agree_on_the_whole_population(self) -> None:
        """`SC-7` over the generated pairs, not only the vectors."""
        rng = random.Random(SEED + 2)
        pairs = [(rng.choice(self.values), rng.choice(self.values)) for _ in range(400)]
        ts = ts_reader({"selectorDecide": [list(pair) for pair in pairs]})["selectorDecide"]
        for index, (parent, child) in enumerate(pairs):
            with self.subTest(parent=parent, child=child):
                decision = decide(parent, child)
                self.assertEqual(
                    {"included": decision.included, "reason": decision.reason}, ts[index])


class AttenuationSemantics(unittest.TestCase):
    """The rules `CT-24`..`CT-28` depend on, stated as tests."""

    def test_narrowing_is_never_silent(self) -> None:
        """`CT-25`: an over-broad request is denied whole, not intersected."""
        parent = {"kind": "fs", "root": "/w", "paths": ["/w/src"]}
        child = {"kind": "fs", "root": "/w", "paths": ["/w/src/a.ts", "/w/secrets"]}
        decision = decide(parent, child)
        self.assertFalse(decision.included)
        self.assertEqual(decision.reason, "not_included")
        # And the grantable part is still expressible, so the caller can record
        # both what was requested and what was grantable (`CT-24`).
        self.assertTrue(includes(parent, {"kind": "fs", "root": "/w", "paths": ["/w/src/a.ts"]}))

    def test_a_wildcard_parent_never_admits_a_wildcard_child(self) -> None:
        parent = {"kind": "network", "hosts": ["*.example.com"], "ports": [443]}
        for child_host in ("*.a.example.com", "*.example.com.evil.com"):
            with self.subTest(host=child_host):
                child = {"kind": "network", "hosts": [child_host], "ports": [443]}
                self.assertFalse(includes(parent, child))

    def test_secret_disclosure_flag_is_a_literal(self) -> None:
        """04 §5.2: there is no code path that flips this flag."""
        with self.assertRaises(SelectorError):
            parse_selector({"kind": "secret", "refs": ["vault://a"], "discloseToModel": True})
        parsed = parse_selector({"kind": "secret", "refs": ["vault://a"],
                                 "discloseToModel": False})
        self.assertIs(parsed["discloseToModel"], False)

    def test_generic_containment_is_literal_equality_only(self) -> None:
        """Approximating pattern containment silently widens authority."""
        broad = {"kind": "generic", "uriPattern": "vg://tool/*"}
        narrow = {"kind": "generic", "uriPattern": "vg://tool/echo"}
        self.assertFalse(includes(broad, narrow))
        self.assertFalse(includes(narrow, broad))
        self.assertTrue(includes(broad, dict(broad)))

    def test_origin_has_no_subdomain_or_path_containment(self) -> None:
        parent = {"kind": "browser", "origin": "https://example.com"}
        self.assertFalse(includes(parent, {"kind": "browser", "origin": "https://a.example.com"}))
        with self.assertRaises(SelectorError):
            parse_selector({"kind": "browser", "origin": "https://example.com/app"})

    def test_path_normalisation_is_not_authority(self) -> None:
        """`D-2`: two spellings of one path are the same path, and no more."""
        canonical = canonicalise_selector({"kind": "fs", "root": "/w", "paths": ["/w/src"]})
        for spelling in ("/w/src/", "/w/./src", "/w/x/../src", "\\w\\src"):
            with self.subTest(path=spelling):
                self.assertEqual(
                    canonicalise_selector({"kind": "fs", "root": "/w", "paths": [spelling]}),
                    canonical)

    def test_a_glob_is_never_grantable(self) -> None:
        """04 §5.3.1: expand at issuance, or the grant means something unknown."""
        for path in ("/w/*", "/w/**/a.ts", "/w/[ab]", "/w/{a,b}", "/w/a?"):
            with self.subTest(path=path):
                with self.assertRaises(SelectorError):
                    parse_selector({"kind": "fs", "root": "/w", "paths": [path]})
