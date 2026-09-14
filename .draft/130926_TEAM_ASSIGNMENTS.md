---
id: draft.assignments.130926
class: directive
authority: leadership-assignment-draft
status: draft
owner: ceo-cto
date: 2026-09-13
subject_head: 4db1f758a4621868e8fbcca80d472c20e94ab385
branch: feat/aether-framework-electroweak-canonical-agents
companion: .draft/130926_CEO_GUIDELINES_TO_DEVS.md
team: Dev A (hard problems, architecture, planning) + Dev B & Dev C (core, together)
horizon: two weeks, autonomous within lease
---

# Team assignments — SOTA coding harness

Three developers. I am Dev A and I take the architecture that changes domain shapes and the
decisions nobody else is allowed to make. B and C own the core together, one coherent half of the agent each, and run without per-leaf permission.

---

## 0. Where we actually are

Verified at `HEAD 4db1f758`. This is the honest gap, not the roadmap's version
of it. Everything marked **landed** is real and should not be rebuilt.

| Capability | What a SOTA harness needs | What we have | Owner |
|---|---|---|---|
| Tool surface | read / write / edit / glob / grep / shell / plan / delegate | **5 verbs**: `fs.read`, `fs.search`, `patch.apply`, `proc.exec`, `finish` | A + B |
| Actions per turn | batch of independent reads, partial-ordered | **1, structurally** — `Proposal.action: str \| None` (`agency/episode/state.py:87`) | **A** |
| Code index | symbol graph, callers, tests, imports | **regex definition scan** (`adapters/stores/repo_index.py:29`); LDA's 90,128 relations unused by the product | **C** |
| Edit primitive | exact unique-preimage replace + whole-file | **unified diff / whole-file only**; `str_replace` returns zero hits repo-wide | **B** |
| Multi-file | atomic all-or-nothing + whole-candidate tree digest | 2PC transaction manager exists; exact-edit and caller admission missing | **B** |
| Planning | durable plan the model reads and revises each turn | `SemanticTaskState` + `PlanRevised` exist and fold; **no plan verb** — the model cannot write to its own plan | **A** |
| Sub-agents | delegate exploration so the parent's context survives | `EpisodeEngine.spawn()` implemented with attenuation — but **`agency.spawn` is not a declared capability in `packs/code-default/harness.yaml`**, so it is unreachable from the product | **A** |
| Memory | authorized retrieval into the turn | adapter is 639 LOC and declared; on the product path only `authorize("write")` appears — **retrieval is not wired** | **C** |
| Skills | retrieved, versioned, promoted on evidence | **one static card** (`pytest-green.json`) | **C** |
| Context economics | progressive, cache-stable prefix, distilled results | **landed** — stable L1–L3, CTRF distillation, trailing goal echo (T-77) | C (hardening only) |
| Prompt caching | provider `cache_control` on the frozen prefix | **landed** — `prompt_codec.py` negotiates per model, auto-detects support; never verified against a live provider (RUN-12) | C (verify hermetically) |
| Compaction / long sessions | survive 100+ turns and a process restart | **landed** — 104 turns across four fresh interpreters, semantic parity (T-110) | C (extend to index/memory) |
| Budget | one aggregate across effects *and* inference | **landed 2026-09-13** — `runtime/inference_meter.py`; presets recalibrated from measurement | A (ratified) |
| Verification truth | exterior oracle on the exact submitted tree; no false green | tamper shield wired; vacuity gate landed; caller admission missing | **B** |
| Measurement gate | the gate runs the instrument that measures us | `just verify` covers ~947 of ~3,171 tests and excludes `test/benchmarks` and `test/falsifiers` | **B** |

**The one-sentence read:** context engineering is largely solved; *acting* and
*seeing* are not. The agent compiles an excellent 11,000-token prompt and then
spends a turn reading 100 lines with a regex index and writes with a diff format
that fails silently.

---

## 1. Dev A — hard problems, architecture, planning (me)

I take the work that changes a domain shape, crosses three layers at once, or is
a decision rather than an implementation. I also own `session.py` arbitration
and every leadership delta.

### A1 — Parallel observation as a causal partial order

**The problem.** `Proposal` carries exactly one `action`. At 20 turns, one
`fs.read` of 100 lines costs 5% of an episode. A brownfield task needs a dozen
reads before the first edit, so the budget is gone before any change is
proposed. This is the single largest cause of low pass rate, larger than any
write-seam defect.

