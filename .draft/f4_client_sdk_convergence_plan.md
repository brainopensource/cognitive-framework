# F4 — Client SDK Convergence: Incremental Migration Plan (Draft)

> Status: drafted 2026-08-31, not yet authorized for execution. Companion to `.draft/frontend_backend_integration_full_plan.md` (this is the detailed breakdown of that plan's F4 phase). Written after F0 (wire contract freeze), F1 (single causal ledger), and F6 (Studio Observatory live wiring, verified end-to-end against a real gateway) shipped in `vanguard/clients/contracts` and `vanguard/clients/studio`.

## Context

Studio and the CLI both currently depend on `@vanguard/client-core` for everything beyond wire-level types. Investigation for this plan found the real gap is narrower and more specific than "swap the import": `@aether/client` already has working equivalents for the *transport* layer (`SocketRuntimeClient`, `HttpRuntimeClient`, `ReplayRuntimeClient`, `OperatorSigner`, `WebCryptoSigner`, plus a `ManagedRuntimeHost` client-core has no equivalent for at all). What `@aether/client` is missing entirely is client-core's **application layer** — 17 small modules under `client-core/src/application/` holding derivation/selector/command-orchestration logic with no port to `@aether/client` yet. `studio/src/contract/index.ts` already funnels every one of Studio's client-core imports through a single seam file, which is what makes an incremental, file-by-file migration possible without a big-bang rewrite.

Studio uses 12 of the 17 application modules (`run-view`, `approvals`, `budget`, `coding-types`, `coding-receipts`, `corrections`, `selectors`, `trace-graph`, `subscribe-run`, `projection-model`, `graph-model`, `mcnemar`). The CLI additionally needs the 5 CLI-specific ones (`attach`, `commands`, `coding-commands`, `resume`, `why`) that Studio never imports. `contract/types.ts` and `contract/parse.ts` (344 lines) are the wire-type layer, already functionally superseded by the just-frozen `@aether/contracts` — but not identical: field names differ (e.g. `StartRunRequest.repo`/`.prompt`/`.manifest` in client-core vs. `.repoPath`/`.brief`/`.manifestPath` in the vg.4 wire contract), so this isn't a pure rename either.

## Module inventory

| Module | LOC | Depends on | Used by | Complexity |
|---|---|---|---|---|
| `contract/types.ts` | 182 | — | everything | Foundational — field-shape reconciliation needed against `@aether/contracts` |
| `contract/parse.ts` | 162 | `contract/types` | everything | Foundational |
| `contract/canonical.ts` | 18 | — | contract/* | Trivial |
| `application/run-view.ts` | 65 | `contract/types` (EventEnvelope only) | Studio | Leaf |
| `application/trace-graph.ts` | 64 | `contract/types` (EventEnvelope only) | Studio | Leaf |
| `application/budget.ts` | 51 | — | Studio, `coding-receipts` | Leaf |
| `application/coding-types.ts` | 104 | — | Studio, `coding-receipts` | Leaf |
| `application/graph-model.ts` | 31 | — | Studio | Leaf |
| `application/mcnemar.ts` | 99 | — | Studio | Leaf |
| `application/projection-model.ts` | 56 | — | Studio | Leaf |
| `application/approvals.ts` | 23 | `contract/{types,parse}` (`RuntimeClient`) | Studio | Low — needs `RuntimeClient` shape |
| `application/corrections.ts` | 37 | `contract/{types,parse}` (`RuntimeClient`) | Studio | Low |
| `application/subscribe-run.ts` | 36 | `contract/types` (`RuntimeClient`) | Studio | Low |
| `application/selectors.ts` | 73 | `run-view.ts` | Studio | Low — depends on one already-ported leaf |
| `application/coding-receipts.ts` | 85 | `budget.ts`, `coding-types.ts` | Studio | Medium — depends on two leaves |
| `application/resume.ts` | 33 | `contract/{types,parse}` | CLI | Low |
| `application/why.ts` | 24 | `contract/types` | CLI | Low |
| `application/commands.ts` | 208 | `contract/types` (`RuntimeClient`) | CLI | Medium — CLI command orchestration |
| `application/coding-commands.ts` | 170 | `commands.ts`, `coding-receipts.ts`, spawns a Python subprocess directly | CLI | High — has its own direct-spawn path (flagged in the archived F4 note as needing a decision: keep, port, or replace with the UDS/HTTP RuntimeService path) |
| `application/attach.ts` | 24 | `adapters/signer`, `adapters/live`, `adapters/transport` | CLI | Medium — this is the daemon-lifecycle glue `@aether/client`'s `ManagedRuntimeHost` is meant to replace, not just port |
| `adapters/*` (8 files, 1512 LOC total) | — | `contract/*` | Studio (indirectly), CLI | **Not migrated module-by-module** — `@aether/client`'s transports/signers already supersede these; see Phase 0 below |

## Dual-compatibility strategy

Two seams make this safe to do incrementally, and neither requires a feature flag or a big-bang cutover:

1. **Studio's `contract/index.ts` seam.** Every Studio file already imports from `../contract/index.js`, never directly from `@vanguard/client-core`. Migrating a module means changing one `export * from "@vanguard/client-core/application/X.js"` line in that one file to `export * from "@aether/client/application/X.js"` (once that module exists there) — zero changes to any Studio UI/runtime file, because the seam absorbs the source change.
2. **Client-core becomes a re-export shim, module by module.** Once a module is ported to `@aether/client` and verified, the original `client-core/src/application/X.ts` is replaced with `export * from "@aether/client/application/X.js"` (plus any field-name adapter needed — see below) rather than deleted outright. This keeps any consumer that still imports `@vanguard/client-core` directly (there may be others outside Studio/CLI we haven't audited) working unchanged, with zero duplicate implementations after the swap — the shim has no logic of its own, just a re-export. Delete the shim file only in the final cleanup phase, after confirming (via a repo-wide grep) nothing imports it anymore.

This means at every point in the migration, both `@vanguard/client-core` and `@aether/client` resolve to **the same code**, just via different entry points — there is never a window where the two packages disagree, which is the actual risk a big-bang rewrite would carry.

### Reconciling `contract/types.ts` field-name drift

`client-core`'s `StartRunRequest` (`repo`/`prompt`/`manifest`) doesn't match the vg.4 wire contract's field names (`repoPath`/`brief`/`manifestPath`, already frozen in `@aether/contracts` and `validate-command.ts` from F0). Two options, pick one at Phase 2 kickoff rather than deciding in the abstract now:
- **(a) Adapter function**: keep `@vanguard/client-core`'s public `StartRunRequest` shape as the compatibility surface, and have the re-export shim's `startRun` wrapper translate field names before calling `@aether/client`'s `HttpRuntimeClient`/`SocketRuntimeClient`. Zero call-site changes anywhere, but keeps a translation layer alive indefinitely.
- **(b) Rename at the source**: fix the handful of `StartRun` call sites in Studio/CLI to use the wire-canonical field names directly, and drop client-core's field names entirely once those call sites are gone. Fewer moving parts long-term, but touches call sites instead of hiding behind the shim.
Recommendation: (a) during the migration (keeps every other phase call-site-free), then a dedicated small cleanup step at the very end of Phase 5 to do (b) and delete the adapter — don't carry a permanent translation layer.

## Phased plan

### Phase 0 — Adapter inventory checkpoint (no code changes)
Confirm `@aether/client`'s `SocketRuntimeClient`/`HttpRuntimeClient`/`ReplayRuntimeClient`/`OperatorSigner`/`WebCryptoSigner` are functionally equivalent to client-core's `adapters/{live,http,replay,scenario,fake,signer,web-signer}.ts` before relying on them in later phases — diff behavior against the existing `@aether/client` test suite (15 tests, already green) and client-core's own adapter tests. `adapters/fake.ts`/`scenario.ts` (demo/test doubles) may have no `@aether/client` equivalent yet — confirm and, if missing, port them in this phase since Studio's `browser-entry.tsx` demo mode depends on `FakeRuntimeClient`.

**Test criteria**: `@aether/client` test suite green (already is); a new small parity test asserting `SocketRuntimeClient`/`HttpRuntimeClient` and their client-core equivalents produce identical `Result` shapes for the same StartRun/Cancel/GetRun commands against a shared test gateway (reuse the `test_transport_parity.py`-style pattern, or a lighter TS-side version driving both clients against one `studio_gateway.py` instance).

### Phase 1 — Leaf modules (no cross-module or `RuntimeClient` dependencies)
Port in this order (each is fully independent, can go in parallel or any order): `run-view.ts`, `trace-graph.ts`, `budget.ts`, `coding-types.ts`, `graph-model.ts`, `mcnemar.ts`, `projection-model.ts`.
For each: copy the module into `vanguard/clients/client/src/application/<name>.ts`, add it to `@aether/client/src/index.ts`'s exports, flip the one line in Studio's `contract/index.ts`, replace the client-core original with a re-export shim.

**Test criteria per module**: (1) the module's own existing behavior is exercised by Studio's existing test suite (`studio.test.ts`, 11 tests) — run it after each flip, must stay green with zero test changes, since output is byte-identical code; (2) a one-line `assert.deepEqual` parity check per module comparing `@vanguard/client-core`'s (now-shimmed) export identity against `@aether/client`'s, added to a new `vanguard/clients/client/test/client-core-parity.test.ts`, to catch a future accidental fork; (3) `npm run typecheck` clean across `client-core`, `client`, `studio`.

### Phase 2 — `RuntimeClient`-dependent low-complexity modules
`approvals.ts`, `corrections.ts`, `subscribe-run.ts` (all just need `RuntimeClient`/`EventCursor`/`StreamItem`/`CommandReceipt` types — this is where the `contract/types.ts` field-name reconciliation from above actually gets exercised, since these call `client.resolveApproval`/`client.recordCorrection`/`client.streamEvents`). Also port `resume.ts` and `why.ts` here (CLI-only, same low complexity, no reason to wait for the CLI-specific phase).

**Test criteria**: same three checks as Phase 1, plus a targeted test that `approvals.ts`/`corrections.ts`/`subscribe-run.ts` ported into `@aether/client` still correctly call through to a `SocketRuntimeClient`/`HttpRuntimeClient` instance end-to-end (reuse `test_transport_parity.py`'s live-gateway pattern from the TS side — this is the same shape of test as the F6 `live-observatory.test.ts` added this pass, just exercising `ResolveApproval`/`RecordCorrection`/`StreamEvents` instead of the Observatory fold).

### Phase 3 — Modules with intra-application dependencies
`selectors.ts` (depends on the now-ported `run-view.ts`), `coding-receipts.ts` (depends on the now-ported `budget.ts` + `coding-types.ts`). Port only after Phase 1 confirms their dependencies are stable in `@aether/client`.

**Test criteria**: same as above, plus explicitly re-run the Phase 1 parity tests for `run-view`/`budget`/`coding-types` first (regression guard: a Phase 3 port must not require reopening a Phase 1 module).

### Phase 4 — CLI-specific composite and lifecycle modules
`commands.ts` (CLI command orchestration), `coding-commands.ts` (has its own direct Python-subprocess-spawn path — per the archived plan, decide here whether to keep that spawn path, port it as-is into `@aether/client`, or replace it with the UDS/HTTP `RuntimeService` path now that F1 guarantees one causal ledger regardless of transport; recommend replacing it, since a second write path is exactly what F0/F1 this pass eliminated on the read side — don't reintroduce one on the write side), and `attach.ts` (daemon-lifecycle glue — this one is **not a straight port**: `@aether/client`'s `ManagedRuntimeHost` already does more than `attach.ts` does — spawn, health-state machine, auto-restart. Phase 4's job here is to replace `attach.ts`'s callers with `ManagedRuntimeHost` directly, not to port `attach.ts` unchanged).

**Test criteria**: CLI's existing test suite (10 files) green after each swap; a new integration test that starts the CLI's daemon lifecycle through `ManagedRuntimeHost` end-to-end (spawn → `RUNNING` → command round-trip → `stop`) since this is new behavior, not a port, and needs its own coverage rather than reusing an existing client-core test.

### Phase 5 — Cutover and cleanup
1. Flip `vanguard/clients/cli/package.json`'s dependency from `@vanguard/client-core` to `@aether/client` + `@aether/contracts`; update all 5 files under `cli/src/adapters/` from re-exporting client-core to re-exporting `@aether/client`.
2. Flip Studio's `package.json` dependency the same way; collapse `studio/src/contract/index.ts` to re-export from `@aether/client`/`@aether/contracts` directly.
3. Do the `StartRunRequest` field-name cleanup deferred from earlier (option (b) above): fix call sites, delete the adapter.
4. Repo-wide grep for any remaining `@vanguard/client-core` import outside `client-core`'s own package. If none, delete the re-export shims and mark `@vanguard/client-core` deprecated in its `README.md` (don't delete the package itself in this pass — a grace period for anything this plan's audit missed).

**Test criteria**: full `just verify` (or `npm run typecheck && npm test` across every workspace) green; `cli`'s and `studio`'s own test suites green with **no test file changes** required beyond what Phases 1–4 already added (proof the migration was behavior-preserving); a final smoke pass through the dossier's §14 manual runbook (start daemon, start run, stream events, resolve approval) against both CLI and Studio.

## Suggested execution order and rollback

Phases 1 → 2 → 3 can proceed with tight verification loops (each module is a small, independently revertible commit — `git revert` one module's commit if its parity test fails, without touching the others). Phase 4 is the highest-risk phase (the `attach.ts` → `ManagedRuntimeHost` swap and the `coding-commands.ts` spawn-path decision are behavior changes, not ports) and should get its own review checkpoint before Phase 5's cutover. Phase 0 should run first as a cheap confirmation before committing to the rest.

## Out of scope for this migration

Desktop's own `@aether/client` usage is already on the target SDK (confirmed in earlier exploration — `desktop/src/main.ts` already calls `createRuntimeClient` from `@aether/client`), so desktop needs no migration work here. Tauri packaging, release CI, and any further F2/F3/F5/F7/F8 roadmap items remain in `.draft/frontend_backend_integration_full_plan.md`, untouched by this plan.
