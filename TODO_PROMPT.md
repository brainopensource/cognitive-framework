---
id: consolidated-close-out-development-guide
class: review
authority: non-authorizing
canonical_for: []
status: historical-advisory
owner: engineering-review
version: "2.0.0"
last_verified: 2026-08-27
subordinate_to: ../../../VISION.md
supersedes:
  - docs/_archive/reviews/TODO_SUGGESTIONS.md
superseded_by: null
---

# AETHER Higgs — Backend Close-Out Development Guide (M-4 → M-8, Beta MVP)

> ## ⚠ NON-AUTHORIZING
>
> **This document diagnoses and instructs; it authorizes nothing.**
>
> Work is authorized *only* by [`docs/03_execution/sprint_active.md`](../../03_execution/sprint_active.md).
> Stable gates live in [`milestones.md`](../../03_execution/milestones.md); stable work-package
> contracts live in [`backlog.md`](../../03_execution/backlog.md). Where this file and the canonical
> triad disagree, **the triad wins and this file is stale**.
>
> Nothing here may be cited to close a gate, mark a milestone `ACCEPTED`, waive a falsifier, or
> justify work outside an authorized package. This file contains **no completion percentages, no
> release claims, and no schedule commitments** — by construction, because those are the three
> failure modes that produced the review sprawl this document replaces.
>
> Reading order for a developer: `VISION.md` → `docs/SPEC.md` → `docs/01_law/` → the relevant ADR →
> `sprint_active.md` → *then* this guide for implementation detail.

---

## Table of Contents

