---
id: VG-08
file: 08_vanguard_phase_0_build_plan_v040.md
title: "Vanguard v4.0 — Phase 0 Build Plan"
version: 4.0.0
status: DISPOSABLE — retired when Phase 0 closes
authority_scope: >
  Phase 0 scope and its non-negotiable exclusions; the three increments;
  falsifiable phase hypotheses; the ticket set and exit tests; the must-fail
  suite and the rule-to-test map; CI gates; the exit criterion.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 3000
owners: [Tech Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Phase 0 Build Plan

> `02`–`07` are the design. **This turns them into commits.**
>
> This document is **disposable**. It is retired when Phase 0 closes, and any contract that must outlive it has already moved to a normative owner (`00 [AR-7]`). Do not maintain it past its purpose.

---

## 0. Scope

**In:** wire schemas and conformance; controller with broker; the episode reducer; budgets and leases; capability grants; the transactional event store with line-delimited export; the blob store; a fake model and one real provider; the Git environment; **TableWorld**; minimal tools and operators; a separately-identified evaluator; `vg run` and `vg trace`; a rootless worker perimeter with containment reporting; crash recovery; basic redaction; and CI carrying boundary, property, conformance and must-fail tests.

**Out, and not renegotiable mid-phase:** canvas or any GUI; protocol integrations and browser; semantic memory; automatic competence promotion; general subagents; search, process rewards or training; public benchmarks; an autonomous updater; a systems-language index; measurement and the A/A floor.

> **The failure this list prevents:** Phase 0 quietly becoming Phase 0–2, taking four months, and never being dogfooded. If something in the right-hand column seems necessary to make Phase 0 work, **that is evidence the loop is wrong, not that the scope is wrong.**

**Measurement is deliberately absent.** There is no floor yet (`07 §5.4`), and a resolve-rate number produced in Phase 0 would be exactly the premature-measurement error this programme exists to avoid.

---

## 1. Hypotheses

Phase 0 is an experiment before it is a build. Each hypothesis names what falsifies it, and a falsified hypothesis is a **finding**, not a failure.

| # | Hypothesis | Falsified by |
|---|---|---|
| H0 | One episode engine serves coding and TableWorld | Any environment-specific change to the core |
| H1 | All external authority derives from a scoped capability | Any effect without a valid grant |
| H2 | A compromised worker cannot reach the control or evidence planes | Any read, write, secret or egress escape in the red-team suite |
| H3 | Events permit recovery without inventing certainty | An in-flight effect that cannot be reconciled being marked as definitely succeeded or failed |
| H4 | The Coding Cell closes the feedback loop on real work | Inability to fix simple and multi-file bugs without manual intervention |
| H5 | The store supports operational replay | Reduced state diverging from stored events |

---

## 2. Three increments

**Increment A — Trust Spine.** Runs a deterministic script with **no model at all** and proves: denial by resource scope; child attenuation; budget enforcement; event atomicity; recovery from a kill; evaluator isolation; secret non-disclosure; redaction. *Building the trust spine before the model is what stops the model's plausibility from masking a broken boundary.*

**Increment B — Coding Cell.** Adds a provider, minimal operators and the Git environment. Must resolve: a single-file bug; a multi-file bug; a bug requiring a test to be run and reacted to; a bug creating a new file; and one task where the correct outcome is **abstention or escalation**.

**Increment C — Generality Witness.** Adds TableWorld **through registries, configuration and adapters only**. Must resolve: a constrained reconciliation; a derived transformation; an inconsistency detection ending in abstention; and a local compensation.

> If Increment C requires touching the episode engine, the capability algebra or the event envelope, **H0 is falsified** — early, cheaply, and therefore usefully. That is why TableWorld ships in Phase 0 rather than Phase 2.

---

## 3. Tickets

Ordered. Each names owned files, a dependency and one exit test. Do not start a ticket whose dependency is unmerged. **Estimates are deliberately absent** — track completion, not velocity.

| # | Ticket | Depends | Exit test |
|---|---|---|---|
| `TK-00` | Repo, tooling, CI, dependency boundaries, ADR-0000…0012 | — | A deliberately cyclic import fails the boundary gate |
| `TK-01` | Wire schemas, canonicalisation, vectors, **TypeScript + Python conformance**, generated reader profiles | TK-00 | **`SC-7` and `SC-12` both closed** — see §3.1 |
| `TK-02` | Identifiers, resources, principals, capability grants, attenuation | TK-01 | Scope escalation denied and emitted as an alertable event |
| `TK-03` | Budget ledger and lease tree | TK-01 | An overrun is debited negative and moves the ceiling; a child cannot exceed the parent's remainder |
| `TK-04` | Event store, reducer, replay | TK-01 | Replay reproduces an identical state digest |
| `TK-05` | Recovery controller | TK-04 | A killed worker yields a terminal record written from outside it, with undeterminable effects marked undeterminable |
| `TK-06` | **Broker, policy, dispatch** | TK-02, TK-03 | Fault injection covering every path in `05 §2.3`; no adapter executes without a grant |
| `TK-07` | Secret references and data policy | TK-02 | No secret value appears in any prompt, event, export or diagnostic stream |
| `TK-08` | Worker perimeter and containment report | TK-06 | Mount, egress and syscall probes recorded; an unverified perimeter blocks publication |
| `TK-09` | Evaluator under a separate identity | TK-06 | A candidate can neither read nor write the evaluator bundle |
| `TK-10` | End-to-end episode on a fake model, then a real provider | TK-04, TK-06 | Proposal → grant → receipt → evaluation completes; a simulated rate limit becomes an instrument termination, never a task failure |
| `TK-11` | Git environment, coding operators, `vg trace` | TK-10 | A new file appears in preview and patch; export is complete, redacted and correlated |
| `TK-12` | TableWorld, its evaluator, and the Phase 0 review | TK-11 | Added with **zero** episode-engine changes; exit criteria signed |

**`TK-01` before everything.** The descriptor is the input to loop detection, policy caching and grant binding, and a defect there presents later as *"the agent got stuck"* rather than as a descriptor bug.

### 3.1 `TK-01` completion criteria — unambiguous

`TK-01` is the first development milestone and owns three deliverables. It is complete when **both** schema conventions close, and not before:

| Deliverable | Closes |
|---|---|
| A TypeScript validator generated from the schemas, agreeing with Python on every vector — valid, invalid, canonical, digest, round-trip and unknown-field families | `SC-7` |
| Canonicalisation triples (input, RFC 8785 form, digest) for every digest-carrying type | `SC-7` (`GV-2`) |
| A schema artifact for **every** type defined in `04`, not only those already drafted | `SC-12` |

> **Why `SC-12` is a completion criterion rather than a nicety.** `04` was frozen once while `effect-descriptor.schema.json` was still planned, and that absence is exactly what concealed the missing grant binding (`09 [ADR-0039]`). Cross-language agreement on the schemas that happen to exist is not coverage.

**No ticket beyond `TK-01` begins until both close.**

**`TK-06` is the ticket to slow down on.** It is the policy kernel. The fault-injection suite is most of its weight, and everything after it assumes it is correct.

---

## 4. CI gates

Every gate must be able to fail. **A gate never seen red is not a gate.**

| Gate | Checks |
|---|---|
| `typecheck`, `lint` | Strict mode; no casts on data crossing a process boundary; no direct system calls outside adapters |
| `boundaries` | The layer lattice of `03 §4` |
| `test-unit`, `test-property` | Algebraic laws: attenuation narrows, provenance never improves, descriptors stable |
| `test-vectors` | Cross-language conformance, both profiles |
| `test-must-fail` | §5, against the broken implementations in the tree |
| `test-fault-injection` | Every failure path in `05 §2.3` |
| `tcb-size` | Policy kernel within its declared ceiling |
| `schema-drift` | Generated artifacts match their source; reader profiles regenerate identically |
| `docs-audit` | `CI-1`…`CI-9` from `00 §9` |

`test-must-fail` runs each test against a deliberately broken implementation kept in `test/broken/`. **If a must-fail test passes against its broken counterpart, CI fails.** This is the mechanism that keeps controls from becoming inert, which is precisely how the prototype's controls died: documented, tested, and unable to fail.

---

## 5. The must-fail suite

Every row is a defect that shipped somewhere, passed review, and had a test that could not fail. The broken implementations live in the tree rather than in a comment.

| # | Broken implementation it must catch | Guards | Ticket |
|---|---|---|---|
| `MF-01` | Capability widening hardcoded to a constant | `05 [K-32]` | TK-06 |
| `MF-02` | Justifying spans reset each turn | `05 [K-33]` | TK-06 |
| `MF-03` | A grant issued with no resource scope | `05 [K-18]` | TK-02 |
| `MF-04` | A child scope broader than its parent | `05 [K-23]` | TK-02 |
| `MF-05` | An over-broad request silently narrowed | `05 [K-26]` | TK-02 |
| `MF-06` | Lease released only on the success path | `05 [K-06]` | TK-03 |
| `MF-07` | Refund clamped at zero | `05 [K-07]` | TK-03 |
| `MF-08` | Adapter resolution after lease acquisition | `05 [K-04]` | TK-06 |
| `MF-09` | A consumed grant replayed successfully | `05 [K-19]` | TK-06 |
| `MF-10` | A grant crossing a process boundary unauthenticated | `05 [K-20]` | TK-06 |
| `MF-11` | Worker reading a control-plane mount | `05 [K-35]` | TK-08 |
| `MF-12` | Egress outside the allowlist | `05 [K-36]` | TK-08 |
| `MF-13` | Containment inferred from configuration rather than probed | `05 [K-42]` | TK-08 |
| `MF-14` | A secret value reaching a prompt, event or diagnostic | `05 [K-22]` | TK-07 |
| `MF-15` | An evaluator bundle writable by the candidate | `06 §4.2` | TK-09 |
| `MF-16` | A shadowing file under an evaluator input path scoring as a pass | `06 §4.3` | TK-09 |
| `MF-17` | A provider error counted as a task failure | `06 [V-05]` | TK-10 |
| `MF-18` | A wrong-but-real answer excluded from the denominator | `06 [V-08]` | TK-10 |
| `MF-19` | A mixed batch reordered | `03 [CC-7]` | TK-06 |
| `MF-20` | A duplicate non-idempotent effect after retry | `05 [K-19]` | TK-06 |
| `MF-21` | A kill producing no recovery record | `03 §9` | TK-05 |
| `MF-22` | An undeterminable external effect resolved to success or failure | `05 [F-22]` | TK-05 |
| `MF-23` | Line-delimited JSON used as the primary store, truncated mid-commit | `04 [CT-42]` | TK-04 |
| `MF-24` | An untracked new file omitted from the patch | `03 §7.3` | TK-11 |
| `MF-25` | An integer above 2⁵³−1 corrupted on the wire | `04 §0.4` | TK-01 |
| `MF-26` | An unknown schema version accepted silently | `04 [CT-48]` | TK-01 |
| `MF-27` | A reader profile rejecting an unknown field | `04 [CT-44]` | TK-01 |
| `MF-28` | A descriptor including the provider-assigned call identifier | `04 [D-3]` | TK-01 |
| `MF-29` | An empty invalidation-conditions array accepted | `04 [INV-1]` | TK-01 |
| `MF-30` | TableWorld requiring a conditional in the core | `02 [C-10]` | TK-12 |
| `MF-31` | A grant issued without a descriptor digest | `04 [CT-51]` | TK-02 |
| `MF-32` | Selector inclusion approximating pattern containment instead of denying | `04 [CT-52]` | TK-02 |
| `MF-33` | A check timestamp written inside a content-addressed artifact | `04 [CT-53]` | TK-01 |
| `MF-34` | An artifact activated with only manual invalidation conditions | `04 [INV-2]` | TK-01 |
| `MF-35` | An evolution event forced to carry a synthetic run identifier | `04 §12.1` | TK-04 |
| `MF-36` | **A crash between dispatch and emit leaving no intent record** | `05 [K-47]` | TK-06 |
| `MF-37` | A conflict resolved as last-write-wins with no event | `03 [CC-6]` | TK-06 |

**Deferred, recorded so it is not lost:** memory-write gating and adversarial ablation at activation (`06 §3`) have no Phase 0 test, because memory is out of scope. They ship with the memory ticket in Phase 2.

### 5.1 The rule-to-test map

`00 [CI-9]` requires every normative rule to name a test or be marked untestable with justification. A hand-maintained map across roughly two hundred rules would rot within a month, so it is **generated**: a script extracts every rule ID from `02`–`07`, joins it against the `Guards` column above, and writes `docs/v4/rule-test-map.md`. CI fails on any rule with neither a test nor an untestable marker.

Three classes are marked **untestable, with justification**, and the justification is part of the artifact:

| Class | Why | Compensating assurance |
|---|---|---|
| Architectural prohibitions (`03 [LT-*]`) | Prove the absence of a path, not a behaviour | Static analysis, which is stronger than a runtime test |
| Statistical rules (`07 [M-*]`) | Hold over a family of experiments, not a single execution | Refusal behaviour is testable: a degenerate floor must be **refused**, and that test exists |
| Human-gated rules (`05 [SA-5]`) | Depend on an out-of-band approval | Tested by proving no autonomous code path exists |

Coverage is satisfied by **any** of five test families, not by must-fail tests alone: must-fail against a broken implementation; architecture test proving a path does not exist; property test over an algebraic law; cross-language conformance vector; fault injection over `05 §2.3`. Demanding must-fail coverage for every rule would produce ceremonial tests, which is the failure this map exists to prevent.

**The map starts red by construction, and that is the point.** Baseline at the opening of Phase 0: **203 normative rules · 28 tested · 42 untestable-with-justification · 133 uncovered.** The list is generated at `docs/v4/phase0-rule-backlog.md`, with an owner and target milestone per rule. The uncovered rules are the Phase 0 test backlog, and the number is the phase's most honest progress metric — more informative than tickets merged, because it counts what is *proven* rather than what is *written*.

`CI-9` is therefore a **Phase 0 exit gate**, not a documentation gate. It runs from `TK-00` and reports; it blocks at §6. Until it is green, **every rule in `02`–`07` is asserted and unproven** — a weaker position than those documents' tone implies, stated here rather than left as an impression.

---

## 6. Exit criterion

Phase 0 closes only when **all** of the following hold.

**Mechanical:**
- the five coding tasks and three TableWorld tasks ran with **no core change between environments**;
- no effect occurred without a valid capability;
- the red-team suite reached neither the control plane, nor the evaluator, nor secrets;
- kill and restart preserved the distinction between known and uncertain;
- replay reconstructs state;
- budgets and cancellation reach the subprocess tree;
- a full audit trace exists and the operational trace contains no known secret;
- provider errors did not contaminate task outcomes;
- every must-fail test fails against its broken counterpart;
- **`CI-9` is green**: every normative rule in `02`–`07` names a test or is marked untestable with justification;
- **an engineer who did not write the policy kernel can audit it and reproduce the suite**;
- every Phase 0 ADR remains accepted, or was explicitly reversed on evidence.

**Measurable dogfood.** Over a fourteen-day window, the team routes **at least 60% of eligible bug-fix work** through the Coding Cell, and every opt-out is logged with a reason. The threshold matters less than the logged reasons: *"I didn't trust it on this one"* is the most valuable output Phase 0 produces, and it is unavailable if usage is judged by impression.

**Judgement, retained deliberately.** Pick three real bugs in a repository someone knows well — not a benchmark, not a toy. At least one requires edits in more than one file; at least one requires running tests and reacting. Run each interactively and **do not fix things by hand mid-run**. Then answer honestly: *next time, would you reach for it?* If no, the loop is not done, and no amount of Phase 1 work fixes that.

**What does not close Phase 0:** all tickets merged; CI green; a demo that worked once; a number.

---

## 7. Early warnings

| Signal | What it means |
|---|---|
| Nobody has run it on a real bug by the halfway point | The single most reliable predictor of a Phase 0 that never closes |
| A must-fail test is hard to write | The control it guards is probably not implemented |
| The policy kernel is growing past its ceiling | Logic belonging in cognition has leaked into the TCB |
| Someone wants a "just this once" second dispatch path | `05 [AT-01]` is about to be violated. The answer is no |
| Scope creep toward memory or general subagents | §0. Write it down for Phase 2 and move on |
| Increment C needing a core change | H0 is falsified. Stop and record it — that is the finding the phase exists to produce |

**Weekly, thirty minutes, three questions:** what merged, what is blocked, and **has anything changed our mind about `02`–`07`?** The third matters most. Those documents make falsifiable claims, and Phase 0 is the first chance to falsify one.

---

*Phase 0 closes → the exit criteria are signed → this document is retired, not archived as a contract.*
