---
status: living
id: protocols-index
class: protocol-reference
authority: descriptive
canonical_for:
  - ports-and-protocols-index
source_of_truth:
  - docs/SPEC.md#1-layer-0--the-microkernel
derived_from:
  - vanguard/packages/ports/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Hexagonal Port Protocols & Interfaces Index

> **Classification:** Protocol Reference (`AS_BUILT`).  
> **Source Code:** [`vanguard/packages/ports/`](../../vanguard/packages/ports/)

---

## Hexagonal Port Specifications

| Protocol | Source File | Implementing Adapters | Key Port Responsibilities |
|---|---|---|---|
| [`kernel.md`](kernel.md) | `ports/kernel.py` | consumed by `kernel/dispatch.py` | Four narrow dependency-inversion ports used by the TCB |
| [`model.md`](model.md) | `ports/model.py` | `adapters/models/` | Proposal request/result seam; routing and measurement remain adapter/runtime concerns |
| [`sandbox.md`](sandbox.md) | `ports/sandbox.py` | `adapters/sandbox/` | Bubblewrap process execution in UID 10001 |
| [`evaluator.md`](evaluator.md) | `ports/evaluator.py` | `adapters/evaluators/` | Grading requests and signed verdict retrieval |
| [`stores.md`](stores.md) | `ports/event_store.py` | `adapters/stores/` | Append/read/digest/count seam; reducers and recovery live outside the port |
| [`spi.md`](spi.md) | `ports/spi.py` | five wire-facing protocols | Planner, context, toolkit, memory, and evaluation-gate SPIs |
