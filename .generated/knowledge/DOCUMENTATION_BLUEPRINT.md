# Canonical Documentation Blueprint

- `analysis_subject_sha`: `9fd444674bf3a97f2673ff36a5f5928ef046c574`
- Context: Block C planning artifact derived from the validated Block B AS_BUILT model and the governing documentation architecture specification.
- This is a planning artifact, not canonical documentation. No candidate page has been written.

## Verdict and approval

`BLOCK C EXIT GATE: PASS`

The delegated Tech Lead / Architecture Owner technically approves this blueprint for Block D AS_BUILT production only. Independent audit, TARGET reconciliation, governance ratification and cutover controls remain mandatory.

## Exact candidate tree

- `candidate-docs/README.md` — `nav.home` (AS_BUILT)
- `candidate-docs/SPEC.md` — `spec.core` (TARGET_DEPENDENT, deferred)
- `candidate-docs/architecture/overview.md` — `arch.system.overview` (AS_BUILT)
- `candidate-docs/architecture/runtime-execution.md` — `arch.runtime.execution` (AS_BUILT)
- `candidate-docs/architecture/kernel.md` — `arch.trust.kernel` (AS_BUILT)
- `candidate-docs/architecture/agency.md` — `arch.agency.turns` (AS_BUILT)
- `candidate-docs/architecture/causal-state.md` — `arch.state.causal` (AS_BUILT)
- `candidate-docs/architecture/composition-extensibility.md` — `arch.composition.extensibility` (AS_BUILT)
- `candidate-docs/architecture/delegation-topology.md` — `arch.orchestration.delegation` (AS_BUILT)
- `candidate-docs/architecture/memory-learning.md` — `arch.memory.learning` (AS_BUILT)
- `candidate-docs/architecture/assurance-evaluation.md` — `arch.assurance.evaluation` (AS_BUILT)
- `candidate-docs/architecture/application-interfaces.md` — `arch.interfaces.clients` (AS_BUILT)
- `candidate-docs/reference/commands.md` — `ref.commands` (AS_BUILT)
- `candidate-docs/reference/runtime-service.md` — `ref.runtime-service` (AS_BUILT)
- `candidate-docs/reference/events.md` — `ref.events` (AS_BUILT)
- `candidate-docs/reference/schemas.md` — `ref.schemas` (AS_BUILT)
- `candidate-docs/reference/configuration.md` — `ref.configuration` (AS_BUILT)
- `candidate-docs/reference/ports.md` — `ref.ports` (AS_BUILT)
- `candidate-docs/reference/manifests.md` — `ref.manifests` (AS_BUILT)
- `candidate-docs/reference/artifacts-memory.md` — `ref.artifacts` (AS_BUILT)
- `candidate-docs/guides/getting-started.md` — `guide.getting-started` (AS_BUILT)
- `candidate-docs/guides/run-and-resume.md` — `guide.run-resume` (AS_BUILT)
- `candidate-docs/guides/compose-an-agent.md` — `guide.compose-agent` (AS_BUILT)
- `candidate-docs/guides/add-pack-or-tool.md` — `guide.add-pack-tool` (AS_BUILT)
- `candidate-docs/guides/add-adapter-or-provider.md` — `guide.add-adapter-provider` (AS_BUILT)
- `candidate-docs/guides/operate-runtime-service.md` — `guide.operate-service` (AS_BUILT)
- `candidate-docs/decisions/README.md` — `decision.index` (TARGET_DEPENDENT, deferred)
- `candidate-docs/execution/milestones.md` — `execution.milestones` (TARGET_DEPENDENT, deferred)
- `candidate-docs/execution/active.md` — `execution.active` (TARGET_DEPENDENT, deferred)
- `candidate-docs/theory/agent-substrate.md` — `theory.agent-substrate` (TARGET_DEPENDENT, deferred)

## Counts

- Canonical IDs: 30
- Block D work packets: 25
- Deferred TARGET packets: 5

## Safe production batches

- `D-BATCH-1`: WP-D-014, WP-D-015, WP-D-016, WP-D-017, WP-D-018, WP-D-019, WP-D-013, WP-D-012
- `D-BATCH-2`: WP-D-004, WP-D-005, WP-D-006, WP-D-007, WP-D-008, WP-D-009, WP-D-010, WP-D-011
- `D-BATCH-3`: WP-D-003
- `D-BATCH-4`: WP-D-002
- `D-BATCH-5`: WP-D-020, WP-D-021, WP-D-022, WP-D-023, WP-D-024, WP-D-025
- `D-BATCH-6`: WP-D-001

## Ownership rule

One durable fact has one canonical owner. The collision review in `documentation-blueprint.json` names every planned summary/link-only relationship.

## Unresolved

- `UNR-C-001` (medium) — The exact future normative SPEC leaf split cannot be selected before Block E TARGET reconciliation.
- `UNR-C-002` (medium) — Decision index/cutover treatment depends on append-only ADR governance ratification.
- `UNR-C-003` (low) — No standalone apps page is justified because vanguard/packages/apps is empty.
- `UNR-C-004` (high) — Live StartRun profile mismatch must remain visible in reference, architecture and guide without becoming three owners.
