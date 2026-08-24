"""B0 Baseline Characterization and Mapping Matrix Contract Tests.

Maps and validates the baseline behavior of:
- Manifest readers (legacy vs v2 named graph)
- Runtime composition callers
- Binding tables and domain-specific isolation
- Event store persistence (memory vs file-backed WAL)
- M-4 foundation evidence auditor behavior
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency.manifests.loader import ManifestLoader, ManifestLoadError
from vanguard.packages.domain.artifacts.graph import ArtifactFile, ArtifactGraph, KindRegistry
from vanguard.packages.domain.artifacts.manifest import (
    ManifestError,
    NamedManifest,
    parse_manifest,
    parse_named_manifest,
)
from vanguard.packages.domain.evidence.audit import (
    REQUIRED_ROW_COUNT,
    REQUIRED_ROW_NAMES,
    audit_foundation_evidence,
)
from vanguard.packages.runtime.compose import CompositionError, Runtime
from vanguard.packages.runtime.registry.compiler import compose_named
from vanguard.packages.runtime.registry.lifecycle import (
    IllegalPluginTransition,
    PluginLifecycle,
    PluginState,
)
from vanguard.packages.runtime.wiring import DEFAULT_BINDINGS, EffectBinding


class B0BaselineCharacterizationTests(unittest.TestCase):
    """Characterization tests documenting baseline behavior and diagnosed gaps."""

    def setUp(self) -> None:
        self.manifests_dir = (
            Path(__file__).resolve().parents[2]
            / "vanguard"
            / "packages"
            / "agency"
            / "manifests"
        )
        self.loader = ManifestLoader(self.manifests_dir)

    def test_b0_01_legacy_manifest_loader_reads_legacy_packs(self) -> None:
        """B0.1: ManifestLoader reads legacy-shaped packs (e.g. vg-code-default)."""
        pack = self.loader.load_pack("vg-code-default")
        self.assertEqual(pack.name, "vg-code-default")
        self.assertIn("fs.read", {c.verb for c in pack.manifest.capabilities})
        self.assertIn("proc.exec", {c.verb for c in pack.manifest.capabilities})

    def test_b0_02_table_pack_cannot_be_wired_by_default_bindings(self) -> None:
        """B0.2: Diagnosed Gap - vg-table-default requires table.read/table.patch,
        which are not present in global DEFAULT_BINDINGS.
        """
        pack = self.loader.load_pack("vg-table-default")
        table_verbs = {c.verb for c in pack.manifest.capabilities}
        self.assertEqual(table_verbs, {"table.read", "table.patch"})

        # DEFAULT_BINDINGS only knows coding verbs
        for verb in table_verbs:
            self.assertNotIn(verb, DEFAULT_BINDINGS)

        # Calling Runtime.compose with default bindings fails as diagnosed in ADR-0088
        with self.assertRaises(CompositionError) as ctx:
            Runtime.compose("vg-table-default")
        self.assertIn("no adapter bound for ['table.patch', 'table.read']", str(ctx.exception))

    def test_b0_03_named_manifest_v2_parser_and_compiler_exist_as_side_path(self) -> None:
        """B0.3: mhf.manifest/2 parser and compiler function correctly when invoked directly."""
        v2_raw = {
            "api": "mhf.manifest/2",
            "id": "char-pack-v2",
            "components": {
                "toolkit": {
                    "kind": "IToolkit",
                    "implementation": "impl.py",
                    "config": "cfg.json",
                    "isolation": "in_process",
                    "ceiling": [{"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}],
                    "interfaces": ["IToolkit"],
                }
            },
            "bindings": [],
            "entrypoints": ["toolkit"],
            "ceiling": [{"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}],
        }
        named = parse_named_manifest(v2_raw)
        self.assertEqual(named.manifest_id, "char-pack-v2")
        self.assertEqual(named.api, "mhf.manifest/2")

        graph = ArtifactGraph(
            (
                ArtifactFile("impl.py", "tool_impl", "def foo(): pass"),
                ArtifactFile("cfg.json", "tool_schema", "{}"),
            ),
            KindRegistry.builtins(),
        )
        frozen = compose_named(v2_raw, graph)
        self.assertTrue(frozen.digest.startswith("sha256:"))

    def test_b0_04_plugin_lifecycle_state_machine_transitions(self) -> None:
        """B0.4: PluginLifecycle enforces DISCOVERED -> RESOLVED -> VERIFIED -> ACTIVATED -> QUIESCING -> RETIRED."""
        class MockEmitter:
            def __init__(self) -> None:
                self.events: list[dict[str, object]] = []

            def emit_kind(self, kind: str, **kwargs: object) -> None:
                self.events.append({"kind": kind, **kwargs})

        emitter = MockEmitter()
        lc = PluginLifecycle("plug-1", emitter, run_id="run-1", principal="reg", manifest_digest="sha256:m")
        self.assertEqual(lc.state, PluginState.DISCOVERED)

        lc.resolve()
        self.assertEqual(lc.state, PluginState.RESOLVED)

        lc.verify(graph_digest="sha256:g", ceiling_digest="sha256:c")
        self.assertEqual(lc.state, PluginState.VERIFIED)

        lc.activate()
        self.assertEqual(lc.state, PluginState.ACTIVATED)

        lc.quiesce()
        self.assertEqual(lc.state, PluginState.QUIESCING)

        lc.retire()
        self.assertEqual(lc.state, PluginState.RETIRED)

        # Illegal transition after retirement raises
        with self.assertRaises(IllegalPluginTransition):
            lc.activate()

    def test_b0_05_m4_auditor_rejects_incomplete_or_synthetic_rows(self) -> None:
        """B0.5: M-4 auditor requires all 9 canonical rows and rejects synthetic markers."""
        # Test missing rows
        partial_rows = [{"row": 1, "run_id": "r1", "name": "real_model_invocation"}]
        res = audit_foundation_evidence(partial_rows)
        self.assertFalse(res.passed)
        self.assertIn("missing_required_evidence_rows", str(res.rejection_reasons))

        # Test synthetic/mock provider rejection
        fake_rows = []
        for i in range(1, REQUIRED_ROW_COUNT + 1):
            fake_rows.append({
                "row": i,
                "run_id": "r1",
                "name": REQUIRED_ROW_NAMES[i],
                "provider": "fake" if i == 1 else "canonical",
            })
        res_fake = audit_foundation_evidence(fake_rows)
        self.assertFalse(res_fake.passed)
        self.assertIn("row_1: fake_or_mock_model_provider_rejected", res_fake.rejection_reasons)


if __name__ == "__main__":
    unittest.main()
