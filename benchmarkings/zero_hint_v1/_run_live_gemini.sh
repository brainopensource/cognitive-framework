#!/usr/bin/env bash
set -u
cd /home/rocha/Coding/Aether-D-System
export PYTHONUNBUFFERED=1
echo "=== live agent: test004_busy_merge via openrouter google/gemini-2.0-flash-001 ==="
python3 benchmarkings/zero_hint_v1/run_live_agent.py \
  --task test004_busy_merge \
  --model google/gemini-2.0-flash-001 \
  --max-turns 12
