# 010 — V5 / Aether Roadmap & the ACI Harvest

**Status:** NON-NORMATIVE. Where this file and a v4 owner disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Owns:** what Vanguard harvests from the sixteen competitor/sibling harnesses, the cheap
adapter-level improvements available now, and the V5 architecture that follows the v0.4.3 MVP.
**Source:** `docs/reviews/done/vanguard_v042_and_v5_from_harness_src.md` (P3 in `009`), promoted
here because **no report in `001`–`008` covers it**.
**Authority cited:** `VG-02 §7 §11`, `VG-03 §2 §10 §12`, `VG-06`, `VG-07`, `GTS-13C` Ch. 3, `L-1`,
`L-6`, `ADR-0003`, `ADR-0006`, `ADR-0016`, `ADR-0019`, `DEF-03`, `DEF-04`, `DEF-09`, `MEM-7`.

---

## 0. The ruling this document carries forward

> **Do not rewrite Vanguard. Do not import competitor feature catalogues. Evolve in place.**

Sixteen harness trees were read line-level (`Harness-D-power/src/`). The finding is not that we are
behind — it is that **they are all the same loop with different skins**, and the three that are
genuinely instructive teach *discipline*, not features:

| Tree | What it actually teaches |
|---|---|
| `src/aether` (our own pre-v4) | How we already failed at control flow. Static topology `retrieve→architect→generate→apply→evaluate→repair→join`, `NODE_SOCKETS`, `WorkflowExecutor`. **Harvest the adapters (indexer, cassette, worktree); never the DAG** (`ADR-0003`, `REJ-01`) |
| `sagiha` (our hexagonal sibling) | Code-graph observations (`find_symbols`, `get_skeleton`, `impacted_by`), a gate evaluator isolated by import-linter, and an SFT exporter that **documents its own fatal gap**: it reconstructs messages without a tool-schema snapshot |
| `reasonix` | **Prefix stability > clever compaction.** Skill *names+descriptions* in a ≤4000-char cache-stable prefix; bodies load on demand; memory never mutates the prefix mid-session; `CompareShape` attributes every cache miss |
| `swe-agent` / `mini-swe-agent` | **ACI quality > scaffold size.** A 100-line file viewer, lint-on-edit and succinct grep beat "more agents". Maintainers now recommend the ~100-line variant, which matches the old agent's scores |

The rest — Grok Build, Kimi, Goose, OpenCode, Codex, OpenHands, DeepSeek Harness, Hermes, Prime —
are product surfaces, protocol adapters, or package sprawl. Several have **no OS sandbox at all**,
which makes Vanguard's rootless perimeter a genuine differentiator rather than catch-up work.

**Rewrite is licensed only if the kernel's dispatch algebra is proven inexpressible** (`ADR-0003`
reversal). Nothing in sixteen trees provides that proof; several provide the opposite.

---

## 1. What we must not copy — named so it can be refused

| Anti-pattern | Where seen | Rule it violates |
|---|---|---|
| Revive the workflow DAG because it "looks complete" | `src/aether` | `REJ-01`, `VG-03 §2` |
| Package explosion (`todo`, `terminal`, `subagent`, `web`, `workflow`, `typert`, `ralph`…) | DeepSeek Harness | `RSK-11` core drift; *"this is how a thin kernel dies"* |
| **In-loop skill self-writing** — skills rewrite the criteria they are judged by | Hermes Agent | `CL-1`, `REJ-04`, `A-05` |
| **LLM-as-judge fitness** over synthetic items generated from the artifact under optimisation | Hermes Self-Evolution `fitness.py` + `dataset_builder.py` | `CL-1`, `N-10`, `ADR-0015` |
| **REPL-as-universe** — unscoped Python as the default ACI | Prime Agent | `proc.exec` with extra steps; `A-03` |
| Policy-only permission prompts presented as isolation | OpenCode, Kimi, Goose | `NC-02`, `N-06`, `S1` |
| Rewrite the kernel in Rust "to be Codex/Grok" | — | `ADR-0006`, `006 §3` |
| Fork `EpisodeEngine` for parallel tools to win a reconstruction demo | — | **Falsifies `T7.6`** |

**The one to watch.** Hermes Self-Evolution has the *right pipeline shape* — offline, constraint
gates (pytest, size, no mid-conversation mutation), output as a PR never a direct commit. That is
`VG-07` L4 exactly. Its **judge** is an LLM scoring synthetic items derived from the very artifact
being optimised. **Steal the pipeline; replace the judge.** This distinction is the single most
important line in this document, because the pipeline is attractive and the judge is invisible.

---

## 2. The ACI harvest — cheap, adapter-only, available now

`VG-03 §7.4` freezes the atom set; none of these adds an atom. Each is an **adapter behaviour plus
a tool-schema line**, and each has published evidence behind it.

