---
adr: 0085
title: "Reversibility radius: decide shape now, defer implementation, reserve the field"
status: accepted
accepted_date: 2026-08-21
amended_date: 2026-08-21
supersedes: none
extends: ADR-0000, ADR-0005, ADR-0023, ADR-0071, ADR-0074, ADR-M0-05, ADR-M0-13
---

# ADR-0085: Reversibility radius — decide shape now, defer implementation, reserve the field

> **Numbering note.** `0077`–`0084` are reserved for the v0.6.1 Substrate Correction Lock
> (drafted, not yet filed). This ADR takes `0085` to avoid collision. It governs *how* those and
> every successor ADR are decided; it does not amend them.

---

**Decision.** Five rules govern every proposed capability, for the life of the programme.

1. **Classify by reversibility radius before estimating effort.** Every proposal is assigned a
   radius `R ∈ {0, 1, 2, 3}` (§1). The radius, not the excitement, determines whether the decision
   is made now.
2. **Radius 0 and 1 are decided now; radius 2 and 3 are not.** A radius-0 or radius-1 question left
   open is a debt that compounds with corpus size. A radius-2 or radius-3 question decided early is
   speculative design and is refused as over-engineering.
3. **Deciding is not building.** A radius-0/1 decision discharges through the **Reservation
   Protocol** (§3) — *parse, digest, refuse, falsify* — at a cost of approximately one schema line
   and one test. Implementation stays at its own milestone.
4. **A reserved field enters the identity digest.** A reservation that is parsed but not digested is
   not a reservation: the composition identity still moves when the capability activates, and the
   corpus is re-attributed. Digest inclusion is what buys forward compatibility (§3.2).
5. **A filed ADR with a bound falsifier and a reversal condition is closed.** It reopens on
   **evidence matching its own stated reversal condition**, never on preference, aesthetics,
   novelty, or a new proposal document. This rule is what terminates re-review (§6).

**Context.** The programme has repeatedly re-litigated the same architectural questions across
independent review passes because the questions were *described* rather than *decided*. The cost is
not the review time; it is that each pass arrives at a larger corpus, where the same decision is
more expensive to act on. Simultaneously, the corpus of governance prose has grown to exceed the
substrate it governs (`005` §W6), so the instinct to "write more of the plan down" makes the problem
worse rather than better. This ADR resolves both pressures with one mechanism: **the future is kept
open by the shape of identity and evidence, not by the volume of documentation.**

---

## 1. The reversibility radius

Define the **artifact dependency DAG** `G = (V, E)` where `V` is the set of durable artifacts —
schemas, digests, ledger rows, packs, manifests, generated types, published contracts — and an edge
`u → v` means `v`'s validity depends on `u`'s shape. For a proposed change `x`, the **blast radius**
is the transitive reachability set:

```
    R(x) = | Reach_G(x) |          artifacts that must be migrated, re-derived, or re-attributed
```

An artifact class `A` is **irreversible** when there exists no total recovery function
`f : State_t → A_{t-1}` — that is, when the information required to reconstruct it has been
destroyed rather than merely displaced.

| Radius | Name | Test | Disposition |
|---|---|---|---|
| **R0** | **Irreversible** | No recovery function exists. The information is destroyed, not displaced. | **Decide now. Reserve now.** Any non-zero probability of future need justifies the reservation (§2.2). |
| **R1** | **Corpus-wide** | Reversible, but `R(x)` grows monotonically with time — every row, trajectory, or attributed measurement added before the fix must be migrated or discarded. | **Decide now.** Implement at its milestone. |
| **R2** | **Pack-wide / contract-local** | `R(x)` is bounded by the number of packs or plugins, and does not grow with runtime. | **Decide at the milestone that needs it.** Do not pre-design. |
| **R3** | **Local** | `R(x) ≈ 1`. A module boundary absorbs the change. | **Do not decide.** Build when needed. Pre-deciding is speculative design. |

**Worked examples from this tree.**

- *Per-turn trajectory cost* is **R0**. The governor's settled cost ledger for a completed run is
  gone; no fold over surviving events reconstructs it. Every episode completing before the fix is a
  permanently degraded row.
