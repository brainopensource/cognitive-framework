---
id: ref.ports
canonical_id: ref.ports
class: reference
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: ports-spi
canonical_for:
  - port signatures and owners
  - five SPI contracts
  - implementer/test-double map
purpose: Own exact port and SPI lookup with implementer mappings.
audience:
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-007
  - E-B-011
  - E-B-012
  - E-B-017
  - E-B-021
  - E-B-037
  - E-B-038
  - E-B-050
  - E-B-053
  - E-B-054
relationships:
  - arch.system.overview
  - arch.composition.extensibility
  - guide.add-adapter-provider
reviewer: documentation-specialist
confidence: high
---

# Hexagonal Ports & SPI Reference

## Purpose
This document is the canonical reference owner for all hexagonal port protocols (`vanguard.packages.ports`), the five frozen Service Provider Interfaces (SPIs), and their concrete adapter mappings and test doubles.

## Scope
- Port protocol signatures in `vanguard/packages/ports/`.
- The five SPI protocols defined in `vanguard/packages/ports/spi.py` (`IPlanner`, `IContextManager`, `IToolkit`, `IMemoryEngine`, `IEvaluationGate`).
- Mapping of ports to concrete production adapters (`vanguard/packages/adapters/`) and test fakes.
- Standard port exception and failure hierarchies.

