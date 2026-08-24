"""RF-93 (ADR-0089, accepted 2026-08-24): activated components must be real."""

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

    def test_production_shaped_activation_materializes_and_closes_service(self) -> None:
        emitter = LedgerEmitter(
            InMemoryEventStore(),
            episode_id="rf93-ep",
            project_id="rf93",
            principal_id="root",
            harness_digest=COMPOSITION_DIGEST,
        )
        plan = self._plan()
        class Service:
            closed = False

            def close(self) -> None:
                self.closed = True

        service = Service()
        with activate(
            plan, emitter=emitter, run_id="rf93-run", principal="root",
            build=lambda _step: service,
        ) as session:
            cell = session["rf93-component"].cell
            self.assertIs(cell, service)
        self.assertTrue(service.closed)


if __name__ == "__main__":
    unittest.main()
