# S21-G-02 — Greenfield zero-turn cause (archived)

**Date:** 2026-08-17 · **GAMMA** · **REQ-TRUST-001**  
**Not a model comparison. Not a lift. 0/4 `oracle_green` remains legal.**

ALFA named the cause in `docs/scrum/sprints/sprint20/evidence/s20-a-live-tool-calling-turn.md` and `vanguard/packages/runtime/outcome_labels.py`. Do not re-score models here.

## What was true

| Arm | GREENFIELD-API-HTML | Label |
|---|---|---|
| Live (S19/S20 first) | 0 turns, `instrument_error` soup | **instrument defect** (60s timeout + `model_not_invoked` masking) |
| After timeout 300s | 0→1 turn on that change alone | still not green |
| Remaining live | translator refuse | **`instrument_error:multi_action_proposal`** — “multiple actions in one proposal are unsupported”; one turn = one effect |
| MOCK | episode not skipped | `test_s21_named_causes.GreenfieldIsAValidWorkspace.test_the_mock_runs_an_episode_on_it` asserts `turns > 0` |

Falsified (ALFA): compose refuses empty tree; IndexPort on empty tree (`index_component` is None on `vg-code-default` compose in that test). Workspace has `TASK.md`, no `src/` — that is the task, not a broken fixture.

`deepseek-r1:14b` prose-only vs `llama3.2:3b` tool-calls is **not** published as a ranking. It is a labelled property of that Ollama tag on this pack. Do not compare models until greenfield live `turns≥1` *and* a tool-calling verb is on the session (S21-G-02). Live greenfield’s named stop is multi-action, not “the model cannot code.”

## Denominator

4 tasks. Missing: 0. `oracle_green`: 0. Named instrument errors stay in the denominator (`test_every_labelled_cause_stays_in_the_denominator`).
