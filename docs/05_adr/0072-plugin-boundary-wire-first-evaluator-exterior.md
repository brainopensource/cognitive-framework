---
adr: 0072
title: "Plugin boundary is wire-first JSON-RPC/UDS; Python Protocol is a client; in_process is a privilege; ADR-0005 freeze stands; evaluator is not a product plugin"
status: accepted
source_section: "v0.6 Concept Lock"
---

# ADR-0072: Plugin boundary, freeze-at-composition, exterior evaluator

**Context.** SPEC v0.5.0 §2.1 describes plugin hot-swap mid-run (activate new version, route new
turns, quiesce old). ADR-0005 forbids runtime extension discovery and freezes registries at
composition. The two sentences cannot both be law. Parecer v4 correctly notes that a Python
`typing.Protocol` cannot be the polyglot substitution boundary, then incorrectly lists Evaluator
as a product plugin (Anel 2). `layer0/spi/jsonrpc.py` already implements line-delimited JSON-RPC
2.0; packages adapters already call it (`adapters/sandbox/toolkit.py`, `adapters/evaluators/gate.py`).
`layer0/spi/ceiling.py:21-22` fail-opens when the capability list is empty. `IEvaluationGate` is
the fifth SPI (ADR-M0-03); the judge itself is a separate identity (ADR-0004, ADR-M0-08).

**Decision.**

1. **Wire is the contract.** Plugin substitution uses JSON-RPC 2.0, line-delimited, over Unix
   domain sockets (ADR-0002, ADR-0059). JSON Schema + JCS remain the type source (ADR-0008,
   ADR-0009). Python `Protocol` types are a **client convenience**, not the normative SPI.
2. **`in_process` is an isolation privilege**, granted by policy (I-6), not a second SPI. An
   in-process plugin still speaks the same wire (loopback). Default isolation for untrusted
   toolkits remains subprocess; `proc.exec` / `patch.apply` remain container-tier (SPEC §3).
3. **ADR-0005 stands for v0.6.** Registries freeze at composition. Unknown names fail at
   compose, not at runtime. Mid-run composition change is forbidden. Quiesce/checkpoint exist
   for restart and fault, not for hot-swap of the FrozenHarness. SPEC §2.1 hot-swap text is
   struck for v0.6.
4. **Five frozen SPIs** remain (ADR-M0-03): `IPlanner`, `IMemoryEngine`, `IToolkit`,
   `IContextManager`, `IEvaluationGate`. First-party `IModelProvider`, `ISandbox`, and store
   ports stay first-party until a later wave. A sixth SPI requires a design review, not a PR.
5. **Mechanism vs strategy.** Below the plugin line: identity, authority, effect mediation,
   event semantics, resource conservation, plugin lifecycle, scheduling mechanism. Above:
   planner, memory, context, compression, cache strategy, indexing, AST, heuristics, tools,
   skills, model routing, reflection, and (later) Meta-Harness strategies.
6. **Evaluator is not a product plugin.** The signed judge remains an exterior daemon
   (UID-separated, unreachable from agency and from plugin cells). `IEvaluationGate` only
   *requests* judgment and gates on **signed** `VerdictRecorded` events. Scheduler code that
   emits `payload={"verdict": "pass"}` without reading a signature (`layer0/scheduler/driver.py:138-139`)
   is defect F1, not an isolation strategy.
7. **Ceilings fail closed.** Empty plugin capability lists do not authorize execute. Capability
   ceilings are part of `FrozenHarness`. `compose()` MUST persist the intersection, not the
   harness list alone. Walking-skeleton echo plugin (ADR-M0-13) MUST traverse the lifecycle on
   the canonical path before product plugins are migrated.

Protobuf/gRPC, WASM-default isolation, and container-per-plugin as the only tier are not v0.6
requirements.

**Alternative considered (and rejected).**

- Keep SPEC hot-swap as a v0.6 feature. Rejected: contradicts ADR-0005; no implementation; would
  break `D_H` attribution mid-run.
- Protocol-only in-process SPIs as the contract. Rejected: not polyglot; parecer diagnosis is
  correct even where its plugin roster is not.
- Evaluator as a replaceable product plugin. Rejected: ADR-0004, ADR-M0-08, separability thesis.
- WASM as default cell. Rejected: no wasmtime stack; hardening, not blocker (forensic §15).

**Evidence / bound test / links.** Forensic §§12–13, 17, 19 P0-8/P0-9; ADR-0002; ADR-0004;
ADR-0005; ADR-0059; ADR-M0-03; ADR-M0-08; ADR-M0-13; `layer0/spi/jsonrpc.py`;
`layer0/spi/ceiling.py:21-22`; `layer0/compose/compiler.py:54-79`. Bound tests (code phase):
forged verdict rejected; missing grant denied; capability widening denied; fail-open ceiling
impossible; walking-skeleton lifecycle ledgered. `REQ-TRUST-001`.

**Reversal condition.** A newer ADR that (a) replaces UDS/JSON-RPC with another wire after a
measured interoperability failure, or (b) permits mid-run composition change with a new
attribution scheme that preserves `D_H`/`D_R` without collapsing them. Replacing the exterior
judge with an in-agent plugin is not available as reversal without also reversing ADR-0004.

**Owner · status.** Principal Staff Engineer / Tech Lead · accepted · 2026-08-20 · accepted

---

## Amendment — 2026-08-23: wire parity without in-process transport overhead

Clause 2's “same wire (loopback)” means schema and method-semantic parity, not mandatory byte
transport. The trusted `in_process` tier dispatches generated typed values directly in memory after
the same schema-boundary validation and MUST NOT open a UDS, serialize JSON, or copy heavy context
bundles merely to simulate an out-of-process boundary. Subprocess and container tiers continue to
use line-delimited JSON-RPC 2.0 over UDS. This optimization creates neither a second SPI nor a second
payload dialect; RF-37 still requires explicit policy for the isolation privilege.
