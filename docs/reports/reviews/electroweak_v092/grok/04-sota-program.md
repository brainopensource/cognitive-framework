---
id: report.electroweak-v092.grok.sota-program
canonical_id: report.electroweak-v092.grok.sota-program
class: report
authority: non-canonical
truth_plane: PROPOSED
status: snapshot
implementation_status: NOT_AUTHORIZING
owner: grok-principal-architect-review
purpose: >
  What I would actually do to make Coding Max and the Aether substrate capable
  of hard SWE (greenfield multi-file, long runs, brownfield blast radius) and
  to make the framework better at building agents. 10-step order aligned with
  MS-TRUTH → RESUME → SEE → CHANGE → CONTROL → outer. Decisions, not slogans.
audience: [architect, release-owner]
last_verified: "2026-09-04"
pin_head: "5243866bc169c7f60cc7d4f74b9a853f60356381"
relationships:
  - report.electroweak-v092.grok.index
  - execution.milestones
  - execution.tasks
---

# 04 — SOTA program: what I would do

This is the action document. It does **not** authorize T-04. It says what a
CTO should decide, in order, and what “SOTA” honestly means for this tree.

SOTA for Aether is **not** “beat Claude Code on Twitter.” It is:

> A structurally untrusted model, on one EpisodeEngine, that cannot admit
> `completed` without a typed exterior oracle; that can resume a crash
> without duplicate effects; that can change 40 implicated files without
> mutating tests; that can scaffold a greenfield so stubs fail before
> implementations pass; and that can run a week of work as a campaign of
> honest episodes rather than one amnesiac chat.

Official DeepSWE / SWE-bench is G-3 **measurement** of that, not the
definition.

---

## 1. Build order (10 steps)

Aligned with **MS-TRUTH → (RESUME already CLOSED) → SEE → CHANGE → CONTROL
→ outer**. TCB ≤ 1438 and I-7 constrain every step (T-35, T-64).

### Step 1 — MS-TRUTH remainder as a governance decision

**T-04 / T-05 / T-07.** Record RF-25 successor baseline **before** shrinking
`ADMISSION_GATE_EXEMPT`. Delete or honor `ADMISSION_GATED_HARNESSES`. Bind
verification **command** as subject.

Falsifier already named (`tasks.md`): `vg-code-default` + `finish` + no
patch ⇒ not completed.

**Until this, do not claim the product agent cannot lie.**

Decision, not slogan: either `vg-code-default` is a debug harness (then
**product docs and arms must not use it**), or it is a product pack (then
it is gated). The current fork is how lying `completed` survives.

### Step 2 — Wire T-18 tamper into `_admit_completion`

Module is live; session call is not. Brownfield agents that edit assertions
must die at admit, not in a blog post. Shield the verification subject and
implicated test files — do not glob `test/**` as the entire enum.

### Step 3 — Bind implicated-set + targeted tests as the verification subject

T-20 facts into session; IndexPort `tests()` / `dependencies()` only. Empty
primary + coverage 1.0 already rejected in pack policy — **if** those
observations are passed. Today they are not. Completeness treating
`surface = changed` is the 40-file hole.

### Step 4 — Greenfield evidence honesty (T-19 / T-63)

Session must record stub-fail then impl-pass, not alias both to
`verification.passed`. Relax or kill the prompt law “do not read first” for
any task that is not a single-file TASK.md toy. Put the file DAG in σ
(`TaskStep` exists).

### Step 5 — MS-SEE leftover: T-46 stays out of IndexPort

If you need phase-aware snippet order, it is pack `context_ranker.py`,
identity in `selection_policy_identity`, never “the index decided.” Do not
close MS-SEE on ranking.

Also in this step, cheap and load-bearing: **sectioned file viewer** using
existing `SectionAddress`; **cache-hit telemetry** on the ledger so L1–L3
freeze can prove it pays rent.

### Step 6 — MS-CHANGE leftover: T-47 first

Read-before-edit at the **effect boundary** + typed conflict recovery
(`PATCH_PREIMAGE_MISMATCH` → forced `fs.read` → retry). Then T-48 circuit
breaker after you can detect \(d_t = d_{t-2}\). Then T-49 checkpoints after
2PC is the default write for a **node**, not only N>1 diffs.

**Do not close MS-CHANGE on dialect tickets** (`milestones.md`). Dialect is
already `[x]`.

Consider 2PC (or an equivalent atomic node commit) for the single-file path
that is actually used, or batch a DAG node’s files so N=1 sequential syntax
receipts cannot be “success.”

### Step 7 — Honest event producers

If fold never sees `HypothesisRejected`, compaction cannot pin dead ends.
Emit the events the fold already names. Reconstruct the prompt from the
ledger. This is harness engineering, not a new agent. Without it, long
context is a sliding window with a 240-char goal echo.

