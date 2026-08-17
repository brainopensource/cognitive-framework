# v0.5.0 concept lock — proposal only

**Not VG-04. Not a second board.** Fold into `roadmap_backend.md` on a branch **after** `feat_sprint_special` → `main` as v0.4.5-beta.

**REQ-TRUST-001.**

## Lock before v0.5 implementation

| Concept | v0.4.5 state | v0.5 may lock |
|---|---|---|
| One dispatch path | Episode engine + kernel | Unchanged. No OpenCode/Claude `while True` |
| One effect per turn | Translator refuse + `terminalRefusal` | Keep. Pack DNA must emit one call; do not batch in the engine |
| Empty repo | Write-first gene + sequenced TASK.md | First live **verb** on greenfield (or keep named refusal) |
| Session | Ledger + JSONL | Same; no second DB |
| Modes | INTERACTIVE vs BENCHMARK | Writes need a human or test approver; no YOLO in BENCHMARK |
| TUI | Out of 0.4.5 | OpenCode-class CLI **after** headless one-tool turns work |
| MCP / playbooks / G_C | Rejected | Still deferred |

## Must not lock as “done” in 0.4.5

Daily-driver Claude, `oracle_green`, Q2, published lift, GUI/daemon.
