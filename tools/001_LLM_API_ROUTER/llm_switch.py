#!/usr/bin/env python3
"""Standalone Multi-Provider LLM Router and Benchmarking CLI."""

from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

# Add current directory to path for provider discovery
sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers import get_provider, LLMResponse


MODEL_ALIASES = {
    # OpenRouter mappings
    "openrouter": {
        "free": "openrouter/free",
        "ling": "inclusionai/ling-3.0-tiny:free",
        "laguna": "poolside/laguna-s-2.1:free",
        "north": "cohere/north-mini-code:free",
        "gemma": "google/gemma-4-26b-a4b-it:free",
        "nemotron": "nvidia/nemotron-3-super-120b-a12b:free",
        "gpt-oss": "deepseek/deepseek-v4-flash-0731",
        "deepseek-flash": "deepseek/deepseek-v4-flash",
        "deepseek": "deepseek/deepseek-v4-flash",
        "mimo": "xiaomi/mimo-v2.5",
        "glm": "z-ai/glm-5.2",
        "gpt-luna": "openai/gpt-5.6-luna",
        "deepseek-pro": "deepseek/deepseek-v4-pro",
        "minimax": "minimax/minimax-m3",
    },
    # Ollama mappings
    "ollama": {
        "llama": "llama3.2:3b",
        "llama3.2": "llama3.2:3b",
        "qwen": "qwen2.5:1.5b",
        "qwen2.5": "qwen2.5:1.5b",
        "qwen-large": "qwen3.6:27b",
        "qwen3.6": "qwen3.6:27b",
        "deepseek-r1": "deepseek-r1:14b",
    },
    # Groq mappings
    "groq": {
        "fast": "llama-3.1-8b-instant",
        "llama": "llama-3.1-8b-instant",
        "llama-fast": "llama-3.1-8b-instant",
        "llama-3.1": "llama-3.1-8b-instant",
        "120b": "deepseek/deepseek-v4-flash-0731",
        "gpt-oss": "deepseek/deepseek-v4-flash-0731",
        "gpt-oss-120b": "deepseek/deepseek-v4-flash-0731",
        "powerful": "deepseek/deepseek-v4-flash-0731",
    },
    # Cloudflare Workers AI mappings - FREE PLAN ONLY
    "cloudflare": {
        # Fast & lightweight (8B)
        "llama": "@cf/meta/llama-3.1-8b-instruct",
        "llama-8b": "@cf/meta/llama-3.1-8b-instruct",
        # Balanced performance (20B)
        "gpt-oss-20b": "@cf/deepseek/deepseek-v4-flash-0731",
        "gpt-oss": "@cf/deepseek/deepseek-v4-flash-0731",
        "20b": "@cf/deepseek/deepseek-v4-flash-0731",
        # Powerful models (26B+)
        "gemma": "@cf/google/gemma-4-26b-a4b-it",
        "gemma-26b": "@cf/google/gemma-4-26b-a4b-it",
        "nemotron": "@cf/nvidia/nemotron-3-120b-a12b",
        "nemotron-120b": "@cf/nvidia/nemotron-3-120b-a12b",
        "glm": "@cf/zai-org/glm-4.7-flash",
        "glm-flash": "@cf/zai-org/glm-4.7-flash",
        # Default to fast model
        "default": "@cf/meta/llama-3.1-8b-instruct",
    },
    # Cloudflare short alias - FREE PLAN ONLY
    "cf": {
        # Fast & lightweight (8B)
        "llama": "@cf/meta/llama-3.1-8b-instruct",
        "llama-8b": "@cf/meta/llama-3.1-8b-instruct",
        # Balanced performance (20B)
        "gpt-oss-20b": "@cf/deepseek/deepseek-v4-flash-0731",
        "gpt-oss": "@cf/deepseek/deepseek-v4-flash-0731",
        "20b": "@cf/deepseek/deepseek-v4-flash-0731",
        # Powerful models (26B+)
        "gemma": "@cf/google/gemma-4-26b-a4b-it",
        "gemma-26b": "@cf/google/gemma-4-26b-a4b-it",
        "nemotron": "@cf/nvidia/nemotron-3-120b-a12b",
        "nemotron-120b": "@cf/nvidia/nemotron-3-120b-a12b",
        "glm": "@cf/zai-org/glm-4.7-flash",
        "glm-flash": "@cf/zai-org/glm-4.7-flash",
        # Default to fast model
        "default": "@cf/meta/llama-3.1-8b-instruct",
    },
}



def resolve_model(provider_name: str, model_arg: str) -> str:
    prov = provider_name.lower().strip()
    alias_map = MODEL_ALIASES.get(prov, {})
    return alias_map.get(model_arg.lower(), model_arg)


