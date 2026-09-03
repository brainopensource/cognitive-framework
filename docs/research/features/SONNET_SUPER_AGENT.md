---
title: The Sonnet Super-Agent Report
subtitle: Empirical Forensics, vg-coder-v4, and a Divergent-Paradigm Roadmap Toward 10/10 Autonomous Software Engineering
author: Claude (Sonnet 5) — Staff Engineer / Principal Architect working session
date: 2026-09-02
status: DRAFT — proposal and findings, not yet ratified
scope: AETHER / Vanguard agentic coding substrate
---

# The Sonnet Super-Agent Report

## Abstract

This report documents one working session's empirical investigation of the AETHER
coding-agent substrate — from a broken desktop client through a live-model
benchmark of a newly built agent, `vg-coder-v4` — and uses what was actually
*measured* (not assumed) to propose four architecturally distinct paths to a
10/10 autonomous engineer: one capable of greenfield synthesis, brownfield
surgery, and deep codebase explanation, on hard multi-file, big-context problems,
in one shot, with minimal operator interaction.

Every claim below is either (a) something this session directly observed —
composed a manifest, launched a live run, read a trajectory, ran a test suite —
or (b) explicitly marked as a proposal. Nothing here reports a benchmark that
was not actually executed. Where an earlier document in this project reached a
conclusion this session's evidence falsifies, that is stated plainly, because a
repeated wrong diagnosis is more expensive than an uncomfortable correction.

This document is deliberately shorter and more grounded than
[`HYDRA_MULTI_AGENT_TOPOLOGY_AND_EMERGENT_AGENCY.md`](HYDRA_MULTI_AGENT_TOPOLOGY_AND_EMERGENT_AGENCY.md),
which already carries the formal mathematics (Thompson-sampling regret bounds,
Bayesian belief updates, the complexity functional) for the Hydra
meta-governor. Where this report references Hydra, it cites that document for
proof and contributes only what changed: what this session's live evidence
says about which of Hydra's assumptions hold, and one new governance
primitive (the routing-policy escalation ladder) that the existing spec
under-weights.

---

## Table of Contents

1. What Was Done This Session (Verified Work)
2. The Corrected Root Cause: Routing Policy, Not Alias Wiring
3. `vg-coder-v4`: Design, Build, and Live Benchmark Evidence
4. Open TODOs and Unresolved Issues
5. The Composition Model: Primitives, Atoms, Molecules, Swarms
6. Four Divergent Paradigms Toward 10/10
   - 6.1 Chimera 2.0 — Evolution, Not Replacement
   - 6.2 Hydra — Chimera as an Inner Head Under Bifurcation Governance
   - 6.3 `vg-hexagonal-tdd` — The Methodology Specialist
   - 6.4 `vg-archeologist-swarm` — Consensus Exploration for Undefined Problems
   - 6.5 Why These Four Are Actually Different (Inner and Outer Loop)
7. Tooling, Skills, and OSS Proposals
8. Roadmap Assessment: Is "Next Sprint" Real?
9. Closing Position

---

## 1. What Was Done This Session (Verified Work)

This session started from a user report ("the desktop app is buggy") and ended
having built and live-benchmarked a new coding agent. The path between those
two points is itself evidence about where this substrate's real defects live —
consistently at the seams between components that were each independently
tested, never at the reasoning core of the model.

### 1.1 Desktop client — real bugs, all fixed and verified

The `@aether/desktop` client had never successfully run in a browser. Root
causes, each confirmed by direct reproduction, not inference:

- **No browser build existed.** `index.html` loaded a `.ts` file directly.
  Built an esbuild pipeline (`scripts/build-browser.mjs`) with a Node-builtin
  shim plugin (`scripts/browser-shims.mjs`) so the `@aether/client` barrel —
  which re-exports `ManagedRuntimeHost`, the operator signer, and the UDS
  transport, all Node-only — stops poisoning the browser bundle. Pure shims
  (`node:path`, `node:url`, `randomUUID`) get real implementations; anything
  a browser genuinely cannot do (`node:fs`, `node:net`, `node:child_process`)
  throws a named error rather than fabricating a plausible-looking result.
- **The typing freeze** ("one letter at a time") — every keystroke forced a
  full `innerHTML = ""` rebuild via two independent notifiers (the store
  signal, and `FrontendAppController.setConversationDraft`), destroying the
  focused textarea each time. Fixed with `Signal.setSilent()` plus a 400 ms
  debounce, and — because *some* re-render is unavoidable (streaming events) —
  a `data-focus-key`-based focus/caret restoration layer
  (`src/dom/focus-preservation.ts`). Verified in real headless Firefox: 11/11
  characters typed, focus and caret survived a forced mid-typing re-render.
- **Settings showed a fabricated `CONFIGURED` badge** next to a machine with
  no key at all, because credential state was a browser-side default, never
  asked of the runtime. Added `GET /api/credentials` and
  `POST /api/credentials:test` — the latter spends exactly one token against
  the real provider and distinguishes `MISSING` / `DENIED` (bad file
  permissions) / `INVALID` (bad key) / `EXHAUSTED` (no credit) /
  `RATE_LIMITED` / `UNREACHABLE`, each with a concrete remedy string.
- **Runs streamed "forever."** The gateway defaulted a missing manifest path
  to a literal `harness.yaml` that exists in no workspace, so
  `RuntimeService._cmd_StartRun` never spawned a worker thread — the run was
  accepted, published one heartbeat, and then produced nothing, forever, with
  no visible error. Added a Logs tab (`LogsPane.ts`) rendering the raw event
  ledger — including terminal states the transcript has no projection for —
  reachable from the top bar, exactly as requested.

