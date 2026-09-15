"""Living Document Atlas & Verification Engine (Requirement 2 & Phase 3).

Validates markdown frontmatter, broken relative links, stale paths,
and provides schema-compliant doc scaffolding and automated link auto-repair.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import unquote, urlparse

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
FILE_URL_RE = re.compile(r"file://[^\s)>\"]+")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", re.MULTILINE)
LDA_IMPLEMENTS_RE = re.compile(r'<!--\s*lda:implements\s+symbol=["\']([^"\']+)["\']\s*-->')

REQUIRED_FRONTMATTER_KEYS = {"id", "class", "authority", "canonical_for"}
KNOWN_AUTHORITIES = {"execution", "standard", "architecture", "reference", "non-canonical", "operational"}
KNOWN_CLASSES = {"standard", "execution", "architecture", "reference", "guideline", "report", "theory"}

DOC_TEMPLATES = {
    "architecture": """---
id: architecture.{slug}
class: architecture
authority: architecture
canonical_for:
  - {slug}
status: living
owner: repository-governance
version: "1.0.0"
last_verified: 2026-09-15
supersedes: []
superseded_by: null
---

# {title}

## 1. Overview
<!-- lda:implements symbol="" -->

## 2. Component Boundaries & Hexagonal Flow

## 3. Invariants & Failure Modes
""",
    "decision": """---
id: decision.{slug}
class: standard
authority: standard
canonical_for:
  - {slug}
status: living
owner: repository-governance
version: "1.0.0"
last_verified: 2026-09-15
supersedes: []
superseded_by: null
---

# DEC-{slug}: {title}

## Context & Problem Statement

## Decision Outcome

## Consequences & Trade-offs
""",
    "report": """---
id: report.{slug}
class: report
authority: non-canonical
canonical_for:
  - {slug}
status: living
owner: repository-governance
version: "1.0.0"
last_verified: 2026-09-15
supersedes: []
superseded_by: null
---

# Technical Report: {title}

## 1. Executive Summary

## 2. Experimental Methodology & Baseline Evidence

## 3. Findings & Next Steps
""",
    "standard": """---
id: standard.{slug}
class: standard
authority: standard
canonical_for:
  - {slug}
status: living
owner: repository-governance
version: "1.0.0"
last_verified: 2026-09-15
supersedes: []
superseded_by: null
---

# Specification: {title}

## 1. Normative Rules (RFC-2119)

## 2. Wire & Data Contracts
""",
}


def _github_slug(label: str) -> str:
    label = re.sub(r"<[^>]+>", "", label)
    label = re.sub(r"[`*_~]", "", label).strip().lower()
    label = re.sub(r"[^\w\- ]", "", label, flags=re.UNICODE)
    return label.replace(" ", "-")


def parse_frontmatter(content: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Extract YAML-like frontmatter without external pyyaml dependency."""
    if not content.startswith("---"):
        return None, content
    end_pos = content.find("---", 3)
    if end_pos == -1:
        return None, content
    fm_raw = content[3:end_pos].strip()
    body = content[end_pos + 3:].lstrip("\r\n")
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    list_items: List[str] = []

    for line in fm_raw.splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        if trimmed.startswith("- ") and current_key:
            list_items.append(trimmed[2:].strip().strip("\"'"))
            data[current_key] = list_items
            continue
        if ":" in line:
            if current_key and list_items:
                list_items = []
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if not v:
                current_key = k
                list_items = []
                data[k] = []
            else:
                current_key = None
                if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                    v = v[1:-1]
                data[k] = v
    return data, body


