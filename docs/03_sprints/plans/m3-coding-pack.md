---
id: SPRINT-M3-CODING-PACK
file: docs/03_sprints/plans/m3-coding-pack.md
title: "Staged plan — v0.5.0 MHF M3: Coding Pack #1 (re-extraction into packs/code-default/)"
status: STAGED
milestone: M3 (of M0–M6, docs/SPEC.md §8) — EPIC-M3-PACK
epic: EPIC-M3-PACK (docs/02_roadmap/backlog.md)
predecessor: M2 Plugin Runtime (docs/03_sprints/plans/m1-m2-lanes.md §3) — gate G-M2 MUST be green first
timebox: 2–3 sprints × 8 working days (docs/02_roadmap/milestones.md)
branch: feat/mhf-m3-coding-pack
spec: docs/SPEC.md            # the ONLY normative document
plan: docs/TECH_LEAD_REVIEW/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md
last_reviewed: 2026-08-19
---

# Sprint board — M3: Coding Pack #1

**Sentence this sprint makes true:**

> The coding domain lives entirely in `packs/code-default/` as manifest-declared plugins — ast-patch,
> repo-map, terminal, and the single planner are re-extracted out of `vanguard/packages/apps/coding/`
> and its adapters, `compose()` compiles and *runs* the pack end-to-end, and `grep -rE "coding|pytest|ast"
> layer0/` returns nothing — so the domain-blind-core claim (I-7) is true by measurement, not by intent.

**Staged, not active.** This board activates only after joint gate **G-M2** is green
(`docs/03_sprints/plans/m1-m2-lanes.md` §3): registry, lifecycle FSM, isolation broker, SPI v1 and
`compose()` v2 must exist before any `apps/coding` file moves — the "honest ledger before extraction"
rule at its stronger fixpoint (execution plan §3, joint gate G-M2).

## 0. Law

Invariants **I-1 … I-11** (`docs/SPEC.md` §Invariants), load-bearing this sprint:

- **I-7 (domain-blind core)** — the sprint's defining constraint: `grep -rE "coding|pytest|ast" layer0/`
  MUST return nothing. Every task below is a *plugin* task; Layer-0 diff for M3 is zero.
- **I-6 (plugins untrusted by default)** — `proc.exec`-capable toolkits (terminal) MUST declare
  `container`/`subprocess` isolation in their plugin manifest; `in_process` is a policy grant, never a
  default.
- **I-5 (exterior judge)** — the pack's oracle suites are preregistered and verdicts signed by the
  evaluator; the planner never grades its own work (`docs/SPEC.md` §4.4).
- **I-1 (one `EffectRequest`)** — toolkits consume the generated type only; no pack-local re-declaration.
- **I-9 (telemetry is a dataset)** — every pack episode still terminates in a valid `mhf.trajectory/1`.
- **I-2 / I-4** — E-COV stays 100% and `replay-parity` stays green with pack plugins live.

**ADR bounds.** `docs/05_adr/ADR-M0-12` (a tool is not an episode) bounds §4.4's planner: the drive-until-green
loop is an `IPlanner` plugin at a scheduler slot, **not** a second engine — no `MetaLoopEngine`
reincarnation (honour table, `docs/SPEC.md` §9; `TSK-CORE-011`). `docs/05_adr/ADR-M0-13` (walking skeleton)
is the precedent this pack generalises: discovery → resolution → activation with zero hardcoded imports.
`docs/05_adr/ADR-M0-03` (five SPIs) fixes the interfaces these plugins implement — M3 adds no SPI.
Normative source: `docs/SPEC.md` §4 (§4.1 ast-patch, §4.2 index + repo-map, §4.3 terminal, §4.4 planner)
and §7 (trajectory record). Measurement discipline: `docs/04_annex/MEASUREMENT.md` (paired McNemar, A/A
floor, preregistration). Backlog row: **EPIC-M3-PACK** (`docs/02_roadmap/backlog.md`), absorbing
`TSK-EPIC-060-001/002/003`, `TSK-EPIC-070-001`, `TSK-HAR-001…006`, `TSK-CTX-003/004`, `H-2`, `RT-01`.

## 1. Board

Lane A = Dev A (pack skeleton, CI/I-7 enforcement, oracles & measurement). Lane B = Dev B (the four
toolkit/planner extractions). Ownership follows the global map in
`docs/TECH_LEAD_REVIEW/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md` §0, extended: `packs/**` is **B**,
`lab/**` + `tools/check_*` + `.github/workflows/**` are **A**, `docs/**` is joint-`handoff`.

### Lane A — pack frame, gates, measurement

- [ ] **S-M3-A-01** — Land the pack skeleton and its manifest:
      `packs/code-default/harness.yaml` (promoted from the M0 draft), `packs/code-default/plugin.yaml`
      per plugin, `packs/code-default/oracles/`. Ports `vanguard/packages/agency/manifests/vg-code-default/`
      to manifest form; the old manifest directory is retired in the same commit, not duplicated.
      *Verify:* `python3 -m unittest discover -s test/packs -t .`

