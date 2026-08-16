# Harness DNA (Pack) Improvements — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `vg-code-default` and `vg-shell-only` comparable, honest genes — then add reconstruction packs as data only — without changing `EpisodeEngine` or kernel dispatch.

**Architecture:** Packs stay JSON/text under `vanguard/packages/agency/manifests/`. The translator maps tool **names** from the frozen pack, not from a hardcoded competitor dict. Paired bench uses the same live model and HOLDOUT tasks; `vg-shell-only` remains undeletable.

**Tech Stack:** existing manifest parser, `Runtime.compose` / `execute_harness`, `zero_hint_v1` runner, `verdict.evidence_label`.

## Global Constraints

- Zero edits to `vanguard/packages/kernel/` or `agency/episode/engine.py` unless a reconstruction **cannot** compose (then stop and write a finding).
- `D_treatment` for DNA trials is **only** `manifest` (and declared gene hashes). Model, sampling, task set, max-turns stay in `K_compat`.
- Do not claim a lift at n<20; n=HOLDOUT (3) is a **case study**.
- Do not start DNA A/B until a model can `patch.apply` (or shell-write) on T1. Calibration is Plane C, already gated by LAR `calibration_passed`.
- Aliases (`Read`→`fs.read`) live in pack-local data, never a global Python dict of product names.

---

## File map

| Path | Responsibility |
|------|----------------|
| `vanguard/packages/agency/manifests/vg-code-default/*` | Product DNA (prompt, tools, context, budget, routing) |
| `vanguard/packages/agency/manifests/vg-shell-only/*` | Control DNA |
| `vanguard/packages/agency/manifests/vg-code-default/aliases.json` | Optional name→verb map (new) |
| `vanguard/packages/agency/episode/` translator (existing) | Consume pack tool schemas + aliases only |
| `benchmarkings/zero_hint_v1/run_live_agent.py` | `--manifest` flag for paired arms |
| `benchmarkings/zero_hint_v1/pairs/` | Case-study artefacts (gitignored if live) |

---

### Task 1: Gene digest in composition (comparability)

**Files:**
- Modify: manifest freeze / `Runtime.compose` output to include per-file SHA-256 of prompt, each tool schema, context/budget/routing policies
- Test: `test/agency/test_manifest_gene_digests.py`

**Interfaces:**
- Produces: `gene_digests: dict[str, str]` on the frozen harness

- [ ] **Step 1:** Failing test: two composes of `vg-code-default` have identical `gene_digests`; changing `system-prompt.txt` bytes changes only that digest.
- [ ] **Step 2:** Implement digest map at compose time (hash file bytes already loaded).
- [ ] **Step 3:** Emit `gene_digests` into `zero_hint_v1` `result.json` `K_compat` / treatment block.

---

### Task 2: Pack-local aliases (translator becomes data)

**Files:**
- Create: `vanguard/packages/agency/manifests/vg-code-default/aliases.json` e.g. `{"read":"fs.read","search":"fs.search","patch":"patch.apply","test":"proc.exec"}`
- Modify: proposal translator to load aliases from the composed pack; unknown names → `instrument_error`
- Test: unknown tool name fails closed; alias `read` maps to `fs.read`

Do **not** add `Bash`/`Read` Claude names until a reconstruction pack exists (Task 5).

---

### Task 3: `--manifest` on the lab runner (paired arms)

**Files:**
- Modify: `benchmarkings/zero_hint_v1/run_live_agent.py`
- Test: argparse accepts `vg-shell-only` and `vg-code-default`; result.json records `manifest` and `evidence_label=lab-execute-harness`

Shell-only arm: same HOLDOUT fixture; model may only `proc.exec` (git, pytest, ruff — note python3 may need to be on the allowlist for fairness, **or** document M-12 if one arm cannot run tests). If `vg-shell-only` cannot run `python3`, that is a DNA bug to fix in the pack selector, not in the kernel.

---

### Task 4: Case-study protocol (not a published lift)

**Files:**
- Create: `benchmarkings/zero_hint_v1/PAIRING.md` (one page: same model, same task, both manifests, 8-turn cap, record tool histogram)
- Run only after T1 `patch.apply` exists

Report: discordant outcomes, turns, tokens. No p-value.

---

### Task 5: Reconstruction packs as data (S7 T7.6)

**Files:**
- Create directories `vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini` copying default pack + prompt/alias deltas only
- Test: `Runtime.compose` each path with **zero** engine edits
- `lab harness diff` can wait; `diff -u` of gene files is enough for this task

**Honesty label:** these are reconstructions of tool surface + prompt, not Anthropic’s scheduler (depth-1 remains).

---

### Task 6: Prompt DNA experiment (optional, after Task 4)

Replace the one-line `vg-code-default/system-prompt.txt` with a slightly longer **frozen** prompt (hash it). Paired vs previous digest on HOLDOUT. One variable. If it does not beat the one-liner, revert.

---

## Stop conditions

- Compose of a new pack requires `episode/engine.py` change → finding, not a workaround.
- Shell-only cannot express a file write that default can → fix pack capabilities (M-12) before claiming typed-tool lift.
- Calibration still failing → do not spend OpenRouter on DNA.

## Execution handoff

Implement Task 1–3 before any live DNA run. Task 4 is operator-gated. Task 5 is framework-as-builder proof, still data-only.
