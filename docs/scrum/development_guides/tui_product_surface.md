# TUI product surface — Claude Code / OpenCode-class terminal (Phase 1)

Status: `PROPOSED`  
Authority: `frontend_senior_review_and_two_lanes.md` D2  
Lane: **FE-2** (`vanguard/clients/cli/**`)  
Harvest: public UX atoms only (`features_to_add_v430.md` §1–2). Packs/models/sandbox stay backend (BETA/ALFA).

Ink is the skin. `@vanguard/client-core` is the brain. Do not add daemon verbs.

---

## 1. What “SOTA TUI” means here

Match the **operator loop** of Claude Code / OpenCode TUI / Codex CLI — not their source:

1. Type a brief → run starts.  
2. Stream thoughts and tool cards as they happen.  
3. Stop with a key (`requestCancel`).  
4. Approve a privileged patch with a real diff (`y`/`n`/`c`).  
5. Resume a durable run (`requestResume`).  
6. Headless JSONL for scripts.  
7. Never look like live when it is mock (`source: mock`).

Pi-length chrome: small header, dense transcript, one prompt bar. Not a dashboard of unused panels.

---

## 2. Layout (binding for FE-2)

```text
┌─ vg · source · seq · budget ─────────────────────────┐
│ transcript (virtualized)   │ detail / approval / why │
│  tool cards, thoughts      │                         │
├────────────────────────────┴─────────────────────────┤
│ prompt bar  (brief)     hints: ctrl+c cancel · ?     │
└──────────────────────────────────────────────────────┘
```

| Region | Behavior |
|---|---|
| Status | `source`, connection, last `payload.kind`, budget from `BudgetCommitted` |
| Transcript | Incremental `reduceRunView`; cap rendered rows; ring buffer already in live adapter |
| Detail | Selected tool/effect payload; `explainArtifact` → `not_available` if empty (no fiction) |
| Approval | Diff + verb/path copy; optimistic UI = `requested` only until `ApprovalResolved` |
| Prompt | Feeds `StartRun.brief`; empty Enter is invalid_request locally |

---

## 3. Keys (map to existing client methods only)

| Keys | Action |
|---|---|
| type + Enter | `startRun` / follow-up brief if a run is active **only if** backend already accepts that shape — else new run |
| `ctrl+c` / Esc (when not in text) | `requestCancel` |
| `y` / `n` / `c` | approve / reject / correct (P0-4) |
| `q` | quit TUI, abort local stream |
| `?` | key help (no color-only info; `NO_COLOR`) |

Do not invent `/mcp`, `/plugin`, parallel sessions (P3).

---

## 4. Performance

- One stream owner (`useVanguardRun`).  
- Do not re-reduce the full ledger on every keystroke.  
- Bound thoughts/tools lists (already slice(-20) / slice(-6) — keep).  
- No sleep in tests.

---

## 5. Reuse in GUI

GUI must not import these Ink files. Same regions become **slots** fed by the same reducers.
