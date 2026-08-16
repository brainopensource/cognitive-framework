#!/usr/bin/env bash
set -u
cd /home/rocha/Coding/Aether-D-System
export PYTHONUNBUFFERED=1
echo "=== live agent: test004_busy_merge via ollama qwen3.6:27b ==="
python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test004_busy_merge \
  --model ollama/qwen3.6:27b \
  --max-turns 12
