# Port interfaces and activation control

**Status:** DRAFT implementation control

**Authority:** `docs/sprint0/system-architecture-icd.md` §4 and `docs/v4/04_vanguard_core_contracts_and_wire_schema_v040.md` §13

**Owner:** Tech Lead

This control resolves implementation placement and activation timing; it does not change the locked v4 concepts. The ICD port table is the Phase 0 implementation inventory. `OperatorRunner` remains an effect-facing runtime concern under the ICD's no-`ToolPort` ruling, and no `ProcessPort` is permitted.

## Activation rule

A production port becomes active only when one change set provides all four pieces:

1. the interface in `vanguard/packages/ports/`;
2. one shared behavioural contract suite, including typed failure behaviour;
3. a deterministic fake with no ambient I/O, clock, or randomness;
4. at least one real adapter in an isolated `vanguard/packages/adapters/<family>/` family.

An interface without that bundle is not advance scaffolding; it is incomplete production code. Planned interfaces stay in the authoritative documents until their bundle is scheduled. Disposable probes may define local types inside `spike/` or `slice/`, but production code cannot import them and they do not satisfy a permanent adapter obligation.

## Current activation

`EventStorePort` is the only activated world-facing port in this branch. `InMemoryEventStore` is its deterministic fake, `SqliteEventStore` is its transactional WAL adapter, and `test/contracts/test_event_store_port.py` supplies the shared behavioural contract. The kernel role protocols in `ports/kernel.py` are narrow dependency-inversion facets for the dispatch implementation; they are not additional cross-process wire contracts and must not be mirrored in clients.

| Planned world-facing port | Activation bundle required |
|---|---|
| `ModelProvider` | scripted fake, rebuilt production provider adapter, proposal/failure contract suite |
| `EnvironmentAdapter` | in-memory versioned environment, Git adapter, snapshot/receipt/compensation suite |
| `EvaluatorPort` | fixed verdict fake, separate-identity evaluator adapter, fail-closed suite |
| `EventStorePort` | **active:** in-memory fake, SQLite/WAL adapter, shared store contract |
| `BlobStorePort` | in-memory classified bytes, encrypted classified store, digest/atomicity suite |
| `ObservationSource` | fixed labelled blocks, repository/retrieval source, label-at-source suite |
| `PolicyEngine` | deterministic table policy, configured policy adapter, denial/scope/expiry suite |
| `Governor` | deterministic vector accounting, runtime budget service, conservation/overrun suite |
| `SandboxRunner` | visibly non-contained fake, rootless perimeter adapter, containment-report suite |
| `ClockPort` / `RandomPort` | fixed/seeded fakes, system clock/CSPRNG adapters, determinism/recording suite |

The remaining ICD ports activate with their planned consumers and real adapters. In particular, no permanent model or environment adapter may be copied out of T0b; the real provider and Git environment adapters are rebuilt at T6.1. `PolicyEngine` and `Governor` extraction must be part of the S3 dispatch integration change set, with their fake/real pairs and common suites, before runtime composition treats either as an external port.

## Language and client boundary

JSON Schema and golden vectors are the cross-language source of truth. A language-internal protocol is not duplicated merely because another language exists. TypeScript clients consume versioned domain event/envelope data and a runtime client surface; they do not mirror Python runtime ports method-for-method. If a port crosses a process or language boundary later, its transport schema, shared vectors, cancellation/backpressure framing, and both readers land in the same activation change.

This keeps the CLI mockable without creating a second backend contract: the versioned client contract under `vanguard/clients/cli/src/contract/` is a client-facing anti-corruption boundary and is implemented by a runtime/daemon adapter when T6.4 integrates.
