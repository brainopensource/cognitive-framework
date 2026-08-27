---
id: adr-master-index
class: decision
authority: binding-decision
canonical_for:
  - architecture-decision-records-index
  - canonical-rf-falsifier-allocation-register
status: living
owner: engineering-director
version: "0.7.3.dev0"
last_verified: 2026-08-26
read_when:
  - resolving-architectural-decisions
  - selecting-an-implementation-bundle
do_not_read_when:
  - consulting-historical-reviews
supersedes: []
superseded_by: null
---

# ADR Index — Architecture Decision Records

> **Status:** Living Master Index of Architecture Decision Records for Vanguard / AETHER.  
> **Rule:** Decision identifiers and Git history are append-only. [`VISION.md`](../../VISION.md) is Law Zero and outranks every ADR (`ADR-0095`); ADRs outrank general documentation; newer ADRs supersede older ones explicitly. Per ADR-0086, superseded bodies may leave the default working tree only after their permanent lineage and recovery commit are indexed.
> **Companion Documents:** [`DEFERRED_REJECTED.md`](DEFERRED_REJECTED.md) · [`DRIFT_REGISTER_v045.md`](DRIFT_REGISTER_v045.md) · [`SPEC.md`](../SPEC.md) · [`sprint_active.md`](../03_execution/sprint_active.md).

---

## Quick Navigation

