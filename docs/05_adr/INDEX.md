# ADR Index (migrated from VG-09 `09_vanguard_decision_register_v040.md`)

> Append-only. Original ADR numbers preserved in front-matter `adr:` field (no renumbering — the
> `ADR-M0-*` namespace below is separate and cannot collide). Migrated mechanically per
> `docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md` §1.12. Source: `docs/archive/v045/01_specs/backend/09_vanguard_decision_register_v040.md`.

| ADR | File | Section | Status |
|---|---|---|---|
| `0000` | [0000-adrs-are-append-only-numbered-and-each-states.md](0000-adrs-are-append-only-numbered-and-each-states.md) | 2. Foundational decisions | accepted |
| `0001` | [0001-typescript-on-a-node-compatible-runtime-for-the.md](0001-typescript-on-a-node-compatible-runtime-for-the.md) | 2. Foundational decisions | reversed |
| `0002` | [0002-subprocess-with-line-delimited-json-as-the-seam.md](0002-subprocess-with-line-delimited-json-as-the-seam.md) | 2. Foundational decisions | accepted |
| `0003` | [0003-agent-loop-primary-no-runtime-workflow-graph.md](0003-agent-loop-primary-no-runtime-workflow-graph.md) | 2. Foundational decisions | accepted |
| `0004` | [0004-the-verifier-is-immutable-and-unreachable-from-every.md](0004-the-verifier-is-immutable-and-unreachable-from-every.md) | 2. Foundational decisions | accepted |
| `0005` | [0005-no-runtime-extension-discovery-registries-freeze-at-composition.md](0005-no-runtime-extension-discovery-registries-freeze-at-composition.md) | 2. Foundational decisions | accepted |
| `0006` | [0006-no-systems-language-components-in-phase-0-including.md](0006-no-systems-language-components-in-phase-0-including.md) | 2. Foundational decisions | accepted |
| `0007` | [0007-parallel-independent-execution-from-the-first-loop-commit.md](0007-parallel-independent-execution-from-the-first-loop-commit.md) | 2. Foundational decisions | deferred (honoured, D-38) |
| `0008` | [0008-json-schema-2020-12-is-normative-a-typescript.md](0008-json-schema-2020-12-is-normative-a-typescript.md) | 3. Adjudications between the two lineages | accepted |
| `0009` | [0009-rfc-8785-canonicalisation-not-a-house-algorithm.md](0009-rfc-8785-canonicalisation-not-a-house-algorithm.md) | 3. Adjudications between the two lineages | accepted |
| `0010` | [0010-a-transactional-embedded-store-with-write-ahead-logging.md](0010-a-transactional-embedded-store-with-write-ahead-logging.md) | 3. Adjudications between the two lineages | accepted |
| `0011` | [0011-capabilities-carry-resources-not-only-verbs.md](0011-capabilities-carry-resources-not-only-verbs.md) | 3. Adjudications between the two lineages | accepted |
| `0012` | [0012-attenuation-denies-out-of-scope-requests-it-never.md](0012-attenuation-denies-out-of-scope-requests-it-never.md) | 3. Adjudications between the two lineages | accepted |
| `0013` | [0013-three-processes-in-phase-0-not-five.md](0013-three-processes-in-phase-0-not-five.md) | 3. Adjudications between the two lineages | accepted |
| `0014` | [0014-two-languages-at-the-first-contract-lock-not.md](0014-two-languages-at-the-first-contract-lock-not.md) | 3. Adjudications between the two lineages | accepted |
| `0015` | [0015-promotion-is-a-partial-order-over-a-frontier.md](0015-promotion-is-a-partial-order-over-a-frontier.md) | 3. Adjudications between the two lineages | accepted |
| `0016` | [0016-operators-are-data-in-the-competence-graph-not.md](0016-operators-are-data-in-the-competence-graph-not.md) | 3. Adjudications between the two lineages | accepted |
| `0017` | [0017-competence-is-a-graph-not-an-array.md](0017-competence-is-a-graph-not-an-array.md) | 3. Adjudications between the two lineages | accepted |
| `0018` | [0018-invalidation-conditions-are-mandatory-and-non-empty.md](0018-invalidation-conditions-are-mandatory-and-non-empty.md) | 3. Adjudications between the two lineages | accepted |
| `0019` | [0019-self-modification-is-a-release-pipeline-in-place.md](0019-self-modification-is-a-release-pipeline-in-place.md) | 3. Adjudications between the two lineages | accepted |
| `0020` | [0020-vg-nn-document-identity-equals-the-file-index.md](0020-vg-nn-document-identity-equals-the-file-index.md) | 3. Adjudications between the two lineages | accepted |
| `0021` | [0021-every-effect-passes-a-mediating-layer.md](0021-every-effect-passes-a-mediating-layer.md) | 4. Corrections | corrected |
| `0022` | [0022-containment-reported-as-a-boolean.md](0022-containment-reported-as-a-boolean.md) | 4. Corrections | accepted |
| `0023` | [0023-a-size-ceiling-covering-the-trusted-computing-base.md](0023-a-size-ceiling-covering-the-trusted-computing-base.md) | 4. Corrections | accepted |
| `0024` | [0024-concurrency-safe-because-reads-precede-writes.md](0024-concurrency-safe-because-reads-precede-writes.md) | 4. Corrections | accepted |
| `0025` | [0025-a-dying-process-emits-a-terminal-event.md](0025-a-dying-process-emits-a-terminal-event.md) | 4. Corrections | accepted |
| `0026` | [0026-an-external-effect-always-resolves-to-success-or.md](0026-an-external-effect-always-resolves-to-success-or.md) | 4. Corrections | accepted |
| `0027` | [0027-capability-widening-as-a-constant.md](0027-capability-widening-as-a-constant.md) | 4. Corrections | accepted |
| `0028` | [0028-justifying-spans-reset-each-turn.md](0028-justifying-spans-reset-each-turn.md) | 4. Corrections | accepted |
| `0029` | [0029-read-only-mounts-protect-the-evaluator.md](0029-read-only-mounts-protect-the-evaluator.md) | 4. Corrections | accepted |
| `0030` | [0030-a-passing-verdict-licenses-a-memory-write.md](0030-a-passing-verdict-licenses-a-memory-write.md) | 4. Corrections | accepted |
| `0031` | [0031-provider-errors-as-task-failures.md](0031-provider-errors-as-task-failures.md) | 4. Corrections | accepted |
| `0032` | [0032-schemas-strict-for-both-readers-and-writers.md](0032-schemas-strict-for-both-readers-and-writers.md) | 4. Corrections | accepted |
| `0033` | [0033-vector-agreement-establishes-schema-equivalence.md](0033-vector-agreement-establishes-schema-equivalence.md) | 4. Corrections | accepted |
| `0034` | [0034-an-architecture-test-requiring-four-process-identities-in.md](0034-an-architecture-test-requiring-four-process-identities-in.md) | 4. Corrections | accepted |
| `0039` | [0039-a-grant-carrying-no-descriptor.md](0039-a-grant-carrying-no-descriptor.md) | 4. Corrections | accepted |
| `0040` | [0040-resources-are-a-subset-with-no-decision-procedure.md](0040-resources-are-a-subset-with-no-decision-procedure.md) | 4. Corrections | accepted |
| `0041` | [0041-a-mutable-timestamp-inside-a-content-addressed-artifact.md](0041-a-mutable-timestamp-inside-a-content-addressed-artifact.md) | 4. Corrections | accepted |
| `0042` | [0042-invalidation-satisfiable-with-only-manual-conditions.md](0042-invalidation-satisfiable-with-only-manual-conditions.md) | 4. Corrections | accepted |
| `0043` | [0043-every-event-bound-to-an-episode.md](0043-every-event-bound-to-an-episode.md) | 4. Corrections | accepted |
| `0044` | [0044-a-single-trailing-emit-point.md](0044-a-single-trailing-emit-point.md) | 4. Corrections | accepted |
| `0035` | [0035-five-process-split.md](0035-five-process-split.md) | 5. Deferred with a scheduled reversal | accepted |
| `0036` | [0036-third-language-conformance-vectors.md](0036-third-language-conformance-vectors.md) | 5. Deferred with a scheduled reversal | accepted |
| `0037` | [0037-memory-write-gating-tests.md](0037-memory-write-gating-tests.md) | 5. Deferred with a scheduled reversal | accepted |
| `0038` | [0038-schema-locked-status.md](0038-schema-locked-status.md) | 5. Deferred with a scheduled reversal | accepted |
| `0045` | [0045-new-decisions-use-the-expanded-fields-required-by.md](0045-new-decisions-use-the-expanded-fields-required-by.md) | 7. Sprint 0 adoption decisions | accepted |
| `0046` | [0046-gts-13c-is-the-sole-active-programme-plan.md](0046-gts-13c-is-the-sole-active-programme-plan.md) | 7. Sprint 0 adoption decisions | accepted |
| `0047` | [0047-spike-and-slice-are-disposable-consumers-only-may.md](0047-spike-and-slice-are-disposable-consumers-only-may.md) | 7. Sprint 0 adoption decisions | accepted |
| `0048` | [0048-the-s4-trust-spine-gate-runs-a-scripted.md](0048-the-s4-trust-spine-gate-runs-a-scripted.md) | 7. Sprint 0 adoption decisions | accepted |
| `0049` | [0049-shipped-tools-begin-as-typed-read-search-patch.md](0049-shipped-tools-begin-as-typed-read-search-patch.md) | 7. Sprint 0 adoption decisions | accepted |
| `0050` | [0050-effects-are-execution-primitives-episodes-coordinate-open-ended.md](0050-effects-are-execution-primitives-episodes-coordinate-open-ended.md) | 7. Sprint 0 adoption decisions | accepted |
| `0051` | [0051-every-effect-is-attributed-and-recorded-only-privileged.md](0051-every-effect-is-attributed-and-recorded-only-privileged.md) | 7. Sprint 0 adoption decisions | accepted |
| `0052` | [0052-the-active-mvp-contract-has-two-independent-100.md](0052-the-active-mvp-contract-has-two-independent-100.md) | 7. Sprint 0 adoption decisions | accepted |
| `0053` | [0053-no-implementation-pr-merges-before-the-governance-baseline.md](0053-no-implementation-pr-merges-before-the-governance-baseline.md) | 7. Sprint 0 adoption decisions | accepted |
| `0054` | [0054-implement-t2-dispatch-as-the-single-s0-s12.md](0054-implement-t2-dispatch-as-the-single-s0-s12.md) | 9. Kernel implementation decisions | accepted |
| `0055` | [0055-rebase-sprint-3-off-covered-t2-t3-s3.md](0055-rebase-sprint-3-off-covered-t2-t3-s3.md) | 10. Sprint 0–2 closure and Sprint 3–4 structure | accepted |
| `0056` | [0056-four-parallel-packets-mixed-complexity-startable-day-one.md](0056-four-parallel-packets-mixed-complexity-startable-day-one.md) | 10. Sprint 0–2 closure and Sprint 3–4 structure | accepted |
| `0057` | [0057-beta-gts-13c-ch-10-q1-q2-at.md](0057-beta-gts-13c-ch-10-q1-q2-at.md) | 10. Sprint 0–2 closure and Sprint 3–4 structure | accepted |
| `0058` | [0058-authorize-phase-2-sprints-5-6-as-the.md](0058-authorize-phase-2-sprints-5-6-as-the.md) | 11. Sprint 3–4 closure and Phase 2 authorization | accepted |
| `0059` | [0059-polyglot-plugin-and-port-decoupling-via-standard-wire.md](0059-polyglot-plugin-and-port-decoupling-via-standard-wire.md) | 11. Sprint 3–4 closure and Phase 2 authorization | accepted |
| `0060` | [0060-the-domain-generality-invariant-the-microkernel-s0-s12.md](0060-the-domain-generality-invariant-the-microkernel-s0-s12.md) | 11. Sprint 3–4 closure and Phase 2 authorization | accepted |
| `0061` | [0061-apply-specification-v0-4-1-v4b-patches-before.md](0061-apply-specification-v0-4-1-v4b-patches-before.md) | 11. Sprint 3–4 closure and Phase 2 authorization | accepted |
| `0062` | [0062-implement-unix-domain-socket-runtimeservice-daemon-and-asymmetric.md](0062-implement-unix-domain-socket-runtimeservice-daemon-and-asymmetric.md) | 11. Sprint 3–4 closure and Phase 2 authorization | accepted |
| `0063` | [0063-the-control-plane-is-python-adr-0001-typescript.md](0063-the-control-plane-is-python-adr-0001-typescript.md) | 12. Phase 3 authorization, language ratification and gate status | accepted |
| `0064` | [0064-record-mvp-gate-status-at-0238b1a-q1-partially.md](0064-record-mvp-gate-status-at-0238b1a-q1-partially.md) | 12. Phase 3 authorization, language ratification and gate status | accepted |
| `0065` | [0065-adopt-d-01-d-15-from-the-lam.md](0065-adopt-d-01-d-15-from-the-lam.md) | 12. Phase 3 authorization, language ratification and gate status | accepted |
| `0066` | [0066-mcp-is-configuration-and-an-adapter-after-v0.md](0066-mcp-is-configuration-and-an-adapter-after-v0.md) | 12. Phase 3 authorization, language ratification and gate status | accepted |
| `0068` | [0068-evidenceclaim-optional-hedge-fields-supportcount-lastcorroboratedat-protectionclass-writer.md](0068-evidenceclaim-optional-hedge-fields-supportcount-lastcorroboratedat-protectionclass-writer.md) | 12. Phase 3 authorization, language ratification and gate status | accepted |
| `0069` | [0069-runtime-convergence-python-first-packages-canonical.md](0069-runtime-convergence-python-first-packages-canonical.md) | v0.6 Concept Lock | accepted |
| `0070` | [0070-recursive-substrate-agent-spawn-swarm-as-policy.md](0070-recursive-substrate-agent-spawn-swarm-as-policy.md) | v0.6 Concept Lock | accepted |
| `0071` | [0071-authority-state-ledger-identity-trinity.md](0071-authority-state-ledger-identity-trinity.md) | v0.6 Concept Lock | accepted |
| `0072` | [0072-plugin-boundary-wire-first-evaluator-exterior.md](0072-plugin-boundary-wire-first-evaluator-exterior.md) | v0.6 Concept Lock | accepted |
| `0073` | [0073-v060-lock-vs-defer.md](0073-v060-lock-vs-defer.md) | v0.6 Concept Lock | accepted |
| `0074` | [0074-gamma-lock-amendments-proof-budget-writer-identity.md](0074-gamma-lock-amendments-proof-budget-writer-identity.md) | v0.6 Concept Lock GAMMA | accepted |

