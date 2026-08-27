# ARCHITECTURE_DELTA — Current (as-built `main`) → Accepted Target (Phase 1)

Format per delta: current evidence → Phase-1 authority → target → layer → symbols → contract/schema
impact → compatibility/migration → tests affected → removals → unlocks. Classes:
`GOV` governance · `DOC` documentation-only · `CON` contract change · `SCH` schema/protocol ·
`FND` foundational correction · `CAP` new generic capability · `DOM` domain capability ·
`MIG` migration · `DEL` deletion/deprecation · `FUT` future-milestone.

---

## D-01 — Constitutional fork resolution `GOV`
**Current:** ADR-0096 `status: proposed` v0.3.0; VISION.md v0.7.0 lacks §12 edits; `EVIDENCE.md:53`
singular reproducibility class; `sprint_active.md` M4-04 b3 self-declared blocked on ratification.
**Phase 1:** ADR-0097 §2 — ratify 0096 with Amendments A/B. **Target:** one constitution;
0096 v0.4.0 `accepted`; 0097 `accepted`. **Layer:** governance. **Symbols:** none (docs).
**Compat:** none. **Tests:** `test/governance/` doc-topology checks re-run. **Unlocks:** D-02,
D-05, D-06, entire M-5a window authority.

## D-02 — Documentation reconciliation `DOC`
Exact edit table in `DEVELOPMENT_PLAN.md §8` (12 documents; atomic commit with D-01 per 0096 §12.1
"same atomic commit" rule). **Removal:** none; `_archive/` frozen. **Consistency checks:** link
lint, secret scan, ladder-authority lint (`tools/linters/`), one-canonical-definition sample audit.

## D-03 — Artifact production path `CAP`
**Current:** `ports/blob_store.BlobStorePort` + `adapters/stores/blob_store.{InMemoryBlobStore,
FileBlobStore}` exist; **no caller writes prompts/outputs/snapshots/patches**; `ArtifactCreated`
in `EVENT_KINDS` with live reducer handling but zero production emitters; `runtime/wiring.py`
constructs no blob store for product runs.
**Phase 1:** F-4/M4-04 b2; EVIDENCE provenance rule; ledger ≠ blob dump (VISION cap. 17).
**Target:** `runtime/artifacts.py` → `ArtifactWriter` (new); wired in `runtime/wiring.py` and
`root.run_composed`; new writer role `artifact_writer` added to `WRITER_ROLES` and
`PRIVILEGED_KIND_OWNERS["ArtifactCreated"] = {"artifact_writer"}` in `runtime/ledger_emitter.py`;
payload `mhf.artifact-created/1` (new file `schemas/mhf/artifact_created.schema.json`).
**Layer:** runtime (+ ports unchanged). **Compat:** additive; role addition is code-level, not
envelope-level. **Tests:** new `test/runtime/test_artifact_writer.py`,
`test/contracts/test_artifact_created_payload.py`, emitter authority test extension.
**Unlocks:** D-04, D-06, D-07, RF-95 trajectory completeness; later M-8 experience retrieval.

## D-04 — Context/compaction/cache provenance `CON`
**Current:** `agency/context/compiler.ContextCompiler.compile` selects/fits layers;
`compaction.COMPACTION_REGISTRY` strategies return `CompactionReport(removed_tokens, strategy)`
(wire type exists) — nothing durable emitted (verified; sprint M4-04 b1). Model cache
(`adapters/models/cassette.py`, `invocation.py`) records nothing.
**Phase 1:** F-4/M4-04 b1; 0096 §5 correlation; §6.2bis payload-position rule (no kind change).
**Target:** agency-local `ProvenanceSink` protocol (new `agency/context/provenance.py`) injected
into `ContextCompiler.__init__`; runtime adapter `runtime/provenance.py::LedgerProvenanceSink`
writes input/output bundles via `ArtifactWriter` and emits `ClaimRecorded` with
`mhf.provenance-claim/1` payload (`claimKind ∈ {context_selection, compaction, cache_interaction,
reproducibility_at_run_close}`); model invocation path emits `cache_interaction` claims.
**Layer:** agency (protocol) + runtime (impl) — preserves the no-upward-import law.
**Compat:** `ContextCompiler` gains optional kwarg (default `None` = no-op) — zero break.
**Tests:** `test/agency/test_context_provenance.py` (sink called with digests, never blobs);
`test/runtime/test_provenance_claims.py`; golden payload vectors. **Unlocks:** RF-95, M-6.5
measurement, M-8 context-policy learning.

