"""A1 support contracts for the canonical composition boundary.

These tests intentionally avoid runtime/manifest implementation details owned by
Dev A. They pin the public and domain-level invariants needed by RF-78/RF-79.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test.falsifiers.canonical_fixtures import (
    authored_twin,
    code_pack,
    legacy_twin,
)
from vanguard.packages.domain.artifacts.manifest import (
    FrozenComposition,
    ManifestError,
    canonical_from_legacy,
    canonical_from_v2,
)
from vanguard.packages.runtime.compose import Runtime


class A1CanonicalCompositionSupportTests(unittest.TestCase):
    """Small independent contracts for the A1 freeze boundary."""

    def test_public_compose_exposes_one_frozen_value_and_stable_dh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = code_pack(Path(tmp))
            first = Runtime.compose(pack, episode_id="episode-a")
            second = Runtime.compose(pack, episode_id="episode-b")

        self.assertIsInstance(first.frozen, FrozenComposition)
        self.assertIsInstance(second.frozen, FrozenComposition)
        self.assertEqual(first.composition_digest, second.composition_digest)

    def test_legacy_and_authored_dialects_share_normalized_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            legacy_path = legacy_twin(base / "legacy", pack_id="rf-twin")
            authored_path = authored_twin(base / "authored", pack_id="rf-twin")
            legacy_raw = json.loads((legacy_path / "manifest.json").read_text())
            authored_raw = json.loads((authored_path / "manifest.json").read_text())

        legacy = canonical_from_legacy(legacy_raw)
        authored = canonical_from_v2(authored_raw)
        self.assertEqual(legacy.identity_preimage(), authored.identity_preimage())

    def test_agent_spawn_is_refused_before_freeze(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pack = code_pack(Path(tmp))
            manifest_path = pack / "manifest.json"
            raw = json.loads(manifest_path.read_text())
            spawn_selector = {"kind": "generic", "uriPattern": "agent://spawn/*"}
            raw["capabilities"].append({
                "verb": "agent.spawn",
                "sink": "privileged",
                "risk": "high",
                "selector": spawn_selector,
            })
            raw["ceiling"].append(spawn_selector)

        with self.assertRaises(ManifestError) as ctx:
            canonical_from_v2(raw)
        self.assertIn("agent.spawn", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
