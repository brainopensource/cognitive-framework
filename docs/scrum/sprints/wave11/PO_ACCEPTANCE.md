# Wave 11–20 — PO acceptance (coding harness backend)

Not a second board. Status: `docs/scrum/roadmap_backend.md`. **REQ-TRUST-001.** Product version: **v0.4.5-beta** (`pyproject.toml`).

Compiler + pack + honest driver **is not** a daily-driver Claude. We do not publish a SWE score.

## Done when (evidence)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | `lab/run.py` computes nothing; driver is `runtime/lab_driver.py` | `[DONE]` | Shim + `test_lab_run_shim_computes_nothing`. ALFA `890216b` / `9192be1` |
| 2 | INTERACTIVE suspends, BENCHMARK denies (real policy) | `[DONE]` (ALFA cited) | S18 `9192be1` — not re-run in this GAMMA session |
| 3 | Session log `vg.coding-session.v1` from ledger envelopes | `[DONE]` | `tools/export_coding_session.py`; ALFA kind-attribute fix |
| 4 | Skill prefix ≤4k; bodies via `fs.read` | `[DONE]` | `format_skill_index` + BETA `test_skills_are_load_bearing_not_decorative` (`005dd95`) |
| 5 | File-todo, not a kernel verb | `[DONE]` | `.vanguard/todo.md` via `patch.apply` (BETA) |
| 6 | MOCK dogfood dirs exist (4/4 in denominator) | `[DONE]` | `lab/tasks/dogfood-0N-*` + `greenfield-api-html`; LAM `workspaceMissingCount=0` |
| 7 | MOCK is a real loop (not fabricated `turnCount:1`) | `[DONE]` (ALFA cited) | 4 turns → `attempts_exhausted`; tape ≠ gold |
| 8 | Live `oracle_green` or live tool-calling turn | `[TODO]` | Ollama ran; no green; no archived first live turn |
| Q2 | Live DOGFOOD-01..03, no mid-run hand-patch | `[TODO]` human | `s8-j-03-dogfood-runbook.md` |
| Spend | S9-J-03 | `[TODO]` | — |
| Claude daily-driver | — | `[TODO]` | v0.5+ |

## Human-only

- Rotate OpenRouter key (`S7-J-04`).
- Spend sign-off (`S9-J-03`).
- Live Q2 (`S8-J-03`).
- Frontend / daemon (`FE-N1`) later.
