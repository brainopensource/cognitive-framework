"""Mock Provider Implementation using Answer Bank catalog or local HTTP server."""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path
from typing import Any
from .base import BaseLLMProvider, LLMResponse

# Try importing catalog engine from 002_LLM_API_MOCK
mock_tool_dir = Path(__file__).resolve().parents[2] / "002_LLM_API_MOCK"
if str(mock_tool_dir) not in sys.path:
    sys.path.insert(0, str(mock_tool_dir))

try:
    from catalog import Catalog, load_catalog, select_reply
    _CATALOG_AVAILABLE = True
except Exception:
    _CATALOG_AVAILABLE = False


class MockProvider(BaseLLMProvider):
    def __init__(self, host: str = "http://127.0.0.1:4141", message: str = "") -> None:
        self.host = host.rstrip("/")
        self.message = message
        self.catalog: Catalog | None = None
        if _CATALOG_AVAILABLE:
            answer_bank_dir = mock_tool_dir / "answer_bank"
            if answer_bank_dir.is_dir():
                try:
                    self.catalog = load_catalog(answer_bank_dir)
                except Exception:
                    self.catalog = None

    def generate(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.2,
        stream: bool = False,
        **kwargs: Any,
    ) -> LLMResponse:
        # 1. If HTTP mock server is online, delegate to it
        try:
            req_body = json.dumps({
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": stream,
            }).encode("utf-8")
            req = urllib.request.Request(
                f"{self.host}/v1/chat/completions",
                data=req_body,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=1) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                if stream:
                    print(content)
                prompt_tokens = max(1, len(prompt.split()))
                completion_tokens = max(1, len(content.split()))
                return LLMResponse(
                    content=content,
                    model=model,
                    provider="mock_server",
                    latency_ms=2,
                    ttft_ms=2,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=prompt_tokens + completion_tokens,
                    cost_usd_micros=0,
                    raw_payload=data,
                )
        except Exception:
            pass

        # 2. Fall back to local in-memory catalog
        if self.catalog:
            # Match scenario by keyword or use default
            scenario = None
            for sc in self.catalog.scenarios.values():
                if any(kw.lower() in prompt.lower() for kw in sc.keywords):
                    scenario = sc
                    break
            if not scenario:
                scenario = self.catalog.default_scenario

            selection = select_reply(scenario, effective_tier=2, prompt=prompt)
            content = selection.reply.text
            if stream:
                print(content)
            prompt_tokens = max(1, len(prompt.split()))
            completion_tokens = max(1, len(content.split()))
            return LLMResponse(
                content=content,
                model=model,
                provider="mock_catalog",
                latency_ms=1,
                ttft_ms=1,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost_usd_micros=0,
                raw_payload={"scenario": scenario.key, "turn": selection.reply.turn},
            )

        # 3. Fall back to generic stub string
        msg = self.message or (
            "this is not your answer, this is only a mocked llm api response stub, "
            "route correctly for the right llm api"
        )
        if stream:
            print(msg)
        prompt_tokens = max(1, len(prompt.split()))
        completion_tokens = max(1, len(msg.split()))
        return LLMResponse(
            content=msg,
            model=model,
            provider="mock_stub",
            latency_ms=1,
            ttft_ms=1,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost_usd_micros=0,
            raw_payload={"mock": True},
        )

