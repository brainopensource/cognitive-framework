"""Implementation of `lda doc-scaffold` and `lda doc-lint`."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from ..core.doc_verifier import auto_fix_links, scaffold_doc, verify_doc_health


def handle_doc_scaffold(
    repo_root: Path,
    doc_type: str,
    title: str,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    rendered = scaffold_doc(doc_type, title, output_path=output_path)
    return {
        "status": "success",
        "doc_type": doc_type,
        "title": title,
        "output_path": str(output_path) if output_path else None,
        "content": rendered,
    }


def handle_doc_lint(
    repo_root: Path,
    fix: bool = False,
) -> Dict[str, Any]:
    health = verify_doc_health(repo_root)
    fixed_count = 0
    if fix:
        doc_files = list(repo_root.glob("docs/**/*.md")) + [repo_root / "README.md", repo_root / "AGENTS.md"]
        for fpath in doc_files:
            if fpath.is_file() and not any(p in fpath.parts for p in {".git", ".venv", "node_modules"}):
                _, count = auto_fix_links(fpath, repo_root)
                fixed_count += count
    health["links_auto_fixed"] = fixed_count
    return health
