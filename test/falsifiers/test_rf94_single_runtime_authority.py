"""RF-94 (ADR-0089): production execution has one runtime authority."""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.authority_audit import audit_runtime_authority


class RF94SingleRuntimeAuthorityFalsifier(unittest.TestCase):
    def test_source_audit_has_no_competing_runtime_caller(self) -> None:
        trace = audit_runtime_authority()
        self.assertTrue(trace.passed, trace.violations)
        self.assertEqual(
            trace.public_boundary,
            "vanguard.packages.runtime.root.Runtime.run_composed",
        )


if __name__ == "__main__":
    unittest.main()
