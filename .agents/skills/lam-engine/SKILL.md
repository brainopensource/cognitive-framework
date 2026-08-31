---
name: lam-engine
description: LLM API Mock (LAM) Engine for zero-cost sub-millisecond mock completions, offline test replays, and cassette capture. Use for fast benchmark iterations and agent harness smoke testing.
version: "1.0.0"
authority: operational
---

# LLM API MOCK (LAM) — Autonomous Agent Guide

The **LAM Engine** allows agents and developers to simulate LLM endpoints with **$0.00 cost** and **<1ms latency**, completely decoupled from any specific repository or network dependency.

---

## 1. Quick CLI Usage

```bash
# 1. Run synthetic benchmark tests offline (50+ scenarios)
python3 tools/002_LLM_API_MOCK/cli.py bench --count 50

# 2. View token savings & recorded telemetry
python3 tools/002_LLM_API_MOCK/cli.py stats

# 3. Start local OpenAI / Ollama compatible HTTP proxy
python3 tools/002_LLM_API_MOCK/cli.py serve --port 8000
```

---

## 2. MCP Server Configuration

To connect LAM to any MCP-compatible client (Antigravity, Claude Code, Cursor, Zed):

```json
{
  "mcpServers": {
    "lam-engine": {
      "command": "python3",
      "args": ["tools/002_LLM_API_MOCK/mcp_server.py"]
    }
  }
}
```

Exposed MCP tools:
- `lam_complete`: Offline mock completion across capability tiers (`tier-1` to `tier-5`).
- `lam_replay_cassette`: Hermetic replay of recorded benchmark cassettes.
- `lam_list_scenarios`: Discover available synthetic coding scenarios.
- `lam_get_stats`: Retrieve total token savings and call volume.

---

## 3. Recording Benchmark Sessions for Offline Replay

When running benchmarks, developers and agents can wrap LLM calls with `MockRecorder` to persist request/response pairs into `tools/002_LLM_API_MOCK/runs/` and `lam.sqlite`:

```python
from recorder import MockRecorder
recorder = MockRecorder("tools/002_LLM_API_MOCK/lam.sqlite")
# Records request_sha256, response_sha256, prompt/completion tokens, and cost.
```