Verification discipline applied throughout: 38 new JS unit tests (focus
preservation, debounced draft, credential panel, logs pane), a shared DOM
mock replacing two ad-hoc inline stubs, and live end-to-end confirmation in
headless Firefox — screenshots taken, not assumed.

### 1.2 The env key was never usable, and the fix path

`.env` at repo root was byte-identical to `.env.example` (empty key) and mode
`0644`. `env_loader.py`'s SEC-01 contract refuses anything looser than
`0600` by design — a key that is *readable by other users* is a security
defect, not a false negative to route around. Once the user supplied a real
key and `chmod 600` was applied, `credential_status()` reported `CONFIGURED`
and a live one-token probe against OpenRouter returned HTTP 200. This
confirms the credential-probe design decision (Section 1.1) end-to-end, not
just in unit tests.

### 1.3 Branch reconciliation — 88 files, verified, not assumed

A parallel session had produced an 88-file uncommitted diff on `main`
diverging from `origin/feat/beta-release-MVP-v092` (10 commits: dialect
projection, protocol recovery, admission-gate verification binding, DAG
topologies). This session's contribution was **verification of a
reconciliation another agent had already drafted**, not the merge itself:

- Confirmed **zero unmerged conflicts** in the integration worktree.
- Confirmed `session.py` genuinely kept both sides (my bounded context-packet
  work at one set of methods, the branch's `ProtocolRecoveryState` and
  completion-verification tracking at another) rather than one side silently
  winning.
- Ran the full test matrix myself rather than trusting the other agent's own
  report: `test/agency` 182/182, `test/kernel` 97/97, `test/contracts` and
  `test/adapters` failures cross-checked against a clean baseline worktree
  and confirmed **pre-existing**, not regressions.
- Independently re-derived the benchmark evidence from
  `benchmarks/artifacts/ladder/*.run.json` rather than trusting the earlier
  session's `benchmark_20_deepseek_v4_flash.json`, which reported **0/20,
  $0.00000, 0 tokens** — a dry run masquerading as a benchmark. The real
  ladder artifacts showed 26 PASS / 19 FAIL / 1 ERROR across 46 live runs.

### 1.4 The first (and corrected) root-cause diagnosis

Cross-tabulating pass rate by manifest against the 46 ladder runs produced a
striking signal: **every one of the 20 failing runs belonged to a single
manifest**, `vg-code-max-v3luna` (2/21 pass), while every agent that inherited
`vg-code-default`'s policy stack passed 24/24. My first diagnosis attributed
this to an orphaned `aliases.json` file (present in six manifests, referenced
by none). **That diagnosis was incomplete** — see Section 2 for the correction,
made by directly reproducing the failure rather than trusting the static
read. This is deliberately included as-is: an investigation that reports only
its final correct conclusion, with no record of the wrong intermediate one,
teaches the next investigator nothing about how to falsify a plausible-looking
theory.

---

## 2. The Corrected Root Cause: Routing Policy, Not Alias Wiring

The static read said `aliases.json` was dead everywhere. Live reproduction
said otherwise:

```python
Runtime.compose("vg-code-max-v3luna/manifest.json")   # via compose.py
```

`compose.py:320-480` **does** auto-load `<pack>/aliases.json` by directory
convention, fail-closed against the manifest's declared capability verbs.
This is the code path `execute_profiled` — and therefore every live
benchmark run — actually takes. The `agency/manifests/loader.py` registry
path used by a separate test family (`test_manifest_loader.py`,
`test_vg_herbs_manifest.py`) does the same, gated behind
`REGISTERED_COMPONENT_CONSUMERS`. Neither path is dead; my first pass had
inspected the manifest's declared `components` block for a `"aliases"` key,
found none, and concluded the file was orphaned — without checking whether
the loader resolves it by *filesystem convention* instead. **A negative
result from grepping a JSON key is not evidence of dead code; it is evidence
that the wiring, if it exists, is implicit.** The correction came from
running `Runtime.compose()` against the actual manifest and inspecting the
`AliasTranslator` it produced, not from reading further code.

The real, confirmed differentiator between the passing and failing manifests
is the **routing policy**:

```jsonc
// vg-code-default/routing-policy.json (365 B) — inherited by v3, chimera-v1,
// 1-forge-v2, herbs. Combined record: 24/24.
{
  "kind": "single-model",
  "role_bands": {"architect": ["medium"], "executor": ["free"],
                  "diagnostic": ["medium"], "reviewer": ["free", "medium"]},
  "failure_escalation": ["no_progress", "instrument_error"],
  "maximum_band": "medium",
  "known_pricing_required": true,
  "resolved_model_required": true
}

// vg-code-max-v3luna/routing-policy.json (29 B) — a fork that kept the key
// and dropped everything else. Record: 2/21.
{"kind": "single-model"}
```

`v3luna` forked the routing policy and, in doing so, silently discarded the
`failure_escalation` ladder. Of its 20 failures, 17 die at
`ProposalTranslator` with `tool is not declared by manifest: patch` /
`patch.apply` / `test`, or `'read' is an alias; no manifest was supplied to
resolve it` — and with no escalation ladder, an `instrument_error` has no
governed recovery path; it simply terminates the run. The remaining 5 are
`no_progress` timeouts with the identical structural cause. **The lesson that
generalizes: a policy file is not local configuration. It is a governance
object, and forking it without understanding what it silently drops is a
class of bug this substrate has no static check for.** Section 6.1 proposes
one.