- *The `D_H` pre-image* (what the manifest can express) is **R1**. Changing the manifest shape
  changes every composition digest, so every trajectory already emitted is attributed to a
  superseded shape. Cheap before the corpus is production; expensive after.
- *Whether a Pareto router exists* is **R2**. It is policy over data that already exists; it adds no
  edge to `G` if the telemetry fields are reserved.
- *Which embedding model backs semantic recall* is **R3**. It sits behind a negotiated
  `IMemoryEngine.capabilities()` and changes nothing outside its own plugin.

> **The discipline this table enforces:** effort estimates and enthusiasm are both uncorrelated with
> radius. A one-line schema field can be R0; a six-week subsystem can be R3. **Classify first.**

---

## 2. The mathematics of when to decide

### 2.1 The rework inequality

Let `t_d` be the decision time and `t_n` the time the capability is actually needed. Let `N(t)` be
the count of dependent artifacts at time `t` — corpus rows, packs, attributed measurements. Then:

```
    C_early(x)  =  c_reserve + c_test                        ≈ O(1),  time-invariant
    C_late(x)   =  R(x) · N(t_n) · c_migrate                  monotonically increasing in t_n
```

Decide now iff:

```
    c_reserve + c_test   <   P(needed) · R(x) · N(t_n) · c_migrate
```

Because the left side is constant and the right side grows with `N(t_n)`, **the inequality flips
exactly once and never flips back.** The only question is whether the flip has already happened.
For a substrate that emits a durable row per episode, `N` grows with usage, so the flip happens
early and silently.

### 2.2 The irreversible case

When `A` is irreversible, `c_migrate → ∞` because migration is not defined — the information does
not exist to migrate. The inequality reduces to:

```
    reserve  iff  P(needed) > 0
```

This is the formal statement of *"trajectories cannot be back-filled."* It is why R0 items are not
subject to cost-benefit argument: **any non-zero probability of future need dominates a constant
reservation cost.** Disputing an R0 reservation requires arguing `P = 0`, which is a much stronger
claim than "we probably won't need it."

### 2.3 Reservation as a real option

A reservation is a **real option** on a future capability. Its premium is `c_reserve + c_test`
(≈ one schema line, one test); its strike is the avoided migration `R(x) · N(t_n) · c_migrate`. The
option is *deep in the money whenever the underlying artifact is irreversible*, because the strike
is unbounded.

Two properties follow, and both are load-bearing:

- **Reservations are not free, so they are not unlimited.** Each one adds a field a reader must
  understand and a test CI must run. The premium is small but non-zero, which is precisely why §5
  is a *closed list* and not an open invitation.
- **The option value comes from the digest, not the field.** A field parsed but excluded from the
  identity pre-image provides no forward compatibility (§3.2). It is a premium paid for nothing.

### 2.4 Coupling cost

Let `κ(x)` be the number of new edges `x` introduces into the boundary lattice
`domain ← ports ← kernel ← agency ← runtime → adapters`. Then:

```
    κ(x) = 0    →  the change is additive.        Admissible at any milestone.
    κ(x) > 0    →  the change is architectural.   Requires an ADR regardless of its size.
```

This is the operational test for *"is this a feature or an architecture change?"* — a question that
otherwise collapses into taste. **A ten-thousand-line pack with `κ = 0` is a feature. A three-line
import with `κ = 1` is an architecture change.**

---

## 3. The Reservation Protocol

The discharge mechanism for every R0 and R1 decision. Four steps, in order.

### 3.1 Parse

The field exists in the schema and the parser accepts it. It is not a comment, not a TODO, and not a
sentence in a plan document. Comments are re-litigated; schemas are not.

### 3.2 Digest

**The reserved field enters the identity pre-image** (`D_H`, `D_R`, or the relevant content
address). This is the step that is routinely skipped and it is the step that does the work.

> **Why.** If `spawn_grant` is parsed at M-3 but excluded from `D_H`, then when the verb activates
> at M-6 the pre-image changes, every prior `D_H` becomes a different digest for the same
> composition, and every trajectory emitted between M-3 and M-6 is attributed to a shape that no
> longer exists. **Digest inclusion is what makes the corpus survive the activation.**

### 3.3 Refuse

