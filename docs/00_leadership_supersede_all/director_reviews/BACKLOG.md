# BACKLOG — Canonical Engineering Backlog (Convergence + Roadmap to M-8 / v1.0 approach)

Item format: **ID · Milestone · Objective** → Authority · Evidence (as-built) · Target · Scope
(files/symbols) · Depends · Invariants/Non-goals · Failure/Telemetry · Migration · Tests/Falsifier ·
Acceptance/DoD · Unlocks. Ownership classes: `GOV` governance/docs · `RT` runtime · `AG` agency ·
`DM` domain · `SC` schemas/codegen · `TL` tooling · `PK` packs · `TS` clients · `LB` lab/bench.

Readiness: items in §A are task-ready (SPRINT_ACTIVE); §B ready-on-ADR-0098 (SPRINT_UPCOMING);
§C+ blocked on named dependencies only.

---

## §A Foundation Convergence + M-4 (task-ready)

**CV-001 `GOV` · pre-M4 · Ratify ADR-0096 v0.4.0 (as amended) + accept ADR-0097**
Authority: ADR-0097 §2. Evidence: `docs/02_decisions/0096-*.md status: proposed v0.3.0`.
Target: 0096 `accepted` with Amendment A (repro value domains) + B (trusted import closure) merged
into its text; 0097 committed `accepted`. Scope: docs/02_decisions/{0096,0097,INDEX.md(+RF-96..100
rows)}. Depends: Director. Non-goals: any code. Tests: governance doc lints. DoD: INDEX rows
present; statuses flipped; commit message references atomic set CV-002. Unlocks: CV-002, M4-103/104.

**CV-002 `GOV` · pre-M4 · Execute 0096 §12 + §12.1 documentation reconciliation atomically**
Authority: 0096 §12/§12.1; DEVELOPMENT_PLAN §8 (exact edit table). Evidence: `EVIDENCE.md:53`
singular class; VISION v0.7.0 unamended; SPEC ladder rules 2–3; EXTENSIBILITY missing gate;
milestones missing RF attachments; glossary v0.6.1. Target: all twelve documents per table, one
commit with CV-001. Invariants: `_archive/` untouched; no duplication; ADR-only amendment trail.
Tests: link lint, secret scan, `test/governance` doc suites. DoD: table rows all checked; VISION
`version: 0.7.1`. Unlocks: M4-104 (retention semantics now lawful).

**M4-101 `RT` · M-4 · ArtifactWriter + `ArtifactCreated` production path (D-03)**
Authority: SPEC_M4 §2. Evidence: `ports/blob_store.py` unused in product wiring;
`grep -rn "ArtifactCreated" vanguard/packages/runtime` → 0 emitters. Target: `runtime/artifacts.py`
per spec; `ledger_emitter.py` `WRITER_ROLES+={"artifact_writer"}`,
`PRIVILEGED_KIND_OWNERS["ArtifactCreated"]={"artifact_writer"}`; wiring constructs
`FileBlobStore(workspace/.aether/blobs)` for durable profiles, `InMemoryBlobStore` for memory
persistence. Depends: none (payload schema in M4-102 co-lands). Invariants: blob-first/event-second;
store computes digest; no inlined blobs; digests-only mode emits fact `stored:false`. Failure:
`ArtifactWriteError` on durability loss. Telemetry: write latency counters (telemetry, not ledger).
Migration: none. Tests: SPEC_M4 §10 rows 1–2. DoD: RF-95 dry-run trajectory shows ≥3 artifacts
(prompt, model_output, context_bundle). Unlocks: M4-102/103/105, sprint b2 flip.

**M4-102 `AG`+`RT`+`SC` · M-4 · ProvenanceSink + LedgerProvenanceSink + payload schemas (D-04)**
Authority: SPEC_M4 §3–4. Evidence: `agency/context/compiler.py` no sink; `compaction.py` report
in-memory only; sprint b1 ❌. Target: `agency/context/provenance.py`; compiler kwarg
`provenance=None`; `runtime/provenance.py`; `schemas/mhf/{artifact_created,provenance_claim}.schema.json`
+ golden vectors. Depends: M4-101. Invariants: agency imports no runtime; sink failure never aborts
compile; digests over JCS forms; retention-mode blob policy per spec. Non-goals: new kinds;
retrieval provenance beyond context path (M-8). Tests: SPEC_M4 §10 rows 3–5. DoD: fixture episode
ledger contains ≥1 context_selection + ≥1 compaction claim validating against schema; b1 flip.
Unlocks: M4-105, M-6.5 measurement, M-8 retrieval provenance reuse.