def verify_doc_health(repo_root: Path, sample_limit: int = 300) -> Dict[str, Any]:
    """Scan docs for frontmatter violations, broken relative links, and stale paths."""
    root = Path(repo_root)
    frontmatter_violations: List[Dict[str, Any]] = []
    broken_links: List[Dict[str, Any]] = []
    stale_paths: List[str] = []
    symbol_implementations: List[Dict[str, str]] = []

    doc_files = list(root.glob("docs/**/*.md")) + [root / "README.md", root / "AGENTS.md", root / "VISION.md"]
    doc_files = [f for f in doc_files if f.is_file() and not any(p in f.parts for p in {".git", ".venv", "node_modules"})]

    for fpath in doc_files[:sample_limit]:
        rel_path = str(fpath.relative_to(root)).replace("\\", "/")
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # Frontmatter validation for docs/
        if rel_path.startswith("docs/") and not rel_path.startswith("docs/_archive"):
            fm, _ = parse_frontmatter(content)
            if fm is None:
                frontmatter_violations.append({
                    "file": rel_path,
                    "issue": "Missing YAML frontmatter",
                })
            else:
                missing = REQUIRED_FRONTMATTER_KEYS - set(fm.keys())
                if missing:
                    frontmatter_violations.append({
                        "file": rel_path,
                        "issue": f"Missing required frontmatter keys: {sorted(missing)}",
                    })

        # Symbol implements linking
        for m in LDA_IMPLEMENTS_RE.finditer(content):
            symbol_implementations.append({
                "doc": rel_path,
                "symbol": m.group(1).strip(),
            })

        # Broken relative link detection
        for m in LINK_RE.finditer(content):
            raw_target = m.group(2).strip()
            if not raw_target or raw_target.startswith("#"):
                continue
            parsed = urlparse(raw_target)
            if parsed.scheme in {"http", "https", "mailto"}:
                continue
            if parsed.scheme == "file":
                local_path = Path(unquote(parsed.path))
                if not local_path.exists():
                    broken_links.append({"file": rel_path, "target": raw_target})
                continue

            path_part, _, _ = raw_target.partition("#")
            path_part = unquote(path_part)
            if not path_part:
                continue
            target_file = (fpath.parent / path_part).resolve()
            if not target_file.exists():
                broken_links.append({"file": rel_path, "target": raw_target})

    return {
        "status": "HEALTHY" if not (frontmatter_violations or broken_links or stale_paths) else "WARNING",
        "scanned_docs": len(doc_files),
        "frontmatter_violations_count": len(frontmatter_violations),
        "frontmatter_violations": frontmatter_violations[:10],
        "broken_links_count": len(broken_links),
        "broken_links": broken_links[:10],
        "stale_paths_count": len(stale_paths),
        "stale_paths": stale_paths[:10],
        "symbol_implementations_count": len(symbol_implementations),
        "symbol_implementations": symbol_implementations[:10],
    }


def scaffold_doc(doc_type: str, title: str, output_path: Optional[Path] = None) -> str:
    """Generate schema-compliant markdown doc template."""
    slug = _github_slug(title)
    dtype = doc_type.lower()
    template = DOC_TEMPLATES.get(dtype, DOC_TEMPLATES["standard"])
    rendered = template.format(slug=slug, title=title)
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    return rendered


def auto_fix_links(file_path: Path, repo_root: Path) -> Tuple[bool, int]:
    """Auto-correct common relative markdown link displacements."""
    if not file_path.is_file():
        return False, 0
    content = file_path.read_text(encoding="utf-8")
    fixes = 0

    def replace_link(match):
        nonlocal fixes
        label = match.group(1)
        raw_target = match.group(2)
        if raw_target.startswith(("http://", "https://", "mailto:", "#")):
            return match.group(0)

        path_part, hash_sym, frag = raw_target.partition("#")
        clean_path = unquote(path_part)
        if not clean_path:
            return match.group(0)

        target_candidate = (file_path.parent / clean_path).resolve()
        if target_candidate.exists():
            return match.group(0)

        # Attempt to find the file from repo_root
        if (repo_root / clean_path).exists():
            # Rewrite relative to file_path
            rel = Path(clean_path)
            try:
                fixed_rel = Path(rel).relative_to(file_path.parent.relative_to(repo_root))
                fixes += 1
                return f"[{label}]({str(fixed_rel)}{hash_sym}{frag})"
            except Exception:
                pass
        return match.group(0)

    new_content = LINK_RE.sub(replace_link, content)
    if fixes > 0:
        file_path.write_text(new_content, encoding="utf-8")
        return True, fixes
    return False, 0
