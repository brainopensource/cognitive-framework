"""Documentation drift detection for LDA.

Deterministic, read-only drift signals derived from the fact graph and the
live workspace: docs referencing deleted paths, source symbols with no
documentation evidence, and documents with no code evidence.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


def detect_drift(storage: Any, repo_root: Path, sample_limit: int = 500) -> Dict[str, Any]:
    root = Path(repo_root)
    stale_paths: List[str] = []
    undocumented_symbols: List[str] = []
    orphan_documents: List[str] = []

    # 1. Symbols pointing at files that no longer exist.
    try:
        paths = storage.sample_symbol_paths(limit=sample_limit)
    except Exception:
        paths = ()
    for p in paths:
        if p and not (root / p).exists():
            stale_paths.append(p)

    # 2. Public symbols (classes/functions) with no docstring and no
    #    documents/specified_by relation.
    con = storage.get_connection()
    try:
        rows = con.execute(
            """
            SELECT s.file_path, s.name, s.kind, s.docstring,
                   (SELECT COUNT(*) FROM relations r
                     WHERE r.target_id = s.id AND r.kind IN ('documents', 'specified_by')) AS doc_rels
            FROM symbols s ORDER BY s.file_path, s.name LIMIT ?
            """,
            (sample_limit,),
        ).fetchall()
        for r in rows:
            if not r["docstring"] and not r["doc_rels"] and r["kind"] in ("class", "function", "method"):
                undocumented_symbols.append(f"{r['file_path']}#{r['name']}")
    except Exception:
        pass

    # 3. Documents with zero relations to code (no documents/specified_by
    #    outgoing edges) — candidates for orphaned or pending documentation.
    try:
        doc_rows = con.execute(
            """
            SELECT d.file_path,
                   (SELECT COUNT(*) FROM relations r
                     WHERE r.source_id = d.id AND r.kind IN ('documents', 'specified_by')) AS rels
            FROM documents d ORDER BY d.file_path LIMIT ?
            """,
            (sample_limit,),
        ).fetchall()
        orphan_documents = [r["file_path"] for r in doc_rows if not r["rels"]]
    except Exception:
        pass

    signals = len(stale_paths) + len(undocumented_symbols) + len(orphan_documents)
    return {
        "status": "HEALTHY" if signals == 0 else "DRIFT_DETECTED",
        "stale_symbol_paths": stale_paths[:20],
        "stale_symbol_paths_count": len(stale_paths),
        "undocumented_symbols": undocumented_symbols[:20],
        "undocumented_symbols_count": len(undocumented_symbols),
        "orphan_documents": orphan_documents[:20],
        "orphan_documents_count": len(orphan_documents),
        "sample_limit": sample_limit,
        "summary": (
            f"{len(stale_paths)} stale path(s), "
            f"{len(undocumented_symbols)} undocumented symbol(s), "
            f"{len(orphan_documents)} document(s) without code evidence"
        ),
    }


__all__ = ["detect_drift"]
