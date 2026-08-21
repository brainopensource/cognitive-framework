---
id: SPRINT-V060-FOUNDATION-BOARD
file: docs/03_sprints/sprint_active.md
title: "Active board — v0.6.1 Foundation (M-2 evidence integrity in flight)"
status: ACTIVE
milestone: M-2 / v0.6.1 — RF-23 NOVA-1 + RF-25 NOVA-2 in flight
spec: docs/SPEC.md
law: ADRs 0069–0084 + docs/04_annex/
register: docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md
plan: wave2C_todo.md
last_reviewed: 2026-08-21
---

# Active board — v0.6.1 Foundation

**Start here if you are new:** read [`README.md`](../../README.md) and [`SPEC.md`](../SPEC.md) first — they name
production truth, the one flow, and the canonical decisions.

## Now

| Lane | State | Who |
|---|---|---|
| **Wave 0 — CI truth + falsifiers** | CLOSED (M-0) | — |
| **Wave 1 — Trust spine** | **CLOSED — M-1 GREEN** | plan: [`done/wave1_trust_spine.md`](done/wave1_trust_spine.md) |
| **Wave 2 — Convergence core** | **DONE; Round-4 evidence retained** | plan: [`done/wave2_convergence.md`](done/wave2_convergence.md) |
| **Wave 2C — Evidence integrity** | **OPEN — M-2/v0.6.1 active lane** | plan: [`wave2C_todo.md`](../../wave2C_todo.md) |
| **Wave 3 — Extensibility** | QUEUED — entry: M-2 green, including RF-23/RF-25 | plan: [`doing/wave3_extensibility.md`](doing/wave3_extensibility.md) |
| **Wave 4 — Foundation E2E** | QUEUED — entry: M-1 + M-2 + M-3 | plan: [`doing/wave4_foundation_e2e.md`](doing/wave4_foundation_e2e.md) |

### Director ratification — 2026-08-21

