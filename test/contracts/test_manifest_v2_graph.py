"""Contract coverage for the canonical named component graph compiler."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.agency.manifests.loader import ManifestLoader
from vanguard.packages.domain.artifacts.graph import ArtifactFile, ArtifactGraph, KindRegistry
from vanguard.packages.domain.artifacts.manifest import ManifestError, parse_named_manifest
from vanguard.packages.runtime.registry.compiler import compose_named


class NamedManifestGraphContract(unittest.TestCase):
    def setUp(self) -> None:
        self.selector = {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}
        self.graph = ArtifactGraph(
            (
                ArtifactFile("impl", "tool_impl", "echo-v1"),
                ArtifactFile("config", "tool_schema", "{}"),
            ),
            KindRegistry.builtins(),
        )

    def manifest(self) -> dict[str, object]:
        return {
            "api": "mhf.manifest/2",
            "id": "named-demo",
            "components": {
                "main": {
                    "spi": "toolkit", "ref": "impl", "config": "config",
                    "isolation": "subprocess", "ceiling": [self.selector],
                    "interfaces": ["IToolkit"],
                },
                "critic": {
                    "spi": "toolkit", "ref": "impl", "config": "config",
                    "isolation": "subprocess", "ceiling": [self.selector],
                    "interfaces": ["IToolkit"],
                },
            },
            "bindings": [{"from": "main", "to": "critic", "interface": "IToolkit", "lazy": True}],
            "entrypoints": ["main"],
            "profiles": {"default": {"mode": "sequential"}},
            "ceiling": [self.selector],
        }

    def test_repeated_spi_instances_compile_and_resolve(self) -> None:
        """RF-28: two named instances may share one SPI kind."""
        frozen = compose_named(self.manifest(), self.graph)
        self.assertEqual([item.kind for item in frozen.components], ["IToolkit", "IToolkit"])
        self.assertEqual(frozen.components[0].implementation, "impl")
        self.assertTrue(frozen.digest.startswith("sha256:"))

    def test_edge_only_change_changes_frozen_digest(self) -> None:
        """RF-30: changing only a binding changes the frozen identity."""
        first = compose_named(self.manifest(), self.graph)
        changed = self.manifest()
        changed["bindings"] = [{"from": "critic", "to": "main", "interface": "IToolkit", "lazy": True}]
        second = compose_named(changed, self.graph)
        self.assertNotEqual(first.digest, second.digest)

    def test_refs_and_graph_rules_fail_closed(self) -> None:
        """RF-32: refs, endpoints, interfaces, self-edges, and eager cycles deny."""
        for change in (
            {"ref": "missing"},
            {"binding": {"from": "main", "to": "missing", "interface": "IToolkit", "lazy": True}},
            {"binding": {"from": "main", "to": "main", "interface": "IToolkit", "lazy": True}},
            {"binding": {"from": "main", "to": "critic", "interface": "IUnknown", "lazy": True}},
        ):
            candidate = self.manifest()
            if "ref" in change:
                candidate["components"] = dict(candidate["components"])
                candidate["components"]["main"] = dict(candidate["components"]["main"])
                candidate["components"]["main"]["ref"] = change["ref"]
            else:
                candidate["bindings"] = [change["binding"]]
            with self.assertRaises((ManifestError, ValueError)):
                compose_named(candidate, self.graph)

        cycle = self.manifest()
        cycle["bindings"] = [
            {"from": "main", "to": "critic", "interface": "IToolkit"},
            {"from": "critic", "to": "main", "interface": "IToolkit"},
        ]
        with self.assertRaises(ManifestError):
            parse_named_manifest(cycle)

    def test_ceiling_and_reserved_spawn_fail_closed(self) -> None:
        """RF-31/RF-74: ceilings deny widening and spawn remains inert before M-6."""
        empty = self.manifest()
        empty["components"] = dict(empty["components"])
        empty["components"]["main"] = dict(empty["components"]["main"])
        empty["components"]["main"]["ceiling"] = []
        with self.assertRaises(ManifestError):
            parse_named_manifest(empty)

        widened = self.manifest()
        widened["components"] = dict(widened["components"])
        widened["components"]["main"] = dict(widened["components"]["main"])
        widened["components"]["main"]["ceiling"] = [
            {"kind": "fs", "root": "/", "paths": ["/"]}
        ]
        with self.assertRaises(ManifestError):
            compose_named(widened, self.graph)

        spawn = self.manifest()
        spawn["capabilities"] = [{"verb": "agent.spawn", "selector": self.selector}]
        with self.assertRaisesRegex(ManifestError, "agent.spawn not implemented"):
            compose_named(spawn, self.graph)

    def test_profiles_and_reserved_metadata_are_identity_inputs(self) -> None:
        """RF-73: reserved profile/route/guardrail values cannot be identity-inert."""
        first = compose_named(self.manifest(), self.graph)
        for field, value in (
            ("profiles", {"default": {"mode": "different"}}),
            ("model_routes", [{"tier": 1, "provider": "fake", "model": "other"}]),
            ("guardrails", {"absence_reason": "explicit"}),
        ):
            changed = self.manifest()
            changed[field] = value
            self.assertNotEqual(first.digest, compose_named(changed, self.graph).digest, field)

    def test_agency_loader_is_a_compatibility_reader(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps(self.manifest()), encoding="utf-8")
            loaded = ManifestLoader(directory).load_named_manifest(path)
        self.assertEqual(loaded.api, "mhf.manifest/2")
        self.assertEqual(loaded.entrypoints, ("main",))


if __name__ == "__main__":
    unittest.main()
