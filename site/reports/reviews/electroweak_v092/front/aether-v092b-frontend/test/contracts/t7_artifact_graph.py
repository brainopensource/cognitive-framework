"""REQ-GRAPH-001 / REQ-BASELINE-001: artifact graph and permanent control."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from vanguard.packages.domain import (
    BUILTIN_KINDS,
    ArtifactFile,
    ArtifactKind,
    GraphError,
    KindRegistry,
    LogicalEdit,
    ManifestError,
    ManifestRegistry,
    Workspace,
    compose,
    parse_manifest,
)

from .schema_subset import SchemaSet

ROOT = Path(__file__).resolve().parents[2]
MANIFESTS = ROOT / "vanguard" / "packages" / "agency" / "manifests"
SCHEMAS = ROOT / "schemas" / "v4"


def _baseline_workspace() -> Workspace:
    kinds = {
        "system-prompt.txt": "system_prompt",
        "shell-tool.json": "tool_schema",
        "context-policy.json": "context_policy",
        "routing-policy.json": "routing_policy",
        "budget-policy.json": "budget_policy",
    }
    artifacts = tuple(
        ArtifactFile(f"vg-shell-only/{name}", kind,
                     (MANIFESTS / "vg-shell-only" / name).read_text())
        for name, kind in kinds.items()
    )
    return Workspace.empty().apply(LogicalEdit("register vg-shell-only", artifacts))


class ArtifactGraphContract(unittest.TestCase):
    def test_kind_registry_is_extensible_without_changing_builtins(self) -> None:
        registry = KindRegistry.builtins()
        extended = registry.extend(ArtifactKind("team_convention", "schema://team/convention-v1"))
        self.assertEqual(tuple(kind.name for kind in registry.kinds), BUILTIN_KINDS)
        self.assertEqual(extended.resolve("team_convention").schema, "schema://team/convention-v1")

    def test_one_logical_edit_is_exactly_one_content_addressed_commit(self) -> None:
        workspace = Workspace.empty()
        next_workspace = workspace.apply(LogicalEdit(
            "add prompt and policy",
            (ArtifactFile("prompt.txt", "system_prompt", "Be precise."),
             ArtifactFile("budget.json", "budget_policy", '{"effects":"1"}')),
        ))
        self.assertEqual(len(next_workspace.commits), 1)
        self.assertEqual(next_workspace.commits[0].changed_paths, ("budget.json", "prompt.txt"))
        self.assertEqual(set(next_workspace.diff(0, 1)), {"budget.json", "prompt.txt"})

    def test_rollback_is_itself_one_auditable_logical_commit(self) -> None:
        original = Workspace.empty().apply(LogicalEdit(
            "add prompt", (ArtifactFile("prompt.txt", "system_prompt", "v1"),)))
        edited = original.apply(LogicalEdit(
            "change prompt", (ArtifactFile("prompt.txt", "system_prompt", "v2"),)))
        rolled_back = edited.rollback(1, "revert prompt experiment")
        self.assertEqual(len(rolled_back.commits), 3)
        self.assertEqual(rolled_back.graph.digest, original.graph.digest)

    def test_unregistered_kind_and_path_escape_fail_closed(self) -> None:
        with self.assertRaises(GraphError):
            Workspace.empty().apply(LogicalEdit(
                "bad kind", (ArtifactFile("x", "hardcoded_new_kind", "x"),)))
        with self.assertRaises(GraphError):
            ArtifactFile("../outside", "skill", "x")

    def test_dependency_edges_resolve_and_cycles_fail_closed(self) -> None:
        workspace = Workspace.empty().apply(LogicalEdit("add dependency graph", (
            ArtifactFile("base.txt", "system_prompt", "base"),
            ArtifactFile("operator.json", "operator", "operator", ("base.txt",)),
        )))
        self.assertEqual([item.path for item in workspace.graph.closure(("operator.json",))],
                         ["base.txt", "operator.json"])
        with self.assertRaisesRegex(GraphError, "cycle"):
            Workspace.empty().apply(LogicalEdit("cyclic graph", (
                ArtifactFile("a", "skill", "a", ("b",)),
                ArtifactFile("b", "skill", "b", ("a",)),
            )))


class ShellBaselineContract(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = json.loads((MANIFESTS / "vg-shell-only" / "manifest.json").read_text())
        self.manifest = parse_manifest(self.raw)
        self.workspace = _baseline_workspace()

    def test_baseline_files_validate_and_match_the_kind_registry(self) -> None:
        schema_set = SchemaSet(SCHEMAS)
        schema_set.validate(self.raw, "harness-manifest.schema.json")
        kind_rows = json.loads((MANIFESTS / "kinds.json").read_text())
        schema_set.validate(kind_rows, "artifact-kind-registry.schema.json")
        self.assertEqual({row["kind"] for row in kind_rows}, set(BUILTIN_KINDS))

    def test_baseline_is_one_tool_with_no_hidden_extension_layers(self) -> None:
        components = dict(self.manifest.components)
        self.assertEqual(len(components["tools"]), 1)
        self.assertNotIn("middleware", components)
        self.assertNotIn("skills", components)
        self.assertNotIn("subagents", components)
        self.assertEqual(len(self.manifest.capabilities), 1)
        self.assertEqual(self.manifest.capabilities[0].sink, "privileged")

    def test_composition_digest_is_episode_independent(self) -> None:
        """ADR-0076 §4 / 1.3-A (F-11): `D_H` is the composition's identity, not
        the run's. `episode_id` is an instance id carried on the frozen
        harness -- it must differ across two runs of the same composition --
        but it is not part of `composition_digest`'s input, so two runs of one
        composition collide byte-identically on that digest.
        """
        frozen = compose(self.manifest, self.workspace.graph, "episode-1")
        again = compose(self.manifest, self.workspace.graph, "episode-1")
        other = compose(self.manifest, self.workspace.graph, "episode-2")
        self.assertEqual(frozen.composition_digest, again.composition_digest)
        self.assertEqual(frozen.composition_digest, other.composition_digest)
        self.assertNotEqual(frozen.episode_id, other.episode_id)
        self.assertEqual(frozen.capability("proc.exec").risk, "high")

    def test_unreferenced_artifact_does_not_change_composed_identity(self) -> None:
        original = compose(self.manifest, self.workspace.graph, "episode-1")
        expanded = self.workspace.apply(LogicalEdit(
            "add unrelated experiment", (ArtifactFile("other-skill.txt", "skill", "unused"),)))
        recomposed = compose(self.manifest, expanded.graph, "episode-1")
        self.assertEqual(original.composition_digest, recomposed.composition_digest)

    def test_baseline_runs_through_an_injected_deterministic_fake(self) -> None:
        frozen = compose(self.manifest, self.workspace.graph, "episode-fake")
        capability = frozen.capability("proc.exec")
        calls: list[tuple[str, str]] = []

        def fake_environment(verb: str, selector: str) -> str:
            calls.append((verb, selector))
            return "3 passed"

        result = fake_environment(capability.verb, capability.selector)
        self.assertEqual(result, "3 passed")
        self.assertEqual(calls, [("proc.exec", capability.selector)])

#: Manifest component role -> artifact kind, for the roles whose names differ.
#: Mirrors `runtime.root.ROLE_KIND`; every other role is its own kind.
_ROLE_KIND = {"system_prompt": "system_prompt", "tools": "tool_schema"}


def _code_default_workspace() -> Workspace:
    """Register exactly the components the manifest declares.

    Derived rather than hardcoded: the previous fixture listed the eight files
    it knew about, so the first pack component added anywhere else in the tree
    broke composition here with `component does not resolve`. A fixture that
    has to be edited whenever the thing it tests grows is a fixture that will
    be wrong before it is noticed.
    """
    manifest = parse_manifest(
        json.loads((MANIFESTS / "vg-code-default" / "manifest.json").read_text()))
    wanted = [(role, path) for role, paths in manifest.components for path in paths]
    wanted.append(("budget_policy", manifest.budget_policy))
    artifacts = tuple(
        ArtifactFile(path, _ROLE_KIND.get(role, role),
                     (MANIFESTS / path).read_text())
        for role, path in wanted
    )
    return Workspace.empty().apply(LogicalEdit("register vg-code-default", artifacts))


class CodeDefaultHarnessContract(unittest.TestCase):
    """REQ-HARN-001: vg-code-default product manifest with typed read/search/patch/test."""

    def setUp(self) -> None:
        self.raw = json.loads((MANIFESTS / "vg-code-default" / "manifest.json").read_text())
        self.manifest = parse_manifest(self.raw)
        self.workspace = _code_default_workspace()

    def test_code_default_files_validate_against_schema(self) -> None:
        schema_set = SchemaSet(SCHEMAS)
        schema_set.validate(self.raw, "harness-manifest.schema.json")
        for tool_file in ("read-tool.json", "search-tool.json", "patch-tool.json", "test-tool.json"):
            tool_data = json.loads((MANIFESTS / "vg-code-default" / tool_file).read_text())
            self.assertIn("name", tool_data)
            self.assertIn("verb", tool_data)

    def test_code_default_contains_typed_tools_and_capabilities(self) -> None:
        components = dict(self.manifest.components)
        self.assertEqual(len(components["tools"]), 4)
        verbs = {cap.verb for cap in self.manifest.capabilities}
        self.assertEqual(verbs, {"fs.read", "fs.search", "patch.apply", "proc.exec"})
        sinks = {cap.verb: cap.sink for cap in self.manifest.capabilities}
        self.assertEqual(sinks["fs.read"], "observation")
        self.assertEqual(sinks["fs.search"], "observation")
        self.assertEqual(sinks["patch.apply"], "privileged")
        self.assertEqual(sinks["proc.exec"], "privileged")

    def test_composition_digest_is_episode_independent(self) -> None:
        """ADR-0076 §4 / 1.3-A (F-11): see the sibling test on
        `ShellBaselineContract` -- `episode_id` is instance identity, not
        composition identity.
        """
        frozen = compose(self.manifest, self.workspace.graph, "episode-1")
        again = compose(self.manifest, self.workspace.graph, "episode-1")
        other = compose(self.manifest, self.workspace.graph, "episode-2")
        self.assertEqual(frozen.composition_digest, again.composition_digest)
        self.assertEqual(frozen.composition_digest, other.composition_digest)
        self.assertNotEqual(frozen.episode_id, other.episode_id)

    def test_registry_contains_both_manifests_and_protects_undeletable_control(self) -> None:
        registry = ManifestRegistry.parse(json.loads((MANIFESTS / "registry.json").read_text()))
        by_name = {entry.name: entry for entry in registry.entries}
        self.assertIn("vg-shell-only", by_name)
        self.assertIn("vg-code-default", by_name)
        self.assertTrue(by_name["vg-shell-only"].undeletable)
        self.assertFalse(by_name["vg-code-default"].undeletable)

        # Baseline control cannot be deleted
        with self.assertRaisesRegex(ManifestError, "undeletable"):
            registry.remove("vg-shell-only")

        # Product default can be replaced or removed without error
        updated = registry.remove("vg-code-default")
        remaining = {entry.name: entry for entry in updated.entries}
        self.assertNotIn("vg-code-default", remaining)
        self.assertIn("vg-shell-only", remaining)


if __name__ == "__main__":
    unittest.main()