`0067` is a documented numbering hole (no file). Do not fill it.
`ADR-M0-07` (six named reservation fields) remains accepted; additive vs structural typing is `ADR-0074`.

## ADR-M0 namespace (Foundation Lock, cannot collide with 0000+)

| ADR | File | Section | Status |
|---|---|---|---|
| `M0-01` | [ADR-M0-01-control-coverage-discipline.md](ADR-M0-01-control-coverage-discipline.md) | M0 control coverage | accepted |
| `M0-02` | [ADR-M0-02-identifier-namespaces.md](ADR-M0-02-identifier-namespaces.md) | M0 identifier namespaces | accepted |
| `M0-03` | [ADR-M0-03-five-spis.md](ADR-M0-03-five-spis.md) | M0 five SPIs | accepted |
| `M0-04` | [ADR-M0-04-approved-stack.md](ADR-M0-04-approved-stack.md) | M0 approved stack | accepted |
| `M0-05` | [ADR-M0-05-risk-register.md](ADR-M0-05-risk-register.md) | M0 risk register | accepted |
| `M0-06` | [ADR-M0-06-plane-mapping-archaeology.md](ADR-M0-06-plane-mapping-archaeology.md) | M0 plane mapping | accepted |
| `M0-07` | [ADR-M0-07-six-dimension-reservation.md](ADR-M0-07-six-dimension-reservation.md) | M0 six-dimension reservation | accepted |
| `M0-08` | [ADR-M0-08-k40-invert.md](ADR-M0-08-k40-invert.md) | M0 K-40 invert | accepted |
| `M0-09` | [ADR-M0-09-f21a-alarm.md](ADR-M0-09-f21a-alarm.md) | M0 alarm set | accepted |
| `M0-10` | [ADR-M0-10-no-metaphysics.md](ADR-M0-10-no-metaphysics.md) | M0 no metaphysics | accepted |
| `M0-11` | [ADR-M0-11-sink-class-mediation.md](ADR-M0-11-sink-class-mediation.md) | M0 sink-class mediation | accepted |
| `M0-12` | [ADR-M0-12-tool-not-episode.md](ADR-M0-12-tool-not-episode.md) | M0 tool ≠ episode | accepted |
| `M0-13` | [ADR-M0-13-walking-skeleton.md](ADR-M0-13-walking-skeleton.md) | M0 walking skeleton | accepted |
