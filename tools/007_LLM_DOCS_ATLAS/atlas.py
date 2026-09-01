"""Central Engine Coordinator for LDA Repository Intelligence."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from .core.compiler import ContextCompiler
from .core.config import AtlasContext
from .core.models import ContextPacket, ProviderResult
from .core.profile import RepositoryProfile
from .core.repo_map import RepositoryMapGenerator
from .core.storage import FactGraphStorage
from .core.test_association import TestAssociationEngine
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
        KnowledgeProvider(),
    ]
    results = []
    for p in providers:
        try:
            results.append(p.collect(ctx))
        except Exception:
            pass
    return results


def rescan_catalog(ctx: AtlasContext) -> Dict[str, Any]:
    """Read-only, in-memory catalog collection (Single Emitter invariant)."""
    provider = FilesystemProvider()
    res = provider.collect(ctx)
    docs = [
        e.metadata for e in res.entities
        if e.kind == "document" and e.metadata.get("path")
    ]
    return {"status": "ok", "documents": len(docs), "written": False}


def index_repository(
    repo_root: Path,
    incremental: bool = False,
    rebuild: bool = False,
) -> Dict[str, Any]:
    """Execute complete repository indexing into SQLite + FTS5 fact graph."""
    start_time = time.time()
    ctx = AtlasContext.discover(Path(repo_root))
    repo_root = ctx.root
    storage = get_storage(repo_root)
    if rebuild:
        storage.purge_all()

    file_states = storage.get_all_file_states() if incremental and not rebuild else {}

    # 1. Discover filesystem files (profile-aware exclusions via the context)
    fs_provider = FilesystemProvider()
    fs_res = fs_provider.collect(ctx, incremental=incremental, file_states=file_states)
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

    # 2. Collect markdown & code facts (profile-aware exclusions via the context)
    md_provider = MarkdownDocProvider()
    md_res = md_provider.collect(ctx)
    ast_provider = CodeASTProvider()
    ast_res = ast_provider.collect(ctx)

    # 3. Insert general entities
    from .core.ir import EntityKind, IREntity, Provenance
    for e in fs_res.entities + md_res.entities + ast_res.entities:
        ir_ent = IREntity(
            id=e.id,
            kind=EntityKind.DOCUMENT if e.kind == "document" else (EntityKind.FILE if e.kind == "file" else e.kind),
            name=e.metadata.get("name", e.id),
            locator=e.locator,
            provenance=Provenance("provider", "lda", e.locator),
            authority=e.authority,
            metadata=dict(e.metadata),
        )
        storage.insert_entity(ir_ent)

    md_docs = md_res.metadata.get("ir_documents", [])
    ast_syms = ast_res.metadata.get("ir_symbols", [])

    known_entity_ids = {e.id for e in fs_res.entities + md_res.entities + ast_res.entities}
    for doc in md_docs:
        if doc.id not in known_entity_ids:
            storage.insert_entity(IREntity(
                id=doc.id,
                kind=EntityKind.DOCUMENT,
                name=doc.title,
                locator=doc.file_path,
                provenance=Provenance("markdown", "lda", doc.file_path),
                authority=doc.authority,
            ))
    for sym in ast_syms:
        if sym.symbol_id not in known_entity_ids:
            storage.insert_entity(IREntity(
                id=sym.symbol_id,
                kind=sym.kind,
                name=sym.name,
                locator=sym.file_path,
                provenance=Provenance("code_ast", "lda", sym.file_path),
            ))

    # 4. Extract & store Markdown Documentation
    for doc in md_docs:
        sections = [s for s in md_res.metadata.get("ir_doc_sections", []) if s.doc_id == doc.id]
        storage.insert_document(doc, sections)

    # 5. Extract & store Code AST & Symbols
    for sym in ast_syms:
        storage.insert_symbol(sym)
    for rel in ast_res.metadata.get("ir_relations", []):
        storage.insert_relation(rel)

    elapsed = time.time() - start_time
    stats = storage.get_stats()
    storage.record_index_run(
        files=int(stats.get("files", 0)),
        symbols=int(stats.get("symbols", 0)),
        relations=int(stats.get("relations", 0)),
        incremental=bool(incremental),
        head_sha=ctx.head_sha,
    )
    return {
        "status": "SUCCESS",
        "incremental": incremental,
        "rebuild": rebuild,
        "files_indexed": indexed_count,
        "total_files": stats.get("files", 0),
        "total_symbols": stats.get("symbols", 0),
        "total_documents": stats.get("documents", 0),
        "total_relations": stats.get("relations", 0),
        "duration_seconds": round(elapsed, 4),
        "database_path": str(storage.db_path),
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


def generate_repository_map(
    repo_root: Path,
    focus_files: Sequence[str] | None = None,
    budget: int = 2000,
) -> str:
    """Generate a dense, graph-centrality ranked structural repository map."""
    storage = get_storage(repo_root)
    stats = storage.get_stats()
    if stats["files"] == 0:
        index_repository(repo_root, incremental=False)
    gen = RepositoryMapGenerator(storage)
    return gen.generate_map(focus_files=focus_files, token_budget=budget)


def find_associated_tests(
    repo_root: Path,
    touched_files: Sequence[str],
    touched_symbols: Sequence[str] | None = None,
) -> Dict[str, Any]:
    """Find targeted tests and falsifiers for touched files (Requirement R2)."""
    storage = get_storage(repo_root)
    engine = TestAssociationEngine(storage)
    return engine.find_associated_tests(touched_files, touched_symbols)


def compile_task_context(
    repo_root: Path,
    task: str,
    budget: int = 8000,
    strategy: str = "ppr_submodular",
    profile: Optional[RepositoryProfile] = None,
    head_sha: Optional[str] = None,
    use_cache: bool = True,
) -> ContextPacket:
    ctx = AtlasContext.discover(Path(repo_root))
    profile = profile or ctx.profile
    head_sha = head_sha if head_sha is not None else ctx.head_sha
    storage = get_storage(repo_root)
    stats = storage.get_stats()
    if stats["files"] == 0:
        index_repository(repo_root, incremental=False)
    compiler = ContextCompiler(repo_root, storage, profile=profile, head_sha=head_sha)
    return compiler.compile(task, budget=budget, strategy=strategy, use_cache=use_cache)
