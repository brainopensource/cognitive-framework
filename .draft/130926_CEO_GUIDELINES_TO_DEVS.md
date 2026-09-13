---
id: draft.ceo.guidelines.130926
class: directive
authority: leadership-decision-draft
status: draft
owner: ceo-cto
date: 2026-09-13
subject_head: 4db1f758a4621868e8fbcca80d472c20e94ab385
branch: feat/aether-framework-electroweak-canonical-agents
supersedes_scheduling_in: docs/execution/main/tasks.md (pending Senior transfer)
binding: >-
  Advisory until the Senior transfers the numbered decisions into
  docs/execution/main/{spec,tasks}.md. Nothing here edits canonical law directly.
---

# CEO / CTO Directive — 2026-09-13

## Read this part if you read nothing else

We have spent the last several cycles perfecting a ruler and almost none building
the thing it measures. Eight of the nine active rows on the board are about the
*instrument* — quarantine, gate discovery, accounting, approval probes, write
probes. Every row that would make the agent **better at software engineering** is
unchecked and unowned: T-75 (real code index), T-76 (symbol verbs), T-78 (exact
edit), T-80 (thrash breaker), T-83b (caller admission).

Meanwhile the product agent, at `HEAD`, has:

- **five tool verbs** — `read`, `search`, `patch`, `test`, `finish`
  (`vanguard/packages/agency/manifests/vg-code-balanced/manifest.json`)
- **one action per turn**, structurally — `Proposal.action: str | None`
  (`vanguard/packages/agency/episode/state.py:87`)
- **a regex code index** — `FileRepoIndex` is a definition-regex scan
  (`vanguard/packages/adapters/stores/repo_index.py:29`), while our own LDA graph
  holds 63,514 `calls` and 11,752 `tests` relations that the product cannot see
- **no exact-edit primitive** — `str_replace` does not exist anywhere in
  `vanguard/` or `packs/`; writes are unified-diff or whole-file overwrite
  (`vg-code-default/patch-tool.json`)
- **`read` defaulting to 100 lines**, inside a 20-turn ceiling

A perfect instrument pointed at that agent will measure a low number, correctly,
and we will have learned nothing we did not already know. **MS-CONTROL is not
currently blocked by measurement integrity. It is blocked by capability.**

So: the program splits into two streams that do not gate each other, plus one
that fixes the accounting. Capability work no longer waits on T-27. Nothing is
weakened — the control boundary stays exactly as strict as it is today; it just
stops being the critical path for everything else.

---

## Part I — Decisions

These are decisions, not proposals. D-1 through D-9 are ratified by this
directive. The Senior transfers them into `main/` (see Part V).

### D-1. Two independent delivery streams. No gate between them.

`MEASURE` (control integrity) and `CAPABILITY` (SOTA harness) proceed in
parallel with disjoint leases. A capability row may not cite an unfrozen corpus
as a blocker, and a measurement row may not cite an unlanded capability as a
blocker. The only place they meet is the widened verification gate (D-8).

**Rationale.** `requires:` edges currently route almost everything through
T-27, which routes through T-26, which routes through T-51, which is blocked on
an independent human curator and an external sealed store we do not possess.
That is a single point of program failure with a non-engineering root cause.

### D-2. Q-01 is proven by denial, never by inventory. (The reserved decision.)

The previous session reserved one question for me: *Q-01's contamination claim
rests on inventory rather than enforcement.* Ruling:

1. **T-133's reopening stands.** The Director was right and the grounds are
   correct: `guard_materialization(task_id=None)` returning normally is a
   bypass, an unchecked source fingerprint is not a guard, and a truthy
   authority string is not evaluation authority.
2. **The acceptance predicate for a quarantine gate is a set of *denials*,
   each proven red by mutation.** Not a count of entrypoints, not a passing
   helper suite, not an `exit 0` diagnostic. Concretely: N adversarial
   materialization attempts — missing ID, unknown ID, renamed alias, copied
   tree, modified sealed source, forged authority, forged FROZEN flag, absent
   registry, absent attestation — each MUST be denied, and each denial MUST be
   shown to disappear when the guard is reverted. A guard with no demonstrated
   red is not a guard.
