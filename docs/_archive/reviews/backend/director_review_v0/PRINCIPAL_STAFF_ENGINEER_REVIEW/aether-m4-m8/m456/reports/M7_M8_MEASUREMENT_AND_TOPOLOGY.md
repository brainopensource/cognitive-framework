# M-7 / M-8 — Measurement, Bounded Concurrency, and Explicit Topologies

**Class:** engineering plan (non-normative — neither milestone is authorised)
**Date:** 2026-08-24
**Prerequisite:** M-6 closed via ADR-0090

---

## 0. Foundation performance work completed in this wave

Both fixes share one root cause: **every turn re-carries and re-canonicalises
byte-identical context layer bodies.** Measured against the real trajectory
shape dumped from `test_lam_runtime_vertical` (L2 tool-schema block = 5,926
bytes, identical on every turn).

| axis | before | after | factor |
|---|---|---|---|
| RAM — 50 turns retained | 304,390 B | 27,609 B | **11.0×** |
| CPU — 200-turn canonicalisation | 135.3 ms | 11.4 ms | **11.9×** |
| Cold start — `adapters.models` import | 140.8 ms | 12.9 ms | **10.9×** |

`context_store.py` interns layer bodies by digest **and** memoises the digest
computation, so one store fixes both axes. `turn_digest()` hashes refs, not
bodies. The store is append-only within an episode and never evicts — replay
correctness depends on every referenced digest remaining resolvable.

The cold-start fix is PEP 562 lazy attribute access in
`adapters/models/__init__.py`. `ollama` eagerly pulled `urllib → http.client →
email.parser` (~106 ms) on every process start, including `local`-profile runs
that never touch it. Verified: `urllib.request` is absent from `sys.modules`
after importing `FakeModel`, all names still resolve, and the full repository
suite is **unchanged at 1294 passed / 8 failed** — identical to the
pre-change baseline, so this is a pure win with no behavioural delta.

**Replay fidelity is preserved.** The digest *is* the identity the trajectory
already carried via `prefixDigest`; interning changes representation, never
meaning. `rehydrate()` returns byte-exact content.

---

## 1. M-7 — measure first, then decide

`milestones.md` is explicit: I-11 sequential execution remains mandatory until
M-7 measurement **and** an explicit Director lift. The gate is an *accepted
measurement ADR*, not a concurrency feature.

The ordering is not bureaucratic. Concurrency changes what "exactly-once
settlement" means. If both land together, neither is falsifiable: a duplicate
effect could be a scheduler bug or a recovery bug, and there is no baseline to
attribute it to.

### 1.1 Deliverable A — reproducible sequential baseline

Before any scheduler exists, publish a fixed-seed baseline over a fixed task set:

```
per-task: wall_ms, model_ms, tool_ms, idle_ms,
          turns, tokens_in/out, cache_hit_rate, usd_micros,
          critical_path_ms, contention_ms (0 by construction)
```

`cache_hit_rate` is called out deliberately. The Claw-SWE-Bench harness study
reports it as a **diagnostic field for cost accounting, not a measure of
capability** — cost is jointly affected by model price, token counts, cache
policy, and adapter call path. Baseline it now or cost comparisons later are
uninterpretable.

### 1.2 Deliverable B — the independence analysis

Concurrency is only safe where effects are genuinely independent. Derive
independence from the **selector algebra already in the manifests**, not from
intuition:

```
independent(a, b) ⟺ selector_disjoint(a, b)
                  ∧ sink(a) ≠ privileged ∨ sink(b) ≠ privileged
                  ∧ no shared idempotency key
```

Two `fs.read` calls on disjoint paths are independent. Two `patch.apply` calls
on the same file are not. Publish the measured fraction of independent pairs in
the baseline — **if it is small, M-7 is not worth doing**, and that is a valid
and valuable outcome.

### 1.3 Deliverable C — the decision ADR

Must state: measured speedup ceiling given the independent fraction, contention
cost, the leasing protocol, and the exact conditions under which I-11 is lifted.
Only the Director may lift it.

### 1.4 Non-negotiable

RF-25 cold continuation must stay green **under** concurrency. At-least-once
execution with idempotent settlement, never an exactly-once illusion.

---

## 2. M-8 — topologies as composition, not engine code

The claim: debate, critic/reviser, planner/executor/verifier, and bounded tree
search are expressible as **manifest configuration**. The gate (RF-65) is zero
kernel and zero episode-engine diff across at least three topologies.

```json
{ "api": "mhf.topology/1", "id": "critic-reviser",
  "roles": [
    {"id":"author", "pack":"vg-code-default",  "authority":["fs.read","patch.apply"]},
    {"id":"critic", "pack":"vg-code-explain",  "authority":["fs.read"]}
  ],
  "sequence": [
    {"role":"author", "until":"proposal"},
    {"role":"critic", "until":"verdict", "input":"@author.proposal"},
    {"role":"author", "until":"terminal", "input":"@critic.verdict", "maxRounds":3}
  ]}
```

**This is static addressing, not a runtime DAG.** `sprint_active.md` §2 is firm:
the graph is composition, never a runtime workflow engine. `sequence` is
resolved at freeze time into role-attributed episodes that the *existing*
sequential engine runs. If a topology needs runtime scheduling, it belongs in
M-7, not M-8.

