---
id: report.electroweak-v092.grok.theories
canonical_id: report.electroweak-v092.grok.theories
class: report
authority: non-canonical
truth_plane: BOTH
status: snapshot
implementation_status: NOT_AUTHORIZING
owner: grok-principal-architect-review
purpose: >
  Consolidate control laws from this tree's research, sibling octopus notes,
  and 2025–2026 SOTA harness practice. Separate FACT at pin from [PROPOSAL]
  from research fiction. Why-not / how / what / when for every major lever.
audience: [architect, release-owner]
last_verified: "2026-09-04"
pin_head: "5243866bc169c7f60cc7d4f74b9a853f60356381"
relationships:
  - report.electroweak-v092.grok.index
  - research.coding-harness-dekas-claude-prototype
  - research.coding-harness-meta-cognitive-engineering
---

# 02 — Theories and control laws

This file is the theory ledger. Implementation proposals live in
[`03-evolution-architecture.md`](03-evolution-architecture.md). The program
lives in [`04-sota-program.md`](04-sota-program.md).

## 0. How to use a theory in this repo

Indexes route; canonical documents constrain; source implements; tests
falsify; ledger and benchmark artifacts demonstrate. A beautiful treatise
that cites files that do not exist is **intent**, not architecture.

Tag every inherited idea:

| Tag | Meaning |
|---|---|
| **LAW** | Control law we should keep even if every vendor disappears |
| **FACT** | True of this tree at pin |
| **`[PROPOSAL]`** | Board or this review; not authorized by being written |
| **FICTION** | Research badge or lock-file claim that does not match HEAD |
| **POST-v1** | Legitimate after settlement + control, not a 2026 product loop |

---

## 1. The substrate thesis (keep)

**LAW (DEKAS, agrees with HEAD):** an agentic system is a non-deterministic
transition system driven by an **untrusted oracle**. The oracle proposes
intents. The kernel converts authorized intents into effects. Effects produce
events. Events fold into state. State projects into context, which re-primes
the oracle. That is the whole loop.

Consequences DEKAS states that this tree already believes:

- Prompt injection is unfixable when tool output and user instruction share a
  trust level; containable when provenance is a lattice and authority cannot
  be widened by tainted data. FACT: kernel provenance / I-7 domain-blindness.
- Rollback is hard when state is mutated in place; tractable when state is a
  fold over an append-only log. FACT: ledger + `fold_task_state`.
- Multi-agent coordination is a distributed-systems research problem when
  agents share mutable state; it is a merge over commutative reducers when
  they do not. **WHY NOT Chimera blackboard as product.**
- Self-improvement requires a data pipeline nobody builds — unless the
  execution log *is already* the training corpus. **WHEN:** after events are
  honest. Auto-evolving a harness on dishonest `completed` overfits DeepSWE
  and lies to yourself.

**LAW (Aether technical report Part I, agrees with HEAD):** capability and
authority must not be conflated. Restricting what the model may *say* is a
lever that does not hold. The model is structurally untrusted. Every effect
passes through `Kernel.dispatch` and there is no second path.

**WHY NOT** a second `EpisodeEngine`, ChimeraEngine-as-product, or “the
director dispatches shell”. Those recreate a second path.

**Force ranking (DEKAS §1.2, adopt as review policy):**

1. Fail-closed security
2. Causal integrity (ledger never rewritten)
3. Generality of the kernel (domain in packs)
4. Progressive cost (simple agent must not pay for unused machinery)
5. Verified outcomes over fast outcomes
6. Latency, only within 1–5

Force 4 is why HYDRA, MCTS, SBFL, SMT, and soul files must not sit in the
default coding arm.

---

## 2. Inner loop vs outer loop vs substrate

```text
INNER   = one EpisodeEngine turn: compile → propose → dispatch → ingest →
          compact → admit. Tools + admission facts. Not a second runtime.

OUTER   = many admitted episodes: campaign DAG, director, worktrees,
          investigator, operator interrupt. Client of EpisodeEngine.

SUBSTRATE = compiler/packet, 2PC, verify subject, resume, epoch, dialect,
            budgets, observability, IndexPort, MemoryPort. TCB ≤ 1438; I-7.
```

**LAW:** outer loops multiply whatever inner settlement is. If
\(\Pr(\text{honest completed})\) is near 0, a campaign of 8 children is
\(0^8\), not a 8× speedup.

