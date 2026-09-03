"""Ollama Local Provider Implementation."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.request
from typing import Any, Dict
from .base import BaseLLMProvider, LLMResponse


def _find_ollama_host() -> str:
    if "OLLAMA_HOST" in os.environ:
        return os.environ["OLLAMA_HOST"].strip()

    candidates = ["127.0.0.1", "localhost"]
    try:
        gw = subprocess.check_output(["ip", "route"], stderr=subprocess.DEVNULL).decode()
        for line in gw.splitlines():
            if "default via" in line:
                candidates.append(line.split()[2].strip())
    except Exception:
        pass

    try:
        with open("/etc/resolv.conf", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("nameserver"):
                    candidates.append(line.split()[1].strip())
    except Exception:
        pass

    for ip in dict.fromkeys(candidates):
        ip = ip.strip()
        try:
            s = socket.create_connection((ip, 11434), timeout=0.5)
            s.close()
            return f"http://{ip}:11434"
        except Exception:
            continue

    return "http://127.0.0.1:11434"


class OllamaProvider(BaseLLMProvider):
    def __init__(self, host: str = "") -> None:
        raw_host = (host or _find_ollama_host()).strip()
        if not raw_host.startswith("http://") and not raw_host.startswith("https://"):
            raw_host = f"http://{raw_host}"
        self.host = raw_host.rstrip("/")

    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        url = f"{self.host}/api/generate"
        body = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
            },
        }

        start_time = time.monotonic()
        ttft_ms = 0

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                if stream:
                    chunks = []
                    for line in resp:
                        if not line.strip():
                            continue
                        chunk_obj = json.loads(line.decode("utf-8"))
                        token = chunk_obj.get("response", "")
                        if token:
                            if ttft_ms == 0:
                                ttft_ms = int((time.monotonic() - start_time) * 1000)
                            print(token, end="", flush=True)
                            chunks.append(token)
                    print()
                    content = "".join(chunks)
                    raw_data = {"streamed": True}
                else:
                    raw_text = resp.read().decode("utf-8")
                    ttft_ms = int((time.monotonic() - start_time) * 1000)
                    raw_data = json.loads(raw_text)
                    content = raw_data.get("response", "")

            latency_ms = int((time.monotonic() - start_time) * 1000)
            prompt_tokens = raw_data.get("prompt_eval_count") or max(1, len(prompt.split()))
            completion_tokens = raw_data.get("eval_count") or max(1, len(content.split()))
            total_tokens = prompt_tokens + completion_tokens

            return LLMResponse(
                content=content,
                model=model,
                provider="ollama",
                latency_ms=latency_ms,
                ttft_ms=ttft_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd_micros=0,  # Local inference is free
                raw_payload=raw_data,
            )

        except Exception as exc:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            return LLMResponse(
                content="",
                model=model,
                provider="ollama",
                latency_ms=latency_ms,
                ttft_ms=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd_micros=0,
                raw_payload={},
                error=f"Ollama connection to {self.host} failed: {exc}",
            )
