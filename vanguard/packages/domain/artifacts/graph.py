"""Pure, content-addressed artifact workspace.

One ``LogicalEdit`` creates exactly one ``Commit``. The workspace is immutable,
so diff and rollback operate on snapshots without hidden filesystem state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional

from ..canonicalisation.digest import digest_of

BUILTIN_KINDS = (
    "system_prompt", "tool_schema", "tool_impl", "middleware", "skill",
    "context_policy", "retrieval_policy", "compaction_policy", "routing_policy",
    "budget_policy", "approval_policy", "skills", "subagent_config",
    "playbook", "process_definition", "runtime_image", "operator",
    "competence_claim",
)


class GraphError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class ArtifactKind:
    name: str
    schema: str

    def __post_init__(self) -> None:
        if not self.name or not self.schema:
            raise GraphError("artifact kind requires a name and schema")


@dataclass(frozen=True, slots=True)
class KindRegistry:
    kinds: tuple[ArtifactKind, ...]

    def __post_init__(self) -> None:
        names = [kind.name for kind in self.kinds]
        if len(names) != len(set(names)):
            raise GraphError("artifact kind names must be unique")

    @classmethod
    def builtins(cls) -> "KindRegistry":
        return cls(tuple(ArtifactKind(name, f"schema://vanguard/artifacts/{name}")
                         for name in BUILTIN_KINDS))

    def resolve(self, name: str) -> ArtifactKind:
        for kind in self.kinds:
            if kind.name == name:
                return kind
        raise GraphError(f"unregistered artifact kind: {name}")

    def extend(self, kind: ArtifactKind) -> "KindRegistry":
        if any(current.name == kind.name for current in self.kinds):
            raise GraphError(f"artifact kind already registered: {kind.name}")
        return KindRegistry(self.kinds + (kind,))


@dataclass(frozen=True, slots=True)
class ArtifactFile:
    path: str
    kind: str
    content: str
    dependencies: tuple[str, ...] = ()
    digest: str = field(init=False)

    def __post_init__(self) -> None:
        if not self.path or self.path.startswith("/") or ".." in self.path.split("/"):
            raise GraphError(f"artifact path must be relative and contained: {self.path!r}")
        if not isinstance(self.content, str):
            raise GraphError("artifact file content must be immutable text")
        if len(self.dependencies) != len(set(self.dependencies)):
            raise GraphError(f"artifact dependencies must be unique: {self.path}")
        object.__setattr__(self, "digest", digest_of({"kind": self.kind,
                                                      "content": self.content,
                                                      "dependencies": self.dependencies}))


@dataclass(frozen=True, slots=True)
class ArtifactGraph:
    files: tuple[ArtifactFile, ...]
    registry: KindRegistry
    digest: str = field(init=False)

    def __post_init__(self) -> None:
        paths = [artifact.path for artifact in self.files]
        if len(paths) != len(set(paths)):
            raise GraphError("artifact paths must be unique")
        for artifact in self.files:
            self.registry.resolve(artifact.kind)
        index = {artifact.path: artifact for artifact in self.files}
        for artifact in self.files:
            for dependency in artifact.dependencies:
                if dependency not in index:
                    raise GraphError(f"artifact dependency does not resolve: {artifact.path} -> {dependency}")
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(path: str) -> None:
            if path in visiting:
                raise GraphError(f"artifact dependency cycle reaches {path}")
            if path in visited:
                return
            visiting.add(path)
            for dependency in index[path].dependencies:
                visit(dependency)
            visiting.remove(path)
            visited.add(path)

        for path in sorted(index):
            visit(path)
        ordered = sorted((item.path, item.kind, item.digest) for item in self.files)
        object.__setattr__(self, "digest", digest_of(ordered))

    def by_path(self) -> Mapping[str, ArtifactFile]:
        return MappingProxyType({artifact.path: artifact for artifact in self.files})

    def closure(self, roots: tuple[str, ...]) -> tuple[ArtifactFile, ...]:
        index = self.by_path()
        selected: set[str] = set()

        def include(path: str) -> None:
            if path not in index:
                raise GraphError(f"artifact does not resolve: {path}")
            if path in selected:
                return
            selected.add(path)
            for dependency in index[path].dependencies:
                include(dependency)

        for root in roots:
            include(root)
        return tuple(index[path] for path in sorted(selected))


@dataclass(frozen=True, slots=True)
class LogicalEdit:
    message: str
    upserts: tuple[ArtifactFile, ...] = ()
    deletes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.message:
            raise GraphError("logical edit requires a message")
        touched = [item.path for item in self.upserts] + list(self.deletes)
        if len(touched) != len(set(touched)):
            raise GraphError("one logical edit cannot touch a path twice")


@dataclass(frozen=True, slots=True)
class Commit:
    commit_id: str
    parent_id: Optional[str]
    message: str
    graph_digest: str
    changed_paths: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Workspace:
    graph: ArtifactGraph
    commits: tuple[Commit, ...] = ()
    snapshots: tuple[ArtifactGraph, ...] = ()

    @classmethod
    def empty(cls, registry: Optional[KindRegistry] = None) -> "Workspace":
        graph = ArtifactGraph((), registry or KindRegistry.builtins())
        return cls(graph=graph, snapshots=(graph,))

    def apply(self, edit: LogicalEdit) -> "Workspace":
        current = dict(self.graph.by_path())
        for path in edit.deletes:
            if path not in current:
                raise GraphError(f"cannot delete absent artifact: {path}")
            del current[path]
        for artifact in edit.upserts:
            self.graph.registry.resolve(artifact.kind)
            current[artifact.path] = artifact
        next_graph = ArtifactGraph(tuple(sorted(current.values(), key=lambda item: item.path)), self.graph.registry)
        if next_graph.digest == self.graph.digest:
            raise GraphError("logical edit must change the graph")
        parent = self.commits[-1].commit_id if self.commits else None
        changed = tuple(sorted((*edit.deletes, *(item.path for item in edit.upserts))))
        commit_id = digest_of({"parent": parent, "message": edit.message,
                               "graph": next_graph.digest, "paths": changed})
        commit = Commit(commit_id, parent, edit.message, next_graph.digest, changed)
        return Workspace(next_graph, self.commits + (commit,), self.snapshots + (next_graph,))

    def diff(self, older: int, newer: int) -> Mapping[str, tuple[Optional[str], Optional[str]]]:
        before = self.snapshots[older].by_path()
        after = self.snapshots[newer].by_path()
        result = {}
        for path in sorted(set(before) | set(after)):
            left = before[path].digest if path in before else None
            right = after[path].digest if path in after else None
            if left != right:
                result[path] = (left, right)
        return MappingProxyType(result)

    def rollback(self, snapshot: int, message: str) -> "Workspace":
        target = self.snapshots[snapshot]
        current = self.graph.by_path()
        desired = target.by_path()
        upserts = tuple(desired[path] for path in sorted(desired)
                        if path not in current or current[path].digest != desired[path].digest)
        deletes = tuple(path for path in sorted(current) if path not in desired)
        return self.apply(LogicalEdit(message=message, upserts=upserts, deletes=deletes))