3. **T-132 may not re-close Q-01 on the weaker basis.** Gate coverage and corpus
   integrity are two different receipts. "The corpus suites now run in
   `just verify`" proves the suites run. It says nothing about whether the
   corpus is clean. Neither receipt may ever be cited for the other, and a
   `just verify` pass MUST NOT appear in any Q-01 acceptance argument.

This does not weaken any existing check. It replaces a check that cannot fail
(an inventory) with one that can (a mutation-proven denial).

### D-3. The Sealed Holdout Protocol — commitment, not custody.

Q-01 as written requires "a separate curator-controlled store absent from
developer mounts" and "an independent curator" attesting lineage. We do not have
a second human and our agents have full repository access. That is an
organizational constraint dressed as a linter task, and it will block T-51
forever if we leave it as written.

**Replace physical separation with cryptographic commitment plus a tripwire.**

```
HOLDOUT REGISTRY (in repo, public)        SEALED BUNDLE (out of repo)
  opaque_id                                 age/gpg-encrypted tarball
  stratum                                   plaintext tasks + oracles
  commit = HMAC(K_reg, canonical_bytes)     key held by release owner only
  exposure_tombstone: bool                  injected at a measured slot, then
                                            the mount is torn down
            |                                          |
            +---------------- TRIPWIRE -----------------+
   every loader / capture / export / index / LAM path computes
   HMAC(K_reg, bytes_it_touched) and checks membership in the
   commitment set. A hit writes an irreversible EXPOSED tombstone
   and fails closed. Absence of a hit is not proof of cleanliness;
   presence of a hit is proof of contamination.
```

Properties that matter:

- `closure(H) ∩ closure(D*) = ∅` becomes **machine-checkable without the
  plaintext being present**, which is the whole point. The registry carries
  commitments; the linter can run in CI with no secret.
- A rename, copy, or re-digest does not evade it — the commitment is over
  canonical content bytes, not paths or IDs.
- The "independent curator" obligation reduces to **role separation by key
  custody**: whoever holds `K_bundle` may not be the person who runs the solver.
  That is one person and one key, not a second organization.
- The tripwire is the enforcement D-2 demands. It is a *denial* mechanism, not
  an inventory.
- Near-duplicate/semantic-novelty attestation stays a human judgment and stays
  outside the linter's claims. The linter must continue to say "no commitment
  collision found", never "corpus is clean."

**T-51 is unblocked to build the protocol.** It remains blocked to *freeze*
until a real sealed bundle exists and the tripwire has demonstrated denials.

### D-4. Lossless Trajectory Bundle (LTB) — the highest-leverage thing we can build.

RUN-13's causal question cannot be answered with the evidence we retain. The
retained cassettes hold "hashes and usage counts rather than tool payloads", so
no historical failure can be replayed. T-130 therefore probed with *synthetic*
fixtures and returned NOT_REPRODUCED — which was the only possible outcome,
because synthetic fixtures emit well-formed tool calls. We built a probe that
could not, in principle, observe the failure class we were hunting.

**Decision: every model call captures a lossless, content-addressed
request/response pair, in every profile, retained by policy rather than
truncated by default.** Redaction is a *policy* applied to a complete capture,
never a lossy capture pretending to be a policy.

This is Vision Chapter 3 (replay vs. re-execution) and Chapter 9 (observability
is part of the product, not post-processing) made real. What it buys:

- Any run — historical or future — becomes replayable hermetically at **$0**.
- Every failing dev run becomes a free regression fixture. Our falsifier corpus
  starts growing by itself.
- RUN-13 becomes answerable without a single paid call.
- Paired A/B trials, ablations, and compaction studies (Vision Ch. 9) get their
  substrate for free.

The capture seam is `vanguard/packages/runtime/` (`ArtifactWriter` / capture
policy already exist at `session.py:955-975`). Kernel delta: **zero**.

### D-5. Reproduce RUN-13 with a local model. It is free and it is real.

RUN-12 says zero provider calls, zero USD — and permits `lam-engine` and
`llama-cpp`. A local GGUF model through `llama-server` is **not a provider
call** and costs **$0.00**. It also produces the exact phenomena a synthetic
fixture cannot: fenced JSON inside `note`, schema drift, truncated tool
arguments, argument-name synonyms, hallucinated diff context lines.

