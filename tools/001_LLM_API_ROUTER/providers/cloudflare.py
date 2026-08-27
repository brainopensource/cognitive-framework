"""Cloudflare Workers AI Provider Implementation."""

from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict
from .base import BaseLLMProvider, LLMResponse


def _load_env_api_token() -> str:
    token = os.environ.get("CLOUDFARE_API_TOKEN_AI", "")
    if token:
        return token
    for p in (Path(".env"), Path("../../.env"), Path(__file__).resolve().parents[3] / ".env"):
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("CLOUDFARE_API_TOKEN_AI="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _load_env_account_id() -> str:
    account_id = os.environ.get("CLOUDFARE_ACCOUNT_ID", "")
    if account_id:
        return account_id
    for p in (Path(".env"), Path("../../.env"), Path(__file__).resolve().parents[3] / ".env"):
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("CLOUDFARE_ACCOUNT_ID="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


MODEL_PRICING_MICROS = {
    # Cloudflare Workers AI - FREE PLAN MODELS
    # All pricing set to 0 for free models (no billing)
    "@cf/meta/llama-3.1-8b-instruct": {"prompt": 0, "completion": 0},
    "@cf/deepseek/deepseek-v4-flash-0731": {"prompt": 0, "completion": 0},
    "@cf/zai-org/glm-4.7-flash": {"prompt": 0, "completion": 0},
    "@cf/google/gemma-4-26b-a4b-it": {"prompt": 0, "completion": 0},
    "@cf/nvidia/nemotron-3-120b-a12b": {"prompt": 0, "completion": 0},
}


class CloudflareProvider(BaseLLMProvider):
    def __init__(self, api_token: str = "", account_id: str = "", base_url: str = "") -> None:
        self.api_token = api_token or _load_env_api_token()
        self.account_id = account_id or _load_env_account_id()
        self.base_url = base_url or f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"

    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        if not self.api_token:
            return LLMResponse(
                content="",
                model=model,
                provider="cloudflare",
                latency_ms=0,
                ttft_ms=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd_micros=0,
                raw_payload={},
                error="Missing CLOUDFARE_API_TOKEN_AI in environment or .env file",
            )

        if not self.account_id:
            return LLMResponse(
                content="",
                model=model,
                provider="cloudflare",
                latency_ms=0,
                ttft_ms=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd_micros=0,
                raw_payload={},
                error="Missing CLOUDFARE_ACCOUNT_ID in environment or .env file",
            )

        # Use model-in-path endpoint format: /accounts/{id}/ai/run/{model}
        url = f"{self.base_url}/{model}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "User-Agent": "Cloudflare-AI-Client/1.0",
        }
        
        # Add gateway ID header for Workers AI models
        if model.startswith("@cf/"):
            headers["cf-aig-gateway-id"] = "default"
        
        body = {
            "messages": [{"role": "user", "content": prompt}],
        }
        if temperature is not None:
            body["temperature"] = temperature

        start_time = time.monotonic()
        ttft_ms = 0

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers=headers
            )
            with urllib.request.urlopen(req, timeout=25) as resp:
                raw_text = resp.read().decode("utf-8")
                ttft_ms = int((time.monotonic() - start_time) * 1000)
                raw_data = json.loads(raw_text)

                # Cloudflare /ai/run response: {"result": {"choices": [...]}, "success": true}
                if raw_data.get("success"):
                    result = raw_data.get("result", {})
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                else:
                    error_msg = raw_data.get("errors", [{}])[0].get("message", "Unknown error")
                    return LLMResponse(
                        content="",
                        model=model,
                        provider="cloudflare",
                        latency_ms=int((time.monotonic() - start_time) * 1000),
                        ttft_ms=ttft_ms,
                        prompt_tokens=0,
                        completion_tokens=0,
                        total_tokens=0,
                        cost_usd_micros=0,
                        raw_payload=raw_data,
                        error=f"Cloudflare API error: {error_msg}",
                    )

            latency_ms = int((time.monotonic() - start_time) * 1000)
            
            # Get token usage from response, or estimate
            result = raw_data.get("result", {})
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens") or max(1, len(prompt.split()))
            completion_tokens = usage.get("completion_tokens") or max(1, len(content.split()))
            total_tokens = usage.get("total_tokens") or (prompt_tokens + completion_tokens)

            pricing = MODEL_PRICING_MICROS.get(model, {"prompt": 50, "completion": 150})
            cost_micros = int((prompt_tokens * pricing["prompt"] + completion_tokens * pricing["completion"]) / 100)

            return LLMResponse(
                content=content,
                model=model,
                provider="cloudflare",
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
                provider="cloudflare",
                latency_ms=latency_ms,
                ttft_ms=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd_micros=0,
                raw_payload={},
                error=f"Cloudflare request failed: {exc}",
            )
