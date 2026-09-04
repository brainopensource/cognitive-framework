---
id: report.electroweak-v092.grok.evolution
canonical_id: report.electroweak-v092.grok.evolution
class: report
authority: non-canonical
truth_plane: PROPOSED
status: snapshot
implementation_status: NOT_AUTHORIZING
owner: grok-principal-architect-review
purpose: Inner / outer / substrate evolution architecture. FACT vs [PROPOSAL]. What each idea fixes in R. What it must not do.
audience: [architect, release-owner]
last_verified: "2026-09-04"
pin_head: "5243866bc169c7f60cc7d4f74b9a853f60356381"
relationships:
  - report.electroweak-v092.grok.index
  - report.electroweak-v092.grok.live-agent
  - execution.tasks
---

# 03 — Evolution architecture

Keep **one** `EpisodeEngine`. Inner loop = offered tools + admission facts,
not a second runtime. Tag: **inner** | **outer** | **substrate**.

For each idea: what it fixes in \(R\); what must already be true; what it
must not do (admit `completed`, enlarge budget, second engine, kernel AST,
ranking-as-IndexPort).

---

## A. Inner loops to add or replace

### A.1 Settlement loop — **the** inner change

**Layer:** inner + session wiring. **Must already be true:** T-04 as an
explicit governance decision (RF-25 successor baseline recorded **before**
shrinking `ADMISSION_GATE_EXEMPT`); T-08 parser (landed).

**What.** `finish` admissible iff: patch postimage bound; `WorkspaceEpoch`
fresh; `VerificationReceipt` on a **typed subject** (argv digest + workspace
+ task); `executed_test_count > 0` from a real runner; tamper freeze intact;
implicated files inspected.

**Fixes \(R\):** this is the factor currently allowed to be 0. Outer loops
cannot raise a product of zeros.

**How.** Session already has `completion_admitter`. Wire
`TestTamperShield.evaluate` into `_admit_completion`. Pass
`implicated_files` / `callers_by_symbol` from IndexPort **observations**
(reverse `dependencies()`, not a new ranking API). Supply real
`oracle_failed_on_stub` for greenfield. Delete or honor
`ADMISSION_GATED_HARNESSES` (defined, unused).

**FACT vs `[PROPOSAL]`:** gate + parser = FACT. Tamper-on-admit + implicated
facts-on-admit = **`[PROPOSAL]` wiring** of MECHANISM modules. T-04 shrinking
exemption = **`[PROPOSAL]` / governance**.

**Must not:** admit `completed` on boolean `verification_passed`; invent test
counts; put AST in kernel; enlarge budget on reject; silent exemption shrink.

### A.2 Localize → edit → `verify_targeted`

**Layer:** inner. **Must already be true:** IndexPort `tests()` /
`dependencies()` populated; T-07 so the command is the subject; tamper so
the agent cannot rewrite those tests.

**What.** After `patch.apply`, the next offered verify is IndexPort.tests()
for changed + reverse-dep callers, not `pytest` of the universe and not
`python3 -c`.

**Fixes \(R\):** the observation after edit is **about the change**.

**Why not full-suite every turn:** hours-long brownfield dies on cost; the
model then skips tests. **Why not “model picks tests”:** it picks the green
ones.

**Must not:** rank inside IndexPort (T-46).

### A.3 Greenfield oracle loop

**Layer:** inner. **Must already be true:** T-19 module; admitter actually
running (not `vg-code-default` exempt).

**What.** Record empty-tree baseline → write contract/smoke that **fails on
stub** → implement → same oracle passes → admit. File DAG in σ (`TaskStep`
already exists). One file per turn still OK; **order** comes from the DAG.

**Fixes \(R\):** kills vacuous green on `pass` / `NotImplemented`.

**Kill:** prompt rule “do not read first” as a universal. It is a TASK.md
toy heuristic. Multi-day greenfield needs ports/types → file DAG → scaffold
→ oracle-red → topological 2PC → smoke+entrypoint.

**FACT:** policy names `VACUOUS_ORACLE`. Session evidence currently aliases
both structural and behavioral to `verification.passed` and never sets
`oracle_failed_on_stub`.

### A.4 Recover-on-`PATCH_PREIMAGE_MISMATCH`

**Layer:** inner (dialect family T-21, extend to patch). **Must already be
true:** `SectionAddress` (exists); strict preimage (exists).

**What.** Conflict → engine offers **only** `fs.read` of that path →
recompile hunk → retry. Ladder `[PROPOSAL]` T-47: exact → whitespace →
indent → fuzzy → whole-file for small files.

**Fixes \(R\):** turns “retry same hunk until budget dies” into honest
progress or honest fail.

**Why not fuzzy-first:** silent mis-apply is a lying state.

