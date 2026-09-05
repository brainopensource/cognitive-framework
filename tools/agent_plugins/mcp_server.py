#!/usr/bin/env python3
"""Model Context Protocol (MCP) Server for Vanguard / AETHER Agent Capabilities.

Exposes declarative agent skills, techniques, and proficiencies over stdio JSON-RPC:
- `agent_list_plugins`: Enumerate skills, techniques, and proficiencies with prefix tokens.
- `agent_run_test`: Execute isolated tests under bounded timeout protection.
- `agent_generate_patch`: Spec-driven grounded code synthesis via LDA + local LLM.
- `agent_run_falsifier`: Discover and run targeted test falsifiers for touched code.
- `agent_autofix`: Execute closed-loop SWE multi-turn repair with fail-closed rollback.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from vanguard.packages.runtime.agent_plugins import (
    PluginSpec,
    build_plugin_index,
    filter_plugins,
    load_agent_plugins,
)

# Technique & skill runners
TEST_RUNNER = REPO_ROOT / ".agents/skills/test-runner/scripts/run_test.py"
T1_RUNNER = REPO_ROOT / ".agents/techniques/spec-driven-codegen/scripts/generate_grounded_patch.py"
T2_RUNNER = REPO_ROOT / ".agents/techniques/tdd-falsifier/scripts/run_falsifier.py"
AUTOFIX_RUNNER = REPO_ROOT / ".agents/proficiencies/autofix-swe-loop/scripts/autofix_harness.py"

# Direct imports if available
sys.path.insert(0, str(TEST_RUNNER.parent))
sys.path.insert(0, str(T1_RUNNER.parent))
sys.path.insert(0, str(T2_RUNNER.parent))
sys.path.insert(0, str(AUTOFIX_RUNNER.parent))

from run_test import run_isolated_test
from generate_grounded_patch import generate_patch
from run_falsifier import run_falsifier
from autofix_harness import execute_autofix_loop


class AgentCapabilitiesMCPServer:
    def __init__(self):
        self.plugins = load_agent_plugins(REPO_ROOT)

    def handle_tool_call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "agent_list_plugins":
            category = args.get("category")
            filtered = filter_plugins(self.plugins, categories=[category] if category else None)
            index = build_plugin_index(filtered)
            data = {
                "total_plugins": len(filtered),
                "prefix_chars": index.size_chars,
                "budget_chars": index.budget_chars,
                "dropped": index.dropped,
                "plugins": [
                    {
                        "name": p.name,
                        "category": p.category,
                        "mode": p.mode,
                        "description": p.description,
                        "doc_path": p.doc_path,
                        "has_runner": bool(p.runner_path),
                        "composes_skills": p.composes_skills,
                        "composes_techniques": p.composes_techniques,
                    }
                    for p in filtered
                ],
                "rendered_prefix": index.render(),
            }
            return {
                "content": [{"type": "text", "text": json.dumps(data, indent=2)}]
            }

        elif name == "agent_run_test":
            cmd = args.get("command", "")
            timeout = float(args.get("timeout", 15.0))
            cwd = args.get("cwd", ".")
            result = run_isolated_test(cmd, timeout=timeout, cwd=cwd)
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }

        elif name == "agent_generate_patch":
            task = args.get("task", "")
            target_file = args.get("target_file")
            error_feedback = args.get("error_feedback")
            budget = int(args.get("budget", 2500))
            default_model = os.environ.get("VANGUARD_LLAMA_MODEL") or str(Path.home() / "Models" / "Qwen2.5-Coder-1.5B-Instruct-Q4_K_M.gguf")
            model_path = args.get("model_path", default_model)
            port = int(args.get("port", 8080))
            result = generate_patch(
                task=task,
                target_file=target_file,
                error_feedback=error_feedback,
                budget=budget,
                model_path=model_path,
                port=port,
                auto_manage_server=True
            )
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }

        elif name == "agent_run_falsifier":
            target_file = args.get("target_file")
            test_cmd = args.get("test_cmd")
            timeout = float(args.get("timeout", 15.0))
            result = run_falsifier(
                target_path=target_file,
                explicit_cmd=test_cmd,
                timeout=timeout
            )
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }

        elif name == "agent_autofix":
            task = args.get("task", "")
            target_file = args.get("target_file", "")
            test_cmd = args.get("test_cmd")
            max_turns = int(args.get("max_turns", 3))
            budget = int(args.get("budget", 2500))
            timeout = float(args.get("timeout", 15.0))
            result = execute_autofix_loop(
                task=task,
                target_file=target_file,
                test_cmd=test_cmd,
                max_turns=max_turns,
                timeout=timeout,
                budget=budget
            )
            return {
                "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
            }

        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        }

    def run_stdio(self) -> None:
        """Run standard stdio line-delimited JSON-RPC loop."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            req_id = None
            try:
                req = json.loads(line)
                req_id = req.get("id")
                method = req.get("method")
                params = req.get("params", {})

                if method == "initialize":
                    res = {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "vanguard-agent-capabilities",
                            "version": "1.0.0",
                        },
                    }
                elif method == "tools/list":
                    res = {
                        "tools": [
                            {
                                "name": "agent_list_plugins",
                                "description": "List all declarative skills, techniques, and proficiencies with prefix token budgets.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "category": {
                                            "type": "string",
                                            "enum": ["skill", "technique", "proficiency"],
                                            "description": "Optional category filter.",
                                        }
                                    },
                                },
                            },
                            {
                                "name": "agent_run_test",
                                "description": "Execute tests in an isolated, timeout-bounded subprocess, capturing exit code and structured diagnostics.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "command": {"type": "string", "description": "Test command to execute."},
                                        "timeout": {"type": "number", "description": "Timeout in seconds (default: 15.0)."},
                                        "cwd": {"type": "string", "description": "Working directory."},
                                    },
                                    "required": ["command"],
                                },
                            },
                            {
                                "name": "agent_generate_patch",
                                "description": "Spec-driven grounded code synthesis via LDA fact graph and local LLM.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task": {"type": "string", "description": "Task description or defect explanation."},
                                        "target_file": {"type": "string", "description": "Path to file being modified."},
                                        "error_feedback": {"type": "string", "description": "Feedback or traceback from prior test failure."},
                                        "budget": {"type": "integer", "description": "Token budget for LDA AST context."},
                                    },
                                    "required": ["task"],
                                },
                            },
                            {
                                "name": "agent_run_falsifier",
                                "description": "Locate and execute correlated test falsifiers for any touched file using the LDA SQLite fact graph.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "target_file": {"type": "string", "description": "Target source file to falsify."},
                                        "test_cmd": {"type": "string", "description": "Optional explicit test command override."},
                                        "timeout": {"type": "number", "description": "Execution timeout in seconds."},
                                    },
                                },
                            },
                            {
                                "name": "agent_autofix",
                                "description": "Autonomous closed feedback loop SWE repair engine with state, iterative test feedback, and fail-closed rollback.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "task": {"type": "string", "description": "Defect description to repair."},
                                        "target_file": {"type": "string", "description": "File path to repair."},
                                        "test_cmd": {"type": "string", "description": "Test command to verify fix."},
                                        "max_turns": {"type": "integer", "description": "Max repair turns (default: 3)."},
                                    },
                                    "required": ["task", "target_file"],
                                },
                            },
                        ]
                    }
                elif method == "tools/call":
                    tool_name = params.get("name", "")
                    tool_args = params.get("arguments", {})
                    res = self.handle_tool_call(tool_name, tool_args)
                else:
                    res = {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Unsupported method: {method}"}],
                    }

                reply = {"jsonrpc": "2.0", "id": req_id, "result": res}
                sys.stdout.write(json.dumps(reply) + "\n")
                sys.stdout.flush()

            except Exception as exc:
                err_reply = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32603, "message": str(exc)},
                }
                sys.stdout.write(json.dumps(err_reply) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    server = AgentCapabilitiesMCPServer()
    server.run_stdio()