ADRs [`0077`](../05_adr/0077-named-component-graph-manifest.md) through
[`0084`](../05_adr/0084-compounding-macro-tools-active-inference.md) are accepted. Their canonical
map is in the [`ADR index`](../05_adr/INDEX.md#tier-s-evolution-contract-00770084). Acceptance fixes
the long-horizon design; it does not move deferred implementation before its milestone.

The previous M-2 Round-4 submission remains valid evidence for the original convergence scope,
but it does **not** close M-2 under the ratified content/continuation law. The Engineering Director
opens **Wave 2C** and binds M-2/v0.6.1 closure to exactly two primary falsifiers:

| Gate | Decision | Required red-to-green proof | Owner | State |
|---|---|---|---|---|
| **RF-23 / NOVA-1** | ADR-0078 | A completed invoked episode emits a populated `mhf.trajectory/1`: attributable model route, explicit measurement status, conserved per-turn/episode cost, proper `D_H/D_R/D_X`, receipts/evidence, and derived eligibility. | Developer A | **READY — WRITE RED FIRST** |
| **RF-25 / NOVA-2** | ADR-0082 | A file-backed SQLite WAL run loses all live process state, reconstructs and legally continues in a fresh interpreter, preserves budgets/digests, and neither repeats settled effects nor guesses unresolved effects. | Developer B | **READY — WRITE RED FIRST** |

RF-24 (cost-writer authority) and RF-27 (digest separation) are supporting assertions under RF-23;
they do not create additional M-2 scheduling lanes. Production changes begin only after the named
tests demonstrably fail for the diagnosed reasons. M-3 remains closed until both primary gates and
all pre-existing M-2 gates are green and the Tech Lead signs the re-gate.

**Immediate file ownership:** Developer A owns the trajectory schema/writer/session accounting
surface. Developer B owns the fresh-process continuation test and recovery surface. If both need
`runtime/session.py`, Developer B proposes the narrow resume interface first and Developer A lands
or approves the shared seam; neither branch invents a second session engine.

### Wave 2 convergence assignment slices (completed history)

The assignments below record the completed convergence work; do not pick them up again. Sprint
2.1's tasks were independent moves; 2.2 depended on all of 2.1. Wave 3's entry is **not**
relaxed — 3.1 builds on the wire and lifecycle that 2.1 lands, so starting it early would fork the
very duplication Wave 2 exists to remove.

- **Developer A (the wire):** 2.1-A (jsonrpc → `domain/wire/`), 2.1-B (codegen target + shim),
  2.1-C (SPI Protocols → `ports/spi.py`). One import surface, one owner.
- **Developer B (the algebra + detector):** 2.1-D (ceiling delegates to `domain/selectors/`,
  fail-closed — the domain side already exists as `ceiling_allows`/`intersect_ceilings` from 1.3-B,
  so this is delegation, not a second implementation), 2.1-E (duplication detector hardening).
- **Then together:** 2.2-A parity triage (Tech Lead signs the keep/kill list), 2.2-B deletion —
  A owns every `layer0` removal, nobody else edits `layer0/` while it is open — 2.2-C `root.py`
  split along the named seams, 2.2-D linter extension.
- **Shared rule:** no new `from layer0` imports in `vanguard/packages/`. Wave 2 removes the
  remaining ones; adding one reopens M-2.

### Wave 1 exit — Tech Lead adjudications (settled, do not reopen)

| Item | Decision |
|---|---|
| **F-08 ambiguity** | **Stale falsifier, not a production defect.** The test dispatched a fully authorized `fs.write` and asserted `failure is not OK` — it asserted the grant path must fail on its own happy path. The kernel is correct: S6 issues via `SinkRegistry.requires_grant`, S8 re-verifies against the descriptor digest at the point of effect (`K-05`), S8a records `grantId`/`grantDigest` in durable intent. Restated in both directions in `test/falsifiers/`. No kernel change. |
| **Falsifier subject of record** | F-01, F-03, F-07, F-09, F-10, F-12 were measuring `layer0/` (or a file-exists probe). Repointed onto `vanguard/packages/`. M-1 must not be gated on defects the plans defer to Wave 2. |
| **1.2-C `project_id`** | **Config-declared** (`TaskContext.project_id`), never workspace-derived. A workspace fingerprint makes `prev_digest` a function of where the repo sits, forking the chain on every clone/move/mount and leaving cold replay (F-02) unable to reattach. |
| **1.3-C kernel diff** | **Accepted.** `_exceeds` is called only on additive dimensions (`max_bytes`, `max_effects`); `max_depth` is compared directly, since depth is a structural ceiling and absent from `Reservation.as_map()`. The changed branch can only turn allow→deny. Net TCB delta 0; gate at 1359/1438. |
| **`test/kernel/test_replay_parity.py` deletion** | **Correct.** It folded a same-list of in-memory envelopes — exactly the mechanism I-4 / ADR-0071 forbid as replay evidence. Replaced by `ColdReplayParity` in `test/runtime/test_ledger_truth.py`, folding from a real WAL file in a fresh process, and wired as its own CI job. |

### 2.2-A parity triage — **GREEN. 2.2-B/C AUTHORIZED** (Tech Lead)

Keep/kill settled in [`plans/wave2_convergence.md`](plans/wave2_convergence.md). The one blocker is
closed; deletion may proceed against the scope named there.

**Blocker closed — selector conformance (Developer B).** Verified: the correction is entirely in
*declarations and call sites*. `domain/selectors/resource_selector.py`, `adapters/sandbox/ceiling.py`,
`domain/wire/` and `vanguard/packages/kernel/` are **byte-unchanged** — no relaxation, no second
dialect, no normalisation shim. The pack now declares `paths: ["/workspace"]` and expresses
`proc.exec` as `{kind: generic, uriPattern: "proc://exec/allow/git,pytest,ruff,python3"}`, matching
`vg-code-default/manifest.json`; `DefaultPlannerAdapter` and `DriveUntilGreenPlanner` emit the same
canonical shapes. `test/registry` 26 green, `test/packs` 27 green, new
`test/packs/code_default/test_capability_selectors.py` pins parse, inclusion, `/etc` denial, empty
ceiling, legacy-`proc` rejection, and host-gate/domain agreement. `SELECTOR_KINDS` still excludes
`proc`; empty ceiling still returns `empty_ceiling`; `{kind: proc}` still raises.

Two items found during this review and fixed here: the `test/adapters` CI step had been dropped
while adding `test/registry` (caught by F-17, restored), and the layer0 CI step's comment claimed
deletion at 2.2-B — per the triage it **shrinks** at 2.2-B and is deleted at 3.1.

Follow-up, not blocking: `_PROC_PATTERN` is a literal in `adapters/models/planner.py` that repeats
the manifest's ceiling. It should be read from the compiled harness ceiling rather than restated —
carry into 3.1, where the registry supplies the plugin ceiling as a real operand.

<details>
<summary>Original blocker (closed) — kept for the record</summary>

**The plugin capability dialect was never conformant to the domain selector algebra.**
2.1-D correctly deleted `layer0/spi/ceiling.py`'s ad-hoc `_selector_subset` and its fail-open
`if not capabilities: return True`, and delegated to `domain/selectors/`. That delegation exposed
the fact that the pack's capability declarations are not canonical selectors:
`packs/code-default/plugins/*.yaml` declare `{kind: fs, root: /workspace}` with **no `paths`**, and
`terminal.yaml` / `harness.yaml` declare `kind: proc`, which is not in `SELECTOR_KINDS`
(`fs, network, secret, git, table, browser, generic`). `parse_selector` rejects both, `decide()`
returns `unparsable`, and the cell gate denies **every** plugin capability in the shipped pack.

The old fail-open walk was masking this. It fails *closed*, so it is not a security hole — but the
plugin cell is inert, and Wave 3 builds directly on it.

- **Detected by:** `test/registry` — 5 failures (`test_attenuation_rpc_gate`,
  `test_plugin_isolation`). Bisected to the 2.1 working tree, **not** to Wave 1 or to the 2.2-A
  absorptions. Green at `f949dc6`.
- **Why it was missed:** `test/registry` is not a CI step. Add it — this is the suite that guards
  the plugin isolation boundary Wave 3 depends on.
- **Both sides must be canonical**, not just the manifests: a canonical ceiling still denies a
  root-only *request* selector, so every call site constructing a request selector migrates too.
  `vg-code-default/manifest.json` already shows the target form — `paths: ["/workspace"]`, and
  `proc` expressed as `{kind: generic, uriPattern: "proc://exec/allow/..."}` (matching
  `adapters/models/invocation.py:517`, which already refuses `kind: process` for this reason).
- **Owner:** Developer B, closing out 2.1-D. Not a repair of `layer0/` — the fix is in the pack
  declarations and the packages call sites.

**Do not** resolve this by restoring a permissive branch in `adapters/sandbox/ceiling.py`, and do
not re-point the gate at a second subset walk. One algebra (ADR-0069); the declarations conform to
it, not the reverse.

</details>

### M-2 convergence evidence — **ROUND 4 SUBMISSION RETAINED; EXIT SCOPE EXTENDED BY ADR-0078/0082** (Developer A, 2026-08-21)

All three requirements from the Round-3 block are implemented and verified green on the canonical `vanguard/packages/` path:

1. **Fold rules landed in `reducer.py`:**
   - `EffectFailed`: Closes in-flight effects (`effects[d].status = "failed"`, records outcome/error, resultDigest, receiptDigest).
   - `EffectRejected`: Closes effects (`effects[d].status = "rejected"`, records rejection reason/outcome).
   - `BudgetExhausted`: Debits committed to `cumulative_budget_debits` and marks lease released.
   - `CapabilityAttenuated`: Records child grant with `parentGrantId` and attenuated constraints/actions in `state.grants`.
   - `TurnStarted`: Records active episode turn transitions in `episode.state_transitions`.
   - `Plugin*` lifecycle (`PluginResolved`, `PluginActivated`, `PluginQuiesced`, `PluginRetired`, `PluginFaulted`): Reduced into typed `PluginRecord` instances in `LedgerState.plugins` (included in `to_canonical_dict()`).
2. **Catalogued-and-folded property test landed:**
   - `test/contracts/test_event_coverage.py::CataloguedKindsAreFoldedOrAllowlisted` asserts that every kind in `EVENT_KINDS` (56 total) is either folded into typed state or explicitly named in `UNFOLDED_ALLOWLIST` (21 kinds: advisory requests, pre-decision requests, triggers, or Phase-2 pipeline markers). Zero kinds silently fall into `unknown_events`.
   - Direct unit tests verify `EffectFailed`, `EffectRejected`, `BudgetExhausted`, `CapabilityAttenuated`, `TurnStarted`, and `Plugin*` walks leave `unknown_events == ()`.
3. **Tool docstring & CI integrity:**
   - `tools/check_event_coverage.py` assertion ("every production-emittable event kind is in the canonical catalog and representable") holds true with the fold rules landed.
   - All suites and linters pass: `test/kernel` (93), `test/contracts` (142), `test/agency` (107), `test/packs` (31), `test/falsifiers` (23), `test/trust` (22), `test/security` (45), `test/registry` (26), `test_ledger_truth` (15, incl. ColdReplayParity), `check_boundaries` (283 files), `check_tcb_budget` (1365 ≤ 1438), `check_domain_blindness`, `check_isolation_policy`, `check_duplication --enforce`, `check_stale_paths`, `check_markdown_links`, `scan_secrets`.

<details>
<summary>Previous Round-3 blocker record (Tech Lead, archived)</summary>

### M-2 gate — **RE-GATE: BLOCKED (round 3)** (Tech Lead, 2026-08-20)

The round-2 blocker's core deliverable is **not done**. Developer A's catalog-side work below is real,
verified, and kept (EVENT_KINDS 56, `VerdictRecorded` fold, E-COV tool retarget, ColdReplayParity with
a genuine Ed25519 verdict — all re-verified green here). But the blocker explicitly required
*fold rules* for `EffectFailed`, `BudgetExhausted`, `CapabilityAttenuated`, `TurnStarted`, the
`Plugin*` five, and `EffectRejected`; *none exist*. `reducer.py` has no `kind ==` branch for any of
them. Reproduced directly (packages path, current HEAD `bf5e3be`):

```
EffectStarted(d1) then EffectFailed(d1) → effects[d1].status == "started" (still in flight),
                                           unknown_events == ['EffectFailed']     ← the blocker scenario, verbatim
PluginResolved / BudgetExhausted / TurnStarted / CapabilityAttenuated / EffectRejected
    → all in EVENT_KINDS (catalog TRUE), all in unknown_events (reduced FALSE)
```

"Present in the catalog" ≠ "reduced": the derived state still under-reports exactly the direction the
blocker forbade, and Wave 3's lifecycle events still land invisible in `unknown_events`. Three
consequences that must all be closed at once:

1. **Fold rule for each of the four** (`EffectFailed` closing the `effects` record like
   `EffectCompleted`, `BudgetExhausted` against the lease/debit vector, `CapabilityAttenuated`
   against the grant tree, `TurnStarted` against episode progress) **plus the `Plugin*` five and
   `EffectRejected`** — same shape, Wave 3 depends on it.
2. **Property test no longer `catalogued`, but `catalogued **and** folded`** — the current
   `test/contracts/test_event_coverage.py` is all `assertIn` (catalogued only) and would pass while
   `unknown_events` records failures. An explicit, named allowlist is acceptable for kinds
   deliberately not folded, but the silent `else` is not.
3. **`tools/check_event_coverage.py` docstring still over-claims** — lines 29–31 still read "so
   `LedgerEmitter` can never write an event the reducer would silently misfile into `unknown_events`".
   That is false until the folds land (membership implies nothing about folding). Either the folds
   land first or the docstring must be corrected — it cannot keep asserting a guarantee the gate does
   not provide.

Owner: Developer A. Also addressed there: the `tool`'s subset assertion is the *write* side
(production-emittable ⊆ catalog) — right and kept — but the *read* side (catalogued ⇒ folded) is the
half still missing. Re-gate will be re-run exactly against the falsifier above.

</details>

<details>
<summary>Developer A round-3 submission (archived) — catalog side landed and kept</summary>

Fixed on the canonical `vanguard/packages/` path only; no Wave-2 structure and no `root.py`
decomposition touched.

- `domain/ledger/events.EVENT_KINDS` is now `frozenset(kind.value for kind in EventKind) |
  _V4_ONLY_KINDS` — derived from the schema-generated `mhf.event/1` kind enum
  (`domain/wire/types_gen.py`, A-4/I-1) plus an explicitly-named, documented set of VG-04 kinds the
  wire schema never carried forward. One derivation, not a second taxonomy. 56 kinds total; all
  five named kinds (`VerdictRecorded`, `EffectFailed`, `BudgetExhausted`, `CapabilityAttenuated`,
  `TurnStarted`) and all five Wave-3 `Plugin*` lifecycle kinds present.
  `test/kernel/test_event_kinds_writer.py`'s closed-catalog assertions (`RunFailed`,
  `NotARealKind` excluded) still pass unmodified.