## Non-responsibilities
- Step-by-step procedures for writing a new adapter (owned by [`guide.add-adapter-provider`](../guides/add-adapter-or-provider.md)).
- High-level hexagonal architectural dependency rationale (owned by [`arch.system.overview`](../../architecture/overview.md) and [`arch.composition.extensibility`](../architecture/composition-extensibility.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Pure Python protocols enforce strict dependency inversion (`domain <- ports <- kernel <- agency <- runtime -> adapters`).
- `PARTIAL` — `IContextManager` and `IndexPort` provide the existing extension seams; the provider-neutral repository `ContextPacket` usage described in Section 5 is a **v0.9.2 target**, not a new implemented port signature.

---

## 1. The Five Frozen SPI Protocols (`ports/spi.py`)

The five SPI protocols represent the client interfaces of the agent substrate:

```python
from vanguard.packages.ports.spi import (
    IPlanner,
    IContextManager,
    IToolkit,
    IMemoryEngine,
    IEvaluationGate,
)
```

| SPI Interface | Key Methods | Input / Output Types | Primary Responsibility |
|---|---|---|---|
| `IPlanner` | `plan(view, budget)`<br>`observe(receipts, view)`<br>`reflect(outcome, trajectory)` | `EpisodeView`, `Reservation`<br>$	o$ `Result[Proposal]`, `Result[Reflection]` | Cognition engine; proposes next effect action. |
| `IContextManager` | `compile(view, budget_tokens)`<br>`ingest(receipts)`<br>`compact(pressure)`<br>`reground(error)` | `EpisodeView`, `int`<br>$	o$ `Result[ContextBundle]`, `Result[CompactionReport]` | Prefix-stable prompt assembly and context compaction. |
| `IToolkit` | `verbs()`<br>`execute(request, ctx)`<br>`compensate(receipt)`<br>`health()` | `EffectRequest`, `EffectContext`<br>$	o$ `Result[Receipt]`, `Health` | Physical effect execution (leased work only, never grants). |
| `IMemoryEngine` | `query(q)`<br>`store(record)`<br>`consolidate(hits)`<br>`prune(criteria)` | `MemoryQuery`, `MemoryRecord`<br>$	o$ `Result[Sequence[MemoryHit]]` | Episodic and semantic retrieval with scoped authorization. |
| `IEvaluationGate` | `evaluate(req)`<br>`rubrics()` | `EvaluationSubject`<br>$	o$ `Result[SignedVerdict]` | Exterior evaluation verdict provider. |

---

## 2. Core Hexagonal Port Protocols

Hexagonal ports define the interfaces required by the runtime and kernel:

| Port Protocol (`vanguard/packages/ports/`) | Method Signatures | Description |
|---|---|---|
| `KernelPort` (`kernel.py`) | `dispatch(intent, grant) -> EffectReceipt`<br>`observe(event) -> Observation` | Kernel mediation and effect dispatch pipeline entry. |
| `ModelPort` (`model.py`) | `generate(request) -> ModelResponse`<br>`stream(request) -> Iterator[ModelStreamChunk]` | LLM inference adapter interface. |
| `SandboxPort` (`sandbox.py`) | `execute(cmd, env, cwd) -> ExecResult`<br>`spawn(cmd, env) -> ProcessHandle` | Process isolation and execution container. |
| `EvaluatorPort` (`evaluator.py`) | `evaluate_trajectory(traj) -> EvaluationVerdict` | Exterior verification and scoring daemon. |
| `EventStorePort` (`event_store.py`)| `append(envelope) -> None`<br>`read(range) -> Iterator[EventEnvelope]` | Append-only event persistence and causal ordering. |
| `BlobStorePort` (`blob_store.py`) | `put(bytes) -> str (digest)`<br>`get(digest) -> bytes`<br>`has(digest) -> bool` | Content-addressed storage (CAS) for artifacts. |
| `EnvironmentPort` (`environment.py`) | `get(key) -> str`<br>`cwd() -> Path`<br>`qualify(tool) -> bool` | Host environment inspection and path resolution. |
| `ClockPort` (`determinism.py`) | `now() -> datetime` | Pluggable time source for deterministic replay. |
| `RandomPort` (`determinism.py`) | `token() -> str`, `randint(a, b) -> int` | Pluggable entropy source for deterministic replay. |
| `IndexPort` (`index.py`) | `search(query) -> list[Hit]`, `index(doc) -> None` | Inverted index / search interface. |
| `MemoryPort` (`memory.py`) | `search(q) -> list[MemoryHit]`, `put(r) -> None` | Memory retrieval port interface. |
| `ChildTurnPort` (`child_turn.py`) | `spawn(child_spec) -> ChildResult` | Mediated child agent execution delegation. |

---

## 3. Concrete Implementations & Test Doubles

Adapters live in `vanguard/packages/adapters/` and must never import `kernel` or `agency`:

| Port | Production Adapter (`adapters/`) | In-Memory / Test Double |
|---|---|---|
| `ModelPort` | `models.openrouter.OpenRouterModel`<br>`models.ollama.OllamaModel` | `models.cassette.CassetteModel`<br>`models.fake.FakeModel` |
| `SandboxPort` | `sandbox.bwrap.BwrapSandbox` (Bubblewrap) | `sandbox.fake.FakeSandbox`<br>`sandbox.host.HostSandbox` |
| `EvaluatorPort` | `evaluators.daemon_client.EvaluatorDaemonClient` | `evaluators.fake.FakeEvaluator` |
| `EventStorePort` | `stores.sqlite.SqliteEventStore` | `stores.in_memory.InMemoryEventStore` |
| `BlobStorePort` | `stores.blob_store.FilesystemBlobStore` | `stores.blob_store.InMemoryBlobStore` |
| `MemoryPort` | `stores.memory_engine.SqliteMemoryEngine` | `stores.memory_engine.InMemoryMemoryEngine` |
| `ClockPort` | `runtime.determinism.SystemClock` | `runtime.determinism.FrozenClock` |
| `RandomPort` | `runtime.determinism.SystemRandom` | `runtime.determinism.DeterministicRandom` |

---

## 4. Failure Hierarchy & `Result[T]` Monad

SPI methods return the `Result[T]` Algebraic Data Type (`vanguard.packages.domain.wire.result`):
- `Ok(value)`: Successful operation wrapping output value.
- `Err(error)`: Explicit typed error (`EffectFailure`, `MemoryError`, `EvaluationError`) avoiding untyped runtime exceptions.

---

## 5. v0.9.2 Target: Repository-Intelligence Binding

> **TARGET / PLANNED — not AS_BUILT.** Reuse the five frozen SPIs and existing `IndexPort`; do not add an LDA-specific substrate port.

The code-pack `IContextManager` may query `IndexPort` or a provider adapter and compile the results into a bounded, value-only context packet. The planned logical fields are:

```text
task_digest                 repository_snapshot_digest
provider_id                 provider_version
query_digest                selected_documents[]
selected_symbols[]          selected_files[]
related_tests[]             dependency_edges[]
estimated_tokens            omissions[]
packet_digest
```

`omissions` makes truncation, unavailable sources, and failed provider lookups explicit. Hits are advisory references with provenance and confidence; consumers resolve and verify target files before use. An index health claim is usable only when its schema is valid, its source snapshot matches, required entity counts are non-zero, referenced paths resolve, and freshness checks pass. Otherwise composition degrades to a deterministic filesystem/source search implementation.

The provider boundary is intentionally narrow: it retrieves and ranks information but cannot dispatch effects, mutate task state, grant capabilities, or become an authority source. Exact value types and versioned schemas should be added here only when their source implementation lands.

---

## Implementation Evidence

- **Port Definitions**: `vanguard/packages/ports/` (`spi.py`, `kernel.py`, `model.py`, `sandbox.py`, `evaluator.py`, `event_store.py`, `blob_store.py`, `environment.py`, `determinism.py`, `index.py`, `memory.py`, `child_turn.py`).
- **Adapter Implementations**: `vanguard/packages/adapters/`.
- **SPI Tests**: `test/contracts/test_spi_protocols.py`, `test/contracts/test_a1_canonical_composition.py`.
