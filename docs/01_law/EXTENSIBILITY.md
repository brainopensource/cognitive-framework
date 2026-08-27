---
id: normative-extensibility-law
class: law
authority: normative
canonical_for:
  - manifest-plugin-spi-law
  - component-graph-static-law
status: living
owner: principal-systems-architect
version: "0.8.0"
last_verified: 2026-08-25
read_when:
  - changing-manifests-or-plugins
  - adding-an-spi-or-domain-pack
do_not_read_when:
  - changing-ledger-recovery-only
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Extensibility law

This leaf routes manifest, plugin, SPI, and pack work to the preserved detailed clauses in
[`RUNTIME.md §2`](RUNTIME.md#2-plugin-architecture--spi-definitions) and the as-built contracts in
[`../05_contracts/manifests.md`](../05_contracts/manifests.md), [`../06_protocols/spi.md`](../06_protocols/spi.md),
and [`../02_decisions/0077-named-component-graph-manifest.md`](../02_decisions/0077-named-component-graph-manifest.md).

> **Authority.** Normative, but subordinate to [`VISION.md`](../../VISION.md) (Law Zero, `ADR-0095`).

## The runtime owns no domain

The runtime owns composition, lifecycle, sessions, persistence, and execution. **It owns no domain
behavior.** Coding, table, formal, research, and every future domain MUST reach the runtime through
discoverable, injectable extension points: binding providers, tools, context logic, evaluators,
policies, packs, and adapters. A domain name appearing in a runtime module is a defect, not a design.

Domain effects enter through namespaced binding providers implementing existing ports. Neither a
global coding-specific binding table nor a hardcoded command/manifest mapping is an extensibility
authority.

## Kernel Neutrality Gate

Any milestone introducing a new domain or changing a foundational contract MUST run RF-98. The
expected result is zero Kernel semantic diff. A non-zero diff fails the gate unless an accepted ADR
explains why the capability cannot be expressed through ports, adapters, packs, policies,
projections, or Runtime mechanisms. RF-97 measures the automatically discovered transitive
executable import closure of production Kernel modules; directory-only or hard-coded dependency
counts are insufficient.

> **Current-state gap / planned migration.** Source code still carries domain knowledge inside the
> runtime package. Named instances at `ADR-0095` acceptance:
>
> | Location | Coupling | Migration |
> |---|---|---|
> | `runtime/entrypoint.py` | hardcodes `vg-code-default` / `vg-code-explain` manifest selection and raises `unsupported coding command`; defaults `project_id` to `coding-preview` | resolve the manifest through pack discovery; the entrypoint must be domain-neutral |
> | `runtime/scoring.py` | scores "a coding arm" from the ledger projection | move to a pack/adapter-owned projection |
> | `runtime/autonomous_grant.py` | issues grants named for "autonomous coding" sessions | make the grant generic; domain naming belongs to the pack |
>
> These are concrete migration tasks (M-5a lane), **not** a licence to describe the runtime as
> domain-aware. The rule above is the target and is binding on new code today.

## Static graph, emergent trajectory

Two graphs MUST be distinguished.

**Composition** (`mhf.manifest/2`) is a named component graph evaluated at composition time. It
declares the *space of possibilities*: which capabilities, providers, plugins, limits, schemas, and
policies exist for an execution. It does not prescribe the order in which they are used, and it is
not a runtime control-flow DAG.

**Trajectory** is the emergent causal graph recorded in the ledger: which possibilities were actually
used, in what causal order, with which inputs, outputs, and results. It is *observed after the fact*,
though portions may be conditioned by policies or topologies.

The runtime turn loop remains unary and sequential (I-11) until M-7 measurement and an explicit
Director lift. Multi-agent topologies are mediated delegation (`agent.spawn`, M-6) or composed
plugins; they never add a dynamic scheduler graph to the kernel. Topologies, when they arrive at M-7,
are versioned configuration or artifacts — never a second runtime authority.

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

Unsupported providers, fields, references, endpoints, interfaces, selector relations, or unconsumed
authority fail before activation.

## Planned domain and delegation gates

**M-5a** allocates the event-derived `AgentView` vocabulary and lineage/scope semantics, then
re-tags the substrate baseline. **M-5b** adds Math/Formal Deductive Verification only as pack,
adapter, exterior checker, and tests; its RF-86 proof interval MUST leave
`vanguard/packages/{domain,ports,kernel,agency/episode,runtime}` semantically unchanged **relative to
the accepted successor baseline**. ADR-0102 records the historical `M-5A-BASE-v2` ref as
contaminated/unpublished; the new treatment compares only to reviewed `CONVERGENCE-BASE-v1`. A
discovered missing primitive fails the generality proof and returns an
architectural finding to governance; RF-86 is never weakened to accommodate a domain.

At **M-6**, `agent.spawn` is an ordinary privileged effect addressed by target `D_H`. It does not
instantiate an agent object: it creates a **nested execution lineage** subordinate to the current one,
carrying its own identity, parent reference, goal, selected context, budget, capabilities, depth
boundary, and terminal conditions. The generic kernel mediates it through S0–S12 and MUST NOT branch
on the verb; a runtime adapter creates the child only after durable intent. Authority, additive
budget, depth, turns, handles, credentials, lineage, recovery, and return provenance remain
monotonically bounded. Agency cannot create a production child directly.

A tool is not a spawn. A tool is an encapsulated transformation, however sophisticated internally —
including a fully deterministic one such as a solver, compiler, or linter. A child lineage has its own
agentic cycle, context evolution, and budget. That difference is what justifies `agent.spawn` as a
distinct operation rather than another tool.

At **M-6.5**, adaptive strategy and meta-control land as policy, reducer, or plugin. A meta-controller
observes projections and emits ordinary commands; it holds no kernel authority and passes S0–S12 like
any other proposer. **Metacognition is policy/reducer/plugin, never a kernel primitive.**

## Read map

| Concern | Canonical detail |
|---|---|
| Plugin model and manifest schema | [`RUNTIME.md §2.1`](RUNTIME.md#21-plugin-model) |
| Frozen SPI roster | [`RUNTIME.md §2.2`](RUNTIME.md#22-spi-definitions-typed-frozen-versioned) |
| Harness compilation and `D_H` | [`RUNTIME.md §2.3`](RUNTIME.md#23-canonical-manifest-and-execution-plans-the-compile-target) |
| Composition/identity concept lock | [`ADR-0088`](../02_decisions/0088-m3c-m8-concept-lock.md) (sequencing superseded by [`ADR-0095`](../02_decisions/0095-vision-as-law-zero-and-roadmap-reconciliation.md)) |
| Lifecycle and layer0 absorption | [`../02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md`](../02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md) |
| Pack boundaries and E2E | [`RUNTIME.md §4`](RUNTIME.md#4-coding-domain-pack-first-domain-foundation-e2e-not-this-lock-wave) |
