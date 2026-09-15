# Ruling Ledger — 2026-09-15

**Subject:** `d614e5ce` (branch `feat/aether-strongforce-sota-coder`).
**Not** `1a2cb2b6` as the Executive Dispatch Directive states — HEAD advanced
through `4bbc5895` → `756e8e5c` → `d614e5ce`. Line locators in the directive
were resolved against the older subject and several have drifted; see
**Locator corrections** below. Named symbols are identity, line numbers are not.

**Authority:** records the rulings in `.draft/suggestions_development_1509.md`.
This ledger transfers; it does not originate law.

**Status vocabulary:** `mechanical` (text edit, no behaviour change) ·
`engineering` (needs a code packet) · `blocked-external` (needs an authority or
resource this repository cannot supply) · `no-op` (already satisfied in source).

---

## Locator corrections — read before acting on the directive

| Directive says | Actual on this subject |
|---|---|
| C1 exemption at `spec.md:1885` | `spec.md:1885` is a `TransformSpec` field block. The stale exemption is **`spec.md:1953`**. |
| Surviving FACT at `spec.md:1051` | The capability-derived FACT is **`spec.md:1120`**; `spec.md:2216` already records `ADMISSION_GATE_EXEMPT` as *Removed*. |
| Rewrite `docs/architecture/data-flow.md:87` to 14 stages | **Already correct** at `data-flow.md:87` — full S0→S12 with `S8a` and "Durable intent always precedes the physical effect." **No edit required.** |

---

## Contradictions

| ID | Operative ruling | Target file | Acceptance citation | Status |
|---|---|---|---|---|
| **C1** | Delete the product-name admission exemption; capability-derived admission survives. | `docs/execution/main/spec.md` (`:1953`) | `runtime/session.py:admission_required` (`:280`) — docstring records both name sets removed | mechanical · **lease-blocked (C/T-132)** |
| **C2** | Extend the existing context compiler through policy; admit no second compiler. | `spec.md` (`:2186`, `:2334`) | `agency/context/compiler.py`; `agency/context/progressive.py` **does not exist** | mechanical |
| **C3** | Preserve one fold-produced `SemanticTaskState`; versioned continuation envelopes may wrap it, never replace it. | `spec.md`, `technical.md` | `domain/task_state.py:SemanticTaskState` (`:210`) | mechanical |
| **C4** | Sum the four additive dimensions only; `depth`/`turns` stay structural ceilings. | `spec.md` (`:1581-1595` §23.2) | `kernel/budget.py:ADDITIVE_DIMENSIONS` (`:48`) — comment names sibling-summing as defect `F-10` | mechanical |
| **C5** | Retain stale-preimage rejection, atomic rollback **and** IndexPort enumeration in the surviving `INV-DELTA-1..5`. | `spec.md` (`:1037-1043` vs `:2192-2196`) | — consolidation must not drop a protection | mechanical |
| **C6** | Keep workspace, behaviour/composition and verification-subject identities separate and explicitly bound; never collapse to one digest. | `technical.md` (`:569`), `spec.md` (`:1910`, `:563`) | `runtime/session.py:_workspace_digest`; `agency/episode/admission_gate.py:VerificationReceipt` | engineering → **unblocks W2b** |
| **C7** | Retain one dialect contract. | `spec.md` (`:1915-1917` / `:1940-1942`) | — byte-identical duplicate | mechanical |
| **C8** | Current dependencies govern T-83b; its acceptance provenance still needs repair. | `spec.md`, `tasks.md` | — | mechanical + blocked-external |
| **C9** | Link unresolved invariant identifiers to their canonical owners; do not duplicate definitions. | five-file runway | `kernel/dispatch.py:3-21` defines S0–S12 (incl. `S8a`) | mechanical |

## Open decisions

| ID | Operative ruling | Target | Citation | Status |
|---|---|---|---|---|
| **OD-1** | Promote accepted baseline behaviour with its original subject and limitations; record pending work as as-built observation. | `spec.md`, `docs/architecture/` | — | mechanical |
| **OD-2** | Preserve the five-file runway; `technical.md` is guidance, never competing law. | `AGENTS.md:335`, `README.md:26-35` | — | mechanical |
| **OD-3** | Apply C1–C9 above; historical examples never override living contracts. | this ledger | — | mechanical |
| **OD-4** | Long-horizon work uses a separately identified bounded composition; do not touch control presets. | `packs/code-default/presets.json` (read-only) | `spec.md` RUN-04 | engineering |
| **OD-5** | Extend `Topology`; a plan may be a versioned input artifact, never a second scheduler. | `runtime/topology.py` | `spec.md` RUN-10 | engineering |
| **OD-6** | Require isolated writable views and fenced mutation ownership before concurrent mutating workers. | `runtime/child_runtime.py` | carries **no** worktree/workspace reference today | engineering |
| **OD-7** | Pairwise non-author developer review; Leadership accepts batches only where genuinely independent of the repair. | `tasks.md` (Senior) | — | **blocked-external** (see gap below) |
| **OD-8** | Admit the four bounded capability packets without waiting for MS-CONTROL. | `backlog.md`, `tasks.md` | — | engineering |
| **OD-9** | Preserve two-sided uncorrected Wilson, z=1.96, 30 fixed slots, 18/30, zero observed false completions as hard veto. | `spec.md:75`, `technical.md:1300` | formula appears nowhere in source | engineering |
| **OD-10** | Preserve receipts and surviving semantics before removing duplication. | five-file runway | `README.md:108-110` | mechanical |
| **OD-11** | Append `check_doc_budgets` + `check_stale_paths` to `docs-check` **only after** the three execution documents are under ceiling. | `justfile` (C/T-132) | `check_doc_budgets.py:37-38` | engineering · lease-bound |
| **OD-12** | No version cut. | — | — | deferred |

---

## Recorded gaps — not to be signed

1. **No independent acceptor exists for this session's work.** W0's repair, W2a
   and W3a were all authored or materially supplied by the same actor. Under
   OD-7's binding condition ("where Leadership materially supplied the change
   under acceptance, the claim is marked LANDED / acceptance pending"), none of
   these may be recorded as accepted. They are **LANDED / acceptance pending**.
2. **The `session.py` T-140 release date is unknown.** C retains the lease until
   explicit release. No date is recorded here, because none was supplied and the
   directive forbids a manufactured one. W4 and W5(4.3) stay blocked.
3. **C1's edit collides with C's T-132 lease.** The directive instructs the
   Senior to edit `spec.md`, while OD-11 scopes T-132 to exactly
   `spec.md`/`tasks.md`/`technical.md`. The C1 correction must serialize through
   C, or T-132 must be explicitly narrowed. **Not edited here.**
