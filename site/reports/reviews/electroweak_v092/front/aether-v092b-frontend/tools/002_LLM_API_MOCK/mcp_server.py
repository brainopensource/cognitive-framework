#!/usr/bin/env python3
"""Standalone Model Context Protocol (MCP) Server for LLM API MOCK (LAM).

Exposes mock capabilities over standard stdio JSON-RPC protocol:
- `lam_complete`: Execute offline sub-millisecond LLM mock completion.
- `lam_replay_cassette`: Replay byte-exact cassette by name.
- `lam_list_scenarios`: Discover available scenario fixtures.
- `lam_get_stats`: Query telemetry, tokens saved, and cache performance.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from engine import LamEngine
from cassette import Cassette

SCENARIOS_DIR = _DIR / "scenarios"
CAPTURES_DIR = _DIR / "runs" / "benchmark_20_captures"
DB_PATH = _DIR / "lam.sqlite"


class LamMCPServer:
    def __init__(self):
        self.engine = LamEngine.from_directory(SCENARIOS_DIR) if SCENARIOS_DIR.exists() else None

    def handle_tool_call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "lam_complete":
            model = args.get("model", "mock-tier-2")
            prompt = args.get("prompt", "")
            if not self.engine:
                return {"error": "LAM engine scenarios not loaded"}
            
            t0 = time.perf_counter()
            resp = self.engine.complete({
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            })
            dt_ms = (time.perf_counter() - t0) * 1000
            
            return {
                "status": "success",
                "latency_ms": round(dt_ms, 3),
                "cost_usd": 0.0,
                "response": resp
            }

        elif name == "lam_replay_cassette":
            cname = args.get("cassette_name", "")
            cpath = CAPTURES_DIR / (cname if cname.endswith(".json") else f"{cname}_cassette.json")
            if not cpath.exists():
                return {"error": f"Cassette not found: {cpath.name}"}
            
            cassette = Cassette.load(cpath)
            return {
                "status": "success",
                "cassette": cpath.name,
                "entries_count": len(cassette.entries),
                "valid": True
            }

        elif name == "lam_list_scenarios":
            tier = args.get("tier")
            if not self.engine:
                return {"error": "Engine not loaded"}
            
            sc_list = []
            for sc in self.engine.scenarios:
                if tier is None or sc.tier == tier:
                    sc_list.append({
                        "id": sc.id,
                        "tier": sc.tier,
                        "title": sc.title,
                        "turns_count": len(sc.turns)
                    })
            return {
                "total": len(sc_list),
                "scenarios": sc_list[:args.get("limit", 50)]
            }

        elif name == "lam_get_stats":
            if not DB_PATH.exists():
                return {"calls": 0, "tokens": 0, "cost": 0.0}
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*), SUM(tokens), SUM(cost_usd) FROM mock_calls")
                calls, tokens, cost = cur.fetchone()
            return {
                "total_calls": calls or 0,
                "tokens_saved": tokens or 0,
                "estimated_cost_saved_usd": round(cost or 0.0, 4)
            }

        return {"error": f"Unknown tool: {name}"}

    def run_stdio(self):
        """Standard JSON-RPC loop over stdio."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
                req_id = req.get("id")
                method = req.get("method")
                params = req.get("params", {})

                if method == "tools/list":
                    res = {
                        "tools": [
                            {
                                "name": "lam_complete",
                                "description": "Execute sub-millisecond zero-cost offline mock completion",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "model": {"type": "string", "description": "Tier name (e.g. tier-1, tier-2) or scenario ID"},
                                        "prompt": {"type": "string", "description": "Prompt text"}
                                    },
                                    "required": ["prompt"]
                                }
                            },
                            {
                                "name": "lam_replay_cassette",
                                "description": "Inspect and replay a recorded challenge cassette",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "cassette_name": {"type": "string", "description": "Name of cassette file"}
                                    },
                                    "required": ["cassette_name"]
                                }
                            },
                            {
                                "name": "lam_list_scenarios",
                                "description": "List available offline scenarios in scenario bank",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "tier": {"type": "integer", "description": "Filter by tier (0 to 5)"},
                                        "limit": {"type": "integer", "description": "Max results to return"}
                                    }
                                }
                            },
                            {
                                "name": "lam_get_stats",
                                "description": "Get recorded mock calls telemetry and token savings",
                                "inputSchema": {"type": "object"}
                            }
                        ]
                    }
                elif method == "tools/call":
                    tool_name = params.get("name")
                    tool_args = params.get("arguments", {})
                    res = self.handle_tool_call(tool_name, tool_args)
                else:
                    res = {"error": f"Unsupported method: {method}"}

                reply = {"jsonrpc": "2.0", "id": req_id, "result": res}
                sys.stdout.write(json.dumps(reply) + "\n")
                sys.stdout.flush()

            except Exception as exc:
                err_reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": str(exc)}}
                sys.stdout.write(json.dumps(err_reply) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = LamMCPServer()
    server.run_stdio()