- `reduce_event` gained a real `VerdictRecorded` case: reduces the ledgered `SignedVerdict` body
  into a new `VerdictRecord`, keyed by `evaluation_request_id`, in a new `LedgerState.verdicts`
  mapping (`domain/ledger/state.py`, included in `to_canonical_dict()`/the state digest). No
  signature re-verification in the reducer — that stays the reader's job
  (`adapters/evaluators/gate.py`) — and none is needed: the sole writer
  (`runtime/evaluator_gateway.record_verdict`) refuses to ledger anything without a bound, signed
  body.
- `ColdReplayParity` (`test/runtime/test_ledger_truth.py`) now runs its scripted episode with a
  fake `EvaluatorPort` (`_SignedVerifier`) that produces a genuinely Ed25519-signed, bound verdict
  via `VerdictSigner`. Both live and cold-reconstructed state are asserted to carry the verdict —
  same `evaluation_request_id`, same signature — and `cold_state.unknown_events == ()`. The WAL
  round-trip proves I-4 for the vocabulary this blocker was about, not just for grants/budgets.
- `tools/check_event_coverage.py` retargeted off the deleted `layer0.events.taxonomy` import.
  "Production-emittable" is now computed as the union of `PRIVILEGED_KIND_OWNERS`
  (`runtime/ledger_emitter.py` — the writer-authority table, i.e. what a role is *legally* permitted
  to emit) and a static AST walk of `kernel/`, `agency/`, `runtime/` (excluding `runtime/service/`,
  the separate CLI "vg.4" wire protocol) for `Event(kind=...)`, `.emit_kind(...)`, and the kernel's
  `_emit(...)` call sites. Asserts the one direction that matters — production-emittable ⊆
  `EVENT_KINDS` — never equality, so a locked-but-dormant kind (e.g. `TurnStarted` today) never
  forces a false failure. Verified fail-closed: re-running against a catalog with the four kernel/
  evaluator-privileged kinds stripped back out reports exactly those four as missing. Wired into
  `.github/workflows/ci.yml` as a living gate (`Event coverage (E-COV, SPEC §1.2, ADR-0076 §6)`).
