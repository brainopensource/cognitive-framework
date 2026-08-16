# Vanguard × LAM × Manifests — Sprints 7–10 Master Architectural Roadmap

**Status:** NON-NORMATIVE review and implementation guideline. Updated post-Sprint 6B closure (`v0.4.1-beta` candidate sealed with R0–R10 proofs, Ed25519 asymmetric verification, rootless Bubblewrap worker, and live RuntimeService). Where this file and a v4 owner disagree, the v4 owner wins (`PR-3`).

**Audience:** Project Lead, Tech Lead, Senior Architects implementing S7–S10 independently.

**Date:** 2026-08-16

**Inspected corpus:** `docs/main_v4` VG-00 … VG-12 plus GTS-13C (`13_C_gts_mvp_program_and_engineering_plan.md`).

**Inspected code:** `vanguard/packages/{domain,ports,kernel,agency,runtime,adapters}`, `vanguard/clients/cli`, `tools/002_LLM_API_MOCK`.

---

## 0. How to use this document

This is a **decision lock + packet map**, not a sprint backlog dump and not a second charter.

1. Read §1 (thesis) and §4 (hard decisions). If a packet would reverse a locked decision, stop and write an ADR citing the reversal condition — do not “just add the verb.”
2. Implement packets in §11 in order **unless** a packet’s “May start when” is already true.
3. Treat LAM as a **gym and cassette factory**. Treat Vanguard as the **instrument**. Never let the gym become a fake brain, and never let the instrument grow a second episode engine for a competitor clone.
4. Label every number: `lam-replay` | `cassette` | `live-ollama` | `live-openrouter-free` | `live-paid`. A number without a label is unpublished (`VG-01 §4.1`, `VG-07` “a number produced outside the rules is not a number”).

**For agentic workers later:** execute packets with TDD. Do not start from this file’s prose and invent kernel branches. Start from the named files and the falsification tests.

---

## 1. Destination thesis (what S7–S10 are for)

Vanguard’s mission (`VG-02`) is not “ship a Claude Code clone.” It is:

> When an agent solves a task, **what solved it** — model, scaffold, prompt, tools, context policy, retry — must be separable, and the judge must be unreachable from the judged.

Sprints 0–6 (Beta product slice `v0.4.1-beta`) froze **one** coding pack, `vg-code-default`, on **one** loop, establishing Chapter 10 Q1–Q2 closure.

S7–S10 exist to make the framework **earn** four fundamental proofs:

| Gate (Ch.10) | Sentence that must become true | Primary tickets |
|---|---|---|
| **S7: Configurability** | Claude-Code-shaped, OpenCode-shaped, and mini-SWE-agent-shaped harnesses are **pure data manifests**. `vg harness build \| run \| diff \| bench` exists. Reconstructions require **zero core changes**. | T7.1–T7.7 |
| **S8: Measurable (Q3)** | An A/A floor exists per task class against **`vg-shell-only`**. A paired comparison runs. The verifier–deployment gap has a measured number. | T8.1–T8.8 |
| **S9: Generality (Q4)** | One non-coding environment (TableWorld / structured-data reconciliation) is added through **registries, adapters, and configuration only**. | T9.1–T9.3 |
| **S10: Meta-Cognitive Release** | Exterior verdict telemetry, offline competence distillation, bounded non-authoritative memory recall, and full release gate dossier seal the Phase 3 MVP. | T10.1–T10.9 |

S9 is the MVP **gate review**, not “we look like Grok Build.” Competence promotion (`VG-06` active competence, `VG-07` L4) is **after** the instrument exists. Open concept O-01: do not design the promotion topology until one distilled artifact clears A/A.

**Product language vs architecture.** README’s `vg-code-frontier` four primitives (`repo.tree`, `ast.search`, `proc.interactive`, `patch.bundle`, correction memory) are a **pack/adapter target**. They are not kernel verbs and they are not a licence to auto-promote claims. `VG-12` is non-normative. `REJ-09` forbids “cognitive OS” as specification.

---

## 2. Authority map for this workstream

| Question | Owner | Do not restate here as if you owned it |
|---|---|---|
| What is an episode / observe-propose-authorise-effect | `VG-03` | Loop shape |
| Wire types, CorrectionRecord, Recording, Process* | `VG-04` / `domain/wire/contracts.py` | Field lists |
| Dispatch, grants, sinkClass, sandbox claim | `VG-05` / `kernel/` | Second path to effects |
| Claim pipeline, four stores, MEM-* | `VG-06` | “The agent learns” |
| A/A, pairing, splits, CL-1..3 | `VG-07` | Publishing a lift |
| What is out of Phase 0 | `VG-08`, `VG-10` DEF-* | MCP, semantic memory, public benches |
| Reversal conditions | `VG-09` ADRs | Silent reversals |
| Sprint sequencing, T7–T9 | GTS-13C (plan, **not** a contract) | Inventing tickets |
| Precedence | `VG-00` PR-1..PR-5 | This review outranking v4 |

GTS-13C itself says it **defines no contract, gates no merge, locks no decision**. Use it for *why* and *order*. Use the Active MVP Contract for *what is required*. Do not mark REQ-* covered from LAM evidence.

---

## 3. As-built vs destination (empirical, 2026-08-16)

This section is a **survey of the tree**, not a claim that Beta shipped.

### 3.1 What already exists and must be reused

**Hexagonal lattice (real).** `domain ← ports ← kernel ← agency ← runtime → adapters`. Boundary gate and `test/broken/` exist. Do not add `agency → adapters/evaluators`. Do not put approval logic in `agency/`.

**Kernel (real).** Single dispatch path S0–S12 (`kernel/dispatch.py`). `SinkRegistry` infers privileged prefixes `fs.write`, `fs.delete`, `net.`, `exec.`, `proc.`, `secret.` and observation prefixes `fs.read`, `fs.stat`, `fs.list`, `git.read`. Unknown actions fail closed as privileged. `MF-KRN-001` proves the widening classifier cannot be a constant.

**Composition (real, load-bearing).** `runtime/root.py` documents ADR-0060: adding a domain must require **zero** lines in `kernel/` or `agency/episode/`. `DEFAULT_BINDINGS` is the verb → adapter table. Missing verb ⇒ `CompositionError` **before** a run. This is the S7 falsification hinge.

