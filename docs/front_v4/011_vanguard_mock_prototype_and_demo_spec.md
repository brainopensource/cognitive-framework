# Vanguard Mock Beta Prototype & Demonstration Specification

**Document ID:** `VG-FE-011`  
**Version:** `0.4.1-beta`  
**Status:** `Normative / Authoritative`  
**Owner:** `Product Lead & Developer Relations Lead`  
**Target:** `vanguard/clients/cli/fixtures/`, `vg --demo`

---

## 1. Objectives of the Mock Beta Demonstration

The Mock Beta Testbed enables anyone (investors, enterprise stakeholders, open-source contributors) to experience the full Vanguard agentic coding workflow **instantly without needing LLM API keys, payment setups, or cloud dependencies**.

```
┌────────────────────────────────────────────────────────────┐
│                    VANGUARD DEMO RUNTIME                   │
├────────────────────────────────────────────────────────────┤
│ 1. Instant Start: `vg --demo`                              │
│ 2. Zero API Keys Required (Replays Pre-Recorded Session)   │
│ 3. Full Interactive TUI: Live Streaming, Diffs & Signatures│
│ 4. Deterministic 100% Success Rate                         │
└────────────────────────────────────────────────────────────┘
```

---

## 2. Built-in Demonstration Scenarios

| Scenario Flag | Title | Workflow Demonstrated |
| :--- | :--- | :--- |
| `vg --demo bugfix` | SWE Bug Fix | Agent investigates bug, reads test failure, writes patch, runs tests |
| `vg --demo approval` | Operator Approval | Agent requests high-risk `rm -rf` command; demonstrates Ed25519 signing |
| `vg --demo subagent` | Multi-Agent Swarm | Main coordinator delegates research to Subagent 1 and testing to Subagent 2 |
| `vg --demo full` | Complete TDD Loop | End-to-end task from requirement prompt to green tests |

---

## 3. Session Fixture Architecture (`fixtures/sessions/`)

The demo engine reads structured JSONL event fixtures with realistic token delays:

```jsonl
{"seq": 1, "timestamp": "2026-08-16T20:00:00.000Z", "kind": "run.started", "run_id": "demo_run_01", "manifest": "vg-code-swe-mini"}
{"seq": 2, "timestamp": "2026-08-16T20:00:00.200Z", "kind": "turn.started", "turn_index": 1}
{"seq": 3, "timestamp": "2026-08-16T20:00:00.500Z", "kind": "stream.thinking", "delta": "Analyzing the test failure in test_dispatch.py..."}
{"seq": 4, "timestamp": "2026-08-16T20:00:01.000Z", "kind": "tool.requested", "call_id": "call_1", "tool_name": "fs.read", "args": {"path": "vanguard/packages/kernel/dispatch.py"}}
{"seq": 5, "timestamp": "2026-08-16T20:00:01.300Z", "kind": "tool.completed", "call_id": "call_1", "tool_name": "fs.read", "result": "347 lines read", "exit_code": 0}
{"seq": 6, "timestamp": "2026-08-16T20:00:02.000Z", "kind": "approval.requested", "approval_id": "appr_demo", "descriptor": {"capability": "proc.exec", "action_descriptor": {"command": "git apply patch.diff"}}}
```

---

## 4. Interactive Walkthrough Script for Stakeholder Demos

1. **Launch Demo:**
   ```bash
   vg --demo
   ```
2. **Select Scenario:** The user selects `[1] SWE Bug Fix Scenario`.
3. **Observe Live Output:**
   * Watch reasoning stream in real-time.
   * Review the syntax-highlighted diff displayed in the terminal.
   * Press `[A]` on the keyboard to sign the Ed25519 capability approval.
   * Observe test execution output turning green.
4. **Inspect Ledger:** Type `/inspect` to view the deterministic append-only ledger entries and token spend.