- [ ] **S-M3-A-02** — **I-7 CI gate**: add `tools/check_domain_blindness.py` to
      `.github/workflows/ci.yml`, hard-fail, plus a deliberately-broken fixture proving it fails.
      *Verify:* `grep -rE "coding|pytest|ast" layer0/ ; test $? -eq 1`

- [ ] **S-M3-A-03** — Isolation-tier policy gate: `container` (or `subprocess`) mandatory for any plugin
      declaring a `proc.exec` capability; `packs/code-default/plugin.yaml` for the terminal toolkit
      complies. Closes the I-6 half of the pack. *Verify:* `python3 tools/check_isolation_policy.py`

- [ ] **S-M3-A-04** — Retire the second budget controller (D-43): `apps/coding/coding_budget.py`'s
      pre-call worst-case USD reservation is expressed as a six-dim `Reservation` through the kernel
      `Governor`; no pack-local budget arithmetic survives.
      *Verify:* `grep -rn "class .*Budget" packs/ ; test $? -eq 1`

- [ ] **S-M3-A-05** — Oracle suites + preregistration: port `apps/coding/coding_verification.py` oracle
      semantics into `packs/code-default/oracles/`, preregistered with the exterior evaluator, verdicts
      signed. Anti-cheat lint (`test_anticheat.py` semantics) runs against the pack.
      *Verify:* `python3 -m unittest test.packs.test_oracles`

- [ ] **S-M3-A-06** — **Phase-1 acceptance measurement** (`docs/SPEC.md` §4 gate): compiled
      `code-default` vs. the v0.4.5 baseline on the `lab/` dogfood triple + `benchmarkings/zero_hint_v1`,
      paired McNemar per `docs/04_annex/MEASUREMENT.md`, A/A floor respected, preregistered before the run.
      *Verify:* `python3 lab/bench.py --pack code-default --paired --against v0.4.5-baseline`

- [ ] **S-M3-A-07** — **Un-mocked greenfield proof**: ≥1 greenfield task solved end-to-end by the
      compiled pack against a **live** model with a signed `oracle_green` verdict (carries G-050-06
      verbatim). Cassette runs do not satisfy this row.
      *Verify:* `python3 tools/run_v0450_greenfield_campaign.py --pack code-default --live`

- [ ] **S-M3-A-08** — Replay/E-COV regression with the pack live: `replay-parity` green over a pack
      episode; E-COV stays 100% with pack plugin kinds emitting.
      *Verify:* `python3 tools/check_event_coverage.py && python3 -m unittest test.layer0.replay.test_parity`

### Lane B — the four re-extractions

Each row moves logic **out of** `vanguard/packages/` **into** `packs/code-default/`; the source module is
deleted (not left as a shim) in the same PR, and the plugin imports `layer0/spi` + generated types only.

- [ ] **S-M3-B-01** — `packs/code-default/toolkits/ast_patch.py` (`mhf.toolkit.ast-patch`,
      `docs/SPEC.md` §4.1). Sources: patch/diff application in
      `vanguard/packages/adapters/environment/git.py` + `apps/coding/coding_plan.py` edit paths.
      Anchored edits `(node_kind, qualified_name, content_digest_of_anchor) → replacement`, fallback
      ladder search/replace → unified diff negotiated via `IModelProvider.capabilities()`; every applied
      patch emits an **AST-level structural diff** into the receipt (symbol added/removed/signature-changed),
      raw text diff carried as a blob ref.
      *Verify:* `python3 -m unittest test.packs.code_default.test_ast_patch`

- [ ] **S-M3-B-02** — `packs/code-default/toolkits/repo_map.py` (`mhf.toolkit.index` +
      `mhf.context.repo-map`, `docs/SPEC.md` §4.2). Sources:
      `vanguard/packages/adapters/stores/repo_index.py` (`FileRepoIndex`, symbol extraction) +
      `vanguard/packages/agency/context/` repo-map layer. Merkle tree over the workspace with
      dirty-subtree invalidation, tag extraction (defs/refs), import/reference-graph ranking rendered
      into a token-budgeted L4 map. **Index updates are receipt-driven — never a hot-path scan.**
      *Verify:* `python3 -m unittest test.packs.code_default.test_repo_map`

- [ ] **S-M3-B-03** — `packs/code-default/toolkits/terminal_runner.py` (`mhf.toolkit.terminal`,
      `docs/SPEC.md` §4.3). Sources: `vanguard/packages/adapters/sandbox/{toolkit,rootless,worker}.py`.
      PTY-backed persistent shell per workspace cell; incremental output streaming with
      **early classification** — pytest/ruff output parsed into structured events at *first failure*,
      not at process exit, while the process still runs under its lease. `dogfood-02` timeout/censoring
      semantics preserved as contract tests. Declares `proc.exec` ⇒ `container` tier (S-M3-A-03).
      *Verify:* `python3 -m unittest test.packs.code_default.test_terminal_runner`

