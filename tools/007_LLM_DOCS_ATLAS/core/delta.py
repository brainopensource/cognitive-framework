"""Ephemeral Incremental Delta Indexer for LDA (Requirement Phase 2).

Provides sub-50ms dirty-file detection and AST/doc re-indexing with zero
background daemon overhead (0 MB idle RAM, 0% CPU).
"""
from __future__ import annotations

import hashlib
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from ..providers.code_ast import CodeASTProvider
from ..providers.markdown import MarkdownDocProvider
from .config import AtlasContext
from .gitinfo import current_head_sha
from .ir import EntityKind, IREntity, Provenance
from .profile import RepositoryProfile
from .runner import run_command
from .standardizer import detect_language, file_kind
from .storage import FactGraphStorage


def detect_dirty_files(
    repo_root: Path,
    profile: Optional[RepositoryProfile] = None,
    storage: Optional[FactGraphStorage] = None,
) -> Tuple[List[str], List[str]]:
    """Detect modified/added and deleted files relative to index / git HEAD.

    Returns:
        (modified_or_added_paths, deleted_paths) normalized as relative POSIX paths.
    """
    root = Path(repo_root).resolve()
    active_profile = profile or RepositoryProfile()
    code_exts = set(active_profile.code_extensions)
    doc_exts = set(active_profile.document_extensions)
    all_valid_exts = code_exts | doc_exts | {".md", ".mdx", ".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go"}
    skip_dirs = {".git", ".venv", "node_modules", "__pycache__", "dist", "build", ".lda"} | set(
        active_profile.excluded_dirs
    )

    modified: Set[str] = set()
    deleted: Set[str] = set()

    # 1. Check via git status --porcelain (fastest: ~10-15ms)
    code, out, _ = run_command(["git", "status", "--porcelain"], root)
    if code == 0 and out:
        for raw_line in out.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            status = raw_line[:2]
            path_part = raw_line[3:].strip()
            # Handle renames: 'R  old -> new'
            if " -> " in path_part:
                old_p, new_p = path_part.split(" -> ", 1)
                old_p = old_p.strip().strip("\"'")
                new_p = new_p.strip().strip("\"'")
                deleted.add(old_p)
                path_part = new_p
            else:
                path_part = path_part.strip("\"'")

            rel = str(Path(path_part)).replace("\\", "/")
            if any(part in rel.split("/") for part in skip_dirs):
                continue
            if not any(rel.endswith(ext) for ext in all_valid_exts):
                continue

            if "D" in status:
                deleted.add(rel)
            else:
                p = root / rel
                if p.is_file():
                    modified.add(rel)
                else:
                    deleted.add(rel)
        return sorted(modified), sorted(deleted)

    # 2. Fallback if not git or git failed: compare mtime with latest index run
    if storage is None:
        from ..atlas import get_storage
        storage = get_storage(root)

    run = storage.latest_index_run()
    last_completed = float(run.get("completed_at", 0)) if run else 0.0

    file_states = storage.get_all_file_states()
    current_paths: Set[str] = set()

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = str(p.relative_to(root)).replace("\\", "/")
        if any(part in p.parts for part in skip_dirs):
            continue
        if p.suffix.lower() not in all_valid_exts:
            continue
        current_paths.add(rel)

        stat = p.stat()
        if rel in file_states:
            prev = file_states[rel]
            if stat.st_mtime > prev.get("mtime", 0) or stat.st_size != prev.get("size_bytes", 0):
                modified.add(rel)
        elif stat.st_mtime > last_completed:
            modified.add(rel)

    for old_path in file_states:
        if old_path not in current_paths:
            deleted.add(old_path)

    return sorted(modified), sorted(deleted)


