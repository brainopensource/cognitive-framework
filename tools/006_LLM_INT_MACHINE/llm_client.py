"""OpenRouter LLM client and Fake/Mock test double for 006_LLM_INT_MACHINE."""

from __future__ import annotations
import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

try:
    from .env_loader import load_openrouter_api_key
except ImportError:
    from env_loader import load_openrouter_api_key


@dataclass
class LLMUsageMetrics:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cached_tokens: int = 0
    total_tokens: int = 0
    latency_seconds: float = 0.0
    cost_usd: float = 0.0
    model_name: str = ""


@dataclass
class LLMResponse:
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    usage: LLMUsageMetrics = field(default_factory=LLMUsageMetrics)
    raw_response: dict[str, Any] = field(default_factory=dict)


PRICING_PER_1M: dict[str, tuple[float, float]] = {
    "openrouter/free": (0.0, 0.0),
    "minimax/minimax-m3:free": (0.0, 0.0),
    "z-ai/glm-5.2:free": (0.0, 0.0),
    "stealth/ox-alpha": (0.0, 0.0),
    "google/gemini-2.0-flash-exp:free": (0.0, 0.0),
    "meta-llama/llama-3.3-70b-instruct:free": (0.0, 0.0),
    "deepseek/deepseek-v4-flash-0731": (0.10, 0.20),
    "deepseek/deepseek-r1": (0.55, 2.19),
    "anthropic/claude-3.7-sonnet": (3.00, 15.00),
    "anthropic/claude-3.5-haiku": (0.80, 4.00),
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    for prefix, (p_rate, c_rate) in PRICING_PER_1M.items():
        if prefix in model:
            return (prompt_tokens * p_rate + completion_tokens * c_rate) / 1_000_000.0
    return 0.0


class OpenRouterClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://openrouter.ai/api/v1") -> None:
        self._api_key = api_key or load_openrouter_api_key()
        self.base_url = base_url
        self.total_calls: int = 0
        self.cumulative_usage = LLMUsageMetrics()

    def complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
        model: str = "openrouter/free",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        timeout: int = 60,
    ) -> LLMResponse:
        if not self._api_key:
            raise ValueError("OPENROUTER_API_KEY is not set or empty.")

        payload: dict[str, Any] = {
            "model": model,
            "messages": list(messages),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = list(tools)
            payload["tool_choice"] = "auto"

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
                "HTTP-Referer": "https://github.com/vanguard-coding-machine",
                "X-Title": "006_LLM_INT_MACHINE",
            },
            method="POST",
        )

        start_time = time.perf_counter()
        retries = 3
        last_err = None

        for attempt in range(retries):
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    resp_bytes = resp.read()
                    data = json.loads(resp_bytes.decode("utf-8"))
                    break
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                last_err = f"HTTP {e.code}: {err_body}"
                if e.code in (429, 502, 503, 504) and attempt < retries - 1:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                raise RuntimeError(f"OpenRouter API Error: {last_err}") from e
            except Exception as e:
                last_err = str(e)
                if attempt < retries - 1:
                    time.sleep(2.0 * (attempt + 1))
                    continue
                raise RuntimeError(f"OpenRouter Connection Error: {last_err}") from e

        duration = time.perf_counter() - start_time
        self.total_calls += 1

        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content") or ""
        tool_calls = message.get("tool_calls") or []

        raw_usage = data.get("usage", {})
        prompt_t = raw_usage.get("prompt_tokens", 0)
        compl_t = raw_usage.get("completion_tokens", 0)
        cached_t = raw_usage.get("prompt_tokens_details", {}).get("cached_tokens", 0)
        cost = estimate_cost(model, prompt_t, compl_t)

        metrics = LLMUsageMetrics(
            prompt_tokens=prompt_t,
            completion_tokens=compl_t,
            cached_tokens=cached_t,
            total_tokens=prompt_t + compl_t,
            latency_seconds=duration,
            cost_usd=cost,
            model_name=model,
        )

        self.cumulative_usage.prompt_tokens += prompt_t
        self.cumulative_usage.completion_tokens += compl_t
        self.cumulative_usage.cached_tokens += cached_t
        self.cumulative_usage.total_tokens += prompt_t + compl_t
        self.cumulative_usage.cost_usd += cost
        self.cumulative_usage.latency_seconds += duration

        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            usage=metrics,
            raw_response=data,
        )


class MockLLMClient:
    def __init__(self, canned_responses: Sequence[str | dict[str, Any]] | None = None) -> None:
        self._canned = list(canned_responses or [])
        self._index = 0
        self.total_calls = 0
        self.cumulative_usage = LLMUsageMetrics()

    def complete(
        self,
        messages: Sequence[Mapping[str, Any]],
        tools: Sequence[Mapping[str, Any]] | None = None,
        model: str = "mock-model",
        temperature: float = 0.0,
        max_tokens: int = 4096,
        timeout: int = 60,
    ) -> LLMResponse:
        self.total_calls += 1
        if self._index < len(self._canned):
            resp = self._canned[self._index]
            self._index += 1
        else:
            resp = "I have analyzed the codebase and determined the solution is complete."

        if isinstance(resp, str):
            content = resp
            tool_calls = []
        elif isinstance(resp, dict):
            content = resp.get("content", "")
            tool_calls = resp.get("tool_calls", [])
        else:
            content = str(resp)
            tool_calls = []

        metrics = LLMUsageMetrics(
            prompt_tokens=150,
            completion_tokens=50,
            cached_tokens=0,
            total_tokens=200,
            latency_seconds=0.01,
            cost_usd=0.0,
            model_name=model,
        )
        self.cumulative_usage.prompt_tokens += 150
        self.cumulative_usage.completion_tokens += 50
        self.cumulative_usage.total_tokens += 200

        return LLMResponse(content=content, tool_calls=tool_calls, usage=metrics)
