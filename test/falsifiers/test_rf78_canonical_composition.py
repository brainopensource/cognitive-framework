"""RF-78 (ADR-0088): both domains compose to one public canonical frozen value.

Red until A1 lands. The falsifier deliberately enters through `Runtime.compose`
— the *public* boundary — because the diagnosed defect is not that a `/2`
parser is missing (it exists, in `domain/artifacts/manifest.py`) but that the
public path cannot reach it: composition still enters through
`ManifestLoader.load_pack`, the legacy `HarnessManifest` value, and the global
coding-specific `DEFAULT_BINDINGS` table.

Probing the side path instead would pass today and prove nothing.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test.falsifiers.canonical_fixtures import (
    canonical_composition_type,
    code_pack,
    table_pack,
)
from vanguard.packages.runtime.compose import Runtime


class RF78CanonicalComposition(unittest.TestCase):
    """ADR-0088 Decision 1: one authored shape, one normalized value, one `D_H`."""

    def _compose(self, pack: Path, failures: list[str], label: str):
        """Compose through the public boundary, recording the architectural cause."""
        try:
            return Runtime.compose(pack, episode_id=f"ep-rf78-{label}")
        except Exception as exc:  # noqa: BLE001 - the cause is the evidence
            failures.append(
                f"{label}: authored mhf.manifest/2 does not compose through the "
                f"public Runtime.compose boundary: {type(exc).__name__}: {exc}")
            return None

    def test_code_and_table_v2_manifests_compose_to_one_frozen_value(self) -> None:
        failures: list[str] = []

        canonical = canonical_composition_type()
        if canonical is None:
            failures.append(
                "no canonical FrozenComposition value exists; FrozenHarness is still "
                "the composition identity rather than a facade over it (ADR-0088 §1.2, §1.5)")

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            code = self._compose(code_pack(base), failures, "code")
            table = self._compose(table_pack(base), failures, "table")

            for label, composed in (("code", code), ("table", table)):
                if composed is None:
                    continue
                digest = getattr(composed, "composition_digest", None)
                if not isinstance(digest, str) or not digest.startswith("sha256:"):
                    failures.append(f"{label}: composition carries no sha256 D_H")
                if canonical is not None:
                    frozen = getattr(composed, "frozen", composed)
                    if not isinstance(frozen, canonical):
                        failures.append(
                            f"{label}: public composition value is "
                            f"{type(frozen).__name__}, not the canonical FrozenComposition")

            if code is not None and table is not None:
                code_frozen = type(getattr(code, "frozen", code))
                table_frozen = type(getattr(table, "frozen", table))
                if code_frozen is not table_frozen:
                    failures.append(
                        "the two domains produce different composition value types "
                        f"({code_frozen.__name__} vs {table_frozen.__name__}); "
                        "one public path must produce one value")
                if code.composition_digest == table.composition_digest:
                    failures.append("distinct domains must not share one D_H")

        self.assertEqual(failures, [], "RF-78 remains red:\n- " + "\n- ".join(failures))

    def test_a_behaviour_affecting_change_moves_the_composition_digest(self) -> None:
        """`D_H` covers config, refs, and edges — not just the manifest name."""
        failures: list[str] = []

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            pack = code_pack(base)
            baseline = self._compose(pack, failures, "baseline")

            # A component's config bytes are behaviour-affecting authority.
            (pack / "context-policy.json").write_text(
                json.dumps({"maxTokens": 4000}), encoding="utf-8")
            mutated = self._compose(pack, failures, "mutated-config")

            if baseline is not None and mutated is not None:
                if baseline.composition_digest == mutated.composition_digest:
                    failures.append(
                        "a changed component config left D_H unchanged; the composition "
                        "digest does not cover every behaviour-affecting input")

        self.assertEqual(failures, [], "RF-78 remains red:\n- " + "\n- ".join(failures))

    def test_unconsumed_authority_fails_before_activation(self) -> None:
        """ADR-0088 §1.7: unknown authority denies at compose, and says so.

        The refusal must *name* the unconsumed field. Asserting only that some
        exception was raised would pass today for the wrong reason — the legacy
        parser rejects every `/2` manifest wholesale — and a falsifier that
        passes for the wrong reason is worse than one that fails.
        """
        failures: list[str] = []

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)

            # The clean pack must compose, or the refusal below is unattributable.
            self._compose(code_pack(base, "rf-authority-clean"), failures, "clean")

            pack = code_pack(base, "rf-authority-unknown")
            manifest = json.loads((pack / "manifest.json").read_text(encoding="utf-8"))
            manifest["components"]["toolkit"]["unknown_authority"] = "escalate"
            (pack / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            try:
                Runtime.compose(pack, episode_id="ep-rf78-unknown")
            except Exception as exc:  # noqa: BLE001 - the message is the evidence
                if "unknown_authority" not in str(exc):
                    failures.append(
                        "composition refused the unknown-authority pack without naming "
                        f"the unconsumed field: {type(exc).__name__}: {exc}")
            else:
                failures.append(
                    "an unconsumed authority field composed successfully; unknown "
                    "authority must fail before activation")

        self.assertEqual(failures, [], "RF-78 remains red:\n- " + "\n- ".join(failures))


if __name__ == "__main__":
    unittest.main()
