# System Architecture & Interface Control Document — Sprint 0 baseline

Status: `DRAFT — Tech Lead approval required`  
Owners: Tech Lead (primary); Senior Developer (ports, testability and conformance)  
Authority: below Vanguard v4 contracts and the Decision Record; above GTS-13C and the issue tracker  
Baseline date: 2026-08-14

## 1. Scope and naming resolution

This ICD controls physical source boundaries and interface ownership. It does not redefine wire fields owned by VG-04 or security rules owned by VG-05.

The implementation root is `vanguard/packages/`. The six top-level packages are exactly `domain`, `ports`, `kernel`, `agency`, `runtime`, and `adapters`. Historical names map as follows:

| Contract name | Physical package |
|---|---|
| `wire-schema` | `schemas/v4/`; generated language types may be consumed by `domain` |
| `policy-kernel` | `vanguard/packages/kernel` |
| `controller` | split by authority between `agency` and `runtime` |
| `governance` | `vanguard/packages/runtime/governance`; statically treated as a restricted package that may import only `domain`, `ports`, and `kernel` |
| `clients` / `cli` | future clients outside the package root; may import `domain` and the runtime client surface only |
| `lab` | repository `lab/`; isolated from all production imports |

This mapping resolves vocabulary without changing the v4 topology. A new seventh core package requires an ADR and an ICD revision.

## 2. Dependency lattice

An arrow points from a consumer to what it may import:

The compact mandated notation is `domain <- ports <- kernel <- agency <- runtime -> adapters`; the expanded graph below removes the notation's ambiguity by listing every allowed edge.

```text
runtime ────────→ agency ────────→ kernel ────────→ ports ────────→ domain
   │                 │                │                 │
   ├──────────────→ kernel            └──────────────→ domain
   ├──────────────→ ports
   ├──────────────→ domain
   └──────────────→ adapters ───────────────────────→ ports, domain

runtime/governance ─────────────────────────────────→ kernel, ports, domain
```

| Package | Owns | Allowed project imports | Forbidden authority |
|---|---|---|---|
| `domain` | Pure values, state and reducers | none | I/O, clocks, randomness, environment variables, adapters |
| `ports` | Interfaces and failure contracts | `domain` | concrete implementations, composition, policy decisions |
| `kernel` | Grants, attenuation, policy, budgets, dispatch, provenance | `domain`, `ports` | cognition, concrete adapters, evaluator implementation |
| `agency` | Episode coordination, context, operators, playbooks | `domain`, `ports`, `kernel` | adapters, evaluator paths, approvals, releases, finite governance processes |
| `runtime` | Composition root, daemon and lifecycle wiring | all six packages | domain rules or a second dispatch path |
| `runtime/governance` | Process definitions/instances, approvals, releases, restart-resume | `domain`, `ports`, `kernel` | `agency`, model ports/providers, adapters, open-ended control flow |
| `adapters` | Real/fake implementations behind ports | `domain`, `ports` | kernel policy, cognition, runtime; sibling adapter families may not import one another |

The CI boundary check fails on forbidden edges and file-level dependency cycles. `spike/` and `slice/` may consume public core interfaces for experiments, but no other directory may import either. Production source never imports `lab/`; `lab/` imports no project source and consumes versioned exports only.

## 3. Authority and call paths

There is one proposal-to-effect path. `agency` emits a proposal; `kernel` parses, classifies, authorises privileged sinks, writes durable intent, dispatches through a port, commits and releases the lease, and records the outcome. `runtime` alone injects a concrete adapter. No adapter decides policy and no caller bypasses the kernel for a privileged effect.

All effects are recorded. `pure` and `observation` effects do not require a capability grant; observations remain selector-checked and provenance-labelled. `privileged` effects require a descriptor-bound grant verified at the point of effect. A tool executes one typed effect and coordinates nothing.

Evaluation is exterior: agency cannot import evaluator implementations or request its own evaluation. The Evidence identity observes terminal ledger events and triggers evaluation. Activation and rollback are out-of-band human actions in the MVP; promotion changes an activation pointer and never overwrites a running component.

## 4. Port control table

