# 003 — Core Architecture, Coupling & the Second-Loop Problem

**Status:** NON-NORMATIVE. Where this file and a v4 owner disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Owns:** the structural diagnosis of the runtime — parallel execution paths, layer-contract
drift, the composition-root monolith, recursion, resume, and the concrete refactors.
**Authority cited:** `VG-03 §§3–12`, `VG-02 A-01…A-12`, `GTS-13C` Ch. 4–5, `ADR-0050`, `ADR-0060`.

---

## 1. The one-sentence diagnosis

> **The architecture specifies one execution primitive and the tree now contains three, and the
> two that were added later are the two that produced the delivered evidence.**

`A-01` — *"The episode is the only execution primitive"* — is the first axiom, and its stated
enforcement is *"no workflow engine, topology language, graph validator or node registry exists
in the tree."* That enforcement was written against the *previous* failure mode (a static DAG)
and does not catch the *current* one (a second imperative loop). The axiom held; the test for it
was aimed one war back.

---

## 2. The three loops

| # | Loop | Location | Kernel | Ledger | Sandbox | Exterior judge | Context compiler |
|---|---|---|---|---|---|---|---|
| 1 | `EpisodeEngine` | `agency/episode/engine.py` (293 LOC) | ✅ single path | ✅ | ✅ via adapters | ✅ never invoked in-loop | ✅ via `_LayeredOperator` |
| 2 | `MetaLoopEngine` | `runtime/loops/meta_loop.py` (144 LOC) | ❌ none | ❌ none | ❌ host `subprocess` | ❌ **grades itself** | ❌ ad-hoc truncation |
| 3 | Benchmark runners | `benchmarkings/**` (4 files) | ❌ none | ❌ none | ❌ host `subprocess` | mixed | ❌ ad-hoc dict |

### 2.1 Loop 2 — `MetaLoopEngine`, in detail

```python
# meta_loop.py:100-110
test_proc = subprocess.run([sys.executable, "-m", "pytest"], cwd=workspace_dir, ...)
exit_code, output_text = test_proc.returncode, ...
if exit_code == 0:
    passed = True
    break
```

Violations, each traceable to a named rule:

| Rule | Violation |
|---|---|
| `A-03` / `N-01` / `T4.1` | An effect executes with no descriptor, no grant, no receipt |
| `A-05` / `ADR-0004` / `L-01` | The loop invokes the evaluator and branches on the verdict |
| `VG-03 §3` | *"Evidence owns the evaluation trigger… No episode can request its own evaluation"* |
| `T5.5` | Same, restated as a contract row |
| `A-07` | Zero events emitted; the run is invisible to the ledger |
| `N-06` / `SBOX-01` | Shell contained by the sandbox — here it is contained by nothing |
| `LT-*` | `runtime/loops/` is not a package in the layer topology |
| — | `sys.executable` used with **no `import sys`**: `NameError` on the default path |

The compaction is also a regression, not an advance: `compact_context` keeps the first 100 lines
of every file over 8 KB — a cruder policy than the *"compactor that kept the last four blocks"*
that `VG-03 §10` cites as the prototype's worst investment.

**Ruling: delete `vanguard/packages/runtime/loops/` and `test/runtime/test_meta_loop.py`.**

The three ideas in it are worth keeping and each already has an owner:

| Idea in `meta_loop.py` | Correct home |
|---|---|
| Context compaction | `ContextCompiler._fit` — already implements `result_eviction`; add `structured_consolidate` (`VG-03 §10.4`) as a **registered strategy selected by `context_policy`** |
| Retry on test failure with the trace | Not a feature. `VG-03 §2.2`: *"repair does not exist. The agent observes failing output as a result and continues — that is the loop."* Requires only that the receipt body re-enters L5, which `receipt_labeller` already does |
| Tier escalation ollama→free→paid | `routing_policy` as a real component (`005 §4`), consumed by a `ModelPort` router. `adapters/models/routing.py` (107 LOC) already exists and is unwired |

### 2.2 Loop 3 — the benchmark runners

