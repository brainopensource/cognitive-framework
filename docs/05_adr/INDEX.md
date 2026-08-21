# ADR Index — Architecture Decision Records

> **Status:** Living Master Index of Architecture Decision Records for Vanguard / AETHER.  
> **Rule:** Append-only numbering. ADRs outrank general documentation; newer ADRs supersede older ones by explicit citation (e.g., ADR-0069 reverses ADR-0001; ADR-0076 canonicalizes execution artifacts; ADR-0077–0084 ratify the Tier S+ evolution contract).  
> **Companion Documents:** [`DEFERRED_REJECTED.md`](DEFERRED_REJECTED.md) · [`DRIFT_REGISTER_v045.md`](DRIFT_REGISTER_v045.md) · [`SPEC.md`](../SPEC.md) · [`sprint_active.md`](../03_sprints/sprint_active.md).

---

## Quick Navigation

- 🚀 [v0.6.0 Concept Lock & Foundation Execution (`0069`–`0076`)](#v060-concept-lock--foundation-execution-canonical-law) — **Start here for active production law**
- 🧭 [Tier S+ Evolution Contract (`0077`–`0084`)](#tier-s-evolution-contract-00770084) — **Ratified v0.6.1→v1.0 design and phased implementation law**
- 🛡️ [ADR-M0 Namespace (`M0-01`–`M0-13`)](#adr-m0-namespace-foundation-lock) — M0 Foundation Lock decisions
- 📜 [Pre-v0.6 Historical Decisions (`0000`–`0068`)](#pre-v06-historical-decisions-00000068) — Lineage and historical evolution
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

## Tier S+ Evolution Contract (`0077`–`0084`)

The Engineering Director ratified this catalog on **2026-08-21**. These ADRs are binding design
law, but their implementation remains limited by the milestone named in each record. In
particular, acceptance does not authorize M-3–M-10 production work before its entry gate. This
table is the canonical numbering map and supersedes conflicting maps in advisory proposal files.

| ADR | File & Title | Scope & Key Decisions | Status | Accepted |
|---|---|---|---|---|
| `0077` | [`0077-named-component-graph-manifest.md`](0077-named-component-graph-manifest.md) | **Named Component Graph:** `mhf.manifest/2`, typed bindings, one semantic compiler, complete graph identity in $D_H$; implementation at M-3. | accepted | 2026-08-21 |
| `0078` | [`0078-trajectory-un-hollowing-cost-accounting.md`](0078-trajectory-un-hollowing-cost-accounting.md) | **NOVA-1:** non-breaking `mhf.trajectory/1` content strengthening, explicit missingness, conserved cost, $D_R/D_X$, derived legacy exclusion; immediate RF-23 M-2 gate. | accepted | 2026-08-21 |
| `0079` | [`0079-absent-vs-forged-derived-promotability.md`](0079-absent-vs-forged-derived-promotability.md) | **Absent vs Forged:** three evidence states; declared absence enters $D_H$; promotability is derived and never author-writable. | accepted | 2026-08-21 |
| `0080` | [`0080-capability-mediated-agent-spawn-design-freeze.md`](0080-capability-mediated-agent-spawn-design-freeze.md) | **Mediated `agent.spawn`:** design frozen now; S0–S12 implementation deferred to M-6 after M-4/M-5. | accepted; implementation deferred | 2026-08-21 |
| `0081` | [`0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md`](0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md) | **Lifecycle and convergence:** add `PluginDiscovered`/`PluginVerified`; absorb registry/compose; NOVA-4; atomic Layer-0/package/CI deletion at M-3. | accepted | 2026-08-21 |
| `0082` | [`0082-universal-turn-loop-m10-compatibility-contract.md`](0082-universal-turn-loop-m10-compatibility-contract.md) | **Universal mechanism and M-10 compatibility:** RF-25 cold continuation plus twelve stable substrate seams for graph, authority, state, evidence, identity, data, ports, schemas, and promotion. | accepted | 2026-08-21 |
| `0083` | [`0083-dynamic-pareto-controller-profile-matrix.md`](0083-dynamic-pareto-controller-profile-matrix.md) | **Dynamic Pareto profiles:** alpha/beta/gamma/delta as composition policy; feasibility first; schema M-3, controller activation M-7. | accepted; activation deferred | 2026-08-21 |
| `0084` | [`0084-compounding-macro-tools-active-inference.md`](0084-compounding-macro-tools-active-inference.md) | **Compounding and Active Inference:** T0 witness memo at M-5; least-privilege macro lab M-9; VFE/EFE, DPO, exact paired promotion M-10. | accepted; phased implementation | 2026-08-21 |

**Immediate authorization boundary.** For M-2/v0.6.1, the newly active implementation gates are
only ADR-0078/RF-23 and ADR-0082/RF-25. The other accepted ADRs constrain future design and do not
self-authorize their deferred code.

---

## ADR-M0 Namespace (Foundation Lock)

Decisions established during the M0 Foundation Lock (cannot collide with `0000+`).

| ADR | File | Subject | Status |
|---|---|---|---|
| `M0-01` | [`ADR-M0-01-control-coverage-discipline.md`](ADR-M0-01-control-coverage-discipline.md) | Control coverage and verification discipline | accepted |
| `M0-02` | [`ADR-M0-02-identifier-namespaces.md`](ADR-M0-02-identifier-namespaces.md) | Identifier namespaces and UUID formats | accepted |
| `M0-03` | [`ADR-M0-03-five-spis.md`](ADR-M0-03-five-spis.md) | Five standard Service Provider Interfaces (SPIs) | accepted |
| `M0-04` | [`ADR-M0-04-approved-stack.md`](ADR-M0-04-approved-stack.md) | Approved runtime technology stack | accepted |
| `M0-05` | [`ADR-M0-05-risk-register.md`](ADR-M0-05-risk-register.md) | Foundation risk register | accepted |
| `M0-06` | [`ADR-M0-06-plane-mapping-archaeology.md`](ADR-M0-06-plane-mapping-archaeology.md) | Plane mapping and architectural archaeology | accepted |
| `M0-07` | [`ADR-M0-07-six-dimension-reservation.md`](ADR-M0-07-six-dimension-reservation.md) | Six-dimension budget reservation model (additive vs structural typed in `0074`) | accepted |
| `M0-08` | [`ADR-M0-08-k40-invert.md`](ADR-M0-08-k40-invert.md) | Kernel K-40 inversion handling | accepted |
| `M0-09` | [`ADR-M0-09-f21a-alarm.md`](ADR-M0-09-f21a-alarm.md) | F-21a alarm set and fail-closed thresholds | accepted |
| `M0-10` | [`ADR-M0-10-no-metaphysics.md`](ADR-M0-10-no-metaphysics.md) | Operational definitions over metaphysical claims | accepted |
| `M0-11` | [`ADR-M0-11-sink-class-mediation.md`](ADR-M0-11-sink-class-mediation.md) | Sink class mediation (`pure`, `observation`, `privileged`) | accepted |
| `M0-12` | [`ADR-M0-12-tool-not-episode.md`](ADR-M0-12-tool-not-episode.md) | Tool execution separation from episode lifecycle | accepted |
| `M0-13` | [`ADR-M0-13-walking-skeleton.md`](ADR-M0-13-walking-skeleton.md) | Walking skeleton rule for extensibility verification | accepted |

---

## Pre-v0.6 Historical Decisions (`0000`–`0068`)

Historical decisions migrated from the Phase 0–3 registers.

| ADR | File | Original Topic / Domain | Status |
|---|---|---|---|
| `0000` | [`0000-adrs-are-append-only-numbered-and-each-states.md`](0000-adrs-are-append-only-numbered-and-each-states.md) | ADR discipline and append-only numbering | accepted |
| `0001` | [`0001-typescript-on-a-node-compatible-runtime-for-the.md`](0001-typescript-on-a-node-compatible-runtime-for-the.md) | TypeScript runtime for control plane | **reversed** (by `0063`, `0069`) |
| `0002` | [`0002-subprocess-with-line-delimited-json-as-the-seam.md`](0002-subprocess-with-line-delimited-json-as-the-seam.md) | Subprocess with line-delimited JSON RPC seam | accepted |
| `0003` | [`0003-agent-loop-primary-no-runtime-workflow-graph.md`](0003-agent-loop-primary-no-runtime-workflow-graph.md) | Agent loop as primary, no runtime workflow graph | accepted |
| `0004` | [`0004-the-verifier-is-immutable-and-unreachable-from-every.md`](0004-the-verifier-is-immutable-and-unreachable-from-every.md) | Immutable exterior verifier | accepted |
| `0005` | [`0005-no-runtime-extension-discovery-registries-freeze-at-composition.md`](0005-no-runtime-extension-discovery-registries-freeze-at-composition.md) | Registries freeze at composition; no runtime discovery | accepted |
| `0006` | [`0006-no-systems-language-components-in-phase-0-including.md`](0006-no-systems-language-components-in-phase-0-including.md) | No systems-language components in initial phase | accepted |
| `0007` | [`0007-parallel-independent-execution-from-the-first-loop-commit.md`](0007-parallel-independent-execution-from-the-first-loop-commit.md) | Parallel independent execution | deferred (D-38) |
| `0008` | [`0008-json-schema-2020-12-is-normative-a-typescript.md`](0008-json-schema-2020-12-is-normative-a-typescript.md) | JSON Schema 2020-12 as normative contract | accepted |
| `0009` | [`0009-rfc-8785-canonicalisation-not-a-house-algorithm.md`](0009-rfc-8785-canonicalisation-not-a-house-algorithm.md) | RFC 8785 canonical JSON algorithm | accepted |
| `0010` | [`0010-a-transactional-embedded-store-with-write-ahead-logging.md`](0010-a-transactional-embedded-store-with-write-ahead-logging.md) | Transactional embedded store with WAL | accepted |
| `0011` | [`0011-capabilities-carry-resources-not-only-verbs.md`](0011-capabilities-carry-resources-not-only-verbs.md) | Capabilities carry resources and actions | accepted |
| `0012` | [`0012-attenuation-denies-out-of-scope-requests-it-never.md`](0012-attenuation-denies-out-of-scope-requests-it-never.md) | Fail-closed capability attenuation | accepted |
| `0013` | [`0013-three-processes-in-phase-0-not-five.md`](0013-three-processes-in-phase-0-not-five.md) | Initial three-process architecture split | accepted |
| `0014` | [`0014-two-languages-at-the-first-contract-lock-not.md`](0014-two-languages-at-the-first-contract-lock-not.md) | Two languages at contract lock | accepted |
| `0015` | [`0015-promotion-is-a-partial-order-over-a-frontier.md`](0015-promotion-is-a-partial-order-over-a-frontier.md) | Artifact promotion as partial order | accepted |
| `0016` | [`0016-operators-are-data-in-the-competence-graph-not.md`](0016-operators-are-data-in-the-competence-graph-not.md) | Operators as data representation | accepted |
| `0017` | [`0017-competence-is-a-graph-not-an-array.md`](0017-competence-is-a-graph-not-an-array.md) | Competence graph structure | accepted |
| `0018` | [`0018-invalidation-conditions-are-mandatory-and-non-empty.md`](0018-invalidation-conditions-are-mandatory-and-non-empty.md) | Mandatory non-empty invalidation conditions | accepted |
| `0019` | [`0019-self-modification-is-a-release-pipeline-in-place.md`](0019-self-modification-is-a-release-pipeline-in-place.md) | Self-modification through formal release pipeline | accepted |
| `0020` | [`0020-vg-nn-document-identity-equals-the-file-index.md`](0020-vg-nn-document-identity-equals-the-file-index.md) | Document identity mapping | accepted |
| `0021` | [`0021-every-effect-passes-a-mediating-layer.md`](0021-every-effect-passes-a-mediating-layer.md) | Every effect passes mediating layer | corrected |
| `0022` | [`0022-containment-reported-as-a-boolean.md`](0022-containment-reported-as-a-boolean.md) | Containment reported as boolean | accepted |
| `0023` | [`0023-a-size-ceiling-covering-the-trusted-computing-base.md`](0023-a-size-ceiling-covering-the-trusted-computing-base.md) | Size ceiling covering Trusted Computing Base (TCB) | accepted |
| `0024` | [`0024-concurrency-safe-because-reads-precede-writes.md`](0024-concurrency-safe-because-reads-precede-writes.md) | Read-preceding-write concurrency safety | accepted |
| `0025` | [`0025-a-dying-process-emits-a-terminal-event.md`](0025-a-dying-process-emits-a-terminal-event.md) | Terminal events on process termination | accepted |
| `0026` | [`0026-an-external-effect-always-resolves-to-success-or.md`](0026-an-external-effect-always-resolves-to-success-or.md) | External effect resolution certainty | accepted |
| `0027` | [`0027-capability-widening-as-a-constant.md`](0027-capability-widening-as-a-constant.md) | Capability widening constraints | accepted |
| `0028` | [`0028-justifying-spans-reset-each-turn.md`](0028-justifying-spans-reset-each-turn.md) | Justifying spans reset per turn | accepted |
| `0029` | [`0029-read-only-mounts-protect-the-evaluator.md`](0029-read-only-mounts-protect-the-evaluator.md) | Read-only mounts protecting evaluator | accepted |
| `0030` | [`0030-a-passing-verdict-licenses-a-memory-write.md`](0030-a-passing-verdict-licenses-a-memory-write.md) | Passing verdict licensing memory writes | accepted |
| `0031` | [`0031-provider-errors-as-task-failures.md`](0031-provider-errors-as-task-failures.md) | Model provider errors classified as task failures | accepted |
| `0032` | [`0032-schemas-strict-for-both-readers-and-writers.md`](0032-schemas-strict-for-both-readers-and-writers.md) | Strict schema validation for readers and writers | accepted |
| `0033` | [`0033-vector-agreement-establishes-schema-equivalence.md`](0033-vector-agreement-establishes-schema-equivalence.md) | Vector agreement establishing schema equivalence | accepted |
| `0034` | [`0034-an-architecture-test-requiring-four-process-identities-in.md`](0034-an-architecture-test-requiring-four-process-identities-in.md) | Architecture tests requiring process identities | accepted |
| `0035` | [`0035-five-process-split.md`](0035-five-process-split.md) | Five-process split deferral | accepted |
| `0036` | [`0036-third-language-conformance-vectors.md`](0036-third-language-conformance-vectors.md) | Polyglot conformance vectors | accepted |
| `0037` | [`0037-memory-write-gating-tests.md`](0037-memory-write-gating-tests.md) | Memory write gating tests | accepted |
| `0038` | [`0038-schema-locked-status.md`](0038-schema-locked-status.md) | Schema locked status | accepted |
| `0039` | [`0039-a-grant-carrying-no-descriptor.md`](0039-a-grant-carrying-no-descriptor.md) | Grants without descriptors rejected | accepted |
| `0040` | [`0040-resources-are-a-subset-with-no-decision-procedure.md`](0040-resources-are-a-subset-with-no-decision-procedure.md) | Resource subset matching | accepted |
| `0041` | [`0041-a-mutable-timestamp-inside-a-content-addressed-artifact.md`](0041-a-mutable-timestamp-inside-a-content-addressed-artifact.md) | Content-addressed artifact timestamps | accepted |
| `0042` | [`0042-invalidation-satisfiable-with-only-manual-conditions.md`](0042-invalidation-satisfiable-with-only-manual-conditions.md) | Invalidation conditions | accepted |
| `0043` | [`0043-every-event-bound-to-an-episode.md`](0043-every-event-bound-to-an-episode.md) | Events bound to episode context | accepted |
| `0044` | [`0044-a-single-trailing-emit-point.md`](0044-a-single-trailing-emit-point.md) | Single trailing event emit point | accepted |
| `0045` | [`0045-new-decisions-use-the-expanded-fields-required-by.md`](0045-new-decisions-use-the-expanded-fields-required-by.md) | Expanded decision fields | accepted |
| `0046` | [`0046-gts-13c-is-the-sole-active-programme-plan.md`](0046-gts-13c-is-the-sole-active-programme-plan.md) | GTS-13C programme adoption | accepted |
| `0047` | [`0047-spike-and-slice-are-disposable-consumers-only-may.md`](0047-spike-and-slice-are-disposable-consumers-only-may.md) | Disposable spikes and slices | accepted |
| `0048` | [`0048-the-s4-trust-spine-gate-runs-a-scripted.md`](0048-the-s4-trust-spine-gate-runs-a-scripted.md) | Trust spine gate scripting | accepted |
| `0049` | [`0049-shipped-tools-begin-as-typed-read-search-patch.md`](0049-shipped-tools-begin-as-typed-read-search-patch.md) | Standard shipped toolset primitives | accepted |
| `0050` | [`0050-effects-are-execution-primitives-episodes-coordinate-open-ended.md`](0050-effects-are-execution-primitives-episodes-coordinate-open-ended.md) | Effects as execution primitives | accepted |
| `0051` | [`0051-every-effect-is-attributed-and-recorded-only-privileged.md`](0051-every-effect-is-attributed-and-recorded-only-privileged.md) | Effect attribution and recording | accepted |
| `0052` | [`0052-the-active-mvp-contract-has-two-independent-100.md`](0052-the-active-mvp-contract-has-two-independent-100.md) | MVP contract independence | accepted |
| `0053` | [`0053-no-implementation-pr-merges-before-the-governance-baseline.md`](0053-no-implementation-pr-merges-before-the-governance-baseline.md) | Governance baseline before PR merges | accepted |
| `0054` | [`0054-implement-t2-dispatch-as-the-single-s0-s12.md`](0054-implement-t2-dispatch-as-the-single-s0-s12.md) | S0–S12 13-stage dispatch pipeline | accepted |
| `0055` | [`0055-rebase-sprint-3-off-covered-t2-t3-s3.md`](0055-rebase-sprint-3-off-covered-t2-t3-s3.md) | Sprint 3 rebase | accepted |
| `0056` | [`0056-four-parallel-packets-mixed-complexity-startable-day-one.md`](0056-four-parallel-packets-mixed-complexity-startable-day-one.md) | Four parallel packets | accepted |
| `0057` | [`0057-beta-gts-13c-ch-10-q1-q2-at.md`](0057-beta-gts-13c-ch-10-q1-q2-at.md) | Beta GTS-13C milestone closure | accepted |
| `0058` | [`0058-authorize-phase-2-sprints-5-6-as-the.md`](0058-authorize-phase-2-sprints-5-6-as-the.md) | Phase 2 authorization | accepted |
| `0059` | [`0059-polyglot-plugin-and-port-decoupling-via-standard-wire.md`](0059-polyglot-plugin-and-port-decoupling-via-standard-wire.md) | Standard wire decoupling for plugins/ports | accepted |
| `0060` | [`0060-the-domain-generality-invariant-the-microkernel-s0-s12.md`](0060-the-domain-generality-invariant-the-microkernel-s0-s12.md) | Domain generality invariant (I-7) for microkernel | accepted |
| `0061` | [`0061-apply-specification-v0-4-1-v4b-patches-before.md`](0061-apply-specification-v0-4-1-v4b-patches-before.md) | v0.4.1 v4b patches application | accepted |
| `0062` | [`0062-implement-unix-domain-socket-runtimeservice-daemon-and-asymmetric.md`](0062-implement-unix-domain-socket-runtimeservice-daemon-and-asymmetric.md) | UDS RuntimeService daemon & CLI streaming protocol | accepted |
| `0063` | [`0063-the-control-plane-is-python-adr-0001-typescript.md`](0063-the-control-plane-is-python-adr-0001-typescript.md) | Control plane is Python (reversing ADR-0001) | accepted |
| `0064` | [`0064-record-mvp-gate-status-at-0238b1a-q1-partially.md`](0064-record-mvp-gate-status-at-0238b1a-q1-partially.md) | MVP gate recording | accepted |
| `0065` | [`0065-adopt-d-01-d-15-from-the-lam.md`](0065-adopt-d-01-d-15-from-the-lam.md) | Adoption of decisions D-01 through D-15 | accepted |
| `0066` | [`0066-mcp-is-configuration-and-an-adapter-after-v0.md`](0066-mcp-is-configuration-and-an-adapter-after-v0.md) | Model Context Protocol (MCP) as configuration/adapter | accepted |
| `0068` | [`0068-evidenceclaim-optional-hedge-fields-supportcount-lastcorroboratedat-protectionclass-writer.md`](0068-evidenceclaim-optional-hedge-fields-supportcount-lastcorroboratedat-protectionclass-writer.md) | EvidenceClaim optional hedge and protection fields | accepted |

> *Note on numbering:* `0067` is a documented historical numbering gap (no file exists).

---

## Companion Registers & Governance Documents

- [`DEFERRED_REJECTED.md`](DEFERRED_REJECTED.md) — Comprehensive register of capabilities deferred to later phases or rejected with rationale.
- [`DRIFT_REGISTER_v045.md`](DRIFT_REGISTER_v045.md) — Forensic register of historical drifts identified and resolved.
- [`SPEC.md`](../SPEC.md) — Living normative specification (Vanguard Meta-Harness Framework).
- [`005_V061_SUBSTRATE_GENERALITY_REVIEW.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md) — Substrate generality analysis and v0.6.1 recommendations.
- [`004_V061_ALIGNMENT_ROADMAP.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/004_V061_ALIGNMENT_ROADMAP.md) — v0.6.1 alignment and M-2 through M-10 execution roadmap.