**M4-103 `RT` · M-4 · Cache-interaction provenance (D-04 cache leg)**
Authority: SPEC_M4 §4 recorder. Evidence: `adapters/models/{cassette,invocation}.py` record nothing.
Target: `CacheProvenanceRecorder` hooked at invocation seam; cassette/replay hits emit
`ClaimRecorded{cache_interaction}` (cacheId, keyDigest, sourceDigest, hit, validated, turnIndex).
Depends: M4-102, CV-001 (claim vocabulary lawful). Invariants: live no-cache runs emit nothing;
adapters stay behind ports (recorder injected by wiring, not imported by adapters — implement as
invocation-wrapper in runtime/model_selection path if adapter-side injection violates direction).
Tests: cassette-hit test; live-path absence test. DoD: cassette fixture run shows claims. 

**M4-104 `RT`+`SC` · M-4 · `ExecutionProfile.retention` axis → `D_R` (D-05)**
Authority: SPEC_M4 §5; 0096 §8 (ratified). Evidence: `runtime/profiles.py` fields end
`network_mode`; sprint b3 ❌ verified. Target: field+validation+to_dict+PRESETS+_narrow per spec;
`schemas/mhf/execution_profile.schema.json` enum. Depends: CV-001/002. Invariants: hermetic⇒full;
narrow-only; no silent fallback semantics touched. Migration: intended `D_R` change (documented in
release notes). Tests: SPEC_M4 §10 row 6; RF-87 extension. DoD: `to_dict()` golden vector updated;
b3(retention) flip. Unlocks: M4-105 derivation input.

**M4-105 `RT` · M-4 · Reproducibility vector capture at run close (D-06, RF-100)**
Authority: SPEC_M4 §6; ADR-0097 §2.1 domains. Evidence: no repro computation anywhere;
`determinism.py` pins exist. Target: `runtime/reproducibility.py` pure derivation + run-close
`ClaimRecorded{reproducibility_at_run_close}` before trajectory flush; embed in trajectory.
Depends: M4-101/102/104. Invariants: computed-not-declared (episode cannot author); run-close
claim never overwritten; scoped-claim language in report strings. Tests:
`test_rf100_reproducibility_vector.py` derivation table + immutability. DoD: falsifier green;
b3(repro) flip. Unlocks: M-5a `reproducibility_current` (M5A-109).

**M4-106 `RT`+`SC` · M-4 · Trajectory additive provenance/artifact/repro sections (D-07)**
Authority: SPEC_M4 §7. Evidence: `assemble_trajectory` signature (no provenance inputs);
`trajectory.schema.json` lacks members. Target: additive kwargs + members; reader extraction;
schema update (no version bump). Depends: M4-101/102/105. Invariants: additive-only; old
trajectories parse. Tests: §10 row 8. DoD: `diff_trajectories` can ablate on provenance fields.

**M4-107 `LB` · M-4 · Append/fold micro-benchmark baseline**
Authority: assessment §7; DEVELOPMENT_PLAN §10. Evidence: `lab/bench.py` exists, no ledger bench.
Target: `bench_append_fold` — SqliteEventStore WAL append events/s; `reduce_batch` μs/event on
1k/10k fixtures; JSON artifact under `benchmarks/`. Depends: none (parallel). DoD: baseline
artifact committed pre-M-5a. Unlocks: M-5a regression gate (SPEC_M5A §9.5).

**M4-108 `LB` · anytime · M7-01 independence analysis lane (analysis-only)**
Authority: milestones M7-01 (ADR-0092 provenance). Evidence: lane named, unstarted. Target:
`lab/m701_independence.py` over fixed-seed recorded workloads → independence report artifact.
Constraints (law): may not add concurrency/scheduler/workers/claims/leases/topology. Depends:
recorded ledgers (grows richer post-M4-102). DoD: first report versioned; feeds ADR-0099.

**M4-109 `RT`+`GOV` · M-4 exit · Execute RF-95 product proof (D-08)**
Authority: SPEC_M4 §9; sprint M4-05. Evidence: runner dry-run qualified; NO-GO standing.
Target: one live-candidate run; evidence bundle; independent review; Director closes M-4.
Depends: M4-101…106 all green; CV-001/002. Invariants: no fake/cassette; no manual event repair;
one candidate. Failure: gap ⇒ NO-GO persists, bundle preserved unrepaired. DoD: review checklist
signed; milestones row flipped COMPLETE. Unlocks: ADR-0098 window (§B).

