> **CLOSED 2026-08-16 — archived from `docs/reviews/todo/`.**
> **PROMOTE.** Fully carried forward into `010_v5_aether_roadmap_and_aci_harvest_V043-REV.md`.
> Finding-level verdicts and evidence: `docs/reviews/doing/009_prior_review_reconciliation_V043-REV.md`.
> Surviving findings are tracked in `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md`.
> This document is historical. Do not action it directly.

---

# Vanguard v0.4.2 and Aether V5 — Investigation of Harness-D-power/src

**Status:** NON-NORMATIVE. Not in `docs/main_v4/00_vanguard_registry_v040.md` Chapter 2. Where this file and a v4 owner disagree, the owner wins (`PR-3`).

**Date:** 2026-08-16

**Audience:** Project Lead, Tech Lead, Principal Architects, researchers who will still be here when the ledger outlives the code.

**Primary corpus (read in this tree, not marketing pages):**

```text
/home/rocha/Coding/Harness-D-power/src/
  aether/                 # pre-v4 Aether: workflow DAG (the thing VG-03 rejected)
  sagiha/                 # hexagonal sibling: ports, kernel, outer_loop SFT/DPO, code graph
  claude_refs/            # guides, not Claude Code source
  open_code/              # OpenCode: client/server, PermissionV2, read/bash/edit
  grok_build/             # Rust harness: tool-protocol, hooks, sandbox types
  kimi_cli/               # Python Soul loop + agent.yaml packs; ACP/MCP; kaos host (no OS sandbox)
  goose/                  # AAIF general agent: MCP/ACP, Rust, not coding-only
  openhands/              # this snapshot is Agent Canvas (control center), not only the SDK loop
  swe-agent/              # ACI paper lineage; maintainers now point to mini-SWE-agent
  reasonix/               # Go: prefix-cache as an invariant (best empirical L1–L5)
  deepseek-harness/       # package explosion: todo/terminal/subagent/web/workflow/typert
  hermes_agent/           # personal gateway + in-loop skill writing
  hermes_self_evolution/  # DSPy+GEPA offline → PR; pytest/size gates real; fitness is LLM-as-judge unless goldens exist
  prime-agent/            # RLM / Continual Harness; explicit non-sandbox warning
  codex/                  # OpenAI coding CLI snapshot
```

**Also used:** live Vanguard (`Aether-D-System/vanguard/packages`), `docs/main_v4` VG-00…12 + GTS-13C, prior reviews in this folder.

**One-sentence ruling.** Do **not** rewrite Vanguard from scratch. Do **not** import competitor feature catalogs into Sprint 6B. Ship **v0.4.2** as a thin, high-leverage patch on the existing hexagonal kernel. Plan **V5** as the first *competence-accumulation runtime* that can run for decades — which is the only honest translation of “AGI-like even if it takes 200 years.” `VG-02` NC-01 still forbids claiming AGI. The programme claims an **instrument that cannot stop asking whether competence accumulated**.

---

## 0. How to read this

| Horizon | Name | What it is |
|---|---|---|
| Now (days–weeks) | **v0.4.2** | Patch the Beta product path + three ACI/context gifts that are *data or adapters* |
| After Beta (S7–S9) | **v4.x packs** | Manifest reconstructions, A/A, TableWorld — already planned |
| Next architecture tag | **V5 / Aether** | Outer loop, exact trajectory export, code-graph observations, skill-index-in-prefix, independence groups — **still one kernel** |
| Civilizational | **Programme** | Ledger + invalidation + exterior judge outlive every CLI fashion |

Rewrite-from-scratch is licensed only if the kernel’s dispatch algebra is proven inexpressible (`ADR-0003` reversal). Nothing in `Harness-D-power/src` provides that proof. Several trees provide the opposite: **more packages around the same loop**.

---

## 1. Lineage in this folder (do not confuse the three Aethers)

### 1.1 `src/aether` — pre-v4 prototype (do not revive)

`engine.py` still registers a **static topology**:

```text
retrieve → architect → generate → apply → evaluate → reflector → repair → join
```

`NODE_SOCKETS` and `WorkflowExecutor` are exactly the failure `VG-03 §2` documented: the agent is a leaf of a graph validator; repair is a bounded `for` over a chain; tools require booleans in three layers. It also already had Tree-sitter indexing, Git worktrees, cassette providers, and a measurement floor — **good adapters trapped in a bad control language**.

**V5 implication:** harvest adapters (indexer, cassette, git worktree), never the DAG.

