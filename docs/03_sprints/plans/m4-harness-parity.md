---
id: SPRINT-M4-HARNESS-PARITY
file: docs/03_sprints/plans/m4-harness-parity.md
title: "Staged plan — v0.5.0 MHF M4: Harness Parity (five packs, one frozen Layer 0)"
status: STAGED
milestone: M4 (of M0–M6, docs/SPEC.md §8) — EPIC-M4-PARITY
epic: EPIC-M4-PARITY (docs/02_roadmap/backlog.md)
predecessor: M3 Coding Pack #1 (docs/03_sprints/plans/m3-coding-pack.md) — gate G-M3 MUST be green first
timebox: 1 sprint × 8 working days (docs/02_roadmap/milestones.md)
branch: feat/mhf-m4-harness-parity
spec: docs/SPEC.md            # the ONLY normative document
plan: docs/TECH_LEAD_REVIEW/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md
last_reviewed: 2026-08-19
---

# Sprint board — M4: Harness Parity

**Sentence this sprint makes true:**

> Five harnesses and a second domain compile and run as manifests over a Layer 0 that received **zero
> diffs** all sprint — parity against the v0.4.5 baseline is proven on `zero_hint_v1` and the Tier-5
> Datalog frontier task under paired McNemar, the terminal's sub-second first-failure mandate is measured
> rather than asserted, and the TypeScript client typechecks against the same frozen contracts — so
> "adding pack #N costs no core change" is a falsified-or-standing claim, not a slogan.

**Staged, not active.** Activates only after gate **G-M3** is green
(`docs/03_sprints/plans/m3-coding-pack.md` §2).

## 0. Law

Invariants **I-1 … I-11** (`docs/SPEC.md` §Invariants), load-bearing this sprint:

- **I-7 (domain-blind core)** — M4 is the *generality falsification* milestone (`docs/SPEC.md` §6.4,
  handbook M11 merged per matrix §1.4): **acceptance is `git diff --stat layer0/` = 0 across the whole
  sprint.** A core diff needed to land a pack falsifies the architecture; it does not get waived.
- **I-8 (generated or normative, never both)** — the TypeScript client reads generated types only;
  a stale-codegen drift is a build failure (`docs/05_adr/ADR-M0-08` lineage, closes D-21 downstream).
- **I-1 (one `EffectRequest`)** — the same generated dataclass across five manifests, two domains, and
  both languages.
- **I-5 / I-9** — exterior signed verdicts and a schema-valid `mhf.trajectory/1` per episode, unchanged
  by pack count.
- **I-11 (sequential scheduler)** — latency work this sprint is *streaming and early classification*, not
  concurrency. D-38's measurement gate is not open; do not open it here.