The capability is **rejected at the boundary with a named reason** until its milestone opens.
`spawn_grant: true` returns *"`agent.spawn` not implemented before M-6"*.
`max_parallel_claims > 1` returns *"I-11: sequential until the M-7 measurement gate."*

Refusal must be at the **outermost boundary that can see the request** — compose time, not runtime
— so the failure is a composition error, never a partial execution (`ADR-0005`).

### 3.4 Falsify

A test asserts the inert state. `test_spawn_grant_true_is_rejected_before_M6`.
`test_max_parallel_claims_above_one_fails_at_compose`.

**This is what closes the question.** Per `ADR-0074`, a concept without a bound falsifier is not
locked. A reservation without an inert-state test is an intention, and intentions are re-argued.

### 3.5 The stopping rule

> **Parse, digest, refuse, falsify — then stop.**

Do **not** additionally write: task-level plans for the deferred milestone, a design document for the
unbuilt capability, a prototype, a feature flag with a live code path, or a placeholder module. Those
are the over-engineering the radius classification exists to prevent. The reservation *is* the
forward compatibility. Anything beyond it is speculative construction.

---

## 4. Applying the radius per engineering aspect

### 4.1 Features

A feature proposal is admissible only with a stated radius and `κ`. Features with `κ = 0` and
`R ≤ 2` require no ADR — they enter as *plugin + manifest + policy + composition*, which is the
growth rule already locked. **A feature that cannot enter that way is not a feature; it is an
architecture change wearing a feature's name**, and it requires an ADR before an estimate.

### 4.2 Architecture

Architecture changes are exactly those with `κ > 0` or `R ∈ {0, 1}`. They are batched into lock
waves rather than trickled, because each one re-attributes the corpus and the re-attribution cost is
paid once per wave, not once per change. **This is why v0.6.1 files eight ADRs at once rather than
eight ADRs over eight sprints.**

### 4.3 Performance

Performance decisions are **measure-gated without exception**: no optimisation before a named
measurement, and no measurement without a reserved telemetry field. Note the asymmetry — the
*optimisation* is R3 (local, deferrable), but the *telemetry field that makes it measurable* is R0
(the observation is destroyed if not captured at the time).

> **Rule: reserve the measurement, defer the optimisation.** The common failure is the reverse —
> optimising against an unmeasured baseline, then discovering the baseline cannot be reconstructed.

A latency, throughput, or cost claim without a paired measurement against a preserved baseline is
**not a result** and may not appear in normative text.

### 4.4 Relations and coupling

The boundary lattice is the coupling ledger. `κ(x) > 0` demands an ADR, and the ADR must state which
edge is added and why no existing edge suffices. Duplication is preferred to a new edge until the
duplication is measured — a second copy is R3; a new dependency edge is at least R2 and frequently
R1.

### 4.5 Risk

`ADR-M0-05` holds the standing risk register. This ADR adds the classification rule: **a risk whose
realisation would destroy information is R0 and is mitigated by reservation, not by monitoring.** A
risk whose realisation is merely expensive is R1–R3 and may be monitored. Monitoring an
irreversible risk is not a mitigation; it is a record of the loss.

### 4.6 Rework

Rework is not a failure mode to be eliminated — it is the *expected cost of a correctly deferred
decision*. The failure mode is **unbudgeted** rework: rework whose radius was never estimated. Every
deferral in this programme states the radius it accepts. A deferral without a stated radius is not a
deferral; it is an omission.

---

## 5. The closed reservation list

The following are reserved under §3 for the current programme. **This list is closed.** Additions
require an ADR citing this one, and the burden is to show `R ≤ 1` and `P(needed) > 0`.

### 5.1 Composition (`mhf.manifest/2`, M-3)

| Reserved | Radius | Inert until | Refusal |
|---|---|---|---|
| `components` + **`bindings`** (typed edges) | R1 | active at M-3 | — |
| `profiles` (execution profiles) | R1 | router active M-7 | recorded and honoured sequentially |
| `spawn_grant` per component | R1 | M-6 | `true` rejected at compose |
| `guardrails` + `absence_reason` | R1 | active at M-3 | absence without reason rejected |
| per-component `isolation` tier | R2 | active at M-3 | — |
| `max_parallel_claims` | R1 | M-7 | `> 1` rejected while I-11 stands |

