# Wave 3 — Extensibility Foundation (plugins on the canonical path)

**Outcome:** New capability enters through manifests, plugins, and policy — proven by a trivial
plugin traversing the full lifecycle on the production path before any real plugin migrates
(ADR-M0-13, the walking-skeleton rule).
**Entry:** Wave 2 exit green (wire + lifecycle FSM live in packages; one selector algebra).
**Exit (M-3):** echo plugin walks DISCOVERED → RESOLVED → VERIFIED → ACTIVATED → QUIESCING →
RETIRED over UDS with every transition ledgered; `code-default` toolkits load through the same
lifecycle; I-7 holds everywhere.

## Sprint 3.1 — Walking skeleton

| # | Task | Where | Acceptance evidence | Readiness |
|---|---|---|---|---|
| 3.1-A | Registry lifecycle FSM on packages: absorb `layer0/registry/` semantics into `runtime/registry/`; every transition is a `Plugin*` event through the registry-role emitter facade | `runtime/registry/` | FSM property tests; ledger shows the full trail; only the registry can append plugin kinds (F-05 family) | READY |
| 3.1-B | Compose v2 wired to the registry: `plugin.yaml` discovery → resolve (semver caret) → verify (schema + ceiling policy) → freeze; unknown ref fails at compose, never at runtime (ADR-0005/0072) | `runtime/compose.py` | Unknown-ref and empty-ceiling negatives; frozen `D_H` includes plugin digests (F-11 recheck) | READY |
| 3.1-C | Echo plugin: subprocess cell, JSON-RPC over UDS, one `echo` verb, declared ceiling; full lifecycle then fault injection (kill the cell → `PluginFaulted`, crash-loop backoff) | `packs/` or `test/fixtures/` echo dir | ADR-M0-13 gate: lifecycle + fault trail ledgered on the canonical path; no hot-swap path exists (ADR-0072 §3) | READY |
| 3.1-D | Isolation broker: subprocess tier with rlimits (seccomp profile may land as a follow-on hardening task, not a gate) | `runtime/registry/` broker + `adapters/sandbox/` | Cell cannot exceed declared rlimits; `in_process` requires an explicit policy grant (I-6) | TECH-LEAD (scope the rlimit set) |

## Sprint 3.2 — The pack on the wire

| # | Task | Where | Acceptance evidence | Readiness |
|---|---|---|---|---|
| 3.2-A | `code-default` toolkits (fs, ast-patch, terminal, index) load through discovery→freeze as real plugin cells (subprocess tier; `proc.exec`/`patch.apply` still execute container-tier per SPEC §3) | `packs/code-default/` | `test/packs` green through the lifecycle path, not direct imports | READY |
| 3.2-B | Coding-token sweep: any residual coding behavior in `domain/`/`kernel/` moves to `packs/`/`apps/`; F-18-extended linter enforces I-7 on both trees | repo-wide | `check_domain_blindness.py` green on its widened surface | READY |
| 3.2-C | Manifest loader convergence: `agency/manifests/loader.py` and compose v2 share one manifest parse (no second YAML→harness path) | `agency/manifests/`, `runtime/compose.py` | Duplication detector green; one parser | DEV-LOCAL (layout) |

**Deliberately not in scope:** wasm tier, plugin signatures as mandatory policy, model/sandbox
behind the wire (P1-11/12 deferred), any second plugin beyond echo + the existing pack.
