#!/usr/bin/env python3
"""F-16: No duplicate kernel. AST/token-set similarity detector.

Wave 0 scope: the detector exists and runs (002 exit gate). Threshold
enforcement is Wave 2, once the second selector algebra is resolved and deleted.

What this detects
-----------------
A "second selector algebra" is any Python module in the repository that defines
a class or set of functions that duplicate the capability / resource-selector
logic already implemented in vanguard/packages/kernel/ or layer0/kernel/.

Approach: extract the normalized token multiset from each .py file, then compute
Jaccard similarity between all pairs within and across the two kernel locations.
Pairs that exceed the similarity threshold are reported. A pair that exceeds
HARD_FAIL_THRESHOLD causes a non-zero exit (build breaks). A pair between
WARN_THRESHOLD and HARD_FAIL_THRESHOLD is reported as a warning only.

Wave 2 action: lower HARD_FAIL_THRESHOLD once layer0 duplicate modules are
deleted (behavioral parity gate first).

Usage
-----
    python3 tools/check_duplication.py                  # scan default trees
    python3 tools/check_duplication.py --warn-only      # warnings, no failure
    python3 tools/check_duplication.py --show-pairs     # print all high pairs
"""

from __future__ import annotations

import argparse
import ast
import sys
import tokenize
import io
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import repo_root

# Wave 2: lower HARD_FAIL_THRESHOLD to ~0.75 once layer0 is pruned.
# Wave 0: set high enough to not break the existing known-duplicate structure.
WARN_THRESHOLD: float = 0.70      # pairs above this are reported as warnings
HARD_FAIL_THRESHOLD: float = 0.90  # pairs above this cause exit 1

# Directories whose similarity to each other we track as the primary risk.
# The known duplicate is layer0/kernel ↔ vanguard/packages/kernel.
PRIMARY_SCAN_PAIRS: list[tuple[str, str]] = [
    ("layer0/kernel", "vanguard/packages/kernel"),
    ("layer0/scheduler", "vanguard/packages/kernel"),
]

# Directories not to cross-compare internally (expected near-identical files
# are within the same tree at different stages of convergence).
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}


def _token_set(source: str) -> set[str]:
    """Return the set of non-whitespace, non-comment Python tokens."""
    tokens: set[str] = set()
    try:
        reader = io.StringIO(source).readline
        for tok in tokenize.generate_tokens(reader):
            if tok.type in (
                tokenize.COMMENT,
                tokenize.NEWLINE,
                tokenize.NL,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.ENCODING,
                tokenize.ENDMARKER,
            ):
                continue
            normalized = tok.string.strip()
            if normalized:
                tokens.add(normalized)
    except tokenize.TokenError:
        pass
    return tokens


def _ast_identifier_set(source: str) -> set[str]:
    """Return the set of top-level class and function names in the module."""
    names: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return names
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
    return names


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _collect_py_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    files: list[Path] = []
    for path in sorted(directory.rglob("*.py")):
        if set(path.parts) & SKIP_DIRS:
            continue
        files.append(path)
    return files


def _read_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _compare_trees(
    root: Path,
    dir_a: str,
    dir_b: str,
) -> list[tuple[float, Path, Path]]:
    """Compare all .py file pairs between two directories. Return (score, a, b) tuples."""
    tree_a = _collect_py_files(root / dir_a)
    tree_b = _collect_py_files(root / dir_b)

    if not tree_a or not tree_b:
        return []

    results: list[tuple[float, Path, Path]] = []
    for pa in tree_a:
        src_a = _read_safe(pa)
        tok_a = _token_set(src_a)
        for pb in tree_b:
            src_b = _read_safe(pb)
            tok_b = _token_set(src_b)
            score = jaccard(tok_a, tok_b)
            if score >= WARN_THRESHOLD:
                results.append((score, pa, pb))
    return sorted(results, key=lambda t: -t[0])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="F-16: detect duplicate selector/kernel algebras."
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Report high-similarity pairs but do not fail (exit 0).",
    )
    parser.add_argument(
        "--show-pairs",
        action="store_true",
        help="Print all pairs above WARN_THRESHOLD.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (auto-detected if omitted).",
    )
    args = parser.parse_args()

    repo = args.root.resolve() if args.root is not None else repo_root()

    hard_failures: list[tuple[float, Path, Path]] = []
    warnings: list[tuple[float, Path, Path]] = []

    for dir_a, dir_b in PRIMARY_SCAN_PAIRS:
        pairs = _compare_trees(repo, dir_a, dir_b)
        for score, pa, pb in pairs:
            rel_a = pa.relative_to(repo)
            rel_b = pb.relative_to(repo)
            if args.show_pairs or score >= HARD_FAIL_THRESHOLD:
                label = "HARD-FAIL" if score >= HARD_FAIL_THRESHOLD else "WARN"
                print(
                    f"DUPLICATION {label} ({score:.2f}): "
                    f"{rel_a} ↔ {rel_b}"
                )
            if score >= HARD_FAIL_THRESHOLD:
                hard_failures.append((score, pa, pb))
            else:
                warnings.append((score, pa, pb))

    total_pairs = len(hard_failures) + len(warnings)
    print(
        f"DUPLICATION CHECK: {total_pairs} pair(s) above {WARN_THRESHOLD:.0%} threshold "
        f"({len(hard_failures)} hard-fail, {len(warnings)} warn-only)"
    )
    print(
        f"  Hard-fail threshold: {HARD_FAIL_THRESHOLD:.0%} (Wave 2: lower to ~75% after layer0 pruning)"
    )

    if hard_failures and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
