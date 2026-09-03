"""Typed artifact graph and immutable harness composition (T7.1-T7.3)."""

from .graph import (
    BUILTIN_KINDS,
    ArtifactFile,
    ArtifactGraph,
    ArtifactKind,
    Commit,
    GraphError,
    KindRegistry,
    LogicalEdit,
    Workspace,
)
from .skill_index import (
    MAX_SKILL_INDEX_CHARS,
    SkillCard,
    SkillIndexError,
    format_skill_index,
    parse_skill_card,
)
from .manifest import (
    CapabilityRequirement,
    CanonicalManifest,
    FrozenComposition,
    FrozenHarness,
    HarnessManifest,
    ManifestRegistry,
    RegisteredManifest,
    ManifestError,
    compose,
    parse_manifest,
    NamedComponent,
    NamedManifest,
    TypedBinding,
    compose_named_manifest,
    parse_named_manifest,
)

__all__ = [
    "BUILTIN_KINDS", "ArtifactFile", "ArtifactGraph", "ArtifactKind", "Commit",
    "GraphError", "KindRegistry", "LogicalEdit", "Workspace",
    "CanonicalManifest", "CapabilityRequirement", "FrozenComposition", "FrozenHarness", "HarnessManifest", "ManifestRegistry",
    "RegisteredManifest", "ManifestError",
    "compose", "parse_manifest",
    "NamedComponent", "NamedManifest", "TypedBinding", "compose_named_manifest",
    "parse_named_manifest",
    "MAX_SKILL_INDEX_CHARS", "SkillCard", "SkillIndexError",
    "format_skill_index", "parse_skill_card",
]
