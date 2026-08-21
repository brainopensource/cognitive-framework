# 001 — ALFA Tier S+ Architecture Decision Briefing

## Final disposition of proposals 002–008

**Document class:** Engineering Director decision briefing  
**Status:** **SUBMITTED FOR DIRECTOR RATIFICATION — NOT NORMATIVE LAW**  
**Decision date:** 2026-08-21  
**Selected master baseline:** [`006_fi_review_full_gptsol_proposal.md`](006_fi_review_full_gptsol_proposal.md)  
**Controlling law until ratification:** [`docs/SPEC.md`](docs/SPEC.md), accepted ADRs [`0069–0076`](docs/05_adr/INDEX.md), and the [`active execution board`](docs/03_sprints/sprint_active.md)

> This briefing selects a direction; it does not itself authorize implementation, amend the specification, accept an ADR, move a milestone, or waive a stop line. Only an Engineering Director decision followed by the normal append-only ADR and documentation cascade can do that.

---

## 1. Final call

Adopt **006 Fi — AETHER Tier S+ Master Architecture** as the sole architectural baseline for the ALFA decision. Its **Verified Adaptive Obligation Harness (VAOH)** is the strongest synthesis because it binds the Pareto harness, stigmergic coordination, Active Inference, and macro-tool compilation to AETHER's existing Decision, State, and Evidence planes without creating a second runtime or enlarging the trusted core. It also states the decisive safety law: **state, price, belief, rating, cached success, or learned policy may narrow behavior or influence selection, but may never widen authority**.

The other reports remain valuable **non-normative suggestion and review inputs**, not competing specifications. Their strongest compatible contributions are incorporated below as bounded amendments to 006. Conflicting ADR numbering, fabricated-zero economics, path-bag-as-graph claims, fixed performance promises, self-scoring, or any architecture that bypasses the universal turn mechanism are rejected. There will be one accepted architecture, one ADR sequence, one execution board, and one production lattice.

### Decision hierarchy

| Order | Artifact | Final role |
|---:|---|---|
| 1 | [`docs/SPEC.md`](docs/SPEC.md), [`docs/04_annex/`](docs/04_annex/), accepted [`ADRs`](docs/05_adr/INDEX.md) | Controlling law and invariants. |
| 2 | [`docs/03_sprints/sprint_active.md`](docs/03_sprints/sprint_active.md) and [`milestones.md`](docs/02_roadmap/milestones.md) | Authorized execution scope and gates. |
| 3 | [`006_fi_review_full_gptsol_proposal.md`](006_fi_review_full_gptsol_proposal.md) | **Selected Tier S+ design baseline**, pending Director ratification and ADR filing. |
| 4 | Proposals [`002`](002_beta_review_full_gem_proposal.md), [`004`](004_delta_review_full_glm53_proposal.md), [`005`](005_epsilon_review_full_dsv4-proposal.md), [`007`](007_zeta_review_full_opus_proposal.md), and [`008`](008_alfa_review_full_grok_proposal.md) | Advisory source material only; no independent implementation authority. |
| 5 | This briefing | Records the recommended final disposition and asks for the Director's decision. |

---

## 2. Tier S+ architecture to ratify

The selected architecture is:

```text
goal + witness contract + 6D ceiling
                  |
                  v
Decision Plane: context bottleneck + Pareto/EFE policy + graph refinement
                  |
                  v
Authority: universal turn loop -> S0-S12 -> attenuated grant -> durable intent
                  |
                  v
State Plane: SQLite WAL -> typed obligations/claims -> artifacts -> provenance DAG
                  |
                  v
Evidence Plane: exterior checker (UID 10002) -> subject-bound signed verdict
                  |
                  v
Compounding: T0 witness memo -> T1 macro -> T2 skill/router -> T3 DPO/harness
```

The Compounding Plane is a deployment view of ordinary exterior clients and plugins, not a new authority plane. No optimizer, scheduler, learner, memory system, macro compiler, or swarm controller belongs in the kernel. No inner loop may perform an outer-loop transition: an episode may propose a candidate, but it may not certify or promote what it produced.

### Five binding pillars

