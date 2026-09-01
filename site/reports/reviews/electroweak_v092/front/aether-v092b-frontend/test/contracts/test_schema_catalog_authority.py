"""B-O2-01: one authority per contract across schemas/mhf and schemas/v4.

Order 2 asks which of ``schemas/mhf`` and ``schemas/v4`` is authoritative. The
answer is that they are not two versions of one catalog -- they are two disjoint
catalogs with different jobs, and the real hazard is the narrower one this module
guards: the same contract defined twice, in two places, with two shapes.

``ApprovalDecision`` was exactly that. ``approval-decision.schema.json`` required
the 128-hex Ed25519 signature both signers emit; ``runtime-service.schema.json``
inlined a near-copy that accepted any non-empty string, and the copy was the one
guarding ResolveApproval ingress. The weaker duplicate wins by default, because
nothing compares them.

Catalog partition:

* ``schemas/mhf/`` -- event and ledger payload wire types (event kinds,
  trajectory, topology, execution profiles, named manifest v2). Consumed by
  ``tools/codegen/generate_types.py`` into the Python wire types.
* ``schemas/v4/`` -- vg.4 domain and service contracts (envelope, receipt,
  artifact, capability grant, runtime service). Consumed by
  ``tools/codegen/generate_ts_contracts.py`` into the TypeScript contracts.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_MHF = _REPO_ROOT / "schemas" / "mhf"
_V4 = _REPO_ROOT / "schemas" / "v4"

#: Manifest authority, resolved by Order 2 from what the code actually loads.
#: `agency/manifests/loader.py` reads v4/harness-manifest as the current schema
#: and mhf/manifest_v2 as the legacy named-manifest ingress schema.
#: `mhf/harness_manifest.schema.json` is loaded by nothing: it survives only in
#: the baseline digest set, and is recorded here as orphaned rather than deleted,
#: because deleting it would silently change that digest set.
_ORPHANED = {"harness_manifest.schema.json"}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _defs(path: Path) -> dict:
    return _load(path).get("$defs", {})


class SchemaCatalogPartition(unittest.TestCase):
    def test_both_catalogs_exist_and_are_disjoint_by_id(self) -> None:
        """No `$id` appears in both catalogs: they are not two versions of one thing."""
        def ids(d: Path) -> set[str]:
            return {_load(p).get("$id", p.name) for p in d.glob("*.schema.json")}

        self.assertTrue(ids(_MHF))
        self.assertTrue(ids(_V4))
        self.assertEqual(ids(_MHF) & ids(_V4), set())

    def test_every_schema_id_is_unique_within_its_catalog(self) -> None:
        for catalog in (_MHF, _V4):
            with self.subTest(catalog=catalog.name):
                seen: dict[str, str] = {}
                for path in sorted(catalog.glob("*.schema.json")):
                    schema_id = _load(path).get("$id")
                    if schema_id is None:
                        continue
                    self.assertNotIn(
                        schema_id, seen, f"{path.name} reuses the $id of {seen.get(schema_id)}"
                    )
                    seen[schema_id] = path.name

    def test_manifest_authority_is_recorded_and_orphans_are_declared(self) -> None:
        """A manifest schema is either loaded by the code or declared orphaned."""
        self.assertTrue((_V4 / "harness-manifest.schema.json").is_file())
        self.assertTrue((_MHF / "manifest_v2.schema.json").is_file())

        loader = (
            _REPO_ROOT / "vanguard" / "packages" / "agency" / "manifests" / "loader.py"
        ).read_text(encoding="utf-8")
        self.assertIn("harness-manifest.schema.json", loader)
        self.assertIn("manifest_v2.schema.json", loader)

        for name in _ORPHANED:
            with self.subTest(orphan=name):
                self.assertNotIn(name, loader, f"{name} is declared orphaned but is loaded")


class NoDuplicateContractDefinitions(unittest.TestCase):
    """A contract with its own schema file is referenced, never re-inlined."""

    def test_standalone_v4_schemas_are_not_redefined_inline(self) -> None:
        standalone = {
            p.stem.replace("-", " ").title().replace(" ", ""): p
            for p in _V4.glob("*.schema.json")
            if not p.name.endswith(".reader.schema.json")
        }
        for path in sorted(_V4.glob("*.schema.json")):
            if path.name.endswith(".reader.schema.json"):
                continue
            for name, node in _defs(path).items():
                if name not in standalone or standalone[name] == path:
                    continue
                with self.subTest(schema=path.name, definition=name):
                    self.assertIn(
                        "$ref",
                        node,
                        f"{path.name} inlines {name}, which {standalone[name].name} already "
                        f"defines. Two shapes for one contract drift, and the weaker one "
                        f"guards ingress. Reference it instead.",
                    )
                    self.assertNotIn("properties", node)

    def test_approval_decision_has_exactly_one_shape(self) -> None:
        """The regression this module exists for."""
        standalone = _load(_V4 / "approval-decision.schema.json")
        slot = _defs(_V4 / "runtime-service.schema.json")["ApprovalDecision"]
        self.assertEqual(slot.get("$ref"), "approval-decision.schema.json")
        self.assertEqual(
            standalone["properties"]["signature"]["pattern"], r"^[0-9a-fA-F]{128}$"
        )


if __name__ == "__main__":
    unittest.main()
