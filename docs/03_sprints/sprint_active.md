---
id: SPRINT-V060-FOUNDATION-BOARD
file: docs/03_sprints/sprint_active.md
title: "Active board — v0.6 Foundation (M-1 green → Wave 2 in flight)"
status: ACTIVE
milestone: M-1 GREEN (Wave 1 closed) → M-2 (Wave 2) in flight
spec: docs/SPEC.md
law: ADRs 0069–0076 + docs/04_annex/
register: docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md
plans: docs/03_sprints/plans/
last_reviewed: 2026-08-20
---

# Active board — v0.6 Foundation

**Start here if you are new:** read
[`plans/000_CANONICAL_EXECUTION_PATH.md`](plans/000_CANONICAL_EXECUTION_PATH.md) first — it names
production truth, the one flow, and the decisions you must not re-make. Then your wave plan.

## Now

| Lane | State | Who |
|---|---|---|
| **Wave 0 — CI truth + falsifiers** | CLOSED (M-0) | — |
| **Wave 1 — Trust spine** | **CLOSED — M-1 GREEN** | plan: [`plans/wave1_trust_spine.md`](plans/wave1_trust_spine.md) |
| **Wave 2 — Convergence** | **OPEN — entry satisfied, both developers** | plan: [`plans/wave2_convergence.md`](plans/wave2_convergence.md) |
| **Wave 3 — Extensibility** | QUEUED — entry: M-2 green (unchanged) | plan: [`plans/wave3_extensibility.md`](plans/wave3_extensibility.md) |
| **Wave 4 — Foundation E2E** | QUEUED — entry: M-1 + M-2 + M-3 | plan: [`plans/wave4_foundation_e2e.md`](plans/wave4_foundation_e2e.md) |

### Wave 2 assignment slices (parallelizable)

Sprint 2.1's tasks are independent moves; 2.2 depends on all of 2.1. Wave 3's entry is **not**
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

### Wave 2 lanes — now open

- **Developer A:** 2.2-B deletion, against the scope in the triage: `layer0/kernel/`,
  `layer0/scheduler/`, `layer0/events/{selectors,canonical,fold,blob}.py`,
  `layer0/spi/{interfaces,fakes}.py`, then the `layer0/spi/` shims once importers are rewritten.
  **Retained until 3.1:** `layer0/registry/`, `layer0/compose/`,
  `layer0/events/{emitter,envelope,store,taxonomy}.py`. Shrink the advisory layer0 CI step as its
  subjects go; do not un-quarantine it.
- **Developer B:** 2.2-C — split `root.py` in place along the named seams (`compose.py`,
  `session.py`, `wiring.py`; `ledger_emitter.py` already landed in 1.2), then 2.2-D linter rows.
  No behavior change: `test/runtime` green unmodified.
- Independent lanes; 2.2-C touches no file 2.2-B deletes.

### Decision queue

| Item | Needs | Owner |
|---|---|---|
| M-2 exit re-gate | Tech Lead sign-off once 2.2-B/C land | Tech Lead |
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
| `assemble_trajectory` reports a zero cost vector; real per-turn cost needs the governor's settled ledger | Wave 4 (`wave4_foundation_e2e.md` cost row) |
| `intersect_ceilings` is the identity over a single harness ceiling until a plugin ceiling exists | 3.1 (registry lands the second operand) |

## Definition of done (every task)

Falsifier/acceptance evidence named in the wave plan passes on the canonical path · suites of
record stay green · boundary/TCB/duplication linters green · no new `layer0` imports · trajectory,
envelope, verdict shapes validate against `schemas/mhf/`.
