# 03 — SPRINTS PARALLEL EXECUTION PLAN: M0 → M1 → M2, Two Engineers, Zero Merge Conflicts

**Authority:** SPEC (MHF v1) + deliverables 01/02. Cadence: 5 sprints × 8 working days (M0 = 1, M1 = 2, M2 = 2).
**Engineers:** **Dev A — Core, Event-Sourcing & CI** · **Dev B — SPIs, Plugin Lifecycle & Coding-Pack Prep**.

---

## 0. Conflict-freedom model (read before assigning anything)

Zero merge conflicts is achieved **structurally**, not by coordination effort:

1. **Directory ownership is exclusive and CI-enforced.** A `CODEOWNERS`-style map (below) is checked by a CI job (`check_lane_ownership.py`, trivially adapted from `check_boundaries.py`): a PR touching a path outside its author's lane fails unless labelled `handoff` and approved by the other dev. No shared files, ever — shared *concepts* cross through generated artifacts and frozen interfaces.
2. **The contract-first waist.** Dev A owns `schemas/mhf/*.json` and the codegen tool; Dev B owns everything that *imports* the generated `layer0/spi/types_gen.py`. B never edits schemas; A never edits SPI protocol classes. Schema changes are proposed as PRs to A with B as reviewer (the reverse of code review — the consumer reviews the producer).
3. **Two interface-freeze checkpoints.** IF-1 (end of Sprint 2 / M1.1): `EffectRequest`, `Receipt`, `Proposal`, `Reservation`, envelope schema frozen — B builds SPIs against them. IF-2 (Sprint 3 day 3): `KernelFacade` + `SchedulerHooks` constructor signatures frozen — B builds `compose()` against them. Post-freeze changes require a joint half-day RFC.
4. **The kernel is read-only for both** after its verbatim port lands (Sprint 2, Dev A). Amendments go through `handoff` PRs with both approvals — the TCB discipline survives the rewrite.

### Global ownership map (all sprints)

| Path | Owner | Notes |
|---|---|---|
| `schemas/mhf/**`, `tools/codegen/**` | **A** | single source of truth; B reviews |
| `layer0/events/**`, `layer0/kernel/**`, `layer0/scheduler/**` | **A** | kernel read-only after port |
| `layer0/spi/**` (protocols), `layer0/registry/**`, `layer0/compose/**` | **B** | imports `types_gen` only |
| `plugins/**`, `packs/**` | **B** | |
| `test/layer0/{events,kernel,scheduler,replay}/**` | **A** | |
| `test/layer0/{spi,registry,compose}/**`, `test/plugins/**` | **B** | |
| `.github/workflows/**`, `tools/check_*`, `tools/telemetry/**`, `lab/**` | **A** | |
| `docs/05_adr/**`, `docs/04_annex/**`, `docs/SPEC.md` | **A** (M0), then joint-`handoff` | |
| `docs/03_sprints/sprint_active.md` | joint | edited at sprint boundaries only |
| deletions/history rewrite (M0) | **A** executes; B signs the manifest | one force-push window |

---

## 1. SPRINT 1 — **M0: Excise & Sanitize** (8 days)

Dev B does not idle on deletion work: B front-loads M2 design (schemas review, SPI drafts on paper, plugin.yaml schema) and executes the *code-side* purge in his future lanes.

### Dev A — atomic tasks

