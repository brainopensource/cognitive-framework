#!/usr/bin/env python3
"""Fail on forbidden Vanguard imports, disposable imports, or source cycles."""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import defaultdict
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import repo_root


SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
IGNORED_PARTS = {".git", ".venv", "node_modules", "__pycache__", "dist", "build"}
PACKAGE_NAMES = {"domain", "ports", "kernel", "agency", "runtime", "adapters"}
ALLOWED = {
    "domain": set(),
    "ports": {"domain"},
    "kernel": {"domain", "ports"},
    "agency": {"domain", "ports", "kernel"},
    "adapters": {"domain", "ports"},
    # VG-03 LT-6: runtime/ may import everything, and it is the only module
    # that may -- it is the composition root. Omitting "governance" made the
    # declared approval process unreachable from any composition, which is a
    # gap in this table rather than a property of the architecture.
    "runtime": {"domain", "ports", "kernel", "agency", "adapters", "governance"},
    # VG-03 5.4: no model dependency in governance. A compliance path that
    # calls an LLM is not a compliance path, so this row stays narrow.
    "governance": {"domain", "ports", "kernel"},
    "client": {"domain", "runtime"},
}

# S7-A-02 (N-06): shell is contained by the sandbox, not mediated by the host
# language. Process creation belongs to adapters/sandbox/ alone; this rule is
# the static half of that guarantee.
SUBPROCESS_MODULES = {"subprocess", "os.popen", "pty", "child_process", "node:child_process"}
SUBPROCESS_HOME = ("vanguard", "packages", "adapters", "sandbox")

# Triaged exceptions, each named individually. A wildcard here would defeat the
# rule, so entries are exact repo-relative paths and every one carries its
# justification. Adding a row is a deliberate act with a reviewer attached.
SUBPROCESS_ALLOWLIST = {
    # The exterior judge executes the oracle in its own process. A-05/LT-4: the
    # evaluator is architecturally unreachable from the agent it judges, so it
    # cannot borrow the agent's sandbox to do this.
    "vanguard/packages/adapters/evaluators/isolated.py",
    # EnvironmentPort's git-backed snapshot/diff. Host git invocation behind the
    # port. Candidate for containment once the sandbox grows a git verb.
    "vanguard/packages/adapters/environment/git.py",
    # `git ls-files --error-unmatch` proving the .env is untracked before a
    # secret is read. Read-only query, no agent-supplied argv.
    "vanguard/packages/adapters/models/env_loader.py",
}

JS_IMPORT = re.compile(
    r"(?:\b(?:import|export)\s+(?:[^;\n]*?\s+from\s+)?|\brequire\s*\(|\bimport\s*\()"
    r"[\"']([^\"']+)[\"']"
)


def source_files(root: Path) -> list[Path]:
    starts = [
        root / "vanguard" / "packages",
        root / "vanguard" / "clients",
        root / "benchmarkings",
        root / "spike",
        root / "slice",
        root / "lab",
    ]
    files: list[Path] = []
    for start in starts:
        if not start.exists():
            continue
        for path in start.rglob("*"):
            if path.is_file() and path.suffix in SOURCE_SUFFIXES and not (set(path.parts) & IGNORED_PARTS):
                files.append(path.resolve())
    return sorted(set(files))


def area_for(path: Path, root: Path) -> tuple[str | None, str | None]:
    rel = path.resolve().relative_to(root.resolve())
    parts = rel.parts
    if parts and parts[0] in {"spike", "slice", "lab", "benchmarkings"}:
        return parts[0], None
    if len(parts) >= 3 and parts[:2] == ("vanguard", "packages"):
        package = parts[2]
        if package == "runtime" and len(parts) >= 4 and parts[3] == "governance":
            return "governance", None
        if package == "adapters":
            family = parts[3] if len(parts) >= 4 else None
            return "adapters", family
        if package in PACKAGE_NAMES:
            return package, None
    if len(parts) >= 3 and parts[:2] == ("vanguard", "clients"):
        return "client", parts[2]
    return None, None


