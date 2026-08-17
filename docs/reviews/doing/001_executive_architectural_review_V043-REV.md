# 001 — Executive Architectural Review, Aether Vanguard v0.4.3

**Classification:** Internal engineering + programme review. NON-NORMATIVE.
Not in `docs/main_v4/00_vanguard_registry_v040.md` Ch. 2. Where this file and a v4 owner
disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16
**Branch / HEAD:** `sprints7-8/integration` @ `0238b1a`
**Reviewer stance:** Principal architect + tech lead, adversarial. My job here is to find
what would cost us a rewrite in six months, not to certify what already works.
**Companion documents:** `002`–`008` in this directory. This one is the ruling; the others
carry the evidence and the remediation.

---

## 0. The ruling, in one page

**The foundation is genuinely good. The product built on it is not the product the foundation
describes. And a meaningful fraction of the delivered "evidence" measures nothing.**

Three sentences that summarise 15,569 lines of runtime, 12,199 lines of test, 4,928 lines of
normative specification and ten prior review documents:

1. **The keel is sound.** The wire schemas, canonicalisation vectors, resource-selector
   inclusion algebra, kernel dispatch sequence S0–S12, attenuation, budget lease tree and
   failure taxonomy are better than anything I have reviewed at this stage of a programme.
   `vanguard/packages/kernel/dispatch.py` is close to publishable as a reference
   implementation of capability-mediated effect dispatch. **Do not touch it except to shrink it.**

