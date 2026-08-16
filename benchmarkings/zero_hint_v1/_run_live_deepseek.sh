#!/usr/bin/env bash
set -u
cd /home/rocha/Coding/Aether-D-System
export PYTHONUNBUFFERED=1
echo "=== live agent: test004_busy_merge via openrouter deepseek/deepseek-chat ==="
python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test004_busy_merge \
  --model deepseek/deepseek-chat \
  --max-turns 12
