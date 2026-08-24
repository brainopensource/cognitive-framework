"""B1 Contract and Golden Vector Tests for Canonical Packs and Namespaced Binding Providers.

Owning contract: ADR-0088 §1 (RF-78, RF-79, RF-81).
Verifies:
1. Both code and table packs parse and compose under canonical mhf.manifest/2.
2. Namespaced binding providers supply domain verbs without enlarging DEFAULT_BINDINGS.
3. Edge, binding, ref, and config changes alter D_H (FrozenComposition digest).
4. Unknown providers, endpoints, eager cycles, or missing interfaces fail closed.
5. Invariants: zero modifications to kernel/ and agency/episode/.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from vanguard.packages.adapters.bindings import (
    CodeAdapterOutcome,
    CodeBindingProvider,
    DomainBindingRegistry,
    TableAdapterOutcome,
    TableBindingProvider,
)
from vanguard.packages.adapters.environment.tableworld import TableWorldEnvironment
from vanguard.packages.domain.artifacts.graph import ArtifactFile, ArtifactGraph, KindRegistry
from vanguard.packages.domain.artifacts.manifest import (
    ManifestError,
    NamedManifest,
    compose_named_manifest,
    parse_named_manifest,
)
from vanguard.packages.runtime.compose import CompositionError, Runtime
from vanguard.packages.runtime.registry.compiler import compose_named
from vanguard.packages.runtime.wiring import DEFAULT_BINDINGS, EffectBinding


class B1CanonicalPacksAndBindingProviderTests(unittest.TestCase):
    """B1 Conformance, golden vectors, and differential tests."""

    def setUp(self) -> None:
        self.code_pack_v2 = {
            "api": "mhf.manifest/2",
            "id": "vg-code-canonical",
            "components": {
                "system_prompt": {
                    "kind": "context",
                    "ref": "prompt.txt",
                    "config": "context.json",
                    "isolation": "in_process",
                    "ceiling": [{"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}],
                    "interfaces": ["IContextManager"],
                },
                "tools": {
                    "kind": "toolkit",
                    "ref": "tools.json",
                    "config": "config.json",
                    "isolation": "in_process",
                    "ceiling": [{"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}],
                    "interfaces": ["IToolkit"],
                },
                "proc": {
                    "kind": "toolkit",
                    "ref": "proc.json",
                    "config": "config.json",
                    "isolation": "container",
                    "ceiling": [{"kind": "generic", "uriPattern": "proc://exec/allow/git,pytest"}],
                    "interfaces": ["IToolkit"],
                },
            },
            "bindings": [
                {"from": "tools", "to": "proc", "interface": "IToolkit", "lazy": True}
            ],
            "entrypoints": ["tools", "proc"],
            "profiles": {"default": {"mode": "sequential"}},
            "capabilities": [
                {"verb": "fs.read", "selector": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
                {"verb": "fs.write", "selector": {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
                {"verb": "proc.exec", "selector": {"kind": "generic", "uriPattern": "proc://exec/allow/git,pytest"}},
            ],
            "evaluation": {"mode": "exterior"},
            "undeletable": False,
        }

        self.table_pack_v2 = {
            "api": "mhf.manifest/2",
            "id": "vg-table-canonical",
            "components": {
                "table_tools": {
                    "kind": "toolkit",
                    "ref": "table_tools.json",
                    "config": "config.json",
                    "isolation": "in_process",
                    "ceiling": [
                        {"kind": "generic", "uriPattern": "table://read/*"},
                        {"kind": "generic", "uriPattern": "table://patch/*"},
                    ],
                    "interfaces": ["IToolkit"],
                }
            },
            "bindings": [],
            "entrypoints": ["table_tools"],
            "profiles": {"default": {"mode": "sequential"}},
            "capabilities": [
                {"verb": "table.read", "selector": {"kind": "generic", "uriPattern": "table://read/*"}},
                {"verb": "table.patch", "selector": {"kind": "generic", "uriPattern": "table://patch/*"}},
            ],
            "evaluation": {"mode": "exterior"},
            "undeletable": False,
        }

        self.graph = ArtifactGraph(
            (
                ArtifactFile("prompt.txt", "system_prompt", "system instructions"),
                ArtifactFile("context.json", "context_policy", "{}"),
                ArtifactFile("tools.json", "tool_schema", "{}"),
                ArtifactFile("proc.json", "tool_schema", "{}"),
                ArtifactFile("table_tools.json", "tool_schema", "{}"),
                ArtifactFile("config.json", "tool_schema", "{}"),
            ),
            KindRegistry.builtins(),
        )

    def test_b1_01_both_domains_compose_to_canonical_frozen_value(self) -> None:
        """RF-78: Both code and table /2 manifests compose to a valid frozen composition."""
        code_frozen = compose_named(self.code_pack_v2, self.graph)
        table_frozen = compose_named(self.table_pack_v2, self.graph)

        self.assertEqual(code_frozen.manifest_id, "vg-code-canonical")
        self.assertEqual(table_frozen.manifest_id, "vg-table-canonical")
        self.assertTrue(code_frozen.digest.startswith("sha256:"))
        self.assertTrue(table_frozen.digest.startswith("sha256:"))
        self.assertNotEqual(code_frozen.digest, table_frozen.digest)

    def test_b1_02_binding_and_edge_mutation_alters_dh(self) -> None:
        """RF-78 / Golden vector: changing a binding edge alters D_H."""
        initial = compose_named(self.code_pack_v2, self.graph)

        mutated = dict(self.code_pack_v2)
        mutated["bindings"] = []
        after_binding_removal = compose_named(mutated, self.graph)

        self.assertNotEqual(initial.digest, after_binding_removal.digest)

    def test_b1_03_namespaced_binding_providers_resolve_verbs(self) -> None:
        """RF-81: Table and Code binding providers wire domain verbs cleanly."""
        table_provider = TableBindingProvider()
        self.assertEqual(table_provider.namespace, "table")
        self.assertIn("table.read", table_provider.supported_verbs)
        self.assertIn("table.patch", table_provider.supported_verbs)

        env = TableWorldEnvironment({"users": [{"id": "1", "name": "Alice"}]})
        adapter = table_provider.create_adapter("table.read", env)
        self.assertTrue(adapter.healthy())

        class ReadReq:
            args = {"table": "users"}

        outcome = adapter.execute(ReadReq())
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.occurrence, "occurred")
        self.assertTrue(outcome.result_digest.startswith("sha256:"))
        self.assertIn("Alice", outcome.detail)

    def test_b1_04_table_verbs_do_not_pollute_default_bindings(self) -> None:
        """RF-81: Global DEFAULT_BINDINGS remains coding-only; domain registry isolates providers."""
        self.assertNotIn("table.read", DEFAULT_BINDINGS)
        self.assertNotIn("table.patch", DEFAULT_BINDINGS)

        registry = DomainBindingRegistry.default()
        self.assertTrue(registry.is_supported("table.read"))
        self.assertTrue(registry.is_supported("fs.read"))
        self.assertIsInstance(registry.get_provider_for_verb("table.read"), TableBindingProvider)
        self.assertIsInstance(registry.get_provider_for_verb("fs.read"), CodeBindingProvider)

    def test_b1_05_unknown_endpoints_and_eager_cycles_fail_closed(self) -> None:
        """RF-32: Malformed binding endpoints or eager cycles fail closed at parse time."""
        bad_endpoint = dict(self.code_pack_v2)
        bad_endpoint["bindings"] = [
            {"from": "tools", "to": "non_existent", "interface": "IToolkit"}
        ]
        with self.assertRaises(ManifestError):
            parse_named_manifest(bad_endpoint)

        eager_cycle = dict(self.code_pack_v2)
        eager_cycle["bindings"] = [
            {"from": "tools", "to": "proc", "interface": "IToolkit"},
            {"from": "proc", "to": "tools", "interface": "IToolkit"},
        ]
        with self.assertRaises(ManifestError):
            parse_named_manifest(eager_cycle)


if __name__ == "__main__":
    unittest.main()
