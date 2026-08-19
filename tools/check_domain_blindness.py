#!/usr/bin/env python3
"""I-7: Layer-0 is domain-blind. Whole-word coding|pytest|ast are forbidden."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import repo_root

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
    layer0 = repo / "layer0"
    hits = scan(layer0)
    if args.expect_fail:
        if hits:
            print(f"DOMAIN-BLINDNESS FIXTURE FAIL-CLOSED: {len(hits)} planted hit(s)")
            return 0
        print("DOMAIN-BLINDNESS FIXTURE MISS: expected a leak, found none")
        return 1
    if hits:
        for hit in hits:
            print(f"DOMAIN-BLINDNESS FAIL: {hit}")
        return 1
    print("DOMAIN-BLINDNESS PASS: no coding|pytest|ast tokens in layer0/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
