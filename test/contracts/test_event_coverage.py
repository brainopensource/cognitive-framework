"""E-COV: every event kind the production `LedgerEmitter` can legally write
is present in the canonical event catalog (SPEC §1.2, ADR-0076 §6).

M-2 (2026-08-20, Tech Lead): `domain/ledger/events.EVENT_KINDS` had drifted
from `runtime/ledger_emitter.PRIVILEGED_KIND_OWNERS` and the kinds real
call sites actually emit -- `VerdictRecorded`, `EffectFailed`,
`BudgetExhausted`, `CapabilityAttenuated`, `TurnStarted` and others were
legal for `LedgerEmitter` to write but absent from the catalog, so
`reduce_event` silently misfiled them into `unknown_events`. This is not a
brittle fixed-count check (a count regresses the instant a legitimate kind
is added) -- it asserts the one direction that must always hold: everything
production can actually or legally write is a *subset* of the catalog.
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_TOOLS = str(ROOT / "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from check_event_coverage import production_emittable_kinds  # noqa: E402

from vanguard.packages.domain.ledger.events import EVENT_KINDS  # noqa: E402
from vanguard.packages.runtime.ledger_emitter import PRIVILEGED_KIND_OWNERS  # noqa: E402


class ProductionEmittableKindsAreCatalogued(unittest.TestCase):
    """Production-emittable kinds ⊆ `EVENT_KINDS` (subset, never equality)."""

    def test_every_privileged_owner_kind_is_catalogued(self) -> None:
        missing = sorted(set(PRIVILEGED_KIND_OWNERS) - EVENT_KINDS)
        self.assertEqual(missing, [], f"writer-authorised kinds absent from EVENT_KINDS: {missing}")

    def test_every_production_emittable_kind_is_catalogued(self) -> None:
        missing = sorted(production_emittable_kinds() - EVENT_KINDS)
        self.assertEqual(missing, [], f"production-emittable kinds absent from EVENT_KINDS: {missing}")

    def test_m2_named_kinds_are_catalogued(self) -> None:
        # The five kinds the Tech Lead's M-2 blocker named as missing.
        for kind in (
            "VerdictRecorded",
            "EffectFailed",
            "BudgetExhausted",
            "CapabilityAttenuated",
            "TurnStarted",
        ):
            self.assertIn(kind, EVENT_KINDS, f"{kind} must be in the canonical catalog (M-2)")

    def test_wave3_plugin_lifecycle_kinds_are_catalogued(self) -> None:
        # Wave 3 depends on this vocabulary already existing (M-2 blocker note).
        for kind in (
            "PluginResolved",
            "PluginActivated",
            "PluginQuiesced",
            "PluginRetired",
            "PluginFaulted",
        ):
            self.assertIn(kind, EVENT_KINDS)

    def test_kind_never_legitimately_writable_stays_out(self) -> None:
        # The CLI streaming wire protocol (ADR-0062, `runtime/service/`) is a
        # distinct bounded context; its kinds must never enter the ledger
        # catalog (test/kernel/test_event_kinds_writer.py holds the other
        # half of this guarantee at the writer/parse boundary).
        self.assertNotIn("RunFailed", EVENT_KINDS)

    def test_check_event_coverage_tool_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_event_coverage.py")],
            cwd=ROOT, text=True, capture_output=True, check=False,
            env={**os.environ},
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