Covered in `002 §2`. Structurally the point is identical: nothing in CI forbade importing
`adapters/` from outside `runtime/`. `LT-5`/`LT-6` say adapters are imported **only** by
`runtime/`; `benchmarkings/` was never in the lattice.

**Ruling: one dependency rule (`002 §3.1`) makes loops 2 and 3 unwritable.** Add it before
fixing anything else, or the fix will be re-litigated next sprint.

---

## 3. Recursion: the missing centre

### 3.1 What the specification requires

`GTS-13C §4.3`, `T4.4`, `VG-03 §5.2`:

> An agent is an Episode. A team is an Episode that spawns Episodes. A department is an Episode
> that spawns Episodes that spawn Episodes. **One type, one budget algebra, one attenuation
> rule, one event stream — at every level of coordination.**

Operator invocation *is* child-episode spawn (`T4.10`). Context isolation — *"a child's
exploration never enters the parent's window, and only the result returns"* — is called out in
`VG-03 §5.2` as the property no static graph can express, and is the single most valuable
property in the design.

### 3.2 What exists

`agency/episode/engine.py:17-19`:

```
Depth-1 (`REQ-EXEC-001`): a turn produces one effect request. Recursion is a
budget dimension the kernel already enforces, and this engine never re-enters itself.
```

`run()` takes `depth: int = 1` and passes it into `EffectRequest`. It is telemetry. There is no
spawn, no child lease, no task group, no cancellation scope, no per-branch workspace, no
independence group. `T4.6`, `T4.7`, `CC-1…CC-7` and `VG-03 §8` are entirely unimplemented.

The one thing that *does* model parent/child is `runtime/coordination.py` — §4 below.

### 3.3 The 2026 evidence that this is the highest-value missing feature

Independent of our specification, the field converged on the same primitive:

- Anthropic's multi-agent research system uses **subagents with isolated context windows**, each
  returning 1,000–2,000-token condensed summaries, outperforming a single-agent baseline by
  **90.2%** on their internal research eval.
- Context editing/compaction alone delivers a **29%** lift; on a 100-turn eval it cut token
  consumption **84%** and enabled workflows that otherwise failed on context exhaustion.