Current bindings:

```text
fs.read, fs.search          → environment observer
fs.write, patch.apply, fs.patch → environment effector (diff-carrying)
proc.exec                   → sandbox effector (rootless)
```

There is **no** `fs.list`, `proc.test`, `repo.tree`, `ast.search`, `proc.interactive`, `patch.bundle`. `proc.test` appears in `ProposalTranslator.KNOWN_TOOLS` but not in `DEFAULT_BINDINGS`. The default pack’s test tool is already `verb: proc.exec` (`test-tool.json`). Do not invent `proc.test` in S7 unless you add a binding **and** a selector kind; prefer keeping tests as allowlisted `proc.exec`.

**Manifest freeze (real).** `domain/artifacts/manifest.py` parses, canonicalises selectors, freezes `composition_digest` per `episode_id`. Kind registry in `domain/artifacts/graph.py` and `agency/manifests/kinds.json` already lists every T7.1 kind including `skill`, `operator`, `competence_claim`. **Kinds exist; instances other than the two packs do not.**

**Two packs only (`agency/manifests/registry.json`):**

| Name | Role | undeletable |
|---|---|---|
| `vg-shell-only` | experimental-control | true (L-15) |
| `vg-code-default` | product-default | false |

`vg-code-default` capabilities: `fs.read`, `fs.search`, `patch.apply`, `proc.exec` (git,pytest,ruff,python3). GTS-13C §7.1 also shows `proc.test` and `fallback_tools: [shell@1]`. The pack does **not** currently declare a separate shell fallback tool file; shell is the same `proc.exec` capability. That is acceptable if reconstructions that need a **weaker** default and an **elevated** fallback are expressed as two capabilities with different selectors/risk, not as a kernel special case.

**Episode engine (real, narrow).** Depth-1: one proposal → one `EffectRequest` (`agency/episode/engine.py`). Default `max_turns=8`. Budget policy `depth: "1"`. `ProposalTranslator` **rejects multiple tool calls in one proposal** (`instrument_error`). Claude Code / OpenCode parallel tool use is **not** expressible without either (a) serialising in the adapter, or (b) reversing depth-1 (T4.7 independence groups). See D-02.

**Model port vs LAM (two different cassettes).**

| Object | Speaks | Lives in | Proves |
|---|---|---|---|
| `CassettePlayer` | `ModelPort.propose(context, tools, sampling) → {text, toolCalls}` | `adapters/models/cassette.py` | Vanguard loop still matches a recorded **proposal dialect** |
| LAM `LamEngine` | OpenAI `chat/completions` `messages` + `tool_calls` | `tools/002_LLM_API_MOCK/` | A **tool-loop gym** still matches a gold trajectory, $0, ~ms |

`VG-01 §4.1`: a mock taught by reading its consumer cannot prove agreement with a real endpoint. LAM is that mock **plus** a gold workspace+pytest oracle. Vanguard cassettes are request-digest keyed. **Do not merge the stores.** A bridge (`vanguard_bridge.py`) may translate names; it may not teach the kernel `view_file`.

**Context compiler (real).** L1–L5, prefix-stable. Do not inject full AST dumps into L3.

**CorrectionRecord (schema real, service thin).** `domain/wire/contracts.py` enforces T1.10 fields, reason-code enum, and **style / architecture_preference ⇒ scope ∈ {user, team, repo}**. `RuntimeService._cmd_RecordCorrection` appends a loosely typed payload and does **not** call `parse_wire("CorrectionRecord", ...)`. S7 packet: bind the parser. Do not promote from this event.

**Evaluator (partial).** Manifest names `coding-oracle@3` → `EvaluatorClient`. Beta audit: no attested UID-10002 product composition. S8 meta-evaluator (T8.7) is meaningless until a real exterior verdict exists. Instrument work can still run with **labelled** `inconclusive` and must-fail fakes; it cannot publish Q3.

**TableWorld:** `EnvironmentProfile.kind` comments `"memory" | "git" | "tableworld"`. **No adapter.** T9 is greenfield behind the existing port.

**CLI:** TypeScript client, Unix RuntimeService intended. `RecordCorrection` is a command name in `live.ts`. `vg harness *` **does not exist**. Until the daemon product path is honest, the S7 bench may live as a **lab entrypoint** that calls `Runtime.compose` in-process, labelled `lab`, never advertised as Beta CLI.

### 3.2 LAM as-built (gym, not Vanguard)

| Piece | State | Implication |
|---|---|---|
| `engine.py` | Stateless turn select by `role=tool` count | Correct mock physics |
| `simulate.py` | Local atoms + pytest; system prompt says **“You are OpenCode”** | Prompt is pack-level in Vanguard; LAM currently hardcodes a competitor persona. Fix: scenario or harness-id selects prompt |
| `schema.py` | Atoms `view_file, edit_file, run_command, grep_file, list_dir`; ids `^t[1-5]-` | T6 project traces blocked by regex. Extend to `t6-` when T6 exists |
| `ladder.py` | LAM path uses `simulate_scenario`; live OpenRouter/Ollama complete fns exist | Live escalate must remain fail-closed on T1 fail |
| `vanguard_bridge.py` | Name map only | Allowed. Kernel aliases forbidden |
| `models.json` | `top` is populated with high-band ids | Contradicts fail-closed “PL names three ids.” S7: `top: []` until Decision Record says otherwise |
| `store.py` | Imported by `ladder.py`; not present in tree at review time | Packet 0: implement or stop importing |
| Gold scenarios | t1–t5 family (~10 JSON files) | Insufficient for T8 task-class A/A; enough to start harness *mechanics* replay |

LAM `simulate.py` pass heuristic historically mixed “tests passed” with “more than one LLM call.” Any remaining `passed` stub is a **blocker** for every number in FIT.md.

### 3.3 README frontier primitives vs code

They are **not implemented**. Mapping onto v4 is §6. Implementing them inside `EpisodeEngine` would falsify ADR-0060 / M11.

---

## 4. Hard decisions (Project Lead + Tech Lead)

Each row is a **hypothesis with a reversal condition**. Implementers do not reopen them for convenience (`T10.9`: a conditional naming one competitor is a defect).

