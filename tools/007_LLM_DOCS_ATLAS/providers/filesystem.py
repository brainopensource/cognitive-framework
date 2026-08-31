"""Filesystem and repository file discovery provider."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from ..core.ir import ConfidenceTier, EntityKind, IREntity, Provenance, SourceLocation
from ..core.models import Entity, ProviderResult
from ..core.standardizer import detect_language, file_kind
from .base import BaseProvider


# Generic, project-agnostic ignore set. Project-specific workspace directories
# (e.g. dev_context_logs, .vanguard) belong to the active RepositoryProfile,
# never to this generic default.
IGNORE_DIRS: Set[str] = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".generated", ".pytest_cache", ".tox",
    "dist", "build", ".turbo", ".next", ".mypy_cache", ".ruff_cache",
}


class FilesystemProvider(BaseProvider):
    """Discovers and hashes repository files, classifying by profile extensions."""

    name = "filesystem"
    confidence_tier = ConfidenceTier.STRUCTURED_DOC

    def collect(
        self,
        repo_root: Path | Any,
        incremental: bool = False,
        file_states: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> ProviderResult:
        root = repo_root.root if hasattr(repo_root, "root") else Path(repo_root)
        profile = getattr(repo_root, "profile", None)
        ignored = IGNORE_DIRS | (set(profile.excluded_dirs) if profile else set())
        code_exts = (profile.code_extensions if profile else ())
        doc_exts = (profile.document_extensions if profile else ())
        files_data: List[Dict[str, Any]] = []
        entities: List[Entity] = []

        for dirpath, dirnames, filenames in os.walk(root):
            # Prune ignored directories in-place (generic + profile exclusions)
            dirnames[:] = [d for d in dirnames if d not in ignored and not d.startswith(".")]

            for fname in filenames:
                if fname.startswith("."):
                    continue
                fpath = Path(dirpath) / fname
                try:
                    rel_path = str(fpath.relative_to(root)).replace("\\", "/")
                    lang = detect_language(rel_path)
                    kind = file_kind(rel_path, code_exts=code_exts, doc_exts=doc_exts)
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
                            kind=kind if kind in {"document", "code"} else "file",
                            locator=rel_path,
                            metadata={"language": lang, "size_bytes": size, "path": rel_path}
                        )
                    )
                except Exception:
                    pass

        res = ProviderResult(provider=self.name, entities=entities)
        res.metadata["discovered_files"] = files_data
        return res
