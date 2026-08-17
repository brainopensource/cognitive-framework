# Wave 11–13 — PO acceptance (coding harness backend)

Not a second board. Status lives on `docs/scrum/roadmap_backend.md`. **REQ-TRUST-001.**

## Product

`vg-code-default` compiles into an isolated episode that can **inspect → edit → pytest** on a workspace. Greenfield and bugfix are the same `HarnessSession.run` path. Two modes: `interactive=True` (approvals) and `interactive=False` (BENCHMARK fail-closed).

Compiler + pack + MOCK driver **is not** a daily-driver Claude. We do not publish a SWE score.

## Done when (evidence)

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | `lab/run.py` multi-turn from ledger, not `{turnCount: 1}` stub | `[TODO]` | This tree: `lab/run.py` still stubs. ALFA claims `runtime/repair.py` @ `954478f` — **those files are not on this tree.** |
| 2 | Privileged verbs: INTERACTIVE suspends, BENCHMARK denies | `[TODO]` in this tree | Claimed W11-A; `runtime/root.py` still has the two modes. Proof tests not re-verified here as ALFA-owned files. |
| 3 | Session log = ledger projection `vg.coding-session.v1` | `[DONE]` | `tools/export_coding_session.py`; no second DB |
| 4 | Skill prefix ≤4k; bodies via `fs.read` | formatter `[DONE]`; pack genes `[TODO]` BETA | `format_skill_index`; `docs/scrum/sprints/wave11/skill.example.json` |
| 5 | File-todo, not a kernel verb | `[TODO]` BETA | — |
| 6 | MOCK dogfood dirs exist | `[TODO]` BETA | LAM keeps missing tasks in the denominator (`test/lab/test_coding_instrument.py`) |
| Q2 | Live DOGFOOD-01..03, no mid-run hand-patch | `[TODO]` human | Runbook: `docs/scrum/sprints/wave11/s8-j-03-dogfood-runbook.md` |

## Human-only

- Rotate OpenRouter key (`S7-J-04`).
- Spend sign-off (`S9-J-03`).
- Live Q2 execution (`S8-J-03`).