**Must not:** kernel AST; auto-relocating stale hunks (current git adapter
correctly refuses numbered-anchor drift).

### A.5 Read-before-edit

**Layer:** inner / effect boundary. **Must already be true:** inspected-set
tracking (finish already checks `MODIFIED_FILE_NOT_INSPECTED`).

**What.** Refuse `patch.apply` if path ∉ inspected set this epoch. Move the
check from **finish** to the **effect boundary** so the tree stays clean.

**Fixes \(R\):** a 40-file session of uninspected writes is unrecoverable
state even if finish later refuses.

### A.6 Do not add as inner loops

| Idea | Why not |
|---|---|
| Second EpisodeEngine / ChimeraEngine as product | Forbidden; T-23; T-55 implementer stays EpisodeEngine+pack |
| Phase ladder as default | Blocks pre-verify; product arms don’t use it; inspect-forbids-exec breaks reproduce-first |
| Parallel tool batches | Kernel one-effect; would be a **substrate** change; don’t smuggle as a prompt pack |
| Mutation score as finish law | T-39 `[PROPOSAL]`, not default |
| CodeAct bash-as-universe | Wrong ACI for a capability kernel |
| LLM-summary compaction of L4 | Destroys pinned falsified hypotheses |

---

## B. Outer loops

**Must already be true before any outer loop ships:** inner settlement cannot
lie (MS-TRUTH remaining + tamper wired + verification subject). Living board:
T-28–T-31, T-54–T-55 `[PROPOSAL]`. `runtime/outer_loop/` **absent**.

### B.1 Campaign DAG + director — **the** outer change

**Layer:** outer. **What.** `runtime/campaign/` is a **client of
EpisodeEngine**, not an engine. Director tools: read ledger, spawn read-only
children, record DAG node status. **Zero mutating tools.** Merge predicate:
implicated-test verdict / pack admission on the child episode, **never LLM
vote** (T-30). Crash after node 3 → resume nodes 4–8, no duplicate writes
(T-31).

**Fixes \(R\):** replaces “100 turns in one window” and “40-file brownfield”
with **many honest episodes**. Goal cannot amnesia across a campaign the way
it amnesias inside one 400-turn transcript.

**Why not now:** without honest child `completed`, the DAG is a fan-out of
lies.

**Why not HYDRA-as-default:** T-55; treatise non-canonical; second-brain risk.

**Internet steal:** Claude Code worktrees + subagent separate context so
investigation tokens never enter the writer window. Merge is still git+tests.

**Must not:** mutating tools on the director; LLM quorum merge; inherit meta
into children; second engine.

### B.2 Read-only investigator (T-29)

**Layer:** outer. **What.** Spawn with plan-mode attenuation: withhold
`patch.apply` and `proc.exec` (`wiring.py` `_PLAN_MODE_WITHHELD_VERBS`
already exists). Returns a **localization packet** (paths, symbols,
hypothesized tests) as values. Parent writes.

**When:** after T-27 control exists, as an **ablation** (McNemar including
missingness). If it doesn’t lift, kill it.

**Must not:** a reviewer that can `finish`.

### B.3 Worktree fork

**Layer:** outer / substrate-adjacent. **What.** Isolated git worktree per
writer episode; parent workspace stays clean; merge by tests.

**Why not in-process CoW first:** single-writer invariant. Two writers on one
tree ⇒ duplicate effects and torn 2PC.

**Must already be true:** 2PC; resume identity; no duplicate settled effects.

### B.4 Operator interrupt (T-59)

**Layer:** outer / UX. Cancel, pause, fork, resume from ledger. Not a new
cognition. Stop is operator/kernel `CANCELLED`, not “ask the model”.

### B.5 Meta framework (T-28)

**When:** paired study vs frozen T-27 control. Inconclusive ≠ negative.

**May:** suggest re-localize, escalate model, spawn investigator, compact,
switch reproduce vs write.

**Must not:** admit `completed`; grow budget; be inherited; grade work; become
OCT-04 Meta-Conductor as a second loop.

### B.6 Specialists / different agents

Product path stays three **budgets/routes**, not three ontologies.
`[PROPOSAL]`: differentiate `vg-code-fast/balanced/max` by budget, model
route, `max_turns`, retrieval budget — or stop pretending they are three
agents.

Kill: `vg-hexagonal`, `vg-archeologist-swarm`, Chimera 2.0 as product scores.

### B.7 HYDRA / swarms / compounding

**When not:** before MS-CONTROL. **When:** optional topology after
director+CAS, implementer still EpisodeEngine+pack, off by default.
Stacking spawn + campaign + memory grants + skills is the Aether bet.
Stacking before settlement honesty is a false-completion factory.

---

## C. Framework / substrate improvements

