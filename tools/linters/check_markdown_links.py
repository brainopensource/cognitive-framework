#!/usr/bin/env python3
"""Verify local Markdown links resolve from the repository root layout."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import repo_root

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
FILE_URL = re.compile(r"file://[^\s)>\"]+")

SKIP_PARTS = {".git", "node_modules", ".venv", "__pycache__"}
DOC_GLOBS = (
    "README.md",
    "AGENTS.md",
    "docs/**/*.md",
    "vanguard/**/*.md",
)


def _skip(path: Path) -> bool:
    return bool(set(path.parts) & SKIP_PARTS)


def extract_targets(text: str) -> list[str]:
    targets = [match.group(1).strip() for match in LINK.finditer(text)]
    targets.extend(FILE_URL.findall(text))
    return targets


def resolve_target(source: Path, raw: str, root: Path) -> Path | None:
    target = raw.split()[0].strip("<>")
    if not target or target.startswith("#"):
        return None
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "mailto"}:
        return None
    if parsed.scheme == "file":
        local = Path(unquote(parsed.path))
        # Windows/WSL file URLs may include /home/... which is the live tree.
        return local
    path_part, _, _frag = target.partition("#")
    path_part = unquote(path_part)
    if not path_part:
        return None
    candidate = (source.parent / path_part).resolve()
    return candidate


def check(root: Path) -> list[str]:
    errors: list[str] = []
    files: list[Path] = []
    for pattern in DOC_GLOBS:
        files.extend(p for p in root.glob(pattern) if p.is_file() and not _skip(p))
    files = sorted(set(files))
    if not files:
        return [f"no markdown files under {root}"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        for raw in extract_targets(text):
            resolved = resolve_target(path, raw, root)
            if resolved is None:
                continue
            if not resolved.exists():
                rel = path.relative_to(root) if path.is_relative_to(root) else path
                errors.append(f"{rel}: broken local link {raw!r} -> {resolved}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan every markdown file under docs/, cv13/, schemas/v4/ and package READMEs.",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root is not None else repo_root()
    if args.all:
        global DOC_GLOBS
        DOC_GLOBS = (
            "README.md",
            "docs/**/*.md",
            "cv13/**/*.md",
            "schemas/v4/**/*.md",
            "vanguard/**/*.md",
        )
    errors = check(root)
    if errors:
        for error in errors:
            print(f"LINK FAIL: {error}")
        return 1
    print("LINK PASS: local markdown links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
