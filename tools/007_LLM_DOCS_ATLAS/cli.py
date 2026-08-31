"""Command line interface for LDA — Universal Repository Intelligence."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from .atlas import (
    collect,
    compile_task_context,
    get_callers,
    get_references,
    get_repository_map,
    get_storage,
    get_symbol_details,
    index_repository,
    query_repository,
)
from .core.config import AtlasContext
from .core.models import Candidate, ContextPacket, serialise


def _rows(ctx: AtlasContext, name: str):
    path = ctx.knowledge / name
    if not path.exists():
        if name == "catalog.jsonl":
            from .providers.filesystem import FilesystemProvider
            return [e.metadata for e in FilesystemProvider().collect(ctx).entities if e.kind == "document"]
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _snapshot(ctx: AtlasContext):
    storage = get_storage(ctx.root)
    stats = storage.get_stats()
    topo = storage.get_topology_map()

    docs = _rows(ctx, "catalog.jsonl")
    links = _rows(ctx, "links.jsonl")

    total = {
        "status": "HEALTHY" if stats.get("files", 0) > 0 else "DEGRADED_EMPTY_INDEX",
        "index_hint": (
            "fact graph populated"
            if stats.get("files", 0) > 0
            else "fact graph is empty; run 'uv run lda index' or use tools/docs_rag_v0.py"
        ),
        "root": str(ctx.root),
        "database_stats": stats,
        "topology": topo,
        "documents": stats.get("documents", len(docs)),
        "symbols": stats.get("symbols", len(_rows(ctx, "symbols.jsonl"))),
        "relations": stats.get("relations", len(links)),
        "lines": sum(r.get("lines", 0) for r in docs),
        "bytes": sum(r.get("bytes", 0) for r in docs),
        "estimated_tokens": sum(r.get("estimated_tokens", 0) for r in docs),
        "providers": [r.provider for r in collect(ctx)],
    }
    return total


def main(argv=None):
    parser = argparse.ArgumentParser(prog="lda", description="LDA Universal Repository Intelligence & Context Engine")
    parser.add_argument("--root", type=Path, default=None, help="Root path of target repository")
    sub = parser.add_subparsers(dest="command", required=True)

    # 1. Index command
    idx_p = sub.add_parser("index", help="Index repository into SQLite + FTS5 fact graph")
    idx_p.add_argument("--incremental", action="store_true", help="Perform warm incremental re-index")
    idx_p.add_argument("--json", action="store_true")

    # 2. Status & Scan
    for name in ("status", "scan", "check", "doctor", "build"):
        sub.add_parser(name).add_argument("--json", action="store_true")

    # 3. Query
    q_p = sub.add_parser("query", help="Query repository symbols, docs, and AST entities")
    q_p.add_argument("query", type=str)
    q_p.add_argument("--json", action="store_true")

    # 4. Symbol
    sym_p = sub.add_parser("symbol", help="Lookup detailed symbol information")
    sym_p.add_argument("symbol", type=str)
    sym_p.add_argument("--json", action="store_true")

    # 5. Callers
    call_p = sub.add_parser("callers", help="Find upstream callers of a symbol")
    call_p.add_argument("symbol_id", type=str)
    call_p.add_argument("--json", action="store_true")

    # 6. References
    ref_p = sub.add_parser("references", help="Find references/usages of a symbol")
    ref_p.add_argument("symbol_id", type=str)
    ref_p.add_argument("--json", action="store_true")

    # 7. Context (Primary Product)
    ctx_p = sub.add_parser("context", help="Compile token-budgeted high-signal ContextPacket for an AI agent")
    ctx_p.add_argument("task", type=str)
    ctx_p.add_argument("--budget", type=int, default=8000)
    ctx_p.add_argument("--json", action="store_true")
    ctx_p.add_argument("--include-research", action="store_true")

    # 8. Map
    map_p = sub.add_parser("map", help="Display repository architectural topology map")
    map_p.add_argument("--json", action="store_true")

    # 9. Inspect
    i_p = sub.add_parser("inspect", help="Inspect a specific document or canonical ID")
    i_p.add_argument("target", type=str)
    i_p.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    repo_root = args.root.resolve() if args.root else Path.cwd().resolve()
    ctx = AtlasContext.discover(repo_root, getattr(args, "include_research", False))

    result = None

    if args.command == "index":
        result = index_repository(repo_root, incremental=args.incremental)
    elif args.command in {"status", "scan"}:
        result = _snapshot(ctx)
    elif args.command == "query":
        fts_res = query_repository(repo_root, args.query)
        if not fts_res:
            # Fallback to authority-scored catalog routing (same ranker as the
            # context compiler), since FTS row content is metadata-only.
            from dataclasses import asdict

            from .core.ranking import catalog_fallback_candidates, load_catalog_metadata

            fts_res = [
                asdict(c)
                for c in catalog_fallback_candidates(args.query, load_catalog_metadata(repo_root))
            ]
        result = fts_res
    elif args.command == "symbol":
        result = get_symbol_details(repo_root, args.symbol)
    elif args.command == "callers":
        result = get_callers(repo_root, args.symbol_id)
    elif args.command == "references":
        result = get_references(repo_root, args.symbol_id)
    elif args.command == "context":
        packet = compile_task_context(repo_root, args.task, budget=args.budget)
        result = serialise(packet)
    elif args.command == "map":
        result = get_repository_map(repo_root)
    elif args.command == "inspect":
        result = next((r for r in _rows(ctx, "catalog.jsonl") if args.target in {r.get("path"), r.get("canonical_id")}), {"error": "not found", "target": args.target})
    elif args.command == "doctor":
        storage = get_storage(repo_root)
        index_stats = storage.get_stats()
        index_healthy = (
            index_stats.get("files", 0) > 0
            and index_stats.get("documents", 0) > 0
        )
        result = {
            "root": str(repo_root),
            "storage_db": str(storage.db_path),
            "db_exists": storage.db_path.exists(),
            "index_rows": index_stats,
            "index_healthy": index_healthy,
            "index_hint": (
                "index is populated"
                if index_healthy
                else "index is EMPTY or cold; run 'uv run lda index' — agents should "
                     "verify .generated/knowledge/report.json status=VALIDATED first and "
                     "fall back to tools/docs_rag_v0.py when unhealthy"
            ),
            "required": ["python3", "sqlite3"],
            "optional": {
                "mkdocs": shutil.which("mkdocs") is not None,
                "vale": shutil.which("vale") is not None,
                "markdownlint": shutil.which("markdownlint") is not None,
                "rg": shutil.which("rg") is not None
            }
        }
    elif args.command == "check":
        result = {"delegation": "use just check or test runners", "status": "available"}
    elif args.command == "build":
        from .dashboard import write_dashboard
        path = write_dashboard(ctx, repo_root / "tools" / "007_LLM_DOCS_ATLAS" / "dashboard.html")
        result = {"dashboard": str(path.relative_to(repo_root)), "status": "built"}

    wants_json = getattr(args, "json", False)
    if wants_json or isinstance(result, (dict, list)):
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