**Decision: the write-landing investigation is re-run against local models
before any further synthetic probing.** Small models fail *more*, and more
legibly, than frontier models — which makes them a better instrument for seam
attribution, not a worse one.

Boundaries, stated so nobody oversteps: this is a **diagnostic method**, not a
repair authorization. RUN-13 remains open and **no repair site is named by this
directive**. If the local-model run attributes a first failing seam, that
attribution returns to leadership as evidence; it does not become a lease.

### D-6. Inference Accounting Delta — the budget algebra currently has a hole.

Verified at `HEAD`:

- `harness.budget["tokens"]` is used as the **Governor's additive, conserved
  ceiling** (`runtime/session.py:898-901`, `ADDITIVE_DIMENSIONS` at
  `kernel/budget.py:49`) **and simultaneously** as the **ContextCompiler's
  per-turn prompt window ceiling** (`runtime/session.py:942`).
- Those are two incompatible conservation laws sharing one key. Under reading
  (2), one maximal turn may legally consume the entire episode's budget under
  reading (1). Under reading (1), the 20-turn balanced preset must average
  ≤2,000 tokens/turn — below the stable L1–L3 prefix plus tool schemas.
- The model call is invoked directly (`agency/episode/engine.py:447`,
  `self._model.propose(...)`) and does **not** traverse the kernel's S0–S12
  dispatch. Token usage and USD are recorded as telemetry/diagnostics
  (`engine.py:1034`), not reserved and committed against the `Governor`.

So the dominant cost of a coding episode sits outside the budget algebra the
whole architecture is built on. RUN-09(8) names the *escalation* half of this;
nobody has named the base case.

**Decision, authorized as a named leadership delta (RUN-04 reserves preset and
public-contract changes to leadership; this is leadership exercising it):**

1. **Split the key.** `context_window_tokens` (compiler ceiling) becomes
   distinct from `tokens` (conserved spend). Presets declare both explicitly.
   No preset's *effective* behavior may change silently as a result — the
   migration must publish before/after effective ceilings for all three presets.
2. **Meter inference at the runtime boundary.** A `MeteredModelPort` decorator
   in `runtime/` implements `ModelPort`, reserves worst-case before the call and
   commits actual after, against the same `Governor`. The kernel stays
   domain-blind; the TCB does not grow; this is the ordinary ports-and-adapters
   shape. **Kernel delta: zero. TCB ceiling 1438 unchanged.**
3. **Publish effective vs. declared turns.** Every episode reports the turns it
   could actually fund alongside the turns it declared. A preset that cannot
   reach its declared ceiling is a measurement defect, and MS-CONTROL must not
   be frozen on top of one.

**This is a `BLOCK-T26` item.** Do not freeze a control arm whose declared
resource envelope is not the envelope it enforces.

#### D-6 status: measured, built, landed (2026-09-13)

Not delegated. Measured on the product path, fixed, and falsified in this
session. The measurement first, because it changed the diagnosis:

| preset | declared | reported, before | stopped by |
|---|---|---|---|
| fast | $0.05 / 16,000 tok / 8 turns | $0.20 / 31,200 tok | turn bound |
| balanced | $0.15 / 40,000 tok / 20 turns | $0.50 / 78,000 tok | turn bound |
| max | $0.40 / 96,000 tok / 40 turns | $1.00 / 156,000 tok | turn bound |

So the "double-binding" half of my reading was **wrong** and the hole was
larger than I described: the presets did deliver their declared turns, because
*nothing enforced the other two ceilings at all*. Inference was the one
unmetered resource in an episode. The ceiling denominated in money did not bind.

Landed:

- `runtime/inference_meter.py` (new) — reserve worst-case before the provider
  call, settle actual after, against the same `Governor` the kernel uses.
  Unknown cost is recorded `unsettled`, never zero. Overruns are charged.
- `runtime/session.py` — the meter is built beside the governor and wired into
  the layered operator, which was already the runtime-owned model boundary.
- `agency/episode/engine.py` — a denied reservation terminates
  `BUDGET_EXHAUSTED`, not `instrument_error`. A working ceiling must not be
  reported as the model misbehaving, and must not land in the missingness
  taxonomy (`DIR-D2`).
- `adapters/models/openrouter.py` — a three-valued `pricing` property so the USD
  dimension can be bounded *before* a paid call. Priced route → rates; free tier
  → `(0, 0)`; unknown route → `None`, which has never meant free.