### 1.2 `src/sagiha` — the closest sibling (harvest, don’t merge blindly)

Hexagonal lattice already named: `domain / ports / kernel / agency / adapters / outer_loop`.

| Piece | Path | Why it matters for V5 |
|---|---|---|
| Run loop | `agency/run_loop.py` | Stuck detection (repeat threshold 3), freeze files, compaction events |
| Tools | `adapters/tools/builtins.py` | `read_file, list_dir, grep, apply_edit, write_file, run_command` **plus** `find_symbols, get_skeleton, impacted_by` |
| Freeze | `agency/freeze.py` | Kill-9 snapshot next to the workspace, grants-absent |
| Gate evaluator | `outer_loop/evaluator/gate_evaluator.py` | Isolated from `agency/` via import-linter; suppression markers fail closed; `None ≠ pass` |
| MetaImprover | `ports/meta_improver.py` | Protocol only; **no adapter**; “never writes TCB”; human sign-off |
| SFT export | `outer_loop/export/sft.py` | Reconstructs **exact** assembled messages; documents the gap that **tools snapshot is missing** |

Sagiha’s default prompt only names `apply_edit` and `run_command` — a reminder that **prompt and registry drift**. Vanguard’s frozen manifest is the fix.

**V5 implication:** port `find_symbols` / `get_skeleton` / `impacted_by` as **observation adapters** behind existing `fs.search`/`fs.list` or new observation verbs. Port SFT export’s “exact-not-approximate” law into Vanguard `Recording` + context compiler digest. Keep MetaImprover **out of the TCB**.

### 1.3 `Aether-D-System` Vanguard v4 — current authority

Episode loop, capability kernel S0–S12, L1–L5 compiler, freeze-at-composition manifests, exterior evaluator contract. Beta product path still NO-GO. This remains the trunk.

---

## 2. Comparative anatomy (what the sixteen trees actually are)

### 2.1 The commodity loop (every coding CLI)

Claude’s public Agent SDK, OpenCode tests, Grok’s turn hooks, Kimi’s wire protocol, Codex, Goose, and SWE-agent all reduce to:

```text
prompt + tools + history → model → zero or more tool calls → execute → append → repeat
until text-only or budget
```

Claude documents this as turns that **do not yield to the host until a text-only message**. OpenCode tests fire **parallel** `read` calls in one assistant message. Vanguard’s engine is **depth-1 / one tool call per proposal**. That is a *scheduler* difference, not a *competence* difference.

**Do not fork the kernel to win a demo against Claude’s parallel Read.** Serialise observations or fold them into one `fs.search` / `fs.list` (already decided for S7). Independence groups are a **V5** ADR, not v0.4.2.

### 2.2 What is actually different (the eight surfaces)

Using the phase-2 taxonomy against this source folder:

| Surface | Best teacher in `src/` | Vanguard today | v0.4.2 | V5 |
|---|---|---|---|---|
| Agency loop | SWE-agent (simple) / OpenCode (product) | Depth-1 episode | Keep | Optional independence groups |
| Context | **Reasonix** (prefix invariant) | L1–L5 exists | Measure cache-hit | Skill **index** in L2, bodies in L5 |
| Localisation | **sagiha** code graph + SWE ACI search | `fs.search` | Paginated read (100 lines) | `find_symbols` / `get_skeleton` / `impacted_by` |
| Alteration | SWE lint-on-edit; Grok diffs | `patch.apply` | Lint observation after patch | `patch.bundle` atomic |
| Authority | OpenCode PermissionV2; Codex sandbox+approval | Kernel grants (stronger algebra, weaker product) | **Close the product path** | Session-scoped allowlists as **policy artifacts** |
| Containment | Codex OS sandbox; OpenClaw opt-in (reject); Prime **no sandbox** (reject as default) | Rootless intended | Bind **all** privileged fs | Containment report as publish gate |
| Evidence | sagiha GateEvaluator; SWE tests; Hermes GEPA **offline** | IsolatedEvaluator specified | Attest UID / fail `inconclusive` | Ablation + SFT/DPO export |
| Persistence | sagiha freeze; OpenCode sessions; Prime daemon | Ledger + cassette | Freeze file next to worktree | Continual harness **as R4 content**, not R0 |

### 2.3 Per-tree rulings (short)

**OpenCode (`open_code`).** Real split: TUI / `serve` / `run`, `PermissionV2`, tools `read`/`bash`/`edit`/`glob`/`grep`, `doom_loop` guard, `external_directory` permission. **No OS sandbox.** **Steal:** client/server split; message-tied git snapshot revert (V5-K). **Reject:** YOLO `--auto` as a security story.

