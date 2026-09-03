#!/usr/bin/env python3
"""
Ad-hoc: retire unauthorized Anthropic/Claude model strings from the codebase.

Default replacement policy:
    primary    -> deepseek/deepseek-v4-flash-0731
    escalation -> z-ai/glm-5.3-flash

Files skipped:
    - tools/002_LLM_API_MOCK/models.json        (whitelisted: ALL models allowed)
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

REPO = Path(__file__).resolve().parents[2]

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv",
    "dist-browser", "dist",
}
SKIP_PATH_PREFIXES = (
    "docs/03_execution/prereg/",
    "docs/03_execution/evidence/",
    "docs/_archive/",
    "vanguard/clients/studio/dist-browser/",
    "tools/002_LLM_API_MOCK/models.json",
)
# Files that only contain the *pack name* "vg-code-claude-shaped".
# They are NOT model-string references, so we leave them alone.
PACK_NAME_ONLY = (
    "test/agency/test_manifest_loader.py",
    "test/agency/test_manifest_gene_digests.py",
    "test/agency/test_reconstructions.py",
    "test/integration/test_reconstruction_packs.py",
    "test/lab/test_build.py",
    "test/lab/test_bench.py",
    "test/lab/test_preregistration.py",
    "test/tools/test_lam_importer.py",
    "vanguard/packages/agency/manifests/registry.json",
)

# (regex, replacement) pairs applied in order, on each line.
RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"anthropic/claude-3\.5-sonnet"), "deepseek/deepseek-v4-flash-0731"),
    (re.compile(r"deepseek/deepseek-v4-flash-0731"), "deepseek/deepseek-v4-flash-0731"),
    (re.compile(r"deepseek/deepseek-v4-flash-0731(?:\.\d+)?"), "deepseek/deepseek-v4-flash-0731"),
    (re.compile(r"z-ai/glm-5.3-flash(?:\.\d+)?"), "z-ai/glm-5.3-flash"),
    (re.compile(r"z-ai/glm-5.3-flash"), "z-ai/glm-5.3-flash"),
    (re.compile(r"anthropic/claude-3\.7-sonnet"), "z-ai/glm-5.3-flash"),
    (re.compile(r"z-ai/glm-5.3-flash"), "z-ai/glm-5.3-flash"),
    (re.compile(r"\bclaude-3-5-sonnet\b"), "deepseek/deepseek-v4-flash-0731"),
    (re.compile(r"\bclaude-3-opus\b"),     "z-ai/glm-5.3-flash"),
    (re.compile(r"fp_deepseekv4flash(?:_prod)?"), "fp_deepseekv4flash"),
    (re.compile(r"fp:deepseek/deepseek-v4-flash-0731"),  "fp:deepseek-v4-flash-0731"),
]


def is_skipped(rel: str) -> bool:
    if any(rel.startswith(p) for p in SKIP_PATH_PREFIXES):
        return True
    if rel in PACK_NAME_ONLY:
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
            hits = sum(len(rx.findall(text)) for rx, _ in RULES)
        else:
            hits = rewrite_file(f)
        if hits:
            total_files += 1
            total_hits += hits
            print(f"{rel}: {hits} replacement(s)")

    print(f"\nDone. {total_files} file(s) touched, {total_hits} replacement(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
