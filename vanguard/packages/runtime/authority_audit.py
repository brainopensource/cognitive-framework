"""Executable RF-84 audit for the single production runtime authority."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from ..domain.canonicalisation.digest import digest_of


@dataclass(frozen=True, slots=True)
class AuthorityTrace:
    root: str
    files: tuple[str, ...]
    public_boundary: str
    violations: tuple[str, ...]
    trace_digest: str

    @property
    def passed(self) -> bool:
        return not self.violations

    def to_source(self) -> dict[str, object]:
        return {
            "kind": "runtime_authority_trace",
            "root": self.root,
            "files": list(self.files),
            "public_boundary": self.public_boundary,
            "violations": list(self.violations),
            "trace_digest": self.trace_digest,
        }


def audit_runtime_authority(root: Path | None = None) -> AuthorityTrace:
    """Parse every production Python caller and reject alternate run paths."""
    package_root = root or Path(__file__).resolve().parents[1]
    files = tuple(sorted(package_root.rglob("*.py")))
    violations: list[str] = []
    relative_files: list[str] = []
    for path in files:
        relative = path.relative_to(package_root).as_posix()
        relative_files.append(relative)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        session_aliases = {"HarnessSession"}
        compiler_aliases: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for imported in node.names:
                    local = imported.asname or imported.name
                    if imported.name == "HarnessSession":
                        session_aliases.add(local)
                    if module.endswith("runtime.registry.compiler") and imported.name in {
                        "compose", "compose_named"
                    }:
                        compiler_aliases.add(local)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and relative != "runtime/root.py":
                if any(_call_name(base) in session_aliases for base in node.bases):
                    violations.append(f"{relative}:{node.lineno}: HarnessSession subclass")
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node.func)
            if (name in session_aliases or name.endswith(".HarnessSession")) and relative != "runtime/root.py":
                violations.append(f"{relative}:{node.lineno}: direct HarnessSession construction")
            if name in compiler_aliases:
                violations.append(f"{relative}:{node.lineno}: legacy compiler execution")
            if name.endswith(".run") and relative != "runtime/session.py":
                owner = _call_name(node.func.value) if isinstance(node.func, ast.Attribute) else ""
                if owner in {"session", "HarnessSession"} and relative != "runtime/root.py":
                    violations.append(f"{relative}:{node.lineno}: direct session.run")
    digest_body = {
        "files": relative_files,
        "public_boundary": "vanguard.packages.runtime.root.Runtime.run_composed",
        "violations": sorted(violations),
    }
    return AuthorityTrace(
        root=package_root.as_posix(), files=tuple(relative_files),
        public_boundary=digest_body["public_boundary"],
        violations=tuple(sorted(violations)), trace_digest=digest_of(digest_body),
    )


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""
