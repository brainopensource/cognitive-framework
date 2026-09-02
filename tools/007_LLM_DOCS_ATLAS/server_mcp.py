"""Model Context Protocol (MCP) Server for LDA Repository Intelligence.

Communicates via JSON-RPC 2.0 over standard I/O (stdio).
Exposes the full suite of LDA repository intelligence, AST graph,
FTS5 search, callers/callees, and token-bounded context compilation.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Mapping

# Configure logging to stderr to keep stdout pure for JSON-RPC
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("lda.mcp")


class LDAMCPServer:
    """Zero-dependency Model Context Protocol server exposing all LDA tools.

    Project-agnostic: the workspace root and the active RepositoryProfile are
    resolved through AtlasContext (lda.yaml / $LDA_PROFILE / generic default) —
    never hard-coded to a package location or a project-specific knowledge path.
    """

    def __init__(self, workspace_root: Path) -> None:
        from .atlas import get_storage
        from .core.config import AtlasContext

        self._ctx = AtlasContext.discover(Path(workspace_root))
        self._root = self._ctx.root
        self._storage = get_storage(self._root)

    # ------------------------------------------------------------------
    # Shared health / freshness helpers (fail-closed freshness invariant)
    # ------------------------------------------------------------------

    def _index_health(self) -> bool:
        stats = self._storage.get_stats()
        return stats.get("files", 0) > 0 and stats.get("documents", 0) > 0

    # ------------------------------------------------------------------
    # MCP resources & prompts
    # ------------------------------------------------------------------

    def _list_resources(self) -> list[dict[str, Any]]:
        resources = [
            {
                "uri": "lda://map",
                "name": "Repository topology map",
                "description": "Language/entity/relation statistics for the indexed repository.",
                "mimeType": "application/json",
            }
        ]
        try:
            con = self._storage.get_connection()
            rows = con.execute(
                "SELECT id, file_path, title, authority FROM documents ORDER BY file_path LIMIT 200"
            ).fetchall()
            for r in rows:
                resources.append({
                    "uri": f"lda://docs/{r['id']}",
                    "name": r["title"],
                    "description": f"{r['file_path']} (authority: {r['authority'] or 'none'})",
                    "mimeType": "text/markdown",
                })
        except Exception:
            pass
        return resources

    def _read_resource(self, uri: str) -> dict[str, Any] | None:
        if uri == "lda://map":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps(self._storage.get_topology_map(), sort_keys=True),
            }
        if uri.startswith("lda://docs/"):
            doc_id = uri[len("lda://docs/"):]
            con = self._storage.get_connection()
            row = con.execute(
                "SELECT file_path, title, summary, authority FROM documents WHERE id = ?",
                (doc_id,),
            ).fetchone()
            if row is None:
                return None
            sections = con.execute(
                "SELECT heading, content, start_line, end_line FROM doc_sections "
                "WHERE doc_id = ? ORDER BY start_line",
                (doc_id,),
            ).fetchall()
            parts = [f"# {row['title']}", "", row["summary"] or "", ""]
            for s in sections:
                parts.append(f"## {s['heading']} (L{s['start_line']}-L{s['end_line']})")
                parts.append("")
                parts.append(s["content"] or "")
                parts.append("")
            return {"uri": uri, "mimeType": "text/markdown", "text": "\n".join(parts)}
        return None

    def _get_prompt(self, name: str, args: Mapping[str, Any]) -> dict[str, Any]:
        if name == "lda_task_briefing":
            task = str(args.get("task", ""))
            text = (
                "Use the lda_brief tool to compile a structured briefing for this task, "
                "then read only the cited documents/sections before implementing:\n\n"
                f"Task: {task}"
            )
            return {"description": "LDA task briefing", "messages": [
                {"role": "user", "content": {"type": "text", "text": text}},
            ]}
        if name == "lda_repo_orientation":
            text = (
                "Orient in this repository: call lda_doctor first; if the index is cold, "
                "run 'lda index'. Then call lda_repomap for the structural map and lda_map "
                "for topology. Work only from bounded context packets (lda_context) "
                "afterwards; verify .generated/knowledge/report.json status=VALIDATED "
                "before trusting catalog facts."
            )
            return {"description": "LDA repository orientation", "messages": [
                {"role": "user", "content": {"type": "text", "text": text}},
            ]}
        raise ValueError(f"Unknown prompt: {name}")


    def _head_sha(self) -> str | None:
        from .core.gitinfo import current_head_sha

        return current_head_sha(self._root)

    def handle_request(self, request: Mapping[str, Any]) -> Mapping[str, Any] | None:
        method = request.get("method")
        req_id = request.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {"subscribe": False, "listChanged": False},
                        "prompts": {"listChanged": False},
                    },
                    "serverInfo": {"name": "lda-repository-intelligence", "version": "1.2.0"},
                },
            }

        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"resources": self._list_resources()},
            }

        elif method == "resources/read":
            uri = (request.get("params") or {}).get("uri", "")
            contents = self._read_resource(uri)
            if contents is None:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": f"Unknown resource: {uri}"},
                }
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"contents": [contents]},
            }

        elif method == "prompts/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"prompts": [
                    {
                        "name": "lda_task_briefing",
                        "description": "Compile an LDA task briefing for a task string.",
                        "arguments": [{"name": "task", "description": "Task keywords", "required": True}],
                    },
                    {
                        "name": "lda_repo_orientation",
                        "description": "Orient in an unfamiliar repository using the LDA structural map and topology.",
                        "arguments": [],
                    },
                ]},
            }

        elif method == "prompts/get":
            name = (request.get("params") or {}).get("name", "")
            pargs = (request.get("params") or {}).get("arguments") or {}
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": self._get_prompt(name, pargs),
            }

        elif method == "notifications/initialized":
            return None

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": [
                        {
                            "name": "lda_context",
                            "description": "Compile high-signal token-budgeted context packet containing canonical docs, symbols, tests, and documentation debt obligations for a task.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Task keywords or error message."},
                                    "budget": {"type": "integer", "description": "Token budget (default: 4000).", "default": 4000},
                                    "strategy": {"type": "string", "description": "Strategy: 'ppr_submodular' (default), 'hybrid_rrf' (dense+lexical fusion), or 'fts5_bm25'.", "default": "ppr_submodular", "enum": ["ppr_submodular", "hybrid_rrf", "fts5_bm25"]},
                                },
                                "required": ["query"],
                            },
                        },
                        {
                            "name": "lda_brief",
                            "description": "Compile a structured task briefing: task read-back, intent, authority map, key documents/code, documentation obligations, and test falsifiers (markdown + JSON).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Task keywords or error message."},
                                    "budget": {"type": "integer", "description": "Token budget (default: 8000).", "default": 8000},
                                    "strategy": {"type": "string", "description": "Ranking strategy.", "enum": ["ppr_submodular", "hybrid_rrf", "fts5_bm25"], "default": "ppr_submodular"},
                                },
                                "required": ["query"],
                            },
                        },
                        {
                            "name": "lda_consolidate",
                            "description": "Detect duplicate/overlapping documents and conflicting authority claims (read-only consolidation diagnostics).",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                        {
                            "name": "lda_drift",
                            "description": "Detect documentation drift: stale symbol paths, undocumented symbols, documents without code evidence.",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                        {
                            "name": "lda_repomap",
                            "description": "Generate dense PageRank-ranked repository structural map with multi-file skeletons within a token budget.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "focus_files": {"type": "array", "items": {"type": "string"}, "description": "Optional list of files to prioritize."},
                                    "budget": {"type": "integer", "description": "Token budget for repo map (default: 2000).", "default": 2000},
                                },
                            },
                        },
                        {
                            "name": "lda_focused_tests",
                            "description": "Find targeted tests and falsifiers for a list of modified or touched files (Requirement R2).",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "touched_files": {"type": "array", "items": {"type": "string"}, "description": "List of touched or modified file paths."},
                                },
                                "required": ["touched_files"],
                            },
                        },
                        {
                            "name": "lda_symbol",
                            "description": "Lookup precise AST definitions, signatures, line numbers, and docstrings for a symbol.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"symbol_name": {"type": "string", "description": "Symbol name (e.g. 'Kernel', 'BudgetGovernor')."}},
                                "required": ["symbol_name"],
                            },
                        },
                        {
                            "name": "lda_callers",
                            "description": "Find upstream callers and dependent functions for a given symbol.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"symbol_id": {"type": "string", "description": "Symbol ID or name."}},
                                "required": ["symbol_id"],
                            },
                        },
                        {
                            "name": "lda_callees",
                            "description": "Find downstream functions called by a given symbol.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"symbol_id": {"type": "string", "description": "Symbol ID or name."}},
                                "required": ["symbol_id"],
                            },
                        },
                        {
                            "name": "lda_references",
                            "description": "Find all usages and references of a symbol across the entire repository.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"symbol_id": {"type": "string", "description": "Symbol ID or name."}},
                                "required": ["symbol_id"],
                            },
                        },
                        {
                            "name": "lda_tests_for_symbol",
                            "description": "Find executable test functions and test files covering a specific symbol.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"symbol_id": {"type": "string", "description": "Symbol ID or name."}},
                                "required": ["symbol_id"],
                            },
                        },
                        {
                            "name": "lda_docs_for_symbol",
                            "description": "Find canonical documentation sections specifying a given symbol.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {"symbol_id": {"type": "string", "description": "Symbol ID or name."}},
                                "required": ["symbol_id"],
                            },
                        },
                        {
                            "name": "lda_fts_search",
                            "description": "Full-text BM25 search across repository symbols, documentation, and AST entities.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search query terms."},
                                    "limit": {"type": "integer", "description": "Max results (default: 15).", "default": 15},
                                },
                                "required": ["query"],
                            },
                        },
                        {
                            "name": "lda_map",
                            "description": "Generate architectural topology map of subsystems, module boundaries, and LOC.",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                        {
                            "name": "lda_doctor",
                            "description": "Check repository intelligence health status, SQLite database stats, entity counts, per-language coverage, and HEAD binding.",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                        {
                            "name": "lda_check",
                            "description": "Run the full SOTA health/ruler diagnostics: profile resolution, knowledge-base validity, fact-graph health, orphan/stale/low-signal hygiene, freshness, and recommendations.",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                        {
                            "name": "lda_coverage",
                            "description": "Per-language coverage of the indexed fact graph (files, symbols, relations).",
                            "inputSchema": {"type": "object", "properties": {}},
                        },
                    ]
                },
            }

        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            try:
                result_content = self._execute_tool(tool_name, args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(result_content, indent=2)}]},
                }
            except Exception as exc:
                logger.exception("Tool execution error: %s", exc)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": str(exc)},
                }

        elif method == "notifications/initialized":
            return None

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
        }

    def _execute_tool(self, name: str, args: Mapping[str, Any]) -> Any:
        if name == "lda_context":
            query = args.get("query", "")
            budget = args.get("budget", 4000)
            strategy = args.get("strategy", "ppr_submodular")
            head = self._head_sha()
            healthy = self._index_health()
            if healthy:
                # Packet parity with the CLI (`lda context`): canonical docs,
                # symbols, tests, obligations and provenance — one dialect only.
                from .atlas import compile_task_context
                from .core.models import serialise

                packet = compile_task_context(self._root, query, budget=budget, strategy=strategy)
                payload = serialise(packet)
                payload["bounded_context"] = {
                    "documents": [
                        {"canonical_id": c.title, "path": c.locator, "authority": c.authority}
                        for c in packet.documents
                    ],
                    "symbols": [{"title": c.title, "locator": c.locator} for c in packet.symbols],
                }
            else:
                # Cold/degraded index: fail open to the deterministic catalog
                # routing (authority-aware, read-only) instead of serving
                # empty packet facts. LDA is standalone — no dependency on
                # other repository tools.
                from .core.ranking import catalog_fallback_candidates, load_catalog_metadata

                catalog = load_catalog_metadata(self._root, self._ctx.profile.generated_root)
                payload = {
                    "documents": [
                        {"canonical_id": c.title, "path": c.locator, "authority": c.authority}
                        for c in catalog_fallback_candidates(
                            query, catalog, profile=self._ctx.profile
                        )
                    ],
                    "degraded_mode": "catalog_routing",
                }
                # Preserve the bounded_context view used by older MCP
                # clients while making degraded mode explicit. The fallback
                # contains catalog documents only; it must never pretend to
                # have index-backed symbols or repository facts.
                payload["bounded_context"] = {
                    "documents": list(payload["documents"]),
                    "symbols": [],
                }
            payload["index_healthy"] = healthy
            payload["source_head_sha"] = head
            payload["profile"] = self._ctx.profile.name
            return payload

        elif name == "lda_brief":
            from .core.briefing import compile_brief

            return compile_brief(
                self._root,
                args.get("query", ""),
                budget=args.get("budget", 8000),
                strategy=args.get("strategy", "ppr_submodular"),
            )

        elif name == "lda_consolidate":
            from .core.consolidation import run_consolidation

            return run_consolidation(self._storage)

        elif name == "lda_drift":
            from .core.drift import detect_drift

            return detect_drift(self._storage, self._root)

        elif name == "lda_repomap":
            from .atlas import generate_repository_map

            focus_files = args.get("focus_files")
            budget = args.get("budget", 2000)
            repomap_text = generate_repository_map(self._root, focus_files=focus_files, budget=budget)
            return {
                "repository_map": repomap_text,
                "source_head_sha": self._head_sha(),
                "budget": budget,
            }

        elif name == "lda_focused_tests":
            from .atlas import find_associated_tests

            touched_files = args.get("touched_files", [])
            return find_associated_tests(self._root, touched_files=touched_files)

        elif name == "lda_symbol":
            sym_name = args.get("symbol_name", "")
            results = self._storage.get_symbol(sym_name)
            if not results:
                # Fallback to prefix search in the profile's knowledge base
                # (generated_root is profile-driven, never hard-coded).
                symbols_file = self._ctx.knowledge / "symbols.jsonl"
                matches = []
                if symbols_file.exists():
                    for line in symbols_file.read_text(encoding="utf-8").splitlines():
                        if not line.strip():
                            continue
                        row = json.loads(line)
                        if sym_name.lower() in row.get("symbol", "").lower():
                            matches.append(row)
                            if len(matches) >= 10:
                                break
                return {
                    "symbol": sym_name,
                    "matches": matches,
                    "count": len(matches),
                    "source_head_sha": self._head_sha(),
                }
            return {
                "symbol": sym_name,
                "matches": results,
                "count": len(results),
                "source_head_sha": self._head_sha(),
            }

        elif name == "lda_callers":
            sym_id = args.get("symbol_id", "")
            return {"symbol_id": sym_id, "callers": self._storage.get_callers(sym_id)}

        elif name == "lda_callees":
            sym_id = args.get("symbol_id", "")
            return {"symbol_id": sym_id, "callees": self._storage.get_callees(sym_id)}

        elif name == "lda_references":
            sym_id = args.get("symbol_id", "")
            return {"symbol_id": sym_id, "references": self._storage.get_references(sym_id)}

        elif name == "lda_tests_for_symbol":
            sym_id = args.get("symbol_id", "")
            return {"symbol_id": sym_id, "tests": self._storage.get_tests_for_symbol(sym_id)}

        elif name == "lda_docs_for_symbol":
            sym_id = args.get("symbol_id", "")
            return {"symbol_id": sym_id, "docs": self._storage.get_docs_for_symbol(sym_id)}

        elif name == "lda_fts_search":
            query = args.get("query", "")
            limit = args.get("limit", 15)
            return {"query": query, "results": self._storage.search_fts(query, limit=limit)}

        elif name == "lda_map":
            return {"topology_map": self._storage.get_topology_map()}

        elif name == "lda_doctor":
            stats = self._storage.get_stats()
            healthy = self._index_health()
            return {
                "status": "HEALTHY" if healthy else "DEGRADED_EMPTY_INDEX",
                "index_healthy": healthy,
                "stats": stats,
                "coverage": self._storage.coverage_by_language(),
                "storage_db": str(self._storage.db_path),
                "source_head_sha": self._head_sha(),
                "profile": self._ctx.profile.name,
                "index_hint": (
                    "index is populated"
                    if healthy
                    else "index is EMPTY or cold; run 'lda index' — agents should "
                    "verify report.json status=VALIDATED first and fall back to "
                    "docs_rag_v0.py / rg when unhealthy"
                ),
            }

        elif name == "lda_check":
            from .core.healthcheck import run_healthcheck

            return run_healthcheck(self._ctx, self._storage)

        elif name == "lda_coverage":
            return self._storage.coverage_by_language()

        raise ValueError(f"Unknown tool: {name}")

    def run_stdio(self) -> None:
        """Run JSON-RPC loop over standard input."""
        logger.info("LDA MCP Server started on stdio (root: %s, profile: %s)", self._root, self._ctx.profile.name)
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except json.JSONDecodeError as exc:
                logger.error("JSON-RPC parsing error: %s", exc)
                sys.stdout.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {exc}"},
                }) + "\n")
                sys.stdout.flush()
                continue
            resp = self.handle_request(req)
            if resp is not None:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()


def main(argv: list[str] | None = None) -> None:
    from .core.paths import find_root

    parser = argparse.ArgumentParser(prog="lda-mcp", description="LDA Repository Intelligence MCP server (stdio)")
    parser.add_argument("--root", type=Path, default=None, help="Workspace root (default: discover from cwd)")
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else find_root()
    server = LDAMCPServer(root)
    server.run_stdio()


if __name__ == "__main__":
    main()