- 2026 harness surveys describe *context isolation* — a sub-agent with its own system prompt and
  tool set — as a first-class mechanism for reducing interference and improving modularity.
  ([Code as Agent Harness](https://arxiv.org/html/2605.18747v1),
  [Context Engineering Playbook 2026](https://www.digitalapplied.com/blog/context-engineering-agent-reliability-playbook-2026),
  [SearchSwarm](https://arxiv.org/pdf/2606.09730))

`VG-03 §10.3` already states the conclusion: *"The cheapest way to keep a context window clean
is never to put the exploration in it. Isolation is the primary mechanism; compaction handles
the remainder."* We wrote that and then built only the remainder.

### 3.4 Minimum viable recursion — what to build

Deliberately small. This is not a subagent framework; it is one method on the engine.

```python
# agency/episode/engine.py — sketch, not final
def spawn(self, parent: Episode, *, operator: OperatorRef,
          brief: str, scope: Scope, reservation: Reservation) -> ChildResult:
    """One mechanism. Attenuation at the broker, not at the absence of a call site."""
```

| Requirement | Rule |
|---|---|
| Child scope ⊆ parent scope, verified by the **existing** `kernel/attenuation.py` | `T2.3`, `N-05` |
| Child lease on the parent's remainder, via the **existing** `Governor` | `T2.5`, `CC-5` |
| `depth` is a real budget dimension, denial at the limit is a typed result | `VG-03 §5.2`, `FT-03` |
| Child events carry `causationId = parent episode`, nest in projections | `T1.7`, `VG-03 §8.3` |
| Return value is **text or a structured payload — never a handle, never shared state** | `VG-03 §5.2` |
| Child failure is a typed result, not an exception into the parent loop | `VG-03 §5.2` |
| Child context is a fresh `ContextCompiler` prefix; the parent's L5 receives only the return | `VG-03 §10.3` `operator_isolation` |
| Workspace: parent snapshot by default; isolated snapshot when branching | `VG-03 §5.2` |
| Per-branch workspace destroyed in `finally`, including creation failure | `N-16`, `FT-04` |

**Everything on the right-hand column already exists in `kernel/`.** Recursion is not new
machinery; it is the call site that was never written. That is the good news, and it is why this
is a two-week item and not a quarter.

**What to defer:** parallel branch exploration (`VG-03 §8.4`), independence groups, rankers.
Serial recursion first — it is where the isolation benefit lives, and concurrency without a
noise floor is unmeasurable anyway (`C-04` needs `T8.1`).

---

## 4. `EpisodeCoordinator`: delete the second budget ledger

`runtime/coordination.py` (171 LOC) stores `episode_id, parent_id, depth, depth_label,
budget_tokens, remaining_tokens, tokens_used` in a raw SQLite table.

| Property | Kernel `Governor` | `EpisodeCoordinator` |
|---|---|---|
| Lease with release on every path | ✅ | ❌ |
| Overrun debited at commit | ✅ `K-07` | ❌ |
| Conservation property test | ✅ `T2.5` | ❌ |
| Multi-dimensional (`tokens, usd, millis, bytes, depth`) | ✅ | ❌ tokens only |
| Events / ledger | ✅ | ❌ |
| Attenuation | ✅ | ❌ |
| Recoverable from ledger | ✅ | ❌ |

It is wired in at `root.py:712-723` with three separate defects:

```python
lam_db = os.environ.get("VANGUARD_LAM_DB", "tools/002_LLM_API_MOCK/lam.sqlite")  # (a)
try:
    coordinator = EpisodeCoordinator(lam_db)
    ...
except Exception:            # (b)
    coordinator = None
...
tokens_used = sum(...) or 100   # (c)  root.py:793
```

(a) the composition root defaults to a path inside a **mock-provider tool directory** — a
layering inversion that makes `runtime/` depend on `tools/`; (b) every failure is silently
swallowed, so a corrupt coordination store is indistinguishable from a healthy one; (c) a
**fabricated fallback of 100 tokens** is written into the store when the real figure is zero,
manufacturing telemetry.

**Ruling: delete `runtime/coordination.py`.** Depth, depth labels and parent/child structure are
**projections over ledger events** — `runtime/ledger/projections.py` (265 LOC) already exists and
is the correct home. `GTS-13C §4.3` is explicit: *"the atom/molecule/polymer/cell/organism
vocabulary is not a class hierarchy. It is a set of names the trace viewer applies to observed
coordination depths after a run."* A SQLite table of depth labels is a hand-authored hierarchy
wearing a projection's clothes.

**Migration:** `MetaLoopEngine` (deleted) and `root.py` are the only consumers.
`test/runtime/test_coordination.py` becomes a projection test.

---

## 5. `Runtime.execute_harness`: decomposing the god function

`root.py:634-809`, 175 lines, currently performs eleven distinct responsibilities. It is the
single largest coupling source in the tree and the place every future feature will be tempted to
land.

### 5.1 Hardcoded values that should be data

| Line | Value | Should come from |
|---|---|---|
| 659 | `Path("/usr/bin/bwrap")` | `SandboxRunner` capability probe via `shutil.which`; absence is a composition error with a named remedy, not a path literal |
| 693 | `approval_required_above="low"` | The manifest's `budget_policy` or a new `approval_policy` component |
| 775 | `Reservation(usd_micros=100, millis=1000)` | The budget policy |
| 793 | `... or 100` | **Delete.** Zero tokens is zero tokens; fabricating a figure is `RSK-04` at source |
| 712 | `"tools/002_LLM_API_MOCK/lam.sqlite"` | Deleted with `EpisodeCoordinator` |

### 5.2 The decomposition

Three objects, each independently testable:

```
Runtime.compose(manifest) -> Harness          # already exists and is good. Keep as is.

HarnessSession(harness, ports, task)          # NEW — owns the wiring
    .kernel      : Kernel                     # built ONCE, not per segment
    .engine      : EpisodeEngine
    .operator    : LayeredOperator
    .approvals   : ApprovalFlow
    .evaluator   : EvaluatorPort | None

HarnessSession.run() -> RunResult             # owns the lifecycle, not the wiring
```

Rules the split enforces structurally:

1. **One `Kernel` per run**, not one per segment. Today three are constructed
   (`root.py:742`, `769`, plus the base) with the same collaborators — a smell that the segment
   loop is compensating for a missing suspend/resume.
2. `HarnessSession` takes its ports **injected**. The current signature already has
   `model=`, `store=`, `clock=`, `verifier=`, `bindings=` — it is 80% there; the remaining 20%
   is the sandbox and the approval authority.
3. Composition failures stay in `compose`; runtime failures stay in `run`. Today a missing
   `bwrap` raises `CompositionError` from inside `execute_harness`, after composition succeeded.
4. `_WitnessKernel` (`root.py:429-445`) disappears: it exists only because `DispatchResult`
   does not carry the request through a suspension. Either add `request_digest` to
   `DispatchResult` or have the session hold the pending request — both are cleaner than
   wrapping the kernel.

---

## 6. Suspend and resume, not restart

`root.py:738` loops `for _ in range(max_segments)` and builds a **fresh `Episode` each time**.

| Consequence | Rule violated |
|---|---|
| Real turn bound is `max_turns × max_segments` (8×8=64), not the declared 8 | `VG-03 §6.5` "every turn bounded on every budget dimension" |
| No-progress tuple history resets each segment; livelock across an approval is undetectable | `VG-03 §6.4`, `FT-02` |
| Episode `state_digest` chain is broken; the ledger shows N short runs, not one suspended run | `T3.3` replay yields identical state digest |
| Resume depends on live object identity (`_LayeredOperator._dialogue`) | `T3.6` resume **from the ledger** |

**Fix:** the suspension belongs *inside* the engine as a terminal-with-continuation, and re-entry
reconstructs `Episode` by reducing the ledger for that `episodeId`. `domain/ledger/reducer.py`
(478 LOC) and `runtime/ledger/recovery.py` (221 LOC) already do exactly this for crash recovery —
approval suspension is the same mechanism with a different trigger. This is a **reuse**, not new
code, and it is what makes the `RuntimeService` daemon (`ADR-0062`) correct rather than
accidentally working.

---

## 7. Domain leakage: `ADR-0060` honoured in letter, defeated in purpose

`ADR-0060` requires zero coding-specific lines in `kernel/` and `agency/episode/`. Verified:
**both are clean.** Genuinely well done.

But `adapters/models/invocation.py` now holds the coding domain:

```python
KNOWN_TOOLS = {...}                                              # fs.read, fs.search, patch.apply, proc.exec
if action in {"fs.read","fs.write","patch.apply"}: ...           # requires 'path'
if action == "fs.search": ...                                    # requires 'pattern'
if action in {"proc.exec","proc.test"} and "argv" not in args: ...
def _bind_resource(action, args, root):
    return Result.success({"kind":"fs","root":root,"path":bound.value})
```

So the verb vocabulary, argument shapes and **resource-selector construction** for the coding
domain live in a model adapter. Adding TableWorld (`T9.1`) requires editing this file.
`VG-02 §8` names this precisely: *"If a coding feature needs a special case, that is the capture
happening."*

**Fix:** the manifest capability row already carries `verb`, `sink`, `selector`, `risk`. Extend
it with `args_schema` (already present per tool in `*-tool.json`) and a `selector_binding`
expression, and have the translator do a **generic** projection: tool call → verb → validate
against the declared schema → bind selector by the declared rule. Then `invocation.py` holds
zero domain knowledge and TableWorld is a manifest.

This also fixes the `to_canonical` identity fallback (`001 §3.4`) for free: with the manifest as
the authority, an unknown alias is a **composition error**, satisfying `N-17`.

---

## 8. Layer-contract audit (`VG-03 §4`)

| Contract | Status | Note |
|---|---|---|
| `LT-1` `domain/` imports nothing from the project | ✅ | Verified |
| `LT-2` `ports/` imports only `domain/` | ✅ | |
| `LT-3` `kernel/` imports `domain/`+`ports/`, never `adapters/`/`agency/` | ✅ | `dispatch.py` imports `..domain.canonicalisation` and `..ports.kernel` only |
| `LT-4` `agency/` never `adapters/`, never `lab/` | ✅ | `engine.py` annotates `model: Any` *specifically* to avoid a second port — a good call |
| `LT-5` `adapters/` never each other | ⚠️ | `root.py:513` `_sandbox_effector` returns `_environment_effector`; not an adapter-to-adapter import, but the "compatibility binding" comment marks a name that no longer means what it says |
| `LT-6` only `runtime/` imports everything | ⚠️ | Holds inside `vanguard/`, **breaks outside**: `benchmarkings/` imports `adapters/` directly |
| `LT-7` `clients/` holds no adapter handles | ✅ | TS CLI talks NDJSON to the daemon |
| `LT-8` nothing imports `lab/` | ✅ | |
| — | ❌ | **`runtime/loops/` is not in the lattice at all.** A package that no contract covers is a package no contract constrains |

**Add to `tools/check_boundaries.py`:** any top-level package under `vanguard/packages/` not
named in `LT-1…LT-8` is a build failure. New layers require an ADR, which is the point.

---

## 9. Consolidated refactor backlog

| # | Item | Kind | Effort | Unblocks |
|---|---|---|---|---|
| A1 | Dependency rule: `benchmarkings/` may import `runtime.root`+`ports` only | CI | 0.5 d | `002` M1 |
| A2 | Lattice completeness rule: unknown top-level package = build failure | CI | 0.5 d | prevents recurrence |
| A3 | Architecture test: no `subprocess` outside `adapters/sandbox/`; no evaluator import in `agency/`/`runtime/` (+ broken counterparts) | CI | 1 d | Q1 |
| A4 | **Delete `runtime/loops/`** | deletion | 0.5 d | Q1 |
| A5 | **Delete `runtime/coordination.py`**; depth as a ledger projection | deletion | 2 d | `A-07` |
| A6 | Fix alias translator; fail at composition on undeclared verbs | fix | 1 d | S7 green |
| A7 | Decompose `execute_harness` → `compose / HarnessSession / run`; one kernel per run | refactor | 3 d | testability |
| A8 | Remove hardcoded `bwrap` path, approval threshold, reservation, `or 100` | fix | 1 d | portability |
| A9 | Suspend/resume from the ledger; delete the segment loop | refactor | 1 wk | `T3.6`, daemon |
| A10 | **Recursion: `spawn` + child lease + isolation** (§3.4) | feature | 2 wk | the thesis |
| A11 | Move verb/args/selector binding from `invocation.py` to the manifest | refactor | 1 wk | `Q4`, TableWorld |
| A12 | Add `BlobStorePort`, `IndexPort`, `RandomPort` | feature | 3 d | replay, memory |

A1–A6 total **five days** and are pure subtraction. They restore Q1 and turn the suite green.
A7–A9 are two weeks and make the runtime honest about state. A10–A12 are the four weeks that
make the architecture's central claim real.

---

## Sources

- [Code as Agent Harness — Toward Executable, Verifiable, and Stateful Agent Systems](https://arxiv.org/html/2605.18747v1)
- [Context Engineering: Agent Reliability Playbook 2026](https://www.digitalapplied.com/blog/context-engineering-agent-reliability-playbook-2026)
- [SearchSwarm: Delegation Intelligence in Agentic LLMs for Long-Horizon Deep Research](https://arxiv.org/pdf/2606.09730)
- [SmoothAgent: Long-Horizon LLM Agent Serving with Lookahead Context Engineering](https://arxiv.org/pdf/2607.00151)
- [Slipstream: Trajectory-Grounded Compaction Validation](https://arxiv.org/pdf/2605.08580)