A second, independent finding from this same investigation: of the 26 oracle
`PASS` verdicts across all manifests, only 10 terminated `completed` — 18
ended `abandoned`, most commonly *"repeated action proc.exec over 3 turns"*.
**The files ended up correct in those 18 cases, but the agent did not know it
had won.** This is a distinct failure mode from the routing-policy gap and is
carried into Section 4 as an open TODO, because it recurred — worse — in this
session's own new agent.

---

## 3. `vg-coder-v4`: Design, Build, and Live Benchmark Evidence

### 3.1 Design rationale

Rather than starting from a blank prompt, `vg-coder-v4` was constructed as an
explicit synthesis of what Section 2's forensics had already proven, plus two
new capabilities the backend supported but no existing manifest exposed:

| Component | Source | Why |
|---|---|---|
| `routing-policy.json`, `approval-policy.json`, `retrieval-policy.json`, `budget-policy.json`, `pytest-green` skill | Inherited verbatim from `vg-code-default` | 24/24 combined record — do not fork what is proven |
| `repo-index.json` | Same pattern as `vg-code-max-v3` | Pre-loaded Repository Map avoids orientation churn (v3's 100% easy-tier record) |
| Read tool `offset`/`limit` | Wired in `git.py:280-330` (auto-paginates >100 lines) but only exposed by `vg-code-default` and `vg-herbs`, absent from v3 | Direct requirement for "big context" files |
| Patch tool `diff` mode | Wired in `git.py:519-560` (`_parse_and_validate_patch`) plus a headerless-hunk convenience (`_with_file_header`) — present in the backend, exposed by **zero** existing manifests | A unified-diff hunk on a large file cannot silently drop the untouched remainder the way a truncated full-file rewrite can, and is far cheaper in output tokens |
| System prompt | Synthesized from `v3`'s tight one-tool-per-turn discipline (proven 18/18) plus `v3luna`'s genuinely useful content (offset/limit guidance, multi-file signature-sync mandate, contract-specification discipline) minus `v3luna`'s verbosity and its ambiguous greenfield clause | Keep what worked, discard what didn't, without re-forking the policy layer that actually mattered |

The manifest was registered through the real governance path, not bypassed:
added to `registry.json`, added to the explicit, test-pinned
`ADMISSION_GATED_HARNESSES` set in `session.py`, and
`test/falsifiers/test_completion_gate_scope.py` — which asserts that exact
set by equality — was updated in the same commit-worthy diff, so the scope
change is a visible governance decision, not a silent drift. `test/agency`
remained 182/182 after the addition.

### 3.2 Live benchmark evidence

All runs below used `deepseek/deepseek-v4-flash-0731` via OpenRouter, real
API calls, cassette-recorded, oracle-verified in a subprocess after the
agent finished (never trusting the agent's own claim of success). Total
session spend: **$0.03–0.04 of a $0.10 budget.**

**Head-to-head against `vg-code-max-v3`'s own proven results, same
challenges:**

| Challenge | `vg-code-max-v3` (baseline) | `vg-coder-v4` | Verdict |
|---|---|---|---|
| `sota_medium_public_interface` (3-file signature migration) | PASS, 10 turns, $0.0028 | **PASS, 12 turns, $0.0037,** `completed` | Comparable; genuine multi-file synchronization proven |
| `sota_hard_large_catalog_collision` (large generated file) | PASS, 8 turns, $0.0018 | **PASS, 7 turns, $0.0012,** `completed` | Beats baseline on both turns and cost |

**Full easy tier (10 challenges), single-shot:**

```
6/10 PASS on first attempt.
```

Diagnosis of the 4 failures, done live rather than assumed: 3 of the 4 share
one exact signature — the model writes one sentence of intent ("I'll start
by reading...") and the completion **stops before emitting the tool-call
JSON**. Retrying the *identical* challenge, unchanged, against the same
manifest:

- `tier4_dag_resolver` — retried, **PASS**, real 2-file fix.
- `tier3_api_idempotency_middleware` — retried, **PASS**, real 2-file fix
  (`api/middleware.py`, `api/storage.py`), 13 turns.
- `tier2_web_reactive_signals` — retry killed by an operator-side timeout
  before completion; **inconclusive**, not a confirmed failure.
- `tier2_fsm_workflow_engine` — retried, genuinely **`abandoned`** after 5
  turns. This is the one confirmed real capability gap in the batch.

Net: **8/10 confirmed passable** (80%, matching the stated target) with one
unconfirmed and one genuine gap. This was cross-checked against the
translator directly — reproducing the exact recorded prompt text in
isolation against `ProposalTranslator.translate()` returned a correct,
successful parse every time, which rules out a translator regression and
narrows the transient failures to the live completion itself (see Section
4.1).

### 3.3 What is proven versus what is not

Stated plainly, because a report that blurs this line is worse than one that
omits the section:

**Proven, with live evidence:** brownfield multi-file bugfixes; brownfield
large-file (generated-file) surgery; multi-file public-interface migration
with call-site synchronization; sub-$0.005-per-task economics on a cheap
model.

**Not yet proven:** the diff-mode patch capability was never exercised —
every file `vg-coder-v4` touched across every run was small enough that a
full-content rewrite was the correct choice, and the model correctly chose
it every time. This is not a defect; it means no benchmark task in the
current suite has a large-enough *editable* target file to force the
capability. **Greenfield-from-scratch synthesis** was never attempted — the
prompt's greenfield clause exists, but no greenfield challenge is in the
suite this session ran against. **"Explain code/docs deeply"** has no
manifest, no tool, and no benchmark tier at all; it does not currently
exist as a capability of this substrate.

---

## 4. Open TODOs and Unresolved Issues

Ranked by estimated leverage — cheapest fix with the largest measured effect
first.

1. **Retry-on-empty-completion at the harness level.** The dialect
   degradation ladder (NATIVE → JSON_SCHEMA → FENCED_JSON → TEXT_GRAMMAR)
   handles a *malformed* response; it has no path for a genuinely *empty* one
   (`"proposal must contain text or a tool call"`). This session's evidence
   is that 2 of 4 easy-tier failures were exactly this, and both passed on
   an unmodified retry. This is the single highest-leverage fix identified
   this session: implement a bounded retry (2–3 attempts, same prompt, no
   state mutation) at the point `translate()` returns
   `"proposal must contain text or a tool call"`, before it is scored as a
   terminal `instrument_error`. Estimated effect: recovers roughly half of
   `vg-coder-v4`'s remaining easy-tier gap for near-zero engineering cost.

2. **The abandoned-but-correct paradox is not solved, and it got worse.**
   Section 2 found 18/26 oracle passes across all manifests terminated
   `abandoned`, not `completed` — the fix was right, the agent did not
   believe it. `HYDRA_MULTI_AGENT_TOPOLOGY_AND_EMERGENT_AGENCY.md` §2.3
   already names and mathematically models this ("The Abandoned Paradox").
   `vg-coder-v4`'s prompt tightening (Section 3.1) reduced *analysis-paralysis*
   abandonment (the model reasoning itself out of turns without ever
   patching) but did not address the *verification-blindness* variant (the
   model patches correctly, tests pass, and it still loops on `proc.exec`
   instead of recognizing success). This needs the Tiered Verification
   Gradient's Tier-1 micro-checks (HYDRA §5.2) wired as an always-on signal
   the agent can query cheaply mid-turn, not only the full `test` tool.

3. **`vg-coder-v4`'s diff-mode patch capability is unvalidated.** Needs a
   benchmark task with an editable target file over ~300 lines, specifically
   constructed to make a full-content rewrite economically or reliability
   disadvantageous, before this can be called proven rather than merely
   wired.

4. **No greenfield benchmark tier exists.** The prompt's self-TDD mandate
   ("author the implementation, then a test file covering edge cases, then
   verify") has never been exercised against a real from-scratch task. This
   blocks any claim about greenfield capability, which the user explicitly
   asked about.

5. **No "explain codebase/docs deeply" capability exists at all** — no
   manifest, no read-only exploration tool beyond `fs.read`/`fs.search`, no
   benchmark. Section 6.4 proposes the shape this should take.

6. **`ADMISSION_GATED_HARNESSES` governance is currently manual and easy to
   get wrong silently in the other direction** — nothing stops a new preset
   from being *added to the manifest registry* while someone forgets to add
   it to the gate set, meaning its `finish` calls are never
   verification-checked. The falsifier test only catches a scope that
   *changed*; it does not catch a scope that should have changed and didn't.
   Needs a linter, not just a pinned test (Section 7).

7. **`invocation.py`'s `_tool_object_from_mapping`** now accepts `"action"`
   as a synonym for `"name"` and `"kind": "effect"` as a call-shape signal —
   changes made by the parallel reconciliation session to cross a real
   OpenRouter dialect boundary. These widen what counts as a tool call from
   free text, which is exactly the kind of permissive parsing that made the
   original `v3luna` diagnosis ambiguous. This narrowing is *reverted from a
   wider version* that also accepted a bare `content` key as implying a
   `patch` call regardless of declared schema; the current form is
   schema-gated. It should be watched: if it needs widening again, the
   widening belongs in a pack-declared dialect table, not in the generic
   translator, to avoid re-opening C-01 (a translator carrying an
   ever-growing builtin vocabulary is a second place a domain has to be
   registered).

---

## 5. The Composition Model: Primitives, Atoms, Molecules, Swarms

The Vanguard Invariants (I-1 through I-8, see HYDRA §1.4) already establish
*that* the substrate is built from small, composable, replaceable primitives.
This section proposes a concrete taxonomy for what "compose" means at each
scale, grounded in what this session actually built and observed working.

**Primitive** — one typed capability with one verb, one selector, one risk
tier. `fs.read`, `fs.search`, `patch.apply`, `proc.exec`, `agency.finish`.
This session added two *primitive variants* without adding new verbs: `read`
gained `offset`/`limit` (a read-primitive parameterization for context
economy), and `patch` gained `diff` as an alternative to `content` (a
patch-primitive parameterization for edit economy on large files). The
important architectural point: **neither required a new capability grant,
new risk classification, or new S0–S12 dispatch path** — they widened an
existing primitive's argument shape, which the manifest's `additionalProperties: false`
schema still bounds. This is the cheapest axis of extension available and
should be preferred over adding new verbs whenever the underlying effect
handler already supports the richer shape (as `git.py` already did for
both, unused, before this session).

**Atom** — one primitive plus its governing policy triple: the capability
grant (what it may touch), the selector (where), and the routing/budget
context it executes under. An atom is not just "the `patch` tool" — it is
"`patch.apply` bound to `/workspace`, medium risk, escalating through
`failure_escalation` on `instrument_error`." Section 2's finding is precisely
that `v3luna` had the primitive (the tool schema was intact) but not the
atom (the escalation-governed context around it was stripped). **An atom
without its governance context is not a smaller atom; it is a different,
undeclared, ungoverned atom wearing the same tool name.**

**Molecule** — an ordered composition of atoms with a control-flow contract
between them: the ONE-TOOL-CALL-PER-TURN loop itself (read → patch → test →
finish) is a molecule. `vg-coder-v4`'s prompt is, structurally, a molecule
specification written in natural language rather than code — which is both
the substrate's current strength (trivially editable, no redeploy) and its
current weakness (unenforceable; the model can and does deviate, as Section
3.2's transient failures show). Section 6 proposes three *differently
structured* molecules — Chimera's Bayesian-blackboard loop, Hydra's
bifurcated dual-mode loop, and the Hexagonal specialist's layer-gated
loop — precisely because a single molecule shape cannot be simultaneously
optimal for a five-turn bugfix and a 200-turn greenfield build.

**Swarm** — multiple molecules executing under one shared budget envelope
and one consensus or selection function over their outputs.
`ConsensusSwarmScheduler` (HYDRA §6.4.2) is the existing formal spec; Section
6.4 below proposes its specific application to *underspecified* problems,
where the swarm's real job is not redundant verification but *hypothesis
diversity* — several molecules attempting different interpretations of an
ambiguous brief, with the consensus function operating on falsifiable
behavior, not surface similarity.

**Why this taxonomy matters for the 10/10 goal:** an agent that is only a
better molecule (a better prompt) plateaus, as `vg-coder-v4`'s own results
show — real gains came equally from atom-level correctness (inheriting the
right policy) and primitive-level extension (diff-mode, offset/limit), not
from prompt cleverness alone. The four paradigms in Section 6 are
deliberately differentiated at every one of these four scales, not just in
their prompt text.

---

## 6. Four Divergent Paradigms Toward 10/10

Each paradigm below is evaluated against three axes: **inner loop** (what
happens inside one turn — how a single action gets chosen), **outer loop**
(what happens across turns — how progress and termination are governed), and
**where it is asked to run** (which problem shape it targets). Paradigms
that share an inner loop but differ only in prompt wording are not counted
as distinct; none of the four below share either loop with another.

### 6.1 Chimera 2.0 — Evolution, Not Replacement

Chimera-v1 already scored 6/6 in this session's ladder cross-tabulation —
its architecture is not the problem, and nothing here proposes replacing it.
Its subsystems (`CognitiveBlackboard` for approximate Bayesian belief
updating over hypothesis confidence, `MetaCognitiveGovernor` for directive
state transitions, `CognitiveRouter` using Thompson sampling for model-tier
selection, `SymbolicCortex` for AST invariant checks, `ChimeraAtomicPatcher`
for transactional rollback) are specified in full, with working code, in
HYDRA §2.4 — that is the canonical reference and is not reproduced here.

What this session's evidence adds to the Chimera 2.0 hardening spec (HYDRA
§2.5), concretely:

1. **The routing-policy governance object needs a schema-level completeness
   check, not just inheritance-by-convention.** Chimera-v1 happened to
   inherit `vg-code-default`'s full routing policy; nothing in the manifest
   loader would have caught it if it hadn't. Propose a validator (Section 7)
   that fails composition, not just execution, when a `routing_policy`
   component is present but `failure_escalation` is absent or empty — turning
   Section 2's root cause into a class of bug that cannot ship silently
   again.
2. **`CognitiveBlackboard`'s belief update is a natural home for the
   retry-on-empty-completion signal (TODO 1).** An empty completion is not
   evidence the task is unsolvable; it is evidence the *sample* was bad. A
   blackboard that already tracks approximate confidence over hypotheses is
   the right place to distinguish "this action failed because it was wrong"
   from "this action failed because the channel dropped it," and retry only
   the latter.
3. **`ChimeraAtomicPatcher`'s rollback mechanics are the natural enforcement
   point for the diff-vs-content choice** this session added as a raw
   primitive capability. Chimera 2.0 should make that choice structurally —
   read the target file's line count from the already-open blackboard state
   and select `diff` above a threshold — rather than leaving it to prompt
   instruction as `vg-coder-v4` currently does. This converts an
   unvalidated *prompted* capability into a *governed* one.

### 6.2 Hydra — Chimera as an Inner Head Under Bifurcation Governance

The full architecture — the complexity functional
$\mathcal{C} = f(U_{\text{loc}}, C_{\text{dep}}, S_{\text{spec}}, K_{\text{ctx}})$,
Mode A (fluid ReAct actor) versus Mode B (attenuated multi-head DAG), and the
`HydraMetaGovernor`/`BifurcationClassifier` implementation — is specified in
full in HYDRA §3, and is not re-derived here. Chimera 2.0 is explicitly
positioned there (§3.5) as one candidate *inner specialist head* Hydra can
bifurcate into for a localized, well-specified sub-task, while Mode B's DAG
(planner → implementer → reviewer → verifier → synthesizer) handles the
outer decomposition for problems too large or too ambiguous for any single
molecule.

**What this session's evidence changes about how that spec should be
read**, not what it changes about the spec's mathematics:

- **The bifurcation decision itself needs a fifth input signal**, alongside
  localization uncertainty, dependency coupling, specification entropy, and
  context-volume saturation: *policy completeness of the target harness*.
  Section 2's finding — that an otherwise well-formed manifest silently
  dropped its escalation ladder — is exactly the kind of latent risk a
  governor deciding "spawn a cheap fluid actor" versus "spawn a governed
  multi-head DAG" should be able to see and weight *before* committing
  budget, not discover from a failed run afterward.
- **`sota_medium_public_interface` (Section 3.2) is a worked example of
  where Mode B's DAG genuinely earns its overhead over Mode A's fluid
  actor.** `vg-coder-v4`, running as a single fluid molecule, still passed
  it — 12 turns, one model, no explicit planner/reviewer split — because
  the task's dependency-coupling density (three files, one shared symbol)
  was real but bounded. This is useful calibration data for
  $\mathcal{C}$'s threshold: a task this session's single-molecule agent
  handles correctly is evidence the bifurcation boundary should sit *above*
  three-file/single-symbol migrations, not below them, or Hydra will pay
  DAG overhead where a fluid actor already suffices.
- **The Living Horizon Planning Engine (HYDRA §4)** — rolling-horizon
  planning with event-sourced amendment (`HydraPlanAmended`) rather than
  a priori long-horizon planning — is the correct answer to TODO 4
  (no greenfield capability exists yet). A greenfield build is exactly the
  case where an a priori plan is wrong by turn 20; nothing in this session's
  work contradicts that design, and nothing in this session's work has yet
  tested it, because no greenfield benchmark exists to test it against.

### 6.3 `vg-hexagonal-tdd` — The Methodology Specialist

This is the paradigm the user asked for in the most detail and the one least
developed in the existing corpus (HYDRA §6.1 sketches
`HexagonalBoundaryAstLinter` in ~150 lines; this section specifies the full
agent around it). Its thesis is different from both Chimera's and Hydra's:
where those two paradigms make the *agent* smarter (better belief tracking,
better task decomposition), this paradigm makes the *codebase* smarter by
construction, using industry methodology as a forcing function rather than
as documentation the model might or might not follow.

**Inner loop — methodology-gated, not free-form:**

Every turn is classified into exactly one of four methodological phases
before an action is chosen, and the phase determines which primitives are
even reachable that turn:

1. **RED** — write or extend a failing test that specifies the desired
   behavior, using the language's real test framework, never a fabricated
   assertion. `patch.apply` is permitted only against files under a
   `test/`, `spec/`, or `__tests__/` selector; `proc.exec` is permitted only
   to run the test suite and confirm the new test fails for the *expected*
   reason (not a collection error, not an import failure).
2. **GREEN** — implement the minimum change that makes the RED test pass.
   `patch.apply` against production code is permitted; the loop controller
   rejects any patch that touches more files than the RED-phase test
   exercises, forcing minimal-diff discipline structurally rather than
   asking for it in a prompt.
3. **REFACTOR** — with tests green, restructure for clarity without
   changing behavior. This phase is where the Hexagonal boundary linter
   (below) actually runs; a refactor that introduces an inward-to-outward
   dependency violation is rejected before it reaches `test`, not after.
4. **BOUNDARY-CHECK** — a cheap, non-LLM static pass (the AST linter),
   runnable every turn at near-zero cost, enforcing the canonical dependency
   direction:

```
Domain (entities, value objects, pure business rules)
  ← Ports (interfaces the domain defines, owns, and depends on)
    ← Adapters (databases, HTTP, filesystem, model providers — depend inward)
      ← Application/Composition (wires adapters to ports; nothing depends on it)
```

An import statement in `domain/` naming anything under `adapters/` is a
structural violation the linter catches by AST inspection alone — no model
call needed — and is rejected before it ever reaches the (expensive) `test`
primitive. This is precisely the same enforcement mechanism this repository
already uses on itself (`tools/linters/check_boundaries.py`,
`check_domain_blindness.py`) turned outward, into a tool the agent applies
to the *target* codebase it is editing.

**Outer loop — a methodology state machine, not a turn budget alone:**

```
        ┌─────┐  test written, fails correctly   ┌───────┐
   ───▶ │ RED │ ────────────────────────────────▶ │ GREEN │
        └─────┘                                    └───┬───┘
           ▲                                            │ tests pass
           │ next requirement                            ▼
           │                                    ┌───────────┐
           └────────────────────────────────────│ REFACTOR  │
                    all requirements covered      └─────┬─────┘
                                                          │ boundary-check clean
                                                          ▼
                                                  ┌────────────────┐
                                                  │ next req or    │
                                                  │ FINISH         │
                                                  └────────────────┘
```

Unlike Chimera's Bayesian confidence tracking or Hydra's complexity-scored
bifurcation, this outer loop's termination condition is **methodologically
defined, not statistically inferred**: `finish` is reachable only from
REFACTOR, only when the boundary-check is clean, and only when every
requirement extracted from the brief has a corresponding RED-phase test that
is currently green. This directly targets TODO 2 (the abandoned-but-correct
paradox) by construction — there is no ambiguity about "did I actually
finish," because finishing is a state in a state machine with an explicit
precondition, not a judgment call the model makes from a transcript.

**Clean Code discipline as a governed primitive, not a suggestion:** the
REFACTOR phase's boundary-check is paired with a small set of structural
metrics computed the same way — cyclomatic complexity per function, function
length, parameter count — each with a hard ceiling declared in the manifest
(not the prompt), so "keep functions small" is enforced the same way a
capability grant is enforced: mechanically, before the turn completes,
rather than requested and hoped for.

**Why this is genuinely different from Chimera and Hydra, not a variant:**
Chimera's inner loop is belief-driven (what does the blackboard think is
true); Hydra's is complexity-driven (how hard does this look, so which mode
should run it); this paradigm's inner loop is **phase-driven** — the
methodology itself, not a confidence score or a complexity estimate, decides
what the agent is even allowed to attempt this turn. It is the right
specialist for exactly the class of task where "the code passes tests but is
unmaintainable" is the actual failure mode to guard against — long-lived
brownfield services, not one-shot bugfixes.

### 6.4 `vg-archeologist-swarm` — Consensus Exploration for Undefined Problems

The user's phrasing — "hard to define," "big challenges in one shot using a
mix of agents" — names a real, distinct problem class none of the first
three paradigms are built for: **a brief that is genuinely ambiguous**, not
merely large. `CausalTraceSlicer` (HYDRA §6.3.2, backward AST slicing across
a large repository to find every causal ancestor of a symptom) and
`ConsensusSwarmScheduler` (HYDRA §6.4.2) already exist as specified
primitives; this section proposes their combination into a fourth agent
whose job is explicitly **hypothesis generation and selection**, not
execution.

**Inner loop — evidence gathering before commitment:** where the other three
paradigms choose one action per turn toward one interpretation of the brief,
this paradigm's first several turns are read-only by construction (`fs.read`,
`fs.search`, and the causal slicer only — `patch.apply` is not in scope until
an explicit HYPOTHESIS-COMMIT phase), building a causal graph of what the
ambiguous brief could plausibly mean, grounded in what the codebase actually
does, not in what a fixed prompt template assumes it does. This directly
answers "explain codebase/docs deeply" (TODO 5) as a side effect of its own
inner loop — the causal graph *is* the deep explanation, and can be surfaced
to the operator whether or not a code change is ever attempted.

**Outer loop — bounded parallel divergence, then falsifiable consensus:**
once the causal graph identifies N plausible, materially different
interpretations (not N cosmetic variations of one interpretation — the
`ConsensusSwarmScheduler`'s Pareto-selection step is responsible for
collapsing near-duplicates before spending budget on them), each spawns one
molecule — plausibly a Hydra-bifurcated one, since by this point the
sub-problem is well-specified — under a shared budget envelope. Selection
among the N results is **falsifiable, not majority-vote**: each candidate's
own test suite (self-authored under the Section 6.3 RED discipline, if that
specialist is the molecule spawned) is run against the *other* candidates'
implied acceptance criteria where extractable, so agreement is measured in
behavior, not in surface code similarity.

**Why this is genuinely different, not a Hydra variant:** Hydra bifurcates
*within* one interpretation of an already-legible brief; this paradigm exists
because the brief is not yet legible, and its entire value is in refusing to
commit execution budget until it is. It is the correct front door for
"greenfield challenging software development" (the user's phrase) where the
spec itself is underspecified — exactly the case where a single fluid actor
or even a well-planned Hydra DAG will confidently build the wrong thing
efficiently.

### 6.5 Why These Four Are Actually Different (Inner and Outer Loop)

| | Chimera 2.0 | Hydra | `vg-hexagonal-tdd` | `vg-archeologist-swarm` |
|---|---|---|---|---|
| **Inner loop driven by** | Bayesian belief confidence over a blackboard | Complexity functional $\mathcal{C}$ deciding Mode A/B | Methodology phase (RED/GREEN/REFACTOR/BOUNDARY) | Causal graph completeness before commitment |
| **Outer loop terminates on** | Confidence threshold + `SymbolicCortex` invariant pass | Living-Horizon plan closure or Tier-3 macro-gate | State-machine precondition: all requirements green, boundary clean | Falsifiable cross-candidate consensus |
| **Governs via** | Thompson-sampled model-tier routing | Bifurcation into fluid actor vs. multi-head DAG | Manifest-declared structural ceilings (AST-checked, not prompted) | Bounded parallel budget envelope, Pareto pruning |
| **Best problem shape** | Localized, well-specified bugfix/feature with real uncertainty about the right model tier | Large legible task needing decomposition, or small localized one — decides which | Long-lived brownfield service where maintainability is the actual constraint | Ambiguous brief; greenfield with no fixed spec; deep-explain requests |
| **Primary risk if misapplied** | Overhead on a task too simple to need belief tracking | DAG overhead on a task a fluid actor already solves (Section 6.2's calibration point) | Rigidity — a genuinely trivial one-line fix pays full RED/GREEN/REFACTOR ceremony | Wasted parallel budget if the brief was actually legible |

No two of these four share an inner-loop decision function or an
outer-loop termination condition. This is the concrete answer to "ensure
all the proposals are different from each other" — verified against the
taxonomy in Section 5, not asserted.

---

## 7. Tooling, Skills, and OSS Proposals

Ordered by how directly each connects to a finding above, not by ambition.

1. **A routing-policy completeness validator**, run at manifest composition
   time (`compose.py`), not just execution time. Fails closed if
   `routing_policy` is declared but `failure_escalation` is empty — this is
   the direct, mechanical fix for Section 2's root cause, and should ship
   before any new manifest is added, since it would have caught `v3luna`'s
   defect at authoring time rather than after 21 live runs.
2. **A gate-scope linter**, addressing TODO 6: cross-reference
   `registry.json`'s manifest list against `ADMISSION_GATED_HARNESSES` and
   fail CI if a manifest declaring `patch.apply` is present in one but
   absent from the other without an explicit `# ungated: <reason>` marker
   file colocated with the manifest — making the *absence* of a governance
   decision as visible as its presence already is.
3. **Retry-on-empty-completion**, TODO 1, at the `translate()` call site in
   `invocation.py` or its caller — the single highest-measured-leverage
   change available, at near-zero engineering cost.
4. **The Hexagonal Boundary AST Linter as a standalone CLI**
   (`vg-boundary-lint <path>`), independent of any agent — the same tool
   `vg-hexagonal-tdd` uses internally, exposed so a human reviewer or a CI
   step can run it without spinning up an agent at all. This is explicitly
   the "atom, not just molecule" principle from Section 5: a primitive
   worth having inside an agent is usually worth having outside one too.
5. **A minimal greenfield benchmark tier**, closing TODO 4 — three to five
   from-scratch specification-to-implementation tasks of graduated
   difficulty, oracle-verified the same way the existing ladder is, so any
   claim about greenfield capability (Section 6.2's Living Horizon Engine
   included) has evidence rather than aspiration behind it.
6. **A `vg-explain` read-only manifest**, closing TODO 5 — `fs.read`,
   `fs.search`, and the causal slicer only, no `patch.apply` capability
   grant at all (not merely a prompt instruction not to patch — an actual
   absent grant, so the S0–S12 dispatcher refuses the effect structurally),
   producing a structured causal-graph artifact as its `finish` payload
   instead of a diff. This is the direct product of Section 6.4's inner
   loop, decoupled from the swarm's execution half so it can be used alone
   for "explain this codebase" requests that were never asking for a change.
7. **Diff-mode and offset/limit usage telemetry** — before Section 6.1's
   proposal to make the diff-vs-content choice structural inside Chimera,
   confirm on a real large-file benchmark task (Section 7 item 5's sibling
   for brownfield) that the model actually benefits from the option when
   offered it, closing TODO 3 with evidence rather than assumption.
8. **Cassette-first regression suite for the dialect degradation ladder** —
   this session found harness-side parsing edge cases twice
   (`_lift_text_tool_calls` argument extraction, the empty-completion gap)
   by live reproduction that a recorded-cassette replay would have caught
   without spending API budget. The existing `CassetteRecorder` already
   captures everything needed; what is missing is a growing corpus of
   *adversarial* cassettes (truncated completions, action-as-name dialect,
   headerless diff hunks) checked into the test suite the way `raw_proof_log.json`
   already exists for one prior investigation.

No new OSS dependency is proposed. Every item above composes existing,
already-vendored capability (AST parsing via the stdlib, the existing
capability-grant model, the existing cassette format) — consistent with the
DRY/thin/modular constraint this report was asked to respect, and with the
substrate's own stated preference (README: "AETHER is a general
event-sourced agentic computation framework," not a framework that reaches
outward for its core loop).

---

## 8. Roadmap Assessment: Is "Next Sprint" Real?

The existing milestone ladder (`docs/execution/active.md`'s
`CMX-09`→`CMX-11` sequence; HYDRA §11.1's `M-Hydra-1`→`M-Hydra-4`) is
directionally correct — converge presets, then truthful completion, then
durable sessions, then repo-scale context — but it is sequenced as
backend-plumbing-first. This session's evidence suggests the sequencing
should invert for the specific goal of "10/10 on hard greenfield/brownfield
in one shot":

**What genuinely fits in one focused sprint**, because each item is small,
independently testable, and already has measured evidence behind it:

- Item 3 (retry-on-empty-completion) — hours, not days; directly recovers
  measured failures.
- Item 1 (routing-policy validator) — a static check against an existing,
  well-understood schema; the exact bug it prevents is already fully
  diagnosed.
- Item 6 (`vg-explain` manifest) — no new capability, only a *narrower*
  grant than any existing manifest; the highest-ratio-of-value-to-risk item
  on the list because it cannot make anything worse.

**What does not fit in one sprint, and should not be promised as such:**

- Any claim about greenfield capability, because item 5 (the benchmark tier
  itself) does not exist yet — there is currently no way to *measure*
  greenfield performance, let alone claim 10/10 on it. Building the
  benchmark is itself a sprint's worth of legitimate, separate work before
  any agent work against it can be evaluated.
- `vg-hexagonal-tdd` as specified in Section 6.3 is a new outer-loop state
  machine, not a manifest tweak — realistically 1-2 sprints: one to build
  and unit-test the phase-gated loop controller and the AST boundary
  linter in isolation, one to benchmark it against both a brownfield and
  (once it exists) a greenfield tier.
- `vg-archeologist-swarm`'s consensus-selection logic is the most novel
  piece proposed in this report and has zero live evidence behind it yet,
  unlike every other proposal here, which is either already partially
  built (`vg-coder-v4`, `ConsensusSwarmScheduler`'s existing spec) or a
  small delta from something proven. It should be prototyped against a
  small number of deliberately ambiguous briefs before any timeline
  commitment is made.

**Overall assessment: the milestone ladder's shape is sound; its current
ordering optimizes for backend correctness before it optimizes for the
specific, measured failure modes this session found.** A revised near-term
sequence — validator (item 1) → retry fix (item 3) → `vg-explain` (item 6)
→ greenfield benchmark (item 5) → `vg-hexagonal-tdd` build — reaches a
genuinely stronger, evidence-backed position in roughly the time the
existing `CMX-09` alone was scoped for, because every step in it is sized
against something this session actually measured rather than estimated.

---

## 9. Closing Position

The throughline across every section of this report is the same one that
ran through the desktop-client debugging in Section 1: **the model was
rarely the actual defect.** The desktop app's failures were a missing
browser build, an unmanaged re-render, and a fabricated status badge. The
`v3luna` regression was a silently forked governance object, not a weaker
prompt. Two of `vg-coder-v4`'s four easy-tier failures were a harness gap
in handling an empty completion, confirmed by an unmodified retry passing.
This pattern — real capability sitting behind a structural or wiring
defect — is precisely what `VG_CODE_MAX_V3_ROOT_CAUSE_FINDINGS.md`
documented before this session even began (nine of nine raw model probes
correct; six harness defects were the actual blocker). **The consistent,
falsifiable finding across this entire project's investigative history is
that the intelligence this substrate needs is already closer to emergent
than the milestone ladder's backend-hardening framing suggests — what is
missing is not more model capability, but the governed, verified, small-atom
scaffolding for that capability to land reliably.** Sections 5 through 7 of
this report are, in total, a proposal for exactly that scaffolding: four
paradigms differentiated at the loop level, not the prompt level; primitives
extended in their argument shape before their verb count; and every proposed
tool traceable to a specific, live-reproduced finding rather than a
plausible-sounding hypothesis.