def python_imports(path: Path) -> list[tuple[int, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise ValueError(f"cannot parse {path}: {exc}") from exc
    found: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.extend((node.lineno, alias.name) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            prefix = "." * node.level
            found.append((node.lineno, prefix + (node.module or "")))
    return found


def imports_in(path: Path) -> list[tuple[int, str]]:
    if path.suffix == ".py":
        return python_imports(path)
    text = path.read_text(encoding="utf-8")
    return [(text.count("\n", 0, match.start()) + 1, match.group(1)) for match in JS_IMPORT.finditer(text)]


def resolve_relative(source: Path, spec: str) -> Path | None:
    if not spec.startswith("."):
        return None
    if source.suffix == ".py":
        levels = len(spec) - len(spec.lstrip("."))
        base = source.parent
        for _ in range(max(levels - 1, 0)):
            base = base.parent
        tail = spec[levels:].replace(".", "/")
        candidate = base / tail if tail else base / "__init__"
    else:
        candidate = source.parent / spec
    options = [candidate]
    options.extend(candidate.with_suffix(suffix) for suffix in SOURCE_SUFFIXES)
    options.extend(candidate / ("index" + suffix) for suffix in SOURCE_SUFFIXES)
    options.append(candidate / "__init__.py")
    for option in options:
        if option.is_file():
            return option.resolve()
    return None


def area_from_spec(spec: str) -> tuple[str | None, str | None]:
    normal = spec.replace("@vanguard/", "vanguard/packages/").replace(".", "/")
    parts = tuple(part for part in normal.split("/") if part)
    for disposable in ("spike", "slice", "lab"):
        if disposable in parts:
            return disposable, None
    if "packages" in parts:
        index = parts.index("packages") + 1
        if index < len(parts) and parts[index] in PACKAGE_NAMES:
            package = parts[index]
            if package == "runtime" and index + 1 < len(parts) and parts[index + 1] == "governance":
                return "governance", None
            family = parts[index + 1] if package == "adapters" and index + 1 < len(parts) else None
            return package, family
    if parts and parts[0] in PACKAGE_NAMES:
        family = parts[1] if parts[0] == "adapters" and len(parts) > 1 else None
        return parts[0], family
    return None, None


def find_cycles(graph: dict[Path, set[Path]]) -> list[list[Path]]:
    state: dict[Path, int] = {}
    stack: list[Path] = []
    cycles: list[list[Path]] = []

    def visit(node: Path) -> None:
        state[node] = 1
        stack.append(node)
        for target in sorted(graph.get(node, set())):
            if state.get(target, 0) == 0:
                visit(target)
            elif state.get(target) == 1:
                start = stack.index(target)
                cycle = stack[start:] + [target]
                if cycle not in cycles:
                    cycles.append(cycle)
        stack.pop()
        state[node] = 2

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            visit(node)
    return cycles


def check(root: Path, s4_exit: bool) -> list[str]:
    errors: list[str] = []
    # S7-A-01 (VG-03 4, LT-1..LT-8): the lattice is closed. Anything sitting
    # directly under vanguard/packages/ that the ICD does not name is a build
    # failure -- directory *or* module. Closing over directories alone let a
    # top-level module ride in beside the six packages unnamed, which is how an
    # unlisted subsystem enters the tree without ever facing a boundary row.
    packages_root = root / "vanguard" / "packages"
    if packages_root.is_dir():
        for child in sorted(packages_root.iterdir()):
            if child.name in PACKAGE_NAMES or child.name in IGNORED_PARTS:
                continue
            if child.is_dir():
                kind = "package"
            elif child.suffix in SOURCE_SUFFIXES and child.name != "__init__.py":
                kind = "module"
            else:
                continue
            errors.append(
                f"unknown core {kind} {child.name!r}; ICD permits exactly: "
                + ", ".join(sorted(PACKAGE_NAMES))
            )
    files = source_files(root)
    graph: dict[Path, set[Path]] = defaultdict(set)
    for source in files:
        source_area, source_family = area_for(source, root)
        try:
            imports = imports_in(source)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        for line, spec in imports:
            if source_area == "lab":
                target_area, _ = area_from_spec(spec)
                if spec.startswith(".") or target_area:
                    errors.append(
                        f"{source.relative_to(root)}:{line}: lab/ must import nothing ({spec!r})"
                    )
                continue
            resolved = resolve_relative(source, spec)
            if resolved and resolved in files:
                # benchmarkings is a client boundary, not part of the core
                # package-cycle graph; its import allowlist is checked below.
                if source_area != "benchmarkings":
                    graph[source].add(resolved)
                target_area, target_family = area_for(resolved, root)
            else:
                target_area, target_family = area_from_spec(spec)
            rel_parts = source.relative_to(root).parts
            rel_source = source.relative_to(root).as_posix()
            # Scoped to the core packages. benchmarkings/ is a measurement
            # client governed by its own allowlist row above, not by N-06.
            if (
                spec in SUBPROCESS_MODULES
                and rel_parts[:2] == ("vanguard", "packages")
                and rel_source not in SUBPROCESS_ALLOWLIST
            ):
                if rel_parts[: len(SUBPROCESS_HOME)] != SUBPROCESS_HOME:
                    errors.append(
                        f"{rel_source}:{line}: subprocess is confined to "
                        f"vanguard/packages/adapters/sandbox/ (N-06); {spec!r} is reachable here "
                        f"without a grant. Route it through SandboxPort, or add an explicit, "
                        f"justified row to SUBPROCESS_ALLOWLIST"
                    )
                    continue
            lowered_spec = spec.lower().replace("_", "-")
            if source_area == "benchmarkings":
                # Benchmarks are measurement clients, never model adapters.  The
                # composition root is the sole permitted runtime entrypoint.
                if target_area == "runtime" and not (
                    spec == "vanguard.packages.runtime.root"
                    or spec.startswith("vanguard.packages.runtime.root.")
                ):
                    errors.append(
                        f"{source.relative_to(root)}:{line}: benchmarkings may import only runtime.root + ports ({spec!r})"
                    )
                    continue
                if target_area is not None and target_area not in {"benchmarkings", "runtime", "ports"}:
                    errors.append(
                        f"{source.relative_to(root)}:{line}: benchmarkings may import only runtime.root + ports ({spec!r})"
                    )
                    continue
            if source_area == "governance" and "model" in lowered_spec:
                errors.append(f"{source.relative_to(root)}:{line}: governance may not depend on model APIs ({spec!r})")
                continue
            if source_area in {"agency", "governance"} and "evaluator" in lowered_spec:
                errors.append(f"{source.relative_to(root)}:{line}: {source_area} may not depend on evaluator APIs ({spec!r})")
                continue
            if not target_area or target_area == source_area:
                if source_area == "adapters" and target_area == "adapters" and source_family and target_family and source_family != target_family:
                    errors.append(f"{source.relative_to(root)}:{line}: adapter family {source_family!r} imports sibling {target_family!r}")
                continue
            if target_area in {"spike", "slice"}:
                errors.append(f"{source.relative_to(root)}:{line}: imports disposable {target_area}/ via {spec!r}")
                continue
            if target_area == "lab":
                errors.append(f"{source.relative_to(root)}:{line}: lab/ must import nothing and be imported by nothing ({spec!r})")
                continue
            if source_area in {"spike", "slice"}:
                continue
            if source_area in ALLOWED and target_area not in ALLOWED[source_area]:
                errors.append(f"{source.relative_to(root)}:{line}: forbidden {source_area} -> {target_area} import via {spec!r}")

    for cycle in find_cycles(graph):
        rendered = " -> ".join(str(path.relative_to(root)) for path in cycle)
        errors.append(f"source import cycle: {rendered}")

    if s4_exit:
        for name in ("spike", "slice"):
            if (root / name).exists():
                errors.append(f"S4 exit requires {name}/ to be absent")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--s4-exit", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve() if args.root is not None else repo_root()
    errors = check(root, args.s4_exit)
    if errors:
        for error in errors:
            print(f"BOUNDARY FAIL: {error}")
        return 1
    print(f"BOUNDARY PASS: {len(source_files(root))} source files checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