| Pillar | Final decision |
|---|---|
| **1. Adaptive informational harness and stigmergy** | Use the SQLite WAL State Plane as the authoritative shared work surface. Agents pull versioned, lease-bound obligations; publish immutable artifact and witness references; and coordinate through attributed state. Peer RPC is not an authority channel. The defensible complexity claim is conditional `O(cN)` state operations when each of `N` agents performs at most `c` indexed operations per round—not a universal `O(N)` theorem. |
| **2. Dynamic Pareto controller** | Apply a lexicographic gate: authority/isolation/evidence/safety first; 6D reservation and dependency feasibility second; witness floor third; Pareto nondominance fourth; product preference last. `flash`, `balanced`, `certain`, `frontier`, and `adaptive` profiles are versioned policy priors, not kernel logic or latency guarantees. Every escalation requires a new authorized reservation. |
| **3. Active Inference and compounding** | Use VFE for belief fitting after attributed observations and EFE for choosing among already-feasible policies. Record predictions before execution so calibration is measurable. Compound in order: exact witness memoization, verified macro compilation, skill/router learning, then DPO/harness evolution. The `50k -> 500` token-collapse example is a benchmark hypothesis, never a release promise. |
| **4. Forensic substrate repair** | Close hollow trajectory economics; prove fresh-process cold continuation; compile an actual typed Named Component Graph with bindings; add ledger parity for `PluginDiscovered` and `PluginVerified`; compute and distinguish `D_R`, `D_H`, and `D_X`; use `RF-*` only for the proposal register; absorb every remaining `layer0/` owner and remove packaging references atomically with NOVA-4. |
| **5. Hard gates and invariants** | Preserve A-B-C-D separation, the clean hexagonal lattice, domain blindness, monotonic attenuation, exterior verdict authority, single-writer ordering, the kernel budget `<=1438` logical LOC, sequential execution through M-6, the nine-row single-run M-4 stop, and the M-5 Pack #2 zero-domain/kernel-diff proof. |

---

## 3. Bounded synthesis from the suggestion reports

006 remains the baseline. The following imports sharpen it without forking it:

| Source | Import into the final ALFA architecture | Condition or correction |
|---|---|---|
| [`002 Beta`](002_beta_review_full_gem_proposal.md) | User-facing execution profiles and the macro-tool cost-collapse thesis. | Profiles remain exterior policy. Token/latency bands and reduction percentages must be measured; `stigmergic_blackboard: bool` is not an architectural primitive. |
| [`004 Delta`](004_delta_review_full_glm53_proposal.md) | Harness-first literature discipline, topology-cost measurement, and an A/A floor before trusting A/B promotion. | Promotion uses exact paired McNemar, effect size, interval, and a stable pairing key—not an asymptotic chi-square shortcut. |
| [`005 Epsilon`](005_epsilon_review_full_dsv4-proposal.md) | A-B-C-D framing, absent-vs-forged reasoning, and the clear version ladder. | Do not fold `VERIFIED` into another lifecycle payload; every material FSM transition must be catalogued, emitted, and reduced. |
| [`007 Zeta`](007_zeta_review_full_opus_proposal.md) | Monotonic RF execution matrix, ADR reversal conditions, `D_R` gap, F-/RF- collision, third manifest composition surface, and the M-4 row-8 loophole. | The current component map is a named path bag, not a wired graph. Obligations extend the State Plane; they do not replace the universal loop. |
| [`008 Alfa proposal`](008_alfa_review_full_grok_proposal.md) | Derived unattributability, explicit missing-cost reasons, post-M-3 SPI migration detail, and removal of `layer0*` from packaging. | Prefer the lower-churn trajectory decision below. Stale filesystem findings must be reverified immediately before any deletion. |

### Final trajectory amendment to 006

Retain the existing wire identifier **`mhf.trajectory/1`** and strengthen its content contract rather than introducing a breaking `/2` identifier during M-2. A completed real turn must record model/provider/fingerprint or an explicit unavailable reason, prompt/completion/cache token accounting, charged latency, byte accounting, context identity, proposals, receipts, and effect lineage. Unknown cost is represented as unavailable with a reason—never as a fabricated zero. Historical or incomplete records receive a **derived reader-side `legacy_incomplete` classification**; the WAL is not rewritten and the flag is not author-writable. Promotion eligibility is derived from populated attributable evidence, never declared by YAML.

This is the only material amendment to 006's immediate data contract. It preserves its invariant while avoiding unnecessary schema-version churn before M-4.

---

## 4. Final implementation sequence

No step below begins merely because it appears here. Each step begins only when its predecessor gate is green and the Director has placed the work on the canonical board.

