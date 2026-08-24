#!/usr/bin/env python3
"""Standalone LLM API Mock Server [DEPRECATED -> Use server.py instead].

DEPRECATED: Prefer server.py (the unified LAM HTTP server) which supports
OpenAI + Ollama wire protocols, live proxy mode, and explicit evidence labels.
"""

from __future__ import annotations
import warnings
warnings.warn(
    "mock_server.py is deprecated; use server.py (unified LAM server) instead.",
    DeprecationWarning,
    stacklevel=2,
)

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from catalog import Catalog, Reply, Scenario, ToolCallSpec, load_catalog, select_reply, select_tool_step
from cassette import Cassette
from recorder import MockRecorder


# Tier aliases mapping
TIER_ALIASES = {
    # Tier 1: Toy / Small
    "qwen2.5:1.5b": 1,
    "llama3.2:3b": 1,
    "tier-1": 1,
    "mock-tier-1": 1,
    # Tier 2: Small / Free / Cheap
    "qwen3.6:27b": 2,
    "deepseek-r1:14b": 2,
    "openrouter/free": 2,
    "tier-2": 2,
    "mock-tier-2": 2,
    # Tier 3: Strong Flash / Mid
    "deepseek/deepseek-chat": 3,
    "google/gemini-2.0-flash-001": 3,
    "qwen/qwen-2.5-72b-instruct": 3,
    "tier-3": 3,
    "mock-tier-3": 3,
    # Tier 4: Frontier SOTA
    "anthropic/claude-3.5-sonnet": 4,
    "openai/gpt-4o": 4,
    "tier-4": 4,
    "mock-tier-4": 4,
}


def _chunk_text(text: str) -> List[str]:
    """Split response text into realistic token/word chunks for SSE streaming."""
    words = text.split(" ")
    chunks: list[str] = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + 3])
        if i + 3 < len(words):
            chunk += " "
        chunks.append(chunk)
        i += 3
    return chunks if chunks else [text]


