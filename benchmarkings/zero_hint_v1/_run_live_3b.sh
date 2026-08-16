#!/usr/bin/env bash
set -u
cd /home/rocha/Coding/Aether-D-System
export PYTHONUNBUFFERED=1
echo "=== live agent: test004_busy_merge via ollama llama3.2:3b ==="
python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test004_busy_merge \
  --model ollama/llama3.2:3b \
  --max-turns 12