Interfaces accept and return parsed domain/schema types. Provider or environmental failures are typed values, not exceptions. Every active port must land with a contract suite, a deterministic fake and at least one real adapter; adding only an interface is incomplete.

| Port | Minimum operation | Fake strategy | Real strategy | Conformance focus |
|---|---|---|---|---|
| `ModelProvider` | `propose(context, tools, sampling)` | scripted cassette/reply sequence | provider adapter, rebuilt after disposables | tool-call ordering, echoed call IDs, instrument errors |
| `EnvironmentAdapter` | `profile`, `snapshot`, `observe`, `preview`, `apply`, `reconcile`, `dispose` | in-memory versioned resources | Git and later TableWorld adapters | snapshot binding, selector checks, receipts, compensation |
| `EvaluatorPort` | `evaluate(runRef, protocol)` | fixed claims/inconclusive outcomes | separate-identity evaluator adapter | fail-closed verdict construction and isolation |
| `EventStore` | atomic `append`, ordered `read`, `digest` | in-memory single writer | transactional embedded store with WAL | monotonic sequence, crash recovery, replay digest |
| `BlobStore` | immutable `put/get` by digest | in-memory bytes | classified encrypted storage adapter | digest integrity and atomic event references |
| `ObservationSource` | produce labelled context blocks | fixed labelled blocks | repository/retrieval sources | label-at-source and no raw-string assembly |
| `PolicyEngine` | decide an authority request | table policy | configured policy adapter | denial, scope, classification and expiry |
| `Governor` | reserve, commit, release leases | deterministic vector accounting | runtime budget service | conservation, overrun debit, release on every path |
| `SandboxRunner` | execute and return receipt plus containment report | non-contained development fake, visibly marked | rootless worker perimeter | startup probes, mounts, egress, process-group cancellation |
| `ClockPort` / `RandomPort` | `now` / `next` | fixed or seeded values | system clock / CSPRNG adapter | determinism seam and recording |

There is no `ToolPort` or `ProcessPort`: a tool is an effect adapter and a process reduces ledger events.

## 5. Wire and compatibility controls

JSON Schema 2020-12 under `schemas/v4/` is the source of truth. External data is parsed, never cast. Writers reject unknown fields; generated readers preserve them. Canonical bytes use RFC 8785/JCS and `sha256:` digests. Version changes require a migration and a rehearsal against a synthetic corpus. Draft schemas may not record durable trajectories.

Artifact kinds resolve through an extensible registry. Registries and harness manifests resolve and freeze at episode composition. Every artifact is content-addressed and immutable; status, activation and invalidation-check state live separately.

## 6. Process and isolation topology

| Identity | Phase 0 process | May hold | Must not reach |
|---|---|---|---|
| controller | interaction + agency + kernel + governance + event-store client | episode/process state, grant issuance | evaluator inputs/image; worker credentials |
| worker | separate OS identity and mount/network namespace | granted workspace surface only | controller, evaluator, secrets except references |
| evaluator | separate OS identity and image digest | sealed evaluator bundle and completed run view | candidate writable paths; model-controlled capabilities |
| evolution | no runtime process | human-operated candidate review | autonomous promotion, R0/R1 updates |

Startup probes verify declared identities, namespaces, denied egress and denied syscalls. An unverified containment report blocks publication. Local uncontained development is allowed only when every resulting artifact says so.

## 7. Architecture conformance

Merge gates must prove:

1. every source import follows Section 2 and the graph is acyclic;
2. no source imports `spike/`, `slice/` or `lab/`;
3. `runtime/governance` has no model or agency dependency;
4. `agency` has no adapter/evaluator import and no approval/release ownership;
5. a deliberately broken fixture causes each applicable gate to fail;
6. every port implementation passes the same contract suite, including failure behaviour;
7. the deployed Phase 0 process/identity topology matches Section 6.

The Senior Developer owns the port contract suites, fake strategies and broken-fixture proofs. The Tech Lead owns approval of any boundary or authority change.

## 8. Change control

Boundary, authority, wire or isolation changes require an ADR with a reversal condition and linked Active MVP Contract rows. GTS-13C may motivate scheduling but cannot approve the change. Unknown or contradictory requirements stop at the Tech Lead rather than being resolved in implementation.
