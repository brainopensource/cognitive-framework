"""Filesystem and repository file discovery provider."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.ir import ConfidenceTier, EntityKind, IREntity, Provenance, SourceLocation
from ..core.models import Entity, ProviderResult
from .base import BaseProvider


LANG_EXT_MAP = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".md": "markdown",
    ".mdx": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".sh": "bash",
    ".sql": "sql",
    ".html": "html",
    ".css": "css"
}

IGNORE_DIRS: Set[str] = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".generated", "dev_context_logs", ".pytest_cache", ".tox",
    "dist", "build", ".turbo", ".next", ".mypy_cache", ".ruff_cache",
    ".vanguard", ".docs", ".draft"
}


class FilesystemProvider(BaseProvider):
    """Discovers and hashes repository files."""

    name = "filesystem"
    confidence_tier = ConfidenceTier.STRUCTURED_DOC

    def collect(
        self,
        repo_root: Path | Any,
        incremental: bool = False,
        file_states: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> ProviderResult:
        root = repo_root.root if hasattr(repo_root, "root") else Path(repo_root)
        files_data: List[Dict[str, Any]] = []
        entities: List[Entity] = []

        for dirpath, dirnames, filenames in os.walk(root):
            # Prune ignored directories in-place
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]

            for fname in filenames:
                if fname.startswith("."):
                    continue
                fpath = Path(dirpath) / fname
                try:
                    rel_path = str(fpath.relative_to(root)).replace("\\", "/")
                    ext = fpath.suffix.lower()
                    lang = LANG_EXT_MAP.get(ext, "unknown")
                    stat = fpath.stat()
                    mtime = stat.st_mtime
                    size = stat.st_size

                    # Incremental check
                    content_hash = ""
                    if incremental and file_states and rel_path in file_states:
                        prev = file_states[rel_path]
                        if prev.get("mtime") == mtime and prev.get("size_bytes") == size:
                            content_hash = prev.get("content_hash", "")

                    if not content_hash:
                        raw = fpath.read_bytes()
                        content_hash = hashlib.sha256(raw).hexdigest()

                    files_data.append({
                        "path": rel_path,
                        "language": lang,
                        "content_hash": content_hash,
                        "mtime": mtime,
                        "size_bytes": size
                    })

                    entities.append(
                        Entity(
                            id=rel_path,
                            kind="document" if lang == "markdown" else "file",
                            locator=rel_path,
                            metadata={"language": lang, "size_bytes": size, "path": rel_path}
                        )
                    )
                except Exception:
                    pass

        res = ProviderResult(provider=self.name, entities=entities)
        res.metadata["discovered_files"] = files_data
        return res