**Grok Build (`grok_build`).** Runnable Rust kernel; FQ tools `GrokBuild:read_file`; Claude-name aliases; bubblewrap profiles; `before_turn`/`after_turn` hooks that **MUST NOT block**. Subagent as `session_relationship`. **Steal:** aliases + checkpoint *idea* + hook *events* as ledger kinds. **Reject:** hooks that could grant; rewriting Vanguard in Rust.

**Kimi CLI (`kimi_cli`).** Python `KimiSoul` + `agents/default/agent.yaml` pack composition; ACP; concurrent subagents. **kaos** local/SSH — **no OS sandbox**. **Steal:** explicit subagent event correlation ids; YAML Soul packs. **Defer:** subagents (`DEF-03`).

**Goose.** Operation state machine over SQLite; extensions as MCP clients; ACP server **and** ACP providers. Inspectors + SmartApprove — still not OS sandbox. **Steal later:** ACP-as-client (`DEF-04`). **Reject now:** becoming a generic assistant (C-10); replacing the episode engine with Goose’s SM.

**OpenHands snapshot.** This tree’s README is **Agent Canvas**: a control center that *hosts* Claude/Codex/ACP agents. That is a **product above harnesses**. Vanguard’s analogue is `vg harness bench` + maybe a future canvas (`DEF-01`). Do not build a multi-agent IDE in 6B.

**SWE-agent.** ACI: 100-line viewer, lint-on-edit, succinct grep (file list not dump), empty-output acknowledgement. Maintainers **recommend mini-SWE-agent** (~100 lines) matching old SWE-agent scores. **This is the strongest empirical argument for thinness.** Vanguard’s typed tools already are an ACI. Finish them.

**Reasonix.** Skills: **names+descriptions in cache-stable prefix (≤4000 chars); bodies load on demand.** Memory/control input **never mutate the prefix mid-session.** Guardian review keeps prefix warm. Plugin lazy-load comments warn that new tools **invalidate prefix cache at 10× miss pricing**. **This is the best implementation of `VG-03` T4.9 in the wild.** Vanguard L1–L5 is the same idea; Reasonix proves the *discipline* (what must not enter L1/L2).

**DeepSeek Harness.** Hundreds of packages (`todo`, `terminal`, `subagent`, `web`, `workflow`, `typert`, `ralph`, …) plus a Python JSON-RPC SDK. **Steal:** `llm-replay` / `agent-loop-testkit` (LAM’s cousin). **Reject:** this packaging style. It is how a thin kernel dies.

**Hermes Agent.** Gateway, cron, FTS5 memory, **skills that self-improve during use**. Scientifically interesting, **CL-1 / REJ-04 hostile** if skills rewrite the criteria they are judged by. Treat as a *different product*.

**Hermes Self-Evolution.** DSPy+GEPA, constraint gates (pytest, size, no mid-conversation mutation), **PR never direct commit**. The *pipeline shape* is VG-07 L4. The *fitness* in this tree is not: `dataset_builder.py` synthesises eval items from the skill under optimisation; `fitness.py` scores with **LLM-as-judge**. That is `REJ-04` / `CL-1` unless replaced by golden exterior oracles. Steal the pipeline; **replace the judge**.

**Prime Agent.** RLM: context as variables, IPython as the tool, `/refine` updates **supplemental** harness state, **never the immutable base prompt**, snapshots for rollback. Honest README: **not a security sandbox**. **Steal the partition** (immutable L1 vs mutable R4). **Reject REPL-as-universe** as default ACI (unscoped Python is `proc.exec` with extra steps).

**Codex.** OS sandbox + approval policy; plugins. Aligns with “workspace-write + ask.” Vanguard already specified a stricter algebra; **ship it**.

**claude_refs.** Secondary literature and workflows (plan-driven, TDD, agent teams). Not source. Do not treat as Anthropic internals.

**prime-agent / hermes** long-running daemons.** Useful for “detach and reattach.” Vanguard already has checkpoint/resume **as commands**. Productise resume before inventing a second process model.

---

## 3. Cognitive and meta-loop reading (principal specialist layer)

### 3.1 Complementary Learning Systems, mapped without biology-as-spec

`VG-12` is non-normative. The *useful* mapping, now evidenced by these trees:

| CLS idea | Competitor implementation | Vanguard contract | Allowed |
|---|---|---|---|
| Fast episodic | OpenCode/Kimi session JSON; sagiha trajectory SQLite | Ledger `L` | Yes |
| Slow semantic | Hermes FTS5 + Honcho; Prime `/refine` | `VG-06` claims with invalidation | Yes, **offline** |
| Interleaved replay | Hermes GEPA on traces; sagiha SFT export | Cassette + LAM + `Recording` | Yes |
| Catastrophic interference | Reasonix: don’t mutate prefix; Hermes evolution: no mid-conversation change | L1–L3 freeze per episode | Yes |
| Hippocampal indexing | sagiha FTS5 + tree-sitter graph | Index adapter (`DEF-05` until measured) | Observation only |

**Forbidden mapping:** “the event store is a hippocampus.” `REJ-10`.

### 3.2 Metacognition that is not theatre

Prime’s `/refine` and T4.11 (competence estimate recorded **before** acting) are the same family: a **prediction** with a later score. Hermes `/journey` is an audit UI over memory. Vanguard’s `vg why` (T6.5) is the governance analogue.

**v0.4.2:** record the estimate (already T4.11 in GTS). Do not consume it.

**V5:** Brier score as an **alarm**, never as a scalar fitness (`ADR-0015`).

### 3.3 Self-improvement that can run 200 years

Three loops, only one of which may touch running code:

1. **Inner (episode).** Tools, tests, abstention. No learning. Every CLI already does this.
2. **Middle (harness artifacts).** Prompts, skills, routing. Hermes-GEPA / sagiha MetaImprover / Prime `/refine`. **Candidate diffs, human or evidence-gated promotion, rollback tested first (`L-06`).**
3. **Outer (weights).** SFT/DPO from **opt-in** trajectories (`MEM-7`, `DEF-09`). sagiha already exports; Vanguard `Recording` must snapshot **tool schemas** (sagiha’s documented gap m-7 — do not copy the gap). An outer optimiser that uses LLM-authored rubrics (Hermes GEPA as shipped) is **not** this loop until the judge is exterior.

AGI-like behaviour, if it ever appears, is a **side effect of (2)+(3) under CL-1..3**, not a feature flag. A million sprints of adding MCP servers is not that programme.

### 3.4 Complex coding tasks (what actually moves the needle)

SWE-agent paper + mini-SWE-agent: **ACI quality > scaffold size.** 100-line viewer, lint-on-edit, short grep beat “more agents.”

Reasonix: **prefix stability > clever compaction.** Compaction that rewrites L1 is a cost explosion.

Sagiha: **code graph observations** (skeleton, impact) beat dumping files.

Therefore v0.4.2’s “power” is ACI + turns + tests + `AGENTS.md`, not subagents.

---

## 4. Rewrite vs evolve (decision)

| Option | Verdict | Why |
|---|---|---|
| Rewrite kernel in Rust like Grok/Goose | **No for V5** | ADR-0001 TS control plane; kernel is Python and small on purpose. A rewrite resets must-fail archaeology. |
| Revive `src/aether` workflow DAG | **Never** | `REJ-01` / `VG-03 §2`. |
| Merge sagiha into Vanguard | **No big-bang** | Sibling; harvest adapters and export law. Two TCB stories would fork the programme. |
| Become DeepSeek-harness-shaped monorepo | **No** | Package sprawl is entropy. |
| Evolve Vanguard in place | **Yes** | Kernel algebra is the scarce asset. Packs and adapters are cheap. |

**Reversal:** a reconstruction (T7.6) is inexpressible without a new dispatch axiom, written as ADR, with property tests. Then a *module* rewrite of that axiom, not a greenfield org.

---

## 5. Vanguard v0.4.2 — what to ship now

**Goal:** a developer can fix a real multi-file bug with `vg`, trust the sandbox, and the ledger can be replayed. **Framework hypothesis test:** zero edits to `kernel/` and `agency/episode/` except bugfixes required for the product path.

Versioning: treat as **0.4.2** on the v4 line (patch). Not a new VG-nn document set. If a contract field is added, it is a **minor** wire bump with reader profiles (`T1.13`), not “V5.”

### 5.1 P0 — product path (without this, 0.4.2 is a number on a lie)

1. CLI cannot succeed without a RuntimeService (kill feed-on-empty-stdin).
2. Provider `{text, toolCalls}` translates to canonical proposals (already `invocation.py`; make it the only live path).
3. All privileged filesystem effects use the same sandbox binding as `proc.exec`.
4. Evaluator: attested or `inconclusive` — never FakeEvaluator pass.
5. Approval: descriptor-bound; do not ship HMAC as if it were operator-held Ed25519.
6. `RecordCorrection` calls `parse_wire("CorrectionRecord")`.