### Step 8 — MS-CONTROL: T-26 then T-27

Frozen preregistration; canary disposition in `{POSITIVE, NEGATIVE,
UNDETERMINABLE, INVALID}`. T-23 ≠ control. **Decision:** no specialist /
campaign / memory lift claims before this canary. This is how you stop
shipping SONNET paradigms and HYDRA governors as “the next sprint.”

### Step 9 — Outer, in this order

1. T-29 investigator (no `patch.apply`) as an **ablation** vs T-27 control
2. T-30 merge-by-tests (never LLM vote)
3. T-31 director + CAS (zero mutating tools); worktree per writer
4. T-32 memory grants (authorize-before-retrieve; generator ≠ evaluator ≠
   promoter)
5. T-28 meta only as paired study
6. T-59 operator interrupt UX (cancel/pause/resume from ledger)
7. T-55 HYDRA last and **off-by-default**
8. T-33 official DeepSWE wrapper last (G-3)

Octopus `ORCH-*` eleven-pack layout is too much machinery for step 9. One
director client + event kinds on the existing ledger is enough. Progressive
cost.

### Step 10 — Product honesty on the three arms

Differentiate `vg-code-fast/balanced/max` by budget, model route, and
`max_turns` (and maybe retrieval budget), **or** stop advertising three
agents. Identical manifests are a product lie. Do not invent three
ontologies. Do not put Forge/Chimera back into product scores.

---

## 2. What I would change in the coding agent (concrete)

### Greenfield multi-file, multi-day

**Today:** prompt says don’t read; policy wants oracle-on-stub; session
doesn’t pass the fact; default pack can finish anyway.

**I would:**

1. Gate `vg-code-default` (step 1).
2. Make the first **admitted** greenfield episode a **scaffold+oracle**
   episode: write failing smoke, bind it as verification subject, refuse
   `completed` until that command has been observed red, then later green.
3. Put a file DAG in σ; one file (or one 2PC node) per turn; topological
   order from types/ports outward.
4. Worktree the whole campaign so day-3 crash ≠ dirty parent tree.
5. Kill “do not read first” except for a named toy profile.

### Brownfield 40-file blast radius

**Today:** implicated-set exists and is not fed; tamper unwired; verify can
be the wrong pytest; finish-time uninspected-file check is too late.

**I would:**

1. Forced reproduce (`proc.exec` of implicated tests) before first
   `patch.apply` on brownfield profiles — **not** via the phased ladder that
   forbids exec until after patch.
2. Callers as IndexPort observations into completeness. Surface ≠ changed.
3. Tamper on the verification subject.
4. Read-before-edit at apply time.
5. Surgical 2PC on the implicated set; fail-to-pass + pass-to-pass; postimage
   digest.
6. If the implicated set is huge, **campaign**: investigator episode
   (read-only) → writer episodes per subgraph → merge by tests.

### Long context (100+ turns)

**Today:** prefix freeze is right; compaction is recency; σ emission is
suspect; no cache telemetry; 240-char goal echo.

**I would:**

1. Instrument cache hits (prove L1–L3 freeze).
2. Honest Hypothesis/DeadEnd events so L4 pinning has content.
3. Distill at the effect boundary (already mostly there); recover via
   `fs.read` + section addresses.
4. Never splice retrieved RAG into L1–L3.
5. After ~N turns or token ceiling, **start a new episode** with restored σ
   rather than compacting the same transcript into mush. That is already the
   resume identity. Productize it as “continue campaign node,” not “keep
   chatting.”

### Long runs (hours, crash, resume)

**Today:** MS-RESUME CLOSED; no campaign; T-59 UX `[PROPOSAL]`.

**I would:** ship checkpoint/resume UX on top of existing σ **before** any
swarm. Operator cancel is kernel `CANCELLED`. Worktrees so a crashed writer
does not poison the parent. Campaign DAG so “hour 6 of 40” is node 12 of 18,
not turn 347 of one window.

---

## 3. What I would change in the framework (so it builds agents better)

The dual mission is (1) Coding Max and (2) the same substrate for other
agents. (2) is the actual Aether bet. Today it is real as **composition**
and weak as **product differentiation and honesty**.

### 3.1 Keep the hexagonal bet; stop paying for unused machinery

Pack + profile + tools + admission is the right atom. Progressive cost
(DEKAS force 4): a Q&A agent must not load 2PC, tamper, campaign, or HYDRA.
Compose them. Do not kernel-flag them.

### 3.2 Admission is the product

An agent without a gate is a chatbot. The framework should make **the
default pack gated**, and make “exempt” an explicit debug profile with a
name that cannot be confused with product (`vg-code-debug`, not
`vg-code-default`). That single naming/gating decision would do more for
every future agent than another topology paper.