- 🚀 [v0.6.0 Concept Lock & Foundation Execution (`0069`–`0076`)](#v060-concept-lock--foundation-execution-canonical-law) — **Start here for active production law**
- 🧭 [Tier S+ Evolution Contract (`0077`–`0085`)](#tier-s-evolution-contract-00770085) — **Ratified evolution contracts and reservation law**
- 🧹 [Repository Governance (`0086`–`0087`)](#repository-governance) — historical-body consolidation, topology, and recovery rule
- 🔒 [M-3C to M-8 Concept Lock (`0088`)](#m-3c-to-m-8-concept-lock) — canonical activation, evidence, generality, delegation, and scale seams
- 🛠️ [W-3D Product Runtime Profiles (`0089`)](#w-3d-product-runtime-profiles-0089) — execution profiles, bootstrap, activation, and product/runtime seam
- 🧬 [Mediated Delegation Event Roster (`0090`)](#mediated-delegation-event-roster-0090) — `ChildSpawned`/`ChildReturned` allocation, single writer, and reducer fold
- 🔐 [Delegation Digest and Measurement Decisions (`0091`–`0092`)](#delegation-digest-and-measurement-decisions-00910092) — collision-free child state identity, archived-bundle boundary, and measurement-only M7-01
- 🧰 [Product-first M-4 (`0094`)](#product-first-m-4-0094) — useful coding proof first; hermetic assurance remains optional and honest
- 🌟 [Vision as Law Zero (`0095`)](#vision-as-law-zero-0095) — **`VISION.md` is the constitutional authority for v0.7+**; roadmap reconciled; milestone identifier mapping
- 🧪 [Constitutional Evidence and Two-Lane Activation (`0096`–`0098`)](#constitutional-evidence-and-two-lane-activation-00960098) — proof-honest evidence, strict schema evolution, Phase-0 closure, and event substrate `/2`
- 🧭 [M-8 Contract and 2026 Convergence (`0100`–`0102`)](#m-8-contract-and-2026-convergence-01000102) — durable memory/promotion, receipt-backed acceptance, and baseline succession
- 🛡️ [Canonical RF Falsifier Allocation Register](#canonical-rf-falsifier-allocation-register) — ratified requirement identifiers and falsifier allocations
- 📜 [Consolidated Historical Lineage](#consolidated-historical-lineage) — summaries here; full bodies in Git
- 📂 [Companion Registers & Governance](#companion-registers--governance-documents)

---

## v0.6.0 Concept Lock & Foundation Execution (Canonical Law)

These ADRs form the binding architectural constitution approved by Engineering Leadership (`ADR-0075`).

| ADR | File & Title | Scope & Key Decisions | Status |
|---|---|---|---|
| `0069` | [`0069-runtime-convergence-python-first-packages-canonical.md`](0069-runtime-convergence-python-first-packages-canonical.md) | **Runtime Convergence:** Python-first control plane; `vanguard/packages/` is the sole canonical production lattice (`domain → ports → kernel → agency → runtime → adapters`); `layer0/` is absorbed; no third tree or Rust rewrite. | accepted |
| `0070` | [`0070-recursive-substrate-agent-spawn-swarm-as-policy.md`](0070-recursive-substrate-agent-spawn-swarm-as-policy.md) | **Recursive Substrate:** `Agent = Principal + HarnessInstance`; `spawn()` is the sole recursion primitive with monotonic capability/budget attenuation; swarm coordination is policy over events, not a separate engine. | accepted |
| `0071` | [`0071-authority-state-ledger-identity-trinity.md`](0071-authority-state-ledger-identity-trinity.md) | **Authority, State & Identity Trinity:** Three-plane split (Decision / State / Evidence); Ledger-as-truth; cold replay from disk (I-4); Identity trinity ($D_H$ composition, $D_R$ runtime run, $D_X$ experiment). | accepted |
| `0072` | [`0072-plugin-boundary-wire-first-evaluator-exterior.md`](0072-plugin-boundary-wire-first-evaluator-exterior.md) | **Plugin Boundary & Exterior Judge:** JSON-RPC 2.0 / UDS wire-first plugin boundary; Exterior signed evaluator daemon (UID 10002); unforgeable signed verdicts; refusal of in-engine or self-signing evaluators. | accepted |
| `0073` | [`0073-v060-lock-vs-defer.md`](0073-v060-lock-vs-defer.md) | **v0.6.0 Lock vs. Defer vs. Refuse:** Boundaries of the foundation lock through Wave 4; explicit deferral/refusal register (deferring extra packs, concurrency, meta-harness until post-M4). | accepted |
| `0074` | [`0074-gamma-lock-amendments-proof-budget-writer-identity.md`](0074-gamma-lock-amendments-proof-budget-writer-identity.md) | **GAMMA Lock Amendments:** Bound falsifier discipline (proof obligations); typed budget algebra (additive dimensions vs. structural ceilings); writer authority on privileged events; full $D_H$ definition. | accepted |
| `0075` | [`0075-director-review-v060-approved-wave0-authorized.md`](0075-director-review-v060-approved-wave0-authorized.md) | **Director Review & Wave 0 Authorization:** Formal Director/Chief Engineer approval of Concept Lock GAMMA; adds falsifiers F-18…F-21; authorizes Wave 0. | accepted |
| `0076` | [`0076-foundation-execution-decisions-canonical-artifacts.md`](0076-foundation-execution-decisions-canonical-artifacts.md) | **Canonical Artifacts for Execution:** Names definitive artifacts for envelope (`mhf.event/1`), selector algebra (`resource_selector.py`), bytes (JCS RFC 8785), $D_H$, signed verdicts (`SignedVerdict`), and single-writer `LedgerEmitter`. | accepted |

---

## Tier S+ Evolution Contract (`0077`–`0085`)

The Engineering Director ratified this catalog on **2026-08-21**. These ADRs are binding design
law, but their implementation remains limited by the milestone named in each record. In
particular, acceptance does not authorize M-3–M-10 production work before its entry gate. This
table is the canonical numbering map and supersedes conflicting maps in advisory proposal files.

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0077` | [`0077-named-component-graph-manifest.md`](0077-named-component-graph-manifest.md) | **Named Component Graph:** `mhf.manifest/2`, typed bindings, one semantic compiler, complete graph identity in $D_H$; dated amendment reserves profiles and selector-shaped spawn authorization without activating them. | accepted; amended 2026-08-21 | 2026-08-21 |
| `0078` | [`0078-trajectory-un-hollowing-cost-accounting.md`](0078-trajectory-un-hollowing-cost-accounting.md) | **NOVA-1:** non-breaking `mhf.trajectory/1` content strengthening, explicit missingness, conserved cost, $D_R/D_X$, derived legacy exclusion; immediate RF-23 M-2 gate. | accepted | 2026-08-21 |
| `0079` | [`0079-absent-vs-forged-derived-promotability.md`](0079-absent-vs-forged-derived-promotability.md) | **Absent vs Forged:** three evidence states; declared absence enters $D_H$; promotability is derived and never author-writable. | accepted | 2026-08-21 |
| `0080` | [`0080-capability-mediated-agent-spawn-design-freeze.md`](0080-capability-mediated-agent-spawn-design-freeze.md) | **Mediated `agent.spawn`:** design frozen now; S0–S12 implementation deferred to M-6 after M-4/M-5. | accepted; implementation deferred | 2026-08-21 |
| `0081` | [`0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md`](0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md) | **Lifecycle and convergence:** add `PluginDiscovered`/`PluginVerified`; absorb registry/compose; NOVA-4; atomic Layer-0/package/CI deletion at M-3. | accepted | 2026-08-21 |
| `0082` | [`0082-universal-turn-loop-m10-compatibility-contract.md`](0082-universal-turn-loop-m10-compatibility-contract.md) | **Universal mechanism and M-10 compatibility:** RF-25 cold continuation plus twelve stable substrate seams for graph, authority, state, evidence, identity, data, ports, schemas, and promotion. | accepted | 2026-08-21 |
| `0083` | [`0083-dynamic-pareto-controller-profile-matrix.md`](0083-dynamic-pareto-controller-profile-matrix.md) | **Dynamic Pareto profiles:** alpha/beta/gamma/delta as composition policy; feasibility first; schema M-3, controller activation M-7. | accepted; activation deferred | 2026-08-21 |
| `0084` | [`0084-compounding-macro-tools-active-inference.md`](0084-compounding-macro-tools-active-inference.md) | **Compounding and Active Inference:** T0 witness memo at M-5; least-privilege macro lab M-9; VFE/EFE, DPO, exact paired promotion M-10. | accepted; phased implementation | 2026-08-21 |
| `0085` | [`0085-reversibility-radius-decide-shape-defer-implementation.md`](0085-reversibility-radius-decide-shape-defer-implementation.md) | **Reservation discipline:** classify reversibility radius; reserve R0/R1 identity shape through parse/digest/refuse/falsify; defer implementation; RF-73–RF-75. | accepted; amended 2026-08-21 | 2026-08-21 |

**Amendment record.** The Director chose a dated in-place amendment to ADR-0077 rather than filing
a separate ADR at that time. ADR-0085 carries the matching dated correction so its original boolean spawn example
cannot conflict with the canonical selector algebra. ADR-0080 records RF-26, and ADR-0082 names
RF-76/RF-77 without advancing their implementation milestones.

## W-3D Product Runtime Profiles (`0089`)

ADR-0089 was accepted by the Engineering Director on 2026-08-24. W-3D is an authorized corrective
wave for execution profiles, adapter bootstrap, real plugin activation, portable assurance modes, and
the generic CLI/runtime entrypoint. RF-85 execution is paused until W-3D requalifies the baseline;
M-5 through M-8 remain locked.

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0089` | [`0089-execution-assurance-profiles-and-product-runtime.md`](0089-execution-assurance-profiles-and-product-runtime.md) | **W-3D Product Runtime Profiles:** identity-bearing execution profile, one bootstrap seam, explicit assurance modes, real activation handles, shared generic entrypoint, durable streaming fan-out. | accepted | 2026-08-24 |

**Immediate authorization boundary.** W-3D may implement only W3D-00 through W3D-12 and its RF-87–RF-94
falsifiers. It does not authorize `agent.spawn`, concurrency, topology engines, Pack #2, retrieval,
macro promotion, adaptive routing, or meta-cognition.

---

## Mediated Delegation Event Roster (`0090`)

ADR-0090 was ratified by the CEO on 2026-08-24. It allocates exactly two event kinds for mediated
delegation, binds `runtime.SpawnAdapter` as their sole legal writer, and folds them into
`LedgerState.children`. The kernel is untouched; both events are emitted from `runtime/`.

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0090` | [`0090-mediated-delegation-event-roster.md`](0090-mediated-delegation-event-roster.md) | **Mediated delegation event roster:** `ChildSpawned`/`ChildReturned` allocated; `SpawnAdapter` sole writer; open-until-returned fold with cold reconciliation; cost conservation; derived authority; no `ChildFailed` third kind; no kernel change. | accepted | 2026-08-24 |

**This ADR does not close M-6.** It closes the roster question only. `agent.spawn` remains inert at
manifest ingress and the product path until the active M-6 gate enables those seams. RF-55–RF-59
are implemented as one conjunctive gate: RF-55 grant denial/no child event; RF-56 durable intent,
idempotent receipt and strict attenuation; RF-57 declared target, four-dimensional conservation and
depth/turn ceilings; RF-58 explicit evaluator authority plus typed acyclic join; RF-59 sole-writer
enforcement plus kill-tree recovery as `UNDETERMINABLE` with no silent retry. This register resolves
the narrower historical wordings in ADR-0080 and ADR-0090 without weakening either decision.

---

## Delegation Digest and Measurement Decisions (`0091`–`0092`)

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0091` | [`0091-delegation-state-digest-extension.md`](0091-delegation-state-digest-extension.md) | Non-empty child state is canonical identity; empty maps preserve historical non-delegating digests. | accepted | 2026-08-24 |
| `0092` | [`0092-review-bundle-disposition-and-m7-measurement.md`](0092-review-bundle-disposition-and-m7-measurement.md) | Archived bundle remains non-production; context-store non-fix rejected; M7-01 authorized for measurement only. | accepted | 2026-08-24 |
| `0093` | [`0093-aether-higgs-v070-release-baseline.md`](0093-aether-higgs-v070-release-baseline.md) | **AETHER — Higgs Release Baseline:** ratifies v0.7.0 version baseline while preserving internal module structure (`vanguard/packages/`). **Milestone identifier semantics superseded by ADR-0095 §4**; release-baseline content retained. | accepted; identifiers amended by ADR-0095 | 2026-08-24 |

## Product-first M-4 (`0094`)

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0094` | [`0094-product-first-m4-and-optional-assurance.md`](0094-product-first-m4-and-optional-assurance.md) | RF-95 closes M-4 with a useful durable real-model coding run; RF-85 hermetic assurance is retained but no longer blocks product/generalization work. | accepted | 2026-08-25 |

---

## Vision as Law Zero (`0095`)

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0095` | [`0095-vision-as-law-zero-and-roadmap-reconciliation.md`](0095-vision-as-law-zero-and-roadmap-reconciliation.md) | **Authority hierarchy inverted to match the accepted architecture:** [`VISION.md`](../../VISION.md) becomes constitutional Law Zero; agent-as-projection ontology and milestone identities locked. M-5b/M-6 delivery sequencing is refined by ADR-0097 without changing milestone meaning. | accepted; sequencing refined by ADR-0097 | 2026-08-25 |

> **Precedence note.** Since ADR-0095, ADRs no longer outrank all general documentation without
> qualification: `VISION.md` sits above the law and the decision record. An ADR may refine how the
> Vision is realized; it may not contradict a locked Vision concept without an explicit
> Vision-superseding decision.

## Constitutional Evidence and Two-Lane Activation (`0096`–`0098`)

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0096` | [`0096-constitutional-correction-evidence-causal-invariants-and-falsifiers.md`](0096-constitutional-correction-evidence-causal-invariants-and-falsifiers.md) | **Evidence and falsifiability correction:** admissible counter-evidence, causal-history invariants, proof-honest reproducibility, strict `/2` schema evolution, evidence failure/degradation, privacy/capture separation, transitive TCB measurement, and RF-96…RF-100. | accepted v0.4.0 | 2026-08-25 |
| `0097` | [`0097-phase0-ratification-and-two-lane-activation.md`](0097-phase0-ratification-and-two-lane-activation.md) | **Execution activation:** ratifies the corrected package; authorizes two M-4 Senior lanes; records Linux RF-38…RF-45 qualification; permits M-5b/M-6 parallel work after M-5a; preserves historical `M-5-BASE` and allocates `M-5A-BASE-v2`. | accepted v0.2.0 | 2026-08-25 |
| `0098` | [`0098-event-substrate-v2-and-semantic-kind-roster.md`](0098-event-substrate-v2-and-semantic-kind-roster.md) | **Event substrate `/2`:** adds the four typed authority fields; folds the eight live legacy kinds into the generated schema and deletes `_V4_ONLY_KINDS`; freezes the deprecated-kind register and exactly five new semantic kinds; keeps goal content out of the ledger; sets the `M-5A-BASE-v2` creation criteria. | accepted v1.0.0 | 2026-08-26 |

---

## M-8 Contract and 2026 Convergence (`0100`–`0102`)

`0099` remains reserved for the scheduler disposition and has no accepted ADR until M7-01 evidence
exists. Numbering is append-only; reserving it does not authorize concurrency.

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0100` | [`0100-memory-learning-and-composition-lifecycle.md`](0100-memory-learning-and-composition-lifecycle.md) | **M-8 contract:** verified memory authorization, durable category isolation, retrieval provenance, legal hold/GC, immutable compositions, separated authorities, CAS promotion and real rollback. | accepted v1.0.0 | 2026-08-26 |
| `0101` | [`0101-receipt-backed-evidence-and-acceptance.md`](0101-receipt-backed-evidence-and-acceptance.md) | **Evidence method:** separates facts/artifacts/projections/telemetry/attestations; monotonic evidence and package states; independent receipt-backed acceptance; valid negative-result closure. | accepted v1.0.0 | 2026-08-26 |
| `0102` | [`0102-convergence-and-baseline-succession.md`](0102-convergence-and-baseline-succession.md) | **Convergence:** records `M-5A-BASE-v2` as contaminated/unpublished, resets unsupported claims, defines `CONVERGENCE-BASE-v1`, and retires parallel Leadership planning. | accepted v1.0.0 | 2026-08-26 |

---

## Repository Governance

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0086` | [`0086-historical-adr-working-tree-consolidation.md`](0086-historical-adr-working-tree-consolidation.md) | **Historical consolidation:** preserve old identifiers, summaries, and recovery commit while removing 81 superseded bodies from normal retrieval scope. | accepted | 2026-08-21 |
| `0087` | [`0087-documentation-topology-context-budgets-and-archive-boundary.md`](0087-documentation-topology-context-budgets-and-archive-boundary.md) | **Documentation topology:** authority-ordered directories, compact law index, context budgets, and `_archive/` boundary. | accepted | 2026-08-23 |

---

## M-3C to M-8 Concept Lock

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0088` | [`0088-m3c-m8-concept-lock.md`](0088-m3c-m8-concept-lock.md) | **Canonical foundation and scale seams:** one `/2 -> FrozenComposition -> ActivationPlan -> RunPlan` path; RF-85 assurance evidence; Formal Pack #2; generic-dispatch mediated spawn; reserved M-7/M-8 seams. Its M-4 exit dependency is superseded by ADR-0094; its **M-5…M-8 roadmap sequencing is superseded by ADR-0095** (concept-lock content on composition, identity, and refusals is retained). | accepted; M-4 gate amended by ADR-0094; sequencing amended by ADR-0095 | 2026-08-23 |

---

## Consolidated Historical Lineage

Full bodies in this section were removed from the default working tree by ADR-0086. Their IDs are
permanently reserved; the original bytes are recoverable at Git commit
`5b9966c24c13d0ffc4315a39a97870fd756324a9`. These summaries are provenance, not current
implementation authority. Current work cites SPEC/law leaves and ADRs 0069–0090.

<details>
<summary>M0 and pre-v0.6 decision ledger (expand for archaeology)</summary>

### ADR-M0 Namespace (Foundation Lock)

Decisions established during the M0 Foundation Lock.

| ADR | File | Subject | Status |
|---|---|---|---|
| `M0-01` | [`ADR-M0-01-control-coverage-discipline.md`](#consolidated-historical-lineage) | Control coverage and verification discipline | accepted |
| `M0-02` | [`ADR-M0-02-identifier-namespaces.md`](#consolidated-historical-lineage) | Identifier namespaces and UUID formats | accepted |
| `M0-03` | [`ADR-M0-03-five-spis.md`](#consolidated-historical-lineage) | Five standard Service Provider Interfaces (SPIs) | accepted |
| `M0-04` | [`ADR-M0-04-approved-stack.md`](#consolidated-historical-lineage) | Approved runtime technology stack | accepted |
| `M0-05` | [`ADR-M0-05-risk-register.md`](#consolidated-historical-lineage) | Foundation risk register | accepted |
| `M0-06` | [`ADR-M0-06-plane-mapping-archaeology.md`](#consolidated-historical-lineage) | Plane mapping and architectural archaeology | accepted |
| `M0-07` | [`ADR-M0-07-six-dimension-reservation.md`](#consolidated-historical-lineage) | Six-dimension budget reservation model (additive vs structural typed in `0074`) | accepted |
| `M0-08` | [`ADR-M0-08-k40-invert.md`](#consolidated-historical-lineage) | Kernel K-40 inversion handling | accepted |
| `M0-09` | [`ADR-M0-09-f21a-alarm.md`](#consolidated-historical-lineage) | F-21a alarm set and fail-closed thresholds | accepted |
| `M0-10` | [`ADR-M0-10-no-metaphysics.md`](#consolidated-historical-lineage) | Operational definitions over metaphysical claims | accepted |
| `M0-11` | [`ADR-M0-11-sink-class-mediation.md`](#consolidated-historical-lineage) | Sink class mediation (`pure`, `observation`, `privileged`) | accepted |
| `M0-12` | [`ADR-M0-12-tool-not-episode.md`](#consolidated-historical-lineage) | Tool execution separation from episode lifecycle | accepted |
| `M0-13` | [`ADR-M0-13-walking-skeleton.md`](#consolidated-historical-lineage) | Walking skeleton rule for extensibility verification | accepted |

---

### Pre-v0.6 Historical Decisions (`0000`–`0068`)

Historical decisions migrated from the Phase 0–3 registers.

| ADR | File | Original Topic / Domain | Status |
|---|---|---|---|
| `0000` | [`0000-adrs-are-append-only-numbered-and-each-states.md`](#consolidated-historical-lineage) | ADR discipline and append-only numbering | accepted |
| `0001` | [`0001-typescript-on-a-node-compatible-runtime-for-the.md`](#consolidated-historical-lineage) | TypeScript runtime for control plane | **reversed** (by `0063`, `0069`) |
| `0002` | [`0002-subprocess-with-line-delimited-json-as-the-seam.md`](#consolidated-historical-lineage) | Subprocess with line-delimited JSON RPC seam | accepted |
| `0003` | [`0003-agent-loop-primary-no-runtime-workflow-graph.md`](#consolidated-historical-lineage) | Agent loop as primary, no runtime workflow graph | accepted |
| `0004` | [`0004-the-verifier-is-immutable-and-unreachable-from-every.md`](#consolidated-historical-lineage) | Immutable exterior verifier | accepted |
| `0005` | [`0005-no-runtime-extension-discovery-registries-freeze-at-composition.md`](#consolidated-historical-lineage) | Registries freeze at composition; no runtime discovery | accepted |
| `0006` | [`0006-no-systems-language-components-in-phase-0-including.md`](#consolidated-historical-lineage) | No systems-language components in initial phase | accepted |
| `0007` | [`0007-parallel-independent-execution-from-the-first-loop-commit.md`](#consolidated-historical-lineage) | Parallel independent execution | deferred (D-38) |
| `0008` | [`0008-json-schema-2020-12-is-normative-a-typescript.md`](#consolidated-historical-lineage) | JSON Schema 2020-12 as normative contract | accepted |
| `0009` | [`0009-rfc-8785-canonicalisation-not-a-house-algorithm.md`](#consolidated-historical-lineage) | RFC 8785 canonical JSON algorithm | accepted |
| `0010` | [`0010-a-transactional-embedded-store-with-write-ahead-logging.md`](#consolidated-historical-lineage) | Transactional embedded store with WAL | accepted |
| `0011` | [`0011-capabilities-carry-resources-not-only-verbs.md`](#consolidated-historical-lineage) | Capabilities carry resources and actions | accepted |
| `0012` | [`0012-attenuation-denies-out-of-scope-requests-it-never.md`](#consolidated-historical-lineage) | Fail-closed capability attenuation | accepted |
| `0013` | [`0013-three-processes-in-phase-0-not-five.md`](#consolidated-historical-lineage) | Initial three-process architecture split | accepted |
| `0014` | [`0014-two-languages-at-the-first-contract-lock-not.md`](#consolidated-historical-lineage) | Two languages at contract lock | accepted |
| `0015` | [`0015-promotion-is-a-partial-order-over-a-frontier.md`](#consolidated-historical-lineage) | Artifact promotion as partial order | accepted |
| `0016` | [`0016-operators-are-data-in-the-competence-graph-not.md`](#consolidated-historical-lineage) | Operators as data representation | accepted |
| `0017` | [`0017-competence-is-a-graph-not-an-array.md`](#consolidated-historical-lineage) | Competence graph structure | accepted |
| `0018` | [`0018-invalidation-conditions-are-mandatory-and-non-empty.md`](#consolidated-historical-lineage) | Mandatory non-empty invalidation conditions | accepted |
| `0019` | [`0019-self-modification-is-a-release-pipeline-in-place.md`](#consolidated-historical-lineage) | Self-modification through formal release pipeline | accepted |
| `0020` | [`0020-vg-nn-document-identity-equals-the-file-index.md`](#consolidated-historical-lineage) | Document identity mapping | accepted |
| `0021` | [`0021-every-effect-passes-a-mediating-layer.md`](#consolidated-historical-lineage) | Every effect passes mediating layer | corrected |
| `0022` | [`0022-containment-reported-as-a-boolean.md`](#consolidated-historical-lineage) | Containment reported as boolean | accepted |
| `0023` | [`0023-a-size-ceiling-covering-the-trusted-computing-base.md`](#consolidated-historical-lineage) | Size ceiling covering Trusted Computing Base (TCB) | accepted |
| `0024` | [`0024-concurrency-safe-because-reads-precede-writes.md`](#consolidated-historical-lineage) | Read-preceding-write concurrency safety | accepted |
| `0025` | [`0025-a-dying-process-emits-a-terminal-event.md`](#consolidated-historical-lineage) | Terminal events on process termination | accepted |
| `0026` | [`0026-an-external-effect-always-resolves-to-success-or.md`](#consolidated-historical-lineage) | External effect resolution certainty | accepted |
| `0027` | [`0027-capability-widening-as-a-constant.md`](#consolidated-historical-lineage) | Capability widening constraints | accepted |
| `0028` | [`0028-justifying-spans-reset-each-turn.md`](#consolidated-historical-lineage) | Justifying spans reset per turn | accepted |
| `0029` | [`0029-read-only-mounts-protect-the-evaluator.md`](#consolidated-historical-lineage) | Read-only mounts protecting evaluator | accepted |
| `0030` | [`0030-a-passing-verdict-licenses-a-memory-write.md`](#consolidated-historical-lineage) | Passing verdict licensing memory writes | accepted |
| `0031` | [`0031-provider-errors-as-task-failures.md`](#consolidated-historical-lineage) | Model provider errors classified as task failures | accepted |
| `0032` | [`0032-schemas-strict-for-both-readers-and-writers.md`](#consolidated-historical-lineage) | Strict schema validation for readers and writers | accepted |
| `0033` | [`0033-vector-agreement-establishes-schema-equivalence.md`](#consolidated-historical-lineage) | Vector agreement establishing schema equivalence | accepted |
| `0034` | [`0034-an-architecture-test-requiring-four-process-identities-in.md`](#consolidated-historical-lineage) | Architecture tests requiring process identities | accepted |
| `0035` | [`0035-five-process-split.md`](#consolidated-historical-lineage) | Five-process split deferral | accepted |
| `0036` | [`0036-third-language-conformance-vectors.md`](#consolidated-historical-lineage) | Polyglot conformance vectors | accepted |
| `0037` | [`0037-memory-write-gating-tests.md`](#consolidated-historical-lineage) | Memory write gating tests | accepted |
| `0038` | [`0038-schema-locked-status.md`](#consolidated-historical-lineage) | Schema locked status | accepted |
| `0039` | [`0039-a-grant-carrying-no-descriptor.md`](#consolidated-historical-lineage) | Grants without descriptors rejected | accepted |
| `0040` | [`0040-resources-are-a-subset-with-no-decision-procedure.md`](#consolidated-historical-lineage) | Resource subset matching | accepted |
| `0041` | [`0041-a-mutable-timestamp-inside-a-content-addressed-artifact.md`](#consolidated-historical-lineage) | Content-addressed artifact timestamps | accepted |
| `0042` | [`0042-invalidation-satisfiable-with-only-manual-conditions.md`](#consolidated-historical-lineage) | Invalidation conditions | accepted |
| `0043` | [`0043-every-event-bound-to-an-episode.md`](#consolidated-historical-lineage) | Events bound to episode context | accepted |
| `0044` | [`0044-a-single-trailing-emit-point.md`](#consolidated-historical-lineage) | Single trailing event emit point | accepted |
| `0045` | [`0045-new-decisions-use-the-expanded-fields-required-by.md`](#consolidated-historical-lineage) | Expanded decision fields | accepted |
| `0046` | [`0046-gts-13c-is-the-sole-active-programme-plan.md`](#consolidated-historical-lineage) | GTS-13C programme adoption | accepted |
| `0047` | [`0047-spike-and-slice-are-disposable-consumers-only-may.md`](#consolidated-historical-lineage) | Disposable spikes and slices | accepted |
| `0048` | [`0048-the-s4-trust-spine-gate-runs-a-scripted.md`](#consolidated-historical-lineage) | Trust spine gate scripting | accepted |
| `0049` | [`0049-shipped-tools-begin-as-typed-read-search-patch.md`](#consolidated-historical-lineage) | Standard shipped toolset primitives | accepted |
| `0050` | [`0050-effects-are-execution-primitives-episodes-coordinate-open-ended.md`](#consolidated-historical-lineage) | Effects as execution primitives | accepted |
| `0051` | [`0051-every-effect-is-attributed-and-recorded-only-privileged.md`](#consolidated-historical-lineage) | Effect attribution and recording | accepted |
| `0052` | [`0052-the-active-mvp-contract-has-two-independent-100.md`](#consolidated-historical-lineage) | MVP contract independence | accepted |
| `0053` | [`0053-no-implementation-pr-merges-before-the-governance-baseline.md`](#consolidated-historical-lineage) | Governance baseline before PR merges | accepted |
| `0054` | [`0054-implement-t2-dispatch-as-the-single-s0-s12.md`](#consolidated-historical-lineage) | S0–S12 13-stage dispatch pipeline | accepted |
| `0055` | [`0055-rebase-sprint-3-off-covered-t2-t3-s3.md`](#consolidated-historical-lineage) | Sprint 3 rebase | accepted |
| `0056` | [`0056-four-parallel-packets-mixed-complexity-startable-day-one.md`](#consolidated-historical-lineage) | Four parallel packets | accepted |
| `0057` | [`0057-beta-gts-13c-ch-10-q1-q2-at.md`](#consolidated-historical-lineage) | Beta GTS-13C milestone closure | accepted |
| `0058` | [`0058-authorize-phase-2-sprints-5-6-as-the.md`](#consolidated-historical-lineage) | Phase 2 authorization | accepted |
| `0059` | [`0059-polyglot-plugin-and-port-decoupling-via-standard-wire.md`](#consolidated-historical-lineage) | Standard wire decoupling for plugins/ports | accepted |
| `0060` | [`0060-the-domain-generality-invariant-the-microkernel-s0-s12.md`](#consolidated-historical-lineage) | Domain generality invariant (I-7) for microkernel | accepted |
| `0061` | [`0061-apply-specification-v0-4-1-v4b-patches-before.md`](#consolidated-historical-lineage) | v0.4.1 v4b patches application | accepted |
| `0062` | [`0062-implement-unix-domain-socket-runtimeservice-daemon-and-asymmetric.md`](#consolidated-historical-lineage) | UDS RuntimeService daemon & CLI streaming protocol | accepted |
| `0063` | [`0063-the-control-plane-is-python-adr-0001-typescript.md`](#consolidated-historical-lineage) | Control plane is Python (reversing ADR-0001) | accepted |
| `0064` | [`0064-record-mvp-gate-status-at-0238b1a-q1-partially.md`](#consolidated-historical-lineage) | MVP gate recording | accepted |
| `0065` | [`0065-adopt-d-01-d-15-from-the-lam.md`](#consolidated-historical-lineage) | Adoption of decisions D-01 through D-15 | accepted |
| `0066` | [`0066-mcp-is-configuration-and-an-adapter-after-v0.md`](#consolidated-historical-lineage) | Model Context Protocol (MCP) as configuration/adapter | accepted |
| `0068` | [`0068-evidenceclaim-optional-hedge-fields-supportcount-lastcorroboratedat-protectionclass-writer.md`](#consolidated-historical-lineage) | EvidenceClaim optional hedge and protection fields | accepted |

> *Note on numbering:* `0067` is a documented historical numbering gap (no file exists).

</details>

---

## Canonical RF Falsifier Allocation Register

`F-*` remains the historical kernel-control namespace. Existing `F-*` identifiers are never
renamed or reassigned, and no new proposal requirement may allocate one. Ratified roadmap
falsifiers use `RF-*`.

| Historical control | Ratified requirement | Relationship |
|---|---|---|
| `F-12` | `RF-23` | `F-12` retains the structural `mhf.trajectory/1` schema/emission check. `RF-23` strengthens it with invoked-turn attribution, explicit measurement status, conserved cost, and identity content. This is an alias/lineage edge, not a rename; both tests remain. |

| RF allocation | Owner | Locked subject / milestone |
|---|---|---|
| `RF-23`, `RF-24`, `RF-27` | ADR-0078 | NOVA-1 trajectory content, writer authority, and identity separation / M-2 |
| `RF-25` | ADR-0082 | NOVA-2 true fresh-process cold continuation / M-2 |
| `RF-26` | ADR-0080 + ADR-0067 | Sealed action membership remains denied when the engine pre-filter is bypassed / current behavior |
| `RF-28`–`RF-33` | ADR-0077 | Named Component Graph compilation and identity / M-3 |
| `RF-34`–`RF-37` | ADR-0079 | Absent-vs-forged and derived promotability / M-3–M-5 |
| `RF-38`–`RF-45` | ADR-0081 | Plugin lifecycle parity and NOVA-4 Layer-0 retirement / M-3 |
| `RF-46`–`RF-48` | ADR-0083 | Pareto profile identity, authority, and reservation / M-3 and M-7 |
| `RF-52`–`RF-53` | ADR-0084 | Attributable witness memo / M-5 |
| `RF-55`–`RF-59` | ADR-0080 + ADR-0090 | Conjunctive mediated-spawn gate: grant/no-child denial; durable idempotent intent and attenuation; declared target plus four-dimensional conservation and structural ceilings; evaluator-authorized typed acyclic join; sole writer plus kill-tree `UNDETERMINABLE` recovery / M-6 |
| `RF-65`–`RF-66` | ADR-0082 | Advanced topology fitness and the universal-loop challenge / M-8 |
| `RF-67`–`RF-70` | ADR-0084 | Macro least privilege, dispatch, and exact promotion / M-9–M-10 |
| `RF-72` | ADR-0082 | Identifier uniqueness linter and this one-time historical alias table / governance |
| `RF-73`–`RF-75` | ADR-0085 | Reservation identity, inert refusal, and ADR reversal-condition lint / staged milestones |
| `RF-76` | ADR-0082 | Compatibility-reader fidelity for supported old WAL rows / M-3 |
| `RF-77` | ADR-0082 | Index deletion and rebuild from immutable artifacts / M-9 |
| `RF-78`–`RF-84` | ADR-0088 | Canonical public composition/activation, domain bindings, release durability, evidence derivation, and authority retirement / M-3C |
| `RF-85` | ADR-0088 + ADR-0094 | Optional uninterrupted nine-row hermetic assurance certification; no longer the M-4 exit gate |
| `RF-86` | ADR-0088 | Formal Pack #2 parity with unchanged substrate / M-5 |
| `RF-87`–`RF-94` | ADR-0089 | Execution profile identity, fail-closed assurance, capability qualification, generic entrypoint, shared tools, event streaming, real activation, and single runtime authority / W-3D |
| `RF-95` | ADR-0094 | Real-model, durable, resumable product coding run / M-4 |
| `RF-96`–`RF-100` | ADR-0096 | Cold reconstruction, transitive multidimensional Trusted Core Budget, Kernel Neutrality Gate, authority provenance, and proof-honest computed reproducibility / M-4 (RF-100 capture and run-close assessment) through M-5b. |

RF-72 requires `tools/linters/check_falsifier_ids.py` to reject duplicate or semantically
conflicting allocations across accepted ADRs, SPEC, this register, and the active board. The linter
must expand inclusive ranges, permit repeated citations of the same allocation, and validate the
single `F-12` -> `RF-23` lineage row above. Unlisted IDs remain unallocated; adjacency grants no
meaning.

---

## Companion Registers & Governance Documents

- [`DEFERRED_REJECTED.md`](DEFERRED_REJECTED.md) — Comprehensive register of capabilities deferred to later phases or rejected with rationale.
- [`DRIFT_REGISTER_v045.md`](DRIFT_REGISTER_v045.md) — Forensic register of historical drifts identified and resolved.
- [`SPEC.md`](../SPEC.md) — Living normative specification (Vanguard Meta-Harness Framework).
- [`005_V061_SUBSTRATE_GENERALITY_REVIEW.md`](../_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md) — historical substrate generality analysis.
- [`004_V061_ALIGNMENT_ROADMAP.md`](../_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/004_V061_ALIGNMENT_ROADMAP.md) — historical v0.6.1 alignment roadmap.