**Octopus director** (`../octopus/consolidation/outer-loop-orchestrator.md`)
is right that the kernel does not change and that a director is a consumer of
the ledger and a producer of new `HarnessSession` instances. It is **wrong as
product timing** if it ships before MS-TRUTH leftovers. Its Strategy C
(evolutionary policy) is Chimera-adjacent; keep it off the product path.
Strategy A (sequential topological queue) is the correct **control** for
MS-CONTROL. Strategy B (director + CAS, zero mutating tools) is the outer
change this review endorses **after** inner honesty.

---

## 3. Compress vs compact vs cache vs index vs search vs memory

Conflating these is why “context management” proposals sprawl. They have
different owners and different “when not”.

| Mechanism | Job | This tree (FACT) | When not |
|---|---|---|---|
| **Cache** | Byte-identical prefix → cheap prefill | L1–L3 freeze | Turn index / timestamps / RAG splice in L1 |
| **Compact** | Evict L5 under ceiling, keep receipts | recency + stubs | Compact the brief; LLM-summarize away falsified hypotheses |
| **Compress / distill** | Cap tool body, bind digest | T-36 distiller | Pretend digest = model memory; agent must `fs.read` to recover |
| **Index** | Deterministic structure | IndexPort observation-only | Rank inside the port (T-46); invent symbols (T-45) |
| **Search** | Lexical `fs.search` | tool FACT | Replace callers graph |
| **STM** | σ + L4 pinned | schema FACT; emission density unknown | Dump σ into L3 (T-12 done; handbook stale) |
| **LTM** | grants + experience | SPI FACT; product `[PROPOSAL]` T-32 | Retrieve without grant; generator = evaluator = promoter |

**LAW (prefix cache):** variable content spliced into the frozen prefix
destroys KV reuse. Internet: prefix-cache failure in agent loops is a known
cost cliff. Provider-side online KV compaction papers are **not** yours to
implement in-kernel. Your job is prefix stability + measuring
`cache_read_tokens` on the ledger (engine already has diagnostic fields).

**LAW (octopus long-horizon engine, keep the split):** P1 turn-level bloat →
distill at effect boundary (mostly done). P2 attention dilution → pack
ranker, not IndexPort. P3 cache destruction → layer discipline (mostly done).
P4 cross-episode amnesia → durable memory **after** grants. P5 repo scale →
IndexPort + sectioned viewer, not full-file dump.

**SWE-agent ACI LAW:** a 100-line file viewer beats dumping 10k-line files
into L5. This tree already has `SectionAddress`. Use it.

---

## 4. Editing: diff, whole-file, AST, LSP

**FACT:** product apply is unified diff with strict preimage, plus whole-file
`content`, plus adapter AST **preflight** for 2PC. Pack `AstPatchToolkit` is
not the kernel path.

**LAW:** silent mis-apply is a lying state. Strict fail is correct; **blind
retry of the same hunk** is the \(R\) killer.

**Steal, do not cosplay:**

- Aider: whole-file fallback on **small** files after exact fail.
- Claude/Cursor: search-replace fails on whitespace — so offer re-read, then
  a typed ladder (T-47): exact → whitespace → indent → fuzzy → whole-file.
- Geometric AST-edit numbers: interesting **in adapters**, never in kernel.

**WHY NOT kernel `ast.parse`:** I-7. Domain-blind TCB. AST is a coding-pack
concern.

**WHY NOT LSP as a kernel citizen:** LSP is a future IndexPort **producer**
(callers, defs, refs). The port stays dumb.

**WHY NOT full-file overwrite as default:** `future_improvements` C-16
correctly calls this regressive. Keep whole-file as a **small-file recovery
rung**, not the primary verb.

---

## 5. Verification, oracles, tamper

**LAW:** the model is not the judge of `completed`. An exterior receipt with
a **typed subject** (argv digest + workspace + task) is.

**FACT holes:** unknown-runner count 0; T-07 open; tamper unwired; implicated
tests not bound; greenfield stub-fail not recorded.

**LAW (vacuous oracle):** empty tree + tests that pass on `pass` is the
greenfield cheat. Policy already names `VACUOUS_ORACLE`. Wiring does not
supply the fact.

**LAW (tamper):** brownfield agents that edit assertions must die at admit.
A glob of `test/**` as the entire enumerated set is the wrong shield (easy to
dodge, easy to over-block). Shield the **verification subject** and the
implicated test files, not “every file named test”.