def read_prompt(prompt_input: str) -> str:
    potential_path = Path(prompt_input)
    if potential_path.is_file():
        return potential_path.read_text(encoding="utf-8").strip()
    return prompt_input


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Vanguard LLM Router - Multi-Provider LLM Switching and Benchmarking CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Call local Ollama with a raw message:
  python3 tools/001_LLM_API_ROUTER/llm_switch.py -p ollama -m "qwen2.5:1.5b" -msg "write fibonacci in python"

  # Call OpenRouter using a markdown prompt file:
  python3 tools/001_LLM_API_ROUTER/llm_switch.py -p openrouter -m deepseek/deepseek-v4-flash-0731 -msg tools/001_LLM_API_ROUTER/prompts/default_task.md

  # Streaming mode to terminal and custom output directory:
  python3 tools/001_LLM_API_ROUTER/llm_switch.py -p ollama -m qwen25 -msg "test" -o ./benchmarks --stream
        """,
    )

    parser.add_argument(
        "-provider", "--provider", "-p",
        type=str,
        default="openrouter",
        choices=["openrouter", "or", "ollama", "local", "mock", "stub", "lam", "groq", "cloudflare", "cf"],
        help="LLM provider backend (default: openrouter)",
    )
    parser.add_argument(
        "-model", "--model", "-m",
        type=str,
        default="qwen25",
        help="Target model identifier or alias (e.g. qwen25, deepseek, google/gemini-2.0-flash-001)",
    )
    parser.add_argument(
        "-message", "--message", "-msg",
        type=str,
        required=True,
        help="Prompt text string OR path to a markdown/text prompt file (.md/.txt)",
    )
    parser.add_argument(
        "-output", "--output", "-o",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs",
        help="Destination directory to persist response and metadata files",
    )
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.2,
        help="Sampling temperature (default: 0.2)",
    )
    parser.add_argument(
        "--stream", "-s",
        action="store_true",
        help="Stream response chunks incrementally to stdout",
    )
    parser.add_argument(
        "--raw-only",
        action="store_true",
        help="Output raw LLM text only, suppress terminal formatting headers",
    )

    args = parser.parse_args()

    # Ingest prompt
    prompt_text = read_prompt(args.message)
    resolved_model = resolve_model(args.provider, args.model)
    provider_inst = get_provider(args.provider)

    if not args.raw_only:
        print("=" * 60)
        print("=== Vanguard LLM API Router ===")
        print(f"Provider:    {args.provider}")
        print(f"Model:       {resolved_model} (requested: {args.model})")
        print(f"Prompt Size: {len(prompt_text)} chars / ~{len(prompt_text.split())} words")
        print("=" * 60)

    # Execute generation
    response: LLMResponse = provider_inst.generate(
        prompt=prompt_text,
        model=resolved_model,
        temperature=args.temperature,
        stream=args.stream,
    )

    if response.error:
        print(f"\n[ERROR] {response.error}", file=sys.stderr)
        return 1

    # Print response if not streamed
    if not args.stream and not args.raw_only:
        print("\n--- Response ---")
        print(response.content)
        print("----------------")
    elif not args.stream and args.raw_only:
        print(response.content)

    # Save output artifacts
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_model_name = resolved_model.replace("/", "_").replace(":", "_")
    base_filename = f"{timestamp}_{args.provider}_{clean_model_name}"

    response_file = output_dir / f"{base_filename}_response.md"
    meta_file = output_dir / f"{base_filename}_meta.json"

    response_file.write_text(response.content, encoding="utf-8")

    meta_payload = {
        "timestamp": timestamp,
        "provider": response.provider,
        "model": response.model,
        "requested_model": args.model,
        "temperature": args.temperature,
        "prompt": prompt_text,
        "latency_ms": response.latency_ms,
        "ttft_ms": response.ttft_ms,
        "tokens": {
            "prompt": response.prompt_tokens,
            "completion": response.completion_tokens,
            "total": response.total_tokens,
        },
        "cost_usd_micros": response.cost_usd_micros,
        "cost_usd": response.cost_usd_micros / 1_000_000.0,
        "response_file": str(response_file),
    }

    meta_file.write_text(json.dumps(meta_payload, indent=2), encoding="utf-8")

    if not args.raw_only:
        print("\n=== Execution Telemetry ===")
        print(f"Latency:     {response.latency_ms} ms (TTFT: {response.ttft_ms} ms)")
        print(f"Tokens:      {response.total_tokens} (prompt: {response.prompt_tokens}, completion: {response.completion_tokens})")
        print(f"Cost:        {response.cost_usd_micros} µUSD (${response.cost_usd_micros / 1_000_000.0:.6f})")
        print(f"Saved to:    {response_file}")
        print(f"Metadata:    {meta_file}")
        print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
