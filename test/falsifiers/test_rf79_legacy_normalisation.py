"""RF-79 (ADR-0088): legacy input normalizes, and no legacy value crosses over.

Two claims, both red until A1 lands:

1. A supported `mhf.harness/1` pack and the authored `mhf.manifest/2` statement
   of the *same* facts converge on one normalized value and one `D_H`. The
   fixtures are a twin pair over byte-identical component files, so a digest
   difference can only come from dialect, which is exactly what normalization
   must erase.
2. No legacy value survives past the compatibility boundary. Today
   `Runtime.compose` returns a `FrozenHarness` built directly from
   `HarnessManifest`: the legacy value *is* the composition identity, which is
   the defect ADR-0088 §1.1 and §1.5 name.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from test.falsifiers.canonical_fixtures import (
    TWIN_FACTS,
    authored_twin,
    canonical_composition_type,
    legacy_twin,
)
from vanguard.packages.runtime.compose import Runtime


class RF79LegacyNormalisation(unittest.TestCase):
    """The compatibility reader is ingress only, never an execution authority."""

    def _compose(self, pack: Path, failures: list[str], label: str):
        try:
            return Runtime.compose(pack, episode_id=f"ep-rf79-{label}")
        except Exception as exc:  # noqa: BLE001 - the cause is the evidence
            failures.append(f"{label}: does not compose through the public "
                            f"boundary: {type(exc).__name__}: {exc}")
            return None

    def test_legacy_and_authored_input_converge_on_one_digest(self) -> None:
        failures: list[str] = []

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            legacy = self._compose(legacy_twin(base), failures, "legacy")
            authored = self._compose(authored_twin(base), failures, "authored")

            if legacy is not None and authored is not None:
                if legacy.composition_digest != authored.composition_digest:
                    failures.append(
                        "the same facts stated in two dialects produced two D_H values "
                        f"({legacy.composition_digest} vs {authored.composition_digest}); "
                        "compatibility ingress must normalize before identity")

                for name, expected in TWIN_FACTS.items():
                    for label, composed in (("legacy", legacy), ("authored", authored)):
                        observed = self._facts(composed, name)
                        if observed != expected:
                            failures.append(
                                f"{label}: normalized {name} is {observed!r}, "
                                f"expected {expected!r}")

        self.assertEqual(failures, [], "RF-79 remains red:\n- " + "\n- ".join(failures))

    @staticmethod
    def _facts(composed: object, name: str) -> object:
        """Read one normalized fact off whatever the public value turns out to be."""
        frozen = getattr(composed, "frozen", composed)
        if name == "capabilities":
            rows = getattr(frozen, "capabilities", ())
            return tuple(sorted((getattr(row, "verb", None), getattr(row, "sink", None),
                                 getattr(row, "risk", None)) for row in rows))
        return tuple(getattr(frozen, name, ()))

    def test_no_legacy_value_is_the_composition_identity(self) -> None:
        failures: list[str] = []

        canonical = canonical_composition_type()
        if canonical is None:
            failures.append(
                "FrozenComposition does not exist, so FrozenHarness cannot be the "
                "facade over it that ADR-0088 §1.5 requires")

        with tempfile.TemporaryDirectory() as tmp:
            composed = self._compose(legacy_twin(Path(tmp)), failures, "legacy")

            if composed is not None:
                frozen = getattr(composed, "frozen", composed)
                if canonical is not None and not isinstance(frozen, canonical):
                    failures.append(
                        f"the composed value is {type(frozen).__name__}; a legacy value "
                        "crossed the compatibility boundary as the execution identity")

                # A facade may wrap the canonical value; it may not *be* the value.
                if canonical is not None and type(frozen).__name__ == "FrozenHarness":
                    inner = getattr(frozen, "composition", None)
                    if not isinstance(inner, canonical):
                        failures.append(
                            "FrozenHarness does not wrap a FrozenComposition; it is a "
                            "second composition identity, not a facade")

        self.assertEqual(failures, [], "RF-79 remains red:\n- " + "\n- ".join(failures))


if __name__ == "__main__":
    unittest.main()