**The design.** A proposal may carry N **independent, read-only** requests,
settled as a partial order within one turn. Vision Ch. 15 names this exactly:
*"duas leituras independentes de arquivos são um caso trivial em que paralelismo
deve ser possível."*

Non-negotiable constraints, because this is where it would go wrong:

- **Read-only only.** `patch.apply`, `proc.exec`, `finish`, `spawn` stay single
  and strictly serialized. No batched mutation, ever — the single-writer rule
  and the atomic-candidate invariant (RUN-10) are untouched.
- **Per-request causal identity.** Each sub-request keeps its own
  `EffectStarted` / receipt / digest. A collapsed batch receipt would destroy
  replay and make `ChangeSurfaceUpdated` unreconstructable. Sequence number is
  not dependency: A before C and B before C without A before B.
- **One reservation per sub-request**, settled individually against the governor.
  The inference meter already establishes that shape.
- **Failure is per-request.** One failing read does not void the others.

**Lease.** `agency/episode/state.py`, `agency/episode/engine.py`,
`domain/ledger/` event shapes, `adapters/models/invocation.py` (batch parsing),
`vanguard/packages/agency/manifests/*/`, new
`test/falsifiers/test_parallel_observation.py`.

**Falsifier.** Ten independent reads settle in one turn with ten distinct
receipts and ten distinct digests; a batch containing any mutation verb is
rejected typed; a mid-batch failure leaves the other nine settled; cold replay
reconstructs the identical partial order. Mutation-proven, each one.

### A2 — Delegation reachable from the product

**The problem.** We built monotonic attenuation, nested lineages, `ChildSpawned`
/ `ChildReturned`, depth bounds and budget conservation — and the coding pack
declares four verbs, none of them `agency.spawn`. The capability is complete and
unreachable. A SOTA harness delegates exploration precisely so the parent's
context is not consumed by it.

**The design.** Declare `agency.spawn` as a capability in the coding pack with a
bounded, read-only child scope: the child may observe and report, it may not
patch or exec. Parent budget funds the child; depth ceiling 1 for this sprint.
The child's finding returns as a bounded artifact receipt, not as raw transcript
spliced into the parent's L5 — otherwise delegation costs more context than it
saves, which is the failure mode everyone hits.

**This is `POST-CONTROL` under the current board.** I am not activating it in the
control arm. It lands behind the existing composition so it is ready and
measurable, and MS-CONTROL's balanced arm does not declare it. Say so in the
handoff and do not let it drift into the measured composition.

**Lease.** `packs/code-default/harness.yaml`, `runtime/child_runtime.py`,
`runtime/delegation.py`, new `test/falsifiers/test_product_delegation.py`.

### A3 — The plan spine the model can actually write to

**The problem.** `SemanticTaskState`, `TaskStep`, `StepState` exist in
`domain/task_state.py`, fold in `runtime/task_state.py`, and are consumed by
`app_service.py`. The model has no verb to write to any of it. Its plan lives in
prose inside `note`, so it is lost at the first compaction and unreconstructable
from the ledger.

**The design.** A `plan` verb whose payload is the existing domain type — no new
step-status enum, no competing state. Plan revision is a `PlanRevised` fact;
compaction preserves it by construction (it is state, not transcript);
a resumed session rebuilds it from the fold rather than from text.

**Lease.** `domain/task_state.py`, `runtime/task_state.py`, the manifest tool
schemas, new `test/falsifiers/test_plan_spine.py`.

### A4 — Lossless Trajectory Bundle

Per D-4 of the directive. Content-addressed raw request/response capture on
every model call, redaction by policy rather than truncation by default. This is
what makes RUN-13 answerable, makes every dev run a free regression fixture, and
gives the paired-trial work in Vision Ch. 9 its substrate. `runtime/artifacts.py`
already has the capture seam; it retains hashes where it needs to retain bytes.

### A5 — Decisions, not implementations

Mine alone, and not delegable: the Sealed Holdout Protocol design (D-3), the
Q-01 denial predicate (D-2), preset calibration ratification, every public port
or schema delta, and independent review of B's and C's adversarial falsifiers —
specifically **re-running their mutations myself**, because last round two of
three peer reviews ran zero mutations and one reviewed functions that do not
exist in the repo.

---

## 2. Dev B — Act & Verify

**Your half of the agent:** everything from "the model decided to change
something" to "an exterior oracle confirms the exact tree it submitted." Plus
the gate that proves it, because a write path nobody measures is not a write
path.

### B1 — Exact-edit primitive (T-78)