| # | Gift | Source | Implementation | Why it moves the needle |
|---|---|---|---|---|
| ACI-1 | **Paginated `fs.read`** — default 100 lines + offset | SWE-agent ACI §2 | Adapter + schema; prompt states the convention | Stops dump-and-drown; the single highest-value ACI change measured in the SWE-agent paper |
| ACI-2 | **Succinct `fs.search`** — file hits first, capped snippets | SWE-agent ACI §3 | Adapter | Matches what the paper actually measured |
| ACI-3 | **Empty-output acknowledgement** on `proc.exec` | SWE-agent ACI §4 | Receipt text | Models loop on silence; this is ~5 lines |
| ACI-4 | **Lint-on-patch as an observation receipt** | SWE-agent ACI §1 | Worker returns lint; a syntax failure is a **receipt**, never a verdict | Cheap signal that does **not** touch the evaluator (`A-05` preserved) |
| ACI-5 | **`AGENTS.md` / `CLAUDE.md` first-read** | OpenCode, Grok, Codex, Kimi | Already discovered by `agency/manifests/discovery.py`; ensure it reaches L3 | Highest-ROI convention in 2026 |
| ACI-6 | **`maxTurns` from `budget_policy`**, not an engine default | Claude SDK `max_turns` | Engine reads the frozen policy | Real bugs need >8 turns; `D-12` says a reconstruction needing 80 turns is a **budget artifact**, not a loop fork |
| ACI-7 | **Manifest aliases** `Read`/`Bash`/`Edit` | OpenCode/Claude names | Pack data, not `KNOWN_TOOLS` growth | Models are trained on those names |

**Status at `0238b1a`:** ACI-5 partially landed (`discovery.py` exists, `render_environment_text()`
is wired at `root.py:697-700`). ACI-6 is blocked on `budget_policy` being read (`005 §3`). ACI-7 is
blocked on the alias repair (`005 §4.1`). **ACI-1…ACI-4 are unstarted and are the cheapest quality
work available in the programme** — all four are Sprint 8 Lane B rows in `011`.

---

## 3. The Reasonix prefix discipline — without a Go rewrite

`VG-03 §12` already names prompt caching as *"the largest single cost lever"* and marks the 50–90%
figure **unverified here**. Reasonix is the best in-the-wild implementation of `VG-03 §10.2`, and it
gives us three rules and one metric:

| Rule | Reasonix mechanism | Vanguard form |
|---|---|---|
| A skills **index**, not skill bodies, rides the prefix | `IndexMaxChars = 4000`; names + descriptions only | `skill` artifacts: ≤4k-char L2/L3 index; bodies via `fs.read` of pack files |
| Memory and control input **never** mutate the prefix mid-session | Separate planner/executor sessions for cache isolation | `ContextCompiler` already freezes L1–L3 at construction — **we are ahead here** |
| New tools invalidate the prefix at ~10× miss pricing | Plugin lazy-load warnings | Registries freeze at composition (`A-11`) — **already correct** |
| **Attribute every cache miss** | `cache_shape.go` `CompareShape` → `system` / `tools` / `compact` / `snip` | **V5-L.** We currently measure *nothing* |

**The gap is measurement, not design.** Our compiler is architecturally correct and its cache-hit
rate has never been observed. `006 §7 S5` and `004 §5.4 C6` both raise this; it is one day of work
and it is the largest unmeasured lever in the system.

Also worth naming: **SWE-agent's `LastNObservations` explicitly breaks prompt caching.** Do not
import history elision into the context compiler. The compaction ladder in `ContextCompiler._fit`
is the correct shape precisely because it never rewrites the prefix.

---

## 4. V5 — the roadmap after the v0.4.3 MVP gate

V5 is **not** "Vanguard with every CLI feature." It is the first tag where the **middle and outer
loops exist as code, still outside the TCB.**

### 4.1 The three loops, and only one may touch running code

| Loop | Scope | Learning | Authority |
|---|---|---|---|
| **Inner** (episode) | Tools, tests, abstention | None | Every CLI already does this |
| **Middle** (harness artifacts) | Prompts, skills, routing, context policy | Candidate diffs | **Evidence-gated promotion; rollback tested first** (`L-05`, `L-06`) |
| **Outer** (weights) | SFT/DPO from opt-in trajectories | Offline | `MEM-7`, `DEF-09`; requires exact corpus (V5-A) |

> AGI-like behaviour, if it ever appears, is a **side effect of (2)+(3) under CL-1..3** — not a
> feature flag, and not a million sprints of adding MCP servers. `NC-01` stands.

### 4.2 Invariants carried into V5 unchanged

Capability + resource scoping (`S1`), evaluator exteriority, freeze-at-composition, `sinkClass`
mediation, `inconclusive` excluded from rates, coding is not the ontology, no scalar fitness, no
self-authored evaluation criteria.

### 4.3 V5-A … V5-M, in dependency order