TCB ≤ 1438. I-7. Prefer **wiring existing MECHANISM** over new modules. Do
not create `episode/compactor.py`.

| Change | Layer | FACT / `[PROPOSAL]` | Must not |
|---|---|---|---|
| T-04/T-05 one gating source | session | `[PROPOSAL]` until RF-25 successor | Silent exemption shrink |
| T-07 typed verify subject | session + receipt | `[PROPOSAL]` | `echo`/`true`/`python3 -c` as verify |
| Wire tamper on admit | session | MECHANISM unwired FACT | Glob `test/**` as enum |
| Supply implicated/greenfield facts | session | policy FACT; wiring hole FACT | Ranking in IndexPort |
| 2PC for the write actually used | adapter | 2PC FACT for N>1; N=1 sequential FACT | Kernel AST |
| T-47 apply ladder + read-before-edit | adapter + session | `[PROPOSAL]` | Silent hunk relocate |
| T-48 fingerprint circuit breaker | session | `[PROPOSAL]` | Auto-finish on cycle |
| T-49 speculative checkpoint | adapter/git | `[PROPOSAL]` | Second store |
| Prefix-stable L1–L3 + **measure** cache hits | compiler + model adapter | compiler FACT; telemetry missing | Timestamps in L1 |
| Honest event producers for σ | runtime ledger | fold FACT; emission density unknown | Fake HypothesisOpened |
| Dialect already typed | adapters/models | T-21 `[x]` | False `ok` on truncated JSON |
| Memory grants on product path | T-32 | SPI FACT; product gated | Retrieve without grant |
| Plan mode | wiring | FACT withhold verbs | Fake plan mode that still grants patch |
| TCB freeze T-35 | kernel | every impl | Domain-aware kernel |

**Observability.** Honest `EffectCompleted` / `VerificationRecorded` /
omission ledger in the events the fold already understands. Trajectory
distill + predicted-vs-outcome. Do not auto-evolve the harness until events
are honest. Official SWE/DeepSWE is G-3, not DoD.

---

## D. New capabilities that raise \(R\) (and kills)

Load-bearing for hard SWE:

1. **Implicated-test runner** (inner/substrate) — IndexPort associations →
   argv subject → receipt. Fixes brownfield false green.
2. **Scaffold + oracle protocol actually bound on admit** (inner) — greenfield
   vacuity.
3. **Blast-radius callers as observations** (inner) — reverse deps into
   completeness. Not GraphOS-the-product.
4. **Checkpoint / resume UX** (outer/client) — T-59; σ already durable.
5. **Worktree isolation** (outer) — one writer per tree.
6. **Cost/cache telemetry** (substrate) — `cache_read_tokens` on the ledger.
7. **Sectioned file viewer** (inner) — `SectionAddress` already exists.
8. **Scripts in skills, not prose** (inner) — pytest argv truth; kernel deny
   for never-do-this.

**Kill (do not raise \(R\)):**

- Soul / heart / persona always-on in L1
- Decorative skill catalogs
- Architect/editor two-model split as a second engine (routing `[PROPOSAL]`,
  not Chimera)
- MemGPT archival as product memory before grants
- Embedding RAG as a substitute for IndexPort
- Mini-SWE-agent “bash only”
- Official leaderboard chasing as the inner-loop spec
- Mutation testing as a gate
- Plugin sprawl that adds verbs without admission facts
- SBFL / MCTS / SWE-RL / eBPF / Z3 as near-term product (POST-v1 or
  measurement-lane treatments)
- Eleven ORCH packs before one tamper-on-admit call

---

## E. Survival recipes (target, not yet true)

These are the behaviors the architecture must survive. They are **not**
true of the default pack today.

### Greenfield (multi-file, multi-day)

```text
requirements → ports/types → file DAG in σ → scaffold
  → oracle FAILS on stubs → topological 2PC (one node per episode or per turn)
  → smoke + entrypoint → admit only if stub-fail then impl-pass
```

### Brownfield (40-file blast radius)

```text
reproduce (fail-to-pass) → callers via IndexPort observations
  → surgical 2PC on implicated set → fail-to-pass + pass-to-pass
  → postimage digest → tamper freeze on verification subject
  → no test mutation → admit
```

### Long context (100+ turns)

```text
prefix-stable L1–L3 (byte-identical) → σ in L4 → rolling L5
  → omissions explicit → epoch after every write → goal echo at L5 tail
  → distill tool bodies; recover via fs.read → never splice RAG into L1
```

### Long runs (hours, crash, resume)

```text
resume episode_id + σ + prefix (MS-RESUME CLOSED)
  → checkpoints (T-49 after 2PC-is-default-write)
  → campaign = many admitted episodes, not one 400-turn transcript
  → operator interrupt from ledger (T-59)
```

Until settlement cannot lie, these recipes are fan-fiction.