### 5.2 Evidence (`mhf.trajectory/1`, M-2)

| Reserved | Radius | Status |
|---|---|---|
| per-turn `cost` (tokens, millis), model fingerprint | **R0** | **required at M-2** |
| `execution_digest` (`D_R`) | **R0** | **required at M-2** |
| `measurement_status` + reason | **R0** | **required at M-2** — *unknown is never a fabricated zero* |
| `verdict_absent_reason` | R0 | required whenever `verdict` is null |
| `profile_used`, `escalations[]` | R1 | optional M-2, required M-3 |
| `memo_hit`, `memo_source_episode_id` | R1 | reserved, inert until M-5 |
| `attribution.prefix_hits` | R1 | optional until M-10 — requiring it earlier manufactures a false green |

### 5.3 Event catalog

| Reserved | Radius | Disposition |
|---|---|---|
| `PluginDiscovered`, `PluginVerified` | R1 | **added at M-3.** Without them, two of seven lifecycle transitions are unledgered and the M-3 gate is unsatisfiable. |
| `ChildSpawned`, `ChildReturned` | — | **already present.** No reservation needed. |
| Work-protocol kinds (`WorkPublished`, `WorkClaimed`, …) | R1 | **named in the ADR as reserved placeholders; NOT added to the catalog** until M-7. Naming is the reservation; catalog entry is the implementation. |

### 5.4 Decisions filed ahead of implementation

ADRs may be filed with status **`accepted, implementation deferred`**. This is the reservation
mechanism at the decision layer: the shape is closed, the falsifier is written red, the code waits.

---

## 6. Termination of re-review

The re-review loop has a single cause: **open questions accumulate reviewers.** Its cure is
structural, not procedural.

```
    OPEN     described in a plan, a proposal, or a comment       →  re-argued each pass, at full cost
    CLOSED   filed ADR + bound falsifier + reversal condition    →  reopens only on matching evidence
```

**Consequences, binding:**

1. A new proposal document **may not reopen** a closed ADR. It may only present evidence matching
   that ADR's stated reversal condition. A proposal that re-argues a closed decision is returned
   without adjudication.
2. **No ticket may cite `docs/07_reviews/` or `docs/06_references/` as a requirement.** If a
   developer needs something not present in an ADR, a schema, or a falsifier, that is the signal a
   decision has *not* been made — it escalates rather than getting improvised into the code.
3. **Length is not evidence.** A twenty-thousand-word proposal and a forty-line ADR have equal
   authority, which is none until filed and total once filed. The programme has repeatedly mistaken
   comprehensiveness for bindingness.
4. **Convergent proposals are not corroboration.** Six documents agreeing is not verification when
   they share a source. Only re-execution against the tree is verification. *(Observed: four
   independent passes propagated the same conflated free-energy formulation, three propagated a
   stale file count, and one propagated findings from a superseded HEAD.)*

---

## 7. Proposal admission checklist

Every capability proposal answers all eight before an estimate is given. Unanswered means
unadmitted.

1. **Radius `R`?** With the reachability set named, not asserted.
2. **Is it irreversible?** Name the information destroyed and why no recovery function exists.
3. **`κ`?** Which lattice edges are added? If `κ > 0`, this is architecture and needs an ADR.
4. **Does it move an identity pre-image?** `D_H`, `D_R`, `D_X`, or a content address.
5. **Reserve or build?** If reserve: the four Protocol steps, named.
6. **Bound falsifier?** One named test function. Not a description.
7. **Reversal condition?** The evidence that would undo this. If none exists, it is not falsifiable
   and cannot be filed.
8. **What does it forbid?** Every decision closes options; naming them prevents the next reviewer
   rediscovering the tradeoff as a defect.

---

## 8. Precedents

Stated as engineering lineage, not authority. Each is adopted for a specific mechanism, not adopted
wholesale.

