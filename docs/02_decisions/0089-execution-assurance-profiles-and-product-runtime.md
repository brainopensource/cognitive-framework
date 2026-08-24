---
id: adr-0089-execution-assurance-profiles-and-product-runtime
adr: 0089
class: decision
authority: binding-decision
canonical_for:
  - execution-assurance-profiles
status: accepted
owner: principal-architect-specialist
version: "0.6.3"
last_verified: 2026-08-24
accepted_date: 2026-08-24
extends:
  - ADR-0088
supersedes: []
superseded_by: null
---

# ADR-0089 — Execution/assurance profiles and the product runtime seam

## Status and scope

**Accepted by the Engineering Director on 2026-08-24.** This is the W3D-00 deliverable of the Principal Architect Specialist lane defined
in `TODO_W-3D_final.md`, which is itself a non-canonical planning artifact per its own §1: it does not
authorize implementation, does not alter the Law, and does not close M-4. This document is the minimal
ADR that artifact calls for and is now binding.

The current Director decision recorded in `docs/03_execution/sprint_active.md` (2026-08-24) is that
M-4 is **PAUSED** for RF-85 execution while W-3D requalifies the product runtime. RF-85 preparation
at `1a1ed6c` remains retained evidence; no RF-85 row may be claimed during W-3D. This ADR opens
**W-3D Product Runtime Profiles** as a corrective wave before M-4 release execution and does not
authorize M-5+ work.

## Context — verified against code at `9a31035`

Three falsifiable defects were checked directly against source, not inferred from planning prose:

1. **Deployment selection is inlined in the execution path, duplicated across two files.**
   `vanguard/packages/runtime/root.py:74-146` takes `release: bool` and `sandbox_mode: str` on the
   public entry, validates `sandbox_mode in {"rootless", "host-dev"}` at line 88-89, and at line
   101-118 directly constructs `RootlessSandboxRunner` (imported at line 18) or a host-dev environment
   inline — the composition root is not the only place this decision is made.
   `vanguard/packages/runtime/lab_driver.py:83,199,215,383-420,467-478` repeats the identical
   `sandbox_mode` parameter, the identical `{"rootless", "host-dev"}` validation, and its own
   `RootlessSandboxRunner` construction. A third caller would repeat it again. This is a real
   duplication defect (`runtime` composing environment inline rather than through one seam), separate
   from any security gap — see point 3 below for what the D_R preimage already captures correctly.

2. **Plugin activation defaults production to `cell=None`.**
   `vanguard/packages/runtime/activation.py:217-260`: `activate()`'s `build` parameter defaults to
   `None`, and line ~247 computes `cell = build(step) if build is not None else None`. The one production
   caller, `vanguard/packages/runtime/root.py:204-208`, calls `activate(activation, emitter=...,
   run_id=..., principal=...)` — it does not pass `build`. Every component activated on the public path
   today therefore carries `cell=None`: the lifecycle FSM (`PluginDiscovered → … → PluginRetired`)
   proves components were walked and torn down in order, but does not prove any service was
   materialized or that `HarnessSession` consumes it (`HarnessSession` builds bindings/kernel/context
   compiler/operator/index/approval flow directly instead).

3. **The CLI's coding entrypoint module does not exist.**
   `vanguard/clients/client-core/src/application/coding-commands.ts:51` resolves
   `options?.module ?? "vanguard.packages.runtime.coding_entrypoint"` and spawns it as a Python module.
   No `coding_entrypoint.py` exists anywhere under `vanguard/packages/runtime/` (confirmed by
   repository-wide search); only `root.py`, `lab_driver.py`, `dogfood.py`, `scoring.py`, `repair.py`,
   `explain.py` do. `vg code` therefore points at an entrypoint that has never existed in this tree.

**Correction to the source document's diagnosis, checked against code:** `TODO_W-3D_final.md` §2.1
implies the environment/deployment axis is entirely absent from `D_R`. That overstates the gap.
`vanguard/packages/runtime/run_plan.py:34-87` already folds `environment` (derived from
`ports.environment.containment_report` via `_environment_identity()` in `root.py:270-286`), `store`,
and `model_route` into the `run_digest` preimage as independent fields — changing sandbox backend or
store already changes `D_R` today, because it changes the environment adapter's `containment_report`.
What is genuinely missing from `D_R` is a **single identity-bearing profile** covering approval policy,
persistence mode, evaluation mode, assurance level, and capture/trainability policy as one resolved,
versioned value — those axes have no field in `RunPlan` at all, and the *selection* of environment
still happens by inline branching in two files rather than through one resolved seam. The defect is
architectural (composition root discipline, SPI activation, entrypoint existence), not a hole in
`D_R`'s existing coverage of environment/store/model identity.

This distinguishes three things the current Law conflates in places (`RUNTIME.md §3` states every
`proc.exec`/`patch.apply` passes through the container tier; `K-46` already permits visible
non-contained local degradation): isolation of untrusted plugin code, containment of an agent-requested
effect, and the assurance required to promote a result. This ADR's job is to make that distinction
explicit in law, not to weaken any of RF-78–RF-85's existing containment/evaluator/WAL requirements.

## Decision