### 5.2 P1 — ACI gifts (days, from SWE-agent + sagiha, adapters only)

| Gift | Source | Implementation | Why models get stronger |
|---|---|---|---|
| Paginated `fs.read` (default 100 lines + offset) | SWE ACI §2 | Adapter + tool schema; prompt says so | Stops dump-and-drown |
| Empty command acknowledgement | SWE ACI §4 | `proc.exec` receipt text | Models loop on silence |
| Succinct `fs.search` (file hits first, cap snippets) | SWE ACI §3 | Adapter | Matches what the paper measured |
| Syntax lint on `patch.apply` (observation, not authority) | SWE ACI §1 | Worker returns lint; failed syntax is a **receipt**, still recorded | Cheap; does not replace evaluator |
| `AGENTS.md` / `CLAUDE.md` first-read | OpenCode, Grok, Codex, Kimi | **System prompt only** | Highest ROI convention in 2026 |
| `maxTurns` 24–32 from budget_policy | Claude SDK `max_turns` | Engine already has `max_turns`; **read policy** | Real bugs need >8 turns |
| Manifest aliases `Read`/`Bash`/`Edit` | OpenCode/Claude names | Data file, not `KNOWN_TOOLS` growth | Models trained on those names |

### 5.3 P2 — Reasonix discipline without a Go rewrite

- Freeze L1/L2/L3 for the episode (already the compiler’s job).
- **Do not** inject skill bodies or memory into L1 mid-run.
- If you add a “skills index,” it is a **≤4k char L2/L3 block of names**, bodies via `fs.read` of pack files (Reasonix `IndexMaxChars = 4000`).
- Log cache-hit if the provider returns it (DeepSeek/OpenRouter). A number, not a rewrite.

### 5.4 Explicitly out of 0.4.2

MCP, ACP, subagents, plan-mode product, LSP tool, `proc.interactive`, parallel tool calls, Hermes memory, Prime IPython-as-OS, Grok marketplace, DeepSeek package copy, public SWE-bench, auto-promotion, kernel rewrite.

### 5.5 Extensibility proof (the framework’s real Beta feature)

One new pack file (`aliases.json` or `AGENTS.md` instruction) changes behaviour. `DEFAULT_BINDINGS` gains **at most** `fs.list` if dogfood demands it. CI: reconstruction-style **core-tree freeze** on 0.4.2 PRs except listed P0 files.

If 0.4.2 needs `if model == "claude"` in `EpisodeEngine`, 0.4.2 has failed.

---

## 6. V5 / Aether — after Beta (the next huge update)

V5 is **not** “Vanguard but with every CLI feature.” It is the first tag where **middle and outer loops exist as code**, still outside the TCB.

### 6.1 Invariants carried forward (non-negotiable)

S1 (capability+resource), evaluator exterior, freeze-at-composition, `sinkClass` mediation, `inconclusive` excluded from rates, coding not ontology, no scalar fitness, no self-authored eval criteria.

### 6.2 New capabilities (ordered by dependency)

**V5-A — Exact corpus (sagiha m-7 fix).** Every `Recording` includes `toolSchemaDigest` + `contextCompilerDigest` + `manifestDigest`. SFT/DPO export reconstructs bytes the model saw. Without this, 200 years of traces are sludge.

**V5-B — Observation graph (sagiha tools).** `find_symbols`, `get_skeleton`, `impacted_by` as observation verbs or `fs.search` modes. Earn vs `vg-shell-only` under T8. Tree-sitter stays in the **worker**.

**V5-C — Skill index (Reasonix).** Pack `skill` artifacts: L2 index only; `run_skill` is `fs.read` + optional child episode later. Cache-miss pricing is a first-class metric.

**V5-D — Plan as capability freeze.** OpenCode/Claude/Grok plan mode = **deny `patch.apply` until a process-engine state `plan_accepted`**. Not a DAG. `REJ-01` holds.

**V5-E — Independence groups (optional).** Parallel **observation** calls with disjoint selectors. Privileged remains singleton. This is the only honest “Claude parallel tools” subset.

**V5-F — Outer optimiser (Hermes GEPA *pipeline*, not its judge).** Offline. Eval set disjoint from promote set (`CL-2`). Constraint gates (tests, size, cache compatibility). Fitness = exterior evaluator / holdout tasks, **never** LLM-as-judge of self-authored synthetic items. Output = PR/diff against **R3 artifacts**. Never R0/R1. Maps to sagiha `MetaImprover`.

