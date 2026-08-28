"""B-O10-05: supersession advances a milestone; it never excuses one.

`check_evidence_acceptance.py` used to fail forever on M-4, M-5b and M-6,
because those bundles record `undeterminable` runs and no amount of correct
later work could change what an old bundle says. The prescribed repair is to
re-execute the evidence -- so the gate has to be able to *recognise* that
repair. It does, under two conditions that this module holds it to: the
successor must verify green under the independent verifier, and it must pin a
commit descended from the bundle it replaces.

Relax either one and the gate becomes a way to bury an inconvenient result,
which is the opposite of what it is for.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT / "tools" / "linters") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools" / "linters"))

from check_evidence_acceptance import _is_ancestor, superseding_bundle  # noqa: E402

EVIDENCE = _ROOT / "docs" / "03_execution" / "evidence"


def _bundles() -> list[Path]:
    return [p for p in sorted(EVIDENCE.glob("*.json"))
            if not p.name.endswith(".acceptance.json")]


class AncestryIsCheckedAgainstRealHistory(unittest.TestCase):
    def test_a_commit_is_not_its_own_ancestor(self) -> None:
        head = "HEAD"
        self.assertFalse(_is_ancestor(head, head))

    def test_an_unknown_commit_is_not_an_ancestor(self) -> None:
        self.assertFalse(_is_ancestor("0" * 40, "HEAD"))
        self.assertFalse(_is_ancestor("HEAD", "0" * 40))


class SupersessionRequiresAGreenDescendant(unittest.TestCase):
    def setUp(self) -> None:
        self.bundles = _bundles()
        self.superseded = {
            p.name: (superseding_bundle(p, self.bundles) or Path("-")).name
            for p in self.bundles
        }

    def test_an_open_milestone_is_not_superseded_by_anything(self) -> None:
        """M-4 and M-5b have no green successor, so they stay failures."""
        for name in self.superseded:
            if name.startswith(("M-4", "M-5b")):
                with self.subTest(bundle=name):
                    self.assertEqual(
                        self.superseded[name], "-",
                        f"{name} must not be excused while its milestone is open")

    def test_a_bundle_never_supersedes_itself(self) -> None:
        for name, successor in self.superseded.items():
            with self.subTest(bundle=name):
                self.assertNotEqual(name, successor)

    def test_a_successor_must_carry_the_same_claim(self) -> None:
        by_name = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in self.bundles}
        for name, successor in self.superseded.items():
            if successor == "-":
                continue
            with self.subTest(bundle=name):
                self.assertEqual(by_name[name]["claim"], by_name[successor]["claim"])

    def test_a_non_green_successor_does_not_supersede(self) -> None:
        """The M-6 chain is only excused because order10 actually verifies."""
        undeterminable = EVIDENCE / "M-6-canonical-recursion.json"
        if not undeterminable.is_file():
            self.skipTest("historical M-6 bundle is absent")
        others = [p for p in self.bundles
                  if p.name not in {"M-6-canonical-recursion-order10.json"}]
        self.assertIsNone(
            superseding_bundle(undeterminable, others),
            "without the green successor, nothing may excuse this bundle",
        )


if __name__ == "__main__":
    unittest.main()