| Source | Mechanism adopted | Bound / refusal |
|---|---|---|
| **Parnas**, *On the Criteria To Be Used in Decomposing Systems into Modules* (1972) | Modules encapsulate **likely changes**; the radius classification is that criterion made quantitative. | Information hiding does not license a new lattice edge. |
| **Dixit & Pindyck**, *Investment Under Uncertainty* (1994) | Real-option value of delay under irreversibility; §2.3's premium/strike framing. | Financial option pricing is **not** imported. No formula is claimed. |
| **Protobuf / Avro** reserved fields and forward-compatible schema evolution | §3's parse-and-reserve mechanism; the direct industrial precedent. | Their tolerance of unknown fields is **refused** — AETHER schemas are `additionalProperties: false` and unknown fields fail at compose (`ADR-0032`). |
| **Merkle DAG / content addressing** | §3.2 — identity is the digest of the pre-image, so the pre-image is the compatibility surface. | Bytes come from JCS (RFC 8785) only (`ADR-0009`). |
| **Popper**, falsifiability as demarcation | §3.4 and `ADR-0074` — a claim without a refutation condition is not a decision. | Not a claim about science; a rule about which documents bind. |
| **Design-of-experiments**, paired comparison and Mill's Canon of Difference | §4.3 — a performance claim requires a paired measurement against a preserved baseline. | Exact tests over approximations, per `docs/04_annex/MEASUREMENT.md` M-03. |
| **Reference-monitor tradition** (Anderson 1972; capability systems) | The invariant that no belief, price, rating, cache, or posterior may widen authority (§4.5). | Authority is mediated at S0–S12 only; no second authorization path, however advisory. |

---

## 9. The self-test

This ADR is subject to its own rules and is admissible only if it passes them.

| Rule | Applied to this ADR |
|---|---|
| Radius | **R1** — it governs the pre-image of every future decision; deciding it late means re-adjudicating every reservation already made. |
| `κ` | **0** — it adds no lattice edge and no runtime artifact. |
| Reserve or build | **Filed, not built.** It introduces no code and no schema. |
| Falsifiable | Yes — §10. |
| Stopping rule | It names a **closed** reservation list (§5) and forbids task-level planning for deferred milestones (§3.5). |
| Length | Justified only because it **terminates recurring argument**. It survives the M-5 collapse because ADRs are a surviving tier; it adds no eighth authority tier. If it is ever cited as a *plan* rather than a *rule*, it has failed. |

---

## 10. Bound falsifiers

| ID | Falsifier | What it kills |
|---|---|---|
| `RF-73` | `test_every_reserved_field_is_in_the_identity_preimage` — enumerate reserved fields from §5, assert each participates in `D_H`/`D_R` | A reservation that is parsed but not digested (§3.2) — the failure that silently re-attributes the corpus |
| `RF-74` | `test_every_inert_reservation_is_refused_at_compose` — each §5 row with an inert-until milestone is rejected at compose with a named reason | A reservation with a live code path |
| `RF-75` | `tools/linters/check_adr_reversal_conditions.py` — every ADR under `docs/05_adr/` states a reversal condition | An ADR that cannot be closed, and therefore cannot stop being re-argued |

---

**Reversal condition.** Evidence that the radius classification produced a **materially wrong**
disposition twice — specifically, an R3 item that later required a corpus migration, or an R0 item
whose reservation was never activated and whose premium measurably slowed delivery. One
misclassification is an estimation error and is corrected in place; two is a defect in the criterion
and reopens §1. Additionally, if the reserved-field count in §5 exceeds twenty without a
corresponding activation, the option premium has stopped being `O(1)` and §5's closure must be
re-adjudicated.

---

## Amendment — 2026-08-21: ratified-catalog and selector correction

The numbering note above is historical: ADRs 0077–0084 were filed and ratified on 2026-08-21.
ADR-0077's same-day amendment narrows §3.2–§3.4 and the §5.1 `spawn_grant` example as follows:

- the reservation is an `agent.spawn` capability declaration using the canonical generic selector
  `agent://spawn/harness/<D_H>`, not a boolean;
- absence means deny;
- before M-6, presence is parsed, included in `D_H`, and refused at compose with the named reason
  `agent.spawn not implemented before M-6`;
- RF-73 and RF-74 apply to this selector-shaped reservation.

Every occurrence of `spawn_grant: true` in the original explanatory text is therefore superseded
by this narrower selector form. This correction changes no implementation milestone and authorizes
no graph or spawn code.

**Owner · status.** Principal Systems Architect · accepted