## D-05 — ExecutionProfile retention axis `SCH`
**Current:** `runtime/profiles.ExecutionProfile` fields end at `network_mode`; `to_dict()` is the
`profile_digest` preimage; PRESETS `product/local/sandboxed/hermetic`; no `retention`.
**Phase 1:** F-4/M4-04 b3; ADR-0096 §8; assessment §6.
**Target:** field `retention: str = "standard"` ∈ {`digests-only`,`standard`,`full`} with
`__post_init__` validation (`hermetic` ⇒ `full`); included in `to_dict()`; preset values —
product `standard`, local `standard`, sandboxed `standard`, hermetic `full`; `_narrow` may narrow
`full→standard→digests-only` only. `schemas/mhf/execution_profile.schema.json` gains the enum.
**Compat:** `profile_digest`/`D_R` changes for new runs — intended identity change; historical
`D_R` values remain valid for their runs. **Tests:** `test/runtime/` profile digest/round-trip +
RF-87 extension asserting retention reaches `D_R`. **Unlocks:** D-06 derivation input.

## D-06 — Computed reproducibility vector `CAP`
**Current:** nothing computes or records reproducibility; `runtime/determinism.py` holds pins.
**Phase 1:** ADR-0097 §2.1 value domains; 0096 §8 computed-not-declared; RF-100.
**Target:** `runtime/reproducibility.py` (new): pure `assess_reproducibility(facts) →
ReproducibilityVector`; recorded at `EpisodeCompleted` as `ClaimRecorded`
`claimKind=reproducibility_at_run_close` and embedded in trajectory; never overwritten
(recompute-as-new-claim only). **Tests:** `test/falsifiers/test_rf100_reproducibility_vector.py`
(derivation table; immutability; agent cannot self-declare). **Unlocks:** M-5a `reproducibility_current`.

## D-07 — Trajectory additive sections `SCH`
**Current:** `runtime/trajectory.assemble_trajectory` emits turns/receipts/model routes/costs;
`schemas/mhf/trajectory.schema.json` has no provenance/artifact/repro members.
**Target:** additive optional top-level members `provenance`, `artifacts`, `reproducibility_at_run_close`
(SPEC_M4 §7); `TrajectoryReader.extract_variables` extended. **Compat:** additive-only within
`mhf.trajectory/1`; old readers unaffected (CT-44 tolerance). **Tests:** schema validation vectors;
`test/runtime/test_trajectory_reader.py` extension.

## D-08 — RF-95 execution `verification`
**Current:** `tools/runners/run_rf95_product_proof.py` dry-run qualified; gate NO-GO.
**Target:** single live one-candidate run post D-03…D-07; independent review; Director closes M-4.
**Removal trigger:** none. **Unlocks:** M-5a window authority.

## D-09 — Envelope `mhf.event/2` `FND` `SCH` `MIG`
**Current:** `mhf.event/1` carries `principal, principal_id, parent_principal_id, causation_id,
correlation_id, idempotency_key, harness_digest` (see `LINEAGE_FIELDS`, `EventEnvelope`); no
`authority_source/policy_version/approval_reference/capability_grant`.
**Phase 1:** 0096 §6/§6.2bis; RF-99; ADR-0097 §3.1. **Target:** four typed fields (two nullable);
parser dual-read; emitter single-write `/2`; codegen regenerates `types_gen.py`.
**Compat:** per DEVELOPMENT_PLAN §9.2; chain continuity proven by mixed-version replay test.
**Tests:** `test/falsifiers/test_rf99_authority_provenance.py`; mixed-chain fresh-process replay.
**Removals:** none (v1 read support retained ≥ v1.0).

## D-10 — Vocabulary unification + deprecation `FND` `DEL`
**Current:** `domain/ledger/events.py::_V4_ONLY_KINDS` (16) ∪ generated enum (42); 8 dead kinds
(`ObservationRequested, OperatorInvoked, OperatorSelected, CorrectionRecorded, CandidateBuilt,
CandidateAttested, CanaryPromoted, RollbackTriggered`).
**Phase 1:** F-2; ADR-0097 §3.2. **Target:** schema is sole kind authority; 8 live kinds folded
into `event_envelope.schema.json`; `_V4_ONLY_KINDS` **deleted**; `DEPRECATED_KINDS` registered in
`docs/05_contracts/events.md` + rejected on write (`LedgerEmitter` raises), accepted on read.
**Tests:** `test/contracts/test_event_coverage.py` rewritten to assert schema-only derivation;
deprecation write-rejection test; historical-read tolerance test. **Unlocks:** A-4/I-8 restored
without exception prose; M-8 reintroduction path clean.

