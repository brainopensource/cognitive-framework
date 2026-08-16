"""Optional live OpenRouter pings. Never prints secrets. Respects $0.50 wave budget."""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request
from typing import Any

FREE = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nvidia/nemotron-3.5-lightning:free",
    "cohere/north-mini-code:free",
]

MEDIUM = [
    "openai/gpt-5.6-luna",
    "deepseek/deepseek-v4-flash-0731",
    "xiaomi/mimo-v2.5",
]

HIGH = [
    "google/gemini-3.7-flash",
    "deepseek/deepseek-v4-pro-0813",
    "z-ai/glm-5.2",
]

# Not named in the request — do not guess flagship ids against a $0.50 cap.
TOP_UNSPECIFIED = []

TIER_PROBES = {
    1: "Fix in one line: def add(a,b): return a-b  # should add. Reply with the corrected function only.",
    2: "Two files: calc.py totals starting at 1; test imports summer not calc. List the two edits as bullets.",
    3: "L3 repo map must stay byte-identical when the task brief changes. What must not be concatenated into L3?",
    4: "Name four ordered todos to add a --json flag to a hello CLI (code, test, docs).",
    5: "In one paragraph: how would you extract digest_of from digest.py into canonicalisation.py and update ledger, compiler, tests without breaking prefix_digest?",
}


def _key() -> str | None:
    value = os.environ.get("OPENROUTER_API_KEY")
    return value if value else None


def ping(model: str, prompt: str, timeout: float = 45.0) -> dict[str, Any]:
    secret = _key()
    if not secret:
        return {"model": model, "ok": False, "error": "OPENROUTER_API_KEY unset", "skipped": True}
    payload = json.dumps(
        {
            "model": model,
            "temperature": 0,
            "max_tokens": 220,
            "messages": [
                {"role": "system", "content": "You are a concise coding assistant. No tools."},
                {"role": "user", "content": prompt},
            ],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://vanguard.local",
            "X-Title": "vanguard-lam-probe",
        },
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        return {
            "model": model,
            "ok": False,
            "status": exc.code,
            "error": "http_error",
            "detail": detail.replace(secret, "OPENROUTER_API_KEY"),
            "wall_s": round(time.perf_counter() - started, 3),
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"model": model, "ok": False, "error": type(exc).__name__, "wall_s": round(time.perf_counter() - started, 3)}
    usage = body.get("usage") or {}
    choice = (body.get("choices") or [{}])[0]
    message = (choice.get("message") or {})
    text = str(message.get("content") or "")
    return {
        "model": model,
        "ok": True,
        "wall_s": round(time.perf_counter() - started, 3),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "finish_reason": choice.get("finish_reason"),
        "chars": len(text),
        "preview": text[:240].replace(secret, "OPENROUTER_API_KEY"),
    }


def probe_band(models: list[str], tier: int = 1) -> list[dict[str, Any]]:
    return [ping(model, TIER_PROBES[tier]) for model in models]


def probe_free_tier1() -> list[dict[str, Any]]:
    """Free models; one short T1 prompt each."""
    return probe_band(FREE, 1)


if __name__ == "__main__":
    print(json.dumps(probe_free_tier1(), indent=2))