- `compose.py` / `packs/code-default/load.py` / `presets.json` / all seven
  manifest `budget-policy.json` — the key split. `tokens` is conserved spend;
  `contextWindowTokens` is the per-turn prompt bound. Every one of those
  manifests had declared `tokens` meaning *window* while handing it to the
  governor as *spend*, which is why the original values were incoherent as
  budgets.
- Calibration is from measurement, not arithmetic: compiled prompts run
  10,823–15,973 tokens/turn, growing ~50–100/turn as L5 accumulates.

Measured after: **fast 8/8, balanced 20/20, max 40/40**, all terminating on the
turn bound with the token and USD ceilings live.

Falsifier: `python3 -m unittest test.falsifiers.test_inference_accounting`
(14 tests). Three mutations proven red and restored:

1. unwire `meter=` in `session.py` → the overrun test reds (`'reservation
   denied' not found in 'turn bound 20 reached'`);
2. delete the engine's budget branch → reds `instrument_error != budget_exhausted`;
3. restore the old token ceilings → `fast declares 8 turns but funded 2`.

Regression: kernel 102, agency 310, contracts 546, adapters 198, packs 92,
apps 38, falsifiers 565, runtime 851, benchmarks 194. The only failures are the
five that are red at `HEAD` without this change (3 runtime import/approval
errors, 2 `test_control_corpus` quarantine failures), confirmed by a stash
baseline. All linters pass; kernel LOC unchanged at 1386.

### D-7. Turn economics — stop spending the budget on looking.

Ranked by leverage, all four are authorized:

| # | Change | Why it is worth a sprint |
|---|---|---|
| 1 | **Parallel read-only observation batch** | `Proposal` is structurally single-action (`agency/episode/state.py:87`). One `read` of 100 lines costs 5% of a balanced episode. Permit a proposal to carry N *independent, read-only* requests settled as a partial order in one turn. Vision Ch. 15 anticipates exactly this ("duas leituras independentes de arquivos são um caso trivial"). **Read-only only** — no batched mutation, no batched `proc.exec`, no relaxation of the single-writer rule. |
| 2 | **LDA-backed `IndexPort` (T-75/T-76)** | We built a state-of-the-art graph retrieval engine and handed the product a regex scanner. 63,514 call edges and 11,752 test associations exist on disk and are invisible to the agent. Dogfood it. One `repo.get_callers` replaces ten `read`s. |
| 3 | **Exact `str_replace` (T-78)** | Unified-diff generation is the single most common write-failure mode in this industry, and it fails *silently* — the model believes it wrote. Exact unique-preimage replacement with typed `PATCH_PREIMAGE_MISMATCH` converts a silent failure into a legible one the agent can recover from. Routed through the existing 2PC manager; byte-identical rollback preserved. |
| 4 | **Caller admission (T-83b)** | A public-symbol change that finishes without inspecting known callers is a false completion waiting to be scored as a pass. |

### D-8. The verification gate becomes real, and review theater ends.

Verified: `just verify` discovers only `test/kernel`, `test/agency`,
`test/contracts` — roughly 947 of roughly 3,171 tests. `test/benchmarks` (which
*contains the control instrument*) and `test/falsifiers` (which contain the
adversarial proofs) are outside it. Every "verify passed" receipt in recent
handoffs is simultaneously true and silent about the instrument. That is how the
stale oracle digest survived.

Separately: `check_doc_budgets` is red on `main` independently of this branch;
`CONVERGENCE-BASE-v1` does not resolve remotely and `check_baseline_manifest.py`
is correctly fail-closed red at `HEAD`; and roughly six test modules fail at
import (`setuptools`, removed `lab.m65_study` / `lab.m701_independence`, deleted
`adapters.models.ollama`). **We have a green-looking CI that is structurally
red.** That is worse than a red one.

Decisions:

1. **T-132 lands full-tree discovery** with individually justified exclusions,
   plus the mandatory red control: an intentionally stale oracle digest MUST
   fail `just verify`. A green widened gate proves nothing.
