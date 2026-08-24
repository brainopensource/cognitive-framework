---
id: normative-extensibility-law
class: law
authority: normative
canonical_for:
  - manifest-plugin-spi-law
  - component-graph-static-law
status: living
owner: principal-systems-architect
version: "0.6.2"
last_verified: 2026-08-23
read_when:
  - changing-manifests-or-plugins
  - adding-an-spi-or-domain-pack
do_not_read_when:
  - changing-ledger-recovery-only
supersedes: []
superseded_by: null
---

# Extensibility law

This leaf routes manifest, plugin, SPI, and pack work to the preserved detailed clauses in
[`RUNTIME.md §2`](RUNTIME.md#2-plugin-architecture--spi-definitions) and the as-built contracts in
[`../05_contracts/manifests.md`](../05_contracts/manifests.md), [`../06_protocols/spi.md`](../06_protocols/spi.md),
and [`../02_decisions/0077-named-component-graph-manifest.md`](../02_decisions/0077-named-component-graph-manifest.md).

## Static graph, sequential runtime

`mhf.manifest/2` is a named component graph evaluated at composition time. It is not a runtime
control-flow DAG. The runtime turn loop remains unary and sequential (I-11). Multi-agent topologies
are mediated delegation (`agent.spawn`, M-6) or composed plugins; they never add a dynamic scheduler
graph to the kernel.

## Canonical composition and activation

The sole production chain is:

```text
mhf.manifest/2 -> CanonicalManifest -> FrozenComposition[D_H]
  -> ActivationPlan[activation_digest] -> RunPlan[D_R] -> EpisodeEngine
```

`CanonicalManifest` is the one normalized schema value. Supported legacy bytes normalize at ingress
and MUST NOT survive as an execution value. `FrozenComposition` resolves and freezes every logical
component, binding, implementation/config digest, interface, entrypoint, profile, isolation policy,
evidence policy, and capability ceiling. `ActivationPlan` is a runtime projection containing concrete
factories/cells, validated interfaces, readiness, initialization dependencies, and reverse cleanup;
it adds no authority and never turns graph edges into workflow scheduling. `RunPlan` binds the frozen
composition and activation to the declared task, environment, store, model, oracle/evaluator,
authority, and budget.

Domain effects enter through namespaced binding providers implementing existing ports. A global
coding-specific binding table is not an extensibility authority. Unsupported providers, fields,
references, endpoints, interfaces, selector relations, or unconsumed authority fail before activation.

## Planned domain and delegation gates

M-5 adds Math/Formal Deductive Verification only as pack, adapter, exterior checker, and tests. Its
proof interval MUST leave `vanguard/packages/{domain,ports,kernel,agency,runtime}` semantically
unchanged; a discovered missing primitive fails the generality proof and returns to governance.

At M-6, `agent.spawn` is an ordinary privileged effect addressed by target `D_H`. The generic kernel
mediates it through S0–S12; a runtime adapter creates the child only after durable intent. Authority,
additive budget, depth, turns, handles, credentials, lineage, recovery, and return provenance remain
monotonically bounded. Agency cannot create a production child directly.

## Read map

| Concern | Canonical detail |
|---|---|
| Plugin model and manifest schema | [`RUNTIME.md §2.1`](RUNTIME.md#21-plugin-model) |
| Frozen SPI roster | [`RUNTIME.md §2.2`](RUNTIME.md#22-spi-definitions-typed-frozen-versioned) |
| Harness compilation and `D_H` | [`RUNTIME.md §2.3`](RUNTIME.md#23-canonical-manifest-and-execution-plans-the-compile-target) |
| M-3C through M-8 lock | [`ADR-0088`](../02_decisions/0088-m3c-m8-concept-lock.md) |
| Lifecycle and layer0 absorption | [`../02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md`](../02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md) |
| Pack boundaries and E2E | [`RUNTIME.md §4`](RUNTIME.md#4-coding-domain-pack-first-domain-foundation-e2e-not-this-lock-wave) |
