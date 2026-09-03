#!/usr/bin/env python3
"""Measure the policy-kernel source inventory and alarm on unreviewed growth."""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import kernel_tcb_budget, repo_root


def logical_lines(path: Path) -> int:
    """Count stable physical logic lines; blanks and comment-only lines do not count."""

    return sum(
        bool(line.strip()) and not line.lstrip().startswith("#")
        for line in path.read_text(encoding="utf-8").splitlines()
    )


def _module_name(path: Path, root: Path) -> str:
    relative = path.relative_to(root).with_suffix("")
    return "vanguard.packages." + ".".join(relative.parts)


def _module_path(module: str, root: Path) -> Path | None:
    path = root.joinpath(*module.split("."))
    candidate = path.with_suffix(".py")
    if candidate.exists():
        return candidate
    init = path / "__init__.py"
    return init if init.exists() else None


def _internal_imports(path: Path, root: Path) -> set[Path]:
    module = _module_name(path, root)
    package = module.rsplit(".", 1)[0] if "." in module else module
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return set()
    found: set[Path] = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = importlib.util.resolve_name("." * node.level + (node.module or ""), package)
                names = [base]
                names.extend(f"{base}.{alias.name}" for alias in node.names if alias.name != "*")
            elif node.module:
                names = [node.module]
                names.extend(f"{node.module}.{alias.name}" for alias in node.names if alias.name != "*")
        for name in names:
            if not name.startswith("vanguard.packages."):
                continue
            candidate = _module_path(name, root.parent.parent)
            if candidate is not None:
                found.add(candidate)
    return found


def trusted_closure(root: Path, source_root: Path) -> list[Path]:
    """Discover the executable in-repository import closure from Kernel."""

    queue = list(sorted(source_root.glob("*.py")))
    seen: set[Path] = set(queue)
    package_root = root / "vanguard" / "packages"
    while queue:
        current = queue.pop(0)
        for imported in _internal_imports(current, package_root):
            if imported.is_relative_to(package_root) and imported not in seen:
                seen.add(imported)
                queue.append(imported)
    return sorted(seen)


def _public_contract_count(kernel_root: Path) -> int:
    try:
        tree = ast.parse((kernel_root / "__init__.py").read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "__all__"
                for target in node.targets
            ):
                value = ast.literal_eval(node.value)
                return len(value) if isinstance(value, (list, tuple)) else 0
    except (OSError, SyntaxError, ValueError):
        pass
    return 0


def _privileged_operation_count(root: Path) -> int:
    path = root / "vanguard" / "packages" / "runtime" / "ledger_emitter.py"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name) and target.id == "PRIVILEGED_KIND_OWNERS":
                        if isinstance(node.value, ast.Dict):
                            return len(node.value.keys)
                        value = ast.literal_eval(node.value)
                        return len(value) if isinstance(value, dict) else 0
    except (OSError, SyntaxError, ValueError):
        pass
    return 0


def rf97_v2(root: Path, source_root: Path) -> int:
    closure = trusted_closure(root, source_root)
    inventory = {str(path.relative_to(root)): logical_lines(path) for path in closure}
    identifiers: set[str] = set()
    imported_modules: set[str] = set()
    for path in closure:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError:
            continue
        identifiers.update(node.id for node in ast.walk(tree) if isinstance(node, ast.Name))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_modules.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module)
    forbidden_domain = sorted(identifiers & {
        "coding", "research", "pytest", "agent_view", "reproducibility",
        "trajectory", "skills", "memory",
    })
    extension_imports = sorted({
        segment
        for module in imported_modules
        for segment in ("adapters", "agency", "runtime", "packs")
        if segment in module.split(".")
    })
    dependency_names = sorted({
        "domain" if "/domain/" in path else "ports" if "/ports/" in path else "kernel"
        for path in inventory
    })
    receipt = {
        "rf": "RF-97",
        "version": 2,
        "closure": sorted(inventory),
        "logical_loc": inventory,
        "public_contracts": _public_contract_count(root / "vanguard" / "packages" / "kernel"),
        "privileged_ops": _privileged_operation_count(root),
        "dependencies": {"stdlib": True, "internal": dependency_names},
        "domain_concepts": forbidden_domain,
        "extension_knowledge": extension_imports,
        "change_amplification": sum(
            1 for path in (root / "vanguard" / "packages").rglob("*.py")
            if path not in closure and any(
                module in path.read_text(encoding="utf-8")
                for module in ("vanguard.packages.kernel", "..kernel", "..kernel.")
            )
        ),
    }
    print(json.dumps(receipt, sort_keys=True))
    if forbidden_domain or extension_imports:
        print("RF-97 FAIL: trusted closure contains domain or extension knowledge")
        return 1
    print(f"RF-97 PASS: trusted closure contains {len(closure)} executable files")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--budget", type=Path, default=None)
    parser.add_argument("--v2", action="store_true", help="run the transitive RF-97 closure gate")
    args = parser.parse_args()
    root = args.root.resolve() if args.root is not None else repo_root()
    if args.budget is None:
        budget_path = kernel_tcb_budget()
    else:
        budget_path = args.budget if args.budget.is_absolute() else root / args.budget
    if not budget_path.exists() and (root / "docs/agile/sprint2/kernel-tcb-budget.json").exists():
        budget_path = root / "docs/agile/sprint2/kernel-tcb-budget.json"

    try:
        budget = json.loads(budget_path.read_text(encoding="utf-8"))
        source_root = root / budget["source_root"]
        baseline = int(budget["baseline_logical_loc"])
        alarm_delta = int(budget["alarm_delta_lines"])
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"TCB FAIL: invalid budget: {exc}")
        return 2

    if args.v2:
        return rf97_v2(root, source_root)

    files = sorted(source_root.glob("*.py"))
    if not files:
        print(f"TCB FAIL: no kernel sources under {source_root}")
        return 2
    inventory = {str(path.relative_to(root)): logical_lines(path) for path in files}
    current = sum(inventory.values())
    threshold = baseline + alarm_delta
    receipt = {
        "alarm_delta_lines": alarm_delta,
        "baseline_logical_loc": baseline,
        "current_logical_loc": current,
        "files": inventory,
        "threshold": threshold,
    }
    print(json.dumps(receipt, sort_keys=True))
    if current > threshold:
        print(f"TCB ALARM: kernel grew to {current} logical lines; reviewed threshold is {threshold}")
        return 1
    print(f"TCB PASS: {current} logical lines across {len(files)} files (alarm above {threshold})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
