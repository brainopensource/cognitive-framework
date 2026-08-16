"""OpenRouter Provider Implementation."""

from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict
from .base import BaseLLMProvider, LLMResponse


def _load_env_api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if key:
        return key
    for p in (Path(".env"), Path("../../.env"), Path(__file__).resolve().parents[3] / ".env"):
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


MODEL_PRICING_MICROS = {
    # OpenRouter Verified Free Models ($0.00)
    "openrouter/free": {"prompt": 0, "completion": 0},
    "inclusionai/ling-3.0-tiny:free": {"prompt": 0, "completion": 0},
    "poolside/laguna-s-2.1:free": {"prompt": 0, "completion": 0},
    "cohere/north-mini-code:free": {"prompt": 0, "completion": 0},
    "google/gemma-4-26b-a4b-it:free": {"prompt": 0, "completion": 0},
    "nvidia/nemotron-3-super-120b-a12b:free": {"prompt": 0, "completion": 0},
    "openai/gpt-oss-20b:free": {"prompt": 0, "completion": 0},
    # OpenRouter Verified Low-Cost Paid Models
    "deepseek/deepseek-v4-flash": {"prompt": 14, "completion": 28},
    "deepseek/deepseek-v4-flash-0731": {"prompt": 14, "completion": 28},
    "xiaomi/mimo-v2.5": {"prompt": 10, "completion": 30},
    # OpenRouter Frontier Cloud Models
    "z-ai/glm-5.2": {"prompt": 35, "completion": 140},
    "openai/gpt-5.6-luna": {"prompt": 100, "completion": 400},
    "deepseek/deepseek-v4-pro": {"prompt": 45, "completion": 180},
    "minimax/minimax-m3": {"prompt": 20, "completion": 80},
    # OpenAI & DeepSeek Direct
    "gpt-4o": {"prompt": 250, "completion": 1000},
    "openai/gpt-4o": {"prompt": 250, "completion": 1000},
    "deepseek-reasoner": {"prompt": 55, "completion": 219},
    "deepseek-coder": {"prompt": 14, "completion": 28},
}



class OpenRouterProvider(BaseLLMProvider):
    def __init__(self, api_key: str = "", base_url: str = "https://openrouter.ai/api/v1") -> None:
        self.api_key = api_key or _load_env_api_key()
        self.base_url = base_url.rstrip("/")

    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        if not self.api_key:
            return LLMResponse(
                content="",
                model=model,
                provider="openrouter",
                latency_ms=0,
                ttft_ms=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd_micros=0,
                raw_payload={},
                error="Missing OPENROUTER_API_KEY in environment or .env file",
            )

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/aether-d-system",
            "X-Title": "Vanguard LLM Router",
        }
        body = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "stream": stream,
        }

        start_time = time.monotonic()
        ttft_ms = 0

        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=25) as resp:
                if stream:
                    chunks = []
                    for line in resp:
                        line_str = line.decode("utf-8").strip()
                        if not line_str.startswith("data:"):
                            continue
                        data_part = line_str[5:].strip()
                        if data_part == "[DONE]":
                            break
                        try:
                            delta_obj = json.loads(data_part)
                            delta = delta_obj.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                if ttft_ms == 0:
                                    ttft_ms = int((time.monotonic() - start_time) * 1000)
                                print(delta, end="", flush=True)
                                chunks.append(delta)
                        except Exception:
                            continue
                    print()
                    content = "".join(chunks)
                    raw_data = {"streamed": True}
                else:
                    raw_text = resp.read().decode("utf-8")
                    ttft_ms = int((time.monotonic() - start_time) * 1000)
                    raw_data = json.loads(raw_text)
                    content = raw_data.get("choices", [{}])[0].get("message", {}).get("content", "")

            latency_ms = int((time.monotonic() - start_time) * 1000)
            usage = raw_data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens") or max(1, len(prompt.split()))
            completion_tokens = usage.get("completion_tokens") or max(1, len(content.split()))
            total_tokens = usage.get("total_tokens") or (prompt_tokens + completion_tokens)

            pricing = MODEL_PRICING_MICROS.get(model, {"prompt": 20, "completion": 60})
            cost_micros = int((prompt_tokens * pricing["prompt"] + completion_tokens * pricing["completion"]) / 100)

            return LLMResponse(
                content=content,
                model=model,
                provider="openrouter",
                latency_ms=latency_ms,
                ttft_ms=ttft_ms,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost_usd_micros=cost_micros,
                raw_payload=raw_data,
            )

        except Exception as exc:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            return LLMResponse(
                content="",
                model=model,
                provider="openrouter",
                latency_ms=latency_ms,
                ttft_ms=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd_micros=0,
                raw_payload={},
                error=f"OpenRouter request failed: {exc}",
            )