2. **Mutation proof becomes machine-checked, not promised.** A falsifier that
   does not red under the mutation harness is not a falsifier and does not
   count toward any acceptance. Last round two of three peer reviews ran zero
   mutations and one verified functions that do not exist in the repo
   (`_propose_or_latch`, `_execute_or_latch`) — which is how a real
   `observedTestCount` bug survived two reviews.
3. **Per-row Director review is retired** in favor of (1) + (2) + leases.
   Director review is reserved for the four escalation classes: public
   interface/schema change, an invariant that cannot be preserved,
   budget/authority expansion, and a falsifier that would need weakening.

Read decision 3 correctly: **no check is removed.** Human review is being
*replaced by a strictly stronger automated gate*, because a review that runs
zero mutations catches less than a mutation harness that always runs. The
standing rule holds in full — never weaken, narrow away, or delete an existing
check; narrow it and prove it still reds.

### D-9. Autonomy: two-week sprints, whole streams, no per-leaf permission.

Each developer owns a **stream**, not a row. Within your stream and lease you
choose sequencing, helpers, fixtures, error wording, algorithms, and the order
in which you close your objectives. You do not ask permission to start the next
thing. You escalate for exactly four reasons (D-8.3) and nothing else.

What does **not** relax: file leases (zero overlap, transfer never concurrent
patching), RUN-12 zero provider calls / zero USD, byte-for-byte rollback on
repair loops, honest status reporting, and the mutation-proof requirement.

---

## Part II — Stream assignments

Three streams. Two weeks. Owners A, B, C; pull in your own help freely.

### Stream A — *"The agent can act"* (write path, inference accounting)

**Objective.** A model's intent to change a file becomes a change to that file,
atomically, observably, and within an enforced budget — or fails loudly with a
typed reason the agent can act on.

| Work | Contract | Notes |
|---|---|---|
| **A1. Exact-edit primitive** (T-78) | Unique-preimage `str_replace` routed through the existing atomic multi-file transaction manager. Non-unique preimage or syntax failure → typed `PATCH_PREIMAGE_MISMATCH`, byte-identical rollback of all files. No fuzzy matching, no indentation relaxation, ever. | Declare it in the four presets alongside `patch`. This is a tool-surface addition, pre-authorized by this directive. |
| **A2. Inference accounting delta** (D-6) | Split `context_window_tokens` from `tokens`. `MeteredModelPort` in `runtime/` reserves worst-case and commits actual against the `Governor`. Publish declared-vs-effective turns per episode. | **Kernel delta zero.** Publish the before/after effective ceilings for `fast`/`balanced`/`max` — if any preset currently cannot reach its declared turn count, that number is the headline of your sprint. |
| **A3. Local-model write-landing reproduction** (D-5) | Re-run the write-landing investigation against `llama-cpp` local GGUF models across L0 / multi-file / greenfield. Attribute each failure to its **first** failing seam. Multiple independent causes are reported separately, never collapsed. | Zero USD, zero provider calls. This is diagnosis, **not** a repair lease. Do not name a repair site; return attribution as evidence. |
| **A4. Candidate/evidence identity** (T-131.6) | Unchanged from your existing row. Qualify identity through public `execute` → durable receipt → exterior oracle → returned evidence. Foreign same-named tree, post-verification mutation, extra/deleted file, stale artifact: none may publish green. | Do not invent a second tree algorithm. |

**Lease:** `runtime/entrypoint.py`, `runtime/evidence_capture.py`, new
`runtime/metered_model.py`, `adapters/environment/{git,transaction}.py`,
`vanguard/packages/agency/manifests/*/`, `packs/code-default/presets.json`
(transferred from C for A2 — C, hand it over before you start),
`test/falsifiers/test_t131_row6_evidence_identity.py`,
`test/benchmarks/test_product_path_subject.py`, new
`test/adapters/test_str_replace_exact.py`, new
`test/runtime/test_inference_accounting.py`.
`session.py` and `benchmarks/ladder/evidence.py` remain B's.

**Exit:** A1 and A2 landed with mutation-proven falsifiers; A3 returns a seam
attribution or a documented reason the class is unreachable locally; A4 closed.

---

### Stream B — *"The agent can see"* (retrieval, context, turn economics)

**Objective.** The agent stops spending its turn budget on looking. One
observation should answer a structural question, not return 100 lines of text.