| Milestone | Final scope | Non-negotiable exit |
|---|---|---|
| **M-2 / v0.6.1** | Finish one-runtime convergence. Add NOVA-1 populated `mhf.trajectory/1` evidence and NOVA-2 suspend/restart/resume from SQLite WAL in a genuinely fresh process. | No fabricated zeros; incomplete evidence cannot promote; fresh-process continuation reconstructs the same authoritative state and effect intent. |
| **M-3 / v0.6.2** | Land `mhf.manifest/2` as a named typed graph with explicit bindings across all composition surfaces. Ledger `PluginDiscovered` and `PluginVerified`. Resolve RF naming. Finish runtime absorption and delete `layer0/`, its tests/shims, and packaging inclusion with NOVA-4 negatives. | One compiler to immutable `FrozenHarness`; unknown or mismatched binding fails closed; every lifecycle transition has event parity; no `layer0` import or packaged module remains. |
| **M-4 / v0.6.3** | Run Domain Pack #1 through the full real mechanism. | **Nine populated evidence rows from one uninterrupted, unstitched, zero-human-intervention run under one `run_id`.** No cassette substitute, copied verdict, or equivalent demo. Row 8 is schema-valid **and populated**. Stop here if any row fails. |
| **M-5 / v0.7.0** | Ship Pack #2: Math & Formal Deductive Verification. Add deterministic T0 witness memoization and collapse governance documents only after the foundation proof. | Zero diffs under `vanguard/packages/domain/` and `vanguard/packages/kernel/`; exterior formal witness; memo key binds obligation, inputs, environment, checker, toolchain, assurance, and policy version. |
| **M-6 / v0.8.0** | Implement capability-mediated `agent.spawn` through S0-S12 using the existing `EpisodeEngine.spawn()` semantics as oracle. | Denied without the action/grant; child authority is a strict subset; spawn and return are durably attributable; kernel remains within budget. |
| **M-7 / v0.9.0 foundation** | Add lease-bound obligation claims, controlled concurrency, and the exterior Pareto router. | NOVA-2 remains green under concurrency; selector-disjoint scheduling loses no events; contention, bytes, retries, model calls, and critical-path latency are separately measured. |
| **M-8 / v0.9.0 completion** | Expose declarative framework construction for debate, critic/revisor loops, tree search, and swarms. | Multiple topologies and packs run without engine, domain, or kernel changes. |
| **M-9 / v1.0.0 candidate** | Add hybrid retrieval, macro candidate compilation, adversarial replay, and scale measurement. | Every macro is an ordinary least-privilege plugin; capability ceiling is no wider than the inferred source hull intersected with pack and publisher ceilings; fallback and total cost are measured. |
| **M-10 / v1.0.0 promotion** | Enable calibrated Active-Inference routing, skill evolution, signed DPO harvesting, harness experiments, and reversible promotion. | Pareto-safe improvement; immutable signed preference pairs; A/A floor; exact paired McNemar plus effect size/interval; exterior evidence; human-controlled default-pointer change and tested rollback. |

### Foundation stop-line ruling

M-4 is sacred. Post-foundation intelligence work cannot be used to manufacture the evidence that authorizes post-foundation intelligence work. A red NOVA-2 prevents concurrency. A hollow trajectory prevents learning and promotion. A path bag prevents graph claims. A self-issued verdict prevents promotion. A Pack #2 requiring changes to `domain/` or `kernel/` fails the generality thesis.

---

## 5. Unbreakable implementation laws

1. **One mechanism:** all effects, including future delegation and macros, traverse the universal turn loop and S0-S12.
2. **Authority monotonicity:** state, price, confidence, ratings, cached success, or learned policy can never widen a capability.
3. **Feasibility before optimization:** no scalar score may compensate for failed safety, authority, isolation, evidence, witness, or reservation constraints.
4. **Exterior truth:** only the bound exterior evaluator may mint promotion-eligible verdicts; the evaluated agent cannot reach or impersonate it.
5. **Explicit missingness:** absent measurement is unavailable plus reason, never zero, success, or promotable evidence.
6. **Single writer:** plugins and workers propose typed events; they never append authoritative envelopes directly.
7. **Digest separation:** `D_H`, `D_R`, and `D_X` are computed, carried, and asserted distinct according to their subjects; correlation is not causation.
8. **State-mediated swarms:** direct agent messages, if retained, are untrusted derived observations and never grants, claims, verdicts, or promotion commands.
9. **Least-privilege macros:** compiled procedures receive an inferred narrow interface and ceiling; successful source runs do not transfer their authority or verdict to a new subject digest.
10. **Human-gated promotion:** an episode, model, router, or compiler may nominate but cannot move the production default pointer.
11. **TCB discipline:** no Pareto policy, graph search, memory learner, obligation scheduler, or macro compiler enters `kernel/`; total logical LOC remains `<=1438`.
12. **No silent compatibility:** legacy readers are explicit and sunset by gate; no second parser, selector algebra, runtime, event owner, or shadow corpus survives convergence.

