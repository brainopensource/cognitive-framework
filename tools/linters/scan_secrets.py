#!/usr/bin/env python3
"""Blocking secret scanner for diff, tree, refs and built artifacts (S6B-SEC-002).

Never prints secret values. Match names and paths only.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_TOOLS = Path(__file__).resolve().parent
_COMMON = _TOOLS.parent / "common"
for _p in (_COMMON, _TOOLS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from repo_paths import repo_root

# Synthetic tokens used only in broken fixtures. Real key material is never listed here.
FAKE_ALLOWLIST = {
    "vg_fake_secret_DO_NOT_USE_000000000000",
}

RULES = (
    ("openrouter-key-assignment", re.compile(r"OPENROUTER_API_KEY\s*=\s*['\"]?(sk-|or-)")),
    ("generic-sk-live", re.compile(r"sk-or-v1-[A-Za-z0-9]{16,}")),
    # A bare PEM header carries no key material; security prose quotes it constantly.
    # Real key material always has a base64 body on the following line, so require one.
    ("pem-private-key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----\s*\r?\n[A-Za-z0-9+/=]{32,}")),
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
)

SKIP_PARTS = {".git", "node_modules", ".venv", "__pycache__"}
TEXT_SUFFIXES = {
    ".py", ".md", ".json", ".yml", ".yaml", ".ts", ".tsx", ".js", ".env", ".txt", ".toml",
    ".sh", ".csv", ".tsv", ".example",
}


def iter_tree_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if set(path.parts) & SKIP_PARTS:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {".env", "env"}:
            continue
        files.append(path)
    return files


def scan_text(label: str, text: str) -> list[str]:
    hits: list[str] = []
    for name, pattern in RULES:
        for match in pattern.finditer(text):
            snippet = match.group(0)
            if any(fake in snippet for fake in FAKE_ALLOWLIST) and "fixtures" in label:
                continue
            hits.append(f"{label}: rule {name}")
            break
    return hits


def scan_tree(root: Path) -> list[str]:
    hits: list[str] = []
    for path in iter_tree_files(root):
        rel = path.relative_to(root)
        rel_s = str(rel).replace("\\", "/")
        if path.name == ".env" and path.resolve() == (repo_root() / ".env").resolve():
            tracked = subprocess.run(
                ["git", "ls-files", "--error-unmatch", ".env"],
                cwd=repo_root(),
                text=True,
                capture_output=True,
                check=False,
            )
            if tracked.returncode == 0:
                hits.append(".env: tracked .env is forbidden")
            continue
        if "test/broken/fixtures/secrets" in rel_s or "test/broken/fixtures/secret_leak" in rel_s:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits.extend(scan_text(rel_s, text))
    return hits


def scan_git_diff(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--unified=0"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return scan_text("git-diff-cached", result.stdout)


def scan_all_refs(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "rev-list", "--objects", "--all"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return [f"git-rev-list failed with exit {result.returncode}"]
    # Names only: blob paths that look like env files in history.
    hits: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split(" ", 1)
        if len(parts) != 2:
            continue
        name = parts[1]
        if name.endswith(".env") and name not in {".env.example"}:
            hits.append(f"reachable-object: env-named blob {name}")
    return hits


def scan_artifacts(path: Path) -> list[str]:
    if not path.exists():
        return []
    hits: list[str] = []
    for artifact in path.rglob("*"):
        if artifact.is_file():
            try:
                text = artifact.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            hits.extend(scan_text(str(artifact), text))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-refs", action="store_true")
    parser.add_argument("--artifacts", type=Path, default=None)
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--allow-fake-fixture", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve() if args.root else repo_root()
    hits = scan_tree(root)
    hits.extend(scan_git_diff(root))
    if args.all_refs:
        hits.extend(scan_all_refs(root))
    if args.artifacts:
        hits.extend(scan_artifacts(args.artifacts if args.artifacts.is_absolute() else root / args.artifacts))
    unique = sorted(set(hits))
    if unique:
        for hit in unique:
            print(f"SECRET SCAN FAIL: {hit}")
        return 1
    print("SECRET SCAN PASS: no blocking secret patterns in scanned surfaces")
    return 0


if __name__ == "__main__":
    sys.exit(main())