| Work | Contract | Notes |
|---|---|---|
| **B1. LDA-backed `IndexPort`** (T-75) | Implement the existing `IndexPort` structurally over `.lda/index.db`. Value-only symbols, dependency edges, test associations. Missing or stale index fails **deterministically** with no partial map — preserving T-45's fallback. Ranking never enters the port or the adapter. | The current `FileRepoIndex` regex scan stays as the declared fallback. Do not delete it. |
| **B2. `repo.*` observation verbs into L5** (T-76) | `repo.search_symbols`, `repo.get_callers`, `repo.get_dependencies`, `repo.get_tests` as bounded observations. Results enter **L5 only**; the L1–L3 prefix stays byte-identical across turns. | Prefix stability is a hard invariant — it is what makes provider caching possible at all. Ten turns, identical L1–L3 digest. |
| **B3. Parallel read-only observation batch** (D-7.1) | A proposal may carry N independent **read-only** requests settled as a partial order within one turn. Mutation, `proc.exec`, and `finish` remain strictly single and strictly serialized. Each sub-request keeps its own receipt and its own causal identity — no receipt merging. | This touches `Proposal` (`agency/episode/state.py:87`) and the engine's turn loop. It is a domain shape change: **named leadership delta, authorized here**. Ledger event identity per sub-request is non-negotiable — Vision Ch. 15's partial order, not a collapsed batch. |
| **B4. Caller admission** (T-83b) | `IndexPort.get_callers` feeds `_admit_completion` through the pack's `multi_file_completeness` middleware. A public-symbol edit cannot finish while known callers are uninspected → typed `UNINSPECTED_CALLERS_REMAINING`. | Requires B1. |
| **B5. `INDEX_UNBOUND` disposition** (T-135) | Unchanged from your existing row. `index=None` is typed infrastructure `UNDETERMINABLE` with a retained slot: consults policy zero times, admits no completion, burns no recovery retry, lowers the binary count. Publish both denominators. | Stale packet, policy denial, provider failure and missing index stay four distinct things. |

**Lease:** `vanguard/packages/adapters/stores/` (new `lda_index.py`),
`vanguard/packages/ports/index.py`, `vanguard/packages/agency/episode/`,
`vanguard/packages/agency/context/`, `vanguard/packages/runtime/session.py`,
`packs/code-default/{toolkits,middleware,plugins}/`,
`benchmarks/ladder/evidence.py`, and the corresponding
`test/{contracts,agency,falsifiers}/` modules.

**Exit:** B1+B2 landed with the L1–L3 byte-identity proof; B3 landed with
per-sub-request receipts and a proof that mutations cannot batch; B4, B5 closed.

---

### Stream C — *"The numbers are true"* (instrument, gate, quarantine, CI truth)

**Objective.** Every green we report means something, and the corpus gate denies
rather than lists.

| Work | Contract | Notes |
|---|---|---|
| **C1. Quarantine by denial** (T-133 correction, D-2) | Close the four reopening grounds: unknown/absent ID bypass, identity-only guards, unverified evaluation authority, 14 unleased loaders. Every inventory entry gets **callable-level** guard and role coverage, not a guard name somewhere in the file. `HOLDOUT UNACCEPTED` must exit non-zero on any acceptance/scoring path. | Acceptance = mutation-proven denials, one per adversarial class. Revert the guard, show the red, restore. No exceptions. |
| **C2. Sealed Holdout Protocol** (D-3) | Build the commitment registry, the tripwire, and the bundle format. Registry is public and carries commitments only. Tripwire hooks every loader, capture, export, index and LAM path. A hit writes an irreversible tombstone and fails closed. | This is the row that unblocks T-51. Design it so CI can verify with **no secret present**. |
| **C3. Full-tree gate + red control** (T-132) | `just verify` discovers the whole tree with individually justified exclusions. `test/e2e` and `test/broken` not being importable is either deliberate-and-recorded or fixed — do not leave it unstated. Keep `just check` fast. Record measured wall-clock for narrow vs. widened on the same subject. | Mandatory red control: a stale oracle digest MUST fail `just verify`. If the widened gate is too slow to run every time, bring me the exact numbers, not a convenient subset. |
| **C4. CI truth cleanup** | Fix the ~6 import-time failures: missing `setuptools`; removed `lab.m65_study` / `lab.m701_independence`; `test_s20_live_turn_freeze` importing the deleted `adapters.models.ollama`. Purge remaining `ollama` references (it is forbidden repo-wide). Resolve `check_doc_budgets` red on the five owner-held docs — reduce or calibrate, your call, but record which and why. | Ordinary work, high value, zero drama. A test that cannot import is a check that cannot fail. |
| **C5. Approval-path probe** (T-137) | Unchanged from your existing row. Full matrix: interactive false/true, policy allowing/requiring, no approver, explicit denial, valid signed descriptor-bound approval, stale/foreign/boolean approval. Missing approver MUST NOT become default-allow. | Attribute, do not repair. Both instrument controls must pass or the run is inconclusive, not a finding. |
| **C6. Baseline disposition** (`CONVERGENCE-BASE-v1`) | It does not resolve on the remote and its pins do not match `HEAD`; `check_baseline_manifest.py` is correctly fail-closed red. **Do not regenerate a substitute and do not re-sign** (DIR-D3). Produce a one-page disposition: what the accepted subject was, why the ref is unreachable, and the two or three options. | This returns to leadership as a decision, not a fix. |