### D-01 — Two cassette systems, one ModelPort

**Decision.** Keep LAM and `CassettePlayer` distinct. Vanguard CI of the **loop** uses ModelPort cassettes (proposal dialect). LAM CI of **trajectories and model ceilings** uses OpenAI chat completions. Live providers (Ollama, OpenRouter) implement ModelPort **or** a 20-line adapter into LAM’s `complete` fn — never a third dialect in `agency/`.

**Why.** Merging them produces the historical bug: a mock that cannot see the assistant tool-call message (`VG-01 §4.1`). The dialects already diverge (`{text, toolCalls}` vs `choices[].message.tool_calls`).

**Reversal.** A single golden vector set is proven byte-identical across both stores **and** both parsers, with a migration of the existing cassette corpus. Until then, dual-store is cheaper than a silent dialect squash.

### D-02 — Depth-1 remains the engine; reconstructions serialise parallel tools

**Decision.** S7 reconstructions **must not** change `EpisodeEngine` to N effects per turn. A Claude-Code-shaped pack that “wants” parallel `Read` calls is implemented by **N serial observation turns**, or by a **single** `fs.search` / `repo.tree` that returns many hits. `ProposalTranslator` continues to reject `len(toolCalls) != 1` unless an ADR supersedes this.

**Why.** T4.7: mutations are barriers; parallelism requires declared independence or disjoint read/write sets. Today there is no independence-group type in the engine. Teaching the loop “Claude parallel tools” is a **core change**, which **falsifies T7.6** if done “so the reconstruction looks right.”

**Honesty label.** `vg-code-claude-shaped` is a reconstruction of **tool surface + prompt + context policy**, not of Anthropic’s scheduler.

**Reversal.** T4.7 independence groups land with property tests; translator accepts N **observation** calls with proven disjoint selectors; privileged calls remain singleton. Then a `parallel-obs@1` middleware artifact may exist. Not in S7.

### D-03 — No live PTY (`proc.interactive` is not a handle)

**Decision.** Reject a live interactive shell handle in the model context (`VG-03`: observe returns a snapshot, never a live handle). S7–S8 “terminal co-pilot” = `proc.exec` with **chunked receipts** (stdout/stderr bounded, timeout, process-group kill T4.6), still one privileged descriptor.

**Why.** A PTY is a capability-widening session: argv, cwd, env, and subsequent writes are not the approved descriptor. `REJ-07`: shell parsing is not a security boundary. The perimeter is.

**Reversal.** An ADR for `proc.session` that: (1) grant binds `{argv0, cwd, envDigest, ttl, maxBytes}`; (2) every stdin chunk is a new privileged effect or is denied; (3) no file descriptor enters L5; (4) cancel kills the group. Explicitly **not** “Claude bash.”

### D-04 — New verbs are registry rows, not engine branches

**Decision.** A new coding primitive is: (a) `tool_schema` artifact, (b) capability line, (c) `DEFAULT_BINDINGS` row **or** a factory keyed from a **closed** adapter registry in `root.py`, (d) `SinkRegistry` prefix or explicit register, (e) selector kind that `includes` is decidable (`T1.3`). **Zero** `if harness == "claude"` in `agency/` or `kernel/`.

**Why.** Open/closed (`VG-01`), L-13 (coding is not the ontology), T10.9.

**Reversal.** Never for competitor names. A new **environment kind** (browser, TableWorld) is an adapter behind `EnvironmentAdapter`, still one loop.

### D-05 — Translator must become manifest-driven (S7 P0 for configurability)

**Decision.** `ProposalTranslator.KNOWN_TOOLS` is a **Beta freeze**, not the S7 architecture. T7.6 is **falsified** the day a reconstruction needs a new OpenAI tool **name** and a senior adds it to the hardcoded dict **and** to the engine.

**S7 rule.** Frozen harness tool schemas are the only name→verb map. Unknown names ⇒ `instrument_error`. Verbs not in `DEFAULT_BINDINGS` ⇒ fail at **composition**, not at turn 3.

**Allowed temporary aliases** in a **pack-local** `aliases.json` (artifact kind `middleware` or a field on `tool_schema`): `Bash→proc.exec`, `Read→fs.read`. Aliases are data. A global Python dict of competitor names is a second ontology.

**Reversal.** None while ADR-0060 holds.

### D-06 — `vg-shell-only` is the only legal control arm

**Decision.** Every claim “typed tools / repo map / skills help” is a **paired** comparison against `vg-shell-only` under T8 (`L-15`). Deleting or “simplifying away” the baseline is forbidden (`ManifestRegistry.remove` already throws). LAM replay of `vg-code-default` gold is **not** an A/A floor.

**Why.** LAM is deterministic. A/A of a cassette is degenerate (variance ≈ 0) and will **invent significance** for any live arm (`CL-3`).

**Reversal.** L-15’s measured evidence that typed tools cost more than they return — still does not license deletion; it licenses **not using** typed tools as default.

### D-07 — LAM never sets competence; corrections are episodic

**Decision.** `RecordCorrection` writes `CorrectionRecorded` after `parse_wire`. Recall into L5 is **data without instruction authority** (`MEM-4`). Style/preference cannot be `scope: general`. No packet in S7–S9 may “fine-tune from corrections” (`DEF-09`, `MEM-7`). Distillation is an **offline optimiser** emitting **candidate artifacts** with invalidation conditions — Phase after S9, trigger O-01.

**Reversal.** `VG-06 §5` promotion has run on a real artifact that cleared A/A **and** ablation. Then write the lifecycle doc (`DEF-10`).

### D-08 — Public leaderboards are still deferred

**Decision.** No SWE-bench Verified/Lite/Pro publication in S7–S9 (`DEF-08`). Internal corpus only. The phase-2 review already forbids treating mixed SWE percentages as decisions.

**Reversal.** Phase 3, after T8.1 noise floor is non-degenerate **on live models**, splits exist, and the verifier–deployment gap is monitored.

### D-09 — Reconstruction honesty

**Decision.** Names:

| Manifest id | What it is allowed to claim |
|---|---|
| `vg-code-claude-shaped` | Our **reimplementation** of a documented tool/prompt **shape** |
| `vg-code-opencode-shaped` | Same, OpenCode-shaped |
| `vg-code-swe-mini` | Same, mini-SWE-agent-shaped |
| `vg-code-kilo-shaped` / `vg-code-codex-shaped` / `vg-code-grok-shaped` | **S8+ optional**, only after the first three compose without core changes |

Never: “beats Claude Code,” “equivalent to Codex.” GTS-13C §7.3: a comparison against a reimplementation is a comparison against **that reimplementation**.

**Reversal.** A legal agreement to run vendor binaries as an arm, with the same evaluator and instance set. Out of scope here.

### D-10 — Instrument CLI vs product CLI

**Decision.** `vg harness {build,run,diff,bench}` is specified in GTS-13C T7.5. If RuntimeService is not yet a trustworthy product path (Beta audit NO-GO), ship first as:

```text
python3 -m vanguard.lab.harness {build,run,diff,bench}
```

under `lab/` (**imports nothing production, imported by nothing** — T10.1). Promote onto `vg harness` only when the CLI talks to a real daemon and cannot succeed on empty stdin (P0-01 of the Beta audit).

**Reversal.** Product path closed; then the lab module becomes a thin wrapper or is deleted.

### D-11 — Parallel tool names vs kernel verbs

**Decision.** LAM atoms stay `view_file | edit_file | run_command | grep_file | list_dir` (+ later `repo_tree`, `ast_search`, `patch_bundle` as **LAM-only** names). Kernel verbs stay `fs.* | patch.apply | proc.exec`. Packs declare the **model-visible** name; composition binds the verb.

**Why.** Teaching the kernel OpenCode names is ARCH-02 / M11.

### D-12 — Turn bounds live in budget_policy, not engine defaults

**Decision.** `EpisodeEngine(max_turns=8)` is a Beta default. S7 manifests set `effects` / a `maxTurns` field in `budget_policy`. T5/T6 project scenarios may need 15–40 **observation+effect** turns. The engine reads the frozen policy. A reconstruction that “needs 80 turns like Claude” is a **budget artifact**, not a loop fork. Caps remain hard; overrun ⇒ `BUDGET_EXHAUSTED` / `ABANDONED`, not silent continuation.

### D-13 — `top` band is empty until named in the Decision Record

**Decision.** `tools/002_LLM_API_MOCK/models.json` `top` must be `[]` (or absent) until Project Lead records three ids. Current populated `top` is a **process defect**. Paid `high`/`medium` require `allow_live_call` and the uncommitted ledger convention (10 live calls = $0.05 wave accounting, even if provider $0 for `:free` **call counts**).

### D-14 — Indexing is an observation adapter (`DEF-04` / `DEF-05`)

**Decision.** `repo.tree` / `ast.search` are **not** a systems-language index in S7 (`ADR-0006`, `DEF-05`). Python/tree-sitter **inside the worker** returning a **size-capped snapshot** is allowed as `sinkClass: observation` if composition binds it. Do not add an in-kernel index. Do not claim semantic search.

**Reversal.** Measured first-token/context cost on a real repo crosses a stated threshold (`07 §5.8`) — then a dedicated index adapter, still not kernel.

### D-15 — TableWorld is the generality falsifier, not a coding feature

**Decision.** T9 in S8 as GTS-13C scheduled. If TableWorld requires `EpisodeEngine`, capability algebra, or event envelope changes, **H0 / C-10 is falsified** — file a finding, do not “make the engine more general” in the same PR as the adapter.

---

## 5. Target architecture (S7–S9 system)

```text
                         ┌─────────────────────────────────────────┐
                         │  Harness packs (data)                   │
                         │  vg-shell-only                          │
                         │  vg-code-default                        │
                         │  vg-code-claude-shaped                  │
                         │  vg-code-opencode-shaped                │
                         │  vg-code-swe-mini                       │
                         │  vg-tableworld-default  (S8)            │
                         └─────────────────┬───────────────────────┘
                                           │ compose() freeze
┌──────────────┐   ModelPort    ┌──────────▼──────────┐  Kernel.dispatch
│ Ollama       │◄──────────────►│ Runtime.compose     │──────────────► adapters
│ OpenRouter   │                │ EpisodeEngine       │   Environment / sandbox
│ Cassette     │                │ ContextCompiler     │   Evaluator (exterior)
│ LAM-as-port* │                └──────────┬──────────┘
└──────────────┘                           │
                                           ▼
                         ledger L  +  FrozenHarness.composition_digest
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              ▼                            ▼                            ▼
     lab harness bench              LAM gym (tools/)              competence
     T8 A/A + paired                record/replay traces          (after S9)
     same evaluator                 SQLite/JSONL metadata         VG-06
```

`*LAM-as-port`: optional `LamOperator` that implements `ModelPort.propose` by translating to OpenAI complete **if and only if** the translation is lossless for that pack’s tool schemas. If lossy, **do not ship the port**; run LAM beside Vanguard, not inside it.

**Three closure conditions (`VG-07` CL-1..3)** still bind every bench number:

- Judge exterior (evaluator not in agency).
- Promote set ⊥ optimise set (LAM gold used to **tune prompts** must not be the holdout used to **claim lift**).
- Delta > A/A noise of the **same live configuration**, not of LAM.

---

## 6. Frontier primitives — implementation physics

### 6.1 Interactive workspace map — `repo.tree` / `ast.search`

| Axis | Spec |
|---|---|
| Model-visible names | `RepoMap` / `repo.tree`, `AstSearch` / `ast.search` (pack aliases) |
| Kernel verb | Prefer **`fs.list`** for tree; **`fs.search`** with `mode=ast` **or** new `fs.ast` if selector needs a language id |
| sinkClass | `observation` |
| Selector | `glob` / `path` under worktree root only |
| Adapter | Worker: walk + optional tree-sitter. Return `{digest, truncated, entries[]}` with byte cap from budget_policy |
| Context | Optional small L3 fragment; never dump the index |
| LAM atom | `list_dir` already; add `repo_tree` only if gold traces need a distinct shape |
| Earn vs baseline | T8 paired vs `vg-shell-only` (model may `find`/`grep` via shell). If repo map does not beat shell on holdout, it stays optional in `vg-code-default` |

