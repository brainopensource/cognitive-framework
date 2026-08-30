# AS_BUILT Architecture Reconstruction

- `analysis_subject_sha`: `9fd444674bf3a97f2673ff36a5f5928ef046c574`
- Reconstruction branch/HEAD reviewed: `docs/convergenc-electroweak-v091` / `5febb4f547267351b40066e055b4a5ba7b2dbe5a`
- Context: Block B code-first reconstruction from production code, tests, schemas, configuration, manifests and public interfaces.
- This is reconstruction evidence, not canonical product documentation. Canonical documentation has not yet been written.

## Verdict

`BLOCK B EXIT GATE: PASS`

No implementation-relevant path changed between the subject SHA and the reviewed reconstruction HEAD.

## Discovered architecture

A Python-first event-sourced agentic runtime composes manifest-defined packs into a bounded sequential EpisodeEngine. A small domain-blind kernel mediates effects and typed resources; runtime owns composition, lifecycle and the single ledger writer; adapters implement model, environment, sandbox, evaluator and store ports; recursive roles re-enter the same runtime; Python/TypeScript clients consume application/service boundaries.

## Subsystems

- `SUB-B-01` — Domain contracts and projections (IMPLEMENTED): Own pure values, canonicalization, event/artifact/workflow contracts and deterministic reducers.
- `SUB-B-02` — Ports and SPIs (IMPLEMENTED): Define dependency-inversion protocols for kernel, model, environment, stores, evaluator, memory and plugins.
- `SUB-B-03` — Kernel trusted core (IMPLEMENTED): Mediate every generic effect through authorization, grants, typed resources and ordered settlement.
- `SUB-B-04` — Agency turn engine and context (IMPLEMENTED): Run the bounded sequential propose/dispatch/observe loop and compile model context.
- `SUB-B-05` — Causal state, artifacts and persistence (IMPLEMENTED): Persist causal facts and artifacts; reconstruct projections, recovery and checkpoints.
- `SUB-B-06` — Runtime composition and session lifecycle (IMPLEMENTED): Compile manifests, activate components, bind profiles/adapters and run one canonical session.
- `SUB-B-07` — Delegation, topology and workflow mechanisms (PARTIAL): Represent and execute nested lineages and sequential topology routing; host isolated workflow experiments.
- `SUB-B-08` — Memory and governed learning (IMPLEMENTED): Authorize, persist, retrieve and lifecycle-manage memory and immutable compositions.
- `SUB-B-09` — Evaluation, evidence and assurance (IMPLEMENTED): Capture trajectories and obtain exterior signed evaluation without episode self-grading.
- `SUB-B-10` — Packs, manifests and plugin lifecycle (IMPLEMENTED): Supply task-domain composition, tools, policies and plugin activation outside the trusted core.
- `SUB-B-11` — Application, service and client surfaces (PARTIAL): Expose runtime commands, queries, event streams and visual clients without duplicating substrate authority.
- `SUB-B-12` — Schemas and generated wire contracts (IMPLEMENTED): Own exact JSON wire shapes, compatibility readers and conformance vectors.

## Primary execution

manifest parse/compose → activation plan → run plan identity → HarnessSession.begin_episode → EpisodeEngine propose → Kernel.dispatch → adapter effect → ledger/artifact capture → exterior evaluation → EpisodeCompleted/trajectory/result

## Invariants

- `INV-B-001` — Lower-layer dependency direction is enforced: domain <- ports <- kernel <- agency <- runtime, with adapters behind ports.
- `INV-B-002` — Kernel/domain remain domain-blind and kernel stays within 1438 logical LOC.
- `INV-B-003` — Privileged effects persist intent before physical dispatch and release leases before terminal emission.
- `INV-B-004` — Child scopes never widen actions, resources, constraints, depth or network policy.
- `INV-B-005` — Only usd_micros, millis, tokens and bytes are additive budgets; turns/depth are structural ceilings.
- `INV-B-006` — Causal state is reconstructed by folding durable ordered events; checkpoints are discardable verified caches.
- `INV-B-007` — Privileged event kinds have role-scoped writer ownership and new production envelopes use mhf.event/2.
- `INV-B-008` — Canonical runtime turns are sequential; topology/1 lowers to ordinary sequential spawn rather than granting authority.
- `INV-B-009` — Exterior evaluator authority is separate from episode execution and alone writes signed verdict facts.
- `INV-B-010` — Memory retrieval requires scoped authorization before ranking and dereference.

## Significant unresolved findings

- `UNR-B-001` (high, CONTRADICTED) — Default TypeScript live StartRun does not send profileId, while RuntimeService defaults to unsupported code-default.
- `UNR-B-002` (medium, PARTIAL) — mhf.topology/2 WorkflowScheduler and StagedWorkflowEngine are isolated, tested mechanisms with no canonical runtime caller or canonical ledger writer.
- `UNR-B-003` (medium, PARTIAL) — Python vanguard and TypeScript vg expose overlapping, non-identical command sets and no shared command registry.
- `UNR-B-004` (low, OBSOLETE) — Runtime.execute_harness remains public and tested although explicitly retired from production callers.
- `UNR-B-005` (low, UNRESOLVED) — runtime and adapters are namespace packages without curated package-root exports, so module paths act as de facto public surfaces.
- `UNR-B-006` (low, UNRESOLVED) — Hundreds of schema/vector files include compatibility and negative corpora; not every individual vector has a unique production producer/consumer.
- `UNR-B-007` (low, UNRESOLVED) — Root-level benchmark/status Markdown governance remains unclassified.
- `UNR-B-008` (low, PARTIAL) — vanguard/packages/apps contains only an empty package marker.

## Evidence artifacts

The adjacent JSON/JSONL registries are the machine-readable evidence, claims, boundaries, dependencies, flows, interfaces, invariants and unresolved findings for this view.
