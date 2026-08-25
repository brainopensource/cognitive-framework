---
status: living
id: architecture-c4-components
class: architecture
authority: descriptive
canonical_for:
  - c4-components-view
source_of_truth:
  - docs/SPEC.md#1-layer-0--the-microkernel
derived_from:
  - vanguard/packages/domain/__init__.py
  - vanguard/packages/ports/__init__.py
  - vanguard/packages/kernel/__init__.py
  - vanguard/packages/agency/__init__.py
  - vanguard/packages/runtime/__init__.py
  - vanguard/packages/adapters/__init__.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# C4 Component View (Hexagonal Production Lattice)

> **Status:** `AS_BUILT` · Descriptive View.

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Domain     │◄────│    Ports     │◄────│    Kernel    │
│ (Stdlib Py)  │     │ (Protocols)  │     │  (TCB Core)  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 ▲
                                                 │
┌──────────────┐     ┌──────────────┐     ┌──────┴───────┐
│   Adapters   │◄────│   Runtime    │◄────│    Agency    │
│ (Executors)  │     │ (Lifecycle)  │     │(Turn Engine) │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Subsystem Responsibilities

1. **`domain/`** ([`vanguard/packages/domain/`](../../vanguard/packages/domain/)):
   - Value objects, wire contracts, JCS RFC 8785 canonicalization, ledger reducers, event definitions, evidence models, and selector algebra (`resource_selector.py`).
2. **`ports/`** ([`vanguard/packages/ports/`](../../vanguard/packages/ports/)):
   - Hexagonal interfaces: kernel-facing `Clock`, `EffectAdapter`, `EventSink`, and `Ledger`; `ModelPort`, `SandboxRunner`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `EnvironmentPort`, `IndexPort`, injected clock/random ports, and five SPI protocols in `spi.py`.
3. **`kernel/`** ([`vanguard/packages/kernel/`](../../vanguard/packages/kernel/)):
   - Trusted Computing Base ($\le 1438$ LOC budget). 13-stage effect dispatch pipeline (S0–S12), monotonic capability attenuation, typed budget algebra, capability grants, action classification, fail-closed policy, and provenance DAG. Domain-blind (Invariant I-7).
4. **`agency/`** ([`vanguard/packages/agency/`](../../vanguard/packages/agency/)):
   - Turn engine (`EpisodeEngine`), current attenuated child construction, context compiler, and token compactor. The capability-mediated `agent.spawn` effect is deferred to M-6.
5. **`runtime/`** ([`vanguard/packages/runtime/`](../../vanguard/packages/runtime/)):
   - Lifecycle composition (`compose.py`), session management (`session.py`), dependency wiring (`wiring.py`), single-writer `LedgerEmitter` (`ledger_emitter.py`), and evaluator gateway (`evaluator_gateway.py`).
6. **`adapters/`** ([`vanguard/packages/adapters/`](../../vanguard/packages/adapters/)):
   - Concrete implementations: Model adapters (OpenRouter, Ollama, Cassette, Fake), rootless sandbox (bwrap), evaluator daemon client, SQLite event store.