The agent's only edit tools are unified diff and whole-file overwrite. LLM
unified diffs fail on hallucinated context lines, and they fail *silently* — the
model believes it wrote. Whole-file overwrite on a 2,000-line file burns the
context budget and loses unrelated content.

Implement unique-preimage `str_replace` through the **existing** 2PC transaction
manager. Non-unique preimage, absent preimage, or post-edit syntax failure →
typed `PATCH_PREIMAGE_MISMATCH` with byte-identical rollback of every file in
the transaction. **No fuzzy matching and no indentation relaxation, ever** — a
near-miss that silently succeeds is worse than a failure, because it corrupts a
file the agent believes it edited correctly.

Declare it in the four presets next to `patch`. Tool-surface addition is
pre-authorized; you do not need to ask.

### B2 — Multi-file atomicity and the whole-candidate digest

RUN-10 requires an atomic all-or-nothing multi-file commit carrying a final
whole-candidate tree digest, and an exterior oracle that evaluates *that exact
tree*. Prove it end to end: a five-file transaction where file four fails
validation leaves all five byte-identical; a successful transaction publishes
one tree digest; the oracle observes that digest and no other. A same-named
foreign tree, a post-verification mutation, an extra file, a deleted file and a
stale artifact must each fail to publish green.

### B3 — Caller admission (T-83b)

Feed `IndexPort.get_callers` into `_admit_completion` through the pack's
`multi_file_completeness` middleware. A public-symbol change cannot finish while
known callers are uninspected → typed `UNINSPECTED_CALLERS_REMAINING`.

**Depends on C1.** Build against the `IndexPort` interface, not C's
implementation, and write the falsifier with a fake index first — that is the
whole point of the port existing.

**Coordination:** this needs `session.py::_admit_completion`, which is B's lease
this sprint. Deliver the policy as a pure module under `agency/` and hand C the
three-line call. Named handoff, not a concurrent patch.

### B4 — Local-model write-landing reproduction (D-5)

RUN-13's write-landing question is open and T-130 could not answer it: synthetic
fixtures emit well-formed tool calls, so the probe could not observe the failure
class it was hunting. Re-run it against **local GGUF models via llama-cpp** —
not a provider call, `$0.00`, and they produce the real phenomena: fenced JSON
inside `note`, schema drift, truncated arguments, synonym argument names,
hallucinated diff context.

Small models fail *more* and more legibly. That makes them a better instrument
for seam attribution, not a worse one.

Attribute each failure to its **first** failing seam; report multiple
independent causes separately rather than collapsing them into one narrative.
**This is diagnosis, not a repair lease.** Do not name a repair site; the
attribution returns to me as evidence.

### B5 — Make the gate real (T-132)

`just verify` runs ~947 of ~3,171 tests and excludes `test/benchmarks` — which
contains the control instrument — and `test/falsifiers`, which contain the
adversarial proofs. Every "verify passed" in recent handoffs is simultaneously
true and silent about the instrument. That is how the stale oracle digest
survived.

Widen to full-tree discovery with individually justified exclusions. `test/e2e`
and `test/broken` not being importable is either deliberate-and-recorded or
fixed — do not leave it unstated. Keep `just check` fast. Record measured
wall-clock narrow vs. widened on the same subject; if full discovery is too slow
to run every time, bring me the numbers rather than a convenient subset.

**Mandatory red control:** an intentionally stale oracle digest MUST fail
`just verify`. A green widened gate proves nothing.

### B6 — Quarantine by denial (T-133 correction) and CI truth

Close the four reopening grounds: unknown/absent ID bypass, identity-only
guards, unverified evaluation authority, 14 unleased loaders. Every inventory
entry needs **callable-level** guard and role coverage, not a guard name
somewhere in the file. `HOLDOUT UNACCEPTED` must exit non-zero on any
acceptance path.

**Acceptance is a set of mutation-proven denials, one per adversarial class** —
missing ID, unknown ID, renamed alias, copied tree, modified sealed source,
forged authority, forged FROZEN flag, absent registry, absent attestation. An
inventory is not a guard. I design the Sealed Holdout Protocol (C5); you
implement the tripwire against it.

Then CI truth: ~6 modules fail at import (`setuptools`; removed `lab.m65_study`
and `lab.m701_independence`; `test_s20_live_turn_freeze` importing the deleted
`adapters.models.ollama`). Purge remaining `ollama` references — forbidden
repo-wide. Resolve `check_doc_budgets`, red on `main` for five owner-held docs:
reduce or calibrate, your call, record which and why. A test that cannot import
is a check that cannot fail.