### 3.3 Ports stay dumb; packs stay smart

IndexPort ranks nothing. MemoryPort retrieves nothing without a grant.
SandboxPort does not parse Python. Kernel does not know AST. This is how
you get a second domain (docs agent, data agent) without forking the TCB.

When people say “GraphOS,” translate: **observations on IndexPort + pack
policy**. When they say “soul,” translate: **versioned skill card**. When
they say “meta-cognition,” translate: **advisor that cannot admit**.

### 3.4 Events are how agents coordinate, not shared memory

Director, investigator, writer, operator: all clients of the ledger. No
Chimera blackboard. No “consensus chat.” Merge by tests. This is also how
you get polyglot later: the ledger is the contract, not Python objects in
RAM.

### 3.5 Observability before self-improvement

Do not build a flywheel that trains on lying `completed`. Honest producers,
trajectory distill, layer-attributed failure (HarnessFix law). Then, and
only then, held-out lift for memory (M-8) and optional HYDRA.

### 3.6 Three arms are budgets, not religions

The framework should make it trivial to vary **model route, token budget,
turn cap, retrieval budget, tool allowlist, admission policy** from a
manifest. That is how you “build agents better.” It is already the design.
It is not the current `vg-code-*` reality.

### 3.7 CLI is a client; stop confusing UX with the loop

Checkpoint/resume, worktree status, campaign DAG view, cost/cache
telemetry: client surfaces on `ApplicationService`. Do not put them in
kernel. Do not put them in Chimera.

### 3.8 What I would not do to the framework

- Second EpisodeEngine
- Kernel AST / LSP
- Ranking inside IndexPort
- HYDRA default
- Meta with budget or admit authority
- Auto-evolving harness
- Plugin verbs that bypass admit
- Treating `.draft/` or `docs/research/` as the board
- Closing MS-CHANGE on dialect, MS-CONTROL on T-23, MS-SEE on T-46
- Official leaderboard as DoD

---

## 4. Feedbacks (blunt)

**To the coding-agent owners.** You have a better substrate than most
vendor harnesses (capability kernel, ledger, prefix compiler, 2PC, resume
σ). You are losing on **settlement honesty and product differentiation**,
which are cheaper than HYDRA. Wire the modules you already wrote.

**To the research corpus.** DEKAS force ranking and the event-native loop
are the best pages in the tree. `future_improvements` “RATIFIED” badges and
the SOTA roadmap’s missing `compactor.py` have already wasted reviewer
trust. Stamp research `authority: non-canonical` in practice, not just
YAML.

**To octopus outer-loop notes.** Kernel-unchanged director is correct.
Eleven ORCH packs and an evolutionary policy are how you skip step 1–8.
Sequential director is the control; mutating-tool-free director is the
treatment; evolutionary is a lab.

**To SONNET four paradigms.** Composition vocabulary yes; four product
agents next sprint no. The session that found routing-policy bugs was
diagnosing **seams**, which is the right instinct. Fix seams (admit,
tamper, implicated facts) before new phenotypes.

**To meta-cognitive engineering.** Right as post-v1 laboratory. Wrong as a
reason to delay T-04. The universe in which theories compete only exists if
`completed` is an empirical event.

**To measurement.** Freeze T-26/T-27 before spending. G-3 forever. Wilson
lower bounds, missingness taxonomy, dirty-subject fail-closed — you already
specified this (T-01–T-03, T-25, T-40). Use it. Do not quote DeepSWE
percentages from research manuals as if they were this harness.

**To TCB.** Every “just a little kernel helper” is how I-7 dies. Put AST,
SBFL, GraphOS queries, and LLM summarizers in adapters/packs.

---

## 5. The two changes, again

**Inner (do first):** Make **settlement** the inner loop — admit on every
coding arm including `vg-code-default` (T-04 as an explicit
successor-baseline decision), **tamper on admit**, and **implicated tests as
the verification subject**, with patch conflicts recovering through re-read
rather than silent/fuzzy apply. That is the term in

\[
R = \prod_t \Pr(\text{honest progress}_t \mid \text{honest state}_{t-1})
\]

that is currently allowed to be 0.

**Outer (do only after that):** A **campaign director with zero mutating
tools**, children in **worktrees**, merge **by implicated-test verdict**
(read-only investigator optional). That is what turns multi-day greenfield
and 40-file brownfield into **many honest episodes**. Not HYDRA. Not
Chimera. Not a second `EpisodeEngine`.

If we do those two, and we do them in that order, this tree is in a position
to be actually SOTA as a **harness**: the thing that makes an untrusted
model finish hard software engineering without a lying `completed`.
Everything else is compounding — and compounding only helps after the
factors in \(R\) are honest.