**TS-101 `TS` · parallel lane · Studio: render artifact/provenance sections of trajectories**
Authority: always-parallel lane (client contract). Evidence: `vanguard/clients/studio` reads
trajectories today. Target: read-only rendering of new optional members. Depends: M4-106 schema.
DoD: studio displays artifact index + repro vector for a fixture trajectory. (Nice-to-have; never
blocks M-4.)

---

## §B M-5a window (ready-on-ADR-0098; promoted via SPRINT_UPCOMING)

**M5A-100 `GOV` · Draft + accept ADR-0098 (substrate change set)** — content = SPEC_M5A as annex;
kind roster §5 table; migration §3; exit gates §9. Depends: M4-109. DoD: accepted; INDEX row.
Unlocks: all below.

**M5A-101 `SC`+`DM` · Envelope `mhf.event/2` + codegen (D-09, RF-99)** — schema oneOf {/1 read,
/2 read-write}; four fields per SPEC_M5A §3; regen `types_gen.py`; `parse_event_envelope`
version dispatch with reader-side defaults. Invariants: never write defaults; nulls only where
inapplicable. Tests: `test_rf99_*` incl. role-consistency forgery rejection + mixed-chain replay.

**M5A-102 `RT` · Emitter v2 write path + authority defaults** — `LedgerEmitter` populates
authority fields per role table; `WIRE_VERSION` cutover flag; deprecated-kind write rejection
(`DeprecatedKindError`). Depends: M5A-101. Tests: emitter authority matrix.

**M5A-103 `SC`+`DM` · Vocabulary unification + deprecation (D-10)** — fold 8 live kinds into
schema; delete `_V4_ONLY_KINDS`; `DEPRECATED_KINDS`/`READABLE_KINDS`; rewrite
`test_event_coverage.py` (schema-sole-authority + reducer-coverage-or-noop-register). Depends:
M5A-101. DoD: `grep _V4_ONLY_KINDS` → 0.

**M5A-104 `DM` · Execution contracts (D-11)** — `domain/execution/{scope,lineage,operation}.py`
per SPEC_M5A §5 + `InvalidScopeAttenuation`; JCS vectors; compat-mapping doc note. Parallel-safe
(pure domain). Non-goal: verb subclassing.

**M5A-105 `SC`+`DM`+`RT` · Semantic kinds package (D-12 roster)** — 5 kinds: schemas+vectors,
emitter ownership rows (orchestrator/session; ProgressAssessed also evaluator_gateway), reducer
handlers. Depends: M5A-101/103. Tests: per-kind reduce round-trip; coverage suite.

**M5A-106 `DM` · AgentView + reducer (D-12)** — `domain/ledger/agent_view.py` per SPEC_M5A §6.
Depends: M5A-104/105. Tests: fold determinism under pins; deprecated-kind no-op tolerance.

**M5A-107 `RT` · RF-96 cold-reconstruction falsifier** — scripted episode → kill → fresh-process
golden AgentView; interrupted-mid-effect variant via `RecoveryScanner`. Depends: M5A-106.
DoD: `test_rf96_cold_reconstruction.py` green vs file-backed WAL.

**M5A-108 `RT`+`SC` · CheckpointManager + `mhf.checkpoint/1` (D-13)** — role `checkpointer`;
digest-verified load; fail-closed-to-cold-fold; policy by count/turns; bench extension
(checkpointed ≤20% cold target). Depends: M5A-106, M4-101(blob), M4-107(bench).

**M5A-109 `RT` · `reproducibility_current` computation (RF-100 completion)** — recompute vector
against present provider/artifact availability; record as new claim; never overwrite run-close.
Depends: M4-105, M5A-101.

**M5A-110 `TL` · RF-97 TCB budget v2 (D-14)** — closure-aware `check_tcb_budget.py` per SPEC_M5A
§8; CI gate switch; self-tests. Parallel-safe from Phase A (tooling-only; gate flips at window).
DoD: `test_rf97_tcb_budget_v2.py` green; CI red on synthetic closure drift fixture.

**M5A-111 `GOV`+`RT` · Window exit gates + M-5-BASE re-tag (D-15)** — run SPEC_M5A §9 checklist;
pin set recorded; tag pushed; `RUNTIME.md §15` gap-closure note; `events.md` tables. Depends: all
§B. Unlocks: §C/§D.

---

## §C M-5b (blocked on M-5-BASE + OD-3)

