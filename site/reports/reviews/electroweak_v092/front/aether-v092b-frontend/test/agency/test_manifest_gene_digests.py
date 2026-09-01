"""Gene digests and pack-local aliases — DNA comparability (no engine edits)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from vanguard.packages.adapters.models.invocation import ProposalTranslator
from vanguard.packages.agency.manifests.loader import ManifestLoader
from vanguard.packages.runtime.root import Runtime

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"
CODE_DEFAULT = MANIFESTS / "vg-code-default" / "manifest.json"


class GeneDigests(unittest.TestCase):
    def test_compose_is_stable_for_one_pack(self) -> None:
        first = Runtime.compose(CODE_DEFAULT, episode_id="gene-1")
        second = Runtime.compose(CODE_DEFAULT, episode_id="gene-1")
        self.assertTrue(first.gene_digests)
        self.assertEqual(dict(first.gene_digests), dict(second.gene_digests))

    def test_prompt_byte_change_moves_only_prompt_digest(self) -> None:
        prompt = MANIFESTS / "vg-code-default" / "system-prompt.txt"
        original = prompt.read_text(encoding="utf-8")
        key = "vg-code-default/system-prompt.txt"
        try:
            before = dict(Runtime.compose(CODE_DEFAULT).gene_digests)
            prompt.write_text(original + "\n", encoding="utf-8")
            after = dict(Runtime.compose(CODE_DEFAULT).gene_digests)
            self.assertNotEqual(before[key], after[key])
            for name, digest in before.items():
                if name == key:
                    continue
                self.assertEqual(digest, after[name], name)
        finally:
            prompt.write_text(original, encoding="utf-8")

    def test_every_registry_pack_composes(self) -> None:
        registry = json.loads((MANIFESTS / "registry.json").read_text(encoding="utf-8"))
        for entry in registry["manifests"]:
            path = MANIFESTS / entry["path"]
            harness = Runtime.compose(path)
            self.assertEqual(harness.harness, entry["name"])
            self.assertTrue(harness.gene_digests)
            names = {item.get("name") for item in harness.tool_schemas}
            if entry["name"] == "vg-code-claude-shaped":
                self.assertIn("Read", names)
            if entry["name"] == "vg-code-opencode-shaped":
                self.assertIn("view_file", names)


class PackAliases(unittest.TestCase):
    def test_read_alias_maps_to_fs_read(self) -> None:
        pack = ManifestLoader().load_pack(CODE_DEFAULT.parent)
        result = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "read", "arguments": {"path": "x.py"}}]},
            aliases=pack.translator,
        )
        self.assertTrue(result.ok, getattr(result, "error", None))
        self.assertEqual(result.value["action"], "fs.read")

    def test_unknown_alias_fails_closed(self) -> None:
        pack = ManifestLoader().load_pack(CODE_DEFAULT.parent)
        result = ProposalTranslator.translate(
            {"text": "", "toolCalls": [{"name": "NotATool", "arguments": {}}]},
            aliases=pack.translator,
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.error.kind, "instrument_error")


if __name__ == "__main__":
    unittest.main()