| ID | Task | Acceptance criterion (command / proof) |
|---|---|---|
| S-M0-A-01 | Land `docs/05_adr/` : migrate VG-09 + VG-10 corpus, mint ADR-M0-01…13 per migration matrix | files exist; append-only CI rule active; each ADR names a reversal condition (or explicit "none") |
| S-M0-A-02 | Land `docs/04_annex/KERNEL.md` (VG-05 + K-40/F-21a/SA-strike amendments) and `annex/MEASUREMENT.md` (VG-07 §5) | matrix rows 1.8/1.10 checklist signed by B |
| S-M0-A-03 | Apply MERGE rows into `docs/SPEC.md` (matrix §§1.4–1.7, 1.9–1.10) | reviewer sign-off per row; RFC-2119 grep gate green |
| S-M0-A-04 | Delete: `docs/01_specs/{backend,frontend}`, `docs/00_executive`, root THEORY/ASBUILT, generated rule files, `docs/scrum/**` (evidence → blob store manifest) | `find docs -name '*.md' \| wc -l` ≤ 30; `check_markdown_links.py` green |
| S-M0-A-05 | **History rewrite** (single `git filter-repo` pass): SEC-01 `.env` blob, `lam.sqlite`, `tools/001_*/outputs/`, `runs/**`, sprint-evidence JSONL, `vanguard-gui/`, `vanguard-ide/`, `benchmark_results.json` | `python3 tools/scan_secrets.py --all-refs` PASS; `git count-objects -vH` ≤ 3 MB pack; purge manifest committed and co-signed by B |
| S-M0-A-06 | CI reset: drop TCB-LOC badge + test-count badge; add RFC-2119 gate, docs-size gate, `check_lane_ownership.py` | pipeline green on rewritten `main` |
| S-M0-A-07 | Rewrite `docs/02_roadmap/{backlog,milestones}.md` per deliverable 02; close legacy TSK rows with `superseded_by` | grep: zero open `TSK-FE-*`; every closed row carries a successor id |

### Dev B — atomic tasks

| ID | Task | Acceptance criterion |
|---|---|---|
| S-M0-B-01 | Scaffold monorepo v-next skeleton: `layer0/{events,kernel,spi,registry,scheduler,compose}/`, `plugins/`, `packs/`, `test/layer0/` with `__init__` stubs + lane ownership file | `check_lane_ownership.py` recognises all paths; empty-package import test green |
| S-M0-B-02 | Author `schemas/mhf/plugin.schema.json` (SPEC §2.1: provides/requires, spi_version ranges, isolation enum, capability ceiling, entry, signature) + 6 golden vectors (valid/invalid) | vectors validate; invalid vectors fail with expected error paths |
| S-M0-B-03 | Author `schemas/mhf/harness.schema.json` (SPEC §2.3) + port `vg-code-default` pack to a draft `packs/code-default/harness.yaml` (non-executing) | schema-validates; digest computed via existing JCS |
| S-M0-B-04 | **SPI RFC** — one document freezing method sets for the 5 SPIs + `IModelProvider`/`ISandbox`/stores, capability-negotiation vocabulary, error taxonomy (`instrument_error` carried) | reviewed + signed by A; becomes the IF-1 checklist |
| S-M0-B-05 | Migrate pytest: `unittest discover` → `pytest` config for the retained suite; mark tests bound for deletion vs port | `pytest -q` green on retained set; port-map committed |
| S-M0-B-06 | Blob-store evidence relocation tool: move purged sprint evidence/run artifacts into digest-keyed local store with an index manifest | round-trip: `fetch(digest)` returns byte-identical artifact for 3 samples |

**Joint gate G-M0 (day 8):** all A+B criteria green; team re-clone completed after force-push; tag `v0.5.0-m0`.

---

## 2. SPRINTS 2–3 — **M1: Layer-0 Microkernel** (2 × 8 days)

### Dev A — atomic tasks