**Lease.** `adapters/environment/{git,transaction}.py`,
`packs/code-default/{toolkits,oracles,middleware}/`, `agency/multi_file_*.py`,
`benchmarks/`, `tools/{linters,diagnostics}/`, `justfile`, `.github/workflows/`,
`test/{adapters,benchmarks,packs,contracts}/`, manifest tool schemas for the
edit verb. Not `session.py` — that is C's this sprint.

**Exit.** B1–B3 landed with mutation-proven falsifiers; B4 returns a seam
attribution or a documented reason the class is unreachable locally; B5 landed
with its red control; B6 accepted on denials, CI green.

---

## 3. Dev C — See & Remember

**Your half of the agent:** everything from "the agent needs to know something"
to that knowledge arriving in the turn, within budget, and surviving a restart.
Your single measure of success: **the agent spends fewer turns looking and more
turns changing.**

### C1 — LDA-backed `IndexPort` (T-75)

We built a state-of-the-art graph retrieval engine — 90,128 relations, 11,608
symbols, sub-50ms delta indexing — and handed the product a regex definition
scan. Every developer and every AI agent in this repo navigates with LDA. The
product agent cannot. Fix the dogfooding gap.

Implement the existing `IndexPort` structurally over `.lda/index.db`. Value-only
symbols, dependency edges, test associations. A missing or stale index fails
**deterministically with no partial map** — preserving T-45's fallback. Ranking
never enters the port or the adapter; the index answers what is in the
workspace, the episode decides what that means.

Keep `FileRepoIndex` as the declared fallback. Do not delete it.

### C2 — `repo.*` observation verbs into L5 (T-76)

Expose `repo.search_symbols`, `repo.get_callers`, `repo.get_dependencies`,
`repo.get_tests` as bounded observations. One `get_callers` replaces ten
`fs.read`s — that is the whole turn-economics argument in one line.

Results enter **L5 only**. The L1–L3 prefix must stay byte-identical across
turns: prefix stability is what makes provider caching possible at all, and
breaking it silently multiplies cost on every subsequent turn. Falsifier: ten
turns, identical L1–L3 digest, all four observations present in L5.

### C3 — Memory retrieval on the product path

The memory adapter is 639 LOC, declared in `harness.yaml`, and on the product
path only `authorize("write")` appears. We write experience nobody reads.

Wire authorized retrieval into context compilation: **authorization precedes
retrieval** (Vision Ch. 20 / ADR-0096), retrieved material carries retrieval
provenance (`require_retrieval_provenance` already exists), and it lands in L5
where it cannot perturb the cached prefix. Retention never grants permission to
capture.

Scope discipline: this is *durable authorized retrieval*, not governed learning.
M-8's lift predicate, separated promotion authority and rollback are **not** in
this sprint. Do not build a promotion path.

### C4 — Skill retrieval

One static card today (`pytest-green`). Make skill selection retrieval-driven
and task-conditioned rather than a fixed list, respecting the `W12-A` ≤4096
character prompt-prefix ceiling. Skills stay in the frozen prefix region only if
they are stable for the composition epoch — a skill set that changes per turn
belongs in L5, not L3, or it destroys the cache.

Promotion on evidence is M-8 and out of scope. Retrieval is in scope.

### C5 — `INDEX_UNBOUND` disposition (T-135)

Unchanged from your existing row. `index=None` is typed infrastructure
`UNDETERMINABLE` with a retained slot: consults policy zero times, admits no
completion, burns no recovery retry, lowers the binary count. Publish both
denominators. Missing index, stale packet, explicit policy denial and provider
failure stay four distinct things.

Note the interaction with C1: once the index is LDA-backed, `INDEX_UNBOUND`
becomes reachable in production for the first time. Make sure it degrades to the
`FileRepoIndex` fallback where a fallback is legitimate, and fails closed where
it is not — and prove which is which.

### C6 — Long sessions: extend the proof to index and memory

T-110 proved 104 turns across four fresh interpreters with semantic parity, for
the context vector. It did not cover a bound index or retrieved memory, because
neither was on the path. Extend the same proof: after a restart, the index
rebinds without re-reading the world, retrieved memory is re-authorized rather
than assumed, and the compaction vector still preserves objective, constraints,
unresolved failures, plan state, changed-file identity and the resource ledger.