**WHY NOT mutation score as a finish law:** T-39 `[PROPOSAL]`, optional
treatment, not default. Cost kills long brownfield; the model then skips
tests. Use it as an ablation after MS-CONTROL, not a gate.

**WHY NOT “model picks which tests”:** it picks the green ones. The
implicated set is the oracle subject.

---

## 6. Cognition, meta-cognition, soul, heart, skills, prompts

**STM cognition that raises \(R\):** σ + pinned dead ends + goal echo at L5
tail + omission ledger. That is enough until MS-CONTROL exists.

**Meta-cognition (T-28):** advisory directives into ordinary proposals.
Suggest re-localize, escalate **model**, spawn investigator, compact. **Must
not:** admit `completed`; grow budget; be inherited by children; grade work.
FACT: `consult` is value-in / value-out.

**POST-v1 (`RESEARCH_META_COGNITIVE_ENGINEERING.md`):** Aether as a laboratory
for competing theories of intelligence (NOESIS / GENESIS / ECOSPHERE) is a
**lab ambition after v1 substrate**, not a 2026 product loop. The research
doc itself says do not put metacognition inside the definition of v1.0.
**Agree.** Vanguard/Higgs must not implement a particular theory of
intelligence; they must be the universe in which theories compete. Shipping
HYDRA-as-default *is* picking a theory.

**Skills LAW (Anthropic 2025–26, steal):** procedures with progressive
disclosure; names in the prefix; bodies on invoke. Deterministic “never do
this” is a **hook / kernel deny**, not a prompt. This tree already has that
shape (T-56). Keep `pytest-green` if it encodes argv truth. Kill decorative
catalogs.

**Soul / heart / character files:** WHY NOT always-on in L1. They burn prefix
cache and do not raise \(R\). If identity is needed, it is a **versioned
skill card**, body on invoke, rollback.

**Prompt engineering:** the one-page system prompt is an ACI contract (one
tool, patch format, argv). Further prompt packs are not this review’s job
and will not fix leaky admit. AHE (arxiv:2604.25850): tools/middleware/memory
beat system prompt. HarnessFix/HarnessLens: diagnose **which layer** failed
before editing prompts.

**WHY NOT unbounded reactive dialogue (C-15):** agrees with this tree’s one
effect + admit. Keep.

---

## 7. Agents, specialists, swarms, HYDRA, compounding

**LAW:** agent = pack + profile + tools + admission. Not a class hierarchy.

**Product arms today:** three names, one agent. `[PROPOSAL]`: differentiate
by budget, model route, `max_turns`, retrieval budget — not by new engines.

**Legitimate specialist packs** (same engine): investigator (read-only;
plan-mode verbs already withheld in `wiring.py`), test-runner (`proc.exec` +
parse only), localizer (index queries). Manifests exist for some — treat as
experimental until T-29 and a T-27 canary.

**Kill as product scores:** `vg-hexagonal`, `vg-archeologist-swarm`, Chimera
2.0, SONNET “four divergent paradigms” as the next sprint. The composition
*insight* (primitives → atoms → molecules → swarms) is fine as a vocabulary
for packs. The *product* is three budgeted arms plus optional investigator.

**HYDRA:** T-55 `[PROPOSAL]`; treatise non-canonical. Bifurcation is a later
topology over the same engine. Complexity functionals and Thompson-sampling
governors are how Chimera became a second brain. **Off by default, last.**

**Compounding Aether abstractions** (spawn, campaign, memory grants, skills):
this is the actual bet of the framework. **WHEN:** after settlement honesty.
Deterministic compounding before statistical (research_harness thesis) is
still the right order.

**Octopus ORCH-* pack sprawl:** WHY NOT eleven orchestration packs before one
wired tamper call. Progressive cost. One director client + CAS mailbox is
enough.

---

## 8. GraphOS, blast radius, callers

**LAW:** blast radius is an **observation** (import/call edges) plus **pack
policy** (implicated set), not a product named GraphOS.

Internet codegraphs and blast-radius MCP posts are query APIs. This tree
should grow IndexPort **observations** (`DependencyEdge` already exists) and
let pack completeness consume them. Do not import LangGraph “GraphOS”
wrappers. Do not put ranking in IndexPort.

**WHY NOT** “the index decided which snippet is in L3”. That is pack
`context_ranker.py` with identity in `selection_policy_identity` (T-46 stays
`[PROPOSAL]` and stays out of the port).