def index_delta(
    repo_root: Path,
    files: Optional[Sequence[str | Path]] = None,
    profile: Optional[RepositoryProfile] = None,
    storage: Optional[FactGraphStorage] = None,
) -> Dict[str, Any]:
    """Perform on-demand ephemeral incremental re-indexing on dirty/specified files.

    Latency target: < 50ms for typical single-to-few file changes.
    Zero daemon overhead: purely in-process SQLite WAL transaction.
    """
    t0 = time.perf_counter()
    root = Path(repo_root).resolve()
    ctx = AtlasContext.discover(root)
    active_profile = profile or ctx.profile
    code_exts = set(active_profile.code_extensions) | {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go"}
    doc_exts = set(active_profile.document_extensions) | {".md", ".mdx"}

    if storage is None:
        from ..atlas import get_storage
        storage = get_storage(root)

    if files:
        raw_modified = []
        deleted_files = []
        for f in files:
            rel = str(Path(f).relative_to(root) if Path(f).is_absolute() else Path(f)).replace("\\", "/")
            if (root / rel).is_file():
                raw_modified.append(rel)
            else:
                deleted_files.append(rel)
    else:
        raw_modified, deleted_files = detect_dirty_files(root, profile=active_profile, storage=storage)

    file_states = storage.get_all_file_states()
    modified_files = []
    for f in raw_modified:
        p = root / f
        if not p.is_file():
            if f not in deleted_files:
                deleted_files.append(f)
            continue
        stat = p.stat()
        if f in file_states:
            prev = file_states[f]
            if stat.st_mtime == prev.get("mtime", 0) and stat.st_size == prev.get("size_bytes", 0):
                continue
        modified_files.append(f)

    if not modified_files and not deleted_files:
        elapsed = time.perf_counter() - t0
        return {
            "status": "UP_TO_DATE",
            "delta": True,
            "files_indexed": 0,
            "modified_files": [],
            "deleted_files": [],
            "duration_seconds": round(elapsed, 4),
            "duration_ms": round(elapsed * 1000, 2),
            "database_path": str(storage.db_path),
        }

    # 2. Process deletions
    for del_path in deleted_files:
        storage.delete_file_facts(del_path)

    # 3. Categorize modified files
    code_targets = [f for f in modified_files if any(f.endswith(ext) for ext in code_exts)]
    doc_targets = [f for f in modified_files if any(f.endswith(ext) for ext in doc_exts)]

    # 4. Process each modified file in storage
    for fpath_str in modified_files:
        p = root / fpath_str
        if not p.is_file():
            continue
        # Cleanly purge stale facts first
        storage.delete_file_facts(fpath_str)

        try:
            raw = p.read_bytes()
            content_hash = hashlib.sha256(raw).hexdigest()
            stat = p.stat()
            lang = detect_language(fpath_str)
            storage.record_file(
                "default",
                fpath_str,
                lang,
                content_hash,
                stat.st_mtime,
                stat.st_size,
            )
        except Exception:
            pass

    # 5. Extract Markdown facts
    if doc_targets:
        md_provider = MarkdownDocProvider()
        md_res = md_provider.collect(ctx, target_files=doc_targets)
        for doc in md_res.metadata.get("ir_documents", []):
            storage.insert_entity(
                IREntity(
                    id=doc.id,
                    kind=EntityKind.DOCUMENT,
                    name=doc.title,
                    locator=doc.file_path,
                    provenance=Provenance("markdown", "lda", doc.file_path),
                    authority=doc.authority,
                )
            )
            sections = [s for s in md_res.metadata.get("ir_doc_sections", []) if s.doc_id == doc.id]
            storage.insert_document(doc, sections)

    # 6. Extract Code AST facts (Pass 1 + Pass 2 with DB fallback)
    if code_targets:
        ast_provider = CodeASTProvider()
        ast_res = ast_provider.collect(ctx, target_files=code_targets, storage=storage)
        for sym in ast_res.metadata.get("ir_symbols", []):
            storage.insert_entity(
                IREntity(
                    id=sym.symbol_id,
                    kind=sym.kind,
                    name=sym.name,
                    locator=sym.file_path,
                    provenance=Provenance("code_ast", "lda", sym.file_path),
                )
            )
            storage.insert_symbol(sym)

        for rel in ast_res.metadata.get("ir_relations", []):
            storage.insert_relation(rel)

    # 7. Invalidate Context Packet cache
    cache_dir = root / ".lda" / "cache"
    if cache_dir.exists():
        try:
            shutil.rmtree(cache_dir, ignore_errors=True)
            cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    # 8. Record index run
    elapsed = time.perf_counter() - t0
    stats = storage.get_stats()
    head_sha = current_head_sha(root)
    storage.record_index_run(
        files=int(stats.get("files", 0)),
        symbols=int(stats.get("symbols", 0)),
        relations=int(stats.get("relations", 0)),
        incremental=True,
        head_sha=head_sha,
    )

    return {
        "status": "SUCCESS",
        "delta": True,
        "files_indexed": len(modified_files) + len(deleted_files),
        "modified_files": modified_files,
        "deleted_files": deleted_files,
        "total_files": stats.get("files", 0),
        "total_symbols": stats.get("symbols", 0),
        "total_documents": stats.get("documents", 0),
        "total_relations": stats.get("relations", 0),
        "duration_seconds": round(elapsed, 4),
        "duration_ms": round(elapsed * 1000, 2),
        "database_path": str(storage.db_path),
    }