**V5-G — Continual harness state (Prime `/refine` partition).** Mutable supplemental files are **R4**, immutable system prompt is **composition**. Snapshots + rollback. Session-local by default; promotion to repo/domain follows `VG-06` scope rules.

**V5-H — Protocol adapters.** MCP/ACP as `DEF-04` reversal: registry freeze, sandbox **on**, tools still `EffectDescriptor`s. Goose/Kimi/OpenHands Canvas are clients or hosts, not kernels.

**V5-I — Second environment.** TableWorld (T9) remains the generality falsifier. Hermes-as-gateway is **not** that environment unless we explicitly start a non-coding programme.

**V5-J — Subagents.** Child episodes with attenuation (`T4.10`, `DEF-03`). Kimi’s correlation ids. Budget lease trees already specified. Do not spawn Claude as a subprocess to “get power.”

**V5-K — Message-tied worktree revert (OpenCode snapshot).** Product undo: FS snapshots keyed to conversation parts. Not 0.4.2. Maps to GitEnvironment + ledger seq, not a second store of truth.

**V5-L — Prefix miss telemetry (Reasonix `CompareShape`).** Every model call records why the prefix broke (`system` / `tools` / `compact` / `snip`). This is how L1–L5 stays honest across providers; do not assume DeepSeek automatic cache.

**V5-M — OS sandbox is already a kernel concern.** Codex Seatbelt/bwrap and Grok `xai-grok-sandbox` confirm: policy-only permissions (OpenCode, Kimi, Goose) are **not** S1. Vanguard’s rootless runner is the right class. 0.4.2 binds it; V5 publishes containment reports. Do **not** rewrite the kernel in Rust to “be Codex.”

### 6.3 What V5 will still not be

A Telegram OS. An IDE. A plugin marketplace as TCB. A REPL that is the universe. A workflow graph. A claim of AGI.

### 6.4 The 200-year programme (honest)

If a grandson finishes this, they should inherit:

1. An **append-only ledger format** with invalidation conditions (`L-1` in `VG-02`: schema is the corpus).
2. A **kernel small enough to audit**.
3. A **judge they still cannot reach**.
4. A **split discipline** so they cannot “train on the test” by accident.
5. Negative results (H0 falsified, degenerate A/A, reconstructions that needed core changes).

That is more AGI-like than a 2026 TUI with 500 models. Fashion CLIs will be gone; the instrument might not be.

---

## 7. Mapping onto existing sprint plan (do not silently explode 6B)

| Item | Stays | Moves |
|---|---|---|
| 6B / v0.4.2 | Product path + ACI gifts + AGENTS.md + aliases + maxTurns | — |
| S7 T7.5–T7.7 | Reconstructions as packs | Kilo = OpenCode-shaped alias, not a fourth core pack |
| S7–S8 T8 | A/A, pairing | LAM replay labelled, never Q3 |
| S8 T9 | TableWorld | — |
| S9 gate | Q1–Q4 | Admit Q3/Q4 may slip; don’t fake them in 6B |
| V5-A…M | After first honest Beta tag | GEPA/MetaImprover (exterior judge), code graph, plan freeze, MCP, revert, prefix telemetry |

**Doc change opportunities (leads file ADRs, don’t edit this review as if it were `VG-09`):**

- Pull `AGENTS.md` convention into 6B close guidelines.
- Add “ACI: paginated read / succinct search / lint receipt” as **adapter tickets**, not kernel.
- Record Reasonix prefix law as an engineering **check** on the context compiler (no new normative VG file unless T4.9 is restated).
- Note sagiha as **internal prior art** for V5 observation tools and exact export.
- Keep `VG-02` NC-01; add a programme sentence in `VG-12` only if you want the 200-year framing in the annex (non-normative).

---

## 8. Independent packets (v0.4.2)

| ID | Owner lens | Files | Done when |
|---|---|---|---|
| 042-0 | Lane A | CLI live client, RuntimeService | Empty stdin ≠ success; daemon required |
| 042-1 | Lane B | sandbox + git/fs bindings | Reads and patches contained; test proves host escape fails |
| 042-2 | Lane B | `invocation.py` + `aliases.json` | `Read` works without Python dict edit |
| 042-3 | Pack | `system-prompt.txt`, `budget-policy.json` | AGENTS.md instruction; maxTurns ≥ 24 |
| 042-4 | Adapter | `fs.read` pagination, search cap, empty exec text, optional lint receipt | Unit tests; SWE-style fixtures |
| 042-5 | Service | CorrectionRecord parse | Wire reject on style+general |
| 042-6 | Dogfood | three real bugs | Q2 evidence, labelled live vs cassette |