**Aider note.** Aider’s repo map is the reference *mechanism* (Tree-sitter, token budget). Reconstruct the **property** (ranked symbol sketch), not Aider’s code. Ablate map on/off under the **same** model.

**Falsify.** Index reads evaluator paths; unbounded output; kernel import of tree-sitter.

### 6.2 Terminal co-pilot — `proc.interactive`

See D-03. Implementation in S7: improve `proc.exec` receipts (exit, truncated stdout, duration) and allowlist. Do **not** add a verb until D-03 reversal.

Claude Code / Grok Build / OpenCode “bash” in reconstructions = alias to `proc.exec` with **their** allowlist in the pack (often wider). Wider allowlist is a **capability** change (risk, selector), reviewed as security, not as UX.

### 6.3 Multi-file staging — `patch.bundle`

| Axis | Spec |
|---|---|
| Kernel | One `patch.apply` whose args are a **multi-file unified diff** or `{files: [{path, hunks}]}` |
| Grant | One descriptor digest covering the **canonical normalised bundle** |
| Git | T7.2 already: one `LogicalEdit` → one commit in `domain/artifacts/graph.py` |
| Approval | T6.6 descriptor-bound; extra file after approval is substitution (must-fail already required for Beta) |
| Depth-1 | A bundle is **one** privileged effect — compatible with D-02 |
| LAM | `edit_file` may already be single-file; T3+ gold should include one multi-file apply |

**Do not** implement N `fs.write` then a commit as “bundle.” The environment’s diff is the definition of the change (`VG-03 §2.2`).

### 6.4 Correction memory

Wire is done. S7 work is **integrity**, not intelligence:

1. `RecordCorrection` → `parse_wire("CorrectionRecord")` or reject.
2. Projection: correction table keyed by `episodeId`, not by prompt text.
3. Optional L5 **non-authoritative** block: “prior human correction in this repo (style, local): …” only if `scope ∈ {user,team,repo}` and data policy allows.
4. LAM: store `(proposedPatchDigest, acceptedPatchDigest)` beside traces for later distillation. No in-engine learning.

`ExplainArtifact` currently returns empty explanation — T6.5 `vg why` is S7 if dogfood needs it; it is not a reconstruction requirement.

---

## 7. Harness zoo — ICD for implementers

### 7.1 Composition invariant (test this first)

```text
GIVEN a directory agency/manifests/<id>/
WHEN Runtime.compose(manifest.json)
THEN FrozenHarness.composition_digest is stable
 AND every capability.verb ∈ DEFAULT_BINDINGS
 AND SinkRegistry.accepts each sink
 AND unknown kind ⇒ GraphError
 AND vg-shell-only cannot be removed from registry.json
```

**Core-change detector (T7.6 / T9.3).** CI job: reconstructions and TableWorld PRs must not modify:

```text
vanguard/packages/kernel/**
vanguard/packages/agency/episode/**
vanguard/packages/domain/wire/**
```

unless the PR is explicitly `ADR-XXXX core change` and Tech Lead + Project Lead are on the review. A reconstruction PR that touches those trees **fails CI**. That *is* the configurability experiment.

Allowed: `agency/manifests/**`, `runtime/root.py` **binding table rows only**, `adapters/**` new modules, `lab/**`, `tools/002_LLM_API_MOCK/**`.

`root.py` binding-table-only is a grey line: adding a row is the designed extension point (open/closed). Adding an `if` on harness name is not. Architecture test: `root.py` has no string literals of competitor harness ids.

### 7.2 Pack directory contract

```text
vanguard/packages/agency/manifests/<id>/
  manifest.json              # harness, components, capabilities, evaluators, budgetPolicy, undeletable
  system-prompt.txt
  *-tool.json                # {name, verb, description, parameters?}
  context-policy.json
  routing-policy.json
  budget-policy.json
  aliases.json               # optional model-visible name → verb (data)
  REFERENCE.md               # non-normative: which public docs were read; what was NOT copied
```

Register in `registry.json`. Role enum suggestion: `experimental-control | product-default | reconstruction | generality-witness`.

### 7.3 Tool-surface matrix (S7 reconstructions)

**Legend.** E = existing verb/binding. A = alias only. N = new binding allowed in `root.py`. X = forbidden in S7 (core or deferred).

| Competitor-shaped behaviour | Claude-shaped | OpenCode-shaped | SWE-mini | Kernel |
|---|---|---|---|---|
| Read file | A `Read`→`fs.read` | A `read`/`view_file` | A | E |
| Grep / glob | A + `fs.search` | A | often glob+python | E |
| Structured edit | A `Edit`→`patch.apply` | A | often full-file write `fs.write` | E (`fs.write` already bound) |
| Bash / shell | A `Bash`→`proc.exec` **wide allowlist** | A | A | E |
| Tests | `proc.exec` pytest | same | same | E |
| Repo map | N `fs.list` or capped `repo.tree` | optional | no | N observation |
| AST search | optional N | no | no | N observation |
| Todo list | **skill + L4 file the agent edits** or operator data; not a kernel todo verb | same | no | no new verb |
| CLAUDE.md / AGENTS.md | L3/L4 files in workspace; agent `fs.read`s | `AGENTS.md` analog | no | no memory store |
| Subagents | X (DEF-03); operator = child episode is T4.10, not S7 reconstructions | X | X | X |
| MCP / browser | X DEF-04 | X | X | X |
| Parallel tools | serialise (D-02) | serialise | n/a | X |
| Interactive PTY | X D-03 | X | X | X |
| Plan mode | playbook artifact or prompt section; **not** a workflow DAG (`REJ-01`) | same | no | data |
| LSP diagnostics | X as authority; optional observation later | OpenCode-shaped may **claim** LSP in REFERENCE.md as unimplemented | no | X |

**mini-SWE-agent-shaped** is the **cheap control among reconstructions**: few tools, short prompt, `maxTurns` small. It is not `vg-shell-only`. Shell-only remains the **zero-assumption** floor (shell is the only tool). SWE-mini still has typed read/edit in most public designs — if the public mini-SWE-agent is bash-only, **map it to `vg-shell-only` plus a different system prompt**, not a fourth verb set. Read the upstream README at implementation time and record the mapping in `REFERENCE.md`. If bash-only, **do not duplicate** `vg-shell-only`; add `vg-code-swe-mini` only if the tool surface actually differs.