Roles get **attenuated authority via the M-6 algebra** — the critic is read-only
because `attenuate()` denies it `patch.apply`, not because the prompt asks
nicely. M-8 is where M-6 pays for itself.

---

## 3. On competing with Codex CLI / OpenCode on SWE-bench Pro

An honest read of the current literature, because strategy built on a wrong
premise wastes a year.

### 3.1 The harness is worth a few points; the model is worth tens

From the harness survey's SWE-bench Verified table, same model across scaffolds:

| model | scaffold | score |
|---|---|---|
| Claude Opus 4/4.5 | mini-SWE-agent | 76.8 |
| Claude Opus 4/4.5 | OpenHands + CodeAct 2.1 | 77.6 |
| Claude Opus 4/4.5 | vendor scaffold | 80.9 |

**~4 points of spread from scaffolding.** Meanwhile model generation moves it far
more. DeepSWE deliberately *holds the harness fixed* under mini-swe-agent so the
leaderboard reflects model capability rather than scaffolding — the field treats
scaffold variance as a confound to eliminate, not a lever to pull.

**Implication: AETHER will not out-score Codex CLI by scaffolding alone.**
A superior harness on a weaker model loses to a plain harness on a stronger one.
Plan accordingly: harness quality is a multiplier on model access, not a
substitute for it.

### 3.2 Where DeepSeek Harness and AETHER actually converge

DeepSeek Harness's stated core idea is **plug-in composability — tools, skills,
sessions, and even entire agent harnesses like Claude Code or Codex mixed,
matched and swapped**. That is the same thesis as AETHER's pack/SPI model, and
it validates the architectural direction independently.

Note also that DeepSeek's own agent-benchmark numbers were produced using the
minimal mode of their harness, which makes the published result **a
model-and-harness result**, with independent reproduction limited until the
harness is released. That is precisely the confound AETHER's attributable
evidence is designed to eliminate.

### 3.3 The defensible differentiator

Not raw score. **Attributability.** No mainstream harness can currently produce:

* a signed, exterior verdict bound to a preregistered oracle;
* a replayable trajectory with conserved cost and explicit measurement status;
* cold reconstruction proving no settled effect was repeated;
* per-row evidence states (`absent` / `invalid` / `unverifiable` / `present_valid`)
  instead of a single pass/fail.

The benchmark audit literature scores papers poorly on exactly this: pinned
dataset version, grader version, partial-credit policy. **AETHER's `D_R` +
event range + signed verdict is a pinned, reproducible run identity by
construction.** That is a real and currently unmet market gap.

### 3.4 Recommended framing

Target **reproducibility-grade SWE-bench**: publish scores *with* a verifiable
evidence bundle per instance, so a third party can replay the exact run. Compete
on "you can verify our number," not "our number is bigger." The T0 memo from M-5
also gives a genuine cost story — cache-equivalent savings on repeated
obligations, measurable via the `cache_hit_rate` field baselined in §1.1.

---

## 4. Sequencing

| step | gate |
|---|---|
| ratify ADR-0090 | M-6 closed |
| wire `context_store` into the live trajectory path | perf fix reaches production |
| tag `M-5-BASE`, wire RF-86 zero-diff into CI | M-5 gate live |
| publish M-7 sequential baseline + independence fraction | M-7 decision ADR |
| Director lift of I-11 (only if the fraction justifies it) | M-7 authorised |
| topology schema + three reference topologies | M-8 / RF-65 |

**Do not start M-8 before M-7's baseline exists.** Topologies change the cost
profile, and without a sequential baseline you cannot tell a topology win from a
scheduler win.

---

## 5. M-7 Deliverable B — independence analyser (built, with a caveat)

`runtime/independence.py` derives independence from the manifest selector
algebra. Fail-closed by construction: unknown selector kinds and network
wildcards are treated as **overlapping**, because wrongly calling two effects
disjoint admits a write race while wrongly calling them overlapping only costs
speed.

```
independent(a,b) <=> selector_disjoint(a,b)
                 AND not (privileged(a) and privileged(b))
                 AND no shared idempotency key
```

Scanned against real packs:

```
### repo packs (code-explain)          fraction  0.0%  -> M-7 NOT justified
### formal-default                     fraction 66.7%  -> MAY be worth measuring
```

### 5.1 Why these numbers are NOT the M-7 decision input

This is **static capability-level** analysis. Two `fs.read` capabilities both
declare `root: /workspace`, so they overlap statically — yet at runtime they
read *different files* and would be genuinely independent. The static figure is
therefore a **pessimistic lower bound**, not the real fraction.

Two further limitations, stated so nobody mistakes this for the answer:

* the scanner reads JSON manifests only; `vg-code-default` declares its
  capabilities in `harness.yaml` and was **not** included in the scan above;
* capability-level pairs are not effect-instance pairs, and only the latter
  carry concrete paths.

**The real M-7 number must come from runtime effect instances captured during
the §1.1 sequential baseline**, where each `EffectRef` carries the concrete
resolved path rather than the declared root. The analyser is the correct
instrument; it is currently pointed at the wrong data. Feeding it the baseline's
effect log is the next step and requires no new code — only `EffectRef`
construction from ledger `EffectStarted` payloads instead of from manifests.

Until that exists, **no concurrency decision should be made.** A 0.0% static
reading is not evidence against M-7; it is evidence that the measurement has not
been taken yet.