- [ ] **S-M3-B-04** — `packs/code-default/planners/single_planner.py`
      (`mhf.planner.drive-until-green`, `docs/SPEC.md` §4.4). Sources:
      `vanguard/packages/runtime/tier_escalation.py` (the D-41 salvage),
      `vanguard/packages/adapters/models/{planner,routing}.py` (`DefaultPlannerAdapter`, single router),
      `apps/coding/coding_coordinator.py` + `coding_progress.py`. plan → patch → verify loop; model-tier
      escalation Free→Cheap→Frontier on `verdict_fail` while budget holds; repair rounds bounded by
      **manifest config**, not code constants (H-2). Verification is `IEvaluationGate` only.
      *Verify:* `python3 -m unittest test.packs.code_default.test_single_planner`

- [ ] **S-M3-B-05** — Retire `vanguard/packages/apps/coding/` and `runtime/coding_*`: the composition
      root no longer imports coding anything; `domain/ledger/coding_session.py` is generalised to a
      domain-tagged `SessionProjection` (closes D-42/D-43 residue).
      *Verify:* `grep -rn "apps.coding\|coding_" vanguard/packages/runtime/ ; test $? -eq 1`

- [ ] **S-M3-B-06** — Context-policy wiring (H-2, `TSK-CTX-003/004`): compaction strategy and repo-map
      token budget selected from `harness.yaml` config; prefix-freeze property preserved across the pack's
      L1–L3. *Verify:* `python3 -m unittest test.packs.code_default.test_context_policy`

- [ ] **S-M3-B-07** — **Pack walking skeleton**: `compose()` compiles `packs/code-default/harness.yaml`
      and runs one full episode with **zero hardcoded imports** — every toolkit and the planner arrive
      through registry discovery.
      *Verify:* `grep -rn "import.*ast_patch\|import.*terminal_runner" layer0/ vanguard/packages/runtime/ ; test $? -eq 1`

## 2. Verification (gate G-M3 — every command MUST exit 0)

```bash
# I-7: the core is domain-blind (inverted grep — no matches is the pass condition)
grep -rE "coding|pytest|ast" layer0/ ; test $? -eq 1

# Layer-0 is untouched by M3
test -z "$(git diff --stat "$(git merge-base HEAD main)"..HEAD -- layer0/)"

# Pack suite, boundaries, TCB budget
python3 -m unittest discover -s test/packs -t .
python3 tools/check_boundaries.py
python3 tools/check_tcb_budget.py

# Carried M1/M2 gates stay green with the pack live
python3 tools/check_event_coverage.py          # E-COV = 100%
python3 -m unittest test.layer0.replay.test_parity   # replay-parity
python3 tools/check_isolation_policy.py        # container tier for proc.exec toolkits

# Phase-1 acceptance (docs/SPEC.md §4) — preregister BEFORE running
python3 lab/bench.py --pack code-default --paired --against v0.4.5-baseline
bash benchmarkings/zero_hint_v1/run_matrix_2x2.sh
python3 benchmarkings/zero_hint_v1/summarize_matrix.py
python3 tools/run_dogfood_r9.py
python3 tools/run_v0450_greenfield_campaign.py --pack code-default --live

# Docs hygiene
python3 tools/check_markdown_links.py
python3 tools/check_stale_paths.py
```

Tag on green: `v0.5.0-m3`. Next board: `docs/03_sprints/plans/m4-harness-parity.md`.

## 3. Explicitly not this sprint

Layer-0 changes of any kind (kernel, events, scheduler, SPI — the SPI set is frozen at
`docs/05_adr/ADR-M0-03`) · new SPIs or SPI method additions · the four remaining packs and TableWorld
registration (**M4**, `docs/03_sprints/plans/m4-harness-parity.md`) · concurrency in the scheduler
(I-11: Phase-1 is sequential; D-38 gate not open) · meta-reflector / outer loop, genome mutation, skill
harvest, calibrated escalation (**M5 / Phase-2**, `docs/SPEC.md` §5) · memory graph, market allocator,
multi-agent delegation (**M6 / Phase-3**, `docs/SPEC.md` §6) · DPO harvest pipeline beyond emitting a
schema-valid trajectory (`docs/SPEC.md` §7 offline half) · embedding sidecar for the index (§4.2 declares
it optional — not built here) · anything in `docs/05_adr/DEFERRED_REJECTED.md` · the honour table's standing
refusals (`docs/SPEC.md` §9): no `MetaLoopEngine`, measurement stays outside `vanguard/packages/`,
`strict` playbook DAG execution.

---

*Predecessor board: M2 (`docs/03_sprints/plans/m1-m2-lanes.md` §3, gate G-M2). Successor board: M4
(`docs/03_sprints/plans/m4-harness-parity.md`).*
