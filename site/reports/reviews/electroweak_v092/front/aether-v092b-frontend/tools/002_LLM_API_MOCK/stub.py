"""Host Probe CLI for Windows 11 / WSL2 Ollama reachability.

Probes Windows host Ollama endpoint, reports installed tags, and suggests
environment exports (VANGUARD_OLLAMA_ENDPOINT and LAM_UPSTREAM).
Fail-closed: returns provider_unreachable if host daemon is absent.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Tuple


def detect_wsl_host_ip() -> Optional[str]:
    """Discover Windows host IP from WSL2 route table or resolv.conf."""
    try:
        out = subprocess.check_output(["ip", "route", "show", "default"], text=True).strip()
        parts = out.split()
        if "via" in parts:
            idx = parts.index("via")
            if idx + 1 < len(parts):
                return parts[idx + 1]
    except Exception:
        pass

    try:
        with open("/etc/resolv.conf", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("nameserver"):
                    return line.split()[1].strip()
    except Exception:
        pass

    return None


def probe_ollama_endpoint(host: str, port: int = 11434, timeout: float = 2.0) -> Tuple[bool, List[str], Optional[str]]:
    """Probe Ollama endpoint at http://{host}:{port}/api/tags."""
    url = f"http://{host}:{port}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [str(m.get("name", "")) for m in data.get("models", []) if isinstance(m, dict)]
                return True, models, None
            return False, [], f"HTTP {resp.status}"
    except urllib.error.URLError as exc:
        return False, [], f"provider_unreachable ({exc.reason})"
    except Exception as exc:
        return False, [], f"provider_unreachable ({exc})"


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe Windows 11 / Local Ollama reachability from WSL2")
    parser.add_argument("--host", type=str, default=None, help="Ollama host IP (default: auto-detect WSL host or 127.0.0.1)")
    parser.add_argument("--port", type=int, default=11434, help="Ollama port (default: 11434)")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    detected_ip = detect_wsl_host_ip()
    target_hosts = []
    if args.host:
        target_hosts.append(args.host)
    else:
        # Check detected host IP first, then localhost
        if detected_ip and detected_ip != "127.0.0.1":
            target_hosts.append(detected_ip)
        target_hosts.append("127.0.0.1")

    probe_results = []
    successful_host = None
    successful_tags = []

    for host in target_hosts:
        ok, tags, err = probe_ollama_endpoint(host, args.port)
        probe_results.append({"host": host, "port": args.port, "reachable": ok, "tags": tags, "error": err})
        if ok and successful_host is None:
            successful_host = host
            successful_tags = tags

    has_qwen = any("qwen2.5:1.5b" in tag for tag in successful_tags)

    summary = {
        "status": "ok" if successful_host else "provider_unreachable",
        "wsl_host_detected": detected_ip,
        "reachable_host": successful_host,
        "installed_tags": successful_tags,
        "default_tag_available": has_qwen,
        "suggested_exports": {
            "VANGUARD_OLLAMA_ENDPOINT": f"http://{successful_host or '127.0.0.1'}:{args.port}/api/chat",
            "LAM_UPSTREAM": f"http://{successful_host or '127.0.0.1'}:{args.port}",
        } if successful_host else {},
        "probes": probe_results,
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        if successful_host:
            print(f"✔ Ollama reachable at http://{successful_host}:{args.port}")
            print(f"  Installed tags ({len(successful_tags)}): {', '.join(successful_tags) if successful_tags else 'none'}")
            if not has_qwen:
                print("  ⚠ Recommended lab default tag 'qwen2.5:1.5b' is NOT pulled.")
                print("    Run on Windows host: ollama pull qwen2.5:1.5b")
            print("\nSuggested Environment Configuration:")
            print(f"  export VANGUARD_OLLAMA_ENDPOINT=http://{successful_host}:{args.port}/api/chat")
            print(f"  export LAM_UPSTREAM=http://{successful_host}:{args.port}")
        else:
            print(f"✖ Ollama unreachable on tested interfaces: {', '.join(target_hosts)}")
            print("  Windows 11 WSL2 Checklist:")
            print("  1. Set OLLAMA_HOST=0.0.0.0:11434 on Windows")
            print("  2. Allow Windows Firewall inbound rule for TCP port 11434")
            print("  3. Run 'ollama serve' and 'ollama pull qwen2.5:1.5b'")

    return 0 if successful_host else 1


if __name__ == "__main__":
    sys.exit(main())