## D-11 — Operation/Lineage/ExecutionScope contracts `CON`
**Current:** implicit — proposals/effects/turns exist (`agency/episode/state.{Proposal,Turn,
Episode}`); authority `Scope` in `kernel/attenuation.py`; no domain-level execution contracts.
**Target:** new `domain/execution/{operation.py, lineage.py, scope.py}` (SPEC_M5A §5) — frozen
dataclasses + protocols; kernel `Scope` remains the authority view referenced by `ExecutionScope`.
**Forbidden:** class-hierarchy of operation verbs (ADR-0097 lock). **Tests:** contract round-trip +
JCS vectors. **Unlocks:** D-12, D-17 typed spawn.

## D-12 — AgentView + semantic kinds `FND` `CAP`
**Current:** `domain/ledger/session_projection.project_session` (thin dict) and
`runtime/ledger/projections.RunSummaryProjection`; no goal/plan/strategy kinds; no AgentView.
**Target:** ADR-0098 kinds `GoalDeclared, PlanRevised, StrategyChanged, ProgressAssessed,
ContextCompacted` (writer roles: orchestrator/session; reducer handling; schemas; vectors);
`domain/ledger/agent_view.py::{AgentView, AgentViewReducer, fold_agent_view}`; RF-96 test = fresh
process rebuilds goal/plan/attempts/settled effects/budget/strategy/terminal from ledger alone.
**Unlocks:** M-6 child briefs from projections; M-6.5 ProgressProjection inputs.

## D-13 — Checkpointed fold `CON` `CAP`
**Current:** `CheckpointCreated` kind exists, never emitted; recovery folds full history
(`replay_ledger_state` O(n)). **Target:** `mhf.checkpoint/1` payload (state blob in artifact
store, digest-verified) + `runtime/ledger/checkpoints.py`; reducer/AgentView fold accepts
checkpoint + suffix; O(suffix) cold start. **Tests:** checkpoint/suffix equivalence vs cold fold;
corrupted-checkpoint fail-closed → cold fold fallback.

## D-14 — RF-97 TCB budget v2 `GOV` tooling
**Current:** `tools/linters/check_tcb_budget.py` LOC-only over `kernel/` (1366/1438).
**Target:** measure trusted import closure (kernel + `domain/canonicalisation/{digest,jcs}` +
`domain/selectors/resource_selector`); gate: closure allowlist, per-dim metrics (invariants, public
contracts via `kernel.__all__`, privileged ops via kernel-owned `PRIVILEGED_KIND_OWNERS` kinds,
dependency count, domain-concept scan = 0, extension-knowledge imports = 0, change amplification =
reverse-dependency count), JSON output, CI gate. **Tests:** linter self-tests under `test/tools/`.

## D-15 — M-5-BASE re-tag `MIG`
Tag + pin set (reducer version, schema versions, envelope version) recorded via
`runtime/determinism.py` and release notes; only after D-09…D-14 green + fresh-process replay
parity. RF-86 measures against this tag.

## D-16 — Formal Pack #2 `DOM` (M-5b) — see SPEC_M5B_M6 §1
New `packs/formal-<oracle>/`; zero kernel/agency/runtime semantic diff (RF-86, RF-98);
deterministic witness (RF-52/53).

## D-17 — Mediated `agent.spawn` `CAP` (M-6) — see SPEC_M5B_M6 §2
**Current:** in-process `EpisodeEngine.spawn` (S8-B-01) + `runtime/delegation.{SpawnRequest,
prepare_spawn}`; `spawn_adapter` role reserved, unimplemented; ADR-0080/0090/0091 design frozen.
**Target:** `agent.spawn` as ordinary EffectRequest; `runtime/delegation.SpawnAdapter`
(EffectAdapter) creates nested lineage post-intent, sole writer of `ChildSpawned/ChildReturned`;
kernel verb-blind. `EpisodeEngine.spawn` becomes the in-process executor invoked *by* the adapter
(not by policy directly) — direct call path deprecated for product profiles.

## D-18 — M-6.5 meta-control `FUT` — SPEC_M65_M7_M8 §1
ProgressProjection (domain), MetaControllerPlugin (plugin SPI), Confidence Protocol
(`mhf.confidence/1`), paired-run lab harness. No kernel change (RF-98 re-check).

## D-19 — M-7 topology + scheduler `FUT` — SPEC_M65_M7_M8 §2
`mhf.topology/1` artifact → lowering compiler → RunPlan lineage templates + `SchedulerPolicy`
protocol; scheduler *mechanism* in runtime; I-11 lift only via ADR-0099 with M7-01 evidence.

## D-20 — M-8 memory/skills `FUT` — SPEC_M65_M7_M8 §3
Five memory category ports (provisional sketches); skill lifecycle with composition-level
promotion; dead-kind reintroduction package if the M-8 pipeline adopts them (ADR-0100).