No packet includes MCP.

---

## 9. Risks if we ignore this investigation

1. **Competitor envy** → DeepSeek-harness package death.
2. **Revive `src/aether` DAG** because it “looks complete.”
3. **Copy Hermes in-loop skill writing** or **GEPA-with-LLM-judge** and quietly violate CL-1 / REJ-04.
4. **Copy Prime REPL** and throw away the sandbox thesis.
5. **Treat Agent Canvas as the product** and never close `vg`’s one path.
6. **Train SFT without tool-schema snapshots** (sagiha m-7) and poison the 200-year corpus.
7. **Claim v0.4.2 “SOTA” from LAM replay.**

---

## 10. Closing

The `Harness-D-power/src` folder is a museum of **the same loop** with different skins, plus three relatives that matter:

- **pre-v4 aether** — how we already failed at control flow;
- **sagiha** — how our own hexagonal family sketched V5 observation and export;
- **Reasonix + SWE ACI + (GEPA pipeline without its judge)** — prefix freeze, thin ACI, offline evolution under an exterior oracle.

Vanguard v4 is the right trunk. **v0.4.2** makes it usable. **V5** makes it accumulative. **AGI**, if the word ever applies, will be a measurement on that accumulation — not a milestone named after a CLI.

---

## Appendix A — Files an implementer should open first

```text
Harness-D-power/src/sagiha/adapters/tools/builtins.py
Harness-D-power/src/sagiha/outer_loop/export/sft.py
Harness-D-power/src/sagiha/outer_loop/evaluator/gate_evaluator.py
Harness-D-power/src/sagiha/ports/meta_improver.py
Harness-D-power/src/reasonix/internal/skill/index.go
Harness-D-power/src/reasonix/internal/memory/doc.go
Harness-D-power/src/swe-agent/docs/background/aci.md
Harness-D-power/src/hermes_self_evolution/README.md
Harness-D-power/src/prime-agent/README.md          # partition + sandbox warning
Harness-D-power/src/aether/engine.py               # what not to rebuild
Harness-D-power/src/open_code/packages/schema/src/permission.ts
Harness-D-power/src/grok_build/crates/common/xai-tool-protocol/src/turn_hook.rs
Aether-D-System/vanguard/packages/runtime/root.py
Aether-D-System/vanguard/packages/adapters/models/invocation.py
Aether-D-System/docs/main_v4/03_*.md
Aether-D-System/docs/main_v4/07_*.md
```

## Appendix B — Survey completeness

All 16 top-level directories were opened in the first pass. A second pass walked loops, tool registries, sandbox, compaction, and judge isolation in each tree. Appendix C records corrections and kernel-vs-pack rulings from that pass.

## Appendix C — Deep tree-walk addendum (2026-08-16)

Empirical corrections after line-level walks. v0.4.2 rulings in §5 do **not** change. V5 gains three IDs (K–M) and a stricter GEPA rule.

### C.1 Kernel vs pack (do not mis-classify)

| Must live in **kernel / ports / sandbox adapter** | Stays a **harness pack / content** |
|---|---|
| OS isolation (Codex Seatbelt/bwrap; Grok bubblewrap profiles; Vanguard rootless) | Tool names, Claude aliases (`Read`→`fs.read`), Grok `MANAGED_TOOLS`, OpenCode registry |
| Grant + descriptor-bound approval (already Vanguard; OpenCode/Kimi/Goose *ask* is UX only) | Skills, SKILL.md, agent.yaml, `.grok/agents/` |
| Episode ledger + receipts (DSH frozen events; not Canvas UI stores; not SWE traj-only) | MCP server catalogs, plugin lists |
| L1–L5 freeze + miss attribution (Reasonix `CompareShape`; reject SWE `LastNObservations`) | Plan prompts; `update_plan` / `EnterPlanMode` as **capability freeze** |
| Nested session / attenuation (when DEF-03 lifts) | Subagent *prompts* and YAML specs (Kimi `coder`/`explore`/`plan`) |
| ACP/MCP as protocol **adapters** with freeze-at-composition | ACP as the product identity (Goose) |

OpenCode **snapshot/revert** and Codex **remote compaction** are kernel-*adjacent* product features (V5-K; provider port for compaction). They are not 0.4.2.

### C.2 Per-tree facts that were underspecified

**claude_refs.** Zero runtime. Analysis lists ~41 tool names (FileRead through LSP, cron, teams). Use as a **capability checklist** for packs, never as a port source. QueryEngine/compaction exist only as documentation.