**Lease:** `benchmarks/ladder/`, `tools/linters/`, `tools/diagnostics/`,
`justfile`, `.github/workflows/`, `test/{contracts,benchmarks,lab}/`,
`test/{__init__,conftest}.py`, execution docs, generated knowledge.
Hand `packs/code-default/presets.json` to A before A2 starts.

**Exit:** C1 accepted on mutation-proven denials; C2 protocol built and its
tripwire demonstrated denying; C3 landed with the red control; C4 green; C5
packet retained; C6 disposition returned.

---

## Part III — Rules that did not change

Do not read the autonomy grant as a relaxation of any of these.

1. **Never weaken, narrow away, or delete an existing check.** If a check is
   noisy, narrow it and prove it still reds on the original defect.
2. **Mutation proof for every adversarial assertion.** Revert the guard, show
   the red, restore. A green suite over an unwired control manufactures false
   assurance, which is worse than no control.
3. **RUN-12: zero provider calls, zero USD.** `lam-engine` and `llama-cpp` only.
   Ollama is forbidden repo-wide. A credential's existence is not authority.
4. **RUN-13 stays open.** No repair site is named by this directive. Attribution
   is evidence; it is not a lease.
5. **Leases are exclusive.** Zero file-level overlap. A defect needing another
   stream's file is a **lease transfer**, never a concurrent patch.
6. **Kernel delta zero; TCB ceiling 1438.** Invariant N-06: no `subprocess`
   import in `runtime/`. Boundary lattice unchanged.
7. **Byte-for-byte rollback** on every iterative repair loop that exhausts.
8. **Honest status reporting.** Report the commands you actually ran. Never
   claim `PASS` for an unexecuted command. Never `|| true`.
9. **LDA: delta-index only.** Never rebuild the index. Check
   `source_head_sha` binds the current `HEAD` before trusting a packet.
10. **No new Markdown under `docs/`.** Findings go into the existing canonical
    files via the Senior, or into your task handoff.

---

## Part IV — What I am explicitly not doing

Named so nobody infers authorization from silence.

- **No paid run, no freeze, no T-26, no T-27.** Control stays UNFROZEN.
- **No M-8 / M-9 / M-10 movement.** FH-1 stays a proposal. T-129 still owns
  package admission.
- **No delegation, no topologies, no MCTS, no critic swarms, no learned
  routing.** All post-control, all still deferred. Do not build a second agent
  loop; there is exactly one `EpisodeEngine`.
- **No memory or skills product wiring yet.** It is the next framework priority
  after control, not a concurrent one.
- **No re-signing, no substitute baselines, no historical evidence mutation.**
- **No score claim of any kind.** Mechanism presence is not acceptance, and it
  will not become acceptance during these two weeks.

---

## Part V — For the Senior: transfer into `main/`

I have written nothing into canonical law. These are the transfers:

