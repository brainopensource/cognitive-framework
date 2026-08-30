"""Central Engine Coordinator for LDA Repository Intelligence."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.compiler import ContextCompiler
from .core.config import AtlasContext
from .core.models import ContextPacket, ProviderResult
from .core.storage import FactGraphStorage
from .providers.code_ast import CodeASTProvider
from .providers.filesystem import FilesystemProvider
from .providers.git import GitProvider
from .providers.knowledge import KnowledgeProvider
from .providers.markdown import MarkdownDocProvider


def get_storage(repo_root: Path) -> FactGraphStorage:
    db_dir = repo_root / ".lda"
    db_dir.mkdir(parents=True, exist_ok=True)
    return FactGraphStorage(db_dir / "index.db")


def collect(ctx: AtlasContext) -> List[ProviderResult]:
    """Execute providers for a repository context (backwards-compatible API)."""
    providers = [
        FilesystemProvider(),
        MarkdownDocProvider(),
        CodeASTProvider(),
        GitProvider(),
        KnowledgeProvider()
    ]
    results = []
    for p in providers:
        try:
            results.append(p.collect(ctx))
        except Exception:
            pass
    return results


def index_repository(repo_root: Path, incremental: bool = False) -> Dict[str, Any]:
    """Execute complete repository indexing into SQLite + FTS5 fact graph."""
    start_time = time.time()
    storage = get_storage(repo_root)

    file_states = storage.get_all_file_states() if incremental else {}
    
    # 1. Discover filesystem files
    fs_provider = FilesystemProvider()
    fs_res = fs_provider.collect(repo_root, incremental=incremental, file_states=file_states)
    discovered_files = fs_res.metadata.get("discovered_files", [])

    indexed_count = 0
    current_paths = set()

    for f in discovered_files:
        path = f["path"]
        current_paths.add(path)
        content_hash = f["content_hash"]
        mtime = f["mtime"]
        size_bytes = f["size_bytes"]
        lang = f["language"]

        # Check if file changed
        if incremental and path in file_states:
            prev = file_states[path]
            if prev["content_hash"] == content_hash and prev["mtime"] == mtime:
                continue  # Unchanged file

        # Purge stale facts if changed
        if incremental:
            storage.delete_file_facts(path)

        storage.record_file("default", path, lang, content_hash, mtime, size_bytes)
        indexed_count += 1

    # Purge deleted files in incremental mode
    if incremental:
        for old_path in file_states:
            if old_path not in current_paths:
                storage.delete_file_facts(old_path)

    # 2. Extract Markdown Documentation
    md_provider = MarkdownDocProvider()
    md_res = md_provider.collect(repo_root)
    for doc in md_res.metadata.get("ir_documents", []):
        sections = [s for s in md_res.metadata.get("ir_doc_sections", []) if s.doc_id == doc.id]
        storage.insert_document(doc, sections)
    for rel in md_res.relations:
        # insert doc relations
        pass

    # 3. Extract Code AST & Symbols
    ast_provider = CodeASTProvider()
    ast_res = ast_provider.collect(repo_root)
    for sym in ast_res.metadata.get("ir_symbols", []):
        storage.insert_symbol(sym)
    for rel in ast_res.metadata.get("ir_relations", []):
        storage.insert_relation(rel)

    # Insert general entities
    for e in fs_res.entities + md_res.entities + ast_res.entities:
        # Convert to IREntity
        from .core.ir import EntityKind, IREntity, Provenance
        ir_ent = IREntity(
            id=e.id,
            kind=EntityKind.DOCUMENT if e.kind == "document" else (EntityKind.SYMBOL if e.kind == "symbol" else EntityKind.FILE),
            name=e.metadata.get("name", e.id),
            locator=e.locator,
            provenance=Provenance("provider", "lda", e.locator),
            authority=e.authority,
            metadata=dict(e.metadata)
        )
        storage.insert_entity(ir_ent)

    elapsed = time.time() - start_time
    stats = storage.get_stats()
    return {
        "status": "SUCCESS",
        "incremental": incremental,
        "files_indexed": indexed_count,
        "total_files": stats.get("files", 0),
        "total_symbols": stats.get("symbols", 0),
        "total_documents": stats.get("documents", 0),
        "total_relations": stats.get("relations", 0),
        "duration_seconds": round(elapsed, 4),
        "database_path": str(storage.db_path)
    }


def query_repository(repo_root: Path, query: str) -> List[Dict[str, Any]]:
    storage = get_storage(repo_root)
    return storage.search_fts(query)


def get_symbol_details(repo_root: Path, symbol_query: str) -> List[Dict[str, Any]]:
    storage = get_storage(repo_root)
    return storage.get_symbol(symbol_query)


def get_callers(repo_root: Path, symbol_id: str) -> List[Dict[str, Any]]:
    storage = get_storage(repo_root)
    return storage.get_callers(symbol_id)


def get_references(repo_root: Path, symbol_id: str) -> List[Dict[str, Any]]:
    storage = get_storage(repo_root)
    return storage.get_references(symbol_id)


def get_repository_map(repo_root: Path) -> Dict[str, Any]:
    storage = get_storage(repo_root)
    return storage.get_topology_map()


def compile_task_context(repo_root: Path, task: str, budget: int = 8000) -> ContextPacket:
    storage = get_storage(repo_root)
    # Ensure index exists
    stats = storage.get_stats()
    if stats["files"] == 0:
        index_repository(repo_root, incremental=False)
    compiler = ContextCompiler(repo_root, storage)
    return compiler.compile(task, budget=budget)
