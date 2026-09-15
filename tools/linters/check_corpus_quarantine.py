#!/usr/bin/env python3
"""Q-01 metadata and admission linter for corpus quarantine."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Any


_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
_ROOT_CANDIDATE = _TOOLS.parents[1]
for _p in (_COMMON, _TOOLS, _ROOT_CANDIDATE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import repo_root

from benchmarks.ladder.quarantine import (
    EXPECTED_HOLDOUT_STRATA,
    HOLD_OUT_UNACCEPTED,
    ROLE_HOLDOUT,
    load_registry,
    validate_registry_document,
)

LOADER_NAMES = frozenset({
    "materialize_scratch_workspace",
    "setup_workspace",
    "load_challenge",
    "trace_to_scenario",
    "execute_product",
    "resolve_task_set",
    "write_control_report",
    "upsert_scenario",
    "materialize",
})
GUARD_NAMES = frozenset({
    "guard_materialization",
    "guard_capture",
    "guard_export",
    "guard_product_execution",
    "refuse_unfrozen_scoring",
})
SKIP_PARTS = frozenset({
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".draft",
    ".lda",
    ".generated",
    "dev_context_logs",
    ".cache",
    ".bun",
})
SKIP_FILES = frozenset({
    "benchmarks/ladder/quarantine.py",
    "tools/linters/check_corpus_quarantine.py",
})
SCAN_ROOTS = (
    "benchmarks",
    "tools/002_LLM_API_MOCK",
    "tools/telemetry",
    "vanguard/packages/runtime",
)


def _rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _function_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    if isinstance(node, ast.Name):
        names.add(node.id)
    elif isinstance(node, ast.Attribute):
        names.add(node.attr)
    return names


def discover_loaders(root: Path) -> set[str]:
    found: set[str] = set()
    for rel_root in SCAN_ROOTS:
        base = root / rel_root
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            rel = _rel(root, path)
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            if rel in SKIP_FILES:
                continue
            if rel.startswith("test/"):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
            except (OSError, SyntaxError):
                continue
            names: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    names |= _function_names(node.func)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(node.name)
            if names & LOADER_NAMES:
                found.add(rel)
    return found


def _file_calls(root: Path, rel: str) -> set[str]:
    path = root / rel
    if not path.is_file():
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
    except (OSError, SyntaxError):
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            names |= _function_names(node.func)
    return names


def check_entrypoints(root: Path, registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    declared = registry.get("entrypoints")
    if not isinstance(declared, list):
        return ["missing entrypoint inventory"]
    declared_paths: dict[str, dict[str, Any]] = {}
    for item in declared:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append("malformed entrypoint row")
            continue
        declared_paths[item["path"]] = item
    discovered = discover_loaders(root)
    uncovered = sorted(discovered - set(declared_paths))
    for path in uncovered:
        errors.append(f"uncovered loader {path}")
    for path, row in declared_paths.items():
        if not (root / path).is_file():
            errors.append(f"inventoried entrypoint missing {path}")
            continue
        kind = row.get("guard")
        if kind == "required":
            calls = _file_calls(root, path)
            if not (calls & GUARD_NAMES):
                errors.append(f"unguarded loader {path}")
    return errors


def check_metadata(
    root: Path,
    *,
    registry_path: Path | None = None,
    scan_entrypoints: bool = True,
) -> list[str]:
    target = registry_path or (root / "benchmarks" / "ladder" / "corpus_registry.json")
    try:
        registry = load_registry(target)
    except Exception as exc:
        return [f"registry load failed: {exc}"]
    errors = validate_registry_document(registry)
    if registry.get("holdout_admission") == "ACCEPTED":
        holdout = [row for row in registry.get("members") or [] if isinstance(row, dict) and row.get("role") == ROLE_HOLDOUT]
        if not holdout:
            errors.append("cannot report corpus acceptance without HOLDOUT members")
    if scan_entrypoints:
        errors.extend(check_entrypoints(root, registry))
    control_path = root / "benchmarks" / "ladder" / "control_preregistration.json"
    if control_path.is_file():
        try:
            control = json.loads(control_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"unreadable control preregistration: {exc}")
        else:
            if control.get("status") != "FROZEN":
                runner = root / "benchmarks" / "agentic_harness_matrix_benchmark.py"
                if runner.is_file() and "refuse_unfrozen_scoring" not in runner.read_text(encoding="utf-8"):
                    errors.append("unfrozen scoring is unguarded")
    return errors


def check_admission(
    root: Path,
    *,
    registry_path: Path | None = None,
    scan_entrypoints: bool = True,
) -> list[str]:
    errors = check_metadata(
        root,
        registry_path=registry_path,
        scan_entrypoints=scan_entrypoints,
    )
    target = registry_path or (root / "benchmarks" / "ladder" / "corpus_registry.json")
    try:
        registry = load_registry(target)
    except Exception:
        return errors
    holdout = [
        row for row in registry.get("members") or []
        if isinstance(row, dict) and row.get("role") == ROLE_HOLDOUT
    ]
    if not holdout:
        return errors
    if len(holdout) != 30:
        errors.append(f"holdout count must be exactly 30, got {len(holdout)}")
    strata: dict[str, int] = {}
    for row in holdout:
        stratum = str(row.get("stratum") or "")
        strata[stratum] = strata.get(stratum, 0) + 1
    if strata != EXPECTED_HOLDOUT_STRATA:
        errors.append(f"holdout strata mismatch {strata}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Q-01 corpus quarantine linter")
    parser.add_argument("--metadata", action="store_true")
    parser.add_argument("--admission", action="store_true")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--registry", type=Path, default=None)
    args = parser.parse_args(argv)
    if not args.metadata and not args.admission:
        parser.error("specify --metadata and/or --admission")
    root = args.root.resolve() if args.root is not None else repo_root()
    registry_path = args.registry
    if args.admission:
        errors = check_admission(root, registry_path=registry_path)
        label = "ADMISSION"
    else:
        errors = check_metadata(root, registry_path=registry_path)
        label = "METADATA"
    if errors:
        for error in errors:
            print(f"CORPUS QUARANTINE {label} FAIL: {error}")
        return 1
    if args.admission:
        target = registry_path or (root / "benchmarks" / "ladder" / "corpus_registry.json")
        registry = load_registry(target)
        holdout = [
            row for row in registry.get("members") or []
            if isinstance(row, dict) and row.get("role") == ROLE_HOLDOUT
        ]
        if not holdout or registry.get("holdout_admission") == HOLD_OUT_UNACCEPTED:
            print("CORPUS QUARANTINE ADMISSION: HOLDOUT UNACCEPTED")
            return 0
    print(f"CORPUS QUARANTINE {label} PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
