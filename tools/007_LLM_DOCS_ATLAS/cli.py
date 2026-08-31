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
    find_associated_tests,
    generate_repository_map,
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


def _packet(ctx: AtlasContext, task: str, budget: int = 16000):
    """Compile a token-budgeted ContextPacket (dashboard /api/context surface)."""
    return compile_task_context(ctx.root, task, budget=budget)


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
        "profile": ctx.profile.name,
        "head_sha": ctx.head_sha,
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
    idx_p.add_argument("--rebuild", action="store_true", help="Purge all facts first, then re-index (kills stale/orphan rows)")
    idx_p.add_argument("--json", action="store_true")

    # 2. Status & Scan
    for name in ("status", "scan", "doctor", "build"):
        sub.add_parser(name).add_argument("--json", action="store_true")

    # 2b. SOTA health/ruler commands
    ch_p = sub.add_parser("check", help="Run full health/coverage/hygiene diagnostics (profile, KB, graph, freshness)")
    ch_p.add_argument("--json", action="store_true")
    st_p = sub.add_parser("standardize", help="Inspect symbols in a file via the standardizer (language + canonical kinds)")
    st_p.add_argument("path", type=str, help="Path to a source file")
    st_p.add_argument("--json", action="store_true")

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
    ctx_p.add_argument("--strategy", type=str, default="ppr_submodular", choices=["ppr_submodular", "hybrid_rrf", "fts5_bm25"], help="Context compilation strategy")
    ctx_p.add_argument("--no-cache", action="store_true", help="Bypass packet cache")
    ctx_p.add_argument("--json", action="store_true")
    ctx_p.add_argument("--include-research", action="store_true")

    # 8. Map & RepoMap
    map_p = sub.add_parser("map", help="Display repository architectural topology map")
    map_p.add_argument("--json", action="store_true")

    repomap_p = sub.add_parser("repomap", help="Generate dense PageRank-ranked repository structural map with multi-file skeletons")
    repomap_p.add_argument("--budget", type=int, default=2000, help="Token budget for repomap")
    repomap_p.add_argument("--focus", type=str, nargs="*", default=None, help="Files to prioritize")
    repomap_p.add_argument("--json", action="store_true")

    # 8b. Tests Association (Requirement R2)
    tests_p = sub.add_parser("tests", help="Find targeted tests and falsifiers for touched or modified files")
    tests_p.add_argument("files", type=str, nargs="+", help="Touched file paths")
    tests_p.add_argument("--json", action="store_true")

    # 9. Inspect
    i_p = sub.add_parser("inspect", help="Inspect a specific document or canonical ID")
    i_p.add_argument("target", type=str)
    i_p.add_argument("--json", action="store_true")

    # 10. Brief (Phase B: human+agent readable briefing)
    b_p = sub.add_parser("brief", help="Compile a structured task briefing (markdown + JSON)")
    b_p.add_argument("task", type=str)
    b_p.add_argument("--budget", type=int, default=8000)
    b_p.add_argument("--strategy", type=str, default="ppr_submodular",
                     choices=["ppr_submodular", "hybrid_rrf", "fts5_bm25"])
    b_p.add_argument("--json", action="store_true")

    # 11. Consolidation & drift diagnostics (Phase B)
    con_p = sub.add_parser("consolidate", help="Detect duplicate documents and authority conflicts")
    con_p.add_argument("--json", action="store_true")
    dr_p = sub.add_parser("drift", help="Detect documentation drift (stale paths, undocumented symbols, orphan docs)")
    dr_p.add_argument("--json", action="store_true")

    # 12. Deterministic retrieval benchmark (Phase E)
    bench_p = sub.add_parser("bench", help="Run the deterministic retrieval-quality benchmark (recall@k, MRR, latency)")
    bench_p.add_argument("--budget", type=int, default=2000)
    bench_p.add_argument("--k", type=int, default=5)
    bench_p.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    repo_root = args.root.resolve() if args.root else Path.cwd().resolve()
    ctx = AtlasContext.discover(repo_root, getattr(args, "include_research", False))

    result = None

    if args.command == "index":
        result = index_repository(repo_root, incremental=args.incremental, rebuild=getattr(args, "rebuild", False))
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
        packet = compile_task_context(
            repo_root,
            args.task,
            budget=args.budget,
            strategy=getattr(args, "strategy", "ppr_submodular"),
            use_cache=not getattr(args, "no_cache", False),
        )
        result = serialise(packet)
    elif args.command == "map":
        result = get_repository_map(repo_root)
    elif args.command == "repomap":
        result = generate_repository_map(
            repo_root,
            focus_files=getattr(args, "focus", None),
            budget=getattr(args, "budget", 2000),
        )
    elif args.command == "tests":
        result = find_associated_tests(repo_root, touched_files=args.files)
    elif args.command == "inspect":
        result = next((r for r in _rows(ctx, "catalog.jsonl") if args.target in {r.get("path"), r.get("canonical_id")}), {"error": "not found", "target": args.target})
    elif args.command == "brief":
        from .core.briefing import compile_brief

        brief = compile_brief(
            repo_root,
            args.task,
            budget=args.budget,
            strategy=args.strategy,
        )
        result = brief
        if not args.json:
            print(brief["brief_markdown"])
            return 0
    elif args.command == "consolidate":
        from .core.consolidation import run_consolidation

        result = run_consolidation(get_storage(repo_root))
    elif args.command == "drift":
        from .core.drift import detect_drift

        result = detect_drift(get_storage(repo_root), repo_root)
    elif args.command == "bench":
        from .core.bench import run_bench

        result = run_bench(budget=getattr(args, "budget", 2000), k=getattr(args, "k", 5))
    elif args.command == "doctor":
        storage = get_storage(repo_root)
        index_stats = storage.get_stats()
        index_healthy = (
            index_stats.get("files", 0) > 0
            and index_stats.get("documents", 0) > 0
        )
        from .core.healthcheck import run_healthcheck

        health = run_healthcheck(ctx, storage)
        result = {
            "root": str(repo_root),
            "storage_db": str(storage.db_path),
            "db_exists": storage.db_path.exists(),
            "index_rows": index_stats,
            "index_healthy": index_healthy,
            "profile": ctx.profile.name,
            "head_sha": ctx.head_sha,
            "coverage": storage.coverage_by_language(),
            "health": {
                "status": health["status"],
                "checks": health["checks"],
                "recommendations": health["recommendations"],
            },
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
        from .core.healthcheck import run_healthcheck

        result = run_healthcheck(ctx, get_storage(repo_root))
    elif args.command == "standardize":
        from .providers.code_ast import CodeASTProvider
        from .core.standardizer import detect_language, file_kind

        target = Path(args.path)
        if not target.is_file():
            result = {"error": "not found", "path": str(args.path)}
        else:
            rel = str(target)
            source = target.read_text(encoding="utf-8", errors="replace")
            provider = CodeASTProvider()
            ext = target.suffix.lower()
            if ext == ".py":
                syms, rels = provider._parse_python(rel, source)
            elif ext in (".ts", ".tsx", ".js", ".jsx"):
                syms, rels = provider._parse_tsjs(rel, source)
            elif ext == ".rs":
                syms, rels = provider._parse_rust(rel, source)
            elif ext == ".go":
                syms, rels = provider._parse_go(rel, source)
            else:
                syms, rels = provider._parse_generic(rel, source, detect_language(rel))
            result = {
                "path": rel,
                "language": detect_language(rel),
                "kind": file_kind(rel),
                "symbols": [
                    {
                        "name": s.name,
                        "kind": s.kind,
                        "language": s.language,
                        "line": s.location.start_line if s.location else 1,
                        "signature": s.signature,
                    }
                    for s in syms
                ],
                "relations": [
                    {
                        "kind": getattr(r.kind, "value", str(r.kind)),
                        "target": r.target_id,
                        "evidence": r.evidence,
                    }
                    for r in rels[:20]
                ],
            }
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