---

## 6. ADR and execution disposition requested from the Director

Use the six draft decisions in [`006_fi`](006_fi_review_full_gptsol_proposal.md#4-proposed-append-only-adr-catalog) as the drafting baseline, preserving their 1-to-1 falsifiers and recording any rejection append-only:

| Proposed ADR | Decision subject | Required Director ruling |
|---|---|---|
| **ADR-0077** | Named Component Graph and `mhf.manifest/2`. | Accept, narrow, or reject for M-3. |
| **ADR-0078** | Required, declared-absent, and forged guardrail states. | Accept the trichotomy and derived promotion eligibility. |
| **ADR-0079** | Plugin lifecycle parity, runtime absorption, and Layer-0 retirement. | Accept full event parity and atomic NOVA-4 deletion gate. |
| **ADR-0080** | Universal turn mechanism, typed obligations, and deferred mediated delegation. | Accept mechanism claim; keep spawn at M-6 and obligation claims at M-7. |
| **ADR-0081** | Evidence-complete trajectories and cold continuation. | Accept with this briefing's non-breaking `mhf.trajectory/1` amendment; place NOVA-1/NOVA-2 on the authorized board. |
| **ADR-0082** | Foundation-to-meta-framework Pareto, compounding, and promotion protocol. | Accept only behind M-4/M-5 and human promotion authority. |

Before filing, the Director or ADR owner must verify that 0077 is still the next available append-only number and must use **one mapping only**. The conflicting number assignments inside advisory proposals must not propagate into `docs/05_adr/`.

### Director decision checklist

- [ ] Ratify [`006_fi_review_full_gptsol_proposal.md`](006_fi_review_full_gptsol_proposal.md) as the Tier S+ master baseline, subject to the bounded amendments in this briefing.
- [ ] Confirm that proposals 002, 004, 005, 007, and 008 are suggestion reports only and cannot independently direct implementation.
- [ ] Accept, narrow, or reject each proposed ADR-0077–0082; assign one owner and one bound falsifier per accepted decision.
- [ ] Place only currently authorized M-2/M-3 work onto the [`active board`](docs/03_sprints/sprint_active.md); retain the M-4 and M-5 gates unchanged.
- [ ] Confirm Pack #2 as **Math & Formal Deductive Verification**, not an orphaned existing adapter used as a substitute proof.
- [ ] Confirm the M-4 row-8 strengthening: trajectory evidence is schema-valid **and populated**.
- [ ] Decide whether a separate post-ratification **ALFA master document** is needed.

### Request concerning a new ALFA document

This briefing recommends **not** renaming, overwriting, or promoting [`008_alfa_review_full_grok_proposal.md`](008_alfa_review_full_grok_proposal.md) merely because it already carries the ALFA label. It remains a suggestion report. If the Engineering Director wants a single publication-grade ALFA architecture after adjudicating ADR-0077–0082, the Director should explicitly authorize a **new document** derived from 006 plus the amendments recorded here. That new document must:

1. be created only after the ADR dispositions are known;
2. identify its normative or advisory class in the header;
3. link to accepted ADRs rather than reproduce competing law;
4. contain no unresolved alternative numbering or proposal-vote language; and
5. leave all source proposal reports immutable as provenance.

If no additional narrative is needed, this briefing plus 006 and the accepted ADRs are sufficient; avoid creating a fourth documentation authority layer.

---

## 7. Final decision statement

The definitive implementation direction is:

```text
006 Fi baseline
+ explicit, populated trajectory/1 evidence
+ named wired graph
+ ledger-mediated stigmergy
+ feasibility-first Pareto control
+ VFE belief fitting / EFE policy selection
+ least-privilege verified macro compilation
+ exact paired, exterior, human-gated promotion
```

First make evidence complete and continuation real. Then make composition generic and delete the fork. Prove the nine-row coding foundation once. Prove a non-coding formal pack with zero domain/kernel changes. Only then add mediated delegation, controlled swarms, adaptive routing, macro compilation, and statistical learning. Any feature that weakens the Clean Triad, widens authority from learned state, bypasses S0-S12, fabricates missing economics, or lets a candidate certify itself is rejected even if it improves benchmark quality, token use, cost, or latency.
