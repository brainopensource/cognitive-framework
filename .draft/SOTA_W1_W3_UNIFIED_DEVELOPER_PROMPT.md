# SOTA-W1..W3 Unified Developer Prompt — Build Lane / Measurement Lane Re-Cut

Subject: `ca47eef7da1b4075f8a69d238fe1626fa1ab4c8e` (re-audit; do not trust this SHA blindly)
Program of record: `.draft/VANGUARD_SOTA_BACKEND_COMPLETION_PROGRAM_2026-08-31.md`
Canonical status owners: `docs/execution/active.md`, `milestones.md`, `backlog.md`

---

## 0. Authorization Delta (read first — this supersedes prior refusals)

Two things changed since the last SOTA-W1 handoff. Both are explicit operator
decisions, not inferences you may re-derive or re-litigate.

### 0.1 Spend authorization — GRANTED

```
AUTHORIZED_BUDGET_USD   = 0.15
AUTHORIZED_PROVIDER     = OpenRouter
CREDENTIAL              = OPENROUTER_API_KEY in ./.env   (never print, log, or commit it)
AUTHORIZED_MODELS       = deepseek/deepseek-v4-flash-0731   ($0.14/M in, $0.28/M out)
                          z-ai/glm-5.3-flash               ($0.10/M in, $0.20/M out)
SCOPE                   = SOTA-04 live execution + SOTA-08 internal-easy campaign
                          + bounded research/probe calls
NOT AUTHORIZED          = SWE-Bench Pro 30-task pilot, DeepSWE, official SWE-bench
                          Verified, any frontier-model call, any campaign > $0.15
```

This is a **separate, frozen budget**. It does not extend the pre-existing
`$0.10` W-092 validation ceiling and does not merge with it. Track it in its own
ledger. Hard-stop at the first of: `$0.15`, `300,000` tokens, `120` calls.

Working headroom, for planning only: at a typical 8K-in/1K-out call,
DeepSeek V4 Flash costs `8000·0.14/10⁶ + 1000·0.28/10⁶ = $0.00140` → ~107 calls.
GLM 5.3 Flash costs `$0.00100` → ~150 calls. You are not token-starved; you are
call-starved. Spend calls on *measurement*, not on exploration you can do offline.

**Unknown usage is not zero.** If a response omits `usage`, charge the call at
the model's max context price and block further paid calls until reconciled
(this is the existing `SOTA-07` fail-closed rule; apply it now).

### 0.2 Wave re-cut — MANDATED

The three-wave program is retained in substance but re-cut along the build/claim
seam. The old sequencing was unsatisfiable: `SOTA-04` (claim) gated W2, `SOTA-08`
(claim) gated W3, and `FIN-A1` requires an independent acceptor the producer
cannot be. You are hereby authorized to proceed on the **build lane** without
waiting for measurement-lane acceptance.

```
BUILD LANE   (authorized now, run to completion, no live provider dependency)
  SOTA-01 → SOTA-02 → SOTA-03 → SOTA-05 → SOTA-06 → SOTA-07 → SOTA-09 → SOTA-10 → SOTA-11

MEASUREMENT LANE (fires when its own preconditions hold; never blocks the build lane)
  SOTA-04  ← unblocked NOW by §0.1
  SOTA-08  ← internal-easy/average rungs unblocked NOW; Pro pilot NOT authorized
  SOTA-12  ← still blocked: needs external-run authorization + independent acceptor
```

Invariant preserved: **a build-lane package may be `TECHNICAL COMPLETE`; only a
measurement-lane receipt may move a milestone gate.** M-8 stays `BLOCKED`,
M-9/M-10 stay `UNAUTHORIZED`, until their own predicates are satisfied by
accepted receipts. Building W2/W3 mechanisms does not close them and you must
never imply it does.

Your first documentation act is to record this re-cut in `active.md` (lane
tables + a `SOTA build/measurement lane` section) so the next agent does not
re-derive the old deadlock.

---

## 1. Mandatory Entry Sequence

Non-negotiable, in order:

1. Read `AGENTS.md`. Follow its mandatory sequence exactly.
2. Inspect `context_summary`; run `lda doctor` and `lda context`.
3. Reverse-route every production file you intend to touch; pin affected
   symbols, callers, and tests. Use the `lda-navigator` skill.
