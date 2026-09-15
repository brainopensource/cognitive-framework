#!/usr/bin/env python3
"""I-7: Domain-blind kernel. Whole-word coding|pytest|ast are forbidden.

Scans three trees (F-18, ADR-0075):
  - layer0/                            (original scope)
  - vanguard/packages/domain/          (I-7 also covers packages domain)
  - vanguard/packages/kernel/          (I-7 also covers packages kernel)

Wave 0 extension: the linter previously scanned only layer0/, which is narrower
than Invariant I-7 as stated in SPEC. This change makes the enforcement scope
match the invariant's stated coverage.

Domain filesystem I/O is a hexagonal-purity rule (not I-7). The detector and
DOMAIN_IO_ALLOWLIST live in check_boundaries.py as the single source of truth;
this linter reuses find_domain_io so I/O-in-domain fails here as well.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import repo_root
from check_boundaries import find_domain_io

# Word boundaries so `dataclass` / `last` are not false positives of `ast`.
_FORBIDDEN = re.compile(r"\b(coding|pytest|ast)\b")
_SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}


def scan(root: Path) -> list[str]:
    hits: list[str] = []
    if not root.is_dir():
        return [f"missing layer0 directory: {root}"]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".py", ".md", ".json", ".yaml", ".yml"}:
            continue
        if set(path.parts) & _SKIP_DIRS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            hits.append(f"{path}: {exc}")
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            match = _FORBIDDEN.search(line)
            if match:
                rel = path
                hits.append(f"{rel}:{lineno}: forbidden domain token {match.group(1)!r}")
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--expect-fail",
        action="store_true",
        help="Invert: succeed only when a planted leak is found (fixture proof).",
    )
    args = parser.parse_args()
    repo = args.root.resolve() if args.root is not None else repo_root()

    # F-18 (ADR-0075): scan all three I-7 scopes, not just layer0/.
    scan_targets = [
        ("layer0/", repo / "layer0"),
        ("vanguard/packages/domain/", repo / "vanguard" / "packages" / "domain"),
        ("vanguard/packages/kernel/", repo / "vanguard" / "packages" / "kernel"),
    ]

    all_hits: list[str] = []
    missing: list[str] = []
    for label, target in scan_targets:
        if not target.is_dir():
            missing.append(label)
            continue
        all_hits.extend(scan(target))

    if args.expect_fail:
        if all_hits:
            print(f"DOMAIN-BLINDNESS FIXTURE FAIL-CLOSED: {len(all_hits)} planted hit(s)")
            return 0
        print("DOMAIN-BLINDNESS FIXTURE MISS: expected a leak, found none")
        return 1

    if missing:
        for m in missing:
            print(f"DOMAIN-BLINDNESS WARN: scan target missing (not an error): {m}")

    io_hits = find_domain_io(repo)
    all_hits.extend(io_hits)

    if all_hits:
        for hit in all_hits:
            print(f"DOMAIN-BLINDNESS FAIL: {hit}")
        return 1

    scanned = ", ".join(label for label, t in scan_targets if t.is_dir())
    print(f"DOMAIN-BLINDNESS PASS: no coding|pytest|ast tokens in {scanned}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
