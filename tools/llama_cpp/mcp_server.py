#!/usr/bin/env python3
"""Model Context Protocol (MCP) Server for direct llama.cpp execution.

Exposes llama-server capabilities over stdio JSON-RPC protocol:
- `llama_status`: Check server health, active model, and port.
- `llama_list_models`: Discovers available .gguf files across search paths.
- `llama_chat`: Execute chat completion with strict system prompt, min-p, and optional JSON schema.
- `llama_tokenize`: Tokenize text to check context size and count tokens.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from cli import check_server_health, scan_gguf_models, DEFAULT_HOST, DEFAULT_PORT


class LlamaMCPServer:
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"

    def handle_tool_call(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "llama_status":
            status = dict(check_server_health(self.base_url))
            include_template = bool(args.get("include_template") or args.get("show_template") or args.get("chat_template"))
            if not include_template and "props" in status and isinstance(status["props"], dict):
                props_clean = dict(status["props"])
                props_clean.pop("chat_template", None)
                props_clean.pop("template", None)
                if "default_generation_settings" in props_clean and isinstance(props_clean["default_generation_settings"], dict):
                    gen_clean = dict(props_clean["default_generation_settings"])
                    gen_clean.pop("chat_template", None)
                    gen_clean.pop("template", None)
                    props_clean["default_generation_settings"] = gen_clean
                status["props"] = props_clean
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(status, indent=2),
                    }
                ]
            }

        elif name == "llama_list_models":
            custom_dir = args.get("directory")
            search_dirs = [Path(custom_dir)] if custom_dir else None
            models = scan_gguf_models(search_dirs)
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({"count": len(models), "models": models}, indent=2),
                    }
                ]
            }

        elif name == "llama_chat":
            prompt = args.get("prompt", "").strip()
            if not prompt:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": "Error: 'prompt' parameter is required."}],
                }

            system_prompt = args.get("system", "")
            temperature = float(args.get("temperature", 0.2))
            min_p = float(args.get("min_p", 0.05))
            max_tokens = int(args.get("max_tokens", 2048))
            json_schema_str = args.get("json_schema")
            model_alias = args.get("model", "local-model")

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload: Dict[str, Any] = {
                "model": model_alias,
                "messages": messages,
                "temperature": temperature,
                "min_p": min_p,
                "max_tokens": max_tokens,
                "stream": False,
            }

            if json_schema_str:
                try:
                    schema_obj = json.loads(json_schema_str) if isinstance(json_schema_str, str) else json_schema_str
                    payload["response_format"] = {
                        "type": "json_object",
                        "schema": schema_obj,
                    }
                except Exception as exc:
                    return {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Invalid JSON schema: {exc}"}],
                    }

            req_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/v1/chat/completions",
                data=req_bytes,
                headers={"Content-Type": "application/json", "User-Agent": "llama-mcp/1.0"},
            )

            # At most 1 bounded retry (2 attempts total)
            max_attempts = 2
            last_error_code = "EMPTY_COMPLETION"
            last_error_detail = ""

            for attempt in range(max_attempts):
                t0 = time.perf_counter()
                try:
                    with urllib.request.urlopen(req, timeout=120.0) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        dt = time.perf_counter() - t0
                        choices = data.get("choices") or []
                        if not choices:
                            last_error_code = "EMPTY_COMPLETION"
                            last_error_detail = "Response contains no choices"
                            continue

                        choice = choices[0]
                        message = choice.get("message") if isinstance(choice, dict) else {}
                        content = message.get("content", "") if isinstance(message, dict) else ""
                        finish_reason = choice.get("finish_reason") if isinstance(choice, dict) else None

                        if not content or not content.strip():
                            if finish_reason == "length":
                                last_error_code = "MAX_TOKENS_WITHOUT_CONTENT"
                                last_error_detail = "Generation reached max_tokens with empty content"
                            else:
                                last_error_code = "EMPTY_COMPLETION"
                                last_error_detail = "Completion returned empty content"
                            continue

                        usage = data.get("usage", {})
                        return {
                            "content": [
                                {
                                    "type": "text",
                                    "text": content,
                                }
                            ],
                            "telemetry": {
                                "latency_seconds": round(dt, 3),
                                "usage": usage,
                                "attempts": attempt + 1,
                            }
                        }
                except Exception as exc:
                    last_error_code = "REQUEST_FAILED"
                    last_error_detail = f"Failed to communicate with llama-server at {self.base_url}: {exc}"
                    continue

            return {
                "isError": True,
                "error_code": last_error_code,
                "content": [
                    {
                        "type": "text",
                        "text": f"Error [{last_error_code}]: {last_error_detail} (after {max_attempts} attempts)",
                    }
                ]
            }

        elif name == "llama_tokenize":
            content = args.get("content", "")
            req_bytes = json.dumps({"content": content}).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/tokenize",
                data=req_bytes,
                headers={"Content-Type": "application/json", "User-Agent": "llama-mcp/1.0"},
            )
            try:
                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    tokens = data.get("tokens", [])
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps({"token_count": len(tokens), "tokens": tokens[:20]}, indent=2),
                            }
                        ]
                    }
            except Exception as exc:
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Tokenization failed: {exc}"}],
                }

        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
        }

    def run_stdio(self) -> None:
        """Run standard stdio JSON-RPC event loop."""
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
            except Exception:
                continue

            req_id = msg.get("id")
            method = msg.get("method")
            params = msg.get("params", {})

            if method == "notifications/initialized":
                continue

            try:
                if method == "initialize":
                    res = {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "llama-cpp-mcp", "version": "1.0.0"},
                        "capabilities": {"tools": {}},
                    }
                elif method == "tools/list":
                    res = {
                        "tools": [
                            {
                                "name": "llama_status",
                                "description": "Check if local llama-server is online, active slots, and loaded model.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                },
                            },
                            {
                                "name": "llama_list_models",
                                "description": "Scan and list available GGUF models on disk (e.g. ~/Models, ./models).",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "directory": {
                                            "type": "string",
                                            "description": "Optional custom directory path to scan for .gguf files.",
                                        }
                                    },
                                },
                            },
                            {
                                "name": "llama_chat",
                                "description": "Direct chat completion to llama-server with strict anti-hallucination sampling (Min-P, low temperature, JSON schema).",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "prompt": {
                                            "type": "string",
                                            "description": "User prompt or coding task.",
                                        },
                                        "system": {
                                            "type": "string",
                                            "description": "System instructions / role definition.",
                                        },
                                        "model": {
                                            "type": "string",
                                            "description": "Model alias name (default: local-model).",
                                        },
                                        "temperature": {
                                            "type": "number",
                                            "description": "Sampling temperature (default: 0.2).",
                                        },
                                        "min_p": {
                                            "type": "number",
                                            "description": "Min-P sampling cutoff (anti-hallucination threshold, default: 0.05).",
                                        },
                                        "max_tokens": {
                                            "type": "integer",
                                            "description": "Maximum completion tokens to generate.",
                                        },
                                        "json_schema": {
                                            "type": "string",
                                            "description": "Optional JSON Schema string to enforce strict structured grammar output.",
                                        },
                                    },
                                    "required": ["prompt"],
                                },
                            },
                            {
                                "name": "llama_tokenize",
                                "description": "Tokenize text using llama-server tokenizer to count tokens and prevent context overflow.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "content": {
                                            "type": "string",
                                            "description": "Text content to tokenize.",
                                        }
                                    },
                                    "required": ["content"],
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
    server = LlamaMCPServer()
    server.run_stdio()
