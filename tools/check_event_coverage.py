#!/usr/bin/env python3
"""E-COV: every declared event kind has a reachable emitter site (SPEC §1.2)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

from repo_paths import repo_root

# Import after repo root is on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from layer0.events.taxonomy import EMITTER_SITES, EVENT_KINDS


def _enum_member(kind: str) -> str:
    chars: list[str] = []
    for index, char in enumerate(kind):
        if char.isupper() and index and kind[index - 1].islower():
            chars.append("_")
        chars.append(char)
    return "".join(chars).upper()


def check(root: Path) -> list[str]:
    errors: list[str] = []
    missing_map = sorted(kind for kind in EVENT_KINDS if kind not in EMITTER_SITES)
    extra_map = sorted(kind for kind in EMITTER_SITES if kind not in EVENT_KINDS)
    if missing_map:
        errors.append("taxonomy kinds missing from EMITTER_SITES: " + ", ".join(missing_map))
    if extra_map:
        errors.append("EMITTER_SITES names unknown kinds: " + ", ".join(extra_map))
    for kind, rel in sorted(EMITTER_SITES.items()):
        directory = root / rel
        if not directory.is_dir():
            errors.append(f"{kind}: emitter directory {rel} is missing")
            continue
        found = False
        member = _enum_member(kind)
        needles = (f'"{kind}"', f"'{kind}'", f"EventKind.{member}")
        for path in directory.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(needle in text for needle in needles):
                found = True
                break
        if not found:
            errors.append(f"{kind}: no reachable emitter string in {rel}/")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve() if args.root is not None else repo_root()
    errors = check(root)
    if errors:
        for error in errors:
            print(f"E-COV FAIL: {error}")
        return 1
    print(f"E-COV PASS: {len(EVENT_KINDS)} kinds, 100% emitter coverage")
    return 0


if __name__ == "__main__":
    sys.exit(main())