| ID | Sprint | Task | Acceptance criterion |
|---|---|---|---|
| S-M1-A-01 | 2 | **Codegen**: `tools/codegen/` emits frozen dataclasses (`layer0/spi/types_gen.py`) + TS readers from `schemas/mhf/*.json`; wire into CI (generated files are build artifacts, never hand-edited) | CI fails on stale gen; `EffectRequest` exists exactly once in the tree (`grep -rn "class EffectRequest" \| wc -l` = 1) — closes D-21 |
| S-M1-A-02 | 2 | **Kernel port (verbatim)**: `kernel/{dispatch,attenuation,budget,grants,classifier,policy,provenance,model}.py` → `layer0/kernel/`, retargeted to `types_gen`; six-dim `Reservation` `{usd_micros,millis,tokens,bytes,turns,depth}` | full `test/kernel` port green; S0–S12 ordering tests (K-04…K-47) pass unmodified in semantics; ADR-M0-07 cited in diff |
| S-M1-A-03 | 2 | **Event layer**: envelope (JCS + `prev_digest` chain + `seq` + `causation/correlation` + `branch_id` + idempotency key), full 30+ kind taxonomy per SPEC §1.2, SQLite-WAL store port, blob `write→fsync→emit(digest)` ordering | golden envelope vectors; chain-verification property test; D-19 atomicity test (kill between blob write and emit → recovery consistent) |
| S-M1-A-04 | 2 | **IF-1 freeze** (day 8): `EffectRequest`, `Proposal`, `Receipt`, `Reservation`, envelope schemas tagged `spi-v1.0-frozen` | tag exists; B countersigns |
| S-M1-A-05 | 3 | **Emitter completeness**: every kind wired to its single production emitter (lifecycle→scheduler; auth/budget/effects→kernel S5–S12; approvals→ledgered service; plugins→registry hooks *stubbed to interface*; heartbeat HMAC) | **E-COV job = 100%**: static walk proves reachable emitter per declared kind; `KernelAlarm` fires on F-21a and F-24 |
| S-M1-A-06 | 3 | **Scheduler v1**: sequential turn driver over kernel dispatch (EpisodeEngine discipline preserved: engine-refusal path now emits `AuthorizationDenied` — D-08 closed structurally), turn/depth enforced via `Reservation`, cancellation token, heartbeat loop, `spawn` mechanism with provenance-carrying `ChildSpawned/Returned` | scheduler contract tests; depth-1 child run round-trips spans (G-050-02 re-proven); turn-ceiling exhaustion emits `BudgetExhausted` |
| S-M1-A-07 | 3 | **Trajectory record + M-18**: emit `mhf.trajectory/1` at `EpisodeCompleted`; wire instrument tuple + prefix attribution from `tools/telemetry/` | fixture episode produces schema-valid trajectory; tuple fields populated |
| S-M1-A-08 | 3 | **CI battery**: `replay-parity` (live fixture run → cold fold → structural diff of grants tree, budget vector, approval log, episode FSM), branch-resume test (fold to seq=N + divergent `branch_id`), crash-recovery test (`EffectStarted` orphan → reconcile → `RunRecovered`), mutation testing (`mutmut`/`cosmic-ray`) on `layer0/{kernel,events}`, retarget `rule_test_map.py` to invariants I-1…I-10 | **replay-parity green**; mutation score ≥ 80%; I-map bijection complete |

### Dev B — atomic tasks