class MockServerHandler(BaseHTTPRequestHandler):
    catalog: Optional[Catalog] = None
    cassette: Optional[Cassette] = None
    recorder: Optional[MockRecorder] = None
    latency_ms: int = 0
    default_tier: int = 2

    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("X-Mock-Catalog-SHA256", self.catalog.sha256 if self.catalog else "none")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "catalog_sha256": self.catalog.sha256 if self.catalog else None})
            return

        if self.path in ("/v1/models", "/models"):
            models_list = [
                {"id": name, "object": "model", "owned_by": f"tier-{tier}"}
                for name, tier in TIER_ALIASES.items()
            ]
            self._send_json(200, {"object": "list", "data": models_list})
            return

        if self.path == "/tiers":
            self._send_json(
                200,
                {
                    "1": "Toy / Minimal LLM (e.g. qwen2.5:1.5b, llama3.2:3b)",
                    "2": "Cheap / Local Mid LLM (e.g. qwen3.6:27b, deepseek-r1:14b)",
                    "3": "Strong Flash / Coding LLM (e.g. deepseek-chat, gemini-2.0-flash)",
                    "4": "Frontier SOTA (e.g. claude-3.5-sonnet, gpt-4o)",
                },
            )
            return

        self._send_json(404, {"error": "Not Found", "path": self.path})

    def do_POST(self) -> None:
        content_len = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        # 1. Cassette mode check
        if self.cassette is not None:
            step = self.cassette.replay(raw_body)
            if step is None:
                self._send_json(409, {"error": "cassette_mismatch", "request_sha256": hashlib.sha256(raw_body).hexdigest()})
                return
            self.send_response(step.status_code)
            self.send_header("Content-Type", step.content_type)
            self.send_header("Content-Length", str(len(step.response_body)))
            self.end_headers()
            self.wfile.write(step.response_body)
            return

        # 2. Scripted Catalog mode
        try:
            req_data = json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            self._send_json(400, {"error": "Invalid JSON body", "detail": str(exc)})
            return

        # Resolve tier
        header_tier = self.headers.get("X-Mock-Tier")
        req_model = req_data.get("model", "")
        if header_tier and header_tier.isdigit():
            tier = int(header_tier)
        elif req_model in TIER_ALIASES:
            tier = TIER_ALIASES[req_model]
        else:
            tier = self.default_tier

        # Extract full conversation text and tool count
        messages = req_data.get("messages", [])
        prompt_text = req_data.get("prompt", "")
        tool_results_seen = 0

        if messages:
            history_lines: list[str] = []
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                if role == "tool":
                    tool_results_seen += 1
                if isinstance(content, str) and content:
                    history_lines.append(content)
            prompt_text = "\n".join(history_lines)

        # Resolve scenario
        header_scenario = self.headers.get("X-Mock-Scenario")
        scenario: Optional[Scenario] = None

        if self.catalog:
            if header_scenario and header_scenario in self.catalog.scenarios:
                scenario = self.catalog.scenarios[header_scenario]
            else:
                # Match by keyword in prompt text
                for sc in self.catalog.scenarios.values():
                    if any(kw.lower() in prompt_text.lower() for kw in sc.keywords):
                        scenario = sc
                        break
                if scenario is None:
                    scenario = self.catalog.default_scenario

        if scenario is None:
            self._send_json(500, {"error": "No scenario available in catalog"})
            return

        # Select reply
        is_tool_mode = bool(scenario.replies.get(tier, [None])[0] and scenario.replies[tier][0].tool_calls)
        if is_tool_mode:
            selection = select_tool_step(scenario, tier, tool_results_seen=tool_results_seen)
        else:
            selection = select_reply(scenario, tier, prompt_text)

        reply: Reply = selection.reply

        # Record provenance if enabled
        if self.recorder:
            req_hash = hashlib.sha256(raw_body).hexdigest()
            self.recorder.record_call(
                request_sha256=req_hash,
                scenario_key=scenario.key,
                tier=tier,
                requested_turn=selection.requested_turn,
                returned_turn=reply.turn,
                reply_sha256=reply.sha256,
                source_label=self.headers.get("X-Mock-Source", ""),
                run_id=self.headers.get("X-Mock-Run-Id", ""),
                prompt=prompt_text,
                response=reply.text,
            )

        stream = bool(req_data.get("stream", False))

        # Handle Ollama native format
        if "/api/generate" in self.path:
            self._handle_ollama_response(reply, req_model, stream)
            return

        # Handle OpenAI / OpenRouter format
        self._handle_openai_response(reply, req_model, stream)

    def _handle_openai_response(self, reply: Reply, model: str, stream: bool) -> None:
        created_ts = int(time.time())
        call_id = f"chatcmpl-{uuid.uuid4()}"

        if not stream:
            choice: dict[str, Any] = {
                "index": 0,
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": reply.text if not reply.tool_calls else None,
                },
            }
            if reply.tool_calls:
                choice["finish_reason"] = "tool_calls"
                choice["message"]["tool_calls"] = [
                    {
                        "id": tc.call_id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": tc.arguments,
                        },
                    }
                    for tc in reply.tool_calls
                ]

            payload = {
                "id": call_id,
                "object": "chat.completion",
                "created": created_ts,
                "model": model or "mock-tier-model",
                "choices": [choice],
                "usage": {
                    "prompt_tokens": 15,
                    "completion_tokens": len(reply.text.split()),
                    "total_tokens": 15 + len(reply.text.split()),
                },
            }
            self._send_json(200, payload)
            return

        # SSE Streaming response
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.end_headers()

        chunks = _chunk_text(reply.text)
        for chunk in chunks:
            if self.latency_ms > 0:
                time.sleep(self.latency_ms / 1000.0)
            data_frame = {
                "id": call_id,
                "object": "chat.completion.chunk",
                "created": created_ts,
                "model": model or "mock-tier-model",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": None,
                    }
                ],
            }
            self.wfile.write(f"data: {json.dumps(data_frame)}\n\n".encode("utf-8"))
            self.wfile.flush()

        final_frame = {
            "id": call_id,
            "object": "chat.completion.chunk",
            "created": created_ts,
            "model": model or "mock-tier-model",
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
        }
        self.wfile.write(f"data: {json.dumps(final_frame)}\n\n".encode("utf-8"))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def _handle_ollama_response(self, reply: Reply, model: str, stream: bool) -> None:
        if not stream:
            payload = {
                "model": model,
                "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "response": reply.text,
                "done": True,
                "eval_count": len(reply.text.split()),
                "prompt_eval_count": 12,
            }
            self._send_json(200, payload)
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson")
        self.send_header("Connection", "close")
        self.end_headers()

        chunks = _chunk_text(reply.text)
        for chunk in chunks:
            if self.latency_ms > 0:
                time.sleep(self.latency_ms / 1000.0)
            frame = {"model": model, "response": chunk, "done": False}
            self.wfile.write(f"{json.dumps(frame)}\n".encode("utf-8"))
            self.wfile.flush()

        final_frame = {"model": model, "response": "", "done": True}
        self.wfile.write(f"{json.dumps(final_frame)}\n".encode("utf-8"))
        self.wfile.flush()

    def log_message(self, format: str, *args: Any) -> None:
        pass  # Quiet stdout during mock serving


