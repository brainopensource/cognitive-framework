#!/usr/bin/env python3
"""Check repository for forbidden machine-local absolute paths and user names."""

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

# Directories and files to ignore
IGNORED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    "dist",
    "dist-browser",
    "build",
    "site",
    ".coverage",
    ".vanguard",
    ".lda",
    ".draft",
    "dev_context_logs",
}

IGNORED_FILES = {
    "check_path_hygiene.py",
    "check_markdown_links.py",
    "scan_secrets.py",
}

# Forbidden regex patterns
FORBIDDEN_PATTERNS = [
    (re.compile(r"file:///home/(?!user\b)[a-zA-Z0-9_-]+"), "forbidden machine-specific file:// URI"),
    (re.compile(r"file:///[A-Za-z]:/[a-zA-Z0-9_ -]+"), "forbidden machine-specific file:// URI"),
    (re.compile(r"/(?:home|Users|Documents and Settings)/(?!user\b)[a-zA-Z0-9_-]+/"), "forbidden machine-local user directory path"),
    (re.compile(r"[A-Za-z]:\\(?:Users|Documents and Settings)\\[a-zA-Z0-9_-]+"), "forbidden Windows machine-local user directory path"),
    (re.compile(r"\brocha\b", re.IGNORECASE), "forbidden developer username occurrence"),
]

SCANNABLE_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".md",
    ".sh",
    ".txt",
}


def check(root: Path) -> list[str]:
    errors: list[str] = []
    scanned_count = 0

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.name in IGNORED_FILES:
            continue
        if path.suffix not in SCANNABLE_EXTENSIONS and path.name not in {"justfile", "Makefile", ".env.example"}:
            continue

        scanned_count += 1
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        lines = content.splitlines()
        for idx, line in enumerate(lines, start=1):
            for pattern, reason in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    rel_path = path.relative_to(root).as_posix()
                    errors.append(f"{rel_path}:{idx}: {reason}: {line.strip()[:120]}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Check repository for forbidden machine-local absolute paths.")
    parser.add_argument("--root", type=Path, default=None)
    args = parser.parse_args()

    root = args.root.resolve() if args.root is not None else repo_root()
    errors = check(root)

    if errors:
        for error in errors:
            print(f"PATH HYGIENE FAIL: {error}")
        return 1

    print("PATH HYGIENE PASS: no machine-local paths or developer identifiers detected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
