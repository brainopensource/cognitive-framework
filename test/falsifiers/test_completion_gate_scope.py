"""Completion-gate scope falsifiers (W-092-2 application boundary).

The pack completion policy is wired only for the Coding Max preset harnesses.
``vg-code-default`` is deliberately ungated (frozen M-2 falsifiers compose bare
finishes through it).  These tests pin that scope so any change to it is an
explicit, visible diff -- never a silent drift of the completion contract.
"""

from __future__ import annotations

import inspect
import unittest

import vanguard.packages.runtime.session as session_module
from vanguard.packages.runtime.session import ADMISSION_GATED_HARNESSES


class TestCompletionGateScope(unittest.TestCase):
    def test_the_three_coding_max_presets_are_gated(self) -> None:
        self.assertEqual(
            ADMISSION_GATED_HARNESSES,
            {"vg-code-fast", "vg-code-balanced", "vg-code-max", "vg-code-max-v2"},
        )

    def test_default_harness_exemption_is_explicit_not_accidental(self) -> None:
        self.assertNotIn("vg-code-default", ADMISSION_GATED_HARNESSES)

    def test_gate_is_wired_through_the_named_constant(self) -> None:
        """The inline literal set must not reappear at the wiring site."""
        source = inspect.getsource(session_module)
        self.assertIn("ADMISSION_GATED_HARNESSES", source)
        self.assertNotIn(
            "harness.harness in {",
            source,
            "inline gate-scope set reintroduced; use ADMISSION_GATED_HARNESSES",
        )

    def test_gated_scope_matches_preset_manifests(self) -> None:
        from vanguard.packages.agency.manifests.loader import ManifestLoader

        packs = set(ManifestLoader().list_available_packs())
        missing = ADMISSION_GATED_HARNESSES - packs
        self.assertEqual(
            missing, set(),
            "gated harnesses must exist as registered manifests",
        )


if __name__ == "__main__":
    unittest.main()