**Recommended S7 three-pack (to satisfy T7.6 literally):**

1. `vg-code-claude-shaped` — Read/Edit/Bash/Grep aliases, longer prompt, optional `CLAUDE.md` convention in the **task workspace** not the pack, `maxTurns` 32, no subagents.
2. `vg-code-opencode-shaped` — provider-agnostic prompt, session-like L5 retention policy (compaction still recency — `DEF-11`), tools aligned to OpenCode’s public tool list **as aliases**.
3. `vg-code-swe-mini` — **if** distinct from shell-only; otherwise document T7.6 as `vg-shell-only` + `vg-code-default` + `vg-code-claude-shaped` and **amend GTS ticket text** via Decision Record (do not silently skip OpenCode).

**Kilo / Codex / Grok (S8+, optional packets).** Same matrix. Kilo CLI derives from OpenCode (phase-2 review): likely **alias pack** of `vg-code-opencode-shaped` with a different prompt/budget, not a new adapter. Codex approvals/subagents: approvals already exist as process engine; subagents stay DEF-03. Grok Build: Rust TUI is **client** (`VG-09` ADR-0001 already chose TS control plane); do not rewrite CLI in Rust to “mimic Grok.” Reconstruct **hooks/skills** as artifacts.

### 7.4 `vg harness` / lab commands

| Command | Meaning | Done when |
|---|---|---|
| `build` | Load pack, compose, print `composition_digest`, list verbs, fail if unwired | Golden digest vectors |
| `run` | Execute one task dir against one frozen harness + ModelPort (cassette/LAM/live labelled) | Terminal + evaluator or labelled inconclusive |
| `diff` | Symmetric difference of two frozen graphs (tools, prompts, caps, budgets) | Human-readable + machine JSON |
| `bench` | Paired arms, same instances, same evaluator, pre-registration hash | T8.2 minimum: two manifests, N instances, discordant table |

Pre-registration artifact (T8.4) **hashed before any arm runs**:

```text
hypotheses, primary metric, alpha, correction, manifest hashes, model id,
stopping rule, corpus split ids, instrument-error policy
```

If any arm is LAM replay, the pre-reg file **must** say `backend: lam-replay` and the result **must not** be used as Q3.

---

## 8. Measurement laboratory (T8) — how not to lie

### 8.1 What LAM is allowed to measure

| Quantity | LAM replay | Live Ollama / `:free` | Paid |
|---|---|---|---|
| Harness **mechanics** (tools fire, tests run, digest stable) | Yes, CI | Optional | Wasteful |
| Model **ceiling** (highest tier with ≥1 pass) | No | Yes, labelled | Yes, budgeted |
| A/A noise floor (CL-3) | **No** (degenerate) | Yes if N repeats | Yes |
| “Claude-shaped beats default” | Only as **mechanics** (did both packs apply the gold patch?) | Yes, paired, holdout | Yes |

### 8.2 Task classes for a non-degenerate A/A (when live)

GTS T8.1: ≥3 task classes. Suggested internal classes (not SWE-bench):

1. **T1 syntactic** — single file, LAM already has gold.
2. **T2 multi-file** — two modules + test.
3. **T4 workflow** — docs/todos + code (still mechanical tests).

N repeats of **identical** manifest+model+seed policy. If pass-rate variance is 0 because the model always fails, the floor is **degenerate** and **must refuse to report** (GTS T8.1 tests). That is a valid S7 outcome.

### 8.3 Metrics tuple (every row)

Copy this schema; do not invent FIT.md columns ad hoc:

```text
arm_id, manifest_id, composition_digest, backend, model,
instance_id, task_class, split,
passed, terminal, evaluator_class, instrument_error,
llm_calls, prompt_tokens, completion_tokens, usd, wall_s,
denials, approvals, corrections,
label ∈ {lam-replay, cassette, live-ollama, live-openrouter-free, live-paid}
```

`inconclusive` excluded from numerator **and** denominator (`L-07`).

### 8.4 Contamination

LAM gold used to **author** `vg-code-claude-shaped` prompts is `DEV`. Holdout instances never seen by pack authors are `HOLDOUT`. Sealed stays sealed (`T8.5`). Touch ledger: if a human opened a holdout after freeze, the instance is burned.

---

## 9. LAM evolution for almost-free benches

### 9.1 Role split (repeat until boring)

- **Populate slowly** with Ollama and OpenRouter (free → named paid).
- **Replay** in CI and in `lab harness bench --backend lam`.
- **Metadata** in SQLite/JSONL: scenario, trace, model_ceilings, budget_events.
- **Never** sample “intelligence” in `engine.py`.

### 9.2 Schema extensions (library, TDD)

1. Scenario `id` allow `t6-` for project-scale recordings (15–40 turns, ≥8 files). Hand-authoring T6 is forbidden; **record** from a live pass.
2. Optional `harness_id` on a scenario: which pack’s tool names the gold uses. Same bug, two golds, if Claude-shaped aliases differ in call shape.
3. `validate_scenario` atoms stay disjoint from kernel verbs.
4. `--record` writes gold **only if** pytest passed **and** schema valid.
5. Importer: OpenAI JSONL → scenario; reject unmappable tool names (no guess).
6. System prompt: stop hardcoding “You are OpenCode.” Parameterise.

### 9.3 Ladder rules (already intended; make tests own them)

- T1 fail ⇒ do not call T2 (`--escalate`).
- Stubbed `passed: True` is a merge blocker.
- Free band live ≠ 10 ms LAM. `ladder_free.json` wall time and backend field must make this obvious.
- `load_api_key` / env_loader SEC-003; no raw `.env` scrape in new code (`ladder.py` currently scans `.env` — **align to `adapters/models/env_loader.py`** in the same packet as live ladder, do not fork a third loader).

### 9.4 Vanguard cassette capture from LAM

Preferred S8 path: run `Runtime.execute_harness` with ModelPort = live or LAM-bridge; **CassetteRecorder** writes proposal dialect. Then CI uses `CassettePlayer`. That tests **the real translator**, which LAM `simulate.py` never does.

If the bridge is lossy, **do not** claim Vanguard-on-LAM. Claim LAM-gym-only.