| # | Chapter | Purpose |
|---|---|---|
| 1 | [Executive Briefing](#1-executive-briefing) | What is true, what blocks, what to do |
| 2 | [Authority Model and How To Use This Guide](#2-authority-model-and-how-to-use-this-guide) | Precedence, non-authorizing status, doc contract |
| 3 | [Verified Baseline](#3-verified-baseline) | Measured state at the time of writing, with method |
| 4 | [Adjudication of Prior Review Suggestions](#4-adjudication-of-prior-review-suggestions) | What survived, what was rejected, and why |
| 5 | [Architectural Foundations](#5-architectural-foundations) | Lattice, canonical chain, axioms, invariants |
| 6 | [Standards, Patterns and Engineering Conventions](#6-standards-patterns-and-engineering-conventions) | How to write code that belongs here |
| 7 | [Protocols and Contracts](#7-protocols-and-contracts) | `vg.4`, event substrate, evidence envelopes |
| 8 | [Phase 0 — P0 Trust and Security Repairs](#8-phase-0--p0-trust-and-security-repairs) | Approval spine, CLI keys, gateway, UDS |
| 9 | [Phase 1 — Runtime Truth](#9-phase-1--runtime-truth) | Single writer, canonical envelopes, recovery |
| 10 | [Phase 2 — Protocol and Schema Convergence](#10-phase-2--protocol-and-schema-convergence) | A-4 restoration, shared vectors, fail-closed validation |
| 11 | [Phase 3 — Distribution and CLI Hardening](#11-phase-3--distribution-and-cli-hardening) | Standalone binary, installer, key lifecycle |
| 12 | [Phase 4 — Evidence Governance Restoration](#12-phase-4--evidence-governance-restoration) | Reviewer role, acceptance tooling, baseline succession |
| 13 | [Phase 5 — M-7 Topologies Through One Runtime](#13-phase-5--m-7-topologies-through-one-runtime) | Extension binding, three patterns, M7-01, ADR-0099 |
| 14 | [Phase 6 — M-8 Durable Authorized Memory](#14-phase-6--m-8-durable-authorized-memory) | ADR-0100 memory half |
| 15 | [Phase 7 — M-8 Governed Learning and Rollback](#15-phase-7--m-8-governed-learning-and-rollback) | ADR-0100 promotion half |
| 16 | [M-9 / M-10 Compatibility Boundary](#16-m-9--m-10-compatibility-boundary) | Why no scaffold, and what "seam" means |
| 17 | [Verification, Falsifiers and Test Strategy](#17-verification-falsifiers-and-test-strategy) | How each phase is proven |
| 18 | [Release Qualification and CI](#18-release-qualification-and-ci) | Gate ladder to beta |
| 19 | [Work Packages, Ownership and Sequencing](#19-work-packages-ownership-and-sequencing) | WP-C1…WP-C3, WP-A3/B3, WP-A4/B4 |
| 20 | [Required Canonical Document Updates](#20-required-canonical-document-updates) | Exact edits to `docs/03_execution/` |
| 21 | [Consolidated TODO Table](#21-consolidated-todo-table) | The single actionable list |
| 22 | [Final Briefing](#22-final-briefing) | Everything, compressed |

---

# 1. Executive Briefing

## 1.1 Position

AETHER's substrate is sound. Its **trust spine is currently broken in the newest code**, its
**runtime service holds two competing truths**, and its **evidence governance has no reviewer**.
Two milestones (M-7, M-8) are genuine implementation work, not packaging work.

The beta MVP boundary is **independent acceptance of M-8** — this is fixed by
[`milestones.md:116`](../../03_execution/milestones.md) ("M-8 is the MVP boundary") and
[`SPEC.md:200`](../../SPEC.md). **v1.0.0 belongs to M-9**, which is not authorized and must not be
planned yet.

## 1.2 The four blocking classes

1. **Trust regression (P0, hours to fix, catastrophic if shipped).** The standalone CLI embeds a
   literal Ed25519 operator seed and auto-approves every governance challenge. The HTTP gateway
   fabricates approval signatures. `ResolveApproval` verifies nothing. Together these nullify
   invariant **I-5** and the M-1 trust spine for every non-test execution path.
2. **Runtime truth regression (P0, days).** `RuntimeService.publish_event` writes two stores and
   ignores the canonical result; canonical `mhf.event/2` envelopes are lossily rebuilt with
   substituted identity fields. This regresses the M-2 single-writer anchor recorded at
   [`milestones.md:120`](../../03_execution/milestones.md).
3. **Governance vacuum (P0, cheap, highest leverage).** `accepts()` correctly refuses
   self-acceptance, but no reviewer identity, acceptance CLI, or acceptance linter exists. Four
   producer bundles sit on disk with zero acceptance envelopes. **This single gap blocks M-4, M-6,
   M-6.5, and therefore M-7 and M-8 behind them.**
4. **Genuine implementation debt (weeks).** M-7 topology has a complete, well-built library with
   **zero call sites** in the public runtime. M-8 memory authorization is
   `bool(non_empty_string)` — the precise falsifier ADR-0100 exists to reject.

## 1.3 The order of operations

Repair **trust**, then **runtime truth**, then **evidence governance**, then **deliver M-7**, then
**deliver M-8**. Governance tooling (Phase 4, item 1) is cheap and unblocks three milestones, so it
runs concurrently with Phase 0 from day one.

```
Phase 0  Trust & security P0          ← blocks everything; ~1 engineer-day of edits
Phase 4a Reviewer role + acceptance    ← concurrent; ungates M-4/M-6/M-6.5
Phase 1  Runtime truth                 ← the real service engineering
Phase 2  Protocol/schema convergence
Phase 3  Distribution hardening
Phase 4b Evidence: sign, accept, baseline
Phase 5  M-7 integrate + measure + ADR-0099
Phase 6  M-8 durable authorized memory
Phase 7  M-8 governed learning + rollback
─────────────────────────────────────
         Independent M-8 acceptance = BETA MVP
         M-9 = v1.0.0 (requires new authorization)
```

## 1.4 Non-negotiables for every phase

- No Kernel or domain semantics for spawn, topology, strategy, memory, or learning (**A-1, I-7**).
- Kernel stays ≤ 1,438 logical LOC (currently ~1,365; ~73 headroom).
- No new authority verb without a bound falsifier and TCB proof (**A-6**).
- No receiptless `ACCEPTED`, no test weakening, no unknown-as-pass (`sprint_active.md:143`).
- No M-9/M-10 feature or scaffold (`sprint_active.md:141`).
- Backend only. **No frontend work is in scope for this guide** — `vanguard/clients/`, Studio UI,
  and the TypeScript CLI are explicitly excluded except where a backend contract they consume changes.

---

# 2. Authority Model and How To Use This Guide

## 2.1 Precedence ladder (from `VISION.md:39-47`)

| # | Layer | Documents | Owns |
|---|---|---|---|
| 0 | **Vision (constitutional)** | `VISION.md` | Identity, ontology, product principles, direction |
| 1 | **Law (normative)** | `docs/SPEC.md`, `docs/01_law/` | RFC-2119 requirements, invariants |
| 2 | **Decisions (binding)** | `docs/02_decisions/` | Local architectural decisions |
| 3 | **Contracts & protocols** | `docs/05_contracts/`, `docs/06_protocols/`, `schemas/` | Wire realization |
| 4 | **Sequencing** | `milestones.md`, `backlog.md` | Gates, stable work packages |
| 5 | **Authorization** | `sprint_active.md` | The only board that authorizes work |
| 6 | **Communication** | `README.md`, `docs/04_architecture/`, **this file** | Orientation; no independent architecture |

**This guide sits at layer 6.** It may explain, instruct, and propose. It may not authorize.

## 2.2 The three rules that follow

1. A lower document may not be used to reject a Vision concept. Stale text is stale, not
   counter-authority.
2. The Vision changes only by an explicit Vision-superseding ADR.
3. Divergence is classified explicitly: *implementation non-conformance* is a documented gap with no
   constitutional effect; *reproducible material counter-evidence* triggers architectural review.

## 2.3 How a developer uses this file

1. Confirm your work is inside an authorized package on `sprint_active.md`. **If it is not, stop and
   request authorization** — the service and CLI code that this guide repairs was itself written
   outside the backlog, which is how it accumulated P0 defects unreviewed.
2. Read the phase chapter for your package. Follow the interface contracts and pseudocode as
   *design intent*, not as literal code to paste.
3. Write the falsifier **before** the implementation. A phase is not complete when its code runs;
   it is complete when its named falsifier fails on the unfixed version and passes on the fixed one.
4. Produce an evidence bundle. **Do not accept your own bundle** — `accepts()` will refuse it, and
   ADR-0101 §3 requires a distinct reviewer.

## 2.4 What this document deliberately omits

- **Completion percentages.** Prior reviews asserted "M-8 75% complete" for a subsystem whose
  authorization function is a string-emptiness check. Percentages on unmeasured work are fiction.
- **Time estimates.** Sequencing and dependencies are engineering facts; durations are a planning
  decision owned by leadership.
- **Frontend scope.** Studio, the Ink/React TUI, and browser signing are out of scope here.
- **Speculative pseudocode for unauthorized milestones.** M-9/M-10 get a boundary contract
  (Chapter 16), not a design.

---

# 3. Verified Baseline

## 3.1 Method

Every claim in this guide was checked against the working tree by direct file read, AST parse, or
executed command. Claims inherited from prior reviews were **re-verified, not trusted**; two
inherited claims were found false and are corrected in Chapter 4.

## 3.2 Measured results

| Check | Result |
|---|---|
| `python3 -m unittest discover -s test -t .` | **1995 tests, 3 failures, 8 skipped** |
| `check_boundaries.py` | PASS |
| `check_tcb_budget.py` | PASS (~1,365 / 1,438 logical LOC) |
| `scan_secrets.py` | PASS |
| `check_domain_blindness.py` | PASS |
| `check_isolation_policy.py` | PASS |
| `check_execution_truth.py` | PASS |
| `check_markdown_links.py` | PASS |
| `check_stale_paths.py` | PASS |
| `OPENROUTER_API_KEY` in test environment | **unset** (hermetic) |

**Interpretation.** The architectural linters passing while the trust spine is broken is not a
contradiction — it is a *coverage gap*. The linters enforce structure (imports, LOC, domain
blindness, secret regexes); they do not enforce semantic fail-closure. A hardcoded Ed25519 *seed*
does not match a credential regex. Chapter 17 proposes the falsifiers that would have caught it.

## 3.3 The three test failures

All three trace to the staged bulk model rename (`tools/_adhoc/retire_openai_models.py`):

| Test | Symptom | Class |
|---|---|---|
| `test_model_routing.test_known_model` | `140000 != 150000` | Stale price expectation — benign |
| `test_openrouter.test_priced_accounting_with_provider_usage_and_caching` | `0.000145 != 0.00024` | Same cause — benign |
| `test_instrument_tuple.test_mismatched_compatibility_key_refuses_comparison` | `True is not false` | **Disarmed falsifier — not benign** |

The third is the important one. The rename rewrote the fingerprint on
`test/benchmarks/test_instrument_tuple.py:63` — the line commented `# Different model` — to the same
value as the baseline on line 28. The negative case is no longer negative; an M-18 comparability
falsifier now asserts nothing while reporting green. **A blind rename destroyed a falsifier's
discriminating power.** Fix by restoring a genuinely distinct fingerprint; never by relaxing the
assertion.

## 3.4 Collateral damage from the same rename (AST-verified)

| File | Corruption | Why it matters |
|---|---|---|
| `tools/001_LLM_API_ROUTER/providers/groq.py:37` | `base_url` → `https://api.groq.com/deepseek/deepseek-v4-flash-0731` | `/openai/v1` was Groq's **API path segment**, not a model name. Provider is unreachable. |
| `tools/001_LLM_API_ROUTER/providers/cloudflare.py` | `@cf/openai/gpt-oss-20b` → `@cf/deepseek/…` | Cloudflare Workers AI IDs are `@cf/provider/model`. Now a nonexistent model. |
| `tools/001_LLM_API_ROUTER/llm_switch.py:63-65` | 3 aliases → `@cf/deepseek/…` | Same class. |
| `tools/001_LLM_API_ROUTER/providers/openrouter.py:27` | Duplicate dict key | Later entry silently overwrites pricing. |
| `tools/002_LLM_API_MOCK/server.py:33` | Duplicate dict key | Same. |

**Lesson to encode as a standard (§6.9): never run an unbounded textual rename across a repository
containing protocol paths, fixture negatives, and dict keys.** A rename is a semantic operation and
requires a semantic tool.

## 3.5 Evidence bundle inventory

| Bundle | `signature` | Producer | Independent acceptance |
|---|---|---|---|
| `M-4-rf95-candidate-03.json` | **absent** | `dev-a` | none |
| `M-6-canonical-recursion.json` | **absent** | `dev-a` | none |
| `M-5b-graph-coloring.json` | present | `dev-b` | none |
| `M-6.5-attributable-paired-study.json` | present | `dev-b` | none |

M-4 and M-6 are recorded as `EVIDENCE_READY` on the board while carrying **no producer signature at
all**. Under ADR-0101 that state is not defensible (see §20.1).

---

# 4. Adjudication of Prior Review Suggestions

Five prior reports were consolidated. This chapter records what was accepted, corrected, and
rejected, so that rejected proposals are not silently re-proposed.

## 4.1 Accepted as primary technical basis

**Suggestion 3 (CO5)** and **Suggestion 4 (MM3)** form the technical spine of this guide.

From CO5: the P0 security block (CLI key, auto-approver, gateway signature fabrication, unverified
`ResolveApproval`, CORS/auth/size, UDS `StreamEvents` bypass), the runtime-truth block (dual writer,
lossy envelopes, nominal recovery), schema drift, and the disarmed falsifier.

From MM3: the reviewer-role/acceptance-tooling gap (the highest-leverage item in the entire
program), the unbound preregistration digest, runner default-model drift, the `jsonschema`
fail-open, and the agency "already-applied" blindness.

## 4.2 Selectively retained

**Suggestion 2 (G53)** — its forensics on the staged rename are retained in full (§3.4); every item
was independently re-verified by AST parse. Its observation that `RuntimeService.execute_command`
**does** call `validate_frame_envelope()` and `validate_command()` is correct and **corrects an
inherited error** in the older `TODO_PROMPT.md` and in CO5.

Two G53 claims are rejected:

- *"5 failures; `OPENROUTER_API_KEY` set in shell."* Environment-specific to that reviewer's
  machine. Measured here: key unset, 3 failures.
- *"`sprint_active.md` frontmatter `version: 1.0.0` is a misleading version mismatch."* **Wrong.**
  `VISION.md:27-28` states the frontmatter `version` is the *document's* revision and that the
  package version is owned exclusively by `pyproject.toml`. Acting on this would introduce an error.

**Suggestion 1 (G37)** — retained: "never default to `SqliteEventStore(':memory:')` in product
paths," and the restatement of authorization-before-ranking (already binding via ADR-0100 and
`SPEC.md:160-162`).

## 4.3 Rejected, with reasons

| Proposal | Source | Reason for rejection |
|---|---|---|
| Milestone maturity percentages (M-8 "75% COMPLETE") | G37 | Unsupported. M-8's authorization is `bool(non_empty_string)`; M-7 has zero runtime call sites. |
| Scaffold `ports/distributed.py`, `ports/promotion.py` | G37 | **Prohibited** by `sprint_active.md:141`; `milestones.md:128-131` reserves only *already-existing* seams. |
| "20-tier SWE-bench Pro qualification" as the v1.0.0 gate | G37 | Invented gate; exists in no canonical document. `milestones.md` M-4 requires one preregistered RF-95 candidate. |
| Publish `curl … \| bash` installer | G37, old `TODO_PROMPT.md:429` | Would distribute a shared private key while §8.1 is open. |
| Change execution-doc frontmatter `version` to `0.7.3.dev0` | G53, MM3 | Contradicts `VISION.md:27-28`. |
| "TCB is over budget at 1,747 physical LOC" | MM3 §4d | Budget is *logical* LOC; `check_tcb_budget.py` passes. MM3 did not run it. |
| "No status-consistency linter exists" | MM3 §4c | Partially wrong — `check_execution_truth.py` exists and passes. **Narrowed** to: no *evidence↔board* cross-check and no acceptance gate. |
| Entire content of Suggestion 5 | — | Describes a different repository: fabricated ADR index (`0001–0020`), fabricated law files (`invariants.md`, `threat_model.md`), fabricated milestone ladder ("M-8 Launch: Security Audit & Packaging"), fabricated `REQ-*` catalog, fabricated CI matrix, fabricated entry point `vg = vanguard.packages.apps.cli:main`. |
| Rewriting `milestones.md` | G37, S5 | Its stable contracts are correct. Two reports attempted this; it would have been the real damage. |

## 4.4 The finding no report but one caught

Only CO5 identified the hardcoded operator seed and unconditional auto-approver in
`vanguard/packages/runtime/cli.py`. G37 simultaneously described the same CLI as production-verified
and proposed publishing it via `curl | bash`. This is recorded because it illustrates the review
failure mode this guide guards against: **a report that assesses maturity by feature presence rather
than by falsification will rate a broken trust spine as complete.**

---

# 5. Architectural Foundations

## 5.1 The lattice (binding; enforced by `check_boundaries.py`)

```text
domain ← ports ← kernel ← agency ← runtime → adapters
                                      ↑
                              apps/ and clients/ are
                              consumers of runtime,
                              not a second ontology
```

| Package | May import | Responsibility |
|---|---|---|
| `domain/` | stdlib only | Pure values, wire contracts, JCS, ledger reducers, selector algebra, evidence models |
| `ports/` | `domain` | Abstract interfaces (`KernelPort`, `ModelPort`, `EventStorePort`, `BlobStorePort`, SPI protocols) |
| `kernel/` | `domain`, `ports` | **TCB.** S0–S12 dispatch, attenuation, budget algebra, grants, provenance. Domain-blind (I-7). |
| `agency/` | `domain`, `ports`, `kernel` | Generic turn machine, context compilation, compaction, attenuated spawn |
| `runtime/` | `domain`, `ports`, `kernel`, `agency` | Composition, session, wiring, ledger emitter, governance, service |
| `adapters/` | `domain`, `ports` | Concrete models, stores, sandbox, evaluator. **Never** imports `kernel` or `agency`. |

**Every new module in Phases 0–7 must state its lattice position before its first line of code.**
The most common violation shape in this program is a runtime concern (memory authorization,
promotion, topology) leaking a branch into `kernel/`. It is forbidden by A-1 and I-7 and it is
detectable: if `check_domain_blindness.py` starts failing during M-8, the design is wrong, not the
linter.

## 5.2 The canonical production chain (from `SPEC.md:108-111`)

```text
mhf.manifest/2
   → CanonicalManifest
   → FrozenComposition        (owns D_H)
   → ActivationPlan
   → RunPlan                  (activation/runtime identity binds D_H into D_R)
   → EpisodeEngine
```

Compatibility formats normalize **at ingress** and never become a second runtime value. There is
exactly one public execution path. Everything in this guide — the service, topology, memory,
promotion — attaches to that path or is wrong.

## 5.3 Design axioms (`SPEC.md:70-77`)

| Axiom | Statement | Where this guide touches it |
|---|---|---|
| **A-1** | Microkernel: S0–S12 is the bounded TCB | Chapters 8, 13, 14, 15 — all keep authority out of the kernel |
| **A-2** | Two authority systems: capability grants vs plugin isolation; neither trusts the other's subject | Chapter 8 (approvals), Chapter 14 (memory grants) |
| **A-3** | Events are truth; fresh-process replay proves parity | Chapter 9 |
| **A-4** | One schema: JSON Schema + JCS + golden vectors are wire truth; generated readers replace handwritten mirrors | Chapter 10 — **currently violated twice** |
| **A-5** | Harness identity: `D_H` / `D_R` / `D_X` are never collapsed | Chapters 13, 15 |
| **A-6** | Asymmetric evolution: new authority verbs need a falsifier and TCB proof; everything else lands as packs/plugins/policies/adapters | Chapters 13–16 |

## 5.4 Invariants I-1 … I-11

| ID | Invariant | Status | Phase that restores it |
|---|---|---|---|
| I-1 | One schema-generated `EffectRequest` | Holds | — |
| I-2 | Emitted equals declared; forged rejected | Holds in kernel | — |
| I-3 | Every control merges with its call site | Holds | — |
| I-4 | Durable fresh-process replay | **At risk** (service dual truth) | Phase 1 |
| I-5 | Exterior signed judge | **BROKEN in CLI + gateway + service** | Phase 0 |
| I-6 | Plugins untrusted by default | Holds | — |
| I-7 | Domain-blind kernel | Holds | guard in 5–7 |
| I-8 | Specifications generated or normative, never both | **Violated** (handwritten mirror; fail-open validation) | Phase 2 |
| I-9 | Complete recovered trajectory | **At risk** (nominal checkpoint/resume) | Phase 1 |
| I-10 | Metaphors are not architecture | Holds | — |
| I-11 | Single sequential turn loop | Holds | preserved through Phase 5 |

**Three invariants are currently broken or violated: I-5, I-8, and (in the service) I-4/I-9.**
Phases 0, 1 and 2 exist precisely to restore them. No milestone may be accepted while an invariant
it depends on is broken.

## 5.5 Ontological commitments that constrain design

From `VISION.md` Ch. 4, 12, 16, 17 — these are not philosophy, they are design constraints:

- **An agent is not a persistent privileged object.** `Agent = Identity + Policy + Event-Derived
  Projection + Execution Boundary`. Runtime objects may hold transient optimization state, but **no
  state required for semantic continuation may exist only inside them.** This is why the service's
  in-memory cancellation flag and mutable status rows are architectural defects, not just bugs
  (Chapter 9).
- **Spawn creates a subordinate execution lineage**, not an object instance. This is why M-7
  topologies must lower to ordinary M-6 mediated delegation and not to a second engine (Chapter 13).
- **Topology is structure; scheduler is temporal policy; kernel is admissibility; ledger is fact.**
  Four separate responsibilities. Collapsing any two is the failure mode M-7 must avoid.
- **Memory is a derived capability family**, never a kernel semantic. Authorization precedes ranking
  *and* artifact dereference (Chapter 14).
- **Retention never authorizes capture.** A profile may retain what it was permitted to capture; it
  never grants permission to capture (Chapter 14, §14.8).

---

# 6. Standards, Patterns and Engineering Conventions

## 6.1 Fail-closed as a default, not a mode

Every decision function returns *permit* only on positive evidence. The shapes below are the
canonical anti-patterns found in this tree; treat each as a lint you apply by hand in review.

```python
# ANTI-PATTERN 1 — truthiness as authority   (found: memory.py:27)
def permitted(self) -> bool:
    return bool(self.grant_ref)          # a non-empty string is not a grant

# ANTI-PATTERN 2 — absent verifier means "skip"  (found: learning.py:367)
if self._verifying_keys:                 # no keys configured → verification skipped
    verify(signature)

# ANTI-PATTERN 3 — defaulted security field   (found: service.py:401, studio_gateway.py:309)
signature = payload.get("signature", "dummy-sig-approved")

# ANTI-PATTERN 4 — optional dependency gates a mandatory check  (found: loader.py:138)
if _HAS_JSONSCHEMA and schema:
    jsonschema.validate(...)             # not installed → validation silently disappears

# CANONICAL SHAPE
def authorize(request, verifier, now):
    if verifier is None:
        raise NotAvailableError("verification unavailable")   # never "skip"
    proof = request.proof or fail("missing proof")            # never default
    verifier.verify(proof, now=now)                           # raises on any doubt
    return AuthorizedContext(...)                             # only reachable via proof
```

**Rule.** A security-relevant field has **no default**. A verifier that cannot run is an
*unavailability error*, never a pass. An optional dependency may never gate a mandatory check.

## 6.2 Result and error discipline

- Runtime code returns `Result[T]` where failure is expected and ordinary; it raises typed errors
  where failure is a contract violation.
- **`Result` values are never discarded.** The dual-truth defect in Chapter 9 exists because
  `self.event_store.append(env)` ignored its return.
- Adapter errors stay errors. Never convert an adapter failure into a successful outcome, and never
  convert `unknown` into `pass` (`sprint_active.md:143`).
- The wire error vocabulary is exactly ten codes (§7.2). No handler invents an eleventh.

## 6.3 Identity, digests and canonicalization

- All digests are `sha256:<64 hex>`; all canonical serialization is RFC 8785 JCS via
  `domain/canonicalisation/jcs.py`.
- Deterministic ordering everywhere a set is serialized: sort by a stable key, then tie-break by
  record ID. Ranking quantizes before comparing to avoid float instability.
- `D_H` (composition), `D_R` (runtime/environment/model/oracle), `D_X` (dataset/protocol) are
  **never collapsed** (A-5).

## 6.4 Event and ledger discipline

- One writer. One canonical store. Projections are derived and rebuildable — never a second truth.
- Sequence allocation and append occur inside **one transaction**; notification happens **after**
  commit.
- Canonical envelopes are persisted **unchanged**. Transport frames wrap them; they never
  reserialize through a reduced shape.
- Goal events carry a digest and optional artifact reference, never raw goal text.
- Additive resources are exactly `usd_micros`, `millis`, `tokens`, `bytes`. `depth` and `turns` are
  structural ceilings, not additive budget.

## 6.5 Concurrency and CAS

- The turn loop is unary and sequential (**I-11**) until M-7 measurement and an explicit lift.
- Every durable mutation that can race uses compare-and-swap on an explicit expected value
  (`expectedSeq`, `expected_generation`, `expected_head`), returning the canonical `conflict` code.
- Physical attempts are at-least-once; durable settlement is idempotent/exactly-once per command
  identity.
- Scheduler claim TTL/heartbeat is coordination metadata, **not** budget `millis`.

## 6.6 Storage conventions

- Product execution is always file-backed SQLite-WAL. **`:memory:` is a test-only construction and
  must never be a fallback.** A durable store that cannot be opened is a startup failure.
- Write order for content-bearing records: **blob first, metadata second, causal fact third.** A
  crash between steps leaves an orphan blob (harmless, GC-able) rather than a dangling reference.
- Refuse WAL on a network filesystem (detect and fail closed).

## 6.7 Testing conventions

- Provider keys stay **unset** during tests. Network and live-provider behavior are opt-in and never
  required for hermetic verification.
- Every falsifier has a **negative control**: it must fail on the unfixed code. A falsifier that has
  never been observed failing is unproven.
- Fixture values that are deliberately *different* must be commented as such and protected from bulk
  edits (§3.3 is the cautionary case).

## 6.8 Commit and package discipline

- One reviewed commit per package; WIP=1 per developer; no consuming another developer's unfinished
  branch.
- Every completed task supplies the PR matrix: `obligation → production symbol → test/falsifier →
  evidence artifact`.
- Declare public schema versions, Kernel/lattice/event-writer changes, migration, rollback,
  exclusions, and local versus integrated gates.

## 6.9 Refactoring standard (new — derived from §3.4)

**Never perform an unbounded textual substitution across the repository.** Model identifiers,
protocol path segments, dict keys, and deliberately-distinct test fixtures are textually identical
and semantically unrelated. A rename must:

1. Enumerate targets by **parse**, not by regex (AST for Python, JSON parse for config).
2. Exclude, by explicit allowlist, any file containing URLs, provider path segments, or fixtures
   annotated as negative controls.
3. Run an AST duplicate-key scan afterward.
4. Run the full suite and **inspect the diff of every test that changed**, not just the pass count.

---

# 7. Protocols and Contracts

## 7.1 `vg.4` RuntimeService wire protocol

Frame types are discriminated: `command`, `receipt`, `event`, `error`.

```jsonc
// command frame
{
  "version": "vg.4",
  "frameType": "command",
  "frameId": "<uuidv7>",
  "command": {
    "name": "StartRun",
    "commandId": "<uuidv7>",
    "idempotencyKey": "<opaque>",
    "actor": "<principal>",
    "runId": "<RunId | '' when not run-scoped>",
    "payload": { }
  }
}
```

**The eleven-command union and their run scope:**

| Command | Run scope | Required payload |
|---|---|---|
| `StartRun` | required | `manifestPath`, `repoPath`, `brief` |
| `GetRun` | required | — |
| `ListRuns` | **forbidden** | — |
| `StreamEvents` | required | — |
| `Cancel` | required | — |
| `Checkpoint` | required | — |
| `Resume` | required | — |
| `ResolveApproval` | required | `decision` |
| `RecordCorrection` | required | `correction` |
| `ExplainArtifact` | optional | `artifactId` |
| `GetCapabilities` | **forbidden** | — |

## 7.2 Canonical error vocabulary — exactly ten codes

```
invalid_request  unauthenticated  permission_denied  not_found  conflict
incompatible_version  frame_too_large  rate_limited  not_available  internal
```

`transport_interrupted` is **client-local only** and never appears on the wire. `invalid_json` is
**not** a member and must be removed from the UDS server (§8.5). Every code carries an explicit
retryability hint.

## 7.3 Ingress pipeline (mandatory order)

```
raw bytes
  → frame-size check          (1 MiB, identical on UDS and HTTP)
  → JSON parse                (failure → invalid_request)
  → envelope validation       (frameType/version/frameId discriminated)
  → command validation        (name, run scope, required + allowed fields)
  → authentication / signature verification
  → idempotency lookup
  → authorization
  → runtime execution
  → durable receipt + events
```

**No malformed data may reach idempotency, event storage, or ledger state.** This pipeline is
already correctly implemented in `RuntimeService.execute_command` — the defect is that the UDS
server bypasses it for `StreamEvents` (§8.5) and that the HTTP gateway enters below the size check
(§8.4).

## 7.4 Approval decision contract

All eight fields are **required**; none has a default:

```
approvalId  resolution  reviewer  argsDigest  descriptorDigest  expiresAt  keyId  signature
```

`additionalProperties: false`. One signed `ApprovalDecision` shape is used by every transport.

## 7.5 Event substrate — `mhf.event/2`

The canonical envelope carries, at minimum: `schemaVersion`, `eventId`, `scope`, `seq`,
`occurredAt`, `recordedAt`, `principal`, `principalRole`, `tenantId`, `ownerId`, `confidentiality`,
`retentionClass`, `trainability`, `redactionStatus`, `payload`, `runId`, `episodeId`, `traceId`,
`spanId`.

**Writers single-write `/2`; readers dual-read `/1|/2`; historical identities are never rewritten.**
Unknown events are preserved, never dropped.

## 7.6 Evidence envelope — `aether.evidence/1`

Binds: source commit, input manifest, protocol version, environment identity, test commands and
outputs, artifact digests, event-store digest, trajectory digest, producer identity + signature,
and reviewer slots.

`accepts(acceptance, produced)` returns `True` only when **all three** hold:

1. `acceptance.producer.identity != produced.producer.identity` (independence)
2. `acceptance.outcome == "passed"`
3. `produced.digest() in acceptance.subjects` (no subject drift)

`undeterminable` is a first-class outcome. A valid negative result may close an experiment; an
invalid or incomparable study may not.

## 7.7 Capability grant and memory authorization contract (ADR-0100)

```
MemoryAuthorizationPort.verify(grant, action, selector, tenant, project, purpose, now)
    → AuthorizedMemoryContext
```

The context binds issuer, subject, action, selector, tenant, project, purpose, expiry, revocation
epoch, policy identity, and a verification receipt. It is produced **only** by cryptographic
verification and is required at **use time**, not at construction time.

---

# 8. Phase 0 — P0 Trust and Security Repairs

> **Objective.** Restore invariant **I-5** on every execution path. Until this phase closes, nothing
> in the repository may be described as a beta, and the installer must not be published.
>
> **Lattice position.** `runtime/` and `runtime/service/` only. No `kernel/` change. No new
> authority verb, therefore no A-6 obligation.

## 8.1 CLI operator key lifecycle

**Defect.** `vanguard/packages/runtime/cli.py:87` constructs `OperatorSigner` from a literal seed
(`b"vanguard-autonomous-operator-seed-key"`). Every installed copy shares one private key; anyone
who reads the repository can mint valid approval signatures against any user's runtime.

**Required design.**

```python
# vanguard/packages/runtime/keys.py   (new; runtime layer)

KEY_DIR  = Path.home() / ".vanguard" / "keys"
KEY_FILE = KEY_DIR / "operator.ed25519"

def load_operator_signer(*, allow_create: bool) -> OperatorSigner:
    """Load the per-installation operator key. Never derive it from a constant."""
    if KEY_FILE.exists():
        mode = KEY_FILE.stat().st_mode & 0o777
        if mode != 0o600:
            raise InsecureKeyError(
                f"{KEY_FILE} has mode {mode:o}; refusing to load (expected 0600)")
        return OperatorSigner(KEY_FILE.read_bytes())

    if not allow_create:
        # Ordinary `vanguard run` must NOT silently mint an identity.
        raise NotAvailableError(
            "no operator key; run `vanguard init` to create one")

    KEY_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
    seed = secrets.token_bytes(32)
    fd = os.open(KEY_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(seed)
    return OperatorSigner(seed)
```

**Falsifier RF-C-01.** Grep the built distribution for any 32-byte literal passed to
`OperatorSigner`; assert none. Assert that two fresh installations produce **different** public
keys. Assert a `0644` key file is refused.

## 8.2 CLI approval must involve a human

**Defect.** `cli.py:114` passes `approver=lambda challenge: signer.approve(challenge, ...)`. Every
S0–S12 governance gate self-approves. `interactive=True` is passed but nothing ever asks.

**Required design.**

```python
def interactive_approver(signer, reviewer, *, stream=sys.stdin):
    def approve(challenge):
        if not stream.isatty():
            # Fail closed. An unattended process has no reviewer.
            raise NotAvailableError(
                "approval required but no TTY; supply a scoped autonomous grant")
        print(render_challenge(challenge))   # verb, selector, args digest, budget
        answer = input("approve? [y/N] ").strip().lower()
        if answer != "y":
            return Denial(challenge, reason="operator_denied")
        return signer.approve(challenge, reviewer=reviewer)
    return approve
```

Unattended execution is legitimate **only** through an explicit, scoped, expiring autonomous grant
that the operator created deliberately — never as a default, and never covering a verb the grant
does not name.

**Falsifier RF-C-02.** Run the CLI with stdin redirected from `/dev/null` against a task that
triggers an approval; assert the run terminates `not_available` and that **no** `ApprovalResolved`
fact was appended.

## 8.3 Remove fabricated approval signatures and verify decisions

**Defect A.** `studio_gateway.py:309, 328, 339, 350` each default a missing signature to
`"dummy-sig-approved"`.

**Defect B.** `service.py:401-428` builds an `ApprovalDecision` from the payload with defaults for
`argsDigest` (`sha256:000…`), `descriptorDigest`, `expiresAt` (now), and `keyId`
(`"operator-key-default"`), and records it **without consulting `ApprovalAuthority` at all**.

**Required design.**

```python
def _cmd_ResolveApproval(self, run_id, payload, actor, command_id):
    # 1. The challenge is the authority on what is being approved.
    challenge = self._pending_approvals.require(run_id, payload["decision"]["approvalId"])
    #    → NotFoundError if there is no pending challenge for this run

    # 2. Strict parse. No defaults for any of the eight fields.
    decision = parse_strict_approval_decision(payload["decision"])

    # 3. Cryptographic verification against a registered key.
    self._approval_authority.verify_registered_key(decision.key_id)
    self._approval_authority.verify_signature(decision)
    self._approval_authority.verify_not_expired(decision, now=self._clock.now())

    # 4. Correspondence — the signature must cover *this* challenge.
    require_equal(decision.args_digest,       challenge.args_digest)
    require_equal(decision.descriptor_digest, challenge.descriptor_digest)

    # 5. Only now does a fact exist.
    seq = self.append_fact(run_id, ApprovalResolved(decision=decision, challenge=challenge))
    self._deliver_verified_decision_to_waiter(run_id, decision)
    return {"runId": run_id, "seq": seq, "status": decision.resolution}
```

**Falsifiers RF-C-03…RF-C-07.** (a) missing signature → `invalid_request`; (b) valid signature over a
*different* challenge → `permission_denied`; (c) expired decision → `permission_denied`;
(d) unregistered `keyId` → `unauthenticated`; (e) no pending challenge → `not_found`. Each must
assert **no fact was appended**.

## 8.4 HTTP gateway: authentication, origin policy, size limit

**Defects.** Wildcard `Access-Control-Allow-Origin: *` on every response including approvals
(`studio_gateway.py:57`); no authentication anywhere in the handler; `do_POST` reads
`Content-Length` bytes unbounded (`studio_gateway.py:108`) while UDS enforces 1 MiB; the workspace
file endpoint reads arbitrary files outside the mediated command path.

*Path traversal itself is handled correctly* — `studio_gateway.py:438` resolves then checks
`is_relative_to`, and the suite proves `../../etc/passwd` → 404. The problem is that the endpoint
exists unauthenticated at all.

**Required design.**

```python
MAX_BODY_BYTES = 1 * 1024 * 1024        # identical constant to the UDS server

def _authenticate(self) -> Principal:
    token = self.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if not token:
        raise Unauthenticated("missing bearer token")
    return self.server.token_store.resolve(token)      # raises on unknown/expired

def _cors_headers(self):
    origin = self.headers.get("Origin", "")
    if origin in self.server.allowed_origins:          # configured allowlist; never "*"
        self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")

def do_POST(self):
    length = int(self.headers.get("Content-Length", 0))
    if length > MAX_BODY_BYTES:
        return self._error("frame_too_large")
    principal = self._authenticate()                   # before any body read
    body = self.rfile.read(length)
    frame = route_to_command(self.path, json.loads(body), actor=principal.id)
    return self._respond(self.server.service.execute_command(frame))
```

Additional requirements:

- **Bind actor identity to authentication.** The `actor` field on a command is derived from the
  authenticated principal, never from the request body.
- **Bind default to loopback.** Non-loopback binding requires an explicit flag *and* a configured
  token store; refuse the combination of non-loopback plus no auth.
- **Mediate workspace reads** through a capability selector, or remove the endpoint and serve the
  same need through `ExplainArtifact`.
- Every route maps to a validated command or a read projection. **HTTP handlers never write the
  ledger directly.**

**Falsifiers RF-C-08…RF-C-11.** Unauthenticated request → 401 with no state change; disallowed
origin → no ACAO header; body of `MAX_BODY_BYTES + 1` → `frame_too_large` with the body never fully
read; non-loopback bind without a token store → startup refusal.

## 8.5 UDS: validate every frame; canonical codes only

**Defect.** `server.py:143-166` special-cases `StreamEvents` **before** `execute_command`, reading
`runId` and `afterSeq` from an unvalidated frame. `server.py:132` emits `"code": "invalid_json"`,
which is outside the ten-code vocabulary.

**Required design.**

```python
def _process_client_frame(self, conn, raw_frame):
    try:
        frame = validate_frame_envelope(raw_frame)
        command = validate_command(frame["command"])
    except ContractError as exc:
        return self._send(conn, error_frame(exc.code, exc.message, in_reply_to=raw_frame.get("frameId")))

    if command.name == "StreamEvents":
        # Now — and only now — with a validated run scope and typed afterSeq.
        return self._stream(conn, command)

    return self._send(conn, self.service.execute_command(frame))
```

Plus the standing UDS requirements: NDJSON framing, 1 MiB limit, `0600` socket, response correlation
via `inReplyTo`, command idempotency, cursor resume, duplicate suppression, sequence-gap detection,
clean disconnect/reconnect, graceful shutdown, installed entrypoint.

**Falsifier RF-C-12.** A `StreamEvents` frame with a malformed `afterSeq` and a forbidden `runId`
must be rejected with `invalid_request` **before** any store read.

## 8.6 SSE stream contract

- `afterSeq` query parameter and `Last-Event-ID` header both accepted; header wins on conflict.
- WAL replay **before** live subscription; strictly increasing sequence across the seam.
- Explicit gap response when the requested cursor precedes the retained window.
- Keepalive frames on an idle stream.
- Reconnect without event loss; terminal close after `completed` / `failed` / `cancelled`.

## 8.7 Phase 0 exit criteria

- [ ] No signing seed literal anywhere in the distribution; per-install key at `0600`.
- [ ] No TTY → approval fails closed; no fact appended.
- [ ] Zero defaulted security fields across `service.py` and `studio_gateway.py`.
- [ ] Every approval verified against a pending challenge with a registered key.
- [ ] HTTP authenticated, origin-restricted, size-capped, loopback-default.
- [ ] Every UDS frame validated before state access; only the ten canonical codes emitted.
- [ ] RF-C-01…RF-C-12 all demonstrated failing on the unfixed tree and passing on the fixed tree.

---

# 9. Phase 1 — Runtime Truth

> **Objective.** Restore the M-2 single-writer anchor and make recovery real. Restores I-4 and I-9.
>
> **Lattice position.** `runtime/service/`, `adapters/stores/`. No `kernel/` change.

## 9.1 The dual-truth defect

`service.py:673-703`:

```python
seq = self.store.append_event(run_id, event_envelope, now=now)   # inbox store
env = _envelope_from_service_event(run_id, evt_copy)
self.event_store.append([env])                                   # canonical — Result DISCARDED
# subscribers notified regardless
```

Consequences: an inbox write can succeed while the canonical write fails and the caller still
receives success; subscribers can observe an event absent from canonical history; sequence
allocation and append are not one transaction; `_load_events()` switches between stores depending on
whether the canonical query is empty, creating **state-dependent truth selection**.

## 9.2 The lossy-envelope defect

`service.py:823-850` — `_envelope_from_service_event` rebuilds an `EventEnvelope` from a reduced
dict, substituting defaults for identity fields:

```python
tenant_id      = event.get("tenantId")      or "tenant-default"
owner_id       = event.get("ownerId")       or "owner-platform"
trace_id       = event.get("traceId")       or "trace-service"
span_id        = event.get("spanId")        or "span-service"
principal_role = event.get("principalRole") or "episode"
```

`_ServiceEventStore` (`service.py:852`) then feeds the **runtime's own canonical envelopes** back
through this reducer, so real runtime events have their project identity, parent lineage,
causation/idempotency, and authority provenance flattened on the way to storage.

## 9.3 Target architecture

```text
validated command
   ↓
command / idempotency transaction        (separate store; commands only)
   ↓
Runtime.execute_profiled                 (the one public path)
   ↓
sole LedgerEmitter → sole SqliteEventStore   (atomic seq allocation + append)
   ↓
run status / checkpoint / list / SSE  —  ALL derived projections
```

**Two rules.** (1) There is exactly one canonical event store; the inbox stores *command
idempotency records only*, never event truth. (2) Canonical envelopes are persisted byte-unchanged;
transport frames are constructed **around** them.

## 9.4 Atomic append

```python
def append_event(store, run_id, expected_seq, envelope) -> int:
    with store.transaction():                       # single SQLite transaction
        current = store.last_seq(run_id)
        if expected_seq is not None and expected_seq != current:
            raise ConflictError(expected=expected_seq, actual=current)   # → "conflict"
        next_seq = current + 1
        store.append(run_id, next_seq, envelope)    # envelope persisted unchanged
    # Notification happens strictly AFTER commit. A crash here loses a
    # notification, never a fact; subscribers recover by cursor resume.
    notifier.publish(run_id, next_seq, envelope)
    return next_seq
```

## 9.5 The canonical run worker

```python
def run_worker(request, cancellation):
    append_fact(request.run_id, RunStarted(request))
    try:
        result = runtime.execute_profiled(
            manifest_path = request.manifest_path,
            task_context  = request.task_context,
            profile_id    = request.profile_id,
            model         = request.model,
            store         = canonical_event_store,     # the SAME store, not a wrapper
            listener      = ledger_emitter,
            approval      = verified_approval_callback,
            cancellation  = cancellation,              # cooperative token, see 9.7
        )
        append_fact(request.run_id, RunCompleted(result))
        return result
    except CancellationRequested:
        append_fact(request.run_id, RunCancelled(...))
        return failed_result("cancelled")
    except Exception as exc:
        # An exception is NEVER a completion.
        append_fact(request.run_id, RunFailed(reason=str(exc)))
        return failed_result("internal")
```

The worker persists: run start, every canonical event, approval requests and resolutions,
checkpoints, cancellation, completion or failure, and the final run digest and event sequence.

## 9.6 Real checkpoint and resume

**Defect.** Checkpoint writes `state_json=None` plus a digest and never calls `CheckpointManager`.
Resume emits `RunResumed` and flips a mutable status row — it does not verify the digest, cold
reconstruct, reconcile open effects, or restart execution.

```python
def checkpoint(run_id):
    events         = canonical_store.read(run_id)          # facts only
    reconstruction = checkpoint_manager.reconstruct(events)
    checkpoint     = checkpoint_manager.capture(reconstruction)   # real, reconstructable state
    append_fact(run_id, CheckpointRecorded(checkpoint.digest, checkpoint.seq))
    return checkpoint

def resume(run_id, checkpoint_id):
    checkpoint = verify_checkpoint_against_history(checkpoint_id, canonical_store)
    state      = checkpoint_manager.load(checkpoint)
    reconcile_open_effects(state)                          # no budget leak
    append_fact(run_id, RunRecovered(checkpoint.digest))
    start_runtime_from_reconstructed_state(state)          # joins the trajectory prefix
```

This is the `SPEC.md:130-132` cold-continuation contract: load durable pre-crash events, join the
trajectory prefix, reconcile pending Governor leases, emit `RunRecovered` before a complete
`mhf.trajectory/1` at `EpisodeCompleted`.

## 9.7 Cooperative cancellation

**Defect.** Cancel sets an in-memory boolean the worker never reads; it can only abort a *blocked
approval queue*. A worker can complete successfully after the service recorded cancellation.

```python
def cancel(run_id, reason):
    append_intent(run_id, CancellationRequested(reason))   # durable intent first
    cancellation_port.cancel(run_id)                       # cooperative token the worker polls
    settled = wait_for_terminal_settlement(run_id, timeout=GRACE)
    if settled is None:
        append_fact(run_id, CancellationUndeterminable(...))   # never claim a terminal we did not observe
    return settled
```

The token is checked by the turn loop at turn boundaries and before each effect dispatch. Facts are
never erased by cancellation.

## 9.8 Durable projections and capabilities

- Run status, run listing, and checkpoint listing are **projections folded from canonical events**,
  not mutable tables.
- `GetCapabilities` is derived from actual feature availability with explicit `available`,
  `partial`, `disabled`, `unavailable` states plus a `reasonCode`. A gate that is open reports
  `disabled` with `milestone_gate_open` — it never reports success.
- **No silent fallback from a durable store to `:memory:`.** Failure to open the durable store is a
  startup error.

## 9.9 Phase 1 exit criteria

- [ ] One canonical store; inbox holds command idempotency only.
- [ ] A failed canonical append yields no seq and no notification.
- [ ] Envelope round-trip preserves tenant, owner, project, lineage, causation, authority, trace.
- [ ] Checkpoint persists reconstructable state; resume cold-reconstructs and continues.
- [ ] Cancellation interrupts a running worker at a turn boundary.
- [ ] An exception never produces a `completed` terminal.
- [ ] Fresh-process replay reproduces terminal state and digest (RF-92 / B3-WAL-recovery green).

---

# 10. Phase 2 — Protocol and Schema Convergence

> **Objective.** Restore axiom **A-4** and invariant **I-8**.

## 10.1 The two A-4 violations

**Violation 1 — handwritten mirror that has drifted.** `SPEC.md:75` requires generated readers to
replace handwritten mirrors. `contract.py:1` describes itself as a handwritten mirror, and it
disagrees with the schema:

| Command | `runtime-service.schema.json` | `contract.py` |
|---|---|---|
| `StartRun` payload | `manifestPath, repoPath, brief, profileId` (`additionalProperties: false`) | also allows `model`, `episodeId`, `expectedSeq` |
| `ListRuns` payload | `cursor`, `limit` | `limit`, **`offset`** |
| `StreamEvents.afterSeq` | `IntString` `$ref` | accepted untyped |
| `expectedSeq` | absent from every payload schema | allowed on 8 commands |

**Violation 2 — validation is fail-open in production.** `pyproject.toml:36-40` places
`jsonschema>=4.23.0` under `[project.optional-dependencies].dev`, while
`agency/manifests/loader.py:16-20` imports it inside `try/except` and `loader.py:138` only validates
`if _HAS_JSONSCHEMA and schema`. **In an ordinary `pip install vanguard-runtime`, manifest schema
validation silently does nothing.** This is the §6.1 anti-pattern 4 at its most consequential: the
system's declared source of wire truth is disabled by default in the shipping configuration.

## 10.2 Required remediation

1. **Move `jsonschema` to `[project.dependencies]`.** Delete the `try/except` and the
   `_HAS_JSONSCHEMA` guard. A missing validator becomes an import error at startup, not a silent
   downgrade.
2. **Choose one authoritative shape per command.** Recommendation: the JSON Schema wins on payload
   membership (`cursor`, not `offset`), and `expectedSeq` is promoted to an **envelope-level**
   optional field rather than a per-payload one, since it is a concurrency control concern and not
   command data. Amend the schema and regenerate/derive the Python reader mechanically.
3. **Register `runtime-service.schema.json` in `schemas/v4/MANIFEST.md`.**
4. **Create the shared vector corpus** at `schemas/v4/vectors/runtime-service/{valid,invalid}/`,
   consumed by **both** a Python test and a TypeScript test.
5. **Correct `contract.py:11-13`**, which currently cites `test/runtime/test_contract_vectors.py`
   and `client-core/test/contract-vectors.test.ts` as proof of cross-language agreement. **Neither
   file exists.** Either create them (preferred) or delete the claim. A docstring asserting a
   verification that does not exist is worse than no docstring.

## 10.3 Required negative vectors

Each must be present in the shared corpus with an `.expect.json` naming the exact error code:

```
unknown frame type              wrong protocol version         missing frame ID
invalid inReplyTo               unknown command                unknown command field
unknown payload field           missing run ID                 forbidden run ID
invalid approval signature      unknown error code             oversized frame
receipt containing both success and error
event frame containing receipt-only fields
```

## 10.4 Client-core constraint

Do **not** add a runtime JSON-Schema dependency to `client-core`. It validates with existing
lightweight parsers plus the shared vectors. Removing a public export requires a deprecation note or
a beta-breaking-version note.

## 10.5 Phase 2 exit criteria

- [ ] `jsonschema` is a runtime dependency; no `_HAS_JSONSCHEMA` guard remains.
- [ ] Zero schema/`contract.py` disagreements; the reader is generated or mechanically derived.
- [ ] `runtime-service.schema.json` listed in `MANIFEST.md`.
- [ ] Shared vector corpus exists and is consumed by both languages.
- [ ] `contract.py` docstring is true.

---

# 11. Phase 3 — Distribution and CLI Hardening

> **Objective.** Make the standalone backend CLI installable, safe, and truthful.
> **Publication is gated on Phase 0.**

## 11.1 Defect inventory

| # | Location | Defect |
|---|---|---|
| a | `cli.py:60` | `Path(__file__).resolve().parents[3] / "vanguard" / "packages" / …` resolves only from a repo checkout. Installed into site-packages the manifest path does not exist — **the console script cannot work when installed**. |
| b | `cli.py:48` | `.vanguard/` created unconditionally on every invocation in whatever directory you are standing in. |
| c | `cli.py:136` | `os.popen(f"git -C {workspace} diff")` — unquoted interpolation of a user-supplied path into a shell. |
| d | `cli.py:51-58` | Parses `.env` and writes every key into `os.environ` globally, with no allowlist. |
| e | `cli.py` overall | Single positional task only. Exit codes 0/1 with no distinction for *unavailable capability*. |
| f | `install_vanguard.sh:22` | Hardcodes `/usr/bin/python3` after validating whichever `python3` is on `PATH` — validates one interpreter, runs another. |
| g | `install_vanguard.sh` | No venv, no dependency install, no version pin, no checksum, no signature, no uninstall path. It writes a `PYTHONPATH` shim to the local clone: a dev convenience, not an installer. |
| h | `pyproject.toml:30-34` | Ships `vanguard-studio` as an installed binary — i.e. the unauthenticated wildcard-CORS gateway of §8.4. |

## 11.2 Required CLI surface

```
vanguard --version
vanguard doctor          # environment, key state, store state, capability truth
vanguard init            # create ~/.vanguard/keys + workspace .vanguard/ EXPLICITLY
vanguard run "<brief>"   # canonical Runtime.execute_profiled path
vanguard resume <run-id>
```

Rules:

- **Resource resolution via `importlib.resources`**, never `parents[N]` arithmetic.
- **`.vanguard/` is created only by `init`.** `run` in an uninitialized workspace fails with a
  message naming `init`.
- **`subprocess.run([...])` with an argument list**, never `os.popen` with an f-string.
- **`.env` keys are read into a scoped mapping** passed to the adapter, never into global
  `os.environ`.
- **Exit codes are typed**: `0` success, `1` task failure, `2` invalid usage, `3` capability
  unavailable, `4` authorization denied. Truthful exit codes are part of the fail-closed contract.
- The CLI's store path is always file-backed (`{workspace}/.vanguard/events.sqlite3`).

## 11.3 Installer requirements

Before publication the installer must be: reviewed, version-pinned, checksum-verifiable,
signature-verifiable, venv-based (`~/.vanguard/venv`), dependency-locked, and reversible
(documented uninstall). It must not require provider keys or network access after installation, and
it must use the **same** interpreter it validated.

**The `curl … | bash` convenience form is not published** until all of the above plus Phase 0 are
complete. Documentation shows the inspect-then-run form:

```bash
curl -fsSL https://<host>/install_vanguard.sh -o /tmp/install_vanguard.sh
less /tmp/install_vanguard.sh
sha256sum /tmp/install_vanguard.sh          # compare against the published digest
bash /tmp/install_vanguard.sh
```

## 11.4 Console script policy

`vanguard-studio` must not be an installed entry point while the gateway is unauthenticated. Either
remove it from `[project.scripts]` until §8.4 lands, or make it refuse to start without a configured
token store and origin allowlist.

---

# 12. Phase 4 — Evidence Governance Restoration

> **Objective.** Make milestone acceptance mechanically possible. **This is the highest-leverage
> phase in the program and the cheapest.** It unblocks M-4, M-6, and M-6.5 simultaneously, and
> therefore M-7 and M-8 behind them.

## 12.1 The gap

`domain/evidence/envelope.py:230-245` implements `accepts()` correctly — it refuses self-acceptance,
non-`passed` outcomes, and subject drift. But:

- `tools/runners/` contains only `build_evidence_bundle.py`, `run_rf95_product_proof.py`,
  `run_m5b_formal_proof.py`, `run_swe_challenge.py`. **There is no acceptance tool.**
- `tools/linters/` contains 22 linters. **There is no acceptance gate.**
- Four bundles exist; **zero acceptance envelopes exist.**

The mechanism is sound and the process is absent. No milestone can close in this state.

## 12.2 Reviewer identity

Establish a reviewer identity distinct from every producer identity, with its own Ed25519 key.
Reviewer keys live at `~/.vanguard/keys/<identity>.ed25519`, mode `0600`, and are registered in a
repository-tracked public-key roster so `accepts()` and CI can resolve them.

The reviewer must be able to reproduce the bundle's claim **in a clean environment**. This is why
portability (§12.5) is a precondition, not a nicety.

## 12.3 Acceptance tool

```python
# tools/runners/accept_evidence.py
def main(bundle_path: Path, verdict: str, reviewer_identity: str) -> int:
    produced = EvidenceEnvelope.load(bundle_path)

    # The reviewer reproduces the claim before signing anything.
    report = reproduce(produced)              # re-runs pinned commands in a clean env
    if not report.reproduced:
        verdict = "undeterminable"            # first-class, not a failure to hide

    reviewer = load_signer(reviewer_identity)
    if reviewer.identity == produced.producer.identity:
        raise SelfAcceptanceError("ADR-0101 §3: reviewer must differ from producer")

    acceptance = EvidenceEnvelope(
        schema    = "aether.evidence/1",
        kind      = "acceptance",
        producer  = reviewer.as_producer(),
        subjects  = [produced.digest()],       # binds THIS artifact, no drift
        outcome   = {"pass": "passed", "reject": "failed"}.get(verdict, "undeterminable"),
        detail    = report.summary,
        protocol  = produced.protocol,
        environment = current_environment_identity(),
    )
    acceptance = reviewer.sign(acceptance)
    out = bundle_path.with_suffix(".acceptance.json")
    out.write_bytes(canonical_json(acceptance))     # JCS
    assert accepts(acceptance, produced) or acceptance.outcome != "passed"
    return 0
```

## 12.4 Acceptance and consistency linter

```python
# tools/linters/check_evidence_acceptance.py
EVIDENCE = ROOT / "docs" / "03_execution" / "evidence"

def main() -> int:
    failures = []
    for bundle in sorted(EVIDENCE.glob("*.json")):
        if bundle.name.endswith(".acceptance.json"):
            continue
        produced = EvidenceEnvelope.load(bundle)

        # 1. A producer bundle must be signed to be EVIDENCE_READY.
        if not produced.signature:
            failures.append(f"{bundle.name}: unsigned producer bundle")

        # 2. Acceptance must exist, be independent, and bind this digest.
        acc_path = bundle.with_suffix(".acceptance.json")
        if not acc_path.exists():
            failures.append(f"{bundle.name}: no acceptance envelope")
            continue
        acceptance = EvidenceEnvelope.load(acc_path)
        if not accepts(acceptance, produced):
            failures.append(f"{bundle.name}: acceptance invalid (self/drift/outcome)")

        # 3. Cross-check the board. This is the narrowed MM3 §4c item:
        #    check_execution_truth.py already validates vocabulary; nothing
        #    validates that the board's claimed state matches the artifacts.
        board_state = read_board_state_for(produced.milestone)
        if board_state == "EVIDENCE_READY" and not produced.signature:
            failures.append(f"{produced.milestone}: EVIDENCE_READY with unsigned bundle")
        if board_state == "ACCEPTED" and not acc_path.exists():
            failures.append(f"{produced.milestone}: ACCEPTED without acceptance receipt")
    ...
```

This linter is what makes "no receiptless `ACCEPTED`" mechanically enforced rather than a
convention.

## 12.5 Repair the M-4 evidence chain

Two defects make the M-4 bundle un-reviewable regardless of who signs it:

1. **Unbound preregistration.** `tools/runners/run_rf95_product_proof.py` constructs `TaskContext`
   with no `preregistration=` argument. `root.py:262-265` reads
   `task_context.preregistration or {}`, so `preregistration_digest` lands empty. The candidate is
   bound to its frozen document by commit ordering rather than by an in-run digest — which is
   precisely what RF-95 forbids.

```python
prereg_path  = repo_path / "TASK.md"
prereg_bytes = prereg_path.read_bytes()
task = TaskContext(
    brief      = prereg_bytes.decode("utf-8"),
    repo_path  = repo_path,
    run_id     = "run-rf95-live",
    episode_id = "episode-rf95-live",
    project_id = "calc-fix",
    max_turns  = 20,
    preregistration = {
        "preregistration_digest": "sha256:" + hashlib.sha256(prereg_bytes).hexdigest(),
        "preregistration_uri":    prereg_path.as_uri(),
        "frozen_at":              "<from the preregistration envelope>",
    },
)
```

Apply the same fix to `run_swe_challenge.py`. (`run_m5b_formal_proof.py` binds differently, via
`assert_task_set_is_pinned()` over formula+oracle digests — leave that mechanism alone.)

2. **Non-portable artifacts.** The bundle references a volatile `/tmp/.../events.sqlite3`. Copy
   immutable evidence into a content-addressed, repository-supported location before signing.

Then re-run the candidate, rebuild the bundle, sign it, and obtain an independent acceptance.

## 12.6 Runner default-model drift

Only `run_rf95_product_proof.py:203` resolves `get_default_model()`. `run_m5b_formal_proof.py:163`
hardcodes `deepseek/deepseek-v4-flash-0731`; `run_swe_challenge.py:335` hardcodes
`openrouter/free`. Route **all** runners through the registry resolver so `D_R` model identity has
one source. Hardcoded model literals in evidence-producing runners are an `D_R` integrity hazard.

## 12.7 Baseline succession — `CONVERGENCE-BASE-v1`

Per ADR-0102, `M-5A-BASE-v2` is `CONTAMINATED_UNPUBLISHED` (local lightweight ref, absent from the
remote, contains successor treatment code). It is retained as history and never moved, recreated, or
validated by prose.

The successor manifest (`aether.baseline/1`) binds: annotated **remote** tag object, commit digest,
tree digest, package version, dependency-lock digest, schema and reducer pin digests, prohibited
treatment paths, required gate receipts, creator identity, and independent reviewer identity with a
signed disposition. Missing, weak, lightweight, unpushed, or contaminated → **fail closed**.

**Creation is gated on:** clean declared-dependency gates, independent review of C1 work (§12.3),
and an RF-86/RF-98 rerun against the new tag. Only after the tag is created and remotely verifiable
may the M-5b treatment be compared against it.

## 12.8 Phase 4 exit criteria

- [ ] A reviewer identity exists with a registered key, distinct from all producers.
- [ ] `accept_evidence.py` and `check_evidence_acceptance.py` exist and are in CI.
- [ ] M-4 and M-6 bundles are **signed** and portable.
- [ ] Independent acceptance envelopes exist for M-4, M-6, M-6.5.
- [ ] All runners resolve the model through the registry.
- [ ] `CONVERGENCE-BASE-v1` is annotated, pushed, remotely verified, and reviewed.

---

# 13. Phase 5 — M-7 Topologies Through One Runtime

> **Objective.** Bind digest-pinned, authority-free run-plan extensions into the existing runtime;
> execute three topologies through one public path; measure; record ADR-0099.
>
> **Gate contract:** [`milestones.md:100-107`](../../03_execution/milestones.md).
> **Work packages:** WP-A3 (integration), WP-B3 (measurement).

## 13.1 Current state

`topology.py` (~435 lines) contains a parser, authority rejection, deterministic lowering, selector
analysis, and a sequential scheduler. It is good, correct, authority-free work.

**It has zero call sites.** Verified: `root.py`, `run_plan.py`, `compose.py`, and `session.py`
contain **no occurrence of the string `topology`**. `run_plan.py` has no `extensions` field. The
only consumers are unit tests.

The board's row — *"Topology library present; public runtime integration absent"* — is accurate.

## 13.2 The extension contract

```python
@dataclass(frozen=True, slots=True, order=True)
class RunPlanExtensionRef:
    schema:       str      # e.g. "aether.topology/1"
    digest:       str      # sha256: of the canonical artifact
    artifact_ref: str      # content-addressed location
    required:     bool     # unknown + required → fail closed
```

Refs are **sorted and immutable**, and they enter runtime identity (`D_R`). An unknown *required*
extension fails the run closed; an unknown *optional* extension is recorded and ignored.

## 13.3 Integration point

```python
# vanguard/packages/runtime/root.py :: run_composed — BEFORE the first authorized read

def _bind_topology(task_context, frozen_composition, store):
    ref = verify_extension_ref(task_context.extensions)      # sorted, digest-pinned
    if ref is None:
        return None                                          # disabled path: identical behavior

    artifact  = load_digest_pinned(ref)                      # digest verified on load
    topology  = parse_topology(artifact)
    _reject_authority(topology)                              # no grant/verb/sink may appear
    extension = lower_topology(topology, frozen_composition) # deterministic lowering
    append_fact(RunPlanExtensionAccepted(
        extension_digest = extension.digest(),
        lowering_digest  = extension.lowering_digest(),
        scheduler_digest = SEQUENTIAL_SCHEDULER_DIGEST,
        refs             = sorted(extension.refs()),
    ))
    return extension
```

## 13.4 Execution loop

```python
def execute_topology(extension, store, scheduler):
    settled = fold_settled_operations(store)          # cold-foldable, not in-memory
    while incomplete(extension, settled):
        ready = ready_operations(extension.operations, settled=settled)
        if not ready:
            raise TopologyStalled("no ready operations and work remains")   # cycle/unsettled
        for decision in scheduler.decide(ready, settled):
            execute_as_ordinary_m6_child(decision)    # ordinary mediated delegation
            settled = cold_fold_settlement(store)     # re-fold from facts each wave
    return reconstruct_final_state(store)
```

**Non-negotiable properties.**

- One public runtime, one event system, one budget model, one authority model, one sequential
  reference scheduler.
- Topology **cannot create authority**. It selects among capabilities that the frozen composition
  already grants.
- **Causal edges override disjoint resource selectors.** If A→B is declared causal, disjoint
  selectors do not make them reorderable.
- **Unknown selectors fail closed** and count as non-parallelizable.
- **Disabled topology preserves declared parity** — identical identity and event stream.
- Digest is stable across runs; budget is conserved.

## 13.5 The three required patterns

| Pattern | Shape | What it proves |
|---|---|---|
| **Direct** | single specialist | Extension binding does not perturb the ordinary path |
| **Planner → Executor → Reviewer** | three roles, linear causal chain | Roles are lineages with policies, not classes; ordinary M-6 delegation suffices |
| **Planner → 2 Readers → Merger** | fan-out then causal merge | Merge is causal, deterministic, and fail-closed on unknown selectors |

## 13.6 Telemetry — correlated, never a second truth

Timing is **operational telemetry**, correlated by run, episode, operation, descriptor,
idempotency key, and process epoch. It is captured on a **monotonic** clock.

- Ledger timestamps remain causal wall observations.
- Timing is **never** patched into `EffectStarted` and **never** becomes a budget dimension.
- Telemetry loss cannot alter a projection or a verdict.
- Target: median overhead < 3% on the declared workload; declare host, dependencies, data,
  distributions.

## 13.7 M7-01 measurement and ADR-0099

WP-B3 is an **exterior, read-only** measurement (`lab/m701_independence.py`). A pair of operations is
*eligible* for concurrency only if it has: no causal order, **proven** disjoint selectors, compatible
sinks, safe idempotency, and complete timing. Unknown or missing selector, sink, occurrence, or
timing **serializes the pair and counts as incomplete**.

Report: eligible duration, critical path, sequential makespan, completeness ratio, contention,
cache behavior, recovery, and simulated bounded-read lift with intervals.

**Decision rule.** Recommend read-only parallelism with `max_parallelism=2` **only if** preregistered
thresholds pass with zero state/verdict divergence and zero duplicate privileged occurrence.
Otherwise `SEQUENTIAL_CONFIRMED`. Writes, spawn, promotion, and shared or unknown sinks stay
sequential unconditionally.

**ADR-0099 does not exist as a file, and that is correct** — `INDEX.md:165` reserves the number until
M7-01 evidence exists. Do not "fix" the gap by inventing one. **M-7 may close as
`SEQUENTIAL_CONFIRMED`; it may not close without the decision recorded.**

## 13.8 Phase 5 exit criteria

- [ ] Three topologies execute through `Runtime.run_composed`.
- [ ] Extension identity enters `D_R`; replay reproduces it.
- [ ] Disabled-path parity proven (identical identity + event stream).
- [ ] Authority-bearing topology, unknown role/composition/selector, bad artifact flow, missing
      required extension, cycle, crash, and replay all fail closed.
- [ ] Correlated monotonic telemetry with completeness accounting.
- [ ] Signed M7-01 report, independently reviewed.
- [ ] ADR-0099 accepted with an explicit disposition.

---

# 14. Phase 6 — M-8 Durable Authorized Memory

> **Objective.** Implement the memory half of ADR-0100. **Work package:** WP-A4.
> **Constraint:** the Kernel gains no memory branch. Memory is a derived capability family
> reached through ports.

## 14.1 The falsifier that is currently the implementation

`vanguard/packages/runtime/memory.py:27-28`:

```python
def permitted(self) -> bool:
    return bool(self.grant_ref and self.tenant and self.project and not self.revoked)
```

A non-empty string is authority. `grant_ref="x"` passes. There is no issuer, subject, action,
selector, purpose, expiry, revocation epoch, signature, or verification receipt. ADR-0100 exists
specifically to reject this shape.

`adapters/stores/memory_engine.py` (~87 lines) is generic SQLite with no tenant/category
authorization, no content-addressed blobs, no use-time revocation, no retrieval receipts, no legal
hold, quarantine, or GC.

## 14.2 Authorization contract

```python
# vanguard/packages/ports/memory.py

class MemoryAuthorizationPort(Protocol):
    def verify(self, grant, *, action, selector, tenant, project, purpose, now
               ) -> AuthorizedMemoryContext: ...
        # Raises on: forged signature, unknown issuer, expired, revoked epoch,
        # selector outside grant, tenant/project mismatch, purpose mismatch.
        # NEVER returns a partially-authorized context.

@dataclass(frozen=True, slots=True)
class AuthorizedMemoryContext:
    issuer: str; subject: str; action: str
    selector: ResourceSelector
    tenant: str; project: str; purpose: str
    expires_at: str; revocation_epoch: int
    policy_identity: str
    receipt: VerificationReceipt        # proof this verification happened
```

**Verification happens at use time**, not at construction. A context is not a token to be cached
past its epoch.

## 14.3 Retrieval — authorization strictly precedes ranking

```python
def retrieve(query, grant, *, category, tenant, project, purpose, budget, now):
    auth = memory_authority.verify(
        grant, action="memory.read", selector=selector_for(query),
        tenant=tenant, project=project, purpose=purpose, now=now)

    # Authorization and scope filtering happen in the STORE QUERY, so the
    # ranker never observes an unauthorized candidate. Ranking unauthorized
    # candidates leaks their existence through score distances — a side channel.
    candidates = metadata_store.find_authorized(auth, category=category, query=query)

    ranked   = deterministic_rank(candidates)      # quantize, tie-break by record id
    selected = budget_pack(ranked, budget)

    receipt = persist_retrieval_receipt(
        auth=auth, query_digest=digest_of(query),
        candidate_ids=[c.id for c in candidates],
        selected_ids=[s.id for s in selected],
        dropped_ids=[d.id for d in ranked[len(selected):]],
        policy_identity=auth.policy_identity,
        index_identity=metadata_store.index_identity(),
        tokenizer_identity=budget.tokenizer_identity,
        redacted=any(s.redacted for s in selected))

    # Dereference blobs only for authorized, selected records.
    return dereference_authorized_blobs(auth, selected), receipt
```

**Provenance reaches model context.** Every retrieved item arrives with source, scope, digest, and
the authorization receipt. Retrieval that enters model context without a receipt is a falsifier
violation.

## 14.4 Write path — blob first, metadata second, fact third

```python
def record(value, grant, *, category, tenant, project, now):
    auth = memory_authority.verify(grant, action="memory.write", ..., now=now)
    canonical = canonicalize_and_redact(value, auth.policy_identity)   # JCS

    blob_digest = cas_blob_store.put(canonical)          # 1. content-addressed blob
    with metadata_store.transaction():                   # 2. scoped metadata + index
        record_id = metadata_store.insert(
            digest=blob_digest, category=category,
            tenant=auth.tenant, project=auth.project,
            authorization_receipt=auth.receipt.digest())
    append_fact(ClaimRecorded("memory.recorded/1", record_id, blob_digest))   # 3. causal fact
    return record_id
```

Crash-boundary semantics: a blob without metadata is an **orphan** (GC-able); metadata without a
causal fact is **quarantined**, not served.

## 14.5 Lifecycle operations

| Operation | Semantics |
|---|---|
| `append` | New immutable record; never mutates an existing one |
| `supersede` | New record + a durable supersession edge; the prior record remains addressable |
| `invalidate` | Append-only invalidation fact; the record stops being served, history is preserved |
| `revoke` (grant) | Increments the revocation epoch; **use-time** checks fail immediately, including cached contexts |

## 14.6 Storage model

- **SQLite-WAL** for scoped metadata, indexes, invalidations, and retrieval receipts.
- **Content-addressed store (CAS)** for content.
- Deterministic indexing; corrupt index rebuilds or blocks by profile.
- **Refuse WAL on a network filesystem.**
- Migration is a digest-verified export/import.

## 14.7 Isolation and failure semantics

- Cross-tenant, cross-project, or cross-category access is an **opaque** `Denied` /
  `DID_NOT_OCCUR` — never a distinguishable "exists but forbidden."
- An authorization-service outage fails sensitive use **closed**.
- Forged, expired, revoked, and out-of-scope are indistinguishable to the caller.

## 14.8 Retention, legal hold, quarantine, GC

- Retention classes are `digests_only | standard | full`. **Retention never authorizes capture.**
- Legal hold pins records against GC and against invalidation-driven sweep.
- Quarantine holds metadata whose causal fact is missing.
- GC marks roots, honors legal hold, runs a **reviewed dry run** first, and emits sweep receipts.
- Restore is digest-verified.

## 14.9 Performance targets (declared host)

| Operation | Target |
|---|---|
| Atomic 4 KiB write | p95 < 50 ms |
| Lexical recall at 100k records, `limit ≤ 20` | p95 < 100 ms |

Benchmarks must name host, dependencies, data, and distributions.

## 14.10 Phase 6 exit criteria

- [ ] `AuthorizedMemoryContext` is produced only by cryptographic verification.
- [ ] Authorization precedes ranking **and** artifact dereference.
- [ ] Four categories with four ports; SQLite-WAL metadata + CAS blobs.
- [ ] Append / supersede / invalidate / revoke are durable and recoverable.
- [ ] Retrieval provenance reaches model context with a receipt.
- [ ] Tenant/project/category isolation proven; leaks fail closed and opaque.
- [ ] Retention, quarantine, legal hold, GC, restore all durable.
- [ ] Fresh-process recovery reconstructs all of the above.
- [ ] Independent security review.

---

# 15. Phase 7 — M-8 Governed Learning and Rollback

> **Objective.** Implement the promotion half of ADR-0100. **Work package:** WP-B4.

## 15.1 Current state

`vanguard/packages/runtime/governance/learning.py:367` — the durable composition registry:

- **skips signature verification when no verifying keys are configured** (the §6.1 anti-pattern 2);
- does not enforce generator ≠ evaluator ≠ promoter;
- does not fully cross-bind candidate, report, manifest, and evidence identities;
- permits unsigned rollback;
- changes only the registry head and does not prove that served runtime behavior changed or was
  restored.

## 15.2 Authority separation (structural, not conventional)

```
generator_id ≠ evaluator_id ≠ promoter_id
```

Distinct identities, **distinct keys, distinct stores, distinct roles**. Enforced properties:

- The generator cannot read held-out labels or the promoter's keys.
- The evaluator cannot promote.
- The promoter cannot author a candidate.

## 15.3 Sealed workloads

Seal the digests of the development, held-out, adversarial, and transfer splits **before** any
candidate is generated. A candidate produced after a split digest changed is contaminated and
rejected. Contamination is a falsifier, not a warning.

## 15.4 Evaluation

Paired evaluation records, per item: `present`, `retrieved`, `invoked`, `grounded`, `verified`,
`outcome`. Requirements:

- Preregistered lift with confidence interval, exact test, Holm correction.
- ≤ 5% baseline-success regression budget.
- Zero critical security regressions.
- **Presence-only gains are rejected** — a skill that was present but never invoked, or invoked but
  not grounded, receives no credit.
- 100% of directives attributable.

## 15.5 Promotion — signed CAS

```python
def promote(candidate, report, promotion):
    require(candidate.generator_id != report.evaluator_id != promotion.promoter_id)
    verify_candidate_manifest(candidate)          # base, skills, policies, retrieval policy, sources
    verify_sealed_workload(report)                # split digests match the pre-seal
    verify_evaluator_signature(report)
    verify_held_out_lift(report)                  # preregistered thresholds
    verify_regression_budget(report)
    verify_promoter_signature(promotion)
    verify_cross_binding(candidate, report, promotion)   # each names the others' digests

    with registry.transaction():                  # durable SQLite CAS
        head = registry.current_head()
        if promotion.base_digest        != head.digest:      raise ConflictError("stale head")
        if promotion.expected_generation != head.generation: raise ConflictError("stale generation")
        registry.promote(candidate=candidate, previous=head, generation=head.generation + 1)
        append_fact(CompositionPromoted(candidate.digest, head.generation + 1))

    runtime.reload_verified_head()                # promotion must be RUNTIME-VISIBLE
    prove_behavior(candidate.digest)              # observed behavior matches the promoted digest
```

A missing transition receipt quarantines the head rather than serving an unverified composition.

## 15.6 Rollback — must restore served behavior

```python
def rollback(target_generation, promotion_signature):
    verify_promoter_signature(promotion_signature)     # unsigned rollback is refused
    with registry.transaction():
        head = registry.current_head()
        registry.restore(target_generation, expected_head=head.digest)   # another signed CAS
        append_fact(CompositionRolledBack(target_generation, reason=...))
    runtime.reload_verified_head()
    prove_behavior(registry.current_head().digest)     # prior BEHAVIOR restored, not just a pointer
```

**The acceptance test is behavioral.** Inject a real regression, promote it, observe the degraded
behavior, roll back, and observe the prior behavior restored **in a fresh process**. A registry
pointer that moves without a behavioral change does not satisfy M-8.

## 15.7 Falsifier roster for Phases 6–7

| # | Falsifier | Must |
|---|---|---|
| 1 | Literal/non-empty grant accepted without cryptographic verification | fail |
| 2 | Cross-tenant / project / category leak | fail closed, opaque |
| 3 | Expired or revoked grant succeeds from cache | fail |
| 4 | Ranker observes unauthorized candidates before filtering | fail |
| 5 | Retrieval enters model context without a receipt | fail |
| 6 | Candidate sees held-out labels, or shares identity/key with evaluator or promoter | fail |
| 7 | Presence-only skill receives credit | fail |
| 8 | Two promoters race; both become head | fail (one must lose on CAS) |
| 9 | Rollback moves the registry pointer but not runtime composition | fail |
| 10 | Restart loses memory, promotion head, or provenance | fail |
| 11 | Kernel or generic episode loop gains a memory/skill-specific branch | fail (I-7) |

## 15.8 Phase 7 exit criteria

- [ ] Generator/evaluator/promoter separation enforced structurally.
- [ ] Sealed workloads verified; contamination rejected.
- [ ] Held-out lift measured with preregistered statistics and regression budgets.
- [ ] Promotion is a durable signed CAS; concurrent promoters conflict correctly.
- [ ] Promotion is runtime-visible and behaviorally proven.
- [ ] Injected-regression rollback restores prior behavior in a fresh process.
- [ ] All 11 falsifiers green, each demonstrated failing on the unfixed code.
- [ ] Crash/restart recovery for memory, head, and provenance.
- [ ] Independent security, recovery, performance, RF-98, and TCB review.

---

# 16. M-9 / M-10 Compatibility Boundary

## 16.1 Position

**M-9 and M-10 receive no code, no port files, no service skeletons, no placeholder packages, no
schemas, and no new planning documents in this program.**

This is not conservatism; it is the standing authorization:

- `sprint_active.md:141` — "No M-9/M-10 feature or scaffold."
- `milestones.md:126-131` — reserve only **low-cost seams that already exist**; do not implement
  distributed scheduling, topology search, continuous-learning services, model training, causal
  self-model frameworks, or a second runtime before M-8 acceptance **and measured need**.
- `SPEC.md:201` — "M-9/M-10 — post-MVP — compatibility horizon only until M-8 is independently
  accepted."

A prior review proposed creating `ports/distributed.py` and `ports/promotion.py`. That is precisely
the prohibited act, and it is also unnecessary — see §16.2.

## 16.2 What "compatibility seam" already means here

The seams M-9/M-10 will eventually need **already exist** as artifacts of M-7 and M-8 work:

| Seam | Where it already lives | Reserved for |
|---|---|---|
| Immutable run-plan extension refs | `RunPlanExtensionRef` (Phase 5) | M-9 distributed plan transport |
| Authorized memory ports | `MemoryAuthorizationPort` + four category ports (Phase 6) | M-9 multi-node memory |
| Immutable composition manifests | Candidate manifests (Phase 7) | M-10 architecture evolution |
| Evidence envelopes | `aether.evidence/1` | M-9/M-10 acceptance |
| Exterior candidate-generator boundary | Generator/evaluator/promoter split (Phase 7) | M-10 self-modification governance |
| Language-neutral canonical schemas | `schemas/v4/` + shared vectors (Phase 2) | M-9 polyglot conformance |

**Building these correctly for M-7 and M-8 *is* the M-9/M-10 scaffolding.** No additional file is
required, and an additional file would be an unauthorized, untested, unfalsifiable surface.

## 16.3 The design discipline that keeps the horizon open

While implementing Phases 5–7, prefer the shape that does not foreclose M-9/M-10:

- Keep identity **content-addressed** rather than location-addressed, so a future node boundary is a
  transport change and not an identity change.
- Keep the scheduler an **injected policy** with a digest, so a future distributed scheduler is a
  different policy rather than a different runtime.
- Keep authorization **verification-at-use**, so a remote memory service is a different adapter
  behind the same port.
- Keep promotion a **signed CAS over an immutable manifest**, so a future exterior generator changes
  nothing about who may promote.

## 16.4 When M-9 may be authorized

After M-8 is independently accepted, and only by a new authorization, M-9 becomes the v1.0
integration and transfer release: stable public backend protocol with a compatibility policy;
coding plus formal plus a third transfer/research workload; three topologies; long-run recovery;
operational SLOs; one polyglot conformance implementation if still justified; installation and
independent-user qualification; and no known P0/P1 law/code/evidence contradiction.

M-10 remains post-1.0 research into causal self-models or architecture evolution, admitted only by
**measured superiority over simpler methods** and governed through the M-8 candidate/evaluator/
promoter path.

---

# 17. Verification, Falsifiers and Test Strategy

## 17.1 The falsifier discipline

A falsifier is not a test that passes. It is a test that **fails on the defect and passes on the
fix**, and whose failure mode has been *observed*. Every phase in this guide names its falsifiers;
none may be marked green without having been seen red.

## 17.2 Coverage gap analysis

The eight architectural linters pass while I-5 is broken. That is a coverage gap, and it is
addressable:

| Proposed check | Would have caught |
|---|---|
| `check_no_embedded_key_material.py` — reject byte literals ≥16 bytes flowing into a signer constructor | §8.1 hardcoded operator seed |
| `check_no_security_defaults.py` — reject `.get("<security field>", <default>)` for signature/digest/expiry/keyId | §8.3 `dummy-sig-approved` |
| `check_no_optional_security_dep.py` — reject `try: import <validator>` guarding a mandatory check | §10.1 `jsonschema` fail-open |
| `check_result_not_discarded.py` — reject a bare-expression call returning `Result` | §9.1 discarded append result |
| `check_evidence_acceptance.py` — §12.4 | unsigned `EVIDENCE_READY`, receiptless `ACCEPTED` |

These are cheap, they are all AST-expressible, and each one encodes a defect this program actually
shipped. Recommend adding them during Phase 0–2 rather than after.

## 17.3 Verification order

Run in this order; a failure stops the ladder:

```
 1  documentation / status consistency        11  HTTP route tests
 2  schema and code-generation checks         12  SSE reconnect / gap tests
 3  boundary and domain-blindness checks      13  client-core tests
 4  TCB budget                                14  approval signature tests
 5  isolation and secret scanning             15  M-7 falsifiers
 6  Python contract vectors                   16  M-8 security + rollback falsifiers
 7  TypeScript contract vectors               17  full suite
 8  RuntimeService command tests              18  fresh-process recovery suite
 9  SQLite-WAL restart / replay / CAS         19  evidence acceptance gate
10  qualified Linux UDS tests                 20  independent evidence review
```

## 17.4 Focused commands per phase

```bash
# Phase 0
python3 -m unittest test.security -v
python3 -m unittest test.runtime.test_studio_gateway -v

# Phase 1
python3 -m unittest test.falsifiers.test_rf92_durable_event_stream -v
python3 -m unittest test.contracts.test_b3_wal_recovery -v
python3 -m unittest test.integration.test_stream_reconnect -v

# Phase 2
python3 -m unittest discover -s test/contracts -t .

# Phase 5
python3 -m unittest test.falsifiers.test_m7_topology_and_independence -v
python3 -m unittest test.contracts.test_m7_measurement_and_independence -v

# Phases 6–7
python3 -m unittest test.runtime.test_governed_learning -v
python3 -m unittest discover -s test/security -t .

# Always
python3 -m unittest discover -s test -t .
for l in check_boundaries check_tcb_budget scan_secrets check_domain_blindness \
         check_isolation_policy check_execution_truth check_markdown_links \
         check_stale_paths; do python3 tools/linters/$l.py || echo "FAIL $l"; done
```

## 17.5 Hermeticity

Provider keys stay unset. A test that requires a network or a live provider is opt-in and is never
part of the default gate. A test suite that passes only with a key present is not hermetic and its
result is not admissible as evidence.

---

# 18. Release Qualification and CI

## 18.1 Gate ladder

| Gate | Requires |
|---|---|
| **G0 — Trust** | Phase 0 exit criteria; RF-C-01…RF-C-12 green |
| **G1 — Runtime truth** | Phase 1 exit; fresh-process replay parity |
| **G2 — Protocol** | Phase 2 exit; shared vectors in both languages |
| **G3 — Governance** | Phase 4 exit; every bundle signed + independently accepted |
| **G4 — M-7** | Phase 5 exit; ADR-0099 accepted |
| **G5 — M-8** | Phases 6–7 exit; 11 falsifiers green; independent review |
| **BETA** | G0–G5 and no known P0/P1 law/code/evidence contradiction |

## 18.2 CI additions to recommend

- Add `check_duplication.py --enforce`, `check_stale_paths.py`, `check_markdown_links.py`,
  and the new checks from §17.2 to the lint job.
- Add the evidence acceptance gate (§12.4).
- Add a qualified **Linux AF_UNIX** job — the UDS contract cannot be verified elsewhere, and this
  receipt is an outstanding external request on the active board.
- Add a clean-clone job that installs from declared dependencies only. This is what would surface
  the §10.1 `jsonschema` fail-open and the §11.1(a) manifest-resolution defect.
- Python type checking and formatting are currently declared but unenforced; enabling them is
  optional and independent of the gate ladder.

## 18.3 Release evidence bundle

Every gate produces a digest-addressed manifest containing: source commit, input manifest, protocol
version, environment identity, test commands, test outputs, artifact digests, event-store digest,
trajectory digest, reviewer identity, and acceptance decision.

**No milestone is closed from test counts, merge state, prose, or a producer envelope.**

---

# 19. Work Packages, Ownership and Sequencing

## 19.1 The authorization gap that must be closed first

`backlog.md` defines WP-A1…WP-B4 covering M-4 through M-8. **Nothing covers `runtime/service/`
(protocol, gateway, UDS, approvals) or the standalone CLI and installer.** That code shipped outside
the backlog — which is exactly why it accumulated P0 defects unreviewed.

Phases 0–3 therefore have **no authorizing package today**. Before that work begins, add:

| ID | Milestone | Scope | Owner |
|---|---|---|---|
| **WP-C1** | M-4 preservation | Trust and security repair: CLI key lifecycle, interactive approval, approval verification, gateway auth/CORS/size, UDS validation, canonical error codes | Dev B |
| **WP-C2** | M-2/M-4 preservation | Runtime truth: single canonical writer, unchanged envelopes, real checkpoint/resume/cancel, derived projections, capability truth | Dev B |
| **WP-C3** | M-4 preservation | Protocol convergence + distribution: schema authority, shared vectors, `jsonschema` runtime dep, CLI surface, installer | Dev A |
| **WP-G1** | Governance | Reviewer identity, `accept_evidence.py`, `check_evidence_acceptance.py`, prereg binding, runner model resolution, baseline succession | Leadership + Dev A |

Each must carry the full seven-concern contract used by WP-A1…WP-B4: objective/rationale;
surface/boundary; interface/I-O; algorithm/events; failure/security; observability/performance;
tests/falsifiers; evidence/migration/DoD.

## 19.2 Full package order

```
WP-G1 ──────────────────────────────┐  (start immediately; cheapest, unblocks 3 milestones)
WP-C1 ──► WP-C2 ──► WP-C3 ──────────┤
                                    ├──► WP-A3 (M-7 integrate) ──► WP-B3 (M7-01, ADR-0099)
WP-A1 ✔ (produced, needs acceptance)┤                                        │
WP-B1   (needs baseline)  ──────────┤                                        ▼
WP-B2 ✔ (produced, needs acceptance)┘                        WP-A4 (M-8 memory) ──► WP-B4 (M-8 learning)
                                                                             │
                                                                             ▼
                                                                  Independent M-8 acceptance
                                                                        = BETA MVP
```

## 19.3 Ownership discipline

- **Dev A** — client-core boundary contracts, M-7 topology consumption, ADR-0100 durable memory,
  protocol/distribution (WP-C3).
- **Dev B** — RuntimeService, stores, UDS, HTTP/SSE, protocol validation, evidence tooling,
  governed learning.
- **Leadership** — independent acceptance, baseline creation, ADR-0099 ratification, board updates.

No developer edits the other lane's owned files without explicit review. WIP=1 per developer. Shared
schema or runtime interfaces are frozen by ADR before use.

## 19.4 The producer/reviewer rule

**Leadership, not the producing developer, must:** independently review M-4, M-6, and M-6.5; issue
separate signed acceptance or negative envelopes; resolve WP-B1 evidence truthfully; create
`CONVERGENCE-BASE-v1` only after ADR-0102 prerequisites; verify the annotated tag remotely; and
update boards only from receipts.

---

# 20. Required Canonical Document Updates

> These are the **only** documents whose status content changes. Make these edits in
> `docs/03_execution/` — not in this file, not in a new file.

## 20.1 `sprint_active.md`

1. **Rewrite the "C1 exit state" section.** Line 102's "Developer-side work is complete on both
   lanes" is no longer true: C1's *authorized surface* is complete, but new **unauthorized** surface
   (`runtime/service/`, `cli.py`, `install_vanguard.sh`) arrived carrying P0 trust defects. Rewrite
   around current blockers; do not append another status section.
2. **Resolve the WP-B1 contradiction.** Line 33 says the WP-B1 bundle is absent and `IN_PROGRESS`;
   line 52 lists M-5b as `PACKAGE_READY` with `M-5b-graph-coloring.json`. One truth. Recommended
   reconciliation: keep `PACKAGE_READY` and annotate the bundle as *"admissible as regression
   evidence only; the gate cannot close without the successor baseline."*
3. **Downgrade M-4 and M-6 from `EVIDENCE_READY` to `PACKAGE_READY`.** Both bundles carry **no
   `signature` field**. Under ADR-0101 an unsigned bundle is not `EVIDENCE_READY`. (M-5b and M-6.5
   are signed and stay.)
4. **Add WP-C1, WP-C2, WP-C3, WP-G1** to the active package table with entry gates.
5. **Keep "No M-9/M-10 feature or scaffold" exactly as written.**
6. **Do not touch the frontmatter `version: "1.0.0"`.** It is the document revision, not the package
   version (`VISION.md:27-28`).

## 20.2 `backlog.md`

Add the four new work-package contract blocks (§19.1) in the existing seven-concern format, and add
their rows to the package dependency table.

## 20.3 `milestones.md`

**No change.** Its stable gate contracts for M-4 through M-8 and its M-9/M-10 boundary are correct
and were verified against the code. Two prior reviews attempted to rewrite this ladder; resist it.

## 20.4 `sprint_upcoming.md`

Insert WP-C1…WP-C3 and WP-G1 ahead of C2/C3. Note that WP-A3's entry gate now also requires WP-C2,
since topology execution rides the same runtime whose event truth WP-C2 repairs.

## 20.5 Descriptive drift (low priority, non-blocking)

| File | Line | Issue |
|---|---|---|
| `AGENTS.md` | 46 | "accepted ADRs indexed through `0097`" — actual is `0103` |
| `README.md` | 39, 92 | "through `0102`" — `0103` is accepted and present |
| `docs/02_decisions/INDEX.md` | 163-172 | Section table ends at `0102`; `0103` exists as a file and is cited at line 341 but has no table row |
| `schemas/v4/MANIFEST.md` | — | `runtime-service.schema.json` unlisted |
| `docs/04_architecture/overview.md` | ~76 | Stale synthetic-spawn / M-6.5 description |
| `vanguard/packages/runtime/service/contract.py` | 11-13 | Cites two nonexistent test files as proof of cross-language agreement |

`check_markdown_links.py` and `check_stale_paths.py` both pass, so these are semantic drift, not
broken links.

## 20.6 Archive hygiene

`TODO_PROMPT.md` and `TODO_SUGGESTIONS.md` are superseded by this file. Retain both as provenance;
mark them historical and non-authorizing. **Do not delete historical evidence until provenance has
been extracted and the retention decision is explicit.**

---

# 21. Consolidated TODO Table

Priority key: **P0** = blocks everything downstream; **P1** = blocks a milestone; **P2** = quality
and hygiene; **HOLD** = requires new authorization.

| # | Pri | Phase | Work | Where | Done when |
|---|---|---|---|---|---|
| 1 | **P0** | 0 | Remove hardcoded operator seed; per-install key at `0600` | `cli.py:87`, new `runtime/keys.py` | No seed literal in the distribution; two installs → two keys; `0644` key refused |
| 2 | **P0** | 0 | Replace auto-approver with TTY prompt; fail closed without TTY | `cli.py:114` | Unattended run cannot self-approve; no fact appended |
| 3 | **P0** | 0 | Delete four `dummy-sig-approved` defaults | `studio_gateway.py:309,328,339,350` | Missing signature → `invalid_request` |
| 4 | **P0** | 0 | Verify approvals via `ApprovalAuthority` against the pending challenge | `service.py:401` | Sig/key/expiry/args/descriptor all checked; zero field defaults |
| 5 | **P0** | 0 | HTTP auth + origin allowlist + 1 MiB cap + loopback default | `studio_gateway.py:57,108` | Unauthenticated → 401 with no state change; oversized → `frame_too_large` |
| 6 | **P0** | 0 | Validate `StreamEvents` before state access; remove `invalid_json` | `server.py:132,143` | All frames validated; only the ten canonical codes emitted |
| 7 | **P0** | 1 | One atomic canonical writer; inbox holds command idempotency only | `service.py:673` | Failed canonical append → no seq, no notification |
| 8 | **P0** | 1 | Persist canonical envelopes unchanged | `service.py:823,852` | Tenant/owner/project/lineage/causation/authority survive round-trip |
| 9 | **P0** | 1 | Real checkpoint / resume / cooperative cancel | `service.py:515,553` | Cold reconstruction; worker observes cancellation at a turn boundary |
| 10 | **P0** | 2 | `jsonschema` → runtime dependency; delete `_HAS_JSONSCHEMA` guard | `pyproject.toml:36`, `loader.py:16,138` | Manifest validation cannot be silently skipped |
| 11 | **P0** | 2 | Converge `vg.4`; add real shared vectors; fix the false docstring | `contract.py`, `schemas/v4/` | Zero drift; both languages consume one corpus |
| 12 | **P0** | — | Restore Groq `base_url` to `https://api.groq.com/openai/v1` | `providers/groq.py:37` | Provider reachable |
| 13 | **P0** | — | Restore Cloudflare `@cf/…` model IDs | `cloudflare.py`, `llm_switch.py:63-65` | No nonexistent CF model IDs |
| 14 | **P0** | — | Fix duplicate dict keys | `openrouter.py:27`, `002_LLM_API_MOCK/server.py:33` | AST duplicate-key scan clean |
| 15 | **P0** | — | Restore the disarmed falsifier fixture | `test_instrument_tuple.py:63` | Distinct fingerprint; negative case negative again |
| 16 | **P0** | 4 | Reviewer identity + `accept_evidence.py` + `check_evidence_acceptance.py` | `tools/runners/`, `tools/linters/` | Every bundle has an independent, digest-bound acceptance |
| 17 | **P1** | — | Update two stale pricing expectations | `test_model_routing.py:25`, `test_openrouter.py:339` | Suite green |
| 18 | **P1** | — | Audit the rest of the rename for collapsed negative fixtures | `tools/_adhoc/retire_openai_models.py` | No other disarmed falsifier |
| 19 | **P1** | — | Board truth: WP-B1, M-4/M-6 downgrade, C1-exit rewrite, add WP-C1…C3/G1 | `sprint_active.md`, `backlog.md` | Board self-consistent; repair work authorized |
| 20 | **P1** | 4 | Sign M-4/M-6 bundles; obtain independent receipts for M-4/M-6/M-6.5 | `docs/03_execution/evidence/` | Reviewer ≠ producer; `accepts()` returns true |
| 21 | **P1** | 4 | Thread `TaskContext.preregistration` in the RF-95 runner | `run_rf95_product_proof.py`, `run_swe_challenge.py` | Non-empty `preregistration_digest` in the trajectory |
| 22 | **P1** | 4 | Route all runners through `get_default_model()` | `run_m5b_formal_proof.py:163`, `run_swe_challenge.py:335` | No hardcoded model literal in an evidence runner |
| 23 | **P1** | 4 | Portable M-4 artifacts (no `/tmp` WAL references) | RF-95 runner | Reconstructable in a clean reviewer environment |
| 24 | **P1** | 4 | Create and remotely verify `CONVERGENCE-BASE-v1` | ADR-0102 | Annotated remote tag + signed baseline manifest + review |
| 25 | **P1** | 3 | Fix installed-package resource resolution | `cli.py:60` | `vanguard` works from site-packages |
| 26 | **P1** | 3 | `subprocess.run` list form; gate `.vanguard/` on `init`; scope `.env` | `cli.py:48,51-58,136` | No shell interpolation; no surprise directories; no global env writes |
| 27 | **P1** | 3 | Real installer: venv, pin, checksum, signature, uninstall; same interpreter | `install_vanguard.sh` | Reviewable and reversible; **publish only after 1–6** |
| 28 | **P1** | 3 | Gate or remove the `vanguard-studio` console script | `pyproject.toml:30-34` | Unauthenticated gateway is not an installed binary |
| 29 | **P1** | 5 | Bind `RunPlanExtensionRef` into `RunPlan` and `run_composed` | `run_plan.py`, `root.py`, `topology.py` | Three topologies execute through one public path |
| 30 | **P1** | 5 | Correlated monotonic telemetry with completeness accounting | `runtime/telemetry.py` | < 3% median overhead; never a budget dimension |
| 31 | **P1** | 5 | M7-01 measurement; ratify ADR-0099 | `lab/`, `docs/02_decisions/` | Bounded read concurrency **or** `SEQUENTIAL_CONFIRMED`, signed and reviewed |
| 32 | **P1** | 6 | Real `AuthorizedMemoryContext` + `MemoryAuthorizationPort` | `memory.py:27`, `ports/memory.py` | A non-empty string is not authority |
| 33 | **P1** | 6 | Durable memory: SQLite-WAL metadata + CAS blobs, four category ports | `adapters/stores/` | Blob-first writes; fresh-process recovery |
| 34 | **P1** | 6 | Authorization before ranking and before dereference; retrieval receipts | memory retrieval path | Ranker never observes an unauthorized candidate |
| 35 | **P1** | 6 | Revocation, isolation, retention, quarantine, legal hold, GC, restore | memory lifecycle | Falsifiers 1–5 green |
| 36 | **P1** | 7 | Generator/evaluator/promoter separation; no fail-open verification | `governance/learning.py:367` | Missing keys → refuse, never skip |
| 37 | **P1** | 7 | Sealed workloads + held-out lift + regression budgets | `lab/`, evaluation harness | Presence-only gains rejected |
| 38 | **P1** | 7 | Signed CAS promotion; runtime-visible; concurrent promoters conflict | promotion registry | Falsifier 8 green |
| 39 | **P1** | 7 | Behavioral rollback under injected regression | rollback driver | Prior behavior restored in a fresh process |
| 40 | **P2** | — | Agency "already-applied" vs "patch failed" detection | `episode/state.py:227`, `repair.py:122` | No re-proposal burn on an already-correct workspace |
| 41 | **P2** | 17 | Add the five AST linters from §17.2 | `tools/linters/` | Each encodes a defect this program shipped |
| 42 | **P2** | 18 | CI: qualified Linux AF_UNIX job + clean-clone install job | CI config | UDS receipt obtainable; fail-open deps surfaced |
| 43 | **P2** | — | Never default to `:memory:` in product paths | service/CLI wiring | Durable store failure is a startup error |
| 44 | **P2** | 20 | Descriptive drift: AGENTS `0103`, README `0103`, INDEX row, MANIFEST, overview | §20.5 | ADR references agree with `02_decisions/` |
| 45 | **P2** | 20 | Mark `TODO_PROMPT.md` / `TODO_SUGGESTIONS.md` historical | `docs/_archive/reviews/` | Provenance retained, authority disclaimed |
| 46 | **HOLD** | 16 | M-9 v1.0 integration and transfer release | — | **After** independent M-8 acceptance **and** a new authorization |
| 47 | **HOLD** | 16 | M-10 causal self-model / architecture evolution research | — | Post-1.0; admitted only on measured superiority |

## 21.1 Rejected — do not re-propose

| Proposal | Why it is rejected |
|---|---|
| Scaffold `ports/distributed.py` / `ports/promotion.py` for M-9/M-10 | Prohibited by `sprint_active.md:141`; the needed seams already exist (§16.2) |
| Publish `curl … \| bash` | Would distribute a shared private key while items 1–6 are open |
| "20-tier SWE-bench Pro qualification" as the v1.0.0 gate | Invented; exists in no canonical document |
| Change execution-doc frontmatter `version` to `0.7.3.dev0` | Contradicts `VISION.md:27-28` — that field versions the document |
| "TCB over budget at 1,747 physical LOC" | Budget is logical LOC; `check_tcb_budget.py` passes |
| Invent an ADR-0099 file now | `INDEX.md:165` reserves it until M7-01 evidence exists |
| Rewrite `milestones.md` | Its stable contracts are correct and verified |
| Milestone maturity percentages | Unmeasured; the exact failure mode that rated a broken trust spine as complete |

---

# 22. Final Briefing

## 22.1 What is true

AETHER's foundation is genuinely strong and should be **repaired, not rewritten**. The hexagonal
lattice holds under static analysis; the kernel is domain-blind and under its logical-LOC budget;
the event store is durable with fresh-process continuation; the evaluator is exterior and signs its
verdicts; the sandbox is rootless; recursion (M-6) is real, with synthetic success structurally
removed at three independent layers; the M-6.5 paired-study instrument is signed and materially
rich; `topology.py` is well-built, authority-free work. All eight architectural linters pass and
1,992 of 1,995 tests pass. The active board is unusually honest about M-7 and M-8 — it is not lying
to you about the large things.

## 22.2 What is broken

Four blocking classes, in the order they must be addressed.

**Trust.** The newest code in the repository — the standalone CLI — embeds a literal Ed25519
operator seed and auto-approves every governance challenge, while the HTTP gateway fabricates
approval signatures at four call sites and `ResolveApproval` verifies nothing at all. Together these
nullify invariant **I-5** and the M-1 trust spine on every non-test path. Nothing in this repository
may be called a beta, and the installer must not be published, until this is fixed. It is roughly a
day of local edits.

**Runtime truth.** `RuntimeService` maintains two competing event stores, discards the canonical
append result before notifying subscribers, and lossily rebuilds canonical `mhf.event/2` envelopes
with substituted tenant, owner, trace, and role fields — flattening project identity, parent
lineage, causation, and authority provenance on the way to storage. Checkpoint persists no
reconstructable state, resume flips a status row without cold-reconstructing, and cancellation sets
a flag the worker never reads. This regresses the M-2 single-writer anchor and puts I-4 and I-9 at
risk.

**Governance.** `accepts()` correctly refuses self-acceptance, but no reviewer identity, acceptance
tool, or acceptance linter exists anywhere in the tree. Four producer bundles sit on disk with zero
acceptance envelopes, and two of them — M-4 and M-6 — carry **no producer signature at all** while
the board records them as `EVIDENCE_READY`. This single gap blocks M-4, M-6, and M-6.5, and
therefore M-7 and M-8 behind them. It is also the cheapest thing on the list to fix, which is why it
starts on day one alongside the security work.

**Implementation debt.** M-7's topology library has zero call sites in the public runtime — verified
by direct search across `root.py`, `run_plan.py`, `compose.py`, and `session.py`. M-8's memory
authorization is `bool(non_empty_string)`, the precise falsifier ADR-0100 was written to reject, and
its promotion registry skips signature verification entirely when no keys are configured. These two
are weeks of genuine engineering, not packaging.

## 22.3 What this guide adds beyond diagnosis

Chapters 5–7 fix the architectural vocabulary — lattice position, canonical chain, axioms,
invariants, protocol contracts — so every phase can state where its code lives and which invariant
it restores. Chapter 6 encodes four anti-patterns actually found in this tree (truthiness as
authority, absent-verifier-means-skip, defaulted security field, optional dependency gating a
mandatory check) as review rules, plus a refactoring standard derived from the rename that corrupted
a Groq API path segment, two Cloudflare model IDs, two pricing tables, and one falsifier's
discriminating power. Chapters 8–15 give interface contracts, pseudocode, and named falsifiers for
every phase. Chapter 17 proposes five AST linters, each encoding a defect this program shipped —
because eight architectural linters passing while I-5 is broken is a coverage gap with a concrete
remedy. Chapter 19 closes the authorization gap: the service and CLI code that Phases 0–3 repair has
**no work package today**, which is precisely why it accumulated P0 defects unreviewed, and WP-C1
through WP-C3 plus WP-G1 must be added to `backlog.md` and `sprint_active.md` before that work
begins.

## 22.4 What is deliberately not here

No completion percentages, because a prior review rated a subsystem "75% complete" whose
authorization function is a string-emptiness check. No time estimates, because sequencing is an
engineering fact and duration is a leadership decision. No frontend scope. No M-9/M-10 design — the
seams those milestones need already exist as artifacts of doing M-7 and M-8 correctly, and creating
new port files now is both prohibited by the active board and unnecessary. And no authority: this
file instructs, and `sprint_active.md` authorizes.

## 22.5 The path

Repair trust, then runtime truth, then protocol and distribution, with evidence governance running
concurrently from day one because it is cheap and unblocks three milestones at once. Then integrate
M-7 through the one public runtime, measure independence, and record ADR-0099 with an explicit
disposition — the milestone may close as `SEQUENTIAL_CONFIRMED`, but it may not close without the
decision. Then implement M-8 in two halves: durable authorized memory where authorization precedes
ranking and dereference, and governed learning where generator, evaluator, and promoter are
structurally separate and rollback is proven **behaviorally** in a fresh process, not by moving a
pointer.

**Independent acceptance of M-8 is the beta MVP boundary. v1.0.0 belongs to M-9 and requires a new
authorization that does not exist yet. M-9 and M-10 stay entirely on hold.**

Nothing found in this review requires an architectural rewrite. The substrate is sound; what is
missing is fail-closure in the newest code, one truth in the event ledger, a reviewer with a key,
and two milestones of honest engineering.

---

*End of guide. This document authorizes nothing. Work is authorized only by
[`docs/03_execution/sprint_active.md`](../../03_execution/sprint_active.md).*


# Final Task 

### The Final Step to Fully Close M-8: Fix the 3 Remaining Security Edge Cases

  Dev A and Dev B have delivered the entire turn-loop integration, clock verification, and 585 runtime tests are passing. To close M-8 with 100%
  mathematical rigor, only 3 specific security checks remain:

    flowchart TD
        S1["1. Remove recall() fail-open disjunct in runtime/memory.py (Dev A)"] --> G["2. Run 585+ Tests & 8 Linters"]
        S2["2. Enforce Generator ≠ Evaluator ≠ Promoter in learning.py (Dev B)"] --> G
        S3["3. Require signed PromotionEvidence on rollback (Dev B)"] --> G
        G --> EV["3. Run Evidence Bundles & Countersign"]
        EV --> MVP["4. Declare M-8 BETA MVP ACCEPTED"]
        MVP --> M9["5. Open M-9/M-10 Post-MVP Horizon"]
  ──────
  ### Prompt for Dev A & Dev B (The Final 15-Minute Sweep)

    # ROLE: Dev A & Dev B — Close Final M-8 Security Edge Cases

    ### 1. Dev A — Fix Memory Retrieval Fail-Open Disjunct
    - In memory.py:
      - Remove `or (access.grant_ref and access.tenant and access.project and not access.revoked)`.
      - Enforce that `recall()`, `write()`, and `invalidate()` require `access.permitted()` to be strictly `True`.
      - Extend `test_fake_nonempty_grant_fails_closed` in test_m8_memory_falsifiers.py to assert `recall()` fails closed.

    ### 2. Dev B — Enforce Role Separation & Signed Rollback
    - In learning.py:
      - In `promote()`, enforce `candidate.generator_id != report.evaluator_id != evidence.promoter_id` (raise `PermissionError` on collision).
  Add a test asserting collision refusal.
      - In `restore()` / `rollback()`, require a valid, signed `PromotionEvidence` parameter verified against `ApprovalAuthority`. Unsigned
  rollback must fail closed.

    ### 3. Verify Complete Green Gate
    ```bash
    python3 -m unittest discover -s test/runtime -v
    python3 -m unittest discover -s test/security -v
    for l in check_boundaries check_tcb_budget scan_secrets check_domain_blindness \
             check_isolation_policy check_execution_truth check_markdown_links check_stale_paths; do
        python3 tools/linters/$l.py || exit 1
    done


    Once this sweep completes, **all M-8 security properties and invariants are 100% closed**, and we can transition to independent evidence
  signing and the post-MVP roadmap!