**M5B-100 `GOV` · OD-3 oracle selection memo** (criteria in SPEC_M5B_M6 §1). ·
**M5B-101 `PK` · Pack scaffold `packs/formal-<oracle>/`** (mirror code-default; manifests enter
`D_H`). · **M5B-102 `PK`+`RT-adapters` · Solver toolkit verbs** (`solver.check` etc.; typed
Result; sink class; capability decl). · **M5B-103 `adapters/evaluators` · Deterministic witness
evaluator suite** (signed verdicts; I-5). · **M5B-104 `PK` · Domain projections + context policy**
(pack-owned reducers over generic kinds; no new kinds — enforced by RF-86 job). ·
**M5B-105 `TL` · RF-86 zero-semantic-diff CI job** (substrate path diff vs M-5-BASE). ·
**M5B-106 · Integration run + RF-52/53 fixture set + RF-98 report + exit review.**

## §D M-6 (blocked on M-5-BASE; ∥ with §C)

**M6-100 `RT` · SpawnAdapter core (D-17)** — per SPEC_M5B_M6 §2 pseudocode; sink-class
"delegation" binding in wiring; sole ChildSpawned/Returned writer. Depends: M5A-104 (scope
attenuation), M5A-106 (children in view). · **M6-101 `SC` · `mhf.child-{spawned,returned}/1`
payloads + vectors** (ADR-0090 roster; payload-level only). · **M6-102 `RT` · Budget algebra +
conservation tests (RF-57)** — reserve/consume/release across tree via existing Governor events. ·
**M6-103 `RT` · Kill-tree + restart recovery (RF-59)** — orphan ChildSpawned reconciliation in
`RecoveryScanner`; idempotent subtree settlement. · **M6-104 · Falsifier matrix RF-55/56/58** +
governance test restricting direct `engine.spawn` to lab profiles. · **M6-105 · Nested-lineage
demo run bundle + exit review.**

## §E M-6.5 / §F M-7 / §G M-8 (contract-level; blocked as marked)

**M65-100 `GOV` · OD-4 Confidence Protocol (`docs/06_protocols/confidence.md` + `mhf.confidence/1`)**
— prerequisite gate; depends M4 telemetry. · **M65-101 `DM` · ProgressProjection.** ·
**M65-102 `RT`+plugin · MetaController SPI + engine hook (between-turn consult; directives →
ordinary proposals).** Depends: M5A kinds; M6 for delegate. · **M65-103 `LB` · Paired-run harness
+ study report.** · **M65-104 · Exit gate per SPEC_M65_M7_M8 §1 (or disabled-by-default negative
result recorded).**

**M7-100 `GOV` · ADR-0099 from M7-01 report (implement/simplify/cancel; default cancel <30%).** ·
**M7-101 `SC`+`RT` · `mhf.topology/1` + lowering compiler → RunPlanExtension.** · **M7-102 `RT` ·
SchedulerPolicy split + readiness mechanism (claims TTL = coordination metadata law).** ·
**M7-103 · Safe-parallel independent reads (only concurrency without ADR-0099).** · **M7-104 ·
3-topology zero-diff falsifier + exit.**

**M8-100 `GOV` · ADR-0100 promotion pipeline (+ dead-kind reintroduction decision).** ·
**M8-101 `ports`+adapters · Category ports (Knowledge/Experience/SkillLibrary/ProjectMemory)
[provisional shapes]; capability-mediated access; retrieval provenance via M4-102 path.** ·
**M8-102 · Skill candidate pipeline (generator≠evaluator≠promoter; composition vN+1 unit).** ·
**M8-103 · Regression evaluation suites (held-out, affected-context, presence-only adversarial,
grounding, verification).** · **M8-104 · Promotion/rollback executable path + tested rollback.** ·
**M8-105 · Held-out lift study + exit review + RF-98/neutrality evidence.**

---

## Open-decision register (genuine remaining uncertainty)

| OD | Decision | Owner | Due | Blocks |
|---|---|---|---|---|
| OD-1 | ADR-0098 final kind roster (accept/trim §5 table) | Director | M-5a entry | §B |
| OD-2 | Checkpoint policy defaults (interval; per-lineage vs per-run) | Tech Lead | M5A-108 | none (defaultable) |
| OD-3 | Formal oracle selection | Director | M-5b entry | §C |
| OD-4 | Confidence protocol signal set + calibration method | Tech Lead+Director | M-6.5 entry | §E |
| OD-5 | ADR-0099 concurrency disposition | Director | M-7 entry | §F scope |
| OD-6 | ADR-0100 lifecycle events: reintroduce dead kinds vs ClaimRecorded payloads | Director | M-8 entry | M8-100 |
| OD-7 | Multi-tenant isolation law owner (assessment OQ-8) | Director | pre-M-9 | none through M-8 |
| OD-8 | Blob GC vs `retention_class`/`legal_hold` semantics | Tech Lead | M-8 design | M8-101 |
