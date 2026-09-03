#!/usr/bin/env python3
"""Detect duplicated implementation surfaces (F-16).

Wave 2 enforcement: a second selector algebra, a second canonicaliser, or a
second packages ledger writer fails the gate. The live `layer0/events/selectors.py`
fork is absorb-pending until Tech Lead 2.2-A / Developer A 2.2-B — Jaccard on
that registered pair is recorded, not a merge blocker.

Planted fixtures under `--root` (no absorb-pending pair) must fail `--enforce`
and succeed `--expect-fail`.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import repo_root

# Known fork awaiting 2.2-A keep/kill then 2.2-B deletion. Not an --enforce hit.
_ABSORB_PENDING_PAIRS = (
    (
        "layer0/events/selectors.py",
        "vanguard/packages/domain/selectors/resource_selector.py",
    ),
)

_CANONICALISE_OWNERS = frozenset({
    "vanguard/packages/domain/canonicalisation/jcs.py",
    "vanguard/packages/domain/selectors/resource_selector.py",
})

_WRITER_OWNERS = frozenset({
    "vanguard/packages/runtime/ledger_emitter.py",
})

_SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", "dist", "build"}


def _token_bag(path: Path) -> frozenset[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tokens: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            tokens.append(f"def:{node.name}")
        elif isinstance(node, ast.ClassDef):
            tokens.append(f"class:{node.name}")
        elif isinstance(node, ast.Name):
            tokens.append(node.id)
    return frozenset(tokens)


def _jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def _iter_python(root: Path) -> list[Path]:
    files: list[Path] = []
    for start_name in ("layer0", "vanguard"):
        start = root / start_name
        if not start.is_dir():
            continue
        for path in start.rglob("*.py"):
            if set(path.parts) & _SKIP_DIRS:
                continue
            files.append(path)
    return files


def _rel(repo: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def scan(repo: Path) -> tuple[list[str], list[str]]:
    """Return (enforce_hits, info_lines)."""
    enforce: list[str] = []
    info: list[str] = []

    for left_rel, right_rel in _ABSORB_PENDING_PAIRS:
        left = repo / left_rel
        right = repo / right_rel
        if not left.is_file() or not right.is_file():
            info.append(f"absorb-pending pair absent: {left_rel} or {right_rel}")
            continue
        score = _jaccard(_token_bag(left), _token_bag(right))
        info.append(f"{left_rel} vs {right_rel}: token-similarity={score:.3f} (absorb-pending until 2.2-B)")
        if score >= 0.55:
            info.append(f"DUPLICATE SURFACE (absorb-pending): selector algebra fork ({left_rel}, {right_rel})")

    for path in _iter_python(repo):
        rel = _rel(repo, path)
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            enforce.append(f"{rel}: cannot parse ({exc})")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_selector_subset":
                enforce.append(
                    f"DUPLICATE SURFACE: second selector algebra ({rel}:{node.lineno} def _selector_subset)"
                )
            if isinstance(node, ast.FunctionDef) and node.name == "canonicalise":
                if rel not in _CANONICALISE_OWNERS and not rel.startswith("layer0/"):
                    enforce.append(
                        f"DUPLICATE SURFACE: second canonicaliser ({rel}:{node.lineno} def canonicalise)"
                    )
            if isinstance(node, ast.ClassDef) and node.name == "LedgerEmitter":
                if rel not in _WRITER_OWNERS and rel.startswith("vanguard/packages/"):
                    enforce.append(
                        f"DUPLICATE SURFACE: second ledger writer ({rel}:{node.lineno} class LedgerEmitter)"
                    )

    planted_pair = (
        repo / "layer0" / "fork_selectors.py",
        repo / "vanguard" / "packages" / "domain" / "fork_selectors.py",
    )
    if planted_pair[0].is_file() and planted_pair[1].is_file():
        score = _jaccard(_token_bag(planted_pair[0]), _token_bag(planted_pair[1]))
        if score >= 0.55:
            enforce.append(
                "DUPLICATE SURFACE: planted selector algebra fork "
                "(layer0/fork_selectors.py, vanguard/packages/domain/fork_selectors.py)"
            )
    return enforce, info


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Fail on a second algebra / canonicaliser / packages writer.",
    )
    parser.add_argument(
        "--expect-fail",
        action="store_true",
        help="Invert: succeed only when a planted duplicate is found.",
    )
    args = parser.parse_args()
    repo = args.root.resolve() if args.root is not None else repo_root()
    enforce, info = scan(repo)
    for line in info:
        print(f"DUPLICATION INFO: {line}")
    for line in enforce:
        print(f"DUPLICATION FAIL: {line}")

    duplicate = bool(enforce)
    if args.expect_fail:
        if duplicate:
            print("DUPLICATION PASS: planted duplicate detected")
            return 0
        print("DUPLICATION FAIL: expected a planted duplicate surface")
        return 1
    if duplicate:
        print("DUPLICATION FAIL: second implementation surface present")
        return 1
    print("DUPLICATION PASS: no forbidden duplicate surfaces detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
