"""RF-93 (ADR-0089, accepted 2026-08-24): activated components must be real.

`activate()` (`activation.py:217-260`) defaults its `build` parameter to
`None`, so `cell = build(step) if build is not None else None` leaves every
component's `cell` at `None` unless a caller supplies `build`. The one
production caller, `Runtime.execute_harness` (`root.py:204-208`), calls
`activate(activation, emitter=..., run_id=..., principal=...)` without
`build`. So every component activated on the public path today proves it was
walked and torn down (`PluginDiscovered -> ... -> PluginRetired`), but not
that any declared service was materialized or used.

This test exercises `activate()` exactly as the production caller does — no
`build` — and characterizes today's defect directly (`cell is None`). It is
the W3D-06 acceptance marker in reverse: once `root.py`'s production caller
passes a real `build` factory, this assertion must be inverted to
`assertIsNotNone` (a materialized, non-`None` cell) and the test renamed to
prove the target invariant, not the defect.
"""

from __future__ import annotations

import unittest

from vanguard.packages.adapters.stores.event_store import InMemoryEventStore
from vanguard.packages.runtime.activation import ActivationPlan, ActivationStep, activate
from vanguard.packages.runtime.ledger_emitter import LedgerEmitter

COMPOSITION_DIGEST = "sha256:" + "0" * 64


class RF93PluginActivationMaterializesServicesFalsifier(unittest.TestCase):
    def _plan(self) -> ActivationPlan:
        step = ActivationStep(
            name="rf93-component",
            interface="mhf.model/1",
            isolation="in-process",
            ceiling=(),
            requires=(),
        )
        return ActivationPlan(COMPOSITION_DIGEST, (step,))

    def test_production_shaped_activation_leaves_cell_none_today(self) -> None:
        # This mirrors root.py:204-208's exact call shape: no `build` kwarg.
        emitter = LedgerEmitter(
            InMemoryEventStore(),
            episode_id="rf93-ep",
            project_id="rf93",
            principal_id="root",
            harness_digest=COMPOSITION_DIGEST,
        )
        plan = self._plan()
        with activate(plan, emitter=emitter, run_id="rf93-run", principal="root") as session:
            cell = session["rf93-component"].cell
            # RF-93 RED PROOF (falsifier): production-shaped activation currently leaves
            # cell is None because no build factory is passed.
            self.assertIsNone(
                cell,
                "RF-93 characterization: cell is None when no build factory is passed.",
            )


if __name__ == "__main__":
    unittest.main()