2. **The cognition above the keel is a stub, and two parallel loops have grown beside it.**
   `EpisodeEngine` is explicitly depth-1 and non-recursive
   (`vanguard/packages/agency/episode/engine.py:17-19`). Recursion — the single load-bearing
   claim of the whole architecture (`GTS-13C §4.3`: *"An agent is an Episode. A team is an
   Episode that spawns Episodes"*) — is not implemented in `agency/`. Meanwhile two other
   agent loops now exist: `runtime/loops/meta_loop.py` (Sprint 9) and the benchmark runners in
   `benchmarkings/`. Both bypass the kernel entirely.

3. **A substantial share of the published-looking numbers are vacuous.** Every row in
   `benchmarkings/swe_pro_tiers/matrix_results_tier3_token_bucket.json` reports
   `"pre_passed": true` and `"patch_length": 0` — the oracle passed *before the agent acted*,
   and the agent changed nothing. One row records `turns: 1, total_tokens: 0, cost: 0.0,
   duration: 0.73s` and still scores `"oracle_passed": true`. This is `RSK-04` (measurement
   theatre) and `04.4` degenerate floors, realised exactly as the charter predicted.

**Verdict on the v0.4.3 MVP question — "can we deliver Phases 0–4 / Sprints 1–10 as a Beta
MVP of a harness-builder framework?"**

> **Not on the current trajectory, and the reason is not effort — it is that three of the four
> MVP gate questions (`GTS-13C` Ch. 10) are currently unanswerable, and one of them is
> unanswerable *because the instrument is broken*, not because the work is unfinished.**

The correct move now — and the user is right that now is the moment, at 0.1% of budget — is
**not** to push S9/S10 as planned. It is a **two-sprint consolidation** that (a) deletes the
second and third loops, (b) makes recursion real in `agency/`, (c) makes the manifest actually
determine harness behaviour, and (d) rebuilds the measurement layer so it refuses to report
rather than reporting noise. That is `008`.

---

## 1. What was reviewed, and how

| Surface | Evidence |
|---|---|
| Normative corpus | `docs/main_v4/` VG-00 … VG-12 + GTS-13C, 4,928 lines, read in full for 02/03/09/13C |
| Runtime | `vanguard/packages/**`, 93 files, 15,569 LOC, read: kernel, agency, ports, runtime root, coordination, meta-loop, compiler, manifests |
| Contracts | `schemas/v4/` — 22 schema pairs, ~40 canonicalisation triples, ~60 selector-inclusion vectors |
| Tests | `test/**`, 507 cases executed on this branch |
| Evidence | `benchmarkings/**` result JSON + reports, `lab/`, `tools/` |
| Prior review | 10 documents in `docs/reviews/done/`, 3 in `docs/reviews/done/` |
| External | 2026 literature on harness variance, compaction, verifier gaming, skill-library drift, agent protocols (cited in `002`, `004`, `006`) |

**Test suite state on this branch:** `507 tests, 2 failures, 15 errors, 2 skipped`.
14 of the 15 errors are `ReaderUnavailable: node is required` — the cross-language reader
conformance suite (`SC-7`, `T1.14`) **correctly refuses to run** rather than passing vacuously.
That refusal is a credit to the test design and a debit to the environment: `T1.14` conformance
evidence is currently unverified here. The 3 genuine failures are all in the Sprint 7 alias
translation layer (§3.4).

---

## 2. What is genuinely excellent — and must be protected

I want this on the record before the criticism, because the temptation in a remediation
programme is to churn the parts that are already right.

| Asset | Why it is rare | Protection |
|---|---|---|
| **Kernel dispatch S0–S12** (`kernel/dispatch.py`, 428 LOC) | Ordering rules are each traceable to a real shipped defect; `K-04` (resolve before lease), `K-05` (verify at point of effect), `K-06` (release before emit), `K-47` (durable intent before dispatch) are all correctly implemented, including the subtle `return`-inside-`try` note at line 253-260 | Freeze. ADR per change. TCB alarm already at 1,307/1,438 |
| **Canonicalisation + vectors** | RFC 8785 with ~40 triples including negative zero, astral emoji, UTF-16 key order, NFC-not-applied | Freeze. This is the corpus format (`L-1`) |
| **ResourceSelector inclusion algebra** (450 LOC + ~60 vectors) | Per-kind decidable relation that *denies* undefined pairs, with cross-kind vectors. This is the thing that makes `L-02` (resource-scoped authority) real rather than aspirational | Freeze |
| **Failure taxonomy → `FailurePath`** | Every exit named; `UNDETERMINABLE` preserved and never resolved (`F-22`); `inconclusive` fail-closed | Freeze |
| **Refusing instruments** | `test/contracts/readers` refuses without node; `EVALUATOR_BINDINGS` has no `FakeEvaluator` row *on purpose* (`root.py:529`) | This is the correct instinct. Extend it to `benchmarkings/` (see `002`) |
| **The specification corpus itself** | `02` and `03` are the best charter/architecture pair I have read on an agent programme. `NC-01…NC-12`, `A-01…A-12`, `FT-01…FT-17` are load-bearing and were *used* | Keep. Consolidate the review layer around it (`007`) |

**The honest summary of the last four sprints:** the team built the hard, boring, irreversible
half correctly and then, under delivery pressure, built the visible half twice — once properly
and once quickly — and shipped measurements of the quick one.

---

## 3. The findings, severity-ranked

Severity: **C**ritical = a claim the system cannot support, or active evidence corruption ·
**H**igh = blocks the v0.4.3 MVP claim · **M**edium = compounding debt with a dated owner ·
**L**ow = hygiene.

### 3.1 [C-1] The Sprint 9 meta-loop bypasses every safety boundary and grades itself

`vanguard/packages/runtime/loops/meta_loop.py` (144 LOC) is a complete second agent loop:

```python
test_proc = subprocess.run([sys.executable, "-m", "pytest"], cwd=workspace_dir, ...)
if exit_code == 0:
    passed = True
    break
```

In one function it:

- calls the model directly via `complete_fn(messages)` — **no `ModelPort`, no `ContextCompiler`,
  no prefix stability**;
- executes arbitrary code with `subprocess.run` on the host — **no `Kernel.dispatch`, no grant,
  no descriptor, no sandbox, no `bwrap`**, violating `A-03`, `N-06`, `C-08`, `SBOX-01`;
- **runs the evaluator inside the loop and branches on the verdict** — violating `A-05`
  (verifier outside the mutable surface), `ADR-0004`, `VG-03 §3` (*"No episode can request its
  own evaluation"*), `VG-03 §6.1` reading note 2, and `T5.5`;
- emits **zero events** — violating `A-07` and destroying attribution;
- carries `sys.executable` with **no `import sys`** — a `NameError` on the default path. The
  test at `test/runtime/test_meta_loop.py` passes only because it injects `test_runner`.

This single file falsifies `C-08` and inverts the project's central safety property. It is also
the exact failure `GTS-13C` Ch. 13 names: *"Code that survives because someone got attached to
it is how a prototype quietly becomes the architecture."*

**Ruling: delete `vanguard/packages/runtime/loops/` outright.** Its three genuinely valuable
ideas — compaction, failure-driven re-proposal, tier escalation — are already owned elsewhere
(`ContextCompiler`, the loop's natural continuation after a failed receipt, `routing_policy`)
and must be re-expressed there as *data*, not as a second engine. See `003 §2` and `008 §3`.

### 3.2 [C-2] The benchmark corpus does not run the harness, and reports degenerate passes

`benchmarkings/swe_pro_tiers/runner.py`, `run_matrix_evaluation.py`,
`run_agentic_live_challenge.py` and `run_live_proof.py` import **only**
`adapters/models/openrouter.py` and `adapters/models/env_loader.py`. Each then reimplements the
episode loop — its own `dialogue` list, its own tool execution via `subprocess`, its own
context bundle, and in `runner.py` a **regex fallback that parses tool calls out of prose**
(lines ~208-216).

`run_matrix_evaluation.py` is titled *"Evaluates 3 harness manifests"* and defines
`MANIFEST_DIR` at line 36. **`MANIFEST_DIR` is never used again.** The three "harnesses" are
three hardcoded system-prompt strings in a Python dict (`HARNESS_SPECS`). This is `FT-10`
(decorative switch) producing a comparative claim with no mechanism behind it.

The results are worse than unattributable — they are degenerate:

| Field | Every row of `matrix_results_tier3_token_bucket.json` |
|---|---|
| `pre_passed` | `true` — the oracle passed **before** the agent acted |
| `patch_length` | `0` — the agent changed nothing |
| `oracle_passed` | `true` — scored as a success |
| one row | `turns: 1, prompt_tokens: 0, cost_usd: 0.0, duration_s: 0.73` — **the model was never called** and it still passed |

`RSK-04` names this: *"vacuous passes, degenerate floors"*, mitigated by *"instruments that
refuse rather than report"*. The instrument did not refuse.

**In fairness:** not all of it is theatre. `result_tier1_lru_ttl_cache.json` contains a real
multi-turn trajectory with genuine `fs.read`/`fs.write` calls and real file content, and
`docs/reviews/done/sota_harness_scientific_benchmarking_programme_2026-08-16.md` already
reached this conclusion independently (*"We are cheating in several published-looking numbers.
We are not cheating in the one path that actually uses the production loop."*). That document
is correct and was not actioned. See `002` for the full triage and the labelling regime.

### 3.3 [C-3] `S_t = (G_C, G_E, L, A_t)` — three of the four terms do not exist

`VG-02 §1` defines the persistent object as the immutable competence graph $G_C$, the evidence
graph $G_E$, the ledger $L$, and the activation set $A_t$. In code:

| Term | Status |
|---|---|
| $L$ ledger | **Real.** Event store, reducer, projections, recovery — good quality |
| $G_C$ competence graph | **Absent.** `competence_claim` appears as a *string* in a kinds tuple at `domain/artifacts/graph.py:18`. No node, no edge, no lineage, no supersession |
| $G_E$ evidence graph | **Absent.** `Claim` exists only as a JSON schema (`schemas/v4/evidence-claim.schema.json`). No Python type, no store, no invalidation evaluation |
| $A_t$ activation set | **Absent.** Zero occurrences outside prose. The episode loop takes no activation set; `operatorPolicy.select(view, activationSet)` from `VG-03 §6.1` has no implementation |

Consequently **`A-02` and `L-3` — "operators are data, not control flow", declared irreversible
and load-bearing for the entire self-improvement argument — are unimplemented.** There is no
operator registry, no operator invocation, no playbook engine, no rigidity dial.

This is not a bug; it is the largest scope item still open, and it is the one that determines
whether the project's thesis is testable at all. `004` specifies the minimum viable form.

### 3.4 [H-1] The Sprint 7 harness-DNA layer is broken, and the reconstruction claim is nominal

Three test failures on this branch, all in the alias translator:

```
test_load_vg_code_swe_mini: pack.to_canonical("read_file") == 'read_file', expected 'fs.read'
test_load_vg_shell_only:    pack.to_canonical("bash")      == 'bash',      expected 'proc.exec'
test_bench.ShellOnlyControl: KeyError: 'aliases'
```

Root cause: `vg-shell-only/aliases.json` is `{"shell":"proc.exec"}` while the test expects a
`bash` key and an `{"aliases": {...}}` envelope. The loader accepts three formats
(`loader.py:41-67`) and `to_canonical` **falls back to identity on an unknown name**
(`loader.py:71`). That fallback is the real defect: an alias table that disagrees with the tool
schema fails *silently at first use* as `UNKNOWN_ACTION`, violating `N-17` / `VG-03 §5.3`
(*"unknown names fail at composition, not at first use"*).

More seriously, the reconstruction suite (`T7.6`, `C-01`) is nominal. Diffing the manifests:

> `vg-code-claude-shaped`, `vg-code-swe-mini` and `vg-code-default` are **byte-identical**
> except for `system-prompt.txt` and `aliases.json`. They reference the *same four tool schema
> files*, the same capabilities, the same context policy, the same routing policy, the same
> budget policy, the same evaluator.

A Claude-Code-shaped harness differs from a SWE-agent-shaped one in compaction strategy,
subagent topology, permission model, planning discipline and retry policy. **None of those are
expressible in the current manifest**, so the reconstruction proves only that three prompts can
be swapped. `C-01` remains untested — not falsified, *untested*, which is worse because the
programme is currently recording it as tested. See `005`.

### 3.5 [H-2] `context_policy` and `routing_policy` are decorative

`vg-code-default/context-policy.json` is `{"kind":"recency-window","maxItems":64}`. Grep for
consumption:

```
root.py:134       "context_policy": "context_policy",     # a name in a role map
graph.py:17       "context_policy", ...                    # a name in a kinds tuple
```

**Nothing reads the value.** The `ContextCompiler` is constructed from `system_core`,
`tool_schemas`, `env_text` and a token ceiling derived from the budget (`root.py:702-707`), and
it implements `result_eviction` + oldest-first drop — **a different strategy from the one the
manifest declares**. `routing_policy` (`{"kind":"single-model"}`) is likewise never read.

Both files are hashed into the composition digest, so two harnesses that differ only in context
policy produce *different digests and identical behaviour*. That is `FT-10` in the exact place
where it silently invalidates any A/B comparison keyed on context policy — i.e. the primary
experiment the whole instrument exists to run.

### 3.6 [H-3] `EpisodeCoordinator` is a second, incompatible budget and coordination ledger

`vanguard/packages/runtime/coordination.py` maintains episode identity, parent/child links and
token budgets in a **raw SQLite table**, entirely outside the event ledger and the kernel's
`Governor` lease tree. It duplicates `T2.5` budget algebra with different semantics (no lease,
no release, no overrun debit, no conservation property), emits no events, and enforces no
attenuation.

It is wired in at `root.py:712-723`:

```python
lam_db = os.environ.get("VANGUARD_LAM_DB", "tools/002_LLM_API_MOCK/lam.sqlite")
try:
    coordinator = EpisodeCoordinator(lam_db)
    ...
except Exception:
    coordinator = None
```

Three defects in ten lines: the composition root defaults to a path inside `tools/` (a
mock-provider directory) — a layering inversion; every failure is swallowed by a bare
`except Exception: pass`; and at line 793 the token figure is `... or 100`, a **fabricated
fallback number** written into the coordination store.

`A-07` says everything is an event and every surface is a projection of the ledger. This is a
second source of truth for the most attribution-critical quantity in the system.

### 3.7 [H-4] The episode is restarted, not resumed, across approvals

`root.py:738-777` loops up to `max_segments=8`, and on each iteration constructs a **new
`Kernel` and a new `EpisodeEngine`** and calls `engine.run(...)` from scratch. Approval
suspension terminates the episode (`ESCALATED`), and re-entry begins at turn 0 with a fresh
`Episode` object.

Consequences:
- `max_turns` is per-segment, so the real bound is `8 × 8 = 64` turns, not the 8 declared.
- No-progress detection (`VG-03 §6.4`) resets every segment, so `FT-02` livelock is undetectable
  across an approval.
- Episode state (`turns`, `state_digest` history) is discarded; only `_LayeredOperator._dialogue`
  (L5) survives, because that object happens to be reused.
- `T3.6`/`VG-03 §9` require resume **from the ledger**. This resumes from live object identity.

This works today and will break the moment the runtime is a daemon serving a resumed run — which
is exactly what `RuntimeService` (ADR-0062) already is.

### 3.8 [H-5] The coding domain has leaked into the model adapter

`ADR-0060` (Domain Generality Invariant) forbids coding-specific logic in `kernel/` and
`agency/episode/`. Both are clean — good. But `adapters/models/invocation.py` now holds
`KNOWN_TOOLS` and per-verb argument validation:

```python
if action in {"fs.read", "fs.write", "patch.apply"}: ...   # requires 'path'
if action == "fs.search": ...                              # requires 'pattern'
if action in {"proc.exec", "proc.test"} and "argv" not in args: ...
```

plus `_bind_resource` constructing `{"kind": "fs", "root": ..., "path": ...}` selectors. So the
verb vocabulary, the argument shapes and the resource binding for the coding domain are
hardcoded in a *model adapter*. Adding TableWorld (`T9.1`, mandatory per `VG-03 §7.3`) requires
editing this file — which is the letter of the invariant honoured and its purpose defeated.
This binding belongs in the manifest capability row, where the selector already lives.

### 3.9 [H-6] `ADR-0001` (TypeScript control plane) is contradicted, never superseded

`VG-02 §9` and `ADR-0001` specify TypeScript on Node LTS for the control plane. The control
plane is Python (15,569 LOC); TypeScript survives only as the CLI client. `ADR-0059` and
`ADR-0060` speak of "the Python microkernel" as settled fact, but **no ADR supersedes
`ADR-0001`, and its status is still `accepted`.**

The Python choice is, in my judgement, **correct and should be ratified** — the laboratory,
the evaluator ecosystem, the scientific stack and the team are all Python, and `ADR-0001`'s own
reversal condition ("team composition shifts decisively to another language") has plainly fired.
But an unrecorded reversal in an append-only register is a governance defect that will confuse
every future reader, and it is exactly what `ADR-0000` exists to prevent. Write `ADR-0063`.
See `006`.

### 3.10 [M-1] `Runtime.execute_harness` is a 175-line god function

`root.py:634-809` performs: composition, sandbox provisioning, model instantiation, ledger
bridging, classifier and policy construction, environment discovery, context compilation,
coordinator bookkeeping, an 8-iteration segment loop constructing kernels, approval resolution
and re-dispatch, evaluation, token reconciliation and teardown. It hardcodes
`/usr/bin/bwrap` (line 659), the approval threshold `"low"` (line 693), a `Reservation(100, 1000)`
(line 775) and the `... or 100` token fallback (line 793).

A composition root should compose. This one *is* the application. It is untestable except
end-to-end, it is where every future harness feature will be tempted to land, and it is the
single largest source of coupling in the tree. `003 §4` gives the decomposition.

### 3.11 [M-2] Ports specified in `GTS-13C §5.2` are missing

Present: `ModelPort`, `EnvironmentPort`, `EvaluatorPort`, `EventStorePort`, `SandboxRunner`,
`Clock`. **Missing: `BlobStorePort`, `IndexPort`, `RandomPort`.**

`RandomPort` and a complete `ClockPort` are the determinism seams `T1.11` `Recording` depends
on — without them, "replay" means state reconstruction only, and counterfactual re-execution
(`GTS-13C` Ch. 11 stage 2, the thing that makes the corpus *attributable*) is not reachable.
`BlobStorePort`/`IndexPort` are the seams every memory and retrieval feature will need; their
absence is why there is nowhere for `O-02` to land.

### 3.12 [M-3] Duplicated diff engines

`adapters/environment/fake.py` (642 LOC) has `_parse_and_simulate_patch`;
`adapters/environment/git.py` (762 LOC) has `_parse_and_validate_patch`;
`adapters/environment/sandboxed.py` delegates to a worker with its own path. Three independent
unified-diff implementations across ~1,400 LOC. `T10.2` wants a fake and a real *per port* —
it does not want two divergent parsers. `VG-03 §7.4` says *"the environment's own diff is the
definition of what changed"* and `FT-08` names the second patch path as a failure class. See
`007 §3`.

### 3.13 [M-4] The Phase-3 blueprint has drifted off the specification

`docs/reviews/done/2026-08-16-phase-3-sprints-7-10-blueprint.md` (52 lines) proposes:

| Blueprint says | Specification says |
|---|---|
| Build an **Atom→Molecule→Cell→Body→Biome hierarchy** | `GTS-13C §4.3`: *"Build the classes and you have hand-authored the hierarchy you claimed would emerge."* Depth labels are a **trace-viewer output**, never a class tree |
| `vanguard/packages/manifests/builder.py` | Manifests live in `agency/manifests`; a new top-level package is outside `LT-1…LT-8` |
| `vanguard/cli/harness.py`, `vanguard/tui/dashboard.py` | `LT-7`: clients are `clients/`, pure consumers, no adapter handles. A TUI inside the runtime package inverts the daemon boundary (`VG-03 §12`) |
| `agy harness run` | `T6.4`: `vg run`, `vg trace`, `vg why` |
| **Sprint 10 gate = "100% test pass rate + tag git"** | `GTS-13C` Ch. 10: *"Tickets merged, CI green, and a demo that worked once do not close it."* The gate is four questions |
| No mention of A/A floor, paired comparison, verifier–deployment gap, or the non-coding environment | `ADR-0057`: *"S7–S9 keep Q3+Q4."* Q3 and Q4 are **absent from the entire Phase-3 plan** |

The blueprint is a delivery plan for a demo. The specification is a plan for an instrument.
`008` reconciles them.

### 3.13b [H-7] `SEC-01` is not closed — secret history remains reachable

> **Added 2026-08-16 via `009 §3.1`.** This finding appears in no other section of `001`–`008` and
> corrects `007 §6`.

```
$ python3 tools/scan_secrets.py            → SECRET SCAN PASS
$ python3 tools/scan_secrets.py --all-refs → SECRET SCAN FAIL: reachable-object: env-named blob .env
$ git for-each-ref | grep -c refs/original → 21
```

A previously committed OpenRouter credential remains reachable in history, with 21 `refs/original`
backup refs. The prior audit named this (`mvp_beta_delivery_audit` P0-08) and it was carried as
stale. `007 §6` asserted the opposite on the evidence of `git ls-files`, **which reports HEAD, not
history**.

The generalisable defect: **the scanner was only ever run in its passing mode.** `A-10` extends to
a gate whose failing mode is never invoked. Remediation order is non-negotiable — rotate at the
provider first, then rewrite history under owner authorisation, then verify `--all-refs` **and** a
clean-clone scan. Sprint 7 Joint track in `011`.

### 3.14 [L] Portability, hygiene, process

- `/usr/bin/bwrap` hardcoded — the runtime cannot compose on macOS or Windows and the check is a
  `T10.9` special case. Probe via `shutil.which` behind a `SandboxRunner` capability report.
- `vanguard/clients/cli/dist/`, `node_modules/` and `__pycache__/` are present on disk but
  correctly **gitignored and untracked** (`git ls-files` returns zero matches). Working-tree
  noise only; no action beyond a `make clean`.
- `workflow_visualizer.html` (48 KB) at repo root — an orphan of the rejected graph runtime.
- Bare `except Exception: pass` at `root.py:722`, `root.py:796`, `engine.py:269`,
  `meta_loop.py:125`. Two are justified by `F-25` and say so; two are not.
- **Ten NO-GO review documents sit in `docs/reviews/done/` with none closed.** Reviews are
  accumulating faster than remediation, which is itself the leading indicator that the team is
  reviewing instead of deciding. `007 §5` proposes the closure protocol.

---

## 4. Status against the four MVP gate questions (`GTS-13C` Ch. 10)

| # | Question | Status | What is actually missing |
|---|---|---|---|
| **Q1** | **Is the boundary real?** | **Partially — and regressed** | The kernel path is real and well tested. But `meta_loop.py` and every `benchmarkings/` runner execute effects *outside* it, so the property "effects happen on one path or they did not happen" is currently **false for the code that produced our published numbers**. Q1 was closer to true at `v0.4.0-sprint4` than it is today |
| **Q2** | **Is it useful?** | **Not demonstrated** | `zero_hint_v1` + `execute_harness` is the one honest path and currently shows honest fails (read-loop, no `patch.apply`). No record of three real bugs fixed interactively, and no "would you reach for it again?" answer |
| **Q3** | **Is it measurable?** | **No** | No A/A floor exists. No paired runner. No pre-registration. No verifier–deployment gap number. The comparative results that do exist are degenerate (§3.2) |
| **Q4** | **Is it general?** | **No** | TableWorld / the non-coding environment does not exist. `VG-03 §7.3` calls it *mandatory in Phase 0* and explicitly says building it **first** is the point. It has been deferred four phases, and §3.8 shows the capture it was meant to detect has already begun |

**Only Q1 is within reach this quarter without new architecture, and it requires deletion, not
construction.**

---

## 5. What I would do, as tech lead, starting Monday

Ordered by irreversibility, not by size. Full plan in `008`.

**Week 1 — stop the bleeding. Pure deletion; no new abstractions.**

1. Delete `vanguard/packages/runtime/loops/`. Add an architecture test: *no module outside
   `kernel/` may call `subprocess`* and *no module in `runtime/` or `agency/` may import an
   evaluator*. Prove it fails against a broken counterpart (`T10.3`).
2. Quarantine `benchmarkings/` behind `T10.1`-style dependency rules: a benchmark runner may
   import `Runtime.execute_harness` **or** nothing. Move every result JSON produced by a
   bypassing runner to `benchmarkings/_unlabelled_retired/` with a `RETRACTED.md` stating why.
   Do not delete them — retraction with reasons is evidence; silent deletion is not.
3. Make the degenerate case impossible: a benchmark harness that observes `pre_passed == true`
   or `patch_length == 0` on a repair task must emit `inconclusive` and **refuse to score**.
4. Fix the three alias failures and make `to_canonical` **fail at composition** on any alias
   whose target is not a manifest-declared verb.

**Weeks 2–4 — make the spine carry the weight it claims.**

5. Recursion in `agency/`: `EpisodeEngine` gains child-episode spawn under an attenuated
   kernel lease, with `depth` as a real budget dimension and child events carrying the parent
   id. Delete `runtime/coordination.py`; depth labels become a *projection* over ledger events.
6. Resume, don't restart: the segment loop moves into the engine as a suspend/resume on ledger
   state, so `max_turns` and no-progress detection survive an approval.
7. Make `context_policy` and `routing_policy` load-bearing: compaction strategy and model
   routing become named, registered, frozen-at-composition components selected by the manifest.
   This is the minimum condition for any harness comparison to mean anything.
8. Decompose `execute_harness` into `compose → session → run` (`003 §4`).

**Weeks 5–8 — make it measurable and general (Q3, Q4).**

9. A/A runner against `vg-shell-only` on ≥3 task classes; the floor **refuses to report when
   degenerate**. No delta is interpretable before this number exists (`T8.1`).
10. TableWorld. Build it, and count the lines changed in `kernel/` and `agency/episode/`.
    The count is the `C-10` measurement; a non-zero count is a finding, and a cheap one.
11. Minimum viable $G_E$: `Claim` as a real type with non-empty invalidation conditions
    evaluated on a schedule. $G_C$ and $A_t$ follow only once one artifact clears the A/A floor
    (`O-01` — derive the lifecycle from the survivor).

**What I would explicitly NOT do now:** build the competence graph, the operator registry, the
playbook engine or the offline optimiser. `O-01` is right — those must be derived from a
survivor, and there is no survivor yet because there is no floor. Building them now is the
premature formalisation `VG-02 §8` warns about, and it is the single most expensive mistake
available to this programme.

---

## 6. The honest strategic read

The user's framing — V6 meta-cognitive machines → V5 abstraction → V4 harness framework →
harness agentic coder → solved tasks — is a sound layering, and the v4 corpus is a genuinely
strong foundation for it. The risk is not that the abstraction is wrong. It is this:

> **The programme is currently generating abstraction faster than it is generating evidence,
> and generating evidence faster than it is generating *valid* evidence.**

Ten review documents, five sprint plans, a 25,000-line living task matrix and a 52-line
Phase-3 blueprint have accumulated around a runtime whose central claim — recursive coordination
under one budget algebra — is not implemented, and whose measurement layer reports passes on
tasks that were already passing.

The v4 corpus anticipated all of this. `RSK-04`, `RSK-11`, `FT-10`, `A-10` ("a gate that cannot
fail is not a gate") and `GTS-13C` Ch. 14 ("disposable becomes architecture") each name a
failure that has now occurred. **The specification is not the problem; it is the asset. The
problem is that delivery pressure produced a second implementation path, and nothing in CI
forbade it.** The architecture tests in `T10.4` prove paths *do not exist* — that mechanism is
the right one and it simply was not extended to the new code.

The correct posture for v0.4.3 is therefore not *more*. It is **subtraction, then honesty, then
one real number.** A programme that can produce a single credible A/A floor against
`vg-shell-only`, on a runtime where every effect provably traverses one kernel, is in a
materially stronger position than one holding a passing test suite and a matrix of vacuous
results — and it is roughly six weeks of work, not six months.

---

## 7. Document map

| Doc | Owns |
|---|---|
| **001** (this) | The ruling, severity ranking, gate status, the order of work |
| `002` | Measurement and evidence integrity: benchmark triage, labelling regime, the A/A programme |
| `003` | Core architecture: the second-loop problem, coupling, `execute_harness` decomposition, layer contracts |
| `004` | Cognition, competence and self-improvement: $G_C/G_E/A_t$, operators-as-data, memory, SOTA |
| `005` | The harness manifest framework: what a manifest must express to make `C-01` testable |
| `006` | Tech stack, protocols and polyglot seams: Python ratification, MCP/ACP/A2A, performance |
| `007` | Codebase cleanup, deduplication and documentation consolidation |
| `008` | The corrected v0.4.3 delivery plan for Sprints 7–10, with gates |
