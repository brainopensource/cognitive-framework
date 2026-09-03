"""TSK-LED-005 / S060-B-03: privileged dispatch emits grant and budget kinds.

Emits happen at S12 (after S11 release) so K-06 still holds.
REQ-TRUST-001.
"""

from __future__ import annotations

import unittest

from vanguard.packages.kernel import FailurePath

from . import fakes


class GrantAndBudgetEvents(unittest.TestCase):
    def test_privileged_happy_path_emits_grant_and_budget_kinds(self) -> None:
        harness = fakes.build()
        result = harness.kernel.dispatch(
            fakes.request(), requested_scope=fakes.child_scope(),
            reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.OK, result.detail)
        kinds = [event.kind for event in harness.sink.events]
        self.assertIn("CapabilityGranted", kinds)
        self.assertIn("BudgetReserved", kinds)
        self.assertIn("BudgetCommitted", kinds)
        self.assertIn("EffectCompleted", kinds)
        self.assertLess(harness.trace.index("release"),
                        min(i for i, step in enumerate(harness.trace)
                            if step.startswith("emit:")))