| Decision | Destination | Shape |
|---|---|---|
| D-1 two-stream split | `tasks.md` active table | Remove `requires:` edges that route capability rows through T-27/T-26/T-51. |
| D-2 denial-based Q-01 | `spec.md` DIR-1 / Q-01 | Amend the acceptance predicate; add the "gate coverage ≠ corpus integrity" separation. |
| D-3 Sealed Holdout Protocol | `spec.md` Q-01 | Replace the physical-custody clauses with commitment + tripwire + key-custody role separation. Unblock T-51's build; keep its freeze blocked. |
| D-4 LTB | `spec.md` new clause + `technical.md` | Capture contract, redaction-as-policy rule, replay guarantee. |
| D-5 local-model diagnosis | `spec.md` RUN-12/RUN-13 annotation | Clarify that local GGUF inference is not a provider call. Keep RUN-13 open. |
| D-6 inference accounting | `spec.md` new delta + `tasks.md` | Preset key split, `MeteredModelPort`, declared-vs-effective turns. Mark `BLOCK-T26`. |
| D-7 turn economics | `tasks.md` T-75/T-76/T-78/T-83b + new B3 row | Move all to READY; add the parallel-observation row as an authorized domain delta. |
| D-8 gate + review | `tasks.md` T-132 + session rules | Mutation harness mandatory; Director review narrowed to the four escalation classes. |
| D-9 autonomy | `tasks.md` session rules | Stream-level leases, two-week horizon, no per-leaf permission. |

Flag back to me immediately if any transfer would contradict a clause I have not
read. The canonical document wins over this directive every time — that is the
precedence ladder working, not a conflict.

---

## Appendix — Evidence register

Verified at `HEAD 4db1f758`, clean tree. Cited so nobody has to re-derive them.

| # | Finding | Evidence |
|---|---|---|
| E-1 | Product tool surface is 5 verbs | `agency/manifests/vg-code-balanced/manifest.json` |
| E-2 | One action per turn, structurally | `agency/episode/state.py:87` (`action: str \| None`) |
| E-3 | `IndexPort` is a regex definition scan | `adapters/stores/repo_index.py:29` (`_DEFINITIONS`) |
| E-4 | LDA graph unused by product: 63,514 `calls`, 11,752 `tests`, 10,260 py symbols | `uv run lda doctor --json` |
| E-5 | No `str_replace` anywhere | `grep -rn str_replace vanguard/ packs/` → 0 hits |
| E-6 | **Partly wrong, corrected by measurement.** `tokens` did carry both meanings, but the compiler ceiling never bound, because the governor ceiling was never debited. Now split and both enforced. | probe + `test_inference_accounting` |
| E-7 | **Confirmed, and it was the whole defect.** The model call bypassed the governor; every preset overran its declared token *and USD* ceilings by 1.6–4x with no denial. Fixed. | `agency/episode/engine.py:447`; measured table in D-6 |
| E-8 | `just verify` covers ~947 / ~3,171 tests; excludes `test/benchmarks` and `test/falsifiers` | `tasks.md` T-132 row; `justfile` |
| E-9 | ~6 modules fail at import | `setuptools`; `lab.m65_study`; `lab.m701_independence`; `adapters.models.ollama` |
| E-10 | `check_doc_budgets` red on `main`, 5 owner-held docs | `milestones.md` §"Still failing" |
| E-11 | `CONVERGENCE-BASE-v1` unreachable; verifier correctly fail-closed red | prior-session attribution; DIR-D3 forbids re-signing |
| E-12 | `packs/code-default/planners/single_planner.py` reserves a Governor lease it never commits or releases | `single_planner.py:75-79` — **unverified whether this plugin is on any live path** (`plugins/planner.yaml` declares it; `session.py` does not appear to load it). B: confirm dead or fix the leak; do not assume. |

E-6, E-7 and E-12 are the ones I would want a second pair of eyes on before they
become law. Everything else I read directly.

**Scope note, updated.** E-6 and E-7 were read from source when first written.
They have since been executed: the probe in D-6 ran real episodes through the
public entrypoint, and it corrected E-6. The measurement won, as it should have.

**Stream A no longer owns A2** — it is landed. A's sprint is A1 (exact edit),
A3 (local-model write-landing) and A4 (evidence identity). A should still review
the inference-accounting change as an independent reviewer, and in particular
re-derive the preset calibration on a large workspace: my prompt measurements
come from a synthetic 80-file tree, and a real repository will compile larger
L5 evidence. If `context_window_tokens` turns out to be too tight there, that is
a calibration change, not a design change.