| ID | Sprint | Task | Acceptance criterion |
|---|---|---|---|
| S-M1-B-01 | 2 | **SPI protocols v1** (`layer0/spi/`): `IPlanner`, `IMemoryEngine`, `IToolkit`, `IContextManager`, `IEvaluationGate`, `IModelProvider`, `ISandbox`, store ports — per signed RFC, importing `types_gen` only | mypy `--strict` green; zero `Mapping[str, Any]` in `layer0/spi/` (grep gate — kills AP-3); `spi_version` on every protocol |
| S-M1-B-02 | 2 | **Deterministic fakes + shared contract suites** per SPI (the activation-bundle rule I-3, operationalised): fake planner (scripted), fake toolkit (echo), fake memory (dict), fake context (identity), fake gate (fixed verdict) — no ambient I/O/clock/randomness | one behavioural contract suite per SPI runs against its fake; typed-failure behaviour covered |
| S-M1-B-03 | 2 | **Context compiler port**: `agency/context/{compiler,compaction,layers}.py` → `plugins/mhf_context_baseline/` as the first `IContextManager` impl (prefix-freeze property preserved); `reground()` implemented (D-10 closed by contract) | prefix-stability property test (byte-identical L1–L3 across calls); compaction strategy selected from *config*, honouring H-2 pattern |
| S-M1-B-04 | 2 | **Evaluator gateway design + port prep**: daemon/signing/isolated evaluators port plan; `IEvaluationGate` baseline impl emitting `EvaluationRequested` through the event store (D-02 fix consumed from A's taxonomy) | design signed; gate fake passes contract suite |
| S-M1-B-05 | 3 | **Model-provider plugins v0**: cassette + fake providers behind `IModelProvider` with the 4-protocol codec skeleton (OpenAI-Completions/Responses, Anthropic-Messages, Google-GenAI) — transport codecs stubbed, message shape real | cassette provider replays a recorded episode deterministically end-to-end against A's scheduler (first integration proof, uses fakes elsewhere) |
| S-M1-B-06 | 3 | **`compose()` v2 skeleton**: manifest → resolved refs → capability-ceiling intersection → `FrozenHarness` digest (JCS over manifest + plugin digests); fail-fast on unknown ref/alias (H-1) | compose golden tests: identical inputs ⇒ identical digest; unknown alias fails at compose with named path |
| S-M1-B-07 | 3 | **End-to-end walking skeleton α** (ADR-M0-13): scripted-planner + echo-toolkit + cassette-model harness runs one full episode through A's scheduler+kernel+ledger | trajectory record produced; `replay-parity` passes on this run (joint fixture for S-M1-A-08) |

**Joint gate G-M1 (Sprint 3, day 8):** E-COV 100% · replay-parity green (incl. walking-skeleton fixture) · mutation ≥ 80% · one `EffectRequest` · zero type-erasure in SPI · tag `v0.5.0-m1`.

---

## 3. SPRINTS 4–5 — **M2: Plugin Runtime** (2 × 8 days)

### Dev A — atomic tasks

| ID | Sprint | Task | Acceptance criterion |
|---|---|---|---|
| S-M2-A-01 | 4 | **Registry event integration**: `PluginResolved/Activated/Quiesced/Retired/Faulted` emitters wired to B's FSM hooks (interface frozen at IF-2, day 3) | E-COV stays 100% with plugin kinds live; ledger shows full lifecycle for echo plugin |
| S-M2-A-02 | 4 | **Subprocess isolation substrate**: fork-per-plugin runner, JSON-RPC over UDS, enforced `setrlimit` pre-exec, seccomp allowlist profiles per verb class, no-new-privs (closes D-31/TSK-SEC-002) | `test/security` battery: rlimit breach kills cell + `PluginFaulted`; forbidden syscall (e.g. `connect` under fs-only profile) denied; escape attempts from the existing security suite ported and green |
| S-M2-A-03 | 4 | **AT-12 decision** (TSK-SEC-001): implement capability↛verifier path proof (static reachability: no plugin cell holds evaluator UDS path/keys) **or** ADR-defer with compensating control | either the check exists in CI or ADR lands with B's counter-signature |
| S-M2-A-04 | 5 | **Hot-swap attribution**: routing-flip event records exact turn seq; harness digest recomputed; replay across a swap reconstructs both epochs | swap-mid-run fixture: fold reproduces pre/post-swap routing; lab attribution shows two harness digests |
| S-M2-A-05 | 5 | **CI extensions**: lane-ownership on `plugins/`, plugin-manifest schema gate, isolation-tier policy gate (`container` mandatory for `proc.exec`-capable toolkits), I-7 domain-blindness grep (`grep -rE "coding\|pytest\|ast" layer0/` empty) | all gates in pipeline; deliberately-broken fixtures fail correctly |
| S-M2-A-06 | 5 | **Crash-loop & recovery semantics**: registry backoff policy, `FAULTED→fallback` substitute routing, scheduler drain on `QUIESCING` | kill -9 a plugin cell mid-effect → effect *undeterminable* → reconciled; fallback plugin serves next turn; full trail in ledger |

### Dev B — atomic tasks

| ID | Sprint | Task | Acceptance criterion |
|---|---|---|---|
| S-M2-B-01 | 4 | **Registry + lifecycle FSM**: scan paths + entry-point discovery, semver + `spi_version` range resolution (topological over `requires`), signature verification hook, capability-ceiling policy check, FSM `DISCOVERED→…→RETIRED` with A's event hooks | resolver property tests (version conflicts, cycles, missing deps → typed errors at RESOLVED, never at runtime); FSM transition table = tests bijection |
| S-M2-B-02 | 4 | **Isolation broker client side**: plugin-cell protocol (init/call/health/quiesce), `in_process` tier with import-lint (static: plugin imports `spi`+`events` only), tier selection from manifest | echo plugin runs identically under `in_process` and `subprocess`; import-lint catches a planted violation |
| S-M2-B-03 | 4 | **Walking skeleton β through the registry** (ADR-M0-13 completed): echo plugin discovered from `plugins/`, resolved, verified, activated, executes one episode, quiesced, retired — zero hardcoded imports | `grep -rn "import.*echo" layer0/` empty; full run driven by `harness.yaml` alone |
| S-M2-B-04 | 5 | **`mhf.model.local-adapter`** (the M2 demo payload, from `002_doing`): middleware chain — think-tag stripper, `MultiActionUnpacker` (provider-side decomposition into sequential single-effect proposals; kernel one-effect law untouched), token/time budget middleware; runs `subprocess` tier against live Ollama when available, cassette otherwise | contract suite green under both tiers; multi-action cassette from a recorded `deepseek-r1` reply decomposes into N sequential proposals with correct ordering; kernel sees one effect per turn |
| S-M2-B-05 | 5 | **`compose()` v2 completion**: full harness compile — plugin resolution + grant-ceiling intersection + L1–L3 freeze + digest; `packs/code-default/harness.yaml` compiles (does not yet fully execute — toolkits arrive in M3) | compose of code-default succeeds; ceiling-violation fixture (plugin requesting `proc.exec` beyond pack grant) fails at VERIFIED with named capability |
| S-M2-B-06 | 5 | **Evaluator gateway live**: port daemon/signing adapters; `IEvaluationGate` baseline requests via ledger, verdicts land as signed `VerdictRecorded`; unreadability probe ported | kill session process after episode → ledger watcher still produces `EvaluationRequested` (G-050-05 re-proven, stronger); plugin cells demonstrably cannot reach signing keys (feeds S-M2-A-03) |

**Joint gate G-M2 (Sprint 5, day 8):** echo plugin full-lifecycle with ledger trail · fault-injection + fallback proven · hot-swap with attribution · compose fail-fast (H-1) · local-adapter demo under subprocess isolation · seccomp/rlimits enforced · tag `v0.5.0-m2`. **M3 (Coding Pack) is unblocked** — and only now do `apps/coding` files move, satisfying the old board's "honest ledger before extraction" rule at the stronger fixpoint.

---

## 4. Drop-in replacement — `docs/03_sprints/sprint_active.md`

```markdown
---
id: SPRINT-M0-ACTIVE
file: docs/03_sprints/sprint_active.md
title: "Active sprint — v0.5.0 MHF M0: Excise & Sanitize"
status: ACTIVE
milestone: M0 (of M0–M6, SPEC §8)
predecessor: v0.4.5-beta board (v0.6.0 'Molecular Lattice' — SUPERSEDED, see docs/05_adr/ + 02_ROADMAP §1)
timebox: 8 working days
branch: feat/mhf-m0-excise
spec: docs/SPEC.md            # the ONLY normative document
plan: docs/03_sprints/plans/03_SPRINTS_PARALLEL_EXECUTION_PLAN.md
last_reviewed: 2026-08-18
---

# Sprint board — M0: Excise & Sanitize

**Sentence this sprint makes true:**
> One normative spec + ADR log remain; secrets and artifacts are purged from all reachable
> history; the frontend trees are gone; the v-next skeleton, plugin/harness schemas, and the
> SPI RFC exist — so M1 can start on a clean, ≤3 MB repository.

## 0. Law
Invariants I-1…I-10 (SPEC §preamble). Kernel semantics untouched this sprint. No new features.
Legacy TSK rows are closed only with `superseded_by:` pointers (02_ROADMAP §4).

## 1. Lanes (zero file overlap — enforced by tools/check_lane_ownership.py)

| Lane | Owner | Writes | Does not touch |
|---|---|---|---|
| **A — Docs, Purge & CI** | Dev A | docs/05_adr/** · docs/04_annex/** · docs/SPEC.md · docs/02_roadmap/** · deletions & history rewrite · .github/workflows/** · tools/check_* | layer0/** · plugins/** · packs/** · schemas/mhf/** |
| **B — Skeleton, Schemas & SPI RFC** | Dev B | layer0/** (stubs) · plugins/ · packs/ · schemas/mhf/** · test/layer0/** · pytest migration | docs/** (review only) · CI workflows · anything deleted by A |

**Handoffs:** A's force-push window is day 6, announced 24h ahead; B rebases the skeleton branch
after re-clone. B reviews every MERGE row of the migration matrix; A reviews plugin/harness
schemas and countersigns the SPI RFC (it becomes the IF-1 checklist for M1).

## 2. Board

### Lane A
- [ ] S-M0-A-01 ADR log landed (VG-09/10 migrated + ADR-M0-01…13)
- [ ] S-M0-A-02 annex/KERNEL.md + annex/MEASUREMENT.md
- [ ] S-M0-A-03 SPEC merges applied (matrix rows signed by B)
- [ ] S-M0-A-04 spec/vision/scrum trees deleted; link check green
- [ ] S-M0-A-05 history rewrite: secrets (SEC-01) + artifacts + frontend; scan --all-refs PASS; repo ≤ 3 MB
- [ ] S-M0-A-06 CI reset: RFC-2119 gate, size gate, lane-ownership gate; badges retired
- [ ] S-M0-A-07 roadmap/backlog rewritten; TSK-FE-* closed-kill; superseded_by pointers complete

### Lane B
- [ ] S-M0-B-01 v-next skeleton + ownership map recognised by CI
- [ ] S-M0-B-02 plugin.schema.json + 6 golden vectors
- [ ] S-M0-B-03 harness.schema.json + draft packs/code-default/harness.yaml (validates, digested)
- [ ] S-M0-B-04 SPI RFC signed by A (IF-1 checklist)
- [ ] S-M0-B-05 pytest migration of retained suite; port-map committed
- [ ] S-M0-B-06 evidence blob-store relocation tool; 3-sample round-trip

## 3. Joint verification (Day 8 — gate G-M0)
    python3 tools/scan_secrets.py --all-refs        # PASS
    git count-objects -vH                            # pack ≤ 3 MB
    find docs -name '*.md' | wc -l                   # ≤ 30
    python3 tools/check_markdown_links.py            # PASS
    pytest -q                                        # retained suite green
    python3 tools/check_lane_ownership.py --history  # zero cross-lane commits
Tag: `v0.5.0-m0`. Next board: M1 Sprint 2 (plan §2).

## 4. Explicitly not this sprint
Kernel changes · event taxonomy · SPI implementations · any plugin code beyond stubs ·
coding_* extraction (M3, after G-M2) · anything on the Phase-2/3 deferred list.
```

---

## 5. Risk & dependency ledger (M0–M2)

| Risk | Mitigation |
|---|---|
| History rewrite disrupts in-flight work | Single announced window (day 6); B's branches rebased same day; purge manifest co-signed |
| Schema churn after IF-1 stalls B | Freeze tags + consumer-reviews-producer rule; churn budget: ≤ 2 post-freeze RFCs across M1 |
| E-COV needs registry emitters before registry exists | S-M1-A-05 wires registry kinds to a frozen hook interface (IF-2); B's FSM plugs in at S-M2-A-01 without re-opening emitters |
| Seccomp profiles brittle across kernels | Profiles per verb class, generated from a table; CI runs the security battery in the worker container image (pinned digest) |
| Two-dev bus factor on the kernel | Kernel is a verbatim port with its full inherited test suite; both devs review any `handoff` diff; mutation gate catches silent weakening |
| Walking-skeleton slips (the one genuinely coupled deliverable) | It is *jointly owned by construction*: A's fixture (S-M1-A-08) is B's artifact (S-M1-B-07 / S-M2-B-03); scheduled with 2-day slack in each milestone |