4. Read, in this order: `docs/execution/active.md`, `milestones.md`,
   `backlog.md`, then `.draft/VANGUARD_SOTA_BACKEND_COMPLETION_PROGRAM_2026-08-31.md`.
5. Read as **non-canonical design input only** (they are not source owners):
   - `docs/reports/reviews/electroweak_v092/BACKEND_GUIDELINES_BRIEFING.md`
   - `docs/reports/reviews/electroweak_v092/BACKEND_SUGGESTED_DEVELOPMENT.md`
   - `docs/reports/reviews/electroweak_v092/back/` (dormant prototypes — re-derive, never copy)
   - `.draft/CODING_AGENTS_BENCHMARK_ARCHITECTURE_AND_FUTURE_GUIDE_2026-08-31.md`
   - `.draft/SOTA_AGENTIC_CODING_HARNESS_ENGINEERING_TREATISE.md`
6. Re-audit HEAD. If HEAD ≠ the subject SHA above, record the real SHA and
   re-verify every claim in §0.2 before proceeding.

Preservation rules: **do not modify frontend files**; preserve all unrelated
dirty CLI/client changes (`vanguard/clients/**`). This is backend completion.
Expose stable client contracts; do not rewrite the CLI/TUI.

---

## 2. Theory and Measurement Contract

Everything in the measurement lane must implement these definitions exactly.
Preregister every constant **before** the first live call, in a
content-addressed file, and never tune them afterward.

### 2.1 Outcome variable