**grok_build.** Runnable Rust kernel. FQ tools `GrokBuild:read_file` etc.; Claude-name alias crate; `handle_prompt` ACP turn; git/hunk checkpoints; hooks that **must not block**. Strongest in-folder **sandbox crate**. Steal aliases + checkpoint *idea*; do not replace Vanguard’s Python kernel.

**kimi_cli.** Python `KimiSoul` step loop + declarative `agents/default/agent.yaml`. Approval/yolo/afk; **kaos** local/SSH — **no OS sandbox**. Best **pack composition** reference (Soul swap + YAML). Weaker isolation than Grok/Codex/Vanguard-as-specified.

**open_code.** Effect `prompt.loop`; tools `bash|read|glob|grep|edit|write|task|skill|…`; `doom_loop` threshold 3; plan agent denies edits; **git snapshots + message revert**. Permissions are soft. Steal revert for V5-K; steal permission matrices as **manifest risk tables**.

**goose.** Rust **operation state machine** over SQLite sessions; extensions are MCP clients; ACP server **and** ACP providers (`codex-acp`, `claude-acp`). Inspectors + SmartApprove — still not OS sandbox. Steal ACP-as-client later (`DEF-04`); do not make Goose’s SM the episode engine (`REJ-01` still holds: ops pipeline ≠ workflow DAG, but also ≠ our loop).

**codex (`codex-rs`).** Turn in `session/turn.rs`; real OS sandbox; `apply_patch`; multi-agent tool family; **remote compaction V1/V2** vs local summary. This is the field’s best **policy+containment** product. Vanguard already specified the stricter algebra; **bind the runner** (0.4.2) rather than clone the crate.

**openhands (this snapshot).** Agent Canvas only. Confirms UI ≠ kernel. Multi-backend client of a RuntimeService is the right shape for a future `vg` host.

**swe-agent.** `LastNObservations` **explicitly breaks prompt caching**. Exterior `sb-cli` hook is the judge pattern to keep. Do not import history elision into the context compiler.

**reasonix.** `internal/agent/cache_shape.go` `CompareShape`; snip→prune→summary **before** compact; optional planner/executor **separate sessions** for cache isolation. Guardian is a **policy LLM**, not an exterior competence judge. V5-L.

**deepseek-harness.** `agent-loop` is the only concrete loop; session events frozen; messages derived; `tools/pre-execute` ≈ grant seam; bundles ≈ manifests. Steal the **seams**; reject the monorepo. In-loop guards are not evaluators.

**hermes_agent.** Gateway + `skill_manager` self-write + verify-on-stop **nudges**. Medium–high CL-1 risk.

**hermes_self_evolution.** `evolution/core/fitness.py` LLM-as-judge; `dataset_builder.py` synthetic items from the artifact. **Critical** unless goldens replace both. Pipeline (offline, PR, pytest) remains the template.

**prime-agent.** `/refine` LLM-over-trajectory into harness state; quality gates optional/empty. Honest about limits ≠ success. Partition yes; judge isolation no.

**sagiha / Harness `aether`.** Remain the only trees in the folder with TCB-resident exterior tests. Harness `aether` is a **measurement coding harness** (workflow DAG + floors), not Vanguard’s six-plane kernel. Do not merge; harvest.

### C.3 v0.4.2 unchanged; V5 delta only

0.4.2 still: product path, ACI, AGENTS.md, aliases, maxTurns, bind sandbox.  
V5 adds K (revert), L (prefix telemetry), M (containment as publish gate), and GEPA **without** LLM-as-judge.

### C.4 Must-read files added by the second pass

```text
grok_build/crates/codegen/xai-grok-tools/src/versions.rs
grok_build/crates/codegen/xai-grok-shell/src/session/acp_session_impl/turn.rs
kimi_cli/src/kimi_cli/soul/kimisoul.py
kimi_cli/agents/default/agent.yaml
open_code/packages/opencode/src/session/prompt.ts
open_code/packages/opencode/src/permission/index.ts
open_code/packages/opencode/src/session/revert.ts
goose/crates/goose-agent/src/machine.rs
codex/codex-rs/core/src/session/turn.rs
codex/codex-rs/core/src/tasks/compact.rs
reasonix/internal/agent/run_loop.go
reasonix/internal/agent/cache_shape.go
swe-agent/sweagent/agent/history_processors.py
hermes_self_evolution/evolution/core/fitness.py
hermes_self_evolution/evolution/core/dataset_builder.py
```

