#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
TASKS=(test003_invoice_cents test005_named_amounts)
MANIFESTS=(vg-code-default vg-code-claude-shaped)
MODELS=(deepseek/deepseek-v4-flash openai/gpt-4o-mini)
for manifest in "${MANIFESTS[@]}"; do
  for model in "${MODELS[@]}"; do
    echo "=== MATRIX ${manifest} x ${model} ==="
    python3 benchmarkings/zero_hint_v1/run_live_agent.py \
      --task test003_invoice_cents \
      --task test005_named_amounts \
      --manifest "$manifest" \
      --model "$model" \
      --max-turns 8 || true
  done
done