---

## 9. Logs, trajectories, benchmarking

**LAW:** compiled context must be reconstructable from events. If compiled
context ≠ `fold(events)`, resume will goal-amnesia at turn 80. Mini-SWE-agent
is right that linear history is debuggable; this tree already has a richer
object (the ledger). Make the **prompt** a projection of the ledger, which is
what prefix-stable compile + fold is for.

**Honest event producers:** if fold never sees `HypothesisRejected`,
compaction cannot pin dead ends. This is harness engineering, not a new
agent. Do not emit fake `HypothesisOpened` to look busy.

**Benchmarking LAW (board):** MS-CONTROL T-26 then T-27 freeze \(n\), models,
stop rule **before** paid calls. Canary disposition ∈ `{POSITIVE, NEGATIVE,
UNDETERMINABLE, INVALID}`. T-23 ≠ control. G-3: local ≠ official. DeepSWE
wrapper is T-33 **after** control. Score-band tables in `milestones.md` are
aspirations, not forecasts. “90/100 replaces staff engineers” is unsupported
always.

**WHY NOT** chase official leaderboards as the inner-loop spec. The remaining
45–60% of SWE-bench (research claim) is mostly localization + multi-file +
lying oracles — which is exactly settlement + implicated tests, not MCTS.

---

## 10. Scripts, tools, plugins, modularity

**LAW:** mediated verbs + allowlist. OpenHands CodeAct “bash as universe” is
a different ACI. Steal “run tests before finish”, not unrestricted shell.

**Skills as scripts:** deterministic pytest argv, formatters, oracle
scaffolds. Not prose recipes the model may paraphrase into `python3 -c`.

**Pack plugins** (`packs/code-default/plugin.yaml`): keep. **Must not** add
plugin verbs that bypass admit.

**Modular stacking:** features are optional **packs and policies**, not
kernel flags. Progressive cost: a tutorial agent must not load campaign +
HYDRA + memory promoter.

---

## 11. Internet SOTA — control laws only

Steal laws, not vendor cosplay:

| Source | Law to steal | Law not to steal |
|---|---|---|
| Claude Code | Worktrees; subagent **separate context**; CLAUDE.md as **facts** in L3 not a second constitution; skills progressive disclosure; hooks for deterministic denies | Always-on soul; treating their product UI as our architecture |
| Cursor | Apply/edit models as **adapter** recovery; index as observations; rules as L3 facts | Ranking-as-index; second engine |
| OpenHands | Tests before finish; sandbox | CodeAct unrestricted shell as product ACI |
| SWE-agent | ACI file viewer; history processors | Defining done as SWE-bench score |
| Aider | Repo map as **cheap structure**; architect/editor as two **inferences** same tools | Two-model split as Chimera |
| Letta/MemGPT | Git-backed memory **after** authorize-before-retrieve | Archival soup as product LTM before T-32 |
| AHE / HarnessFix | Diagnose layer; tools > prompts; don’t auto-evolve until events honest | Self-modifying harness as default |

---

## 12. Research corpus — keep / kill / postpone

| Document | Keep | Kill / postpone |
|---|---|---|
| DEKAS | Event-native loop, force ranking, prefix cache, anti-rot ledger, greenfield oracle, brownfield localize | Speculative checkpoint as second store before 2PC-is-default-write |
| ARCHON | Prototype contrast only | Do not implement a second kernel |
| Meta-cognitive engineering | Post-v1 lab; v1 = substrate | NOESIS in the coding arm |
| HYDRA treatise | Optional topology later | Default governor |
| SONNET super-agent | Composition vocabulary; routing-policy as a seam | Four product paradigms next sprint |
| future_improvements 2808 | Deprecated C-15/C-16; AST preflight in adapter | “RATIFIED” badges C-01–C-08 as HEAD truth; SBFL/MCTS/SWE-RL/eBPF/Z3 as near-term |
| SOTA roadmap `.draft` | Five systems challenges (horizon, greenfield DAG, blast radius, resume, anti-tamper) | File paths that do not exist; `EpisodeEngine.step()` |
| VANGUARD_SOTA_BACKEND_COMPLETION_PROGRAM | Historical; board has moved | Do not execute as a calendar |
| Octopus outer-loop | Kernel unchanged; director as client; sequential control | Evolutionary policy; 11 ORCH packs before tamper-on-admit |

That is the theory. Architecture deltas next.
