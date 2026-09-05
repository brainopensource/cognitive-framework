"""Metamorphic policy-digest test (S7-B-03, 005 H4).

Proves the decorative-field defect: today context_policy is read into the
manifest composition digest, but ignored by ContextCompiler (which hardcodes
result_eviction). Mutating context-policy.json does not change any observable
behaviour yet.

This test is expected to fail in Sprint 7 and will turn green in Sprint 8 when
S8-B-02 (CompactionStrategy protocol and registry) connects context_policy
to real compiler execution.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency.context.compiler import ContextCompiler
from vanguard.packages.agency.context.layers import Fragment
from vanguard.packages.agency.manifests.loader import ManifestLoader

MANIFESTS_DIR = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "agency" / "manifests"


class TestManifestMetamorphicPolicy(unittest.TestCase):
    def test_context_policy_mutation_changes_observable_compaction(self) -> None:
        """Mutating context_policy from recency-window to a different strategy must change observable context (S8-B-02)."""
        loader = ManifestLoader(MANIFESTS_DIR)
        pack_default = loader.load_pack("vg-code-default")

        # Create a mutated pack with a restricted context policy
        with tempfile.TemporaryDirectory() as tmpdir:
            pack_dir = Path(tmpdir) / "vg-code-mutated"
            pack_dir.mkdir()
            manifest_data = dict(pack_default.raw_manifest)
            manifest_data["harness"] = "vg-code-mutated"
            manifest_data["components"] = dict(manifest_data["components"])
            manifest_data["components"]["context_policy"] = ["context-policy.json"]
            (pack_dir / "manifest.json").write_text(json.dumps(manifest_data), encoding="utf-8")
            (pack_dir / "aliases.json").write_text(
                json.dumps(dict(pack_default.translator.to_canonical_map)), encoding="utf-8"
            )
            (pack_dir / "context-policy.json").write_text(
                json.dumps({"kind": "recency-window", "maxItems": 1}), encoding="utf-8"
            )

            pack_mutated = loader.load_pack(pack_dir, validate=False)

            dialogue = [
                Fragment(source="agent", label="turn-1-proposal", text="fs.read a.txt"),
                Fragment(source="env", label="turn-1-obs", text="content of a.txt " * 50),
                Fragment(source="agent", label="turn-2-proposal", text="fs.read b.txt"),
                Fragment(source="env", label="turn-2-obs", text="content of b.txt " * 50),
                Fragment(source="agent", label="turn-3-proposal", text="fs.read c.txt"),
                Fragment(source="env", label="turn-3-obs", text="content of c.txt " * 50),
            ]

            context_policy_default = pack_default.components_data.get("context_policy", [{}])[0]
            context_policy_mutated = pack_mutated.components_data.get("context_policy", [{}])[0]
            self.assertNotEqual(context_policy_default, context_policy_mutated)

            compiler_default = ContextCompiler(
                system_core="System prompt",
                token_ceiling=15000,
                context_policy=context_policy_default,
            )
            compiled_default = compiler_default.compile(
                brief="Task statement",
                dialogue=dialogue,
            )

            compiler_mutated = ContextCompiler(
                system_core="System prompt",
                token_ceiling=15000,
                context_policy=context_policy_mutated,
            )
            compiled_mutated = compiler_mutated.compile(
                brief="Task statement",
                dialogue=dialogue,
            )

            # Observable assertion: compiler output differs under mutated policy (S8-B-02 GREEN)
            self.assertNotEqual(compiled_default.blocks, compiled_mutated.blocks)
            self.assertEqual(len([b for b in compiled_mutated.blocks if b.layer.value == "L5"]), 2)
            self.assertEqual(len([b for b in compiled_default.blocks if b.layer.value == "L5"]), 7)


if __name__ == "__main__":
    unittest.main()
