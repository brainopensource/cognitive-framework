---
id: normative-extensibility-law
class: law
authority: normative
canonical_for:
  - manifest-plugin-spi-law
  - component-graph-static-law
status: living
owner: principal-systems-architect
version: "0.6.1"
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

## Read map

| Concern | Canonical detail |
|---|---|
| Plugin model and manifest schema | [`RUNTIME.md §2.1`](RUNTIME.md#21-plugin-model) |
| Frozen SPI roster | [`RUNTIME.md §2.2`](RUNTIME.md#22-spi-definitions-typed-frozen-versioned) |
| Harness compilation and `D_H` | [`RUNTIME.md §2.3`](RUNTIME.md#23-harness-manifest-the-compile-target) |
| Lifecycle and layer0 absorption | [`../02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md`](../02_decisions/0081-plugin-lifecycle-runtime-absorption-layer0-deletion.md) |
| Pack boundaries and E2E | [`RUNTIME.md §4`](RUNTIME.md#4-coding-domain-pack-first-domain-foundation-e2e-not-this-lock-wave) |