---

## 10. TableWorld (S8 T9) — enough to not derail S7

**Environment:** structured tables, constrained reconciliation, derived transform, inconsistency → **abstention** (`VG-08` Increment C).

**Evaluator:** domain-native, same `Evaluator` port, different image/predicate. Not `coding-oracle@3`.

**Tools:** e.g. `table.read`, `table.diff`, `table.patch` as **new verbs** in bindings + a `tableworld` adapter. If you instead overload `fs.read` on CSV files, you have **not** added a second environment; you have added a coding task. That fails C-10’s spirit.

**LAM:** a tiny non-coding scenario bank is optional and must not share coding atoms without a prefix (`table_read`).

**Falsify:** any import from `agency/episode` into the adapter; any envelope field added “for tables.”

---

## 11. Independent implementation packets

Order is dependency order. Owners can work in parallel **only** where “May start when” allows.

### Packet 0 — Honesty and gym floor (LAM, 1–2 days)

**May start when:** now. **Must not touch:** `kernel/`, `agency/episode/`.

- Implement or remove `store.py` import.
- Un-stub ladder; test T1 fail blocks T2.
- Stop hardcoded OpenCode persona.
- `top: []` until Decision Record.
- Align API key load with `env_loader`.
- FIT.md regenerated from labelled JSON only.

**Done:** `python3 -m unittest` for LAM; `simulate` all gold < 1s total; no secrets printed.

### Packet 1 — Manifest-driven translator (Vanguard, 2–4 days)

**May start when:** now. **Touches:** `adapters/models/invocation.py`, tests. **Does not** add competitor packs yet.

- Name→verb solely from frozen tool schemas (+ optional `aliases.json`).
- Keep one-call-per-turn rejection (D-02).
- Architecture test: `KNOWN_TOOLS` shrinks to empty or to a deprecated alias table loaded from data.

**Done:** existing vg-code-default tests green; a pack-local alias `Read`→`fs.read` works without Python edit.

### Packet 2 — Lab harness CLI (T7.5, 3–5 days)

**May start when:** Packet 1 in review. **Lives in:** `lab/` or `tools/vg_harness/`.

- `build | run | diff` against `vg-shell-only` and `vg-code-default`.
- `run` uses cassette or fake model first (no network).
- Print composition_digest.

**Done:** two packs compose; diff JSON stable; labelled `lab`.

### Packet 3 — Observation: `fs.list` / capped tree (optional for Claude-shaped)

**May start when:** Packet 1 merged. **Touches:** `DEFAULT_BINDINGS` row, worker, sandbox, classifier already has `fs.list` prefix.

- Byte cap; snapshot digest; selector.
- LAM atom `list_dir` already; record one gold using it.

**Done:** composition of a pack that declares `fs.list`; must-fail path escape.

### Packet 4 — Three reconstruction packs (T7.6, 4–8 days, parallelisable per pack)

**May start when:** Packets 1–2 merged. **Touches:** `agency/manifests/**` only (+ registry). Core-change CI on.

Each pack: `REFERENCE.md` citing **public** docs/repos read (Claude Code tool list, OpenCode tool list, mini-SWE-agent). No copied proprietary prompts beyond what is public. No claim of parity.

**Done:** `lab harness build` all three; `diff` vs default; **in-process** cassette run of a T1 instance on each (mechanics). Any need to edit kernel ⇒ stop, write finding.

### Packet 5 — `patch.bundle` as multi-file `patch.apply` (2–3 days)

**May start when:** Packet 1 merged. **Touches:** environment apply path, approval descriptor canonicalisation, tests for atomicity.

**Done:** two-file preview; crash mid-apply leaves no partial commit; approval substitution must-fail still holds.

### Packet 6 — CorrectionRecord integrity (1–2 days)

**May start when:** now. **Touches:** `runtime/service/service.py`, wire parse, CLI golden vectors.

**Done:** invalid scope+style rejected; valid record round-trips; no promotion.

### Packet 7 — Paired bench skeleton (T8.1–T8.2, 3–6 days)

**May start when:** Packet 2 merged. Fake/cassette arms first.

- Pre-reg hash enforced.
- A/A on cassette **must refuse** or be labelled `not-a-floor`.
- Live A/A is a **separate** operator job with budget.

**Done:** JSON report with discordant pairs; McNemar **not required** until N is large enough — do not print p-values on N=3 (`VG-07`).

### Packet 8 — Live populate (operator, budgeted)

**May start when:** Packet 0 done. **Not** unprompted.

- Ollama T1 documented.
- OpenRouter free `--escalate` on gold; write `runs/ladder_free.json` with backend field.
- New $0.50 wave only after PL approval; 10 calls ⇒ ledger line.

**Done:** ceilings table with evidence_trace_id; Lightning T1 fail recorded as fail.

### Packet 9 — Vanguard cassette from real translator (S8)

**May start when:** Packet 1 + a working `Runtime.execute_harness` path.

- Record one T1 through ModelPort.
- Replay byte-identical (`T3.8`).

**Done:** CI job, no network.

### Packet 10 — TableWorld adapter (T9, S8)

**May start when:** Packet 2 exists (so composition is the extension proof). **Forbidden files:** episode engine, kernel algebra, wire envelope.

**Done:** four Increment C stories; core-change detector green; domain evaluator under same port.

### Packet 11 — Meta-evaluator + sabotage (T8.7–T8.8, S8)

**May start when:** exterior evaluator is **actually** exterior (Beta P0), not `image_digest=unverified` theatre.

**Done:** seeded proxy-exploit rejected; gap dashboard can freeze promotions (even if freeze only logs, because automated promotion does not exist yet).

### Packet 12 — Optional competitor alias packs (S8–S9)

Kilo = OpenCode-shaped + prompt. Codex = default + process-definition emphasis. Grok = default + skills artifacts. Each is a **pack**, not a CLI rewrite.

**Done:** `lab harness diff` shows only artifacts/prompt/budget deltas.

### Packet 13 — S9 Generality & Gate Dossier (leads)

Answer GTS-13C Ch.10 four questions with **evidence paths**, not slides. Include negative results (degenerate A/A, reconstruction that needed a core change, TableWorld H0). Negative results are publishable (`VG-02`).

