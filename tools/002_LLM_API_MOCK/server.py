"""Unified, dependency-free LAM HTTP server.

Supports:
1. Gold scenario replay (OpenAI /v1/chat/completions and Ollama /api/chat, /api/generate)
2. Live proxy to upstream Ollama (e.g. host Ollama from WSL2)
3. Byte-exact Cassette replay
4. Full call provenance logging to SQLite with explicit evidence_label
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

_DIR = Path(__file__).resolve().parent
if str(_DIR) not in sys.path:
    sys.path.insert(0, str(_DIR))

from cassette import Cassette
from engine import LamEngine
from recorder import MockRecorder

# Tier aliases mapping for fallback catalog matching
TIER_ALIASES: dict[str, int] = {
    "qwen2.5:1.5b": 1,
    "llama3.2:3b": 1,
    "tier-1": 1,
    "mock-tier-1": 1,
    "qwen3.6:27b": 2,
    "deepseek-r1:14b": 2,
    "openrouter/free": 2,
    "tier-2": 2,
    "mock-tier-2": 2,
    "deepseek/deepseek-chat": 3,
    "google/gemini-2.0-flash-001": 3,
    "qwen/qwen-2.5-72b-instruct": 3,
    "tier-3": 3,
    "mock-tier-3": 3,
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


class LamServerHandler(BaseHTTPRequestHandler):
    engine: Optional[LamEngine] = None
    cassette: Optional[Cassette] = None
    recorder: Optional[MockRecorder] = None
    upstream_url: Optional[str] = None
    default_mode: str = "replay"  # "replay" | "proxy" | "cassette"

    def log_message(self, format: str, *args: Any) -> None:
        return  # Quiet logging

    def _send_json(
        self,
        status: int,
        payload: Dict[str, Any],
        evidence_label: str = "lam-replay",
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        raw = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("X-Evidence-Label", evidence_label)
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        path = self.path.split("?")[0].rstrip("/")

        if path in ("/health", ""):
            mode = "cassette" if self.cassette else ("proxy" if self.upstream_url else "replay")
            evidence_label = "cassette-exact" if mode == "cassette" else ("ollama-live" if mode == "proxy" else "lam-replay")
            n_scenarios = len(self.engine.scenarios) if self.engine else 0
            self._send_json(
                200,
                {
                    "status": "ok",
                    "mode": mode,
                    "evidence_label": evidence_label,
                    "upstream": self.upstream_url,
                    "scenarios_count": n_scenarios,
                },
                evidence_label=evidence_label,
            )
            return

        if path in ("/v1/models", "/models"):
            models_list = []
            if self.engine:
                for sc in self.engine.scenarios:
                    models_list.append({"id": f"lam/{sc.id}", "object": "model", "owned_by": f"tier-{sc.tier}"})
            for name, tier in TIER_ALIASES.items():
                models_list.append({"id": name, "object": "model", "owned_by": f"tier-{tier}"})
            self._send_json(200, {"object": "list", "data": models_list}, evidence_label="lam-replay")
            return

        if path == "/api/tags":
            if self.upstream_url:
                # Proxy to upstream tags
                target = f"{self.upstream_url.rstrip('/')}/api/tags"
                try:
                    req = urllib.request.Request(target, method="GET")
                    with urllib.request.urlopen(req, timeout=3.0) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        self._send_json(200, data, evidence_label="ollama-live")
                        return
                except Exception as exc:
                    self._send_json(
                        503,
                        {"error": "provider_unreachable", "detail": f"upstream tags failed: {exc}"},
                        evidence_label="ollama-live",
                    )
                    return
            # Advertise lam/* tags
            tags = []
            if self.engine:
                for sc in self.engine.scenarios:
                    tags.append({"name": f"lam/{sc.id}", "model": f"lam/{sc.id}", "details": {"family": "lam", "tier": sc.tier}})
            self._send_json(200, {"models": tags}, evidence_label="lam-replay")
            return

        self._send_json(404, {"error": {"message": f"not found: {self.path}", "type": "invalid_request_error"}})

    def do_POST(self) -> None:
        content_len = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
        path = self.path.split("?")[0].rstrip("/")

        # 1. Cassette exact replay check
        if self.cassette is not None:
            step = self.cassette.replay(raw_body)
            if step is None:
                self._send_json(
                    409,
                    {"error": "cassette_mismatch", "request_sha256": hashlib.sha256(raw_body).hexdigest()},
                    evidence_label="cassette-exact",
                )
                return
            self.send_response(step.status_code)
            self.send_header("Content-Type", step.content_type)
            self.send_header("Content-Length", str(len(step.response_body)))
            self.send_header("X-Evidence-Label", "cassette-exact")
            self.end_headers()
            self.wfile.write(step.response_body)
            return

        # 2. Parse JSON body
        try:
            body = json.loads(raw_body.decode("utf-8"))
        except Exception as exc:
            self._send_json(400, {"error": {"message": f"invalid json: {exc}", "type": "invalid_request_error"}})
            return

        model_name = str(body.get("model") or "")
        is_lam_model = model_name.startswith("lam/") or (self.engine and model_name in self.engine._by_id)

        # 3. Route logic: Proxy vs Gold Replay
        if not is_lam_model and self.upstream_url:
            self._proxy_to_upstream(path, raw_body, body)
            return

        if not is_lam_model and not self.engine:
            self._send_json(
                503,
                {"error": "provider_unreachable", "message": "no upstream configured and no gold engine loaded"},
                evidence_label="ollama-live",
            )
            return

        # Gold scenario completion
        if path in ("/v1/chat/completions", "/chat/completions"):
            self._handle_openai_completion(body, raw_body)
        elif path in ("/api/chat", "/api/generate"):
            self._handle_ollama_completion(path, body, raw_body)
        else:
            self._send_json(404, {"error": {"message": f"unknown route: {path}", "type": "invalid_request_error"}})

    def _proxy_to_upstream(self, path: str, raw_body: bytes, body: dict[str, Any]) -> None:
        target = f"{self.upstream_url.rstrip('/')}{path}"
        # Forward content type and Authorization header (MITM: pass client creds to upstream)
        fwd_headers: dict[str, str] = {"Content-Type": "application/json"}
        auth = self.headers.get("Authorization")
        if auth:
            fwd_headers["Authorization"] = auth
        req = urllib.request.Request(target, data=raw_body, headers=fwd_headers, method="POST")
        start_t = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=120.0) as resp:
                resp_bytes = resp.read()
                elapsed_ms = int((time.monotonic() - start_t) * 1000)
                resp_status = int(resp.status)

                # Extract token usage from upstream JSON response (OpenAI or Ollama shape)
                tokens = 0
                prompt_tokens = 0
                completion_tokens = 0
                cost_usd: float | None = None
                try:
                    resp_json = json.loads(resp_bytes.decode("utf-8"))
                    usage = resp_json.get("usage") or {}
                    prompt_tokens = int(usage.get("prompt_tokens") or usage.get("prompt_eval_count") or 0)
                    completion_tokens = int(usage.get("completion_tokens") or usage.get("eval_count") or 0)
                    tokens = int(usage.get("total_tokens") or (prompt_tokens + completion_tokens))
                    # OpenRouter surfaces cost in usage.cost (USD float)
                    raw_cost = usage.get("cost")
                    if raw_cost is not None:
                        cost_usd = float(raw_cost)
                except Exception:
                    pass

                # Record provenance with full usage
                if self.recorder:
                    self.recorder.record_call(
                        request_sha256=hashlib.sha256(raw_body).hexdigest(),
                        scenario_key=str(body.get("model", "upstream")),
                        tier=1,
                        requested_turn=0,
                        returned_turn=0,
                        reply_sha256=hashlib.sha256(resp_bytes).hexdigest(),
                        source_label="ollama-live",
                        run_id=self.headers.get("X-Mock-Run-Id", ""),
                        prompt=str(body.get("prompt") or body.get("messages", ""))[:200],
                        response=resp_bytes.decode("utf-8", errors="replace")[:200],
                        evidence_label="ollama-live",
                        tokens=tokens,
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        cost_usd=cost_usd,
                        millis=elapsed_ms,
                    )

                self.send_response(resp_status)
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(resp_bytes)))
                self.send_header("X-Evidence-Label", "ollama-live")
                self.end_headers()
                self.wfile.write(resp_bytes)
        except urllib.error.HTTPError as exc:
            err_body = exc.read()
            self.send_response(exc.code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err_body)))
            self.send_header("X-Evidence-Label", "ollama-live")
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as exc:
            self._send_json(
                503,
                {"error": "provider_unreachable", "detail": f"upstream connection failed: {exc}"},
                evidence_label="ollama-live",
            )

    def _handle_openai_completion(self, body: dict[str, Any], raw_body: bytes) -> None:
        if not self.engine:
            self._send_json(500, {"error": {"message": "LAM engine not initialized"}})
            return

        model_name = str(body.get("model") or "")
        # Normalize model name
        if not model_name.startswith("lam/"):
            if model_name in self.engine._by_id:
                body["model"] = f"lam/{model_name}"
            elif model_name == "" or model_name.startswith("lam"):
                # Empty or ambiguous lam prefix: use default
                body["model"] = "lam/t1-calculator"
            else:
                # Unknown model that is not a lam/* id — fail explicitly
                self._send_json(
                    404,
                    {"error": {"message": f"unknown model: {model_name!r}; use lam/<scenario-id> or a lam/* alias", "type": "invalid_request_error"}},
                    evidence_label="lam-replay",
                )
                return

        start_t = time.monotonic()
        try:
            completion = self.engine.complete(body)
        except KeyError as exc:
            self._send_json(404, {"error": {"message": f"unknown lam scenario: {exc}", "type": "invalid_request_error"}})
            return
        except Exception as exc:
            self._send_json(500, {"error": {"message": f"engine completion error: {exc}", "type": "server_error"}})
            return

        elapsed_ms = max(1, int((time.monotonic() - start_t) * 1000))
        resp_bytes = json.dumps(completion, indent=2).encode("utf-8")

        # Record provenance
        if self.recorder:
            choice = completion.get("choices", [{}])[0]
            msg = choice.get("message", {})
            self.recorder.record_call(
                request_sha256=hashlib.sha256(raw_body).hexdigest(),
                scenario_key=str(body.get("model", "")),
                tier=int(completion.get("lam", {}).get("tier", 1)),
                requested_turn=int(completion.get("lam", {}).get("tool_messages", 0)),
                returned_turn=int(completion.get("lam", {}).get("tool_messages", 0)),
                reply_sha256=hashlib.sha256(resp_bytes).hexdigest(),
                source_label=self.headers.get("X-Mock-Source", "lam-replay"),
                run_id=self.headers.get("X-Mock-Run-Id", ""),
                prompt=str(body.get("messages", ""))[:200],
                response=str(msg.get("content") or msg.get("tool_calls", ""))[:200],
                evidence_label="lam-replay",
                tokens=completion.get("usage", {}).get("total_tokens", 0),
                millis=elapsed_ms,
            )

        stream = bool(body.get("stream", False))
        if not stream:
            self._send_json(200, completion, evidence_label="lam-replay")
            return

        # SSE Streaming for OpenAI
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.send_header("X-Evidence-Label", "lam-replay")
        self.end_headers()

        call_id = completion.get("id", "chatcmpl-lam")
        created_ts = int(time.time())
        first_choice = completion.get("choices", [{}])[0]
        msg = first_choice.get("message", {})
        content = msg.get("content") or ""
        tool_calls = msg.get("tool_calls") or []

        if content:
            chunks = _chunk_text(content)
            for chunk in chunks:
                frame = {
                    "id": call_id,
                    "object": "chat.completion.chunk",
                    "created": created_ts,
                    "model": body.get("model"),
                    "choices": [{"index": 0, "delta": {"content": chunk}, "finish_reason": None}],
                }
                self.wfile.write(f"data: {json.dumps(frame)}\n\n".encode("utf-8"))
                self.wfile.flush()

        if tool_calls:
            for idx, tc in enumerate(tool_calls):
                func = tc.get("function", {})
                frame = {
                    "id": call_id,
                    "object": "chat.completion.chunk",
                    "created": created_ts,
                    "model": body.get("model"),
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "tool_calls": [
                                    {
                                        "index": idx,
                                        "id": tc.get("id", f"call_{idx}"),
                                        "type": "function",
                                        "function": {
                                            "name": func.get("name", ""),
                                            "arguments": func.get("arguments", "{}") if isinstance(func.get("arguments"), str) else json.dumps(func.get("arguments", {})),
                                        },
                                    }
                                ]
                            },
                            "finish_reason": None,
                        }
                    ],
                }
                self.wfile.write(f"data: {json.dumps(frame)}\n\n".encode("utf-8"))
                self.wfile.flush()

        final_frame = {
            "id": call_id,
            "object": "chat.completion.chunk",
            "created": created_ts,
            "model": body.get("model"),
            "choices": [{"index": 0, "delta": {}, "finish_reason": first_choice.get("finish_reason", "stop")}],
        }
        self.wfile.write(f"data: {json.dumps(final_frame)}\n\n".encode("utf-8"))
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def _handle_ollama_completion(self, path: str, body: dict[str, Any], raw_body: bytes) -> None:
        if not self.engine:
            self._send_json(500, {"error": "LAM engine not initialized"})
            return

        model_name = str(body.get("model") or "")
        if not model_name.startswith("lam/"):
            if model_name in self.engine._by_id:
                body["model"] = f"lam/{model_name}"
            elif model_name == "" or model_name.startswith("lam"):
                body["model"] = "lam/t1-calculator"
            else:
                self._send_json(
                    404,
                    {"error": {"message": f"unknown model: {model_name!r}; use lam/<scenario-id> or a lam/* alias", "type": "invalid_request_error"}},
                    evidence_label="lam-replay",
                )
                return

        # Adapt messages if calling /api/generate
        if path == "/api/generate" and "messages" not in body:
            prompt = body.get("prompt", "")
            body["messages"] = [{"role": "user", "content": prompt}]

        start_t = time.monotonic()
        try:
            completion = self.engine.complete(body)
        except Exception as exc:
            self._send_json(500, {"error": f"engine completion error: {exc}"})
            return

        elapsed_ms = max(1, int((time.monotonic() - start_t) * 1000))
        first_choice = completion.get("choices", [{}])[0]
        msg = first_choice.get("message", {})
        content = msg.get("content") or ""
        tool_calls = msg.get("tool_calls") or []

        # Convert tool calls to Ollama structure if present
        ollama_tool_calls = []
        for tc in tool_calls:
            func = tc.get("function", {})
            args = func.get("arguments", {})
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except Exception:
                    pass
            ollama_tool_calls.append({
                "id": tc.get("id"),
                "type": "function",
                "function": {
                    "name": func.get("name"),
                    "arguments": args,
                },
            })

        ollama_resp = {
            "model": body.get("model"),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "message": {
                "role": "assistant",
                "content": content,
                **({"tool_calls": ollama_tool_calls} if ollama_tool_calls else {}),
            },
            "done": True,
            "total_duration": elapsed_ms * 1_000_000,
            "prompt_eval_count": completion.get("usage", {}).get("prompt_tokens", 10),
            "eval_count": completion.get("usage", {}).get("completion_tokens", 10),
        }

        # Provenance logging
        if self.recorder:
            self.recorder.record_call(
                request_sha256=hashlib.sha256(raw_body).hexdigest(),
                scenario_key=str(body.get("model", "")),
                tier=int(completion.get("lam", {}).get("tier", 1)),
                requested_turn=int(completion.get("lam", {}).get("tool_messages", 0)),
                returned_turn=int(completion.get("lam", {}).get("tool_messages", 0)),
                reply_sha256=hashlib.sha256(json.dumps(ollama_resp).encode("utf-8")).hexdigest(),
                source_label=self.headers.get("X-Mock-Source", "lam-replay"),
                run_id=self.headers.get("X-Mock-Run-Id", ""),
                prompt=str(body.get("messages", ""))[:200],
                response=str(content or tool_calls)[:200],
                evidence_label="lam-replay",
                tokens=completion.get("usage", {}).get("total_tokens", 0),
                millis=elapsed_ms,
            )

        self._send_json(200, ollama_resp, evidence_label="lam-replay")


def create_server(
    host: str = "127.0.0.1",
    port: int = 8787,
    scenario_dir: Optional[Path] = None,
    cassette_path: Optional[Path] = None,
    record_db: Optional[Path] = None,
    upstream_url: Optional[str] = None,
) -> ThreadingHTTPServer:
    sc_dir = scenario_dir or _DIR / "scenarios"
    engine = LamEngine.from_directory(sc_dir) if sc_dir.is_dir() else None

    cassette = Cassette.load(cassette_path) if cassette_path and cassette_path.is_file() else None
    recorder = MockRecorder(record_db) if record_db else MockRecorder(_DIR / "lam.sqlite")
    upstream = upstream_url or os.environ.get("LAM_UPSTREAM")

    LamServerHandler.engine = engine
    LamServerHandler.cassette = cassette
    LamServerHandler.recorder = recorder
    LamServerHandler.upstream_url = upstream

    return ThreadingHTTPServer((host, port), LamServerHandler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified LAM HTTP Server (OpenAI & Ollama compatible)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8787, help="Port to listen on (default: 8787)")
    parser.add_argument("--scenarios", type=Path, default=_DIR / "scenarios", help="Path to scenarios directory")
    parser.add_argument("--cassette", type=Path, default=None, help="Path to cassette file for replay")
    parser.add_argument("--record-db", type=Path, default=_DIR / "lam.sqlite", help="Path to SQLite DB for provenance")
    parser.add_argument("--upstream", type=str, default=None, help="Upstream Ollama host URL for live proxy")

    args = parser.parse_args()
    server = create_server(
        host=args.host,
        port=args.port,
        scenario_dir=args.scenarios,
        cassette_path=args.cassette,
        record_db=args.record_db,
        upstream_url=args.upstream,
    )
    upstream_info = f" (Proxy -> {args.upstream or os.environ.get('LAM_UPSTREAM')})" if (args.upstream or os.environ.get("LAM_UPSTREAM")) else " (Gold Replay)"
    print(f"LAM HTTP server listening on http://{args.host}:{args.port}{upstream_info}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping LAM server.")
        server.server_close()


if __name__ == "__main__":
    main()

