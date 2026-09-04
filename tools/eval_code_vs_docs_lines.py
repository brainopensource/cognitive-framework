#!/usr/bin/env python3
"""Evaluate lines of code in Vanguard packages vs markdown documentation lines.

Computes physical lines, non-empty lines, and file counts across:
1. Vanguard hexagonal packages (vanguard/packages/{domain, ports, kernel, agency, runtime, adapters, apps})
2. Client implementations (vanguard/clients/)
3. Documentation tiers (canonical architecture/runway vs non-canonical research/reports)
4. Top-level constitutional docs (VISION.md, AGENTS.md, README.md, docs/README.md)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parents[1]


class Stats(NamedTuple):
    files: int
    total_lines: int
    code_lines: int  # non-blank


def count_file(path: Path) -> tuple[int, int]:
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0, 0
    lines = content.splitlines()
    total = len(lines)
    non_blank = sum(1 for line in lines if line.strip())
    return total, non_blank


def count_directory(dir_path: Path, extensions: tuple[str, ...]) -> Stats:
    if not dir_path.is_dir():
        return Stats(0, 0, 0)

    total_files = 0
    total_lines = 0
    code_lines = 0

    for root, _, files in os.walk(dir_path):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                p = Path(root) / file
                t, c = count_file(p)
                total_files += 1
                total_lines += t
                code_lines += c

    return Stats(total_files, total_lines, code_lines)


def main() -> None:
    pkg_root = ROOT / "vanguard" / "packages"
    vanguard_subsystems = [
        "domain",
        "ports",
        "kernel",
        "agency",
        "runtime",
        "adapters",
        "apps",
    ]

    print("=" * 80)
    print("VANGUARD PRODUCTION LATTICE (vanguard/packages/) - PYTHON LOC")
    print("=" * 80)
    print(f"{'Subsystem':<20} | {'Files':>8} | {'Total Lines':>12} | {'Non-Blank Lines':>16}")
    print("-" * 80)

    total_pkg_files = 0
    total_pkg_lines = 0
    total_pkg_nonblank = 0

    for sub in vanguard_subsystems:
        st = count_directory(pkg_root / sub, (".py",))
        total_pkg_files += st.files
        total_pkg_lines += st.total_lines
        total_pkg_nonblank += st.code_lines
        print(f"{sub:<20} | {st.files:>8} | {st.total_lines:>12,d} | {st.code_lines:>16,d}")

    print("-" * 80)
    print(f"{'TOTAL VANGUARD PKGS':<20} | {total_pkg_files:>8} | {total_pkg_lines:>12,d} | {total_pkg_nonblank:>16,d}")
    print()

    # Client Code (excluding node_modules)
    cli_root = ROOT / "vanguard" / "clients"
    total_cli_files = 0
    total_cli_lines = 0
    total_cli_nonblank = 0
    for root, _, files in os.walk(cli_root):
        if "node_modules" in root or ".next" in root or "dist" in root:
            continue
        for file in files:
            if file.endswith((".ts", ".tsx", ".js", ".jsx")):
                p = Path(root) / file
                t, c = count_file(p)
                total_cli_files += 1
                total_cli_lines += t
                total_cli_nonblank += c

    print("=" * 80)
    print("VANGUARD CLIENTS (vanguard/clients/ src without node_modules)")
    print("=" * 80)
    print(f"{'Component':<20} | {'Files':>8} | {'Total Lines':>12} | {'Non-Blank Lines':>16}")
    print("-" * 80)
    print(f"{'clients (ts/tsx)':<20} | {total_cli_files:>8} | {total_cli_lines:>12,d} | {total_cli_nonblank:>16,d}")
    print()

    # Documentation
    docs_root = ROOT / "docs"
    canonical_sections = [
        ("docs/architecture", docs_root / "architecture"),
        ("docs/backend", docs_root / "backend"),
        ("docs/execution", docs_root / "execution"),
        ("docs/product", docs_root / "product"),
        ("docs/frontend", docs_root / "frontend"),
    ]

    non_canonical_sections = [
        ("docs/theory", docs_root / "theory"),
        ("docs/reports", docs_root / "reports"),
        ("docs/research", docs_root / "research"),
        ("docs/onboarding", docs_root / "onboarding"),
    ]

    print("=" * 80)
    print("DOCUMENTATION ARCHITECTURE (docs/) - MARKDOWN LINES")
    print("=" * 80)
    print(f"{'Doc Tier':<25} | {'Files':>8} | {'Total Lines':>12} | {'Non-Blank Lines':>16}")
    print("-" * 80)

    # 1. Constitutional Entrypoints
    root_docs = ["VISION.md", "AGENTS.md", "README.md", "docs/README.md"]
    c_files, c_lines, c_nonblank = 0, 0, 0
    for rf in root_docs:
        t, c = count_file(ROOT / rf)
        c_files += 1
        c_lines += t
        c_nonblank += c
        print(f"Constitutional: {rf:<9} | {1:>8} | {t:>12,d} | {c:>16,d}")

    # 2. Canonical Architecture & Runway
    can_files, can_lines, can_nonblank = 0, 0, 0
    for name, p in canonical_sections:
        st = count_directory(p, (".md", ".MD"))
        can_files += st.files
        can_lines += st.total_lines
        can_nonblank += st.code_lines
        print(f"Canonical: {name:<14} | {st.files:>8} | {st.total_lines:>12,d} | {st.code_lines:>16,d}")

    subtotal_can_files = c_files + can_files
    subtotal_can_lines = c_lines + can_lines
    subtotal_can_nonblank = c_nonblank + can_nonblank
    print("-" * 80)
    print(f"{'SUBTOTAL CANONICAL DOCS':<25} | {subtotal_can_files:>8} | {subtotal_can_lines:>12,d} | {subtotal_can_nonblank:>16,d}")
    print("-" * 80)

    # 3. Non-Canonical (Research, Labs, Reports)
    non_files, non_lines, non_nonblank = 0, 0, 0
    for name, p in non_canonical_sections:
        st = count_directory(p, (".md", ".MD"))
        non_files += st.files
        non_lines += st.total_lines
        non_nonblank += st.code_lines
        print(f"Non-canon: {name:<14} | {st.files:>8} | {st.total_lines:>12,d} | {st.code_lines:>16,d}")

    total_doc_files = subtotal_can_files + non_files
    total_doc_lines = subtotal_can_lines + non_lines
    total_doc_nonblank = subtotal_can_nonblank + non_nonblank

    print("-" * 80)
    print(f"{'TOTAL ALL DOCS':<25} | {total_doc_files:>8} | {total_doc_lines:>12,d} | {total_doc_nonblank:>16,d}")
    print()

    print("=" * 80)
    print("COMPARATIVE EVALUATION & RATIOS")
    print("=" * 80)
    can_ratio = subtotal_can_nonblank / total_pkg_nonblank if total_pkg_nonblank else 0
    total_ratio = total_doc_nonblank / total_pkg_nonblank if total_pkg_nonblank else 0
    print(f"Production Code (Vanguard Packages): {total_pkg_nonblank:>10,d} non-blank LOC ({total_pkg_files} files)")
    print(f"Canonical Docs (Spec + Arch + Runway): {subtotal_can_nonblank:>10,d} non-blank lines ({subtotal_can_files} files)")
    print(f"Non-Canonical Docs (Research/Reports): {non_nonblank:>10,d} non-blank lines ({non_files} files)")
    print()
    print(f"Canonical Docs-to-Code Ratio:        {can_ratio:>10.2f}x (1 line of active docs per ~{1/can_ratio:.1f} lines of code)")
    print(f"Total Docs-to-Code Ratio:            {total_ratio:>10.2f}x (including exploratory research/historical audits)")
    print("=" * 80)


if __name__ == "__main__":
    main()
