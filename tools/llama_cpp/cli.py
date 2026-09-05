#!/usr/bin/env python3
"""Unified CLI and management tool for direct llama.cpp execution on Fedora/Linux.

Provides direct access to GGUF models, process lifecycle management for llama-server,
and structured generation (Min-P, JSON schema) to eliminate agent hallucinations.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
PID_FILE = Path("/tmp/llama_server.pid")
DEFAULT_MODEL_DIRS = [
    Path.home() / "Models",
    Path.home() / "models",
    Path("./models"),
    Path.cwd(),
]


def find_llama_server_binary() -> Optional[str]:
    """Locate llama-server binary in PATH or common Linux installation locations."""
    # Check PATH first
    for path_dir in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(path_dir) / "llama-server"
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)

    # Common fallback locations on Linux/Fedora
    known_paths = [
        Path.home() / ".local/bin/llama-server",
        Path("/usr/local/bin/llama-server"),
        Path("/usr/bin/llama-server"),
        Path("/opt/llama.cpp/llama-server"),
    ]
    for candidate in known_paths:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


class LlamaBridgeError(Exception):
    """Base exception for llama bridge lifecycle errors."""
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message


class ModelMismatchError(LlamaBridgeError):
    def __init__(self, message: str = "Occupied port model/alias does not match expected identity") -> None:
        super().__init__("MODEL_MISMATCH", message)


class PidStaleError(LlamaBridgeError):
    def __init__(self, message: str = "Recorded child PID is stale or not running") -> None:
        super().__init__("PID_STALE", message)


def check_props_identity(
    props: Mapping[str, Any],
    expected_model: str,
    expected_alias: Optional[str] = None,
) -> bool:
    """Check if /props matches expected model and alias."""
    if not props:
        return False
    default_gen = props.get("default_generation_settings", {}) if isinstance(props, Mapping) else {}
    props_model = str(default_gen.get("model") or props.get("model") or "")
    props_alias = str(props.get("alias") or props.get("model_alias") or "")

    expected_model_name = Path(expected_model).name
    expected_model_stem = Path(expected_model).stem

    model_matches = False
    if props_model:
        model_matches = (
            props_model == expected_model
            or props_model == expected_model_name
            or props_model == expected_model_stem
            or Path(props_model).name == expected_model_name
            or Path(props_model).stem == expected_model_stem
            or (bool(expected_alias) and props_model == expected_alias)
        )

    alias_matches = True
    if expected_alias:
        if props_alias:
            alias_matches = (props_alias == expected_alias)
        elif props_model:
            alias_matches = (props_model == expected_alias or model_matches)
        else:
            alias_matches = False

    return bool(model_matches and alias_matches)


def adopt_server(
    base_url: str,
    expected_model: str,
    expected_alias: Optional[str] = None,
) -> Dict[str, Any]:
    """Adopt an existing server on the port only if /props model and alias match."""
    health = check_server_health(base_url)
    if not health.get("online"):
        raise LlamaBridgeError("SERVER_OFFLINE", f"No server online at {base_url}")
    props = health.get("props", {})
    if not check_props_identity(props, expected_model, expected_alias):
        raise ModelMismatchError(
            f"Occupied port {base_url} model/alias does not match expected ({expected_model}, {expected_alias})"
        )
    return health


def scan_gguf_models(search_dirs: Optional[List[Path]] = None) -> List[Dict[str, Any]]:
    """Scan directories for GGUF model files."""
    dirs = search_dirs or DEFAULT_MODEL_DIRS
    models = []
    seen = set()

    for d in dirs:
        if not d.exists():
            continue
        try:
            for p in d.glob("*.gguf"):
                rp = p.resolve()
                if rp in seen:
                    continue
                seen.add(rp)
                size_gb = round(rp.stat().st_size / (1024 ** 3), 2)
                models.append({
                    "name": p.name,
                    "path": str(rp),
                    "size_gb": size_gb,
                    "mtime": time.ctime(rp.stat().st_mtime),
                })
        except PermissionError:
            continue

    return sorted(models, key=lambda x: x["name"])


def check_server_health(base_url: str = f"http://{DEFAULT_HOST}:{DEFAULT_PORT}") -> Dict[str, Any]:
    """Check if llama-server is responding and return its status/props."""
    health_url = f"{base_url}/health"
    props_url = f"{base_url}/props"
    try:
        req = urllib.request.Request(health_url, headers={"User-Agent": "llama-cli/1.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            health_data = json.loads(resp.read().decode("utf-8")) if resp.status == 200 else {"status": "ok"}
    except Exception as exc:
        return {"online": False, "error": str(exc), "url": base_url}

    props = {}
    try:
        req = urllib.request.Request(props_url, headers={"User-Agent": "llama-cli/1.0"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            props = json.loads(resp.read().decode("utf-8"))
    except Exception:
        pass

    return {
        "online": True,
        "url": base_url,
        "health": health_data,
        "props": props,
    }


def serve_command(args: argparse.Namespace) -> None:
    """Launch llama-server with optimal hardware and context flags."""
    binary = args.binary or find_llama_server_binary()
    if not binary:
        print("Error: Could not locate 'llama-server' binary.", file=sys.stderr)
        print("Please install llama.cpp or specify --binary /path/to/llama-server", file=sys.stderr)
        sys.exit(1)

    model_path = Path(args.model).resolve()
    if not model_path.exists():
        # Try finding it in default model directories
        found = None
        for m in scan_gguf_models():
            if m["name"] == args.model or str(m["path"]).endswith(args.model):
                found = Path(m["path"])
                break
        if found:
            model_path = found
        else:
            print(f"Error: Model file '{args.model}' not found.", file=sys.stderr)
            sys.exit(1)

    cmd = [
        binary,
        "-m", str(model_path),
        "-c", str(args.ctx),
        "-ngl", str(args.ngl),
        "-t", str(args.threads or os.cpu_count() or 4),
        "--host", args.host,
        "--port", str(args.port),
        "--alias", args.alias or model_path.stem,
    ]

    if args.flash_attn != "auto":
        cmd.extend(["--flash-attn", args.flash_attn])
    if args.ctk:
        cmd.extend(["-ctk", args.ctk])
    if args.ctv:
        cmd.extend(["-ctv", args.ctv])

    print(f"Starting llama-server using binary: {binary}")
    print(f"Model: {model_path} ({round(model_path.stat().st_size / (1024**3), 2)} GB)")
    print(f"Endpoint: http://{args.host}:{args.port}")
    print(f"Command: {' '.join(cmd)}")

    if args.background:
        alias = args.alias or model_path.stem
        try:
            result = launch_server_process(
                cmd,
                host=args.host,
                port=args.port,
                expected_model=str(model_path),
                expected_alias=alias,
            )
        except ModelMismatchError as exc:
            print(f"Error [{exc.code}]: {exc.message}", file=sys.stderr)
            sys.exit(1)

        if result["status"] == "ONLINE":
            print("Server is ONLINE and ready for requests.")
        elif result["status"] == "FAILED":
            print(f"Server launch FAILED: {result.get('error', 'unknown error')}", file=sys.stderr)
            sys.exit(1)
        else:
            print("Server process started. Check /tmp/llama_server.log for startup progress.")
    else:
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\nShutting down llama-server...")


def launch_server_process(
    cmd: list[str],
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    expected_model: str,
    expected_alias: Optional[str] = None,
    log_file: str = "/tmp/llama_server.log",
    pid_file: Path = PID_FILE,
    max_wait_seconds: float = 5.0,
) -> Dict[str, Any]:
    """Launch server process and wait for readiness with fail-closed verification."""
    base_url = f"http://{host}:{port}"

    with open(log_file, "w", encoding="utf-8") as log_handle:
        proc = subprocess.Popen(
            cmd,
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid,
        )
    pid_file.write_text(str(proc.pid))

    start_t = time.time()
    while (time.time() - start_t) < max_wait_seconds:
        time.sleep(0.5)
        # If child process exited prematurely, it must be FAILED, never ONLINE
        if proc.poll() is not None:
            return {
                "status": "FAILED",
                "online": False,
                "error": f"Child process (PID {proc.pid}) exited with code {proc.poll()}",
                "pid": proc.pid,
            }
        health = check_server_health(base_url)
        if health.get("online"):
            props = health.get("props", {})
            if check_props_identity(props, expected_model, expected_alias):
                return {
                    "status": "ONLINE",
                    "online": True,
                    "pid": proc.pid,
                    "health": health.get("health", {}),
                    "props": props,
                }
            else:
                return {
                    "status": "FAILED",
                    "online": False,
                    "error": "MODEL_MISMATCH",
                    "pid": proc.pid,
                }

    if proc.poll() is not None:
        return {
            "status": "FAILED",
            "online": False,
            "error": f"Child process exited with code {proc.poll()}",
            "pid": proc.pid,
        }

    return {
        "status": "STARTING",
        "online": False,
        "pid": proc.pid,
    }


def stop_server(pid_file: Path = PID_FILE) -> None:
    """Stop only an identity-verified recorded child process."""
    if not pid_file.exists():
        raise PidStaleError(f"No active PID file found at {pid_file}")

    try:
        pid_text = pid_file.read_text().strip()
        pid = int(pid_text)
    except (ValueError, OSError) as exc:
        pid_file.unlink(missing_ok=True)
        raise PidStaleError(f"Invalid PID file content: {exc}")

    try:
        os.kill(pid, 0)
    except (ProcessLookupError, OSError):
        pid_file.unlink(missing_ok=True)
        raise PidStaleError(f"Process {pid} is not running (stale PID)")

    try:
        os.kill(pid, signal.SIGTERM)
        pid_file.unlink(missing_ok=True)
    except (ProcessLookupError, OSError) as exc:
        pid_file.unlink(missing_ok=True)
        raise PidStaleError(f"Failed to stop process {pid}: {exc}")


def stop_command(args: argparse.Namespace) -> None:
    """Stop the background llama-server process."""
    try:
        stop_server()
        print("Sent SIGTERM to llama-server.")
    except PidStaleError as exc:
        print(f"Error [{exc.code}]: {exc.message}", file=sys.stderr)
        sys.exit(1)


def status_command(args: argparse.Namespace) -> None:
    """Display server health, endpoints, and hardware status."""
    url = f"http://{args.host}:{args.port}"
    status = check_server_health(url)
    if status["online"]:
        print(f"● llama-server is RUNNING at {url}")
        props = status.get("props", {})
        if props:
            print(f"  Model: {props.get('default_generation_settings', {}).get('model', 'Loaded')}")
        print(f"  Health Check: {json.dumps(status['health'])}")
    else:
        print(f"○ llama-server is OFFLINE at {url}")
        print(f"  Details: {status.get('error', 'Connection refused')}")


def list_models_command(args: argparse.Namespace) -> None:
    """List all available GGUF models on disk."""
    models = scan_gguf_models()
    if not models:
        print("No .gguf models found in search paths:")
        for d in DEFAULT_MODEL_DIRS:
            print(f"  - {d}")
        return

    print(f"Found {len(models)} GGUF model(s):")
    for m in models:
        print(f"  • {m['name']:<35} | {m['size_gb']:>6.2f} GB | {m['path']}")


def chat_command(args: argparse.Namespace) -> None:
    """Send a chat completion request to llama-server with strict sampling."""
    url = f"http://{args.host}:{args.port}/v1/chat/completions"

    prompt = args.prompt
    if not prompt:
        if not sys.stdin.isatty():
            prompt = sys.stdin.read().strip()
        else:
            print("Enter prompt (Ctrl+D to end):")
            prompt = sys.stdin.read().strip()

    if not prompt:
        print("Error: Empty prompt.", file=sys.stderr)
        sys.exit(1)

    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": prompt})

    payload: Dict[str, Any] = {
        "model": args.model or "local-model",
        "messages": messages,
        "temperature": args.temperature,
        "stream": args.stream,
    }

    # Anti-hallucination sampling options
    if args.min_p is not None:
        payload["min_p"] = args.min_p
    if args.max_tokens:
        payload["max_tokens"] = args.max_tokens

    # Strict JSON schema / grammar enforcement (prevents output hallucinations)
    if args.json_schema:
        try:
            schema_obj = json.loads(args.json_schema)
            payload["response_format"] = {
                "type": "json_object",
                "schema": schema_obj,
            }
        except json.JSONDecodeError as err:
            print(f"Warning: Invalid JSON schema passed: {err}", file=sys.stderr)

    req_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_bytes,
        headers={"Content-Type": "application/json", "User-Agent": "llama-cli/1.0"},
    )

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=120.0) as resp:
            if args.stream:
                print("Streaming response:")
                for line in resp:
                    line_str = line.decode("utf-8").strip()
                    if line_str.startswith("data: ") and line_str != "data: [DONE]":
                        chunk = json.loads(line_str[6:])
                        delta = chunk["choices"][0].get("delta", {}).get("content", "")
                        sys.stdout.write(delta)
                        sys.stdout.flush()
                print()
            else:
                data = json.loads(resp.read().decode("utf-8"))
                choice = data["choices"][0]
                content = choice.get("message", {}).get("content", "")
                usage = data.get("usage", {})
                dt = time.perf_counter() - t0
                print(content)
                if args.verbose:
                    print("\n--- Telemetry ---")
                    print(f"Elapsed: {dt:.2f}s")
                    if usage:
                        print(f"Prompt Tokens: {usage.get('prompt_tokens')} | Completion Tokens: {usage.get('completion_tokens')}")
    except urllib.error.URLError as exc:
        print(f"Error communicating with llama-server at {url}: {exc}", file=sys.stderr)
        print("Ensure the server is started via: python3 tools/llama_cpp/cli.py serve --model <model.gguf>", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Direct llama.cpp Controller & Inference CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Subcommand: models
    subparsers.add_parser("models", help="Scan and list GGUF models on disk")

    # Subcommand: status
    status_p = subparsers.add_parser("status", help="Check llama-server health & status")
    status_p.add_argument("--host", default=DEFAULT_HOST, help="Server host")
    status_p.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port")

    # Subcommand: serve
    serve_p = subparsers.add_parser("serve", help="Launch llama-server with a model")
    serve_p.add_argument("-m", "--model", required=True, help="Path or name of GGUF model")
    serve_p.add_argument("-c", "--ctx", type=int, default=8192, help="Context size")
    serve_p.add_argument("-ngl", type=int, default=99, help="Number of GPU layers to offload")
    serve_p.add_argument("-t", "--threads", type=int, default=None, help="CPU threads")
    serve_p.add_argument("--host", default=DEFAULT_HOST, help="Bind host")
    serve_p.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port")
    serve_p.add_argument("--alias", default=None, help="Model alias name for API")
    serve_p.add_argument("--binary", default=None, help="Custom path to llama-server binary")
    serve_p.add_argument(
        "--flash-attn", choices=["on", "off", "auto"], default="auto",
        help="llama.cpp Flash Attention mode",
    )
    serve_p.add_argument("--ctk", choices=["f16", "q8_0", "q4_0"], help="KV cache key quantization")
    serve_p.add_argument("--ctv", choices=["f16", "q8_0", "q4_0"], help="KV cache value quantization")
    serve_p.add_argument("-d", "--background", action="store_true", help="Run server in background daemon")

    # Subcommand: stop
    subparsers.add_parser("stop", help="Stop the running background llama-server")

    # Subcommand: chat
    chat_p = subparsers.add_parser("chat", help="Send chat prompt to llama-server")
    chat_p.add_argument("-p", "--prompt", help="Prompt text (or pipe via stdin)")
    chat_p.add_argument("-s", "--system", help="System prompt / instructions")
    chat_p.add_argument("-m", "--model", default="local-model", help="Model name alias")
    chat_p.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature")
    chat_p.add_argument("--min-p", type=float, default=0.05, help="Min-P sampling cutoff (anti-hallucination)")
    chat_p.add_argument("--max-tokens", type=int, default=2048, help="Max tokens to generate")
    chat_p.add_argument("--json-schema", help="JSON Schema string for constrained structured generation")
    chat_p.add_argument("--host", default=DEFAULT_HOST, help="Server host")
    chat_p.add_argument("--port", type=int, default=DEFAULT_PORT, help="Server port")
    chat_p.add_argument("--stream", action="store_true", help="Stream response tokens")
    chat_p.add_argument("-v", "--verbose", action="store_true", help="Print telemetry")

    args = parser.parse_args()

    if args.subcommand == "models":
        list_models_command(args)
    elif args.subcommand == "status":
        status_command(args)
    elif args.subcommand == "serve":
        serve_command(args)
    elif args.subcommand == "stop":
        stop_command(args)
    elif args.subcommand == "chat":
        chat_command(args)


if __name__ == "__main__":
    main()
