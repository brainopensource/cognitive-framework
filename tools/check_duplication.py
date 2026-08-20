#!/usr/bin/env python3
"""Detect duplicated implementation surfaces (F-16).

Wave 0 ships the detector only. Threshold enforcement (--enforce) is Wave 2.
Default mode reports known duplicate pairs and exits 0 so CI can wire the gate
without blocking on the layer0 absorb path.
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import repo_root

# Known fork: layer0 copy vs packages domain algebra (F-16 risk).
_SELECTOR_PAIRS = (
    (
        "layer0/events/selectors.py",
        "vanguard/packages/domain/selectors/resource_selector.py",
    ),
)


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


def scan(repo: Path) -> list[str]:
    hits: list[str] = []
    for left_rel, right_rel in _SELECTOR_PAIRS:
        left = repo / left_rel
        right = repo / right_rel
        if not left.is_file() or not right.is_file():
            hits.append(f"missing pair member: {left_rel} or {right_rel}")
            continue
        score = _jaccard(_token_bag(left), _token_bag(right))
        hits.append(f"{left_rel} vs {right_rel}: token-similarity={score:.3f}")
        if score >= 0.55:
            hits.append(f"DUPLICATE SURFACE: selector algebra fork ({left_rel}, {right_rel})")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Wave 2: fail when duplicate surfaces exceed the detector threshold.",
    )
    args = parser.parse_args()
    repo = args.root.resolve() if args.root is not None else repo_root()
    hits = scan(repo)
    duplicate = any(line.startswith("DUPLICATE SURFACE:") for line in hits)
    for line in hits:
        print(f"DUPLICATION {'FAIL' if line.startswith('DUPLICATE') else 'INFO'}: {line}")
    if duplicate and args.enforce:
        print("DUPLICATION FAIL: second selector algebra present — absorb or delete fork")
        return 1
    if duplicate:
        print("DUPLICATION PASS (detector): fork recorded; enforcement deferred to Wave 2")
        return 0
    print("DUPLICATION PASS: no registered duplicate surfaces detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
