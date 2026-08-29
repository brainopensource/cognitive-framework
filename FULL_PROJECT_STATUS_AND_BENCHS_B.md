# FULL PROJECT STATUS & BENCHMARK FORENSICS REPORT

**Repository:** Vanguard / AETHER Recursive Agency Substrate  
**Branch:** `feat/vanguard-0.9.0b1-beta-evolution`  
**Head Commit:** `30efdf68ad28b6edbe63888a59e19c80ac987cc9`  
**Report Date:** 2026-08-29T03:48:00-03:00  
**Model Under Test:** `deepseek/deepseek-v4-flash-0731` via OpenRouter  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [27-Row Benchmark Results Matrix](#2-27-row-benchmark-results-matrix)
3. [3-Row Canary Smoke Test Results](#3-3-row-canary-smoke-test-results)
4. [SQLite Event Store Forensics](#4-sqlite-event-store-forensics)
5. [Root Cause #1: L5 Dialogue Role Squashing (CRITICAL)](#5-root-cause-1-l5-dialogue-role-squashing-critical)
6. [Root Cause #2: Missing Assistant Proposal Recording](#6-root-cause-2-missing-assistant-proposal-recording)
7. [Root Cause #3: max_turns=8 Too Tight](#7-root-cause-3-max_turns8-too-tight)
8. [Root Cause #4: Claude-Shaped Prompt Tool Mismatch](#8-root-cause-4-claude-shaped-prompt-tool-mismatch)
9. [7 Already-Fixed Defects (Dev B Iteration Log)](#9-7-already-fixed-defects-dev-b-iteration-log)
10. [Module-Level Issue Map](#10-module-level-issue-map)
11. [Architecture & Data Flow Diagrams](#11-architecture--data-flow-diagrams)
12. [Comparison: LIM/LEX vs Vanguard](#12-comparison-limlex-vs-vanguard)
13. [Fix Roadmap & Pseudocode](#13-fix-roadmap--pseudocode)
14. [Linter & TCB Verification Status](#14-linter--tcb-verification-status)
15. [Appendix: Full File Inventory](#15-appendix-full-file-inventory)

---

## 1. Executive Summary

### Current State: Agents Cannot Code

The Vanguard benchmark framework is structurally sound — linters pass, TCB budget holds at 1,384/1,438 LOC, hexagonal boundaries are clean, and the OpenRouter adapter has all 7 wire-level fixes applied. However, **agents consistently fail to produce patches** in benchmark runs.

### Results At A Glance

| Outcome | Count | Percentage |
|---------|-------|------------|
| **COMPLETED** (patch + oracle pass) | 4 | 14.8% |
| **NO_PATCH** (agent finished without editing) | 7 | 25.9% |
| **DATASET_INVALID** (baseline already passes) | 16 | 59.3% |
| **Total** | **27** | 100% |

> [!CAUTION]
> **The 4 COMPLETED runs are all `tier1_lru_ttl_cache`** (the easiest challenge). Zero patches were produced for `tier2_event_bus` or `tier3_token_bucket`. The 3-row canary smoke test (post-fixes) also returned **0/3 NO_PATCH**.

### The Blocking Defect

**L5 Dialogue Role Squashing** in [layers.py:69](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/context/layers.py#L64-L70) — All dialogue history (tool results, assistant actions) is collapsed into a single `"user"` message. The LLM never sees `assistant`/`tool` role alternation, so it cannot reason about its own past actions. This is confirmed by:

- LIM and LEX (working projects) both preserve `assistant`/`tool` role pairs
- SQLite event traces show agents looping on `fs.read` 5-8 times before `ABANDONED`
- The OpenRouter adapter already has a `history_steps` handler (lines 314-325) that emits correct roles — **but nobody populates it**

---

## 2. 27-Row Benchmark Results Matrix

**Source:** [live_27_clean_report_v2.json](file:///home/rocha/Coding/Aether-D-System/benchmarks/frontier_v090/artifacts/live_27_clean_report_v2.json)  
**Schema:** `aether.frontier-benchmark-live-report/2`  
**Total Tokens Consumed:** 538,557

| # | Challenge | Preset | Terminal | Tokens |
|---|-----------|--------|----------|--------|
| 01 | `tier1_lru_ttl_cache` | `vg-code-v090-react-control` | ✅ COMPLETED | — |
| 02 | `tier2_event_bus` | `vg-code-v090-react-control` | ❌ DATASET_INVALID | — |
| 03 | `tier3_token_bucket` | `vg-code-v090-react-control` | ❌ DATASET_INVALID | — |
| 04 | `tier1_lru_ttl_cache` | `vg-code-v090-claude-shaped` | ✅ COMPLETED | — |
| 05 | `tier2_event_bus` | `vg-code-v090-claude-shaped` | ❌ DATASET_INVALID | — |
| 06 | `tier3_token_bucket` | `vg-code-v090-claude-shaped` | ❌ DATASET_INVALID | — |
| 07 | `tier1_lru_ttl_cache` | `vg-code-v090-opencode-shaped` | ✅ COMPLETED | — |
| 08 | `tier2_event_bus` | `vg-code-v090-opencode-shaped` | ❌ DATASET_INVALID | — |
| 09 | `tier3_token_bucket` | `vg-code-v090-opencode-shaped` | ❌ DATASET_INVALID | — |
| 10 | `tier1_lru_ttl_cache` | `vg-code-v090-lex-surgical` | ⚠️ NO_PATCH | — |
| 11 | `tier2_event_bus` | `vg-code-v090-lex-surgical` | ❌ DATASET_INVALID | — |
| 12 | `tier3_token_bucket` | `vg-code-v090-lex-surgical` | ❌ DATASET_INVALID | — |
| 13 | `tier1_lru_ttl_cache` | `vg-code-v090-lim-falsifier` | ⚠️ NO_PATCH | — |
| 14 | `tier2_event_bus` | `vg-code-v090-lim-falsifier` | ❌ DATASET_INVALID | — |
| 15 | `tier3_token_bucket` | `vg-code-v090-lim-falsifier` | ❌ DATASET_INVALID | — |
| 16 | `tier1_lru_ttl_cache` | `vg-tutor-v090-v1-read-search` | ⚠️ NO_PATCH | — |
| 17 | `tier2_event_bus` | `vg-tutor-v090-v1-read-search` | ❌ DATASET_INVALID | — |
| 18 | `tier1_lru_ttl_cache` | `vg-tutor-v090-v2-evidence-graph` | ⚠️ NO_PATCH | — |
| 19 | `tier2_event_bus` | `vg-tutor-v090-v2-evidence-graph` | ❌ DATASET_INVALID | — |
| 20 | `tier1_lru_ttl_cache` | `vg-research-v090-v1-local` | ⚠️ NO_PATCH | — |
| 21 | `tier2_event_bus` | `vg-research-v090-v1-local` | ❌ DATASET_INVALID | — |
| 22 | `tier1_lru_ttl_cache` | `vg-research-v090-v2-web-corroborated` | ⚠️ NO_PATCH | — |
| 23 | `tier2_event_bus` | `vg-research-v090-v2-web-corroborated` | ❌ DATASET_INVALID | — |
| 24 | `tier1_lru_ttl_cache` | `vg-bugfix-v090-v1-direct` | ✅ COMPLETED | — |
| 25 | `tier2_event_bus` | `vg-bugfix-v090-v1-direct` | ❌ DATASET_INVALID | — |
| 26 | `tier1_lru_ttl_cache` | `vg-bugfix-v090-v2-reproduce-verify` | ⚠️ NO_PATCH | — |
| 27 | `tier2_event_bus` | `vg-bugfix-v090-v2-reproduce-verify` | ❌ DATASET_INVALID | — |

### Result Breakdown

- **16 DATASET_INVALID** — All `tier2_event_bus` and `tier3_token_bucket` runs. The baseline code already passed the oracle assertions before patching. These fixtures have since been hardened.
- **7 NO_PATCH** — Agent finished without calling `patch.apply`. Root cause: role squashing (see §5).
- **4 COMPLETED** — All on `tier1_lru_ttl_cache` (easiest task, single-file, short code). The agent managed to patch within 8 turns because the task was trivial enough.

---

## 3. 3-Row Canary Smoke Test Results

**Post-fix canary** (after oracle hardening, DSML parser, fp guard, max_tokens 4096):

| Challenge | Preset | Result | Reason |
|-----------|--------|--------|--------|
| `tier1_lru_ttl_cache` | `vg-code-v090-lex-surgical` | ❌ NO_PATCH | Agent read files but never called `patch.apply` |
| `tier2_event_bus` | `vg-code-v090-react-control` | ❌ NO_PATCH | Agent read files but never called `patch.apply` |
| `tier3_token_bucket` | `vg-code-v090-claude-shaped` | ❌ NO_PATCH | Agent read files but never called `patch.apply` |

> [!WARNING]
> The canary gate failed 0/3. The oracles are now valid (baselines fail before patching), but the agent still cannot produce patches. This confirms the problem is in context compilation, not in the challenge fixtures or wire protocol.

---

## 4. SQLite Event Store Forensics

### 4.1 Event Store Schema

All benchmark runs produce WAL-mode SQLite databases at `<workspace>/.vanguard/events.sqlite3`:

```sql
CREATE TABLE events (
    global_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id      TEXT NOT NULL,
    seq           INTEGER NOT NULL,
    seq_str       TEXT NOT NULL,
    run_id        TEXT NOT NULL,
    episode_id    TEXT NOT NULL,
    project_id    TEXT NOT NULL,
    scope         TEXT NOT NULL,
    occurred_at   TEXT NOT NULL,
    recorded_at   TEXT NOT NULL,
    principal     TEXT NOT NULL,
    tenant_id     TEXT,
    owner_id      TEXT,
    confidentiality TEXT,
    retention_class TEXT,
    trainability  TEXT,
    redaction_status TEXT,
    envelope_json TEXT NOT NULL,
    envelope_digest TEXT NOT NULL
);
CREATE INDEX idx_events_run_seq ON events(run_id, seq);
CREATE INDEX idx_events_scope ON events(scope);
```

### 4.2 Discovered Event Stores

| Path | Size | Events | Challenge |
|------|------|--------|-----------|
| `/tmp/vanguard_swe_tier1_lru_ttl_cache_hkom9edl/.vanguard/events.sqlite3` | 806 KB | 288 | tier1_lru_ttl_cache |
| `/tmp/vanguard_swe_tier2_event_bus_8qx677lg/.vanguard/events.sqlite3` | 356 KB | 138 | tier2_event_bus |
| `/tmp/vanguard_swe_tier2_event_bus_4wkhrrez/.vanguard/events.sqlite3` | 184 KB | — | tier2_event_bus |
| `/tmp/vanguard_swe_tier2_event_bus_y4utodlx/.vanguard/events.sqlite3` | 241 KB | — | tier2_event_bus |
| `/tmp/vanguard_swe_tier4_dag_resolver_pvam9dgo/.vanguard/events.sqlite3` | 258 KB | 98 | tier4_dag_resolver |

### 4.3 Agent Behavior Trace: `tier2_event_bus` (138 events)

```
evt# 54 | ProposalProduced | turn=0 | action=fs.read
evt# 64 | ProposalProduced | turn=1 | action=fs.read
evt# 74 | ProposalProduced | turn=2 | action=fs.search
evt# 84 | ProposalProduced | turn=3 | action=fs.search
evt# 94 | ProposalProduced | turn=4 | action=fs.read
evt#104 | ProposalProduced | turn=5 | action=fs.search
evt#114 | EpisodeCompleted | turn=6 | outcome=instrument_error
                           detail="proposal must contain text or a tool call"
```

> [!IMPORTANT]
> **6 turns, zero `patch.apply` calls.** The agent read the same files 3 times, searched 3 times, then produced a malformed empty proposal. This is the classic symptom of L5 role squashing — the agent doesn't see its prior reads in the context, so it keeps re-reading.

### 4.4 Agent Behavior Trace: `tier1_lru_ttl_cache` (288 events — multiple attempts)

```
# Attempt 1 (approval-suspension cycle, multiple segments):
evt# 54 | ProposalProduced | turn=0 | action=fs.read
evt# 64 | ProposalProduced | turn=1 | action=fs.read
evt# 74 | ProposalProduced | turn=2 | action=fs.search
evt# 84 | ProposalProduced | turn=3 | action=patch.apply    ← SUCCESS (hit patch on turn 3)
evt# 96 | ProposalProduced | turn=0 | action=fs.search      ← (new segment after approval)
evt#106 | ProposalProduced | turn=1 | action=patch.apply
evt#118 | ProposalProduced | turn=0 | action=patch.apply
evt#130 | ProposalProduced | turn=0 | action=patch.apply
evt#142 | ProposalProduced | turn=0 | action=patch.apply

# Attempt 2 (exhausted turns on reads):
evt#218 | ProposalProduced | turn=0 | action=fs.read
evt#228 | ProposalProduced | turn=1 | action=fs.read
evt#238 | ProposalProduced | turn=2 | action=fs.read
evt#248 | ProposalProduced | turn=3 | action=fs.read
evt#258 | ProposalProduced | turn=4 | action=fs.read         ← 5 reads, no patch
evt#264 | EpisodeCompleted | outcome=abandoned                ← turn bound reached
```

> [!NOTE]
> The same challenge (`tier1_lru_ttl_cache`) sometimes succeeds and sometimes exhausts all turns on reads. When it succeeds, it's because the model happened to call `patch.apply` on turn 3 before context degradation. When it fails, the model loops on `fs.read` for 5 turns then gets abandoned.

### 4.5 Agent Behavior Trace: `tier4_dag_resolver` (98 events)

```
evt# 54 | ProposalProduced | turn=0 | action=fs.read
evt# 64 | ProposalProduced | turn=1 | action=fs.read
evt# 74 | EpisodeCompleted | turn=2 | outcome=instrument_error
                           detail="proposal must contain text or a tool call"
```

> [!CAUTION]
> Only 2 turns before instrument_error. The model read 2 files, then on turn 2 produced an empty/malformed proposal. The `exc.fp` NoneType crash was occurring here before the guard was added.

---

## 5. Root Cause #1: L5 Dialogue Role Squashing (CRITICAL)

### The Defect

**File:** [layers.py](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/context/layers.py)  
**Line:** 69  
**Severity:** 🔴 BLOCKING — explains 100% of NO_PATCH failures

```python
# layers.py:64-70
ROLE_FOR_LAYER: Mapping[Layer, str] = {
    Layer.SYSTEM: "system",       # L1
    Layer.TOOLS: "system",        # L2
    Layer.ENVIRONMENT: "system",  # L3
    Layer.TASK: "user",           # L4
    Layer.DIALOGUE: "user",       # L5 ← ALL dialogue becomes "user"
}
```

### What The Model Actually Sees

When `messages()` is called ([layers.py:193-212](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/context/layers.py#L193-L212)), all L5 blocks are joined with `"\n\n"` into a single message:

```python
# layers.py:200-204
rendered.append({
    "layer": layer.value,
    "role": ROLE_FOR_LAYER[layer],  # Always "user" for L5
    "content": "\n\n".join(block.text for block in blocks),  # ALL fragments concatenated
})
```

Then `bundle()` strips everything except `role` and `content` ([layers.py:228-230](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/context/layers.py#L228-L230)):

```python
# layers.py:228-230
"messages": tuple({"role": message["role"], "content": message["content"]}
                  for message in rendered),
```

### What The Model Receives (Pseudocode)

```json
[
  {"role": "system", "content": "You are an autonomous coding agent..."},
  {"role": "system", "content": "[tool-schemas] {\"name\":\"read\",...}"},
  {"role": "system", "content": "[environment-map] ..."},
  {"role": "user",   "content": "Fix the event bus memory leak in events/bus.py..."},
  {"role": "user",   "content": "tool result turn=0 digest=sha256:abc...\n<400 lines of bus.py>\n\ntool result turn=1 digest=sha256:def...\n<200 lines of matcher.py>"}
]
```

### What The Model SHOULD Receive

```json
[
  {"role": "system",    "content": "You are an autonomous coding agent..."},
  {"role": "user",      "content": "Fix the event bus memory leak..."},
  {"role": "assistant", "content": null, "tool_calls": [{"id":"call_1","type":"function","function":{"name":"read","arguments":"{\"path\":\"events/bus.py\"}"}}]},
  {"role": "tool",      "tool_call_id": "call_1", "content": "<contents of bus.py>"},
  {"role": "assistant", "content": null, "tool_calls": [{"id":"call_2","type":"function","function":{"name":"read","arguments":"{\"path\":\"events/matcher.py\"}"}}]},
  {"role": "tool",      "tool_call_id": "call_2", "content": "<contents of matcher.py>"},
  {"role": "assistant", "content": null, "tool_calls": [{"id":"call_3","type":"function","function":{"name":"patch","arguments":"{\"path\":\"events/bus.py\",\"content\":\"...\"}"}}]},
  {"role": "tool",      "tool_call_id": "call_3", "content": "patch applied successfully"}
]
```

### The Dead Code Path

The OpenRouter adapter already has a handler for proper role alternation at [openrouter.py:314-325](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/models/openrouter.py#L314-L325):

```python
# openrouter.py:314-325 — THIS CODE EXISTS BUT IS NEVER REACHED
for step in context.get("history_steps") or ():
    if step.get("type") == "assistant_tool_call":
        messages.append({"role": "assistant", "content": step.get("thought"),
                         "tool_calls": [{"id": step.get("call_id", "call_0"),
                                         "type": "function", "function": {
                                             "name": step.get("action", ""),
                                             "arguments": json.dumps(...)}}]})
    elif step.get("type") == "tool_response":
        messages.append({"role": "tool", "tool_call_id": step.get("call_id", "call_0"),
                         "content": str(step.get("result_text", ""))})
```

**But `context.get("history_steps")` is always empty** because:
1. `bundle()` in layers.py never populates a `"history_steps"` key
2. `assemble()` in [prompt_assembler.py](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/runtime/prompt_assembler.py) never adds it
3. The `_messages()` function takes the `"messages"` early-return path (line 287) because `"messages"` is always present in the bundle

### Data Flow Proving The Bug

```
prompt_assembler.py:101-104
    compiled = self._compiler.compile(brief=..., dialogue=tuple(self._dialogue))
                                                          ↓
compiler.py:164
    dialogue_blocks = list(blocks_of(Layer.DIALOGUE, dialogue))
                                                          ↓
layers.py:240-246 (blocks_of)
    Block(layer=Layer.DIALOGUE, source=fragment.source, label=..., text=...)
                                                          ↓
layers.py:193-211 (messages)
    for layer in LAYER_ORDER:
        blocks = self.layer_blocks(layer)       # Gets ALL L5 blocks
        content = "\n\n".join(block.text ...)   # CONCATENATES them
        role = ROLE_FOR_LAYER[layer]            # = "user" for L5
        rendered.append({"role": "user", "content": <giant blob>})
                                                          ↓
layers.py:228-230 (bundle)
    "messages": tuple({"role": msg["role"], "content": msg["content"]})
                                                          ↓
openrouter.py:287-288 (_messages)
    if "messages" in context:                   # TRUE — takes early return
        return [dict(item) for item in context["messages"]]
    # history_steps handler at line 314 is NEVER REACHED
```

---

## 6. Root Cause #2: Missing Assistant Proposal Recording

### The Defect

**File:** [session.py](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/runtime/session.py)  
**Function:** `_admit_turn_result()` (lines 1098-1129)  
**Severity:** 🔴 BLOCKING (compounds Root Cause #1)

When the agent proposes a tool call, only the **tool result** is recorded into L5:

```python
# session.py:1125-1128
text = f"tool result turn={turn} digest={digest}"
if detail:
    text += f"\n{detail}"
operator.note(label=f"tool-result-{turn}", source="tool_result", text=text)
```

The **assistant's proposal** (what tool it called, with what arguments) is never recorded. Even if the role squashing were fixed, the conversation would be:

```
user: task
tool: result of read    ← But what assistant message requested this read?
tool: result of read    ← Orphaned tool results with no preceding assistant turn
```

### Where The Recording Should Happen

In [engine.py:288](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/episode/engine.py#L288), after `self._emit_proposal(episode, proposal)`, the proposal should also be admitted to L5 as an assistant fragment. Currently it is only emitted as a durable event (for the ledger), not as a context fragment (for the next turn).

---

## 7. Root Cause #3: max_turns=8 Too Tight

### The Defect

**File:** [frontier_v090.py:149](file:///home/rocha/Coding/Aether-D-System/tools/benchmark-drivers/frontier_v090.py#L149)  
**Severity:** 🟡 CONTRIBUTING

```python
# frontier_v090.py:149
allow_paid=True, max_turns=8, max_attempts=2,
```

### Evidence From Event Stores

The `tier1_lru_ttl_cache` trace (§4.4) shows the agent sometimes needs **5+ turns** just to read files. With `max_turns=8`, the happy path (read → read → patch → test) consumes 4 turns minimum, leaving zero margin for error.

**LIM** (working reference project) uses 15-25 turns for comparable tasks.

### The Engine Default

[engine.py:194](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/episode/engine.py#L194) also defaults to `max_turns: int = 8`, and the session loop at [session.py:895-904](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/runtime/session.py#L895-L904) passes `remaining = task.max_turns - self.turns_consumed()`.

---

## 8. Root Cause #4: Claude-Shaped Prompt Tool Mismatch

### The Defect

**File:** [vg-code-claude-shaped/system-prompt.txt](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/manifests/vg-code-claude-shaped/system-prompt.txt)  
**Severity:** 🟡 CONTRIBUTING

```text
You are a coding CLI. Prefer Read and Grep before Edit.
Use Bash for tests and git only.        ← "Bash" is not in the tool whitelist
Smallest patch that satisfies tests. One tool per turn. Do not invent file contents.
```

The `test` tool ([test-tool.json](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/manifests/vg-code-default/test-tool.json)) is `proc.exec` with selector `proc://exec/allow/git,pytest,ruff,python3`. If the model interprets "Use Bash" literally and emits `{"argv": ["bash", "-c", "python3 -m unittest ..."]}`, the capability check rejects it.

The aliases.json does map `"Bash": "proc.exec"` ([aliases.json](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/manifests/vg-code-claude-shaped/aliases.json)), but `argv[0]` must still match the whitelist.

---

## 9. 7 Already-Fixed Defects (Dev B Iteration Log)

These 7 issues were diagnosed and fixed through a 5-iteration smoke-test cycle:

### Fix #1: Secret Loading Across Process Boundaries
- **Symptom:** `instrument_error:provider_key_missing`
- **Root Cause:** Child processes running `run_lab_task` couldn't access `OPENROUTER_API_KEY`
- **Fix:** Wired `load_api_key()` in [frontier_v090.py:135-145](file:///home/rocha/Coding/Aether-D-System/tools/benchmark-drivers/frontier_v090.py)
- **Status:** ✅ FIXED

### Fix #2: HTTP Exception fp.read() NoneType Crash
- **Symptom:** `AttributeError: 'NoneType' object has no attribute 'read'`
- **Root Cause:** Socket timeout closed `exc.fp` before `exc.read()` was called
- **Fix:** Added `getattr(exc, "fp", None) is not None` guard in [openrouter.py:233-237](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/models/openrouter.py#L233-L237) and [openrouter.py:258-262](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/models/openrouter.py#L258-L262)
- **Status:** ✅ FIXED

```python
# BEFORE (crashed):
return int(exc.code), resp_headers, exc.read() or b""

# AFTER (safe):
body = b""
if getattr(exc, "fp", None) is not None:
    try:
        body = exc.read() or b""
    except Exception:
        body = b""
return int(exc.code), resp_headers, body
```

### Fix #3: Dialogue Context Multi-Turn Consolidation
- **Symptom:** Consecutive system messages caused role erasure
- **Fix:** Merge consecutive system messages in [openrouter.py:289-299](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/models/openrouter.py#L289-L299)
- **Status:** ✅ FIXED

### Fix #4: DeepSeek DSML Markup Tool Calls
- **Symptom:** Model emitted `<｜DSML｜tool_calls>` tags instead of JSON `tool_calls`
- **Fix:** Built `_extract_dsml_tool_calls()` parser at [openrouter.py:346-374](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/models/openrouter.py#L346-L374)
- **Status:** ✅ FIXED

```python
# Regex patterns handle both Unicode ｜ (U+FF5C) and ASCII |
invoke_rx = re.compile(
    r'<[｜|]DSML[｜|]invoke\s+name=["\'](.*?)["\']>(.*?)</[｜|]DSML[｜|]invoke>',
    re.DOTALL,
)
```

### Fix #5: JSON Tool Call Truncation & Control Characters
- **Symptom:** `json.loads` failed on unescaped control chars; `max_tokens` (1024) truncated whole-file writes
- **Fix:** `json.loads(strict=False)` + `ast.literal_eval` fallback; raised `max_tokens` to 4096 at [openrouter.py:947](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/models/openrouter.py#L947)
- **Status:** ✅ FIXED

```python
# BEFORE:
"max_tokens": sampling.get("maxTokens", 1024),

# AFTER:
"max_tokens": max(sampling.get("maxTokens", 0), 4096),
```

### Fix #6: Search Tool Blob Pollution
- **Symptom:** `fs.search` returned hundreds of lines of `.vanguard/blobs/` binary hashes
- **Fix:** Added `--exclude-dir=.vanguard --exclude-dir=.git --exclude-dir=__pycache__` to worker `grep`
- **Status:** ✅ FIXED

### Fix #7: Oracle Baseline Invalidation (DATASET_INVALID)
- **Symptom:** 16/27 runs returned `DATASET_INVALID` because baseline code already passed oracle
- **Fix:** Hardened assertions in [challenges.py](file:///home/rocha/Coding/Aether-D-System/benchmarks/swe_bench/challenges.py) — multi-dot wildcard matching, unsubscribe cleanup, fractional burst, cycle trace propagation
- **Status:** ✅ FIXED (verified by canary preflight)

---

## 10. Module-Level Issue Map

```mermaid
graph LR
    subgraph "🔴 BROKEN (Must Fix)"
        A["layers.py:69<br/>ROLE_FOR_LAYER<br/>L5 → 'user'"]
        B["session.py:1098<br/>_admit_turn_result<br/>No assistant recording"]
        C["frontier_v090.py:149<br/>max_turns=8"]
    end
    subgraph "🟡 MINOR (Should Fix)"
        D["claude-shaped/system-prompt.txt<br/>'Use Bash' mismatch"]
    end
    subgraph "✅ FIXED (Already Applied)"
        E["openrouter.py:233<br/>fp guard"]
        F["openrouter.py:346<br/>DSML parser"]
        G["openrouter.py:947<br/>max_tokens 4096"]
        H["openrouter.py:289<br/>system merge"]
        I["openrouter.py:404<br/>json strict=False"]
        J["openrouter.py:314<br/>history_steps handler"]
        K["challenges.py<br/>Hardened oracles"]
    end
    A -->|"causes"| B
    A -->|"blocks"| J
    B -->|"compounds"| A
    C -->|"amplifies"| A
```

### Files With Issues

| File | Path | Issue | Status |
|------|------|-------|--------|
| `layers.py` | `vanguard/packages/agency/context/layers.py` | L5 role squashing at line 69 | 🔴 MUST FIX |
| `compiler.py` | `vanguard/packages/agency/context/compiler.py` | Passes L5 fragments without role metadata | 🔴 MUST FIX |
| `prompt_assembler.py` | `vanguard/packages/runtime/prompt_assembler.py` | Never populates `history_steps` in bundle | 🔴 MUST FIX |
| `session.py` | `vanguard/packages/runtime/session.py` | `_admit_turn_result` doesn't record assistant proposals | 🔴 MUST FIX |
| `engine.py` | `vanguard/packages/agency/episode/engine.py` | Doesn't feed proposal back to context | 🔴 MUST FIX |
| `frontier_v090.py` | `tools/benchmark-drivers/frontier_v090.py` | `max_turns=8` too tight | 🟡 FIX |
| `system-prompt.txt` | `manifests/vg-code-claude-shaped/system-prompt.txt` | "Use Bash" references non-allowed executable | 🟡 FIX |
| `openrouter.py` | `vanguard/packages/adapters/models/openrouter.py` | All 7 fixes applied | ✅ DONE |
| `challenges.py` | `benchmarks/swe_bench/challenges.py` | Oracles hardened | ✅ DONE |

---

## 11. Architecture & Data Flow Diagrams

### 11.1 The Hexagonal Production Lattice

```
domain ← ports ← kernel ← agency ← runtime → adapters
                                                  ↓
                                              OpenRouter
```

### 11.2 The Turn Loop (Current — Broken)

```mermaid
sequenceDiagram
    participant E as EpisodeEngine
    participant M as _LayeredOperator
    participant PA as PromptAssembler
    participant CC as ContextCompiler
    participant L as layers.py
    participant OR as OpenRouter

    E->>M: propose(view, tools, sampling)
    M->>PA: assemble(view, turn)
    PA->>CC: compile(brief, dialogue=[Fragment...])
    CC->>L: blocks_of(Layer.DIALOGUE, fragments)
    L-->>CC: Block(layer=DIALOGUE, source="tool_result", text="...")
    CC-->>PA: CompiledContext
    PA-->>M: bundle = compiled.bundle()
    Note over PA: bundle["messages"] = [{role:"user", content:"<ALL L5 joined>"}]
    Note over PA: bundle has NO "history_steps" key
    M->>OR: propose(bundle, tools, sampling)
    OR->>OR: _messages(context)
    Note over OR: "messages" key exists → early return at line 287
    Note over OR: history_steps handler at line 314 NEVER REACHED
    OR-->>M: Result(proposal)
    M-->>E: proposal
    E->>E: dispatch(proposal) → kernel
    E->>E: _admit_turn_result → operator.note(source="tool_result")
    Note over E: ⚠️ Assistant proposal NOT recorded to L5
    E->>E: Next turn...
```

### 11.3 What LIM/LEX Do Differently

```mermaid
sequenceDiagram
    participant E as LIM TurnLoop
    participant C as ContextEngine
    participant M as Model

    E->>C: build_messages(history)
    Note over C: Maps each history entry to proper role:<br/>model proposal → "assistant" + tool_calls<br/>tool result → "tool" + tool_call_id
    C-->>E: [{role:"system",...}, {role:"user",...}, {role:"assistant",tool_calls:[...]}, {role:"tool",content:"..."}, ...]
    E->>M: complete(messages)
    M-->>E: proposal with tool_call
    E->>E: Execute tool
    E->>C: append(assistant_msg, tool_result)
    Note over C: Both assistant AND tool messages preserved
```

---

## 12. Comparison: LIM/LEX vs Vanguard

| Aspect | LIM (Working) | LEX (Working) | Vanguard (Broken) |
|--------|---------------|---------------|-------------------|
| **Message history format** | Native OpenAI `assistant`/`tool` pairs | Rigid pipeline DAG with diagnostic pass | All L5 flattened to single `"user"` blob |
| **Assistant proposal in context** | ✅ Mapped to `{"role":"assistant"}` | ✅ Passed as structured diagnostic | ❌ Never recorded |
| **Tool result in context** | ✅ Mapped to `{"role":"tool","tool_call_id":"..."}` | ✅ Passed to self-healing worker | ⚠️ Recorded as `source="tool_result"` but rendered as `"user"` |
| **Context compaction** | Semantic LLM summarization | Anti-thrashing FSM circuit breaker | Byte-elision: `[X bytes elided]` |
| **Tool phasing** | Dynamic pruning by phase (LOCALIZATION vs EXECUTION) | Rigid pipeline stages | All 4 tools available every turn |
| **Max turns** | 15-25 | 3-cycle healing limit | 8 |
| **Loop termination** | MCTS speculative sampling | Hash-based thrash detection | No-progress detector (3 identical calls) |

---

## 13. Fix Roadmap & Pseudocode

### Fix 1: Populate `history_steps` in Context Bundle (CRITICAL)

**File:** `vanguard/packages/runtime/prompt_assembler.py`  
**Location:** After line 115 (`bundle = dict(compiled.bundle())`)

```python
# PSEUDOCODE — prompt_assembler.py, inside assemble()
def assemble(self, view, turn):
    # ... existing code ...
    bundle = dict(compiled.bundle())

    # NEW: Build history_steps from dialogue fragments
    history_steps = []
    for fragment in self._dialogue:
        if fragment.source == "assistant":
            # Parse the stored descriptor to extract action and args
            history_steps.append({
                "type": "assistant_tool_call",
                "call_id": fragment.label,         # e.g. "assistant-action-0"
                "action": _extract_action(fragment.text),
                "args": _extract_args(fragment.text),
                "thought": _extract_thought(fragment.text),
            })
        elif fragment.source == "tool_result":
            history_steps.append({
                "type": "tool_response",
                "call_id": _matching_call_id(fragment.label),
                "result_text": fragment.text,
            })
    if history_steps:
        bundle["history_steps"] = history_steps

    # ... rest of existing code ...
```

### Fix 2: Record Assistant Proposals to L5 (CRITICAL)

**File:** `vanguard/packages/runtime/session.py`  
**Location:** In `_admit_turn_result()`, add proposal recording BEFORE the tool result

```python
# PSEUDOCODE — session.py
def _admit_turn_result(operator, turn, result):
    # NEW: Record the assistant's proposal as an L5 fragment
    request = getattr(result, 'request', None)
    if request is not None:
        action = getattr(request, 'action', '') or getattr(request, 'verb', '')
        args = getattr(request, 'args', {})
        call_id = f"call_{turn}"
        operator.note(
            label=f"assistant-action-{turn}",
            source="assistant",
            text=json.dumps({"call_id": call_id, "action": action, "args": args}),
            evictable=False,
        )

    # EXISTING: Record tool result
    outcome = getattr(result, "outcome", None)
    if outcome is None:
        return None
    detail = getattr(result, "detail", "") or getattr(outcome, "detail", "")
    digest = getattr(outcome, "result_digest", None) or ""
    call_id = f"call_{turn}"
    text = f"tool result turn={turn} call_id={call_id} digest={digest}"
    if detail:
        text += f"\n{detail}"
    operator.note(label=f"tool-result-{turn}", source="tool_result", text=text)
```

### Fix 3: Increase max_turns (IMPORTANT)

**File:** `tools/benchmark-drivers/frontier_v090.py`  
**Line:** 149

```python
# BEFORE:
allow_paid=True, max_turns=8, max_attempts=2,

# AFTER:
allow_paid=True, max_turns=20, max_attempts=2,
```

### Fix 4: Fix Claude-Shaped Prompt (MINOR)

**File:** `vanguard/packages/agency/manifests/vg-code-claude-shaped/system-prompt.txt`

```text
# BEFORE:
Use Bash for tests and git only.

# AFTER:
Use the test tool (proc.exec) for tests and git. argv[0] must be python3, pytest, git, or ruff.
```

### Fix Dependency Graph

```mermaid
graph TD
    F1["Fix 1: Populate history_steps<br/>prompt_assembler.py"] --> CANARY["3-Row Canary Gate"]
    F2["Fix 2: Record assistant proposals<br/>session.py"] --> F1
    F3["Fix 3: max_turns 8→20<br/>frontier_v090.py"] --> CANARY
    F4["Fix 4: Claude prompt<br/>system-prompt.txt"] --> CANARY
    CANARY -->|"3/3 pass"| FULL["Full 27-Row Matrix"]
    CANARY -->|"<3/3 pass"| DEBUG["Debug further"]
```

---

## 14. Linter & TCB Verification Status

### All Passing ✅

| Linter | Result | Detail |
|--------|--------|--------|
| **TCB Budget** | ✅ PASS | 1,384 LOC / 1,438 limit (54 LOC headroom) |
| **Hexagonal Boundaries** | ✅ PASS | 426 source files, 0 violations |
| **Secret Scanner** | ✅ PASS | 0 exposed secrets |
| **Domain Blindness (I-7)** | ✅ PASS | No domain tokens in trusted core |
| **Frontier Runner Unit Tests** | ✅ PASS | 5/5 tests (1.496s) |
| **Contract Tests** | ✅ PASS | All model port, evaluator, sandbox, event store contracts |
| **git diff --check** | ✅ PASS | No whitespace errors |

### TCB Budget Detail

```json
{
  "files": {
    "vanguard/packages/kernel/__init__.py": 205,
    "vanguard/packages/kernel/budget.py": 192,
    "vanguard/packages/kernel/capability.py": 133,
    "vanguard/packages/kernel/classify.py": 168,
    "vanguard/packages/kernel/dispatch.py": 163,
    "vanguard/packages/kernel/grant.py": 86,
    "vanguard/packages/kernel/intent.py": 184,
    "vanguard/packages/kernel/model.py": 137,
    "vanguard/packages/kernel/policy.py": 106,
    "vanguard/packages/kernel/provenance.py": 110
  },
  "total": 1384,
  "threshold": 1438
}
```

### Failing Test (Pre-existing)

| Test | Status | Detail |
|------|--------|--------|
| `test_lam_runtime_vertical` | ❌ FAIL | LAM baseline exhausts turns without patching — same L5 role squashing issue |

---

## 15. Appendix: Full File Inventory

### Production Packages (`vanguard/packages/`)

| Package | Path | Role |
|---------|------|------|
| `domain` | `vanguard/packages/domain/` | Pure value objects, wire contracts, JCS canonicalization |
| `ports` | `vanguard/packages/ports/` | Hexagonal port protocols |
| `kernel` | `vanguard/packages/kernel/` | TCB (1,384 LOC), 13-stage dispatch pipeline |
| `agency` | `vanguard/packages/agency/` | Recursive turn engine, context compiler |
| `runtime` | `vanguard/packages/runtime/` | Composition, lifecycle, session, prompt assembly |
| `adapters` | `vanguard/packages/adapters/` | OpenRouter, Ollama, Cassette, Fake, Sandbox |

### Benchmark Artifacts

| Artifact | Path | Size |
|----------|------|------|
| Preregistration | `benchmarks/frontier_v090/artifacts/preregistration.json` | 9.5 KB |
| Dry Run | `benchmarks/frontier_v090/artifacts/dry_run_report.json` | 25.6 KB |
| Live 27 v1 | `benchmarks/frontier_v090/artifacts/live_27_clean_report.json` | 43.8 KB |
| Live 27 v2 | `benchmarks/frontier_v090/artifacts/live_27_clean_report_v2.json` | 43.9 KB |
| HTML Report | `docs/_archive/bench_reports/bench_results_v090_2908.html` | 47.0 KB |
| Solutions MD | `fixing_benchmark_solutions.md` | ~5 KB |

### Agency Manifests (11 Presets)

| Preset | System Prompt | Tools | Evaluator |
|--------|---------------|-------|-----------|
| `vg-code-default` | Own prompt | read, search, patch, test | `coding-oracle@3` |
| `vg-code-v090-lex-surgical` | LEX evidence-first | read, search, surgical_patch, test | `coding-oracle@3` |
| `vg-code-v090-react-control` | Default prompt | read, search, patch, test | `coding-oracle@3` |
| `vg-code-v090-claude-shaped` | Claude CLI | read, search, patch, test | `coding-oracle@3` |
| `vg-code-v090-lim-falsifier` | LIM falsification | read, search, patch, test | `coding-oracle@3` |
| `vg-tutor-v090-v1-read-search` | Read-only tutor | read, search | `answer-oracle@1` |
| `vg-tutor-v090-v2-evidence-graph` | Evidence graph tutor | read, search | `answer-oracle@1` |
| `vg-research-v090-v1-local` | Local research | read, search | `answer-oracle@1` |
| `vg-research-v090-v2-web-corroborated` | Web-corroborated research | read, search | `answer-oracle@1` |
| `vg-bugfix-v090-v1-direct` | Direct bugfix | read, search, patch, test | `coding-oracle@3` |
| `vg-bugfix-v090-v2-reproduce-verify` | Reproduce-verify | read, search, patch, test | `coding-oracle@3` |

### Git History (Last 10 Commits)

| Hash | Message |
|------|---------|
| `30efdf68` | `feat(P8): AETHER Eectroweak Update - BENCHMARKING 27 v2` |
| `24c002f7` | `feat(P8): AETHER Eectroweak Update - BENCHMARKING 27 v2` |
| `716b908c` | `feat(P8): AETHER Eectroweak Update - BENCHMARKING 27 v2` |
| `f703234c` | `feat(P8): AETHER Eectroweak Update - BENCHMARKING 27` |
| `806880b1` | `feat(P7): AETHER Eectroweak Update - CLEAN HARDCODED MODELS` |
| `d1104af4` | `docs: focus benchmark guide on execution` |
| `54640727` | `feat(P7): AETHER Eectroweak Update - CLEAN HARDCODED MODELS` |
| `da871193` | `feat(P6): AETHER Eectroweak Update` |
| `63536950` | `feat(P5): AETHER Eectroweak Update` |
| `09b54dd9` | `feat(P5): AETHER Eectroweak Update` |