Also: verify prompt caching hermetically. `prompt_codec.py` negotiates
`cache_control` per model and auto-detects support, but it has never been
verified against a live provider and RUN-12 forbids one. Prove the *negotiation*
— supported route gets marked breakpoints, unsupported route gets byte-identical
unmarked messages. Prefix equality proves deterministic bytes; it never proves a
cache hit, a speedup, or a cost reduction. Do not claim one.

**Lease.** `adapters/stores/` (new `lda_index.py`), `ports/index.py`,
`ports/memory.py`, `agency/context/`, `packs/code-default/plugins/`,
`vanguard/packages/runtime/session.py` (yours this sprint),
`benchmarks/ladder/evidence.py`, `test/{contracts,agency,runtime,falsifiers}/`
for those surfaces.

**Exit.** C1+C2 landed with the L1–L3 byte-identity proof; C3 landed with
authorization-before-retrieval proven by a denial; C4 landed inside the 4096
ceiling; C5 and C6 closed.

---

## 4. Coordination

Three rules, and nothing else.

1. **`session.py` is C's this sprint.** B and A deliver pure modules plus a named
   wiring request; C lands the call. A defect needing someone else's file is a
   lease transfer, never a concurrent patch. If this becomes the bottleneck I
   expect, tell me in week one and I will decompose the file — that is my job,
   not yours to work around.
2. **Ports before implementations.** B3 builds against `IndexPort` with a fake,
   not against C1's adapter. C1 lands the adapter behind the same port. Neither
   of you waits on the other; that is what the port is for.
3. **Escalate for four reasons only:** a public port or schema change, an
   invariant you cannot preserve, a budget or authority expansion, or a
   falsifier that would need weakening. Everything else is yours.

---

## 5. Rules that do not relax

The autonomy is real. These are not part of it.

1. **Never weaken, narrow away, or delete an existing check.** Narrow it and
   prove it still reds on the original defect. When a guard fires because you
   made an authorized change, update it *and add the new dimension* — that is
   what I did to `EXPECTED_PRESETS` in two files today.
2. **Mutation proof for every adversarial assertion.** Revert the guard, show
   the red, restore. I will re-run your mutations myself. A green suite over an
   unwired control manufactures false assurance and is worse than no control.
3. **RUN-12: zero provider calls, zero USD.** `lam-engine` and `llama-cpp` only.
   Ollama forbidden repo-wide. A credential's existence is not authority.
4. **RUN-13 stays open.** No repair site is named. Attribution is evidence.
5. **Kernel delta zero; TCB ceiling 1438** (currently 1386). Invariant N-06: no
   `subprocess` in `runtime/`. Boundary lattice unchanged: adapters never import
   kernel or agency.
6. **One `EpisodeEngine`.** No second agent loop, no workflow engine, no
   topology language. Delegation is a nested lineage, not a new runtime.
7. **Byte-for-byte rollback** on any repair loop that exhausts its budget.
8. **Honest status.** Report what you actually ran. Never claim `PASS` for an
   unexecuted command. Never `|| true`. A timeout is an incomplete check.
9. **LDA: delta-index only**, never rebuild. Verify `source_head_sha` binds
   current `HEAD` before trusting a packet.
10. **No new Markdown under `docs/`.** Findings go to the Senior for transfer
    into `main/`, or into your task handoff.

---

## 6. Not in this sprint

Named so nobody infers authorization from silence.

- No paid run, no freeze, no T-26, no T-27. Control stays UNFROZEN.
- No M-8: no governed learning, no lift predicate, no promotion authority, no
  rollback path. C3/C4 are retrieval only.
- No topologies, no scheduler, no MCTS, no critic swarms, no learned routing.
- No second agent loop and no workflow engine.
- No public port or schema change without a named delta from me.
- No score claim of any kind. Mechanism presence is not acceptance.

---

## 7. What success looks like

Not "tests pass." In two weeks I want to be able to say, with receipts:

- An agent given a brownfield task **finds the blast radius in one observation
  instead of ten**, and the L1–L3 prefix is byte-identical while it does.
- An agent that decides to change five files **either changes all five or
  none**, and the oracle scores the exact tree it submitted.
- An edit that cannot be applied **says so in a typed way the agent can act on**,
  rather than silently not happening.
- A 100-turn session **restarts and keeps its plan, its index binding and its
  authorized memory**.
- Every declared ceiling on a preset **is a ceiling that binds** — which became
  true today, and must stay true.
- The gate that says "green" **has actually run the instrument that measures us.**

If we get those six, MS-CONTROL becomes a measurement worth taking. Until then
it measures the harness we did not finish building.
