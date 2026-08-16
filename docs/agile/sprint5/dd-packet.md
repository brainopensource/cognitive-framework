# Lane DD Developer Packet — CLI Interface Realignment & JSONL Stream Ingestion

**Assignee:** Mid Developer D  
**Tickets:** `S5-DD-001`  
**Complexity:** Level 2 / 5 (Fast Lane)  
**Contract Row:** [`REQ-CLI-001`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json)  
**Owned Code:** `vanguard/clients/cli/`  
**Target Test:** `npm --workspace @vanguard/cli test`

---

## 1. Scope & Objective
Refactor the `@vanguard/cli` TypeScript client to align its internal interfaces with the normative [`docs/development/cli_tui_architecture.md`](file:///home/rocha/Coding/Aether-D-System/docs/development/cli_tui_architecture.md) specification.

Consume live `EventEnvelope` streams from standard JSONL streams / IPC sockets rather than in-memory mocking.

---

## 2. Invariants & Rules
1. **Hexagonal Isolation:** The CLI package lives outside `vanguard/packages/`. It must never import internal Python files or backend symbols directly.
2. **Deterministic Replay:** `vg trace <run_id>` and `vg why <artifact_id>` must render inspectable views directly from recorded JSONL event lines without calling an LLM.
3. **Headless Cleanliness:** In headless mode (`vg run --headless`), output is strictly clean JSON lines on stdout; interactive prompts are suppressed.

---

## 3. First Failing Test & Verification
```bash
npm --workspace @vanguard/cli test
```
Must prove: Headless runner parses real `EventEnvelope` lines; trace command renders timeline from golden cassette JSONL; `vg why` displays activation evidence.