1. **`ExecutionProfile` becomes an explicit, orthogonal, identity-bearing configuration value**,
   distinct from `D_H`. Fields that alter execution (workspace access, process backend, network,
   approval defaults, persistence mode, evaluation mode, assurance level, capture policy) enter the
   `RunPlan`/`D_R` preimage as one profile digest, in addition to (not replacing) the existing
   `environment`/`store`/`model_route` fields already covered by point 3 above. No production path may
   select or change the effective profile without that digest changing; a change that alters observed
   behavior while leaving `D_R` unchanged is a defect (RF-87).
2. **Composition selects effect scope; deployment selects containment.** A single `RuntimeBootstrap`
   seam becomes the only place authorized to construct concrete adapters (model, store, filesystem,
   process/sandbox backend, evaluator, approver) from resolved config + profile. `root.py` and
   `lab_driver.py` stop constructing `RootlessSandboxRunner`/host-dev environments inline; they call the
   bootstrap. This removes the duplication in point 1 without changing containment guarantees.
3. **Filesystem reads/search are not process containment.** `fs.read`/`fs.search`/structured
   `patch.apply` are path/capability-checked in-process; only `proc.exec` (arbitrary subprocess) is
   routed through the profile's process backend. `bwrap` qualification runs once per
   runner/session, not once per call.
4. **Plugin activation must materialize real services in production**, or the SPI is retired as
   non-consumed. `activate()`'s production caller must pass a real `build`; `cell=None` in the
   production path becomes a falsifiable defect (RF-93), not the default.
5. **`local`, `sandboxed`, and `hermetic` are named profile presets**, not a `trust_tier` scalar.
   `local` is host-explicit and never RF-85/promotion eligible. `sandboxed` fails closed
   (`sandbox_unavailable`) rather than falling back to host when the requested backend is absent.
   `hermetic` keeps every existing RF-85 requirement — preregistration, exterior Ed25519 evaluator,
   file-backed WAL, fail-closed absent/forged rules — unreduced. No profile silently degrades another.
6. **WSL2 (or any host) is qualified by capability probes, not denied by platform name.** `RUNTIME.md`
   §3's blanket "every `proc.exec`/`patch.apply` passes through the container tier" is replaced by
   routing through the resolved profile's backend, with `hermetic` failing closed if the qualifying
   probes (namespace, evaluator isolation, WAL) do not pass — this does not relax RF-85; it removes a
   name-based refusal that the Law does not actually require.
7. **A generic `runtime/entrypoint.py` replaces the nonexistent `coding_entrypoint` reference.**
   `vg code` and `vg explain` become two agents (`code-default`, `code-explain`) composed from the same
   plugins through the same bootstrap and the same `Runtime.run_composed`, not two engines. The CLI
   fix corrects a broken reference; it does not add a new capability surface.
8. **The durable event store remains the sole truth; any live stream is fan-out/replay over the same
   persisted envelope**, never a second ledger. This preserves the existing `LedgerEmitter` writer
   authority; it only forbids `RuntimeService` from inventing a second event identity for streaming.

## Non-goals (explicitly out of scope for this ADR)

- Does not reduce, relax, or reinterpret RF-78–RF-85. `hermetic` keeps every existing requirement.
- Does not open `agent.spawn` (M-6/RF-55–RF-59), concurrency (M-7/RF-46–RF-48), or topology (M-8/RF-65–
  RF-66). I-11's unary sequential mechanism is unchanged.
- Does not introduce a `trust_tier` scalar, a `BaseAgent`/`BaseTool`/service-locator base class, or new
  `AgentSpec`/`FlowSpec` types. `FrozenComposition` remains the sole identity-bearing agent definition.
- Does not change the kernel, S0–S12, JCS/canonicalization, grant algebra, writer authority, or the
  Ed25519 trust root.
- Does not touch `_archive/` (001, 006, Higgs remain provenance, not documentation).

## RF allocation

This accepted ADR allocates `RF-87`–`RF-94` to W-3D.

| RF | Negative proof | Owner lane |
|---|---|---|
| RF-87 | profile selection outside `D_R`, or a profile change that leaves `D_R` unchanged, fails | Architect |
| RF-88 | `sandboxed`/`hermetic` requested and unavailable must not execute on host | Architect |
| RF-89 | a qualified WSL2 host is not denied by platform name; an unqualified WSL1/host cannot claim containment | Staff |
| RF-90 | `vg code`/`vg explain` reach one real entrypoint/runtime; a missing module/agent fails loudly | Staff |
| RF-91 | code/explain share tool/model/context implementations; explain never receives write/exec | Staff |
| RF-92 | persisted and streamed events are the same envelope/seq; reconnect neither duplicates nor drops | Architect |
| RF-93 | a component activated in production has a real service/handle and is closed in reverse order | Architect |
| RF-94 | no lab/CLI/daemon/repair/scoring path runs a second, competing loop/driver | Architect |

## Rollback

Rollback target is the frozen baseline at `1a1ed6c` (RF-85 preparation gate, current `sprint_active.md`
truth). Every W3D-01…W3D-12 slice in the source planning document is a separately revertible commit
series; none may depend on deleting the legacy path in the same commit that introduces the new one.
Reverting this ADR reverts to inline `sandbox_mode`/`release` selection in `root.py`/`lab_driver.py`
and re-opens RF-87–RF-94 as unallocated.

## Decision rights

The Engineering Director ratified W-3D on 2026-08-24. The affected law leaves and execution board
are amended in the same change so this ADR has one canonical next-step authority.
