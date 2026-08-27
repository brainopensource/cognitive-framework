#!/usr/bin/env python3
"""
Ad-hoc: retire unauthorized `openai/*` model strings (except `openai/gpt-5.6-luna`)
and rewrite `deepseek/deepseek-v4-flash-0731` to `deepseek/deepseek-v4-flash-0731`.

Replacement policy:
    openai/*  (NOT openai/gpt-5.6-luna) -> deepseek/deepseek-v4-flash-0731
    deepseek/deepseek-v4-flash-0731             -> deepseek/deepseek-v4-flash-0731
    openai/gpt-5.6-luna                -> KEPT AS-IS (explicit exception)

Files skipped:
    - tools/002_LLM_API_MOCK/models.json        (whitelisted: ALL models allowed)
    - tools/002_LLM_API_MOCK/runs/**            (immutable run artifacts)
    - tools/002_LLM_API_MOCK/live_captures/**   (immutable capture artifacts)
    - tools/001_LLM_API_ROUTER/outputs/**       (immutable router outputs)
    - tools/001_LLM_API_ROUTER/docs/**          (immutable router docs)
    - vanguard/packages/adapters/models/models_registry.json  (canonical registry; values must stay)
    - test/broken/**                            (intentional linter-fail fixtures)
    - docs/03_execution/prereg/**               (append-only ADR/prereg records)
    - docs/03_execution/evidence/**             (immutable evidence artifacts)
    - docs/_archive/**                          (archived; never edited)
    - vanguard/clients/studio/dist-browser/**   (built bundle; rebuild instead)
    - .git, node_modules, __pycache__, .venv
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path("/home/rocha/Coding/Aether-D-System")

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv",
    "dist-browser", "dist", "broken",
}
SKIP_PATH_PREFIXES = (
    "docs/03_execution/prereg/",
    "docs/03_execution/evidence/",
    "docs/_archive/",
    "vanguard/clients/studio/dist-browser/",
    "tools/002_LLM_API_MOCK/models.json",
    "tools/002_LLM_API_MOCK/runs/",
    "tools/002_LLM_API_MOCK/live_captures/",
    "tools/001_LLM_API_ROUTER/outputs/",
    "tools/001_LLM_API_ROUTER/docs/",
    "vanguard/packages/adapters/models/models_registry.json",
    "test/broken/",
)
SKIP_PATH_EXACT = {
    "vanguard/packages/adapters/models/models_registry.json",
}

# `openai/gpt-5.6-luna` is the explicit keep-as-is exception. We carve it out
# with a placeholder so it survives the blanket openai/* rewrite.
#
# Pipeline order:
#   1) protect `openai/gpt-5.6-luna` tokens with a placeholder
#   2) rewrite remaining `deepseek/deepseek-v4-flash-0731` tokens to the replacement
#   3) rewrite `deepseek/deepseek-v4-flash-0731` to the replacement
#   4) restore the placeholder to the original luna string
LUNA_PLACEHOLDER = "\x00__KEEP_OPENAI_GPT_5_6_LUNA__\x00"
KEEP_AS_IS = "openai/gpt-5.6-luna"
REPLACEMENT = "deepseek/deepseek-v4-flash-0731"

RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(re.escape(KEEP_AS_IS)), LUNA_PLACEHOLDER),
    (re.compile(r"openai/[A-Za-z0-9._:\-]+"), REPLACEMENT),
    (re.compile(r"deepseek/deepseek-v4-flash-0731(?:-v3(?:\.[0-9]+)?)?"), REPLACEMENT),
    (re.compile(re.escape(LUNA_PLACEHOLDER)), KEEP_AS_IS),
]


def is_skipped(rel: str) -> bool:
    if rel in SKIP_PATH_EXACT:
        return True
    if any(rel.startswith(p) for p in SKIP_PATH_PREFIXES):
        return True
    return any(part in SKIP_DIRS for part in Path(rel).parts)


def rewrite_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    new_lines: list[str] = []
    hits = 0
    for line in text.splitlines(keepends=True):
        for rx, repl in RULES:
            line, n = rx.subn(repl, line)
            hits += n
        new_lines.append(line)
    if hits:
        path.write_text("".join(new_lines), encoding="utf-8")
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="report only, no writes")
    ap.add_argument("--paths", nargs="*", default=None,
                    help="restrict to these repo-relative paths (default: whole repo)")
    args = ap.parse_args()

    targets: list[Path]
    if args.paths:
        targets = [REPO / p for p in args.paths]
    else:
        targets = [p for p in REPO.rglob("*") if p.is_file()]

    total_files = total_hits = 0
    for f in targets:
        try:
            rel = f.relative_to(REPO).as_posix()
        except ValueError:
            continue
        if is_skipped(rel):
            continue
        if f.suffix not in {".py", ".ts", ".tsx", ".js", ".json", ".md", ".sh", ".yaml", ".yml", ".toml"}:
            continue
        if args.dry_run:
            text = f.read_text(encoding="utf-8", errors="replace")
            sim = text
            for rx, repl in RULES:
                sim, _ = rx.subn(repl, sim)
            hits = 0
            for line_a, line_b in zip(text.splitlines(keepends=True), sim.splitlines(keepends=True)):
                if line_a != line_b:
                    hits += 1
        else:
            hits = rewrite_file(f)
        if hits:
            total_files += 1
            total_hits += hits
            print(f"{rel}: {hits} line(s) changed")

    print(f"\nDone. {total_files} file(s) touched, {total_hits} line(s) changed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
