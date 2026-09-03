"""Shared substitution contract for SandboxRunner.

Owning contract: REQ-PORT-005 / TEST-PORT-005, ICD §4, K-43/K-44/K-46.
"""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.sandbox import FakeSandboxRunner
from vanguard.packages.ports.sandbox import SandboxRunner, publication_decision


def _fake() -> SandboxRunner:
    return FakeSandboxRunner()


class SandboxPortContract(unittest.TestCase):
    def test_fake_is_visibly_non_contained_and_unverified(self) -> None:
        result = _fake().execute(("echo", "ok"))
        self.assertTrue(result.ok)
        self.assertIsNotNone(result.value)
        report = result.value.containment
        self.assertFalse(report.contained)
        self.assertFalse(report.verified)
        self.assertIn("non-contained", report.visibility_mark)

    def test_unverified_report_blocks_publication(self) -> None:
        result = _fake().execute(("echo", "ok"))
        decision = publication_decision(result.value.containment)
        self.assertFalse(decision.ok)
        self.assertIsNotNone(decision.error)
        self.assertEqual(decision.error.kind, "denied")
        self.assertIn("unverified", decision.error.message.lower())
        self.assertIn("publication", decision.error.message.lower())


if __name__ == "__main__":
    unittest.main()