### Packet 14 — S10 Meta-Cognitive Release, Offline Distillation & Release Dossier (leads & devs)

**May start when:** S7–S9 gates are satisfied.

- **Non-authoritative memory recall:** Integrate historical `CorrectionRecord` into L5 context compiler without granting instruction authority (`MEM-4`).
- **Offline Competence Distillation (O-01):** Pipeline candidate skills/artifacts from successful paired trajectories into offline candidate registry; verify against holdout sets before promotion.
- **Dynamic Workspace Context Injection:** Ensure `AGENTS.md` / `CLAUDE.md` discovery is parsed through standard `fs.read` observation into L3/L4.
- **Phase 3 Release Sealing:** Run candidate release runner, verify zero regression on Beta invariants, and tag production `v1.0.0-phase3`.

---

## 12. Files map (where work goes)

| Concern | Path | Notes |
|---|---|---|
| Packs | `vanguard/packages/agency/manifests/` | Data only |
| Kind registry | `kinds.json` + `domain/artifacts/graph.py` BUILTIN_KINDS | Extend via schema, not enum in kernel |
| Bindings | `runtime/root.py` `DEFAULT_BINDINGS` | Rows only |
| Translate | `adapters/models/invocation.py` | Manifest-driven |
| Loop | `agency/episode/engine.py` | **Do not** for reconstructions |
| Dispatch | `kernel/` | **Do not** for reconstructions |
| Git/sandbox | `adapters/environment/*`, `adapters/sandbox/*` | New observation ops |
| Service commands | `runtime/service/service.py` | Parse CorrectionRecord |
| Product CLI | `vanguard/clients/cli` | After daemon honesty |
| Instrument | `lab/` (preferred) | T10.1 isolation |
| LAM | `tools/002_LLM_API_MOCK/` | Gym |
| Bridge | `vanguard_bridge.py` | Names only |
| Wire | `domain/wire/contracts.py` | Already owns CorrectionRecord |
| Decisions | `docs/main_v4/09_…` | ADRs for D-02/D-03 reversals |
| This plan | `docs/reviews/todo/vanguard_LAM_manifests_plan_sprint-7-to-9.md` | Non-normative |

---

## 13. Anti-patterns (seen in this repo’s language already)

1. **README as verb registry.** `repo.tree` is not in `SinkRegistry`. Adding it only to README creates two ontologies.
2. **FIT.md “verified” from LAM wall-clock.** Mechanics ≠ model skill.
3. **Translator as competitor compatibility layer in Python.** That is a hidden third harness.
4. **Using LAM A/A to close Q3.** Degenerate, CL-3 violation.
5. **Promoting corrections because tests passed.** `MEM-1`.
6. **Forking EpisodeEngine for parallel tools** to win a reconstruction demo. Falsifies T7.6.
7. **Calling TableWorld “CSV in git.”** Fails generality.
8. **Marking MVP contract rows covered from gym evidence.**
9. **Copying Claude system prompts into git** beyond public docs — legal + contamination.
10. **`top` models invented by implementers.** D-13.

---

## 14. Suggested Decision Record entries (leads should file, not bury in this review)

If you adopt §4, append to `VG-09` (or the living Decision Record T11.1) roughly:

| ID | One sentence | Reversal |
|---|---|---|
| ADR-S7-01 | Reconstructions are packs; core trees are CI-forbidden on those PRs | A reconstruction inexpressible without a documented core ADR |
| ADR-S7-02 | Depth-1 / single tool call remains until independence groups exist | T4.7 property tests green |
| ADR-S7-03 | No live PTY; streamed `proc.exec` only | `proc.session` ADR with grant-per-chunk |
| ADR-S7-04 | Dual cassette (LAM OpenAI vs ModelPort) | Proven unified vectors |
| ADR-S7-05 | `lab.harness` before `vg harness` if daemon path is NO-GO | Beta P0-01 closed |
| ADR-S7-06 | `models.json` top empty until PL names ids | Named ids in Decision Record |

Do not edit GTS-13C checkboxes as if they were git-tracked completion of the product.

---

## 15. What “S10 Done” Looks Like (Operational Definition of Done)

Not a feature-bloated Claude Code competitor. All of the following verified:

1. **Reconstruction Pure-Data Manifests:** Three reconstruction packs (`vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`) compose without kernel/episode/wire diffs.
2. **Honest Measurement Laboratory:** `lab harness diff/bench` runs paired **cassette or live-labelled** tasks; LAM replay is a separate column.
3. **Undeletable Control Arm:** `vg-shell-only` remains undeletable; paired comparisons run; degenerate A/A **refuses** rather than prints stars.
4. **CorrectionRecord Integrity:** CorrectionRecord cannot enter as unparsed JSON; style/architecture cannot be general scope.
5. **Generality Witness:** TableWorld landed with zero core changes behind standard `EnvironmentAdapter` and `EvaluatorPort`.
6. **LAM Inner-Loop Gym:** LAM records gold traces into SQLite/JSONL store; CI replays gold in milliseconds; live populate is budgeted and labelled.
7. **No Auto-Promotion or PTY Escapes:** No public SWE number overclaiming; zero competence auto-promotion inside the run loop; zero live PTY handles.
8. **Phase 3 Release Candidate:** All Chapter 10 questions (Q1 composition, Q2 dogfood, Q3 measurement, Q4 generality) sealed with cryptographic evidence.

That is the instrument. The competitor-shaped CLIs are **configurations of the instrument**. LAM is how those configurations get **cheap, honest, repeatable** inner-loop evidence while paid models stay on the other side of a ledger.

---

## 16. Reading order for a senior who joins tomorrow

1. `VG-02` mission + non-claims (15 min).
2. GTS-13C T6, T7, T8, T9, T10 and Ch.6–10 (30 min).
3. `runtime/root.py` module docstring + `DEFAULT_BINDINGS` (20 min).
4. `agency/episode/engine.py` + `adapters/models/invocation.py` (20 min).
5. `VG-07` CL-1..3 and `VG-10` DEF-02, DEF-03, DEF-04, DEF-08 (15 min).
6. This file §4 and §11 (20 min).
7. Then only the packet they own.

If they start by cloning Claude Code into `agency/`, they have not read the architecture.