**ADR bounds.** `docs/05_adr/ADR-M0-10` (no metaphysics) — the pack set is a capability matrix, not a tier
ladder. `docs/05_adr/ADR-M0-12` — parity harnesses are manifests over the same engine; a "shaped" pack never
becomes a second engine. `docs/05_adr/DEFERRED_REJECTED.md` bounds every measured deficit found here:
a parity gap becomes an ADR row with a reversal condition, never an unplanned Layer-0 patch.
Normative sources: `docs/SPEC.md` §4.3 (sub-second feedback mandate), §6.4 (domain-agnostic
decomposition / pack #N acceptance), §7 (trajectory + attribution telemetry).
Measurement discipline: `docs/04_annex/MEASUREMENT.md` — paired McNemar, A/A floor, preregistration before
any comparative run. Backlog row: **EPIC-M4-PARITY** (`docs/02_roadmap/backlog.md`), absorbing
`TSK-HAR-007` and `TSK-EPIC-060-004`.

## 1. Board

Lane A = Dev A (measurement, latency instrumentation, CI/freeze enforcement). Lane B = Dev B (manifest
recompilation, TableWorld pack, CLI client).

### Lane A — measurement, latency, freeze enforcement

- [ ] **S-M4-A-01** — **Layer-0 freeze gate**: CI job asserting `git diff --stat layer0/` is empty for
      every commit on the M4 branch relative to the `v0.5.0-m3` tag; a `handoff`-labelled exception
      requires an ADR with a reversal condition.
      *Verify:* `test -z "$(git diff --stat v0.5.0-m3..HEAD -- layer0/)"`

- [ ] **S-M4-A-02** — **Zero-hint parity**: `benchmarkings/zero_hint_v1` run as a 2×2 paired matrix,
      compiled packs vs. the v0.4.5 baseline, preregistered before execution; pass condition is
      **≥ baseline pass rate under paired McNemar** with the A/A floor respected
      (`docs/04_annex/MEASUREMENT.md`).
      *Verify:* `bash benchmarkings/zero_hint_v1/run_matrix_2x2.sh && python3 benchmarkings/zero_hint_v1/summarize_matrix.py`

- [ ] **S-M4-A-03** — **Tier-5 Datalog parity**: `benchmarkings/frontier_tier5_datalog_engine` run under
      the compiled `code-default` pack against the same baseline; incremental stratified fixed-point task
      is the frontier-difficulty witness. Leak lint stays armed — `datalog_solution` MUST NOT be reachable
      from the agent's workspace view (`tools/002_LLM_API_MOCK/verdict.py` `_LEAK_NAMES` semantics ported
      into the pack's anti-cheat lint).
      *Verify:* `python3 lab/bench.py --task frontier_tier5_datalog_engine --pack code-default --paired --against v0.4.5-baseline`

- [ ] **S-M4-A-04** — **Sub-second latency verification** (`docs/SPEC.md` §4.3): instrument the terminal
      toolkit's first-structured-failure path and assert the mandate as a *measured percentile*, not an
      anecdote — p95 from failure-line emission to planner-visible structured event **< 300 ms**, with the
      subprocess still running under its lease. Recorded per harness digest in telemetry (§7 attribution).
      *Verify:* `python3 -m unittest test.packs.code_default.test_terminal_latency` and
      `python3 tools/benchmark_vanguard_performance.py --report latency --p95-ms 300`

- [ ] **S-M4-A-05** — Per-harness attribution report: prefix-hit rate, escalation count, USD/episode and
      pass rate broken out **per harness digest** across the five packs — the artifact that makes "which
      shape wins" answerable and feeds M6 distillation.
      *Verify:* `python3 lab/diff.py --by harness_digest --packs all`

- [ ] **S-M4-A-06** — Disposition of every parity gap: each pack that lands below baseline gets an ADR row
      (cause, reversal condition) rather than a core patch. Zero gaps left undispositioned at gate.
      *Verify:* `python3 tools/check_markdown_links.py` (ADR cross-refs resolve)

### Lane B — five manifests, second domain, client

- [ ] **S-M4-B-01** — Recompile **`code-claude-shaped`** as `packs/code-claude-shaped/harness.yaml`
      (source: `vanguard/packages/agency/manifests/vg-code-claude-shaped/`); the legacy manifest directory
      is retired in the same commit.
      *Verify:* `python3 -m unittest test.packs.test_compile -k claude_shaped`

- [ ] **S-M4-B-02** — Recompile **`code-opencode-shaped`** (source: `manifests/vg-code-opencode-shaped/`).
      *Verify:* `python3 -m unittest test.packs.test_compile -k opencode_shaped`

- [ ] **S-M4-B-03** — Recompile **`code-swe-mini`** (source: `manifests/vg-code-swe-mini/`).
      *Verify:* `python3 -m unittest test.packs.test_compile -k swe_mini`

- [ ] **S-M4-B-04** — Land the fifth coding shape and **resolve the naming discrepancy**:
      `docs/02_roadmap/milestones.md` and `docs/SPEC.md` §8 name `code-pi-shaped`, but the tree carries
      `vanguard/packages/agency/manifests/vg-shell-only/`. Either recompile `vg-shell-only` as
      `packs/code-pi-shaped/` (if it is the same shape under an older name) or author the missing shape —
      and correct the roadmap row so the five-pack list is true in exactly one place.
      *Verify:* `python3 -m unittest test.packs.test_compile -k pi_shaped`

- [ ] **S-M4-B-05** — **TableWorld registered as Pack #2** (closes D-27): `packs/table-default/` from
      `manifests/vg-table-default/` + `vanguard/packages/adapters/environment/tableworld.py`, with its own
      toolkit, oracle suite and selector vocabulary. This is the **generality witness** — a second domain
      landing with zero Layer-0 diff is what S-M4-A-01 is measuring.
      *Verify:* `python3 -m unittest test.packs.test_compile -k table_default`

- [ ] **S-M4-B-06** — All five packs **run**, not merely compile: one full episode each through the
      registry with zero hardcoded imports, each producing a schema-valid `mhf.trajectory/1`.
      *Verify:* `python3 -m unittest discover -s test/packs -t .`

- [ ] **S-M4-B-07** — **CLI TypeScript check**: `vanguard/clients/cli` typechecks and its tests pass
      against the regenerated types; the TS readers emitted by `tools/codegen/` are current (stale
      codegen = build failure, I-8). The client selects a pack by manifest name — no per-pack client code.
      *Verify:* `npm run typecheck -w @vanguard/cli && npm test -w @vanguard/cli`

## 2. Verification (gate G-M4 — every command MUST exit 0)

```bash
# The M4 acceptance condition: Layer 0 received zero diffs all sprint (I-7 / SPEC §6.4)
test -z "$(git diff --stat v0.5.0-m3..HEAD -- layer0/)"
grep -rE "coding|pytest|ast" layer0/ ; test $? -eq 1

# Five packs + TableWorld compile and run
python3 -m unittest discover -s test/packs -t .
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py
python3 tools/check_isolation_policy.py

# Carried M1–M3 gates stay green at five packs
python3 tools/check_event_coverage.py                 # E-COV = 100%
python3 -m unittest test.layer0.replay.test_parity    # replay-parity

# Parity measurement (preregister BEFORE running — docs/04_annex/MEASUREMENT.md)
bash benchmarkings/zero_hint_v1/run_matrix_2x2.sh
python3 benchmarkings/zero_hint_v1/summarize_matrix.py
python3 lab/bench.py --task frontier_tier5_datalog_engine --pack code-default --paired --against v0.4.5-baseline
python3 lab/diff.py --by harness_digest --packs all

# Sub-second first-failure mandate (SPEC §4.3), measured as p95
python3 -m unittest test.packs.code_default.test_terminal_latency
python3 tools/benchmark_vanguard_performance.py --report latency --p95-ms 300

# TypeScript client against generated contracts
npm run typecheck -w @vanguard/cli
npm test -w @vanguard/cli

# Docs hygiene
python3 tools/check_markdown_links.py
python3 tools/check_stale_paths.py
```

Tag on green: `v0.5.0-m4` — this closes **v0.5.0 = MHF v1**. Next: M5/M6 are v0.6.x and gated on the
200-task statistical-power suite (`docs/02_roadmap/milestones.md`); they do not start on this board.

## 3. Explicitly not this sprint

Any Layer-0 diff whatsoever — that is the gate, not a constraint to negotiate · new SPIs or SPI method
changes · scheduler concurrency or async effects (I-11 / D-38 remains closed; a latency deficit is
dispositioned as an ADR row, never as a concurrency patch) · the 200-task suite build-out and any
statistical-power work for M5 · meta-reflector, genome mutation + lab selection, calibrated escalation,
skill harvest (**M5**, `docs/SPEC.md` §5) · memory graph, market/Vickrey allocator, multi-agent economic
delegation (**M6 / Phase-3**, `docs/SPEC.md` §6) · DPO fine-tuning runs (**M6**; M4 only proves the
trajectory rows are schema-valid) · a third domain pack beyond TableWorld · GUI/IDE clients · anything in
`docs/05_adr/DEFERRED_REJECTED.md` or the honour table (`docs/SPEC.md` §9).

---

*Predecessor board: M3 (`docs/03_sprints/plans/m3-coding-pack.md`, gate G-M3). This is the final v0.5.0
board; M5/M6 are v0.6.x (`docs/02_roadmap/milestones.md`).*
