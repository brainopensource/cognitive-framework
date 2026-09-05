"""Completion-gate scope falsifiers (T-04 / T-05 successor baseline).

Successor to the frozen W-092-2 assertion, which pinned the shape this file
now forbids: a name allowlist (``ADMISSION_GATED_HARNESSES``) that nothing
read, beside a name exemption (``ADMISSION_GATE_EXEMPT``) that bought
``vg-code-default`` and ``vg-code-lex`` a permanent product-default bypass.

The successor contract is capability-derived and has exactly one decider:
``admission_required``.  A preset is gated because it declares ``patch.apply``,
never because of what it is called, so the scope cannot drift as presets are
added and no name set can disagree with the predicate.
"""

from __future__ import annotations

import inspect
import unittest
from dataclasses import dataclass

import vanguard.packages.runtime.session as session_module
from vanguard.packages.runtime.root import Runtime
from vanguard.packages.runtime.session import admission_required


@dataclass(frozen=True)
class _Harness:
    """The duck type ``admission_required`` reads: a name and its verbs."""

    harness: str
    verbs: tuple[str, ...]


class TestCompletionGateScope(unittest.TestCase):
    def test_the_product_default_is_no_longer_exempt(self) -> None:
        """T-04. The frozen exemption is gone, not renamed or narrowed."""
        self.assertTrue(
            admission_required(
                _Harness("vg-code-default", ("fs.read", "patch.apply", "proc.exec"))))
        self.assertTrue(
            admission_required(
                _Harness("vg-code-lex", ("fs.read", "patch.apply", "proc.exec"))))

    def test_no_exemption_or_allowlist_constant_survives(self) -> None:
        """T-05. Two name sets could disagree with the predicate; both are gone."""
        self.assertFalse(hasattr(session_module, "ADMISSION_GATE_EXEMPT"))
        self.assertFalse(hasattr(session_module, "ADMISSION_GATED_HARNESSES"))

    def test_gating_is_decided_by_declared_capability_alone(self) -> None:
        """A preset nobody has heard of is gated by what it declares."""
        self.assertTrue(
            admission_required(_Harness("vg-code-invented-tomorrow", ("patch.apply",))))
        self.assertFalse(
            admission_required(_Harness("vg-research-minimal", ("fs.read", "fs.search"))))

    def test_the_name_cannot_change_the_verdict(self) -> None:
        """The gate is a function of the verbs; renaming a preset moves nothing."""
        verbs = ("fs.read", "patch.apply")
        self.assertEqual(
            admission_required(_Harness("vg-code-default", verbs)),
            admission_required(_Harness("anything-at-all", verbs)),
        )

    def test_one_function_decides_gating(self) -> None:
        """No inline set at the wiring site, and no second decider beside it."""
        source = inspect.getsource(session_module)
        self.assertNotIn(
            "harness.harness in {",
            source,
            "inline gate-scope set reintroduced; admission_required is the one decider",
        )
        self.assertEqual(source.count("def admission_required"), 1)

    def test_the_composed_product_presets_are_gated(self) -> None:
        """Read through real composition, not a hand-maintained name list."""
        for preset in ("vg-code-default", "vg-code-lex", "vg-code-max"):
            with self.subTest(preset=preset):
                harness = Runtime.compose(preset, episode_id="ep-gate-scope")
                self.assertIn("patch.apply", harness.verbs)
                self.assertTrue(admission_required(harness))

    def test_a_composed_read_only_preset_is_not_gated(self) -> None:
        """Gating follows the declared capability down as well as up."""
        harness = Runtime.compose("vg-research-minimal", episode_id="ep-gate-scope")
        self.assertNotIn("patch.apply", harness.verbs)
        self.assertFalse(admission_required(harness))


if __name__ == "__main__":
    unittest.main()