For a frozen task set `T = {t₁..tₙ}` and arm `a`, each task yields a binary
outcome from the **exterior evaluator only** (never from the model's self-report):

```
y_a(tᵢ) ∈ {0, 1}          1 iff the exterior evaluator admits the postimage
p̂_a    = (1/n) Σᵢ y_a(tᵢ)   observed success rate
```

Any task whose evaluator verdict is unavailable, timed out, or ambiguous is
`MISSING`. **`MISSING` is never a 0 and never a 1.** Report `n_evaluated` and
`n_missing` separately; a denominator that silently absorbs missingness is a
falsified run.

### 2.2 Confidence — Wilson score interval

Never report a bare proportion. For `p̂` on `n` evaluated tasks at `z = 1.96`:

```
        p̂ + z²/2n  ±  z·√( p̂(1-p̂)/n + z²/4n² )
CI  =  ─────────────────────────────────────────
                    1 + z²/n
```

At `n = 20`, `p̂ = 1.0` gives `CI ≈ [0.839, 1.000]`. State that. A 20/20 result
is **not** evidence of ≥ 84% true capability — it is evidence the lower bound is
0.839. Write the interval into every receipt.

### 2.3 Lift — paired McNemar, not two independent proportions

Control and treatment run the **same** tasks, so outcomes are paired and the
two-proportion z-test is invalid. Build the discordance table:

```
            treatment=1   treatment=0
control=1        a             b        (b = treatment lost)
control=0        c             d        (c = treatment gained)

Δ̂ = (c − b) / n                      point estimate of lift
Exact test: under H₀, c ~ Binomial(b+c, 0.5)
  p = 2 · P(X ≥ max(b,c))  for  X ~ Bin(b+c, 0.5)
```

The canonical threshold `Δ ≥ 0.05` is an **effect-size floor, not a significance
claim**. A run satisfies the M-8 lift gate only when *both* hold:
`Δ̂ ≥ 0.05` **and** the exact McNemar `p < 0.05`.

**Power warning you must record honestly:** with `n = 30` and a plausible
discordant rate `b + c ≈ 6`, power to detect `Δ = 0.05` is under 0.15. A
non-significant result at this `n` is **`UNDETERMINABLE`, not a negative**. Say
so in the receipt. Never report "no lift found" when the design could not have
found it.

### 2.4 Cost-adjusted success

Preregister `λ` (USD per unit of success) before running. Do not fit it afterward.

```
c̄_a = (total USD for arm a) / n_evaluated
U_a = p̂_a − λ · c̄_a
```

A parallel or specialist treatment ships **only if** `U_treatment > U_control`
under the preregistered `λ`. This is the `SOTA-09` / `CMX-06` / `BEP-04`
admission rule; it is not renegotiable after seeing results.

### 2.5 Kill criterion (retained, not exercisable under this budget)

The 30-task SWE-Bench Pro pilot remains a falsifier of the flash-primary 75%
path at `≤ 2/30`. Under `H₀: p = 0.75`, `P(X ≤ 2) ≈ 3·10⁻¹³` — the test is a
valid falsifier. **This pilot is NOT authorized under the current budget.** Do
not run it, do not approximate it with internal tasks, and do not report any
internal proxy as a Pro result.

### 2.6 Budget attenuation (existing invariant — re-verify, do not redesign)

For any parent→child delegation:

```
A(B_parent, B_child):  B_child ≤ B_parent − spent(parent)     (monotone non-increasing)
                       caps(B_child) ⊆ caps(B_parent)          (authority never widens)
```

Escalation may increase *compute* monotonically; it may never widen filesystem,
network, command, evaluator, or child authority. This is the `SOTA-07`
escalation rule and the `DEL-01` gate. Add a falsifier if one is missing.

### 2.7 Routing decision (SOTA-07 — extend, never re-implement)

Extend the existing `RouteDecision` / `RoleAwareRouter` / `TierLadder` path.
Do not create a second router.

```
select(role, complexity, failure_class, health, budget_remaining):
    C = { m ∈ registry
          : price_known(m)                      # unknown price ⇒ excluded, fail closed
          ∧ id_resolved(m)                      # invented IDs are a hard error
          ∧ healthy(m)
          ∧ band(m) ≤ max_band(role)
          ∧ est_cost(m, complexity) ≤ budget_remaining }
    if C = ∅: raise RoutingClosed(reason)       # never silently downgrade
    return argmax_{m ∈ C}  expected_utility(m, role, complexity, failure_class)
```

`google/gemini-3.7-flash` stays **unavailable** unless live provider metadata
supplies an exact ID and price — verify via the OpenRouter models endpoint
(§4.1), do not assume. Record the provider-resolved model behind
`openrouter/free`; an unresolved alias may not carry a capability claim.

---

## 3. Build Lane — Implementation Order

Run these to completion. None requires a provider call. Each package ends with:
targeted LDA-selected falsifiers → affected subsystem suites → boundary/TCB
linters → `just check` → regenerated knowledge → `just verify`.

### SOTA-01 — Truth reconciliation and activation falsifiers
1. Add **real `HarnessSession`** activation falsifiers for BEP-01..03 (not mocks):
   foreign task/composition receipts, cold recovery-budget persistence, dialect
   failure cases, and the task-digest fallback asymmetry.
2. Remove `vanguard/packages/runtime/canonicalization.py` and its runtime-root
   re-export. Fix the benchmark canonicalization boundary **without laundering a
   forbidden import**. Amend the boundary rule only if the canonical client
   contract genuinely requires it, and cover the change with byte-identity tests.
   No compatibility shim may bypass the boundary linter.
3. Mark `OPEN-2` as `DONE` (observation digests are already non-placeholder).
4. Remove duplicate outbound alias schemas; retain inbound alias resolution.
   Falsifier: outbound tool list contains exactly one schema per canonical verb.
5. Rename the internal `CMX-07` `SWE-BENCH-M4` row so it can never be mistaken
   for an official task.

### SOTA-02 — Completion-aware convergence
State machine over an episode with admissible completion evidence:

```
on_verification_success(state):
    if not admissible_completion(state): return CONTINUE
    state.redundant += 1
    if state.redundant == 1:
        return INJECT_TYPED_COMPLETION_FEEDBACK      # "work verified; call agency.finish"
    if state.redundant >= 2:
        return RESTRICT_TOOLS({agency.finish, fs.read, fs.search})
    # never auto-finish; never synthesize a finish call
on_budget_exhausted_without_finish(state):
    return ABANDONED                                  # retained, not softened
```

Critical falsifier: an oracle-green repeatedly-verifying episode converges to a
**model-requested** finish, and a model that still refuses still yields
`ABANDONED`. Fabricated completion is a hard failure.

### SOTA-03 — Official benchmark protocol bridge
Normalized task/submission/`aether.benchmark.receipt/1` contracts (extend
`benchmarks/protocols.py`), isolated evaluator adapters, exact-subject receipts,
hermetic fixtures for SWE-bench Verified, SWE-Bench Pro, DeepSWE v1.1.
Orchestration consumes existing runtime/port seams only — no new runtime, store,
coordinator, tool broker, or evaluator anywhere in this program.
Falsifiers: dry-run emits null empirical values with reasons; the receipt
rejects an altered task, split, patch, model, harness, or evaluator identity.

### SOTA-05 — Long-context identity and retrieval
Add selection-policy identity and resume-time repository/index drift validation
to existing `ContextPacket` flows (new fields optional and backward compatible;
legacy packets may replay but cannot support new capability claims).
Prove all **seven compaction invariants** survive: constraints, next action,
modified resources, last material failure, latest verification, settled effects,
remaining budgets. Add section-addressed large-file retrieval with
path/range/preimage identity; prove a 10,000-line file is handled via a relevant
~40-line section inside budget, with stable-prefix accounting.

### SOTA-06 — Multi-file patch/resume hardening
Falsifiers for stale preimages, partial hunks, ambiguous anchors, path escape,
duplicated settled effects, external workspace drift, and cold-resume
continuation. Patch anchors must reject drift rather than apply fuzzily.

### SOTA-07 — Multi-model economy and escalation
Implement §2.7. Extend `RouteDecision` **additively**: trigger, parent
episode/state digest, budget snapshot, provider-reported usage status, resolved
model identity. Escalation creates attributable linked child episodes preserving
task/state/context identity under §2.6 attenuation. Add provider-usage
reconciliation: unknown usage or price blocks further paid calls. Validate every
active registry entry against live provider metadata (§4.1) — never invent an ID
or a price.

### SOTA-09 — Qualified coordination scheduler
Qualify the **existing** topology/workflow scheduler: durable ready-state
reconstruction, deterministic fairness, bounded leases/backpressure,
cancellation, bounded joins, cold resume, no duplicated effects. Sequential
remains the control. Parallel treatment ships only under §2.4.
Falsifier: scheduling never exceeds declared concurrency and resumes without
duplicate effects.

### SOTA-10 — Agent-builder integration
Unify the existing canonical manifest path, `CompositionRegistry`,
meta-controller, and signed skill lifecycle into one backend agent-builder
service. Child variants are immutable, digest-addressed compositions. Controller
stays default-off and cannot widen authority, budgets, or evidence eligibility.
Promotion/rollback retain separated authorities.
Falsifiers: promotion and rollback reject self-evaluation, stale bases, replay,
and forged signatures.

### SOTA-11 — Hermes / Research / Tutor compositions
`hermes-on-vanguard` as a pack/composition over the **same** `Runtime.compose`
path as Coding Max, targeting the public capability surface of the MIT-licensed
Hermes Agent. Qualify Research (explicit egress) and Tutor (read-only default
authority) through the same public framework contract. Do not copy in another
runtime, store, coordinator, tool broker, or evaluator.

---

## 4. Measurement Lane — Live Execution Protocol

### 4.1 Provider preflight (spend ~$0.00; do this first)
```
GET https://openrouter.ai/api/v1/models     # free, unmetered
```
Resolve and record exact IDs, context lengths, and per-token prices for both
authorized models. Reconcile against `benchmarks/baac/lib/budget.py`. Record
what `openrouter/free` currently resolves to. Any registry entry whose ID or
price is not confirmed here is marked `UNAVAILABLE` and excluded by §2.7.

### 4.2 Preregistration (before any paid call)
Freeze, content-address, and commit: task set membership and digests, arms,
`max_attempts`, `λ`, thresholds, the evaluator, and the stop rule. The manifest
digest is fixed **before** live execution. Invalid or unavailable tasks may
count as neither a pass nor a failure.

### 4.3 SOTA-04 — CMX-06 / CMX-07 / FIN-A1 live execution
Order: structural dry-run preflight → frozen canary verification
(`benchmarks/m8_heldout/canary.py --preflight`, which fails closed on any
drift) → live run via `benchmarks/m8_heldout/runner.py --mode live` with the
injected official runtime executor and exterior evaluator.

CMX-06 preregistration is fixed at one attempt per arm, and treatment
cost-adjusted success must be **no worse** than control (§2.4).

Emit a producer-signed exact-subject FIN-A1 bundle. **You cannot accept your own
bundle.** Produce it, sign it, and stop; record the disposition as
`AWAITING_INDEPENDENT_ACCEPTANCE`. A negative or undeterminable M-8 result is a
valid scientific result, is recorded honestly, and does **not** unlock M-9.

### 4.4 SOTA-08 — internal campaigns (partial authorization)
| Rung | Task set | Target | Status under this budget |
|---|---|---|---|
| B1 | 20 frozen internal easy | 20/20 | **AUTHORIZED** |
| B2 | 30 frozen internal average | ≥ 27/30 | **AUTHORIZED if budget remains** |
| B3 | 30 internal hard | 60% research target | NOT AUTHORIZED (budget) |
| B4/B5 | official SWE-bench / Pro / DeepSWE | reproducible, no promised score | NOT AUTHORIZED |
| B6 | competitor / Hermes / Claude Code | matched protocol only | NOT AUTHORIZED |

Run B1 first. Stop and report if it does not pass — do not spend the remaining
budget on B2 against a failing B1. Do **not** tune thresholds or task membership
after seeing results; that voids the run and you must record it as void.

Run the harness-vs-model ablation with identical tasks, model, attempt policy,
and budget across arms. Any comparison that differs in model is a **product**
comparison, not harness lift; disclose the difference explicitly.

### 4.5 SOTA-12 — remains blocked
Requires explicit external-run authorization **and** an independent acceptor.
Deliver a backend-complete candidate and retain the milestone blocker. Do not
mark M-9 or M-10 accepted. Do not claim SOTA, Claude Code superiority, or Hermes
superiority.

---

## 5. Live-Call Discipline

```
before_each_paid_call(ledger):
    assert ledger.usd   + est_cost  <= 0.15
    assert ledger.calls + 1         <= 120
    assert ledger.tokens+ est_tokens<= 300_000
    assert model in AUTHORIZED_MODELS and price_known(model)

after_each_paid_call(resp, ledger):
    if resp.usage is None:
        ledger.charge_max(model); ledger.block_paid_calls("usage missing")
    else:
        ledger.charge(resp.usage)
    ledger.append(call_id, model_resolved, tokens_in, tokens_out, usd, latency_ms)
```

Persist the ledger to disk after **every** call so a crash cannot lose spend
accounting. Report the final ledger verbatim.

Never send repository secrets, `.env` contents, or credentials in a prompt body.

---

## 6. Definition of Done

Per package: current-source unit and integration tests pass; boundary and TCB
gates green; cold reconstruction tested where state changed; canonical docs and
generated knowledge synchronized; every capability or performance claim backed
by an exact-subject receipt.

Per program, run and report: targeted LDA-selected falsifiers, affected
subsystem suites, architecture/security linters, `just docs-knowledge`, Markdown
link and stale-path checks, `just check`, `just verify`.

Known environment blockers — report as blockers, do not fake around them:
- boundary check blocked by a pre-existing frontend import cycle
- `just` may not be installed (install it or report the exact substitute commands run)
- evaluator-daemon tests blocked by sandbox Unix-socket permissions

Synchronize `active.md`, `backlog.md`, `milestones.md`, and the SOTA program
draft with observed results. `active.md` must end the session recording: the
build/measurement lane re-cut, the frozen $0.15 ledger and its outcome, exact
dispositions per package, and the unchanged M-8 `BLOCKED` /
M-9 `UNAUTHORIZED` / M-10 `UNAUTHORIZED` gates.

## 7. Final Report Format

Report exactly, and honestly: every command run and its result; each package's
disposition; benchmark protocol, model, resolved model ID, cost, tokens,
latency, attempt count, evaluator, and subject SHA; the Wilson interval on every
proportion; the McNemar table and exact p on every lift claim; `n_evaluated`
versus `n_missing`; the final spend ledger; and every gate that remains closed
with the exact predicate that closes it.

If a result is negative or undeterminable, say so plainly. A recorded negative
is a successful session. A fabricated green is a failed one.