| ID | Capability | Depends on | Note |
|---|---|---|---|
| **V5-A** | **Exact corpus.** Every `Recording` carries `toolSchemaDigest` + `contextCompilerDigest` + `manifestDigest` | `RandomPort`/`ClockPort` (S8) | **This is the one that cannot slip.** Sagiha shipped an SFT exporter and documented that it reconstructs messages *without a tools snapshot* — copy the exporter, never the gap. Without this, *"200 years of traces are sludge"* |
| **V5-B** | **Observation graph** — `find_symbols`, `get_skeleton`, `impacted_by` as observation verbs or `fs.search` modes | V5-A | Tree-sitter stays **in the worker** (`D-14`, `ADR-0006`). Must earn its place against `vg-shell-only` under T8 |
| **V5-C** | **Skill index** — pack `skill` artifacts, L2 index only, bodies via `fs.read` | §3 | Cache-miss pricing is a first-class metric |
| **V5-D** | **Plan as capability freeze** — plan mode = deny `patch.apply` until process state `plan_accepted` | process engine (exists) | **Not a DAG.** `REJ-01` holds. This is the honest reconstruction of Claude/OpenCode/Grok plan mode |
| **V5-E** | **Independence groups** — parallel **observation** calls with disjoint selectors; privileged stays singleton | `T4.7` property tests | The only honest subset of "Claude parallel tools". `D-02` reversal condition |
| **V5-F** | **Outer optimiser** — Hermes-GEPA *pipeline*, judge replaced | A/A floor + V5-A | Eval set ⊥ promote set (`CL-2`). Fitness = exterior evaluator on holdout, **never** LLM-as-judge. Output = PR against **R3 artifacts**, never R0/R1 |
| **V5-G** | **Continual harness state** — Prime's `/refine` partition: mutable supplemental files are R4, immutable system prompt is composition | V5-F | Snapshots + rollback; session-local by default; promotion follows `VG-06` scope rules |
| **V5-H** | **Protocol adapters** — MCP/ACP as `DEF-04` reversal | `006 §4.4` rules | Registry freeze, sandbox on, tools still `EffectDescriptor`s |
| **V5-I** | **Second environment** — TableWorld | — | Already Sprint 10 in `011`; remains the generality falsifier |
| **V5-J** | **Subagents** — child episodes with attenuation | recursion (S8) | `T4.10`, `DEF-03`. Kimi's correlation ids. **Do not spawn Claude as a subprocess to "get power"** |
| **V5-K** | **Message-tied worktree revert** | ledger seq | OpenCode's snapshot/revert as product undo. Maps to `GitEnvironment` + ledger seq, **not** a second store of truth |
| **V5-L** | **Prefix-miss telemetry** — every model call records *why* the prefix broke | §3 | `system` / `tools` / `compact` / `snip`. Do not assume any provider's automatic cache |
| **V5-M** | **Containment report as a publication gate** | `T5.2` | An unverified perimeter blocks publication of any result from it |

### 4.4 What V5 will still not be

A Telegram OS. An IDE. A plugin marketplace as TCB. A REPL that is the universe. A workflow graph.
A claim of AGI.

---

## 5. The 200-year framing — what a successor inherits

`VG-02 §11` and the P3 source agree on the same five-item bequest. Stated here because it is the
honest translation of *"AGI-like even if it takes 200 years"*, and because it is what makes
subtraction sprints defensible to stakeholders:

1. An **append-only ledger format** with mandatory invalidation conditions (`L-1`: the schema *is*
   the corpus).
2. A **kernel small enough to audit** (`K-02` budget, currently 1,307/1,438 LOC).
3. A **judge they still cannot reach** (`A-05`, `ADR-0004`).
4. **Split discipline** so they cannot train on the test by accident (`M-19`, `M-20`).
5. **Negative results** — `H0` falsified, degenerate A/A, reconstructions that needed core changes.

> That is more AGI-like than a 2026 TUI with 500 models. Fashion CLIs will be gone; the instrument
> might not be.

---

## 6. Sequencing against `011`

Nothing in §4 enters Phase 3. The triggers:

| Item | Trigger | Earliest |
|---|---|---|
| ACI-1…ACI-4 | none — adapter work | **Sprint 8** |
| ACI-5, ACI-6, ACI-7 | `budget_policy` read + alias repair | **Sprint 7–8** |
| V5-L prefix-miss telemetry | none — one day | **Sprint 8** (it is `006 S5`) |
| V5-A exact corpus | `RandomPort`/`ClockPort` | **Sprint 8** contracts, Phase 4 implementation |
| V5-I TableWorld | domain de-capture | **Sprint 10** |
| V5-J subagents | recursion merged | Phase 4 |
| V5-E independence groups | A/A floor exists (`C-04` is unmeasurable without one) | Phase 4 |
| V5-B, V5-C, V5-D, V5-G, V5-K, V5-M | after the MVP gate | Phase 4 |
| **V5-F outer optimiser** | **`O-01`** — one artifact clears the A/A floor | Phase 4+, and not before |

**The rule that keeps this honest:** every V5 item must earn its place against `vg-shell-only`
under `T8`, paired, on holdout. An ACI gift that does not beat shell-only is a costume. That is
what `L-15` protects and why the baseline manifest is flagged undeletable.