def run_server(
    host: str = "127.0.0.1",
    port: int = 4141,
    answer_bank: Optional[Path] = None,
    cassette_path: Optional[Path] = None,
    record_db: Optional[Path] = None,
    latency_ms: int = 0,
    default_tier: int = 2,
) -> None:
    catalog: Optional[Catalog] = None
    if answer_bank and answer_bank.is_dir():
        catalog = load_catalog(answer_bank)
        print(f"[LAM Mock] Loaded Answer Bank with {len(catalog.scenarios)} scenarios. SHA-256: {catalog.sha256[:12]}...")

    cassette: Optional[Cassette] = None
    if cassette_path and cassette_path.is_file():
        cassette = Cassette.load(cassette_path)
        print(f"[LAM Mock] Loaded Cassette with {len(cassette.steps)} steps from {cassette_path.name}")

    recorder: Optional[MockRecorder] = None
    if record_db:
        recorder = MockRecorder(record_db)
        print(f"[LAM Mock] Recording provenance to SQLite: {record_db}")

    MockServerHandler.catalog = catalog
    MockServerHandler.cassette = cassette
    MockServerHandler.recorder = recorder
    MockServerHandler.latency_ms = latency_ms
    MockServerHandler.default_tier = default_tier

    server = HTTPServer((host, port), MockServerHandler)
    print(f"[LAM Mock] Server listening on http://{host}:{port} (OpenAI & Ollama compatible)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[LAM Mock] Stopping server.")
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="LAM Stateless Multi-Tier Mock LLM Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=4141, help="Port to listen on (default: 4141)")
    parser.add_argument(
        "--answer-bank",
        type=Path,
        default=Path(__file__).resolve().parent / "answer_bank",
        help="Path to Answer Bank catalog directory",
    )
    parser.add_argument("--cassette", type=Path, default=None, help="Path to cassette file for replay")
    parser.add_argument("--record-db", type=Path, default=None, help="Path to SQLite DB for recording provenance")
    parser.add_argument("--latency-ms", type=int, default=0, help="Artificial delay between SSE stream chunks in ms")
    parser.add_argument("--default-tier", type=int, default=2, choices=[1, 2, 3, 4], help="Default capability tier (1-4)")

    args = parser.parse_args()
    run_server(
        host=args.host,
        port=args.port,
        answer_bank=args.answer_bank,
        cassette_path=args.cassette,
        record_db=args.record_db,
        latency_ms=args.latency_ms,
        default_tier=args.default_tier,
    )


if __name__ == "__main__":
    main()