- New durable contract test `test/contracts/test_event_coverage.py` (6 tests): asserts the same
  subset property in-process, names the five M-2 kinds and five `Plugin*` kinds explicitly, asserts
  `RunFailed` stays excluded, and shells out to the tool itself for CI parity. No brittle fixed
  count anywhere in the fix.
- Full sweep green: `test/kernel` (93), `test/contracts` (134, includes the 6 new), `test/agency`
  (107), `test/packs` (31), `test/layer0` (4, advisory), `test/falsifiers` (23), full `test/`
  discover (1176, 6 failures — 3 Ollama-daemon-absent per CLAUDE.md §6, 3 pre-existing
  `test/integration` failures confirmed present on baseline `HEAD` via `git stash`, unrelated to
  this change). `check_boundaries`, `check_tcb_budget`, `check_domain_blindness`,
  `check_isolation_policy`, `check_event_coverage`, `check_stale_paths`, `check_markdown_links`,
  `scan_secrets`, `check_duplication.py --enforce` all pass.

Not self-authorizing Wave 3. Handing back to the Tech Lead for re-gate.

</details>

<details>
<summary>Original blocker record (for context)</summary>

### M-2 gate — **BLOCKED (round 2)** (Tech Lead)

The catalog correction is most of the way there. Four of the five named kinds were added to the
catalog **without** reducer handling, so they still land in `unknown_events`.

