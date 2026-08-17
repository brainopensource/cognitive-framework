"""Tests for approval_policy manifest component resolution (S8-B-04)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency.manifests.loader import ManifestLoader

MANIFESTS_DIR = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency" / "manifests"


class TestApprovalPolicyManifest(unittest.TestCase):
    def test_two_packs_with_different_approval_policies_differ(self) -> None:
        """Two packs declaring different approval policies produce distinct loaded components (S8-B-04 DoD)."""
        loader = ManifestLoader(MANIFESTS_DIR)
        pack_default = loader.load_pack("vg-code-default")

        with tempfile.TemporaryDirectory() as tmpdir:
            pack_a = Path(tmpdir) / "vg-code-low"
            pack_b = Path(tmpdir) / "vg-code-strict"
            pack_a.mkdir()
            pack_b.mkdir()

            manifest_a = dict(pack_default.raw_manifest)
            manifest_a["harness"] = "vg-code-low"
            manifest_a["components"] = dict(manifest_a["components"])
            manifest_a["components"]["approval_policy"] = ["approval-policy.json"]

            manifest_b = dict(pack_default.raw_manifest)
            manifest_b["harness"] = "vg-code-strict"
            manifest_b["components"] = dict(manifest_b["components"])
            manifest_b["components"]["approval_policy"] = ["approval-policy.json"]

            (pack_a / "manifest.json").write_text(json.dumps(manifest_a), encoding="utf-8")
            (pack_a / "aliases.json").write_text(
                json.dumps(dict(pack_default.translator.to_canonical_map)), encoding="utf-8"
            )
            (pack_a / "approval-policy.json").write_text(
                json.dumps({"threshold": "low", "escalate_on": ["admin"]}), encoding="utf-8"
            )

            (pack_b / "manifest.json").write_text(json.dumps(manifest_b), encoding="utf-8")
            (pack_b / "aliases.json").write_text(
                json.dumps(dict(pack_default.translator.to_canonical_map)), encoding="utf-8"
            )
            (pack_b / "approval-policy.json").write_text(
                json.dumps({"threshold": "high", "escalate_on": ["admin", "patch.apply", "proc.exec"]}),
                encoding="utf-8",
            )

            loaded_a = loader.load_pack(pack_a, validate=False)
            loaded_b = loader.load_pack(pack_b, validate=False)

            policy_a = loaded_a.components_data.get("approval_policy", [{}])[0]
            policy_b = loaded_b.components_data.get("approval_policy", [{}])[0]

            self.assertNotEqual(policy_a, policy_b)
            self.assertEqual(policy_a["threshold"], "low")
            self.assertEqual(policy_b["threshold"], "high")
            self.assertEqual(len(policy_a["escalate_on"]), 1)
            self.assertEqual(len(policy_b["escalate_on"]), 3)


if __name__ == "__main__":
    unittest.main()
