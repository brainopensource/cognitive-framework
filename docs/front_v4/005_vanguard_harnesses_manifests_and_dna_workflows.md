# Vanguard Harnesses, Manifests & Agentic DNA Engine Integration

**Document ID:** `VG-FE-005`  
**Version:** `0.4.1-beta`  
**Status:** `Normative / Authoritative`  
**Owner:** `Agency Plane Lead & Principal Architect`  
**Related Specs:** [`03_vanguard_architecture_planes_and_execution_model_v040.md §11`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md), [`ADR-0065`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/09_vanguard_decision_register_v040.md#L195)

---

## 1. Concept: Manifests as Declarative Agent DNA

In Vanguard, an agent is not hardcoded in procedural logic; it is instantiated from a **Declarative Manifest (DNA)**.

A manifest declares:
1. **Capabilities & Tool Palette:** The precise set of permitted tools (`fs.read`, `fs.write`, `proc.exec`, `git.status`).
2. **Layered Prompt Prefix (L1–L4):** Cached, deterministic system instructions and persona.
3. **Approval Policies:** Which capabilities trigger automatic approval vs interactive Ed25519 signing.
4. **Budget & Horizon Limits:** Maximum context window, turns, and cost ceilings.

```
┌──────────────────────────────────────────────────────────────────┐
│                   VANGUARD MANIFEST (Agent DNA)                  │
├───────────────────┬─────────────────────────┬────────────────────┤
│ Capabilities (L1) │ System Context (L2-L4)  │ Policy Rules (Gov) │
│ - fs.read         │ - Identity: Senior Dev  │ - fs.write: Auto   │
│ - fs.write        │ - Tool Guidelines       │ - proc.exec: Sign  │
│ - proc.exec       │ - Verification Strategy │ - git.push: Sign   │
└───────────────────┴─────────────────────────┴────────────────────┘
```

---

## 2. Standard Built-in Manifests

| Manifest ID | Primary Use Case | Permitted Tools | Policy Profile |
| :--- | :--- | :--- | :--- |
| **`vg-code-default`** | Full-stack software engineering | `fs.*`, `proc.exec`, `git.*`, `ast.*` | File writes auto; destructive shell commands require operator sign |
| **`vg-code-swe-mini`** | Fast, lightweight bug fixing & review | `fs.read`, `fs.write_patch`, `proc.exec` | Read-only auto; edits & execution require confirmation |
| **`vg-shell-only`** | Terminal automation & sysadmin tasks | `proc.exec` (single canonical tool) | All external side-effects require operator sign |
| **`vg-reviewer`** | Read-only code audit & vulnerability scan | `fs.read`, `ast.query`, `git.diff` | Strict zero side-effects; pure read-only |

---

## 3. Frontend Manifest Discovery & Schema Explorer

The frontend queries the daemon via RPC `ListManifests` or reads registered schemas from `vanguard/packages/agency/manifests/`.

### Manifest JSON Structure (Frontend Contract)
```json
{
  "manifest_id": "vg-code-swe-mini",
  "version": "1.0.0",
  "name": "SWE Mini Agent",
  "description": "Optimized lightweight harness for benchmarkings and quick patch application",
  "capabilities": [
    { "name": "fs.read", "risk": "low", "approval": "auto" },
    { "name": "fs.write", "risk": "medium", "approval": "auto" },
    { "name": "proc.exec", "risk": "high", "approval": "interactive_sign" }
  ],
  "budget": {
    "default_max_turns": 10,
    "default_max_tokens": 64000,
    "token_bucket_rate": 2000
  },
  "prompt_layers": {
    "l1_identity": "You are a senior software engineer working in a sandboxed repo.",
    "l2_rules": "Always verify changes with existing unit tests before completing."
  }
}
```

---

## 4. Layered Prompt Inspection Surface (L1–L5)

The frontend provides an interactive inspector view (`/prompt` or `Ctrl+I`) to allow developers to inspect prompt caching breakpoints:

* **L1 (System Base):** Universal harness rules & JSON Schema specs (Cached, immutable).
* **L2 (Persona / Manifest DNA):** Specific manifest instructions & capabilities (Cached).
* **L3 (Environment & Workspace):** Git status, repo paths, environment tools (Cached per session).
* **L4 (Historical Memory & Context):** Recalled memory vectors & test results (Cached prefix).
* **L5 (Turn Dynamic):** Current user prompt & immediate tool outputs (Uncached / Volatile).

---

## 5. Multi-Agent & Subagent Topology Visualization

When a parent agent spawns subagents (`Principal::Subagent`), the frontend renders the execution hierarchy in real time:

```
┌──────────────────────────────────────────────────────────┐
│ ⚡ Coordinator Agent (#run_01HPX9)                        │
│   ├── ⚙ Subagent 1 [Research]: Analyzing codebase (Done) │
│   │     └─ fs.read_file('vanguard/packages/kernel/..')   │
│   └── ⚙ Subagent 2 [Test Runner]: Executing tests        │
│         └─ proc.exec('python3 -m unittest ...')          │
│               └─ [Status: RUNNING (PID 48201)]           │
└──────────────────────────────────────────────────────────┘
```