**Done and verified:** `EVENT_KINDS` 37 → 56, covering all five named kinds and the five Wave-3
`Plugin*` kinds. `VerdictRecorded` reduces into a typed `VerdictRecord` keyed by
`evaluation_request_id` and is inside `to_canonical_dict`, so the state digest moves when a verdict
is present — and the reducer deliberately does *not* re-verify the signature, which is the right
call (that is the reader's job, `adapters/evaluators/gate.py`). `test/contracts/test_event_coverage.py`
is genuinely vocabulary-based — a subset assertion derived from `PRIVILEGED_KIND_OWNERS` plus a
call-site scan, not a count. `ColdReplayParity` now drives a real Ed25519-signed, bound verdict
through `HarnessSession` onto the SQLite WAL and asserts a fresh-process fold recovers it with
`unknown_events == ()`. `check_event_coverage.py` reads the canonical catalog, holds no `layer0`
authority, and is wired into CI.

**BLOCKER — catalogued is not the same as reduced.**

`reduce_event` dispatches on an if/elif chain whose `else` appends to `unknown_events` regardless of
`EVENT_KINDS` membership. `EffectFailed`, `BudgetExhausted`, `CapabilityAttenuated` and
`TurnStarted` are now in the catalog and still have no fold rule:

```
EffectStarted(d) then EffectFailed(d)  →  reconstruct_state
    effects[d].status == "started"      outcome: None
    unknown_events == ['EffectFailed']
```

An effect that started and then failed reduces to *still in flight*, forever. The raw event is
retained (CT-44 is lossless), but the **derived** state contradicts the ledger, and it contradicts
it in the direction that under-reports failure. In a substrate whose thesis is verifiable evidence,
reduced state must not be more optimistic than the log it came from.

Two things make this worth another round rather than a follow-up:

1. **The tool now asserts a guarantee it does not provide.** `check_event_coverage.py`'s docstring
   says the check means `LedgerEmitter` "can never write an event the reducer would silently misfile
   into `unknown_events`". That is false as implemented — membership implies nothing about folding.
   A gate tool making a false claim is worse than a known gap, because the next reviewer trusts it.
2. **Wave 3 walks straight into it.** All five `Plugin*` kinds are catalogued and none are reduced.
   3.1's exit gate is the DISCOVERED→…→RETIRED walk; every one of those events would land in
   `unknown_events` and the lifecycle would be invisible in reduced state. Shipping now guarantees
   this same defect resurfaces at M-3.

**To clear** (Developer A, small): a fold rule for each of the four, consistent with the neighbours
already there — `EffectFailed` closing the `effects` record the way `EffectCompleted` does,
`BudgetExhausted` against the lease/debit vector, `CapabilityAttenuated` against the grant tree,
`TurnStarted` against episode progress. Then extend the property test from *catalogued* to
*catalogued **and** folded* (an allowlist is acceptable for kinds deliberately not folded, but it
must be explicit and named, not the silent `else`), and correct the tool docstring. Do the `Plugin*`
five at the same time so 3.1 does not re-open this. `EffectRejected` has the same shape and predates
Wave 2 — fold it in here rather than leaving one more of the same.

### Wave 2 lanes

- **2.2-B — DONE, verified.** Deletion matches the authorized scope exactly: `layer0/kernel/`,
  `layer0/scheduler/`, `layer0/spi/`, `layer0/events/{selectors,canonical,fold,blob}.py` gone;
  `layer0/registry/`, `layer0/compose/`, `layer0/events/{emitter,envelope,store,taxonomy}.py`
  retained. Zero `layer0` imports under `vanguard/` (only provenance comments). `packs/` repointed
  onto `kernel.budget` with an explicit wire→additive conversion at the governor boundary.
- **2.2-C — DONE, verified.** `root.py` is a 126-LOC facade; `Runtime.compose` and `HarnessSession`
  each defined exactly once (`compose.py` 390, `session.py` 646, `wiring.py` 347). No parallel
  composition path. `session.py` exceeds the plan's ~500-LOC guidance; it is one cohesive class and
  splitting it further would invent seams — accepted, noted.
- **2.2-D — retained in M-2.** Complete the widened I-7/boundary check if its board assertion is
  not yet evidenced by a landed task-specific falsifier.
- **Wave 2C — OPEN by Director ratification.** RF-23 and RF-25 are the remaining primary M-2
  gates. The Round-4 convergence submission is retained; it is not repeated.

### Decision queue

| Item | Needs | Owner |
|---|---|---|
| M-2 / v0.6.1 exit re-gate | Round-4 convergence evidence + RF-23 green + RF-25 green + all existing gates green | Tech Lead |
| M-3 entry | Signed M-2 re-gate; ADR-0077/0079/0081 implementation remains queued until then | Director / Tech Lead |
| Release/version cut after M-4 | Decision | Director |

## Already settled — do not reopen on this board

Canonical envelope, one selector algebra, JCS-only bytes, `D_H` definition, verdict binding fields,
single writer (ADR-0076). Scope refusals: SPEC §9. Verdicts on "should we…" questions those cover:
no.

## Scaffolds waiting for completion

| Scaffold | Landed | Completes in |
|---|---|---|
| `schemas/mhf/trajectory.schema.json` (mhf.trajectory/1) | Director prep | 1.3-D — **done** |
| `SignedVerdict` binding fields (`schemas/mhf/spi_payloads.schema.json`) | Director prep | 1.1-B/C/F — **done** |
| Envelope lineage fields (`schemas/mhf/event_envelope.schema.json`) | Director prep | 1.2-A — **done** |

## Follow-ups carried out of Wave 1 (not M-1 blockers)

| Item | Carried to |
|---|---|
| `layer0/scheduler/driver.py` fabricates an unsigned `"pass"`; `layer0/spi/ceiling.py` is fail-open | 2.2-B / 2.1-D — both die with the fork |
| `test/layer0/kernel/test_dispatch.py` — 3 errors, `EffectContext.depth` is `None` against `layer0/kernel/dispatch.py:388`. Pre-existing at `b2ccecb`, not a Wave-1 regression (verified against a clean tree). The fork drifted from the regenerated types. **Do not patch the fork** — its CI step is now advisory and 2.2-B deletes both | 2.2-A (triage: this behavior needs a packages twin or an explicit kill) / 2.2-B |
| `assemble_trajectory` reports a zero cost vector; per-turn attribution and conserved cost must join ledger/adapter measurements without fabrication | **Wave 2C / RF-23 (NOVA-1)** — ADR-0078 supersedes the Wave-4 carry-out |
| `intersect_ceilings` is the identity over a single harness ceiling until a plugin ceiling exists | 3.1 (registry lands the second operand) |

## Definition of done (every task)

Falsifier/acceptance evidence named in the wave plan passes on the canonical path · suites of
record stay green · boundary/TCB/duplication linters green · no new `layer0` imports · trajectory,
envelope, verdict shapes validate against `schemas/mhf/`.

---

## Unified Task Backlog & Execution Register

**Readiness Legend:**
- **READY** — contract, owner boundary, and acceptance evidence are settled; implement directly.
- **SCAFFOLDED** — leadership landed the contract (schema/decision); complete the implementation against it.
- **TECH-LEAD** — needs a Tech Lead decision or diff review before assignment.
- **DEV-LOCAL** — intentionally left to the implementing developer's design.
- **DIRECTOR** — do not decide locally; escalate.
- **DONE** — landed and its falsifier passes on the canonical path.

### Wave 0 — CI Truth & Falsifiers (CLOSED — M-0)
| ID | Task | Readiness |
|---|---|---|
| W0-CI | CI subject-of-record rewire; quarantine Ollama env-sensitive cases | DONE |
| W0-FALS | Falsifiers F-01…F-21 registered as tests | DONE |
| W0-HYG | F-19 `__init__.py` for integration/governance; F-20 oracle artifact; stale-path cleanup | DONE |

### Wave 1 — Trust Spine (`done/wave1_trust_spine.md`) (CLOSED — M-1 GREEN)
| ID | Task | Falsifier | Readiness |
|---|---|---|---|
| 1.1-A | Regenerate types; fix generator | F-13 | DONE |
| 1.1-B | JCS verdict bytes in `signing.py` | F-04 | DONE |
| 1.1-C | Daemon binds verdicts (request/subject/oracle/nonce) | F-04 | DONE |
| 1.1-D | Evaluator gateway = sole `VerdictRecorded` writer | F-03 | DONE |
| 1.1-E | Gate reads ledgered verdicts; delete verify-and-discard | F-03/F-08 | DONE |
| 1.1-F | Flip binding fields required; regenerate | F-04 | DONE |
| 1.1-G | Translator lifting + selector conformance | F-21/P1-17 | DONE |
| 1.2-A | `LedgerEmitter` from `LedgerBridge`; `mhf.event/1` envelopes | F-01 | DONE |
| 1.2-B | Role-scoped writer facades | F-05 | DONE |
| 1.2-C | `project_id` source + per-project chains | F-01 | DONE |
| 1.2-D | Cold `replay-parity` CI job from disk | F-02 | DONE |
| 1.2-E | Durable-intent crash test | F-14 | DONE |
| 1.2-F | Listener uses the emitter | F-01 | DONE |
| 1.3-A | Complete `D_H` at compose | F-11 | DONE |
| 1.3-B | Fail-closed ceiling intersection on canonical path | F-06/F-07 | DONE |
| 1.3-C | Typed budget algebra; `None` fails closed (kernel diff) | F-09/F-10/F-15 | DONE |
| 1.3-D | Trajectory assembly + emission at `EpisodeCompleted` | F-12 | DONE |
| 1.3-E | Receipt carries `lease_id`/`grant_digest` | P1-9 | DONE |

### Wave 2 — Convergence + Evidence Integrity (`done/wave2_convergence.md`, [`wave2C_todo.md`](../../wave2C_todo.md)) (IN FLIGHT — M-2/v0.6.1)
| ID | Task | Readiness |
|---|---|---|
| 2.1-A | jsonrpc → `domain/wire/`; flip 6 imports | DONE |
| 2.1-B | types_gen target moves to packages; shim | DONE |
| 2.1-C | Five SPI Protocols → `ports/spi.py` | DONE |
| 2.1-D | Ceiling delegates to domain algebra; fail-closed | DONE |
| 2.1-E | Duplication detector heuristics (`--enforce` wired in CI) | DONE |
| 2.2-A | Parity assertion triage layer0→contracts (Keep/kill settled) | DONE (GREEN) |
| 2.2-B | Delete 2.2-A KILL surfaces; retire v4 write path | DONE |
| 2.2-C | `root.py` split in place (compose, session, wiring) | DONE |
| 2.2-D | Widen I-7 domain-blindness linter & boundary rows | READY |
| 2C-R23 | Write RF-23 red; implement NOVA-1 populated `mhf.trajectory/1` and exact accounting | **READY — PRIMARY M-2 GATE** |
| 2C-R25 | Write RF-25 red; prove fresh-interpreter continuation from file-backed SQLite WAL | **READY — PRIMARY M-2 GATE** |
| 2C-REGATE | Integrate Round-4 evidence + RF-23/RF-25; run full M-2 gate and obtain Tech Lead signature | BLOCKED on RF-23/RF-25 |

### Wave 3 — Extensibility (`doing/wave3_extensibility.md`) (QUEUED — Entry: signed M-2 including RF-23/RF-25)
| ID | Task | Readiness |
|---|---|---|
| 3.1-A | Registry FSM on packages; ledgered transitions | READY |
| 3.1-B | Compose v2 ↔ registry; freeze-at-compose negatives | READY |
| 3.1-C | Echo plugin lifecycle + fault injection (ADR-M0-13) | READY |
| 3.1-D | Isolation broker rlimits scope | TECH-LEAD |
| 3.2-A | code-default toolkits through the lifecycle | READY |
| 3.2-B | Coding-token sweep; widened I-7 green | READY |
| 3.2-C | One manifest parser | DEV-LOCAL |

### Wave 4 — Foundation E2E (`doing/wave4_foundation_e2e.md`) (QUEUED — Entry: M-3)
| ID | Task | Readiness |
|---|---|---|
| 4.1-A | Fixture repo + preregistered oracle | READY |
| 4.1-B | Nine-row E2E integration test | READY |
| 4.1-C | Cassette of the green run for per-PR CI | READY |
| 4.1-D | Evidence bundle report | DEV-LOCAL |

### Director-Only Escalations (Do Not Pick Up Locally)
New event kinds · Sixth SPI · Kernel LOC ceiling change · Second digest/canonicalisation algorithm · Concurrency enablement · Version/release cut after M-4 · Any item on SPEC §9 refusal list.
