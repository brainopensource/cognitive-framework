# VANGUARD / AETHER v0.6 — INDEPENDENT AI AGENTIC SYSTEMS SPECIALIST CONCEPT LOCK REVIEW

**Role:** PhD-level AI Agentic Systems Architect / Principal AI Research Engineer / Agent Framework Specialist
**Engagement:** ANALYSIS-ONLY. No code, spec, ADR, annex, roadmap, milestone, backlog, sprint, or existing review was modified. No commit was made. This file is the sole artifact produced.
**Tree reviewed:** `main` @ `60c0cba`, working tree as found.
**Date:** 2026-08-20.
**Deliverable path note:** the directive names `00_AI-Specialist_lead_concept_lock_plan_suggestion.md`; this report was written to that exact path, beside the `00_tech_lead_*` and `00_arch_lead_*` pairs.

---

## 1. Executive Summary

I am the fourth reviewer. The three before me — Principal Staff Engineer, Independent Tech Lead, Principal Architect — converge on an architecture: one recursive Python substrate, `Agent = Principal + HarnessInstance`, spawn with capability/budget attenuation, event-sourced ledger as the sole authority, wire-first plugins over five SPIs, exterior signed evaluator, sequential execution with concurrent semantics, graph as projection, Meta-Harness deferred. I read all of their documents in full, then inspected the actual system, because my mandate is not to referee their agreement but to answer a different question: **is this substrate actually capable of becoming a general substrate for compositional, recursive, tool-using, multi-agent AI — starting from a basic coding/file-editing agent — without a new engine per capability?**

My answer: **the architecture is right, and the AI-specific evidence base is not yet in place to lock it.** The compositional thesis is sound and I endorse it on AI-systems grounds, not as deference to the Staff lane. But a concept lock for an *agentic* substrate must lock the things that make agents learnable, attributable, and composable — and on this tree those things are precisely the ones that are missing, mocked, or content-free. Six findings, each verified on this tree in this session:

1. **The system's learning substrate — the trajectory — is content-free.** `[FACT]` `layer0/scheduler/driver.py:221` computes the trajectory digest over `{schema, run_id, episode_id, principal, n}` where `n = len(envelopes)`. It records nothing about what the agent did, what context it saw, what model produced the proposal, or what the verdict was. SPEC §7 specifies a full `mhf.trajectory/1` record (harness_digest, model_routes_used, per-turn context_digest/proposal/receipts/cost, signed verdict, attribution) and Invariant I-9 makes it binding — **no `trajectory.schema.json` exists in either schema directory** (verified: `find schemas -name "*trajectory*"` returns nothing). For an AI-systems review this is the single most consequential gap: trajectories are the substrate's only bridge between *execution* and *learning*, and they cannot be retrofitted after episodes have run without them.
2. **The recursive-agency mechanism the whole thesis rests on exists in the tree CI does not run, and is mocked in the tree CI does run.** `[FACT]` `vanguard/packages/agency/episode/engine.py:531` implements a real `spawn()`: fail-closed child-scope parsing (`:98–149`), depth ceiling (`:574–581`), `attenuate()` call with whole-denial (`:584–591`), tool filtering to granted actions (`:596–598`), causation-tagged child events (`:600–602`, `_CausationEventAdapter`), and untrusted re-entry of child returns (`:639–641`, K-33). `[FACT]` `layer0/scheduler/driver.py:170–192` emits `CHILD_SPAWNED` then immediately `CHILD_RETURNED {"spans": []}` — no child principal, no attenuation, no work. The CI-adjacent test asserts exactly this pair of emissions. The reference implementation of the v0.6 thesis is already written and untested by the gate that matters.
3. **The capability ceiling — the mechanism that makes tool composition safe — is discarded at compile time and fails open four times.** `[FACT]` `packs/code-default/harness.yaml` declares `fs.read`, `fs.search`, `patch.apply`, `proc.exec`. `[FACT]` `layer0/compose/compiler.py::_parse` (lines 90–118) never reads `capabilities`, `system_prompt`, or `approval_policy`; `[FACT]` `compiler.py:57–58` calls `intersect_ceilings(...)` and discards the return value; `[FACT]` `layer0/spi/ceiling.py:21` is `if not capabilities: return True`; `[FACT]` `layer0/registry/grants.py:24` is `if key not in allowed and allowed:` — an empty ceiling permits every plugin capability. I verified the shipped pack compiles to `capability_ceiling == ()` by reading the parse path end to end. For the AI thesis this is not merely a security bug: **capability ceilings are how the substrate says "this composition of tools is what this agent is," and a composition whose declared identity is silently dropped cannot be measured, attributed, or trusted as an experimental unit.**
4. **The exterior-judge thesis — the project's one-sentence identity and its only credible defense against reward hacking — is inverted inside the CI-gated tree.** `[FACT]` `layer0/scheduler/driver.py:138–139` emits `VERDICT_RECORDED payload={"verdict": "pass"}` unconditionally, after calling `self._gate.request(...)` and discarding the answer; it also emits `INVALIDATION_CHECKED {"ok": True}` and a `CLAIM_RECORDED` derived from `len(receipts)`. Every measurement produced through this path since W1 is self-certified. For self-improvement research this is fatal in a specific way: **a learning loop fed by self-signed verdicts learns to satisfy the signer, not the task** — the reward-hacking failure mode the architecture exists to prevent.
5. **Agent identity and causality — the fields that make multi-agent execution attributable — are absent from both trees.** `[FACT]` Grep across both trees: `principal_id` 0/0, `parent_principal_id` 0/0, `project_id` 0/0, `harness_digest` 0/0 (layer0/packages). `Principal` is a bare `str` everywhere. `[FACT]` `layer0/events/emitter.py:38–50` — `LedgerEmitter.emit()`, the function the kernel uses for every event — forwards only `run_id`, `principal`, `payload`, `alertable`, dropping `episode_id`, `causation_id`, `correlation_id`, `idempotency_key`. No call site anywhere populates `causation_id`/`correlation_id` with a non-`None` value. **Every kernel-emitted event in layer0 is un-attributable to an episode.** The packages tree tags `causationId` into child payloads via the adapter, but has no envelope-level field.
6. **The model boundary — the thing that makes heterogeneous multi-model teams possible — is real in packages and absent in layer0.** `[FACT]` `vanguard/packages/adapters/models/` carries 2,349 LOC of real adapters (OpenRouter SSE 896 LOC, Ollama, LAM, cassette, routing with pricing resolution, tier escalation policy). `[FACT]` layer0 has no model port at all: the driver calls `self._planner.plan(view, remaining)` where the planner is an SPI behind which a model may or may not live. The five-SPI set has no `IModelProvider` — SPEC §2.2 lists it as a first-party port, and `layer0/spi/interfaces.py` implements exactly five SPIs without it. Model identity therefore cannot participate in execution attribution in the new tree, which breaks the `D_R` (execution identity) third of the identity trinity all three lanes endorse.

**Independent AI-systems recommendation.** Lock the compositional architecture — it is correct and I would not reopen any of it. But make the lock *AI-load-bearing* by locking the four things an agentic substrate cannot retrofit: **(a) the trajectory record schema and its emission point; (b) envelope lineage fields populated by construction, not by convention; (c) the capability ceiling surviving compilation with fail-closed defaults; (d) model identity as a first-class attribution dimension.** Everything else — swarms, skills, Meta-Harness, memory strategies, context strategies — should be explicitly *refused* in the lock, because they are compositions and the substrate's job is to make them expressible, not to pre-design them.

The MVP filter is satisfied: none of the four requires building future machinery. The trajectory schema is one JSON Schema plus one emitter change. Lineage is envelope fields plus fixing one function. The ceiling fix is making the compiler read a key it already receives. Model identity is a field on the execution digest. **Semantics for the future, implementation for the present** — exactly the asymmetry the directive demands.

---

## 2. AI Specialist Mandate & Independence Statement

My mandate is the fourth lane: test whether the v0.6 foundation can become a general substrate for compositional, recursive, tool-using, multi-agent AI. The other three lanes asked engineering questions (which tree is canonical, how to converge, what CI should gate). I ask agent-science questions: can agents be composed from primitives, can their behavior be attributed and replayed, can trajectories become learning data, can recursive spawning be governed, can multi-agent economics be measured, can self-improvement be governed without reward hacking.

I read the full corpus: `principal_engineer_proposal.md` (4,460 lines), `vanguard-arquitetura-v4-parecer-e-plano.md`, `Vanguard-substrate-060-full-refactor-v3-1.md`, `vanguard-substrate-060-execution-plan.md`, `001_V060_concept_phase_BETA.md`, the Tech Lead review (1,680 lines), and the Principal Architect review (860 lines). I used them as evidence and intellectual input. I did not adopt their conclusions by default and did not manufacture disagreement. Where I differ, I differ because of what an AI-agentic substrate requires, verified against the code.

Three independence notes:

- `[FACT]` The three prior lanes agree on the architecture and disagree mainly on sequencing and scope. A fourth lane that merely ratified the consensus would add nothing; a fourth lane that disagreed for sport would add less. My value is in testing the consensus *against AI-systems requirements the engineering lanes underweighted*: trajectory data, attribution, model identity, learning governance.
- `[FACT]` The Staff lane's own north-star document (`principal_engineer_proposal.md`) contains the richest AI-systems material in the corpus (§5–§41: recursive machine, swarm-as-policy, stigmergy, memory-as-plugin, skills-as-artifacts, Meta-Harness-as-process, self-improvement levels, sparse agency, budget-as-vector, H1–H7 hypotheses). My review is in part an *adjudication of that material against the as-built tree* — much of it is right and none of it is implemented.
- `[FACT]` A fifth lane (`00_SYTEMS-ENG_*`) appears to be running concurrently on this tree. Cross-lane working-tree activity was already flagged by the Tech Lead (§3 of their report). I did not touch any file outside my deliverable.

---

## 3. Current Product Reality

The system must evolve from a **basic working agent capable of relatively simple coding/file-editing behavior**. That is the correct near-term target and I endorse it without reservation. The AI-systems risk is not that the MVP is too small — it is that the MVP's *data exhaust* is too thin to support the later evolution.

`[FACT]` What exists today, per tree:

| Capability | `vanguard/packages/` (22.6k LOC) | `layer0/` (4.5k LOC) |
|---|---|---|
| Real model calls | Yes — OpenRouter SSE, Ollama, LAM, cassettes, routing, tier escalation | No model port |
| Real episode loop | Yes — `agency/episode/engine.py` (693 LOC), multi-turn, spawn | Sequential driver, single toolkit, fabricated verdict |
| Real evaluator | Yes — UID-10002 daemon, Ed25519, SO_PEERCRED | `IEvaluationGate` protocol; verdict fabricated |
| Real ledger | SQLite WAL, BEGIN IMMEDIATE, monotonic seq | `MemoryLedger` (in-memory list) |
| Real sandbox | bwrap `--unshare-all --unshare-user` | rlimits only |
| Real harness compiler | `runtime/root.py` (1,418 LOC monolith) | `compose/compiler.py` (129 LOC, drops capabilities) |
| Real plugin wire | None (in-process) | `registry/broker.py` (UDS, JSON-RPC, rlimits, FSM) — untested |
| Real spawn | Yes (`engine.py:531`) | Mock (two emissions) |
| Real skills | `skill_index.py` (frozen prefix cards) + `vg-code-default/skills/` | None |
| Real context compiler | L1–L5 prefix-stable, compaction strategies | None |
| Real telemetry | `RunTelemetry` (integer-only, absence-preserving) | Content-free trajectory digest |

`[INFERENCE]` The product reality is: **packages is a working single-agent coding runtime with real model calls and real evaluation; layer0 is a clean interface layer with a fabricated execution story.** The v0.6 thesis — recursive compositional agency — is implemented *nowhere* end-to-end, but its hardest single piece (attenuated recursive spawn) exists in packages, and its interface layer (SPIs, broker, envelope) exists in layer0. The convergence plan all lanes endorse is therefore not a rebuild; it is an assembly of already-written parts around a missing middle: **the multi-harness orchestrator and the attribution/trajectory layer.**

The MVP filter applied to my recommendations:

| Recommendation | Must exist semantically now? | Must be implemented now? | Delays a useful coding agent? | Forces migration if deferred? |
|---|---|---|---|---|
| Trajectory schema + emission | Yes | Yes (schema + emitter) | No — one schema, one emitter change | **Yes — unharvestable episodes are unrecoverable** |
| Envelope lineage fields | Yes | Yes (fields + emitter fix) | No | **Yes — ledger history rewrite** |
| Capability ceiling survives compile | Yes | Yes (read the key) | No | No, but every composition is unmeasurable meanwhile |
| Model identity in attribution | Yes | Field only | No | Yes — D_R becomes meaningless retroactively |
| Swarm/skills/Meta-Harness semantics | No | No | — | No |

---

## 4. AI-Agentic Architecture Evaluation Method

I evaluated the substrate against what contemporary agentic systems research and practice actually require, using six tests:

1. **Composition test** — can a new agent type be expressed as a new manifest + plugins, with zero kernel diff?
2. **Recursion test** — does a child agent use exactly the same execution semantics as a root agent?
3. **Attribution test** — given a result, can I reconstruct which composition, which model, which context, which tools, which budget produced it?
4. **Trajectory test** — does execution naturally produce data sufficient for failure analysis, agent comparison, and (later) preference-pair generation?
5. **Governance test** — can capability, budget, and evaluation authority be attenuated down a spawn tree without new mechanisms per level?
6. **Economics test** — can 1-agent vs N-agent comparisons be run under controlled total budget, with cost attribution per agent?

For each SOTA pattern (ReAct, Reflexion, Voyager, AutoGen, MetaGPT, debate, actor systems, tool-calling agents, computer-use agents, memory architectures, skill libraries, LLM routers, MoE analogies, meta-learning, evolutionary search, DPO/SFT/LoRA, empirical self-improvement) I asked: what principle is useful; should it become a primitive; can it remain a plugin/policy; does Vanguard already generalize it; would adopting it create unnecessary complexity?

Evidence labels: `[FACT]` = command output or file content on this tree; `[INFERENCE]` = reasoned from facts; `[AI SYSTEMS RECOMMENDATION]` = this lane's proposed lock decision; `[RESEARCH HYPOTHESIS]` = scientifically interesting, unproven; `[UNKNOWN]` = needs an experiment.

---

## 5. As-Built Agentic Capabilities

`[FACT]` The agentic loop as built (packages tree, the one that actually runs against models):

```text
observe (EpisodeView: episodeId, runId, brief, turn, stateDigest, lastReceiptDigest, lastProgressSignal)
→ propose (model.propose(view, tools, sampling) → typed result; ProposalMalformed is a typed failure)
→ emit ProposalProduced (descriptor only, never args — secrets rule)
→ terminal-proposal reduction (finish/abstain reduce straight to terminal)
→ spawn-proposal reduction (attenuated child episode, S8-B-01)
→ authorize + effect + receipt through Kernel.dispatch (the one path)
→ no-progress detection (same transition without state/progress change, N turns → ABANDONED)
→ terminal (COMPLETED / ABANDONED / BUDGET_EXHAUSTED / CANCELLED / ESCALATED / INSTRUMENT_ERROR / RUNTIME_ERROR)
```

`[FACT]` The turn view is thin: `EpisodeView` carries identifiers and digests, not content. Content assembly (context compilation) happens above the engine in `agency/context/compiler.py` (L1–L5, prefix-stable, brief exempt from compaction, competence prior recorded before turn 1).

`[FACT]` Tools are declared to the model as a list of mappings (`self._tools`), filtered at spawn to granted actions. The kernel resolves verbs to adapters at S2; toolkits never see grants.

`[FACT]` Budget is a 4-dimension `Reservation` in packages (`usd_micros, millis, tokens, bytes_`) and 6-dimension in layer0/SPEC (`+ turns, depth` — ADR-M0-07). The governor debits reality including overruns (K-07) and supports parent leases.

`[FACT]` Evaluation is exterior in packages: the episode terminates; it does not grade itself. `tier_escalation.py` escalates model tiers on stop-reason alone — never on a model's or evaluator's opinion of its own output.

`[INFERENCE]` As-built, this is a competent single-agent ReAct-class loop with unusually strong authority mediation and unusually weak data exhaust. The loop's *decision* semantics are ahead of most frameworks; its *learning* semantics are behind them (no trajectory record, no per-turn context digest, no model attribution).

---

## 6. Agentic Foundation Assessment

**The central thesis** — intelligence emerges from composition over a small recursive substrate, not from a new engine per capability — I evaluate as **correct and endorsed**, with three AI-systems qualifications the lock must carry:

**Qualification 1 — composition needs identity to be measurable.** The thesis's scientific content (Staff proposal §31: measure Δ_C = E[Y|do(C=C₁)] − E[Y|do(C=C₀)]) requires that a composition be an addressable experimental unit. `[FACT]` Today `FrozenHarness.digest` is computed over `{api, id, resolved plugin refs, undeletable, plugin_digests}` — it excludes the capability ceiling (dropped), the system prompt (dropped), the approval policy (dropped), and the model routes (resolved to `provider:model` strings only). `[INFERENCE]` Two harnesses differing only in system prompt or ceiling compile to the *same* D_H. The A/B machinery the whole program depends on is currently blind to three of the most consequential knobs in agent design. **Prompt identity is harness identity** — this is perhaps the most important AI-specific correction in this report.

**Qualification 2 — recursion needs lineage to be governable.** `spawn()` in packages is genuinely good, but it threads `parent_lease` and tags `causationId` into payloads; there is no `parent_principal_id`, no `harness_digest` on child events, no `project_id`. `[INFERENCE]` A swarm of 20 agents today would produce a ledger in which child effects are attributable to a principal string shared with the parent. Budget lineage exists (leases); authority lineage exists (grants); *agent* lineage does not.

**Qualification 3 — emergence needs evidence to be science.** The Staff proposal's H5 (compositional intelligence: ΔY|_{M=fixed} > 0) is the research heart of the project. It is untestable without trajectories that record what composition actually did. `[FACT]` The trajectory digest today identifies nothing (`driver.py:221`). `[FACT]` `RunTelemetry` in packages is excellent (integer-only, absence-preserving) but is run-level, not turn-level, and carries no harness/model/context identity.

**Assessment of the six preservation targets** (small stable substrate / replaceable capabilities / recursive composition / event-derived state / external evidence / resource governance):

| Target | As-built status | Verdict |
|---|---|---|
| Small stable substrate | packages kernel 1,658 LOC with K-rules; layer0 4,556 LOC over A-1's 4,500 budget | **Preserved in packages; violated by layer0's size** |
| Replaceable capabilities | 5 SPIs exist as protocols; wire exists untested; in-process adapters in packages | **Interface preserved; substitution unproven** |
| Recursive composition | Real spawn in packages; mock in layer0 | **Preserved in the ungated tree only** |
| Event-derived state | WAL ledger + pure reducers in packages; MemoryLedger + tautological parity test in layer0 | **Preserved in packages; regressed in layer0** |
| External evidence | UID-10002 Ed25519 daemon in packages; fabricated verdict in layer0 | **Preserved in packages; inverted in layer0** |
| Resource governance | 6-dim governor, K-07 overrun debits, parent leases | **Preserved and genuinely strong** |

`[AI SYSTEMS RECOMMENDATION]` The foundation is sound *as an architecture* and unsound *as an evidence base*. The lock should ratify the architecture and bind it to the four AI-load-bearing obligations (trajectory, lineage, ceiling, model identity) with named falsifiers.

---

## 7. Minimal Primitive Vocabulary

My recommended vocabulary, adjudicated against the directive's candidate list:

**Lock as primitives (substrate):**

| Primitive | Disposition | AI-systems rationale |
|---|---|---|
| `Principal` | **LOCK — typed value** (`id, parent_id?, depth`) | The anchor of every attenuation invariant and every attribution query. A bare `str` cannot express "child of." |
| `HarnessRef` / `FrozenHarness` | **LOCK — with corrected D_H** | The experimental unit. Must digest manifest + plugin digests + **system prompt + capability ceiling + approval policy + model routes**. |
| `HarnessInstance` | **LOCK** | Runtime state of a frozen harness; makes `Agent` non-circular. |
| `Episode` | **LOCK** | The bounded execution unit; already well-established. |
| `Event` / `EventEnvelope` | **LOCK — with lineage fields** | The only irreversible schema. See §16. |
| `EffectRequest` | **LOCK as-is** | One frozen type, one schema (I-1). |
| `Receipt` | **LOCK — add `lease_id`, `grant_digest`** | Ties an effect to the authority that permitted it; without it, cost attribution per agent is impossible. |
| `ArtifactRef` / `BlobRef` | **LOCK** | Content-addressed bytes; events carry refs, never payloads. |
| `Capability` / `Grant` | **LOCK — and put under CI** | The best-designed code in the repo (descriptor-bound, refused at issuance, cascading revoke) with zero CI coverage. |
| `Reservation` / `Lease` | **LOCK** | Six integer dimensions; budget lineage across spawn hangs off `parent_lease_id`. |
| `VerdictRef` / `SignedVerdict` | **LOCK — reducer-enforced** | An unsigned verdict is not a verdict. |

**Explicitly NOT primitives (compositions, projections, plugins, artifacts, policies):**

| Concept | Disposition | Why |
|---|---|---|
| `Agent` | **Composition** (`Principal + HarnessInstance`) | Costs nothing to lock as a definition; must never become a privileged runtime class. |
| `Task` | **Data** (episode brief / project metadata) | No implementation; overlaps Episode. |
| `Skill` | **Artifact** (content-addressed, versioned) | Two `skill_index.py` modules exist, neither CI-exercised. Skills are data consumed by plugins, not substrate. |
| `Memory` | **Plugin** (`IMemoryEngine`) | Never authoritative state. |
| `Swarm` | **Configuration** (N agents + coordination policy) | Policy, not engine. |
| `Project` | **Scope** — **CONDITIONAL** | Undefined anywhere in normative docs or code; `project_id` appears zero times in both trees. Lock only with a one-sentence normative definition (consistency unit: one ledger stream, one ceiling, one root budget), else use `root_episode_id`. |
| `Meta-Harness` | **Process** (H0 → execute → observe → mutate → experiment → promote) | Not a runtime object. Deferred to P3. |
| `Workflow` / `Graph` | **Projection** | Derived from events; never an execution language (ADR-0003 stands). |
| `Orchestrator` | **Policy host** | The scheduler is the mechanism; orchestration strategies are plugins above it. |
| `Experiment` / `Promotion` | **P3** | Gated on the statistical-power suite that does not exist. |

`[AI SYSTEMS RECOMMENDATION]` This is ~12 locked primitives and ~10 explicit refusals. The refusals matter as much as the locks: each refused concept is a place where the substrate could have grown an engine and must instead grow a composition.

---

## 8. Atoms → Skills → Harnesses → Agents Model

The directive's hierarchy:

```text
PRIMITIVE/ATOM → ACTION COMPOSITION → REUSABLE CAPABILITY → HARNESS/AGENT CONFIG → MULTI-AGENT COMPOSITION
```

**Atoms.** `[FACT]` The substrate's atoms are verbs + selectors + sinks: `fs.read`, `fs.search`, `patch.apply`, `proc.exec` over `ResourceSelector`s, mediated by `Kernel.dispatch` with `EffectRequest`/`Receipt`. LLM inference is *not* currently an atom in layer0 (no model port); in packages it is a provider call above the kernel. `[AI SYSTEMS RECOMMENDATION]` Model inference should be expressible as an effect (`model.infer` verb, `model://` selector, OBSERVATION sink) so that token spend enters the same budget/receipt/attribution path as every other action. This is the single cleanest way to make heterogeneous model teams attributable without a new mechanism. It does not require moving providers behind the kernel now — it requires the *semantic slot* to exist.

**Action compositions.** The directive's examples (`list → read → LLM → write` for editing; `inspect → reproduce → diagnose → patch → test → evaluate` for bug-fixing) are *planner policies*, not substrate structures. `[FACT]` The existing `drive-until-green` planner and `tier_escalation.py` policy are exactly this class of thing: strategies around the loop, not engines inside it. `[INFERENCE]` The right architectural unit for reusable compositions is **the manifest fragment + plugin**: a "bug-fixing behavior" is a planner plugin with a config, composed into a harness. No new primitive is needed, and none should be invented.

**Reusable capabilities (skills).** `[FACT]` The repo already has the correct embryonic form: `SkillCard` (`skill_id, name, description, body_path`) rendered into a frozen prefix block, bodies read via `fs.read`, cards omitted whole rather than truncated. `[AI SYSTEMS RECOMMENDATION]` Skills should be **content-addressed artifacts with capability declarations** — a skill that says "I require `proc.exec` on `/workspace`" composes with the ceiling check at compile time. The Staff proposal's SkillManifest (id, version, input/output schema, capabilities required, implementation digest, provenance, validation evidence, applicability metadata) is the right target shape; it is a schema, not a runtime. Versioned, content-addressed, measurable, replaceable — all four properties are artifact properties, not kernel properties.

**Harnesses.** See §15. The `Definition → Resolve → Verify → Freeze → FrozenHarness → HarnessInstance` pipeline is correct and half-built (`compose()` exists; the freeze is incomplete because three manifest fields are dropped).

**Multi-agent composition.** See §10–§11. Expressible via spawn + heterogeneous harness refs; blocked on lineage fields, not on new mechanisms.

**The compositional ladder, as the substrate should express it:**

```text
verb + selector + sink                    (atom — kernel)
→ EffectRequest → Receipt                 (action — kernel)
→ planner policy / manifest fragment      (composition — plugin)
→ skill artifact                          (reusable capability — CAS + plugin)
→ FrozenHarness                           (agent configuration — compose)
→ Principal + HarnessInstance             (agent — scheduler)
→ spawn(parent, harness, caps, budget)    (multi-agent — same machine)
→ agents + coordination policy            (swarm — plugin policy)
```

`[AI SYSTEMS RECOMMENDATION]` Every rung above the kernel is data or plugin. The lock's job is to keep it that way: the falsification test is that adding any new rung requires zero kernel diff.

---

## 9. Agent as Composition / Emergent Property

**The stronger hypothesis:** Agent should not be a privileged runtime object; agency emerges when identity, a harness, state, resources, model access, tools, and policies are composed.

`[FACT]` As-built, `Agent` is already not a class in either tree — it is a `principal: str` plus an engine invocation. The packages `EpisodeEngine` is constructed per episode with `(kernel, model, clock, events, scope, tools, sampling, max_turns, sink_class, parent_lease, attenuated)` — an agent is literally the composition of those arguments. `[INFERENCE]` The codebase has already voted for the emergent view; the lock should ratify it.

**Trade-offs I weighed:**

- *Projection view (recommended):* `Agent = Principal + HarnessInstance` is a *definition*, useful for reasoning and attribution, with no runtime class. Pros: no agent-class proliferation (`CodingAgent`, `ResearchAgent`, `TutorAgent` cannot become engines); heterogeneous children are free (spawn takes any harness ref); logical agents are cheap (a principal row + refs). Cons: no single place to hang agent-level invariants — they must live in the kernel (attenuation) and the ledger (lineage), which is exactly where they already live.
- *Primitive view (rejected):* an `Agent` runtime object with lifecycle methods. Pros: convenient API. Cons: it recreates the engine-per-capability problem one level up (`SwarmAgent`, `MetaAgent`, `CriticAgent` subclasses), and it makes "100 logical agents" mean "100 resident objects" — the exact scaling failure §12 exists to avoid.

`[AI SYSTEMS RECOMMENDATION]` Lock the sentence `Agent = Principal + HarnessInstance` as a *definition with no runtime class*, and lock the corollary: **any behavior that would require an agent subclass is a harness composition instead.** The falsifier: if a critic, reviewer, tutor, or researcher agent ever requires a new class rather than a new manifest, the abstraction has failed.

---

## 10. Recursive Agency Assessment

**`Agent = Principal + HarnessInstance`; `SubAgent = ChildPrincipal + HarnessInstance`** — **AGREE WITH MODIFICATION.**

`[AI SYSTEMS RECOMMENDATION]` Drop `ChildPrincipal` as a distinct type (concurring with the Tech Lead): a child is a `Principal` with `parent_id` set. Two principal types mean two paths through `attenuation.covers()`, and K-26 is only as strong as the number of paths that reach it. One type, one lineage rule.

**Is this sufficient to model root/subagent/specialist/critic/reviewer/researcher/architect/coder/tester/teacher/student-model/meta-agent/swarm-participant without separate classes?** **Yes, with one gap.** `[FACT]` The packages spawn already models: specialist (attenuated scope + filtered tools), critic (a child harness with an evaluation-heavy manifest — expressible), recursive depth ceiling. `[FACT]` What it cannot model today: a child on a *different harness* — `spawn()` in packages reuses `self._model` and filters `self._tools`; the harness is the engine's construction, not a parameter. `[AI SYSTEMS RECOMMENDATION]` The spawn signature the lock should ratify is the Staff lane's: `spawn(parent_principal, harness_digest, requested_scope, requested_reservation) -> Principal | Denial`. Heterogeneous children (researcher spawns coder spawns tester) require the harness to be a *parameter*, which the packages implementation does not yet do and the layer0 mock does not do at all. This is a signature decision, cheap now, expensive later.

**The spawn invariants:**

- `Capabilities(child) ⊆ Capabilities(parent)` — **AGREE, unconditionally.** `[FACT]` `kernel/attenuation.py::attenuate()` implements subset-or-deny-whole (K-26) with per-dimension denial reasons. `[FACT]` Known hole, present in both trees: `_exceeds` returns `False` when either bound is `None`, so an unbounded child passes under a bounded parent. Fix in the lock's proof obligations, not by relock.
- `Budget(child) ≼ RemainingBudget(parent)` — **AGREE, component-wise on all six dimensions.** `[FACT]` The governor supports parent leases (`parent_lease_id`, parent-closure enforcement). Wiring, not new mechanism.

**What identity, causality, ownership, and resource semantics must exist in v0.6 before recursive spawning is enabled:**

| Semantic | Must exist? | Status |
|---|---|---|
| `principal_id` typed with `parent_id`, `depth` | **Yes** | Absent (bare `str`) |
| `parent_principal_id` on every child event | **Yes** | Absent |
| `harness_digest` on every event | **Yes** | Absent |
| `causation_id` populated by construction | **Yes** | Declared, never populated; payload-tagged adapter in packages only |
| `correlation_id` for operation lineage | **Yes** | Declared, never populated |
| Budget lineage (`lease_id` on Receipt) | **Yes** | `parent_lease_id` exists in governor; not surfaced on receipts |
| Capability lineage (`grant_digest` on Receipt) | **Yes** | `parent_grant_id` exists in grants; not surfaced on receipts |
| Denial as a typed value + event | **Yes** | `[FACT]` `layer0/scheduler/driver.py:179` returns `None` on depth exhaustion after emitting `BUDGET_EXHAUSTED` — caller cannot distinguish spawned from denied |
| Depth as a reservation dimension | **Yes** | Exists (ADR-M0-07) |

`[AI SYSTEMS RECOMMENDATION]` Lock spawn semantics **against the packages implementation as reference** (`agency/episode/engine.py:531`), delete the layer0 mock, and require the harness parameter. The falsifier: `test_child_grant_wider_than_parent_is_denied_whole` and `test_spawn_denial_is_a_typed_value_not_a_silent_return`.

---

## 11. Multi-Agent / Swarm Assessment

**`Swarm = Agents + CoordinationPolicy`, not `Swarm = SwarmEngine`** — **AGREE.**

The directive's coordination patterns, adjudicated:

| Pattern | Expressible as? | Mechanism needed |
|---|---|---|
| Hierarchical delegation | spawn tree | None — spawn + attenuation |
| Parallel hypotheses | N spawns, same budget partition | Independence groups (already declared on `Proposal`) |
| Debate | policy plugin orchestrating turns between principals | None — events + artifacts |
| Critic/reviser | child harness with critic manifest | Heterogeneous spawn (§10 gap) |
| Review committees | N critic children + aggregation policy | None |
| Competitive search | N spawns + exterior evaluator selection | Evaluator already exterior |
| Ensemble voting | aggregation policy over child returns | None |
| Specialist routing | model-route policy (exists embryonically as tier escalation) | None |
| Manager/worker | spawn tree with manager policy | None |
| Stigmergic artifact coordination | artifact → ledger/CAS → dependency satisfiable → scheduler proceeds | **Dependency semantics on events** — the one substrate need |

`[INFERENCE]` The stigmergy pattern is the only one that touches the substrate: it requires that an artifact's production can make a dependency satisfiable, i.e., `produced`/`consumed` relations must be derivable from events. They are — *provided* lineage fields are populated (§16). The Staff proposal's formulation ("stigmergy is a possible scientific interpretation of the dynamics, not a primitive called StigmergyEngine") is exactly right.

**What the substrate needs regardless of swarm policy:** identity + causality + budget/capability lineage (§10 table) + per-agent cost attribution (Receipt carrying lease/grant) + the economics measurement capability (§25). None of these are swarm features; they are the same four AI-load-bearing obligations from §1.

**Do not lock:** coordination policies, agent-to-agent messaging protocols, negotiation, quorum rules. `[INFERENCE]` These are the parts of every multi-agent design that get rewritten; none constrains the envelope. ADR-0003 (agent-loop primary, no runtime workflow graph) stands and should be cited in the lock.

---

## 12. Logical Agent vs Worker Model

**`Logical Agent ≠ Heavy Worker`; `K active workers ≪ N logical agents`** — **AGREE as a design constraint; `[UNKNOWN]` as a performance claim** (no workload measurement exists on this tree; concurring with the Tech Lead's U-1).

`[AI SYSTEMS RECOMMENDATION]` What v0.6 must encode *semantically* (all cheap):

1. **Agent identity independent of execution state** — an agent exists as a ledger identity (principal row + harness ref + budget refs) without a resident process. This is the projection view of §9 made operational.
2. **`MAX_CONCURRENCY` as a configured value = 1** — the gate flips later without redesign.
3. **Independence declared, not inferred** — `independence_groups` on `Proposal` (already in `types_gen.py`) + selector-overlap as the concurrency safety predicate (`resource_selector.py` already computes overlap). `[INFERENCE]` The most valuable concurrency preparation in the repo is already written and unused: independence is *computable*; the scheduler simply runs one at a time.
4. **Admission control on the worst simultaneous case** (`Σ R^max_i ⪯ R_available`) — one semantic, expensive to retrofit into a governor.

**Defer entirely (optimization, not semantics):** worker pools, shared model runtime, model broker multiplexing, copy-on-write workspaces, sparse activation machinery, lazy agency, vector clocks, distributed coordination. `[FACT]` The model-sharing economics are real: the Staff proposal's `M_shared ≈ M_model-server + M_core + Σ M_context_i + K·M_worker` is the right target shape, and nothing in the substrate prevents it — model adapters are process-external by construction (OpenRouter/Ollama are daemons), so "100 logical agents" already does not mean "100 model instances." `[INFERENCE]` The expensive resource per agent is *context*, not process — which is why context budgeting (§19) is a first-class reservation dimension and why context digests belong in the trajectory.

`[AI SYSTEMS RECOMMENDATION]` Lock the vocabulary distinction in one sentence each (agent = ledger identity; worker = runtime resource) and defer all machinery. The falsifier for the scaling claim is a measurement (U-1), not an architecture review.

---

## 13. Tool Architecture

**Tools as action capabilities, not intelligence** — **AGREE, and the as-built is closer than the reviews suggest.**

`[FACT]` The kernel's tool model is verb + selector + sink, mediated at S0–S12: toolkits expose `verbs() → Mapping[str, ToolSchema]` and `execute(request, ctx) → Result[Receipt]`; they never see grants. This is precisely the "common effect/capability abstraction preserving domain-specific schemas" the directive asks for: the *envelope* is uniform (`EffectRequest`), the *schema* is per-verb (JSON Schema in `ToolSchema`), and the *authority* is kernel-side.

`[FACT]` Domain-specific tools already exist as pack plugins: `fs.yaml`, `ast-patch.yaml`, `terminal.yaml`, `index.yaml`, `context.yaml`, `memory.yaml`, `planner.yaml`, `evaluation.yaml` in `packs/code-default/plugins/`, with implementations in `packs/code-default/toolkits/` (ast_patch, composite, fs_toolkit, repo_map, terminal_runner).

`[AI SYSTEMS RECOMMENDATION]` Three tool-architecture decisions for the lock:

1. **Tool composition occurs above the kernel** — a composite tool (search → read → patch) is a planner policy or a composite toolkit plugin (`composite.py` already exists embryonically), never a kernel change. The falsifier: if a new tool *category* (browser, database, retrieval) ever requires kernel modification, the verb/selector/sink abstraction has failed.
2. **Model calls should be expressible as effects** (§8) — `model.infer` as a verb with a `model://` selector and OBSERVATION sink, so token spend, model identity, and inference attribution enter the same receipt/budget path. This is what makes heterogeneous model teams (small local + coding-specialist + frontier + deterministic solver + human) *attributable members of a swarm* rather than ambient infrastructure.
3. **The declared isolation tier must match the executed one** — `[FACT]` `terminal.yaml` declares `container` while `terminal_runner.py` runs `subprocess.Popen` in-process with `env={**os.environ}`. For tool architecture this matters beyond security: isolation tier is part of a tool's *execution identity* (D_R); a declared-vs-executed mismatch makes tool-substitution experiments unattributable.

**SOTA adjudication:** tool-calling agents (ReAct-class) are generalized by the proposal/receipt loop; computer-use agents are a toolkit pack; MCP is correctly confined to configuration/adapter (ADR-0066 — it may name tools, never issue grants). None requires a primitive.

---

## 14. Skill / Reusable Behavior Architecture

**What a reusable skill should mean:** `[AI SYSTEMS RECOMMENDATION]` a skill is a **content-addressed artifact consumed by plugins, never a substrate concept.** The forms the directive lists map cleanly:

| Form | Representation |
|---|---|
| Advisory knowledge | skill card artifact (as-built: `SkillCard` + frozen prefix block) |
| Procedural policy | planner plugin config |
| Executable composition | composite toolkit plugin |
| Manifest fragment | harness manifest section |
| Planner pattern | planner plugin |
| Tool macro | composite toolkit |
| Sub-harness | spawn with a harness ref |
| Content-addressed artifact | CAS blob + digest |

**Properties skills must have** (all artifact properties, all lockable as schema requirements): versioned, content-addressed, measurable (a skill's effect on outcomes must be attributable via D_H — which requires the ceiling/prompt/model-route fix in §6), replaceable, provenance-aware (which trajectory produced this skill), capability-declared (a skill requiring `proc.exec` composes with the ceiling at compile time).

`[FACT]` The as-built embryonic form is right: bodies stay on disk, only names/descriptions enter the frozen prefix, cards omitted whole. `[FACT]` SPEC §5.4 already specifies the correct pipeline: harvester mines successful trajectories for recurring effect n-grams with verdict-conditional lift → candidate skill cards → selection pipeline → skills are "distilled, tested procedures, never model free-text pasted into prompts."

`[INFERENCE]` The Voyager lesson is correctly absorbed: skill libraries externalize competence without weight updates. The Vanguard addition — skills enter only through the experimental selection pipeline with exterior verdicts — is stronger than Voyager's and is the right governance shape.

`[AI SYSTEMS RECOMMENDATION]` **Refuse to lock `Skill` as a concept in v0.6** (concurring with the Tech Lead): lock only the *artifact properties* (content-addressed, versioned, capability-declared) and the admission rule (skills enter via the selection pipeline, never free-text). The falsifier: if a skill ever needs kernel awareness to function, the skill abstraction has leaked into the substrate.

---

## 15. Harness Architecture

**Harness as declarative program** — **AGREE; the pipeline is half-built and the freeze is lossy.**

`[FACT]` The intended pipeline: `harness.yaml` (mhf.harness/1) → `compose()` resolves plugin refs against known plugins → verifies ceilings → freezes → `FrozenHarness` (content-addressed digest) → instantiated per episode. `[FACT]` The as-built: `compose()` exists (129 LOC), resolves refs correctly, fails on unknown refs (H-1), but drops `capabilities`, `system_prompt`, `approval_policy` at parse, discards the `intersect_ceilings` result, and digests only `{api, id, resolved refs, undeletable, plugin_digests}`.

`[AI SYSTEMS RECOMMENDATION]` The lock should ratify the pipeline and repair the freeze in the same breath, because **the harness is the substrate's unit of agent design, and a lossy freeze makes every downstream science blind:**

1. **D_H must include the full resolved manifest** — system prompt digest, capability ceiling, approval policy digest, model routes with resolved model identities, plugin configs. Two harnesses that differ in any behavior-affecting field must differ in D_H. `[INFERENCE]` This is the single highest-leverage AI-specific fix in the lock: prompt identity is harness identity.
2. **The capability ceiling must survive compilation** — the ceiling is part of what a harness *is*; dropping it at compile time means the composition's declared action space is fiction.
3. **Freeze at composition stands** (ADR-0005): mid-run composition change is forbidden in v0.6; quiesce/checkpoint is for restart. `[INFERENCE]` For agent science this is also correct: a harness that mutates mid-run is unattributable — you cannot A/B a moving target.
4. **HarnessInstance is the runtime state** — hundreds of agents may share one `FrozenHarnessDigest` without duplicating its definition (Staff proposal §67); each carries only principal, episode state, budget, context refs, memory refs.

**Is this the right substrate for machine-generated agent architectures?** `[AI SYSTEMS RECOMMENDATION]` **Yes, conditionally.** The Meta-Harness's future output is a manifest — data the compiler already consumes. The condition is exactly fix #1: a machine-generated harness must be *addressable* (D_H) and *attributable* (D_R/D_X) or the search over harness space (Staff §76: H' ~ Q(H'|H,D)) has no fitness signal. The falsifier: if a candidate harness cannot be compiled, measured, and compared against a baseline using only existing substrate mechanisms, the harness abstraction is insufficient for meta-programming.

---

## 16. Event-Sourced Agent Execution

**Should agentic activity naturally produce causal events?** **Yes — and the taxonomy is already right.** `[FACT]` SPEC §1.2's 40-kind taxonomy covers the directive's list: task received (`RunStarted`), plan proposed (`ProposalProduced`), tool requested (`EffectStarted` S8a), effect executed (`EffectCompleted`/`EffectFailed`), receipt produced (receipts are dispatch results), artifact produced (CAS + refs), evaluation requested (`EvaluationRequested`), verdict received (`VerdictRecorded` signed), agent spawned/completed (`ChildSpawned`/`ChildReturned`/`EpisodeCompleted`), budget reserved/consumed (`BudgetReserved`/`BudgetCommitted`/`BudgetReleased`/`BudgetExhausted`), capability delegated (`CapabilityGranted`/`CapabilityAttenuated`), candidate generated / experiment started / promotion decided (Phase-2 kinds, correctly absent from v0.6).

**"Everything is an event" ≠ "every byte is an event"** — **AGREE with the corpus's rule:** everything that changes state, authority, causal history, resource accounting, externally visible effects, or evaluation evidence gets durable representation. Tokens, stdout chunks, embeddings, tensors, full contents live in CAS; events carry digests + sizes + types + provenance.

**What belongs where:**

```text
Ledger      authoritative history: identity, authority, causality, budget, effects, verdicts
CAS         content: blobs, artifacts, payloads, skill bodies, model outputs
Projection  derived views: execution graph, read models, indexes
Telemetry   analytical representation — and the DPO harvest schema (I-9)
Memory      cognitive representation — plugin, never authoritative
```

**The two as-built defects that matter for AI systems:**

1. `[FACT]` `LedgerEmitter.emit()` drops `episode_id`, `causation_id`, `correlation_id`, `idempotency_key` — the kernel's entire authority trail is un-attributable to an episode in layer0. The lock's obligation: **lineage fields are populated by construction** — the emitter signature makes them required, not optional kwargs that no call site fills.
2. `[FACT]` `layer0/events/fold.py:99` discards `BudgetCommitted` amounts (`_ = amount`) — committed spend never enters folded state, so budget (one of the four things I-4 names) is not in the replayed state. `[FACT]` The replay-parity test folds one list twice — a tautology. The lock's obligation: **state replay from a cold reader against disk, diffed against live terminal state, covering grants, budgets, approvals, and episode lifecycle** (I-4 as written).

`[AI SYSTEMS RECOMMENDATION]` Lock the envelope field set as the single irreversible decision of the lock (concurring with the Tech Lead's P0-A, which I independently reach from the AI side): `project_id?` (conditional on Project definition), `principal_id`, `parent_principal_id?`, `episode_id`, `parent_episode_id?`, `harness_digest`, `causation_id`, `correlation_id`, `idempotency_key`, `prev_digest`, `seq`, plus the packages governance fields (`tenant_id`, `retention_class`, `trainability`, `redaction_status`, `unknown_fields`). Envelope fields can only be revised later at the cost of the ledger's own history — and the ledger is the only thing in this architecture that is supposed to be true.

---

## 17. Trajectory & Provenance Architecture

**This is my lane's strongest single recommendation, and where I add the most to the prior three lanes.**

The event-sourced architecture *can* naturally produce trajectories — the ledger already contains every proposal, effect, receipt, and verdict. What is missing is the **record schema** that makes a trajectory a *dataset row* rather than a ledger region.

`[FACT]` SPEC §7 specifies `mhf.trajectory/1`: harness_digest, manifest_genome, model_routes_used, per-turn `{context_digest, proposal, receipts, cost}`, verdict (signed, oracle identity, pass), attribution (prefix_hits, escalations) — emitted at every `EpisodeCompleted`, no transformation step. Invariant I-9 makes it binding: telemetry is a dataset; every episode terminates in a trajectory record that is, without transformation, a valid row in the DPO harvest schema.

`[FACT]` No `trajectory.schema.json` exists in either schema directory. `[FACT]` The layer0 trajectory digest is computed over `{schema, run_id, episode_id, principal, n}` — content-free. `[FACT]` The packages tree emits no trajectory record at all; `RunTelemetry` is run-level cost only.

**What trajectories must later support** (directive §14): failure analysis, agent comparison, skill extraction, planner improvement, routing improvement, memory improvement, tool-selection learning, context-policy learning, training-data generation, DPO/SFT pair generation, harness mutation, Meta-Harness experiments.

**What provenance must exist from the beginning because it cannot be reconstructed afterward:**

| Provenance | Why unrecoverable | In trajectory? |
|---|---|---|
| `harness_digest` (D_H) | Which composition ran | Required — SPEC has it |
| Model identity per turn (D_R component) | Which model produced each proposal | **Required — add per-turn model id** |
| `context_digest` per turn | What the agent actually saw | Required — SPEC has it |
| Proposal + receipts per turn | What it did and what happened | Required — SPEC has it |
| Cost per turn | Economics attribution | Required — SPEC has it |
| Signed verdict + oracle identity | Un-gameable learning signal | Required — SPEC has it |
| Turn-prefix divergence point | DPO pair validity (chosen/rejected must share prefix) | **Required — add explicit divergence-point field** |
| `causation_id` chain | Spawn-tree attribution | Via envelope lineage |
| Sampling parameters | Reproducibility of the *stochastic* part | **Required — add sampling params per turn** |

`[INFERENCE]` The DPO pairing rule makes the last two rows load-bearing: SPEC §7 pairs trajectories on identical `(task_digest, harness_digest, turn-prefix context_digest)` with divergent verdicts. A pair is only valid if the prefix genuinely matched — which requires per-turn context digests *and* the divergence point, and (per the Staff proposal §39) `harness_digest_w = harness_digest_l` for the pair. None of this can be mined from a ledger that did not record it.

`[AI SYSTEMS RECOMMENDATION]` **Lock the trajectory record schema and its emission point now; lock nothing about its consumers.** Cost: one JSON Schema + one emitter change. Value: Phase 2 becomes a build rather than a migration; every episode run during convergence becomes harvestable instead of lost. This is the AI-substrate equivalent of the Tech Lead's envelope argument: trajectories cannot be reconstructed retroactively with fidelity, because the *content* of what the agent saw and did at each turn is not derivable from run-level aggregates.

---

## 18. Memory Architecture

**`Ledger = factual history; Memory = selective cognitive representation`** — **AGREE, and the separation is already structural.**

`[FACT]` `IMemoryEngine` is one of the five SPIs: `write/recall/consolidate/invalidate/capabilities()`, with graph as a *negotiated capability* (`capabilities() → {"kv", "vector", "graph"}`), not a sixth SPI. `[FACT]` `LocalFileMemoryAdapter` implements it over SQLite WAL with an `invalidated` flag — memory writes are transactional, and invalidation is a first-class operation.

`[AI SYSTEMS RECOMMENDATION]` All memory strategies — episodic, semantic, vector, graph, procedural, working, long-term, skill memory — remain plugins/projections. The lock should carry three sentences:

1. **Memory never becomes authoritative state** — the negative form the Tech Lead proposes: no projection, index, cache, snapshot, or memory store may be the sole record of any fact. A memory that can disappear and be re-derived is correct; a memory whose loss loses facts is a second ledger and must not exist.
2. **Memory writes are events** (`MemoryWritten`-class events or receipt-mediated writes) so that what an agent remembered *when it decided* is reconstructable — otherwise context-policy learning (§22) has no ground truth.
3. **Memory poisoning is an anticipated failure mode** (§38): invalidation (`InvalidationChecked`) exists in the taxonomy; provenance labels on memory hits (K-28 meet-semilattice) should be required so a poisoned memory item is traceable to its source.

`[INFERENCE]` Reflexion's lesson is correctly absorbable here: reflective feedback stored in episodic memory alters later behavior without weight updates — a memory plugin, not a mechanism. The Staff proposal's framing ("the ledger answers *what happened*; memory answers *what is worth retrieving now*") is the right epistemic division and should be quoted in the lock.

---

## 19. Context Architecture

**The pipeline `Ledger/CAS/Memory/Repository → Selection → Compression → ContextBundle → Model`** — **AGREE; retrieval/ranking/summarization/compression/mapping/budgeting are replaceable strategies.**

`[FACT]` The as-built context compiler (packages) is one of the strongest AI-specific assets in the repo: L1–L5 prefix-stable layers, prefix frozen at construction (mid-run additions go to L5, preserving downstream cache hits), the brief exempt from compaction (work is checked against the brief, never the last summary of it), compaction strategies pluggable (`resolve_compaction_strategy`), competence prior recorded before turn 1, token estimation per block.

`[AI SYSTEMS RECOMMENDATION]` Four lock sentences:

1. **Lossy context transformations never destroy original evidence** — compression operates on a projection; the ledger/CAS originals are untouched. (Already structurally true; lock it as an invariant.)
2. **`context_digest` per turn is a trajectory field** (§17) — context-policy learning requires knowing what the agent saw, digested.
3. **Context budget is a first-class reservation dimension** (tokens) — already true in the 6-dim reservation.
4. **The context compiler holds no authority** — already true (pure function of construction + call arguments; no clock, no sink, no kernel).

`[INFERENCE]` Where the decomposition may become insufficient: the current `EpisodeView` is digest-thin; a research agent or tutor needs richer working context (retrieved documents, learner model state). That is plugin territory (`IContextManager` implementations), not substrate — the falsifier is if a *new domain's* context needs require kernel change (they should not; the compiler is already domain-blind).

---

## 20. Model Architecture

**Agents depend on a Model Broker/Port, not provider assumptions** — **AGREE, with a gap the lock must name.**

`[FACT]` packages has real model infrastructure: `openrouter.py` (896 LOC, SSE streaming), `ollama.py`, `lam.py`, `cassette.py` (recorded nondeterminism for replay), `routing.py` (pricing resolution, capabilities), `invocation.py` (565 LOC), `tier_escalation.py` (policy around the loop, escalating on stop-reason alone). `[FACT]` layer0 has no model port; the five SPIs exclude `IModelProvider`, which SPEC §2.2 lists as a first-party port.

`[AI SYSTEMS RECOMMENDATION]` Three decisions:

1. **Model identity participates in execution attribution (D_R).** The identity trinity (D_H/D_R/D_X) all three lanes endorse is *unimplementable* today in the new tree: D_R = H(D_H ∥ Runtime ∥ Environment ∥ ModelIdentity ∥ OracleIdentity) requires model identity to be recorded per execution — and there is no model port in layer0 and no per-turn model attribution anywhere. Heterogeneous teams (small local + coding-specialist + vision + reasoning + frontier + deterministic solver + human participant) are only meaningful if each member's *model identity* is part of its attributable execution. **Lock: model identity is a required attribution field; the port can arrive later, the field cannot.**
2. **Model calls become expressible as effects** (§8, §13) — `model.infer` verb, OBSERVATION sink, token cost in the reservation. This unifies model spend with tool spend under one budget/receipt regime and makes "which model produced this proposal" a receipt fact rather than an ambient fact.
3. **Cassette capability is the determinism story for schedule replay** — `[FACT]` `cassette.py` already implements recorded nondeterminism keyed for replay. The four-way replay taxonomy (state replay deterministic; schedule replay with cassettes; live re-execution need not match; byte-identical only for controlled fixtures) is correct; adopt verbatim.

`[INFERENCE]` The tier-escalation design deserves explicit praise in the lock as the pattern for all future model routing: it escalates on *stop reason alone*, never on a model's opinion of its own output — the same exteriority discipline as the evaluator, applied to routing. Future LLM routers (learned P(success|task,harness) selection) are plugins above this, and the calibration data they need comes from trajectories (§17).

---

## 21. Plugin Architecture

**Plugin-first** — **AGREE with the corpus's boundary, plus three AI-specific placements.**

Below the plugin line (mechanism/authority): identity, authority, effect mediation, event semantics, resource conservation, plugin lifecycle, scheduling mechanism — **plus canonicalisation (JCS is identity), the selector algebra, and the ledger write path** (concurring with the Tech Lead: a plugin that could change JCS could change every digest in the system; `ceiling.py`'s broken selector re-implementation is the proof).

Above the line (strategy/cognition/domain): planner, memory, context, compression, cache strategy, indexing, AST, heuristics, tools, skills, model routing, reflection, evaluation *gates*, self-improvement strategies, Meta-Harness strategies, swarm coordination policies.

`[AI SYSTEMS RECOMMENDATION]` Two AI-specific additions to the boundary sentence:

1. **The gate that requests judgment is a plugin; the judge is not** (Tech Lead's correction, which I endorse on reward-hacking grounds: C-1 is what the absence of this sentence produced).
2. **The trajectory emitter is below the line** — the record of what happened during execution is state-plane machinery, not a plugin strategy. A plugin that could choose *not to record* a trajectory could hide its own behavior from the learning loop. `[INFERENCE]` This is the telemetry analog of K-47's durable intent: the evidence of execution must not be optional to the executor.

`[FACT]` The wire is real and untested: `registry/broker.py` (subprocess Popen, POSIX rlimits, setsid, UDS, line-delimited JSON-RPC 2.0, four-state cell FSM, method allow-list, SIGTERM→SIGKILL reap), `worker.py` (UDS server, chmod 0600), `validator.py` (SemVer caret parsing, recursive schema shape validation). Zero tests on any of it. `[AI SYSTEMS RECOMMENDATION]` The lock's proof obligation for the plugin boundary is the broker suite (fault injection, timeout kill, rlimit enforcement, ceiling intersection with a non-empty ceiling, illegal FSM transition, evaluator key unreachability from any cell — AT-12, still open).

**Five SPIs, not more** — **AGREE.** `[FACT]` `layer0/spi/interfaces.py` implements exactly five; SPEC §2.2's list of nine is the outlier. The Staff proposal's §78 warning (no `IMutator`/`IReflector`/`ISwarm`/`IOptimizer`/`IMetaCognition` SPI-per-idea) is the correct anti-proliferation rule and should be locked: a sixth SPI requires a design review, and most "new capabilities" enter through the existing five plus ports.

---

## 22. Cognitive Composition

**Can higher-order cognition emerge through composition of planner/working-context/episodic-memory/semantic-memory/retrieval/reflection/uncertainty/world-modeling/tool-use/search/delegation/criticism/evaluation/strategy-selection, rather than CognitiveEngine/MetaCognitionEngine/ReasoningEngine?**

`[AI SYSTEMS RECOMMENDATION]` **Yes for the foreseeable research horizon, with named limits.**

Where the decomposition is strong:

- **Reflection** — `IPlanner.reflect(outcome, trajectory)` is already an SPI method; Reflexion-class adaptation is a planner plugin with memory. `[FACT]` SPEC §5.1 places the outer loop as a *second IPlanner at scheduler slot `outer`* with capability-restricted effects (manifest-mutation proposals, skill writes, oracle preregistration) — "meta-cognition is capability-shaped, not trust-shaped." This is the correct design and ADR-M0-12 (a tool is not an episode) is the correct guard.
- **Uncertainty/calibration** — SPEC §5.3's calibrated `P(pass|action, context)` from ledger history with Brier scoring per harness digest in telemetry. A plugin consuming trajectories; the substrate's only obligation is that the calibration data (verdicts + context digests) exists (§17).
- **Strategy selection** — tier escalation is the embryonic form; learned routing is a plugin above it.
- **Criticism/delegation** — spawn with a critic harness (§10–11).
- **World modeling / search** — planner plugins; the kernel is agnostic.

Where it may become insufficient (honest limits):

1. **Cross-episode working state.** The episode loop is turn-bounded; a "cognitive architecture" with persistent working memory across episodes needs the memory plugin + scheduler slots, which exists, but the *composition* of inner/outer loops across long horizons is unproven. `[RESEARCH HYPOTHESIS]` Global-workspace-style coordination (specialized plugins → selected information → ContextBundle → planner) is expressible as a context-manager plugin; whether it *suffices* for coherent long-horizon behavior is unknown.
2. **Metacognition as observable functions** (Staff §33: monitoring, diagnosis, strategy selection, reflection, calibration) is the right decomposition — each is measurable. `[UNKNOWN]` Whether the *composition* of measurable metacognitive functions yields calibrated self-models at swarm scale is an open empirical question.
3. **The kernel must never learn the word "cognition."** The falsifier: if any metacognitive capability requires kernel awareness, the decomposition has failed.

`[AI SYSTEMS RECOMMENDATION]` Lock the refusal: no `CognitiveEngine`, no `MetaCognitionEngine`, no `ReasoningEngine` — ever. Cognition is composition; the substrate provides identity, authority, causality, resources, and evidence.

---

## 23. Orchestrator / Coordination Architecture

**The orchestrator is a disposable coordination process over the authoritative ledger** — **AGREE with the corpus's two-authority refinement.**

`[AI SYSTEMS RECOMMENDATION]` Lock the distinction: **decision plane** (scheduler/orchestrator/kernel decide who/when/lease/budget/capability) vs **authoritative state plane** (ledger + reducers decide what happened). `Decision → DurableEvent → fold → EffectiveState`, never `Decision → MutableOrchestratorState`. For AI systems this has a specific consequence: **an orchestrator crash must lose nothing** — a new instance restarts by folding the project's event stream; leases expire via heartbeats; uncompleted tasks re-dispatch. Coordination state that lives only in the orchestrator's memory is hallucinated state (§38).

**What the orchestrator may never be:** a stateful monolith with its own truth. `[FACT]` The repo's own cautionary tale is `runtime/root.py` (1,418 LOC composition root) — the practical modularity bottleneck all lanes identify. `[AI SYSTEMS RECOMMENDATION]` The multi-harness orchestrator (the "missing middle" of §3) is legitimate new construction (Parecer v4's identification, endorsed): a *thin* scheduler-adjacent component that routes turns to harness instances under the decision/state split. It should be built after convergence, not during the lock, and its state must be event-derived from day one.

**Do not lock:** orchestration *policies* (DAG scheduling, blackboard, map-reduce coordination) — plugins. The substrate need is dependency semantics on events (§11 stigmergy), which lineage fields provide.

---

## 24. Execution Graph / Causality

**Relations `spawned_by/caused_by/depends_on/produced/consumed/evaluated_by/derived_from/invalidated_by` produce an execution graph as a projection over events** — **AGREE, unconditionally.**

`[AI SYSTEMS RECOMMENDATION]` Lock the sentence: *the execution graph is a projection; there is no graph store, no graph database, and no workflow DAG engine. A relation that cannot be derived from the ledger is fixed by a new envelope field or event kind, never by a graph write.* (Concurring with the Tech Lead's exact formulation — it is correct and cheap to verify.)

`[FACT]` The relations are recoverable *provided* lineage is populated: `spawned_by` from `parent_principal_id`/`parent_episode_id`, `caused_by` from `causation_id`, `correlation` from `correlation_id`, `produced`/`consumed` from artifact refs in receipts, `evaluated_by` from verdict subjects. `[FACT]` Today the fields exist in the envelope schema but are never populated by any producer — the graph is currently *unconstructible*, not merely unbuilt. This is §16's obligation restated: **the execution graph is the projection that makes swarm behavior auditable; without populated lineage it does not exist.**

`[INFERENCE]` SQLite recursive CTEs over `causation_id`/`parent_principal_id` satisfy graph queries for any plausible v0.6 scale; a graph database would create a second write path to truth and prematurely constrain agent autonomy (a static DAG is a workflow engine by another name — ADR-0003 stands).

---

## 25. Resource-Aware / Sparse Agency

**"More available agents should not imply more active agents"** — **AGREE as a principle; it is scheduling/coordination policy, not kernel semantics.**

`[AI SYSTEMS RECOMMENDATION]` The substrate's entire obligation is already in the lock list: budget as a vector (six integer dimensions), admission control on worst simultaneous case, `MAX_CONCURRENCY` as a configured value, agent identity independent of execution state (§12). The *selection policy* — one agent vs agent+critic vs specialist delegation vs parallel hypotheses vs full swarm, chosen by task/uncertainty/expected-benefit/budget/latency/risk — is a coordination plugin. `[INFERENCE]` The MoE analogy (capacity available ≠ capacity active) is informative but must not become architecture: sparse expert routing is a model-internal mechanism; sparse *agency* is a scheduling policy over logical agents. The Staff proposal's `N_active = policy(task, state, budget, uncertainty)` is the right target formula and is a plugin.

**Multi-agent economics (directive §25):** `[AI SYSTEMS RECOMMENDATION]` The architecture makes the experiments possible through exactly three mechanisms, all in the lock: (1) per-agent cost attribution (Receipt with lease_id — cost by principal), (2) budget conservation across spawn trees (total budget B is enforceable at the root), (3) trajectories with cost per turn (quality/cost/latency/tokens per agent per run). With those three, `1 agent × B` vs `N agents × B` is a paired experiment over harness compositions, and swarm efficiency `SE = (Q_swarm − Q_single)/(C_swarm − C_single)` is computable. Without them, it is not. **Do not assume multi-agent improves performance** — the lock should carry the Staff proposal's E2 experiment as a standing obligation of the future lab, and the falsification: if SE ≤ 0 for a task class, swarms are not used for that class.

---

## 26. Concurrency Architecture

**"Design multi-agent semantics now; enable parallel execution only when correctness and measurement justify it"** — **AGREE; this is the best-prepared deferral in the corpus.**

`[AI SYSTEMS RECOMMENDATION]` What v0.6 encodes now (all semantics, no machinery): causation, correlation, parenthood, ownership, read/write selectors, budget lineage, capability lineage, cancellation semantics, leases. `[FACT]` The strongest existing asset: selector overlap *is* the independence predicate (`W_i ∩ R_j = ∅ ∧ R_i ∩ W_j = ∅ ∧ W_i ∩ W_j = ∅`), already computable in `resource_selector.py`, and `independence_groups` already declared on `Proposal`. `[INFERENCE]` Flipping concurrency on later is a scheduler change, not an architecture change — the correct position for a lock.

`[AI SYSTEMS RECOMMENDATION]` Add two semantics the corpus under-specifies:

1. **Cancellation as a first-class typed outcome** — `[FACT]` the packages loop already handles `is_cancelled` before proposal and reduces it to `CANCELLED`; the layer0 driver has a `cancel()` flag. Lock: cancellation is an event (`RunAborted` reason=cancelled), a typed terminal, and never an exception.
2. **Revocation as point-of-effect semantics** — a revoked grant fails S8, not the next request; `Revoke ⇒ NoNewPrivilegedDispatch`, then local termination when possible, remote reconciliation, rejection of new operations and lease renewals. (Staff §50's realistic revocation; one sentence, expensive to retrofit.)

**Sufficient to avoid future migration?** `[INFERENCE]` Yes, with one caveat: the serialized-commit question. Concurrent execution with a serial ledger append is fine (measure `s = T_serial/T_total` before presuming); vector clocks/Merkle DAGs/distributed logs are correctly deferred behind evidence. The falsifier: if enabling `MAX_CONCURRENCY = N` later requires envelope changes, the deferral failed — and the envelope fields in §16 are chosen precisely so it does not.

---

## 27. Meta-Harness Architecture

**Meta-Harness is NOT a separate runtime engine; it is the process that composes, instantiates, observes, measures, compares, and proposes evolution of Harness Definitions** — **AGREE; defer entirely to P3.**

`[AI SYSTEMS RECOMMENDATION]` The lock's only Meta-Harness obligations are *negative* (what not to build) and *enabling* (what makes it possible later):

**Negative:** no `MetaHarnessEngine`, no in-place self-modification, no agent with write access to its own harness definition, no promotion without a preregistered statistical gate, no autonomous core modification (SPEC §9's refusals stand verbatim — they are among the healthiest sentences in the repository).

**Enabling (the entire cost is schemas already in the lock):**
- Harness-as-data with complete D_H (§15) — a candidate harness is a manifest with a different digest.
- Trajectory records (§17) — the fitness signal.
- Identity trinity D_H/D_R/D_X (§20) — experiment cells.
- Exterior verdicts (§30) — un-gameable selection.
- The H0 → Execute → Observe Trajectory → Generate H1 → Controlled Experiment → External Evaluation → Promotion/Rejection cycle is then *expressible* without any new mechanism: the mutator is a planner plugin whose effects are manifest-mutation proposals (SPEC §5.1's capability-shaped meta-cognition), the experiment is paired runs, the promotion is a signed governance event.

**Can optimizer/mutator/agent-designer/team-designer/prompt-optimizer/tool-selector/model-router/skill-synthesizer themselves be Harnesses?** `[RESEARCH HYPOTHESIS]` Yes — `Optimizer ∈ H` is the theoretically interesting recursion (Staff §88), and nothing in the substrate prevents it: an optimizer is an agent whose harness includes analysis plugins and whose effects are manifest proposals. `[AI SYSTEMS RECOMMENDATION]` Do not build it; do not *prevent* it. The governance boundary (learning proposes, experiment measures, evaluator judges, promotion authority decides — learning ≠ authority) must be locked now because it is the anti-reward-hacking spine, and it costs one paragraph.

---

## 28. Self-Improvement Architecture

**The eight levels, adjudicated:**

| Level | v0.6 disposition | Rationale |
|---|---|---|
| Runtime adaptation (retry, rerouting, context adjustment) | **Exists** — tier escalation, model selection | Already plugin policy; no lock |
| Memory adaptation | **Anticipate (SPI shape only)** | `IMemoryEngine` exists; semantics deferred |
| Skill adaptation | **Defer (P3)** | Selection pipeline is Phase-2; artifact properties locked (§14) |
| Composition adaptation (new manifest = new D_H) | **Anticipate — free** | A-5 makes it expressible; the compiler fix (§15) makes it *complete* |
| Planner/Policy adaptation | **Defer (P3)** | Mutation operators are plugins; gated on trajectory corpus |
| Plugin synthesis | **Defer (P3, stronger governance)** | Generated code is untrusted execution — container tier mandatory |
| Model adaptation (SFT/DPO/LoRA) | **Defer (P3, M6)** | Gated on harvest corpus + statistical power; trajectory schema (§17) is the prerequisite |
| Core modification | **REFUSE — permanently, for autonomous loops** | SPEC §9, A-6; human review + PR only |

`[AI SYSTEMS RECOMMENDATION]` The lock carries three self-improvement sentences: (1) **learning never promotes** — the learning plane proposes, the experiment plane measures, the evaluator judges, the promotion authority decides; (2) **preregistration is required for confirmatory claims and promotion, not for exploration** (Staff §72's correction — locking "no learning without preregistration" as written would forbid ordinary investigation); (3) **corpus admission is by provenance, not age** (signed verdict valid, trajectory digest valid, oracle/execution identity known → eligible; else quarantine — Staff §75, strictly better than an age cutoff and a schema decision, so it belongs in the lock).

`[INFERENCE]` The Gödel-Machine contrast is worth one lock sentence: formal proof of improvement is impractical in LLM environments; Vanguard's path is *empirical* — mutation → experiment → exterior evidence → promotion — with explicit governance. Darwin Gödel Machine-style empirical self-modification is the research neighbor; the difference is governance, and the governance is the lock's to state.

---

## 29. Evaluation / Learning / Promotion Separation

**The separation is the project's moat and its most AI-load-bearing architecture.**

`[AI SYSTEMS RECOMMENDATION]` Lock the four-way separation with the reducer-level enforcement the Tech Lead proposes, which I endorse and extend on learning grounds:

1. **The judge is exterior** — separate process, separate identity (UID 10002), signed verdicts, unreachable from agent *and from every plugin*. `[FACT]` The as-built daemon is stronger than the spec (SO_PEERCRED, Ed25519, console-script packaging).
2. **An unsigned verdict is not a verdict** — enforced at the *reducer*: a `VerdictRecorded` payload without a signature verifiable over `subject_digest` is a ledger validation failure. `[INFERENCE]` Reducer enforcement is the right layer for an AI-specific reason: no emission path can bypass it, which means *no learning loop can be fed by self-signed verdicts*. This is the structural defense against reward hacking — the failure mode where the system optimizes the signer instead of the task.
3. **The judge is not truth** — `SignedVerdict ⇏ CorrectVerdict`. The oracle is versioned, content-addressed, tested, adversarially evaluated, replaceable through governance. Evaluation leakage, benchmark overfitting, and agent-evaluator collusion remain live risks (§38) that the *science* plane (holdouts, paired designs, adversarial oracle review) must manage; the substrate's job is to make the judge's identity and version part of every attribution (D_X).
4. **Promotion is a partial order over a frontier** (ADR-0015) — multidimensional metrics (pass rate, cost, latency, tokens, turns, regression rate, safety failures, calibration), Pareto dominance, never a scalar reward.

`[FACT]` The measurement lab exists: McNemar paired testing, A/A floors, preregistration discipline, `_retracted/` convention with RETRACTION.md. `[INFERENCE]` This apparatus, plus exterior verdicts, plus complete attribution, is the combination no competitor pipeline has — the Staff proposal's "moat" argument is correct, and the trajectory schema is the missing piece that makes it real.

---

## 30. AI-Specific Security Boundary

**Minimum AI-specific security substrate required now:**

| Requirement | Status | Lock? |
|---|---|---|
| Principal identity (typed, with lineage) | Absent | **LOCK** |
| Capability boundaries (ceiling survives compile; fail-closed defaults) | Broken (C-2 chain) | **LOCK** |
| Effect mediation (one path, S0–S12) | Strong in packages | **LOCK** (keep verbatim) |
| Budget conservation (6-dim, K-07, parent leases) | Strong | **LOCK** |
| Spawn attenuation (subset-or-deny-whole) | Strong in packages | **LOCK** |
| External evaluator boundary (signed, unreachable) | Strong in packages; inverted in layer0 | **LOCK + repair** |
| Provenance (K-28 meet, taint predicate live) | Weakened in layer0 fork | **LOCK** |
| Plugin boundary (wire-first, untrusted by default) | Built, untested | **LOCK + test obligation** |
| Sandbox path for untrusted execution (bwrap fail-closed) | Strong in packages | **LOCK** |
| Trajectory emission (evidence cannot be hidden by the executor) | Absent | **LOCK** (this lane's addition) |

**Explicitly deferred (later hardening):** WASM everywhere, remote attestation, multi-host zero trust, distributed PKI, hardware isolation, supply-chain machinery, seccomp beyond rlimits, key rotation/quorum, network egress policy. `[AI SYSTEMS RECOMMENDATION]` Concur with the corpus: structural security is born with the substrate; sophisticated hardening plugs into the same seams later. The one AI-specific addition: **the learning boundary is security** — an agent that can influence its own evaluation (self-signed verdicts, evaluator reachability, promotion authority held by the learning mechanism) is a reward-hacking surface, and the four-way separation (§29) is its closure.

---

## 31. MVP Simplicity vs Future Generality

The directive's asymmetry — **semantics for the future, implementation for the present** — applied to every major recommendation:

| Decision | Semantics locked now | Implementation now | Future machinery deferred |
|---|---|---|---|
| Recursive agency | Spawn invariants, harness-as-parameter signature, lineage fields | Adopt packages `spawn()` as reference; delete mock | Orchestrator, worker pools |
| Trajectory | Schema + emission point + provenance fields | One schema, one emitter change | Harvest, DPO, distillation |
| Capability ceiling | Survives compilation; fail-closed | Read the key; fix four fail-opens | Per-verb policy engines |
| Model identity | Required attribution field; effect-expressible | Field on D_R; port later | Broker, routing learners |
| Swarm | "Policy, not engine" refusal | Nothing | All coordination plugins |
| Memory | "Never authoritative" + writes-are-events | Nothing | All memory plugins |
| Context | "Lossy never destroys evidence" + context_digest | Nothing (compiler exists) | Retrieval/ranking learners |
| Meta-Harness | Learning ≠ authority; refusals | Nothing | The entire loop |
| Concurrency | Full semantic field set; MAX_CONCURRENCY=1 | Sequential driver | Parallel workers |

`[AI SYSTEMS RECOMMENDATION]` The MVP is a **single coding agent on the converged substrate with real model calls, real exterior verdicts, complete lineage, and harvestable trajectories.** That is shippable, small, and leaves nothing to rewrite. The rejected extremes: building the future platform first (delays the useful agent indefinitely) and shipping the current layer0 story (fabricated verdicts, content-free trajectories, dropped ceilings — a foundation whose *data* is worthless the day it runs).

---

## 32. Domain Generality Assessment

**The falsification invariant:** a new domain pack requires zero diffs under the substrate (I-7). `[FACT]` The mechanism exists: packs are manifests + plugins + selectors + oracles; `check_domain_blindness.py` greps the core; TableWorld exists as a second-domain witness (`vg-table-default/`, `tableworld.py` environment adapter).

`[AI SYSTEMS RECOMMENDATION]` Lock the *early generality smoke test* (Staff §61): immediately after the first coding agent works, add one small non-coding domain and require `git diff <substrate> == empty`. `[INFERENCE]` This is cheap insurance against the most likely silent failure — a core that accretes coding assumptions through "temporary" conveniences. `[FACT]` The repo has already demonstrated the failure mode in reverse: `layer0/registry/worker.py` special-cases `fs.read` — domain knowledge inside the would-be-blind core that the blindness gate's regex cannot see.

**Scenario walk-through (directive §28's ten scenarios, compressed):** single coding agent (composition — exists in packages); coding+reviewer (spawn with critic harness — needs heterogeneous spawn); architect→coder→tester team (spawn tree — needs lineage); autonomous bug-fix team (same + terminal loop — exists); deep-research agent (search/retrieval/citation toolkits + memory plugin — new packs, zero core); parallel research team (independence groups — declared); RAG assistant (retrieval toolkit + context plugin — new pack); adaptive tutor (learner-memory plugin + curriculum policy — new pack); prototype-writing researcher (terminal + container tier — exists); autonomous heterogeneous project (all of the above + orchestrator — the missing middle). **Kernel changes required: zero. New primitives required: zero.** The answer to the generality falsification test is that the *architecture* passes on paper and the *as-built* passes wherever the four AI-load-bearing obligations are met.

---

## 33. Coding Agent Validation

`[FACT]` The coding domain is the correct first domain: precise artifacts, tests, compilers, linters, repeatable environments, objective partial oracles, rich failure modes (Staff §62). `[FACT]` The pack exists: `packs/code-default/` with planner (drive-until-green), context (repo-map, 4000-token budget, prefix freeze), memory (sqlite-kv), evaluation (oracle-gate, coding-oracle@3), toolkits (fs, ast-patch, terminal, index), model routes (tier 1 ollama qwen2.5:1.5b → tier 2 deepseek-v4-flash → tier 3 $FRONTIER, escalate on verdict_fail/budget_ok), budget (250k usd_micros, 40 turns, depth 2), approval policy, system prompt.

`[AI SYSTEMS RECOMMENDATION]` The coding agent is the *instrument*, not the product: it exists to make the substrate's claims checkable. The lock's coding-agent obligations: (1) real model calls through the port (no fake providers in the acceptance path); (2) real exterior verdicts (the Phase-1 gate: compiled code-default passes the lab dogfood triple + zero_hint_v1 at ≥ v0.4.5 baseline under paired McNemar, replay-parity green, E-COV behavioral); (3) harvestable trajectories from day one (§17 — every dogfood episode is future DPO data); (4) the generality smoke test immediately after (§32).

`[INFERENCE]` The AST-patch design (anchored edits matched to model competence, negotiated via capabilities; structural diffs into receipts for the planner and DPO harvester) is the correct AI-specific detail: it makes *edits* first-class evidence rather than text blobs.

---

## 34. Research Agent Validation

**Composition test:** Research Agent = Model + Search + Retrieval + Citation Tools + Memory + Synthesis Policy. `[AI SYSTEMS RECOMMENDATION]` Expressible as a new pack: search/retrieval/citation toolkits (new verbs: `web.search`, `doc.retrieve`, `cite.record` — new selectors, new schemas, zero kernel change), memory plugin (episodic + semantic), synthesis planner policy, citation-aware context compiler. The substrate obligations it exercises: tool schemas per verb (§13), memory-never-authoritative (§18), context digests (§19), trajectory provenance (§17 — research trajectories are the raw material for retrieval-policy learning).

`[INFERENCE]` The deep-research pattern (`search → retrieve → compare → critique → synthesize → cite`) is a planner policy over the same loop; a parallel research team is N spawns under a partitioned budget with artifact-mediated coordination (§11 stigmergy — produced/consumed relations over citation artifacts). `[AI SYSTEMS RECOMMENDATION]` Do not build this in v0.6; do note in the lock that its *only* substrate dependencies are the four AI-load-bearing obligations — which is the point of locking them.

---

## 35. Tutor / RAG Validation

**Tutor = Model + Learner Memory + Curriculum Policy + Explanation Tools + Assessment + Reflection.** `[AI SYSTEMS RECOMMENDATION]` A pack: learner-model memory plugin (state about the human learner — memory, never authoritative over facts), curriculum planner policy, assessment via the exterior evaluator (the tutor does not grade its own teaching; the *assessment oracle* does — the same separability thesis in a new domain), reflection via the outer-loop planner slot. `[INFERENCE]` The tutor is the cleanest test of the "agent as composition" thesis because nothing about it resembles coding: if it requires core changes, domain generality is falsified in the most useful possible way.

**RAG assistant** = retrieval toolkit + context plugin + memory. `[INFERENCE]` The substrate's context architecture (§19) is already the right shape: retrieval and ranking are `IContextManager` strategies; the RAG loop is a planner policy; citations are artifacts with provenance. The one AI-specific note: **retrieval quality is measurable only if context digests are recorded** (§17) — otherwise "better retrieval" is unfalsifiable.

---

## 36. Autonomous Team Validation

**Architect → coder → tester team; autonomous bug-fix team; autonomous project with heterogeneous agents.** `[AI SYSTEMS RECOMMENDATION]` The substrate requirements are exactly: heterogeneous spawn (harness as parameter, §10), populated lineage (spawn-tree attribution, §16), budget conservation across the tree (exists), per-agent cost attribution (Receipt lease/grant, §7), artifact-mediated coordination (§11), and the exterior judge remaining singular across the swarm ("one economy, one court" — SPEC §6.3). All are in the lock list; none is team-specific machinery.

`[INFERENCE]` The honest AI-systems caveat for the lock: **autonomous teams are where multi-agent economics bite** (§25). The lock should require that the first team experiments run under controlled total budget against a single-agent baseline, with swarm efficiency computed — not because teams won't help, but because "N agents" is the most theater-prone configuration in the field. The falsification: if 20 agents don't beat 1 agent at equal budget for a task class, swarms are not used there (Staff Provocation 3, endorsed).

---

## 37. SOTA Agent Framework Comparison

| SOTA pattern | Useful principle | Primitive? | Plugin/policy? | Vanguard generalizes it? |
|---|---|---|---|---|
| **ReAct** | Interleave reasoning and action | No | Planner policy | Yes — the propose/effect loop *is* ReAct with authority mediation |
| **Reflexion** | Reflective feedback in episodic memory, no weight update | No | `IPlanner.reflect` + memory plugin | Yes — reflect is an SPI method |
| **Voyager** | Growing executable skill library | No | Skill artifacts + selection pipeline | Yes, stronger — skills enter via exterior-verdict selection |
| **AutoGen** | Configurable multi-agent conversation | No | Coordination policy | Yes, lower-level — communication is policy over substrate |
| **MetaGPT** | Roles + SOPs/workflows | No | Manifests + policies | Partially — Vanguard *rejects* SOP-as-core (workflow engine anti-pattern); SOPs are planner policies |
| **Multi-agent debate** | Multiple instances improve some reasoning | No | Coordination policy | Yes — and treats swarm size as an economic variable, correctly |
| **Actor systems** | Independent entities, message passing | Conceptual kin | — | Yes — plus authority, budgets, provenance, exterior evaluation (the additions are the point) |
| **Workflow-based agents** | Explicit graphs | No | Projection only | **Rejected** — ADR-0003; loop-over-DAG inversion |
| **Tool-calling agents** | Uniform tool interface | Verb/selector/sink | Toolkits | Yes — with grants, which most frameworks lack |
| **Computer-use agents** | GUI/browser operation | No | Toolkit pack | Yes — browser toolkit, container tier |
| **Memory architectures** | Episodic/semantic/working distinction | No | `IMemoryEngine` plugins | Yes — with never-authoritative rule |
| **Agent skill libraries** | Reusable procedures | No | Artifacts | Yes (§14) |
| **LLM routers** | Route by task/cost | No | Policy (tier escalation embryonic) | Yes — with calibration from trajectories |
| **MoE analogy** | Sparse activation of capacity | No | Scheduling policy | As analogy only — not architecture |
| **Meta-learning (MAML)** | Fast adaptation | No | Search over composition space | Generalized — the adaptive space includes prompts/plugins/policies, not just weights |
| **Evolutionary search** | Mutation + selection | No | Candidate generator plugin | Yes — with governed promotion |
| **DPO/SFT/LoRA** | Preference/parametric adaptation | No | Offline pipeline (M6) | Yes — with un-gameable signal (exterior verdicts) and pairing validity via provenance |
| **Empirical self-improvement (DGM-class)** | Self-modification validated by benchmarks | No | Meta-Harness process | Yes — with governance as the differentiator |

`[AI SYSTEMS RECOMMENDATION]` The pattern across the table: **every SOTA idea enters as plugin, policy, artifact, or process — none as primitive.** That is the falsification test for the substrate (§57) and the answer to "does Vanguard already generalize it": for the ReAct/Reflexion/Voyager/AutoGen cluster, yes, and with stronger governance; for workflow engines, it deliberately does not, and should not.

---

## 38. AI-System Failure Modes

Adjudicated: **semantics now** vs **later hardening**:

| Failure mode | Disposition |
|---|---|
| Agent loops (no-progress spirals) | **Now** — `[FACT]` no-progress detection exists (same transition, N turns → ABANDONED); lock as scheduler semantic |
| Runaway recursive spawning | **Now** — depth as reservation dimension + budget conservation; the spawn tree cannot exceed root authority |
| Coordination explosion | **Now (semantics)** — budget vector + admission control; **later** — learned coordination policies |
| Context explosion | **Now (semantics)** — tokens as reservation dimension, compaction strategies, brief exempt; **later** — learned compression |
| Tool overuse | **Now** — every effect costs budget (K-07 debits reality); turns dimension bounds loop length |
| Hallucinated state | **Now** — event-derived state only; orchestrator memory never authoritative (§23); the projection rule |
| Memory poisoning | **Now (semantics)** — invalidation events, provenance labels on hits, memory-never-authoritative; **later** — adversarial memory audits |
| Evaluation leakage | **Later (science plane)** — holdouts, paired designs; substrate provides oracle identity in D_X |
| Reward hacking | **Now** — exterior signed judge, reducer-enforced verdict validity, learning ≠ authority (§29); the structural defense |
| Benchmark overfitting | **Later** — preregistration, holdouts, power analysis; the lab exists |
| Agent collusion with evaluator | **Now (boundary)** — judge unreachable from agent *and plugins*; **later** — collusion-detection experiments |
| Stale context | **Now (semantics)** — receipts re-enter justification; reground on failure exists in SPI; **later** — staleness detection policies |
| Duplicated work | **Later** — artifact-mediated coordination makes duplication *visible* (produced relations); dedup is policy |
| Model/provider drift | **Now (attribution)** — model identity in D_R makes drift *detectable*; **later** — drift monitoring |
| Non-deterministic external effects | **Now** — undeterminable/EffectReconciled semantics exist; cassettes for replay |
| Unbounded token spend | **Now** — usd_micros/tokens dimensions, worst-case admission |
| Swarm cost explosion | **Now (semantics)** — budget conservation at root; **later** — swarm-efficiency measurement (§25) |
| False self-improvement | **Now (governance)** — exterior verdicts + preregistered promotion + provenance-based corpus admission; the entire §28–29 apparatus |

`[INFERENCE]` The pattern: the substrate's defense against every failure mode is the same four obligations (lineage, ceiling, trajectory, exterior verdicts) plus the budget vector. That convergence is itself evidence the four are the right lock set.

---

## 39. What Must Be Primitive

**The minimal AI substrate vocabulary** (consolidated from §7):

```text
LOCKED PRIMITIVES (substrate — ~12):
Principal (typed, parent_id, depth) · HarnessRef/FrozenHarness (complete D_H)
HarnessInstance · Episode · Event/EventEnvelope (full lineage) · EffectRequest
Receipt (+lease_id, +grant_digest) · ArtifactRef/BlobRef · Capability/Grant
Reservation/Lease (6-dim) · VerdictRef/SignedVerdict (reducer-enforced)

LOCKED SCHEMAS (data, not runtime):
Trajectory record (mhf.trajectory/1, emission at EpisodeCompleted)
Skill artifact properties (content-addressed, versioned, capability-declared)

LOCKED DEFINITIONS (no runtime class):
Agent = Principal + HarnessInstance · Swarm = Agents + CoordinationPolicy
Meta-Harness = the governed evolution process · Execution graph = projection

LOCKED RULES (one sentence each):
Learning never promotes · Memory never authoritative · Lossy context never destroys evidence
Unsigned verdict is not a verdict · Ceiling survives compilation, fail-closed
Model identity is attribution · Trajectory emission is not optional to the executor

EXPLICITLY REFUSED AS PRIMITIVES:
Task · Skill (as runtime concept) · Memory · Swarm · Project (unless defined)
Meta-Harness (as engine) · Workflow · Graph · Orchestrator (as stateful monolith)
Experiment · Promotion · Cache · ChildPrincipal · MetaAgent
```

`[AI SYSTEMS RECOMMENDATION]` This is deliberately close to the Tech Lead's fourteen and the Staff proposal's §79 — the three lanes independently converging on a small vocabulary is itself evidence. My additions over both: the trajectory schema as a locked *schema* (Tech Lead has it; the Staff BETA doc defers it), and model identity as a locked attribution rule (neither has it explicitly).

---

## 40. What Must Stay Outside the Core

**Excluded from the substrate, without exception:**

```text
coding semantics (AST, patch, pytest, lint)     → packs
research semantics (search, retrieval, cite)    → packs
RAG semantics                                    → packs
tutorial semantics (curriculum, learner model)  → packs
AST logic                                        → toolkit plugins
retrieval logic                                  → toolkit/context plugins
memory algorithms (vector, graph, consolidation)→ IMemoryEngine plugins
reflection logic                                 → planner plugins
debate / swarm policy                            → coordination plugins
graph database                                   → projection (never a store)
prompt strategy                                  → harness manifest / planner config
model-specific behavior                          → model adapters behind the port
self-improvement algorithm                       → candidate-generator plugins (P3)
training logic (SFT/DPO/LoRA)                    → offline pipeline (P3, M6)
```

`[FACT]` The enforcement mechanism exists: `check_domain_blindness.py` (I-7, CI-greppable), the boundary lattice in `check_boundaries.py`, and the pack structure. `[INFERENCE]` The known leak — `layer0/registry/worker.py`'s `fs.read` special case — shows the grep gate's limit; the duplication and behavioral gates (Tech Lead §17) are the complements. `[AI SYSTEMS RECOMMENDATION]` Lock the exclusion list verbatim from SPEC §9's honour table plus the additions above; the falsifier for each line is the generality smoke test (§32).

---

## 41. What I Would Preserve

1. **The separability thesis** — "what solved it must be separable, and the judge must be unreachable from the judged." The project's identity and its only credible anti-reward-hacking architecture.
2. **The S0–S12 dispatch spine with K-rules** — every ordering rule encodes a shipped defect; do not reorder, do not "simplify."
3. **The packages `spawn()`** (`agency/episode/engine.py:531`) — the working recursive-agency implementation: fail-closed scope parsing, depth ceiling, whole-denial attenuation, tool filtering, causation tagging, untrusted return spans (K-33).
4. **The exterior evaluator as built** — UID-10002 daemon, SO_PEERCRED, Ed25519, console script. Stronger than spec.
5. **The 6-dimension integer Reservation with parent leases and K-07 overrun debits** — the resource spine of resource-aware agency.
6. **Grant/descriptor binding (K-18)** — refused at issuance, verified at point of effect, cascading revoke. The best-designed code in the repo.
7. **Attenuation denies whole (K-26)** — with its reasoning: a child repeatedly over-asking is the strongest intrusion signal this system shape produces.
8. **The L1–L5 prefix-stable context compiler** — prefix frozen at construction, brief exempt from compaction, competence prior before turn 1. A genuinely strong AI-specific asset.
9. **`RunTelemetry`'s integer-only, absence-preserving discipline** — "absent is not zero"; floats are not truth. The right epistemics for measurement.
10. **The tier-escalation policy** — escalating on stop-reason alone, never on self-opinion. The exteriority discipline applied to routing.
11. **JCS + golden vectors** as identity; **SQLite WAL** as ledger; **bwrap** as sandbox.
12. **The five SPIs** and the wire-first broker (untested but real).
13. **SPEC §9's refusals and the honour table** — the healthiest document section in the repository.
14. **The measurement lab** — McNemar, A/A floors, preregistration, the `_retracted/` convention.
15. **The skill-card embryonics** — frozen prefix, bodies on disk, cards omitted whole.
16. **The two genuine kernel fixes in the layer0 fork** — `EffectFailed` split; `AuthorizationRequested`/`CapabilityAttenuated` emissions.

---

## 42. What I Would Change

1. **The trajectory record becomes real** — one schema (`mhf.trajectory/1` per SPEC §7, plus per-turn model identity, sampling parameters, and divergence-point fields), emitted at every `EpisodeCompleted`, no transformation step. The single highest-value AI change available.
2. **D_H becomes complete** — the harness digest includes system prompt, capability ceiling, approval policy, model routes. Prompt identity is harness identity.
3. **The capability ceiling survives compilation** — `_parse` reads `capabilities`; `intersect_ceilings` result is used; `ceiling.py`/`grants.py` default-deny and delegate to `decide()`.
4. **Lineage is populated by construction** — `LedgerEmitter.emit()` carries the full set; `causation_id`/`correlation_id` non-null on kernel events; envelope-level (not payload-level) causation.
5. **`Principal` becomes a typed value** with `parent_id` and `depth`.
6. **`Receipt` carries `lease_id` and `grant_digest`** — per-agent cost and authority attribution.
7. **Model identity becomes a required attribution field** (D_R), with `model.infer` as an expressible effect verb.
8. **The verdict rule moves to the reducer** — unsigned `VerdictRecorded` is a ledger validation failure.
9. **Spawn takes a harness parameter** — heterogeneous children; denial is a typed value.
10. **The layer0 mock spawn and fabricated verdicts are deleted** — a mock that satisfies a gate is worse than an unimplemented feature.
11. **`fold.py` folds `BudgetCommitted`**; the replay test becomes a cold-reader diff.
12. **The trajectory emitter sits below the plugin line** — execution evidence is not optional to the executor.

---

## 43. What I Would Remove / Avoid

1. **`layer0/scheduler/driver.py`'s fabricated emissions** — `VERDICT_RECORDED {"verdict": "pass"}`, `INVALIDATION_CHECKED {"ok": True}`, `CLAIM_RECORDED` from `len(receipts)`. Emit nothing rather than emit fiction.
2. **The layer0 mock `spawn()`** — two event emissions executing nothing.
3. **Duplicated kernel/events modules in layer0** — delete after CI retarget; port forward only the two genuine fixes (concurring with the Tech Lead's delete-not-merge).
4. **A Rust core, a third tree, a graph database, a workflow-DAG engine, hot-swap in v0.6** — all correctly rejected by the prior lanes; I concur on AI grounds additionally: each would *reduce* the substrate's scientific measurability (a third runtime is a third unattributable execution identity; a DAG engine forecloses planner autonomy).
5. **`ChildPrincipal` as a distinct type; `MetaAgent`/`SwarmParticipant` classes** — one recursive abstraction; differences are policy.
6. **Any SPI-per-idea proliferation** (`IMutator`, `IReflector`, `ISwarm`, `IOptimizer`, `IMetaCognition`).
7. **Scalar reward for promotion** — partial order over a frontier stands.
8. **Self-signed verdicts anywhere in the measurement path** — including "temporary" test doubles that write to production ledgers.
9. **The metaphysics in `vision.md`/`vanguard_body_detailed.md`** — enforce ADR-M0-10 or repeal it; a substrate whose documents claim emergent intelligence by taxonomy will Goodhart its own research narrative.

---

## 44. What I Would Explicitly Defer

Each deferral with its reversal condition:

| Deferred | Reversal condition |
|---|---|
| Concurrent execution | Measurement showing sequential execution binds lab throughput |
| Worker pools, CoW workspaces, sparse activation | Concurrency enabled |
| Heterogeneous model broker machinery | A second real model provider in a team run (the *field* exists now; the *machinery* does not) |
| Swarm coordination policies | First multi-agent vertical slice with populated lineage |
| Skill selection pipeline / harvest | Trajectory corpus exists (schema locked now, pipeline P3) |
| Meta-Harness loop, plugin synthesis, model adaptation | Statistical-power suite, sized by power analysis |
| Memory plugins beyond sqlite-kv | A domain that demonstrably needs episodic/semantic recall |
| Learned model routing | Calibration data from trajectories |
| WASM/container tiers beyond enum | A plugin that cannot run safely under subprocess+rlimits |
| `Project` as a locked concept | A normative one-sentence definition, or a second domain needing it |
| Multi-host distribution | Never in v0.6; new ADR required |

---

## 45. P0 AI Foundation Decisions

**Lock now — absence makes future recursive/multi-agent evolution require major reconstruction:**

| # | Decision | Falsifier |
|---|---|---|
| **P0-A1** | **Envelope lineage is normative and populated by construction**: `principal_id`, `parent_principal_id?`, `episode_id`, `parent_episode_id?`, `harness_digest`, `causation_id`, `correlation_id`, `idempotency_key`, `prev_digest`, `seq` + governance fields. Emitter signature makes them required. | `test_every_emitted_envelope_carries_full_lineage` — fails against today's `emit()` |
| **P0-A2** | **Trajectory record schema locked + emission point locked** (per SPEC §7 + model identity, sampling, divergence point). Emitted at every `EpisodeCompleted`; consumers unlocked. | `test_episode_terminates_in_valid_trajectory_row` — fails against today's content-free digest |
| **P0-A3** | **D_H is complete**: manifest + plugin digests + system prompt + capability ceiling + approval policy + model routes. | `test_two_harnesses_differing_only_in_prompt_have_different_dh` |
| **P0-A4** | **Capability ceiling survives compilation; authority is fail-closed.** No authority predicate returns `True` on empty input. | `test_declared_ceiling_survives_compilation_and_denies`; `test_empty_ceiling_denies_everything` |
| **P0-A5** | **Model identity is a required attribution dimension** (D_R); model inference is expressible as an effect. | `test_every_turn_attributed_to_model_identity` |
| **P0-A6** | **Spawn semantics locked against the packages implementation**: invariants via `attenuation.covers()`; harness as parameter; denial as typed value; `Principal` typed with lineage. | `test_child_grant_wider_than_parent_is_denied_whole`; `test_spawn_denial_is_typed_value` |
| **P0-A7** | **Unsigned verdict is not a verdict** — reducer-enforced. | `test_scheduler_cannot_produce_a_verdict_without_a_signature` — fails against `driver.py:138` |
| **P0-A8** | **Learning never promotes; memory never authoritative; lossy context never destroys evidence; trajectory emission is not optional to the executor.** Four one-sentence rules. | Each names its wrong implementation |
| **P0-A9** | **The compositional refusal set**: no engine per capability (Cognitive/Swarm/Meta/Research/Tutor); every SOTA pattern enters as plugin/policy/artifact; sixth SPI requires design review. | The generality smoke test; the falsification list (§57) |

*(P0-A1, A4, A6, A7 overlap the Tech Lead's P0-A/B/E/F/J — independently reached; the AI-specific additions are A2, A3, A5, A8's trajectory rule.)*

---

## 46. P1 Lock-or-Defer Decisions

| # | Decision | My call |
|---|---|---|
| P1-1 | `project_id` mandatory envelope field | **CONDITIONAL LOCK** — only with a one-sentence normative definition (consistency unit: one stream, one ceiling, one root budget); else `root_episode_id` (concurring with Tech Lead) |
| P1-2 | `Principal` typed value | **LOCK NOW** — P0-A6 depends on it |
| P1-3 | `Receipt` carries `lease_id` + `grant_digest` | **LOCK NOW** — per-agent economics (§25) depends on it |
| P1-4 | Schema reconciliation (`mhf` vs `v4` envelopes/taxonomies) | **LOCK NOW** — it is a ledger migration; discovering later costs a compatibility layer |
| P1-5 | `model.infer` effect verb semantics | **LOCK the semantic slot NOW; implement the port later** |
| P1-6 | `MAX_CONCURRENCY` configured = 1; admission on worst simultaneous case | **LOCK NOW** — free |
| P1-7 | Revocation point-of-effect semantics | **LOCK NOW** — one sentence |
| P1-8 | Provenance meet over artifact inputs; taint predicate live default | **LOCK NOW** |
| P1-9 | Preregistration scoped to confirmatory claims; corpus admission by provenance | **LOCK NOW** — schema decisions |
| P1-10 | Concurrency execution | **DEFER DELIBERATELY** |
| P1-11 | Mutation-score gate on kernel+reducers | **DEFER** to first code wave; name it as the obligation rule's enforcement |
| P1-12 | Orchestrator (multi-harness) construction | **DEFER DELIBERATELY** — after convergence; state event-derived from day one |
| P1-13 | Heterogeneous spawn implementation | **DEFER** (semantics locked in P0-A6; implementation with the orchestrator) |
| P1-14 | Skill artifact schema | **DEFER** — properties locked (§14); schema when the selection pipeline nears |

---

## 47. P2 Replaceable Implementation Choices

Memory engine implementations (sqlite-kv today; vector/graph later); context compaction strategies; index implementations (tree-sitter vs ast); repo-map ranking; model adapter clients; pricing tables; CLI/TUI ergonomics; blob GC policy; snapshot cadence; JSON-RPC batching; rlimit values; container base images; telemetry export formats; the trajectory *consumer* pipelines (harvest, DPO mining — the schema is locked, the consumers are not); swarm coordination plugin implementations; prompt templates (data in manifests, not code).

---

## 48. P3 Research Program

The Meta-Harness loop (candidate generation → paired experiment → exterior evaluation → governed promotion); harness-space search algorithms (evolutionary, Bayesian, bandit, LLM-proposed — all as comparable plugins); skill harvest and synthesis; DPO/SFT/LoRA distillation from exterior-verified trajectories; calibrated model routing; cross-domain transfer of skills/plugins; sparse-agency selection policies; swarm-efficiency measurement program (E2); recursive-depth economics (E3); stigmergic coordination dynamics; memory-consolidation strategies; active-inference formulations *only if formally implemented* (Staff §35's conservatism is correct); Gödel-Machine-contrast studies (empirical vs proof-based self-improvement under governance); agent-evaluator collusion detection; benchmark-overfitting detection via holdout discipline.

`[RESEARCH HYPOTHESIS]` All of the above are research programs, not capabilities. The substrate's contribution is making them *runnable and attributable* — nothing more, and that is its value.

---

## 49. Unknowns / Required Experiments

| # | Unknown | Experiment |
|---|---|---|
| U-A1 | Does trajectory harvesting yield valid DPO pairs at practical volumes? | Mine pairs from dogfood runs under the locked schema; measure pair validity rate (prefix match + verdict divergence) |
| U-A2 | Is `K ≪ N` the right scale model? | Instrument a 20-episode dogfood run for worker occupancy (concurring with Tech Lead U-1) |
| U-A3 | Does composition beat model scale at fixed budget (H5)? | Fixed-model ablation (E1): vary memory/indexing/tools/reflection/compression; measure ΔY |
| U-A4 | Do swarms beat single agents at equal total budget? | E2 paired design; compute swarm efficiency SE per task class |
| U-A5 | Does recursive depth pay? | E3: depth 0–3, competence vs cost |
| U-A6 | Is the context compiler's prefix stability worth its constraints? | A/B cache-hit-rate measurement (attribution.prefix_hits telemetry) |
| U-A7 | Does calibrated escalation improve over fixed tiers? | Brier-score comparison per harness digest |
| U-A8 | Can skills transfer across domains (H7)? | Skill artifact applied from coding to a second pack; measure lift |
| U-A9 | Subprocess-per-plugin overhead at coding turn rates? | Broker round-trip benchmark (Parecer v4 estimates 0.1–1 ms vs 10⁰–10¹ s model calls; confirm) |
| U-A10 | Does the exterior-verdict signal survive oracle drift? | Verdict validity across oracle versions; D_X sensitivity analysis |

---

## 50. Principal Staff Engineer Review

**`principal_engineer_proposal.md`** — the conceptual north star, and the corpus's richest AI-systems document. My adjudication of its major decisions:

| Decision | Verdict |
|---|---|
| Recursive machine; no engine per capability (§5–8) | **AGREE** — the core thesis; endorsed on AI-systems grounds |
| `Agent = Principal + HarnessInstance`; agent as composition (§6) | **AGREE** |
| Swarm = Agents + CoordinationPolicy (§8) | **AGREE** |
| Stigmergy as interpretation, not primitive (§9) | **AGREE** |
| Graph as projection; no workflow engine (§10) | **AGREE** |
| Ledger as epistemological heart; hybrid event sourcing (§11–13) | **AGREE** |
| "Everything is an event" ≠ "every byte is an event" (§13) | **AGREE** |
| Identity trinity D_H/D_R/D_X (§16) | **AGREE — and under-implemented: D_R requires model identity, which no tree records** |
| Plugin-first, not everything-is-plugin (§17–18) | **AGREE** |
| Memory is plugin; ledger ≠ memory (§19) | **AGREE** |
| Skills as versioned, content-addressed, measured artifacts (§20) | **AGREE** |
| Tools are capabilities, not intelligence (§21) | **AGREE** |
| Context compression is plugin, never alters evidence (§22) | **AGREE** |
| Cache is provenance-aware, never authority (§23) | **AGREE** |
| Meta-Harness as process, not engine (§26) | **AGREE** |
| Self-improvement levels 0–5; core modification not autonomous (§27) | **AGREE** |
| Learning plane never promotes (§28) | **AGREE** |
| Evaluator is authority, not truth (§29) | **AGREE** |
| Intelligence as systemic property Y = F(M,P,Mem,Ctx,Tools,Skills,Search,Coord,Eval,B,Env) (§30) | **AGREE** — the correct framing for H5 |
| Marginal contribution measurement Δ_C (§31) | **AGREE — requires complete D_H (my P0-A3), which their own BETA doc does not fix** |
| Cognition by composition; metacognition as observable functions (§32–33) | **AGREE with limits (§22 here)** |
| Neuroscience as hypothesis source, not blueprint (§34–36) | **AGREE** |
| Evolution/genetics as analogy outside ontology (§37) | **AGREE** |
| Meta-learning over composition space (§38) | **AGREE** |
| DPO pairing validity requires provenance (§39) | **AGREE — and it is why the trajectory schema cannot wait (my P0-A2)** |
| Logical agents vs workers; model sharing; sparse agency (§42–45) | **AGREE as design; UNKNOWN as performance** |
| Budget as vector (§46) | **AGREE** |
| Concurrency: semantics now, execution later (§48) | **AGREE** |
| Security: structural now, hardening later (§51–52) | **AGREE** |
| Preregistration scoped to confirmatory (§72); corpus admission by provenance (§75) | **AGREE — adopt** |
| Minimal primitives (§79); roadmap (§100); "semantics now, implementation later" (§116) | **AGREE** |
| **The BETA doc's twelve P0s** | **AGREE on 1–4, 6–12 (with the modifications all lanes add); P0-5's envelope mandate is right but unimplementable on the current emitter; P0-12's deferral of the trajectory schema is my main disagreement — it is the one Phase-2 artifact expensive to retrofit** |

`[FACT]` The north-star document's self-contradiction on the canonical tree (abstract says recover from packages; body says layer0 is the unequivocal target) is real and the Tech Lead's reading is correct. `[INFERENCE]` Its 4,460-line volume is a risk the BETA doc correctly compresses; the compression dropped the trajectory schema, which is the wrong cut.

---

## 51. Tech Lead Review

The Tech Lead's review is the most forensically rigorous document in the corpus, and its findings reproduce (I verified C-1, C-2, the emitter drop, the content-free trajectory, the mock spawn, the 25-test/0.02s layer0 suite, the missing trajectory schema, the ADVISORY-verb grant-path gap by reading the same files).

| Tech Lead position | My verdict |
|---|---|
| Lock fewer concepts (~14) with explicit refusals | **AGREE** — my §39 converges |
| Proof obligations: every locked concept names its falsifier | **AGREE — adopt verbatim; it is the structural answer to lock decay** |
| Restore the evidence base inside the lock phase (four carve-outs) | **AGREE** — the lock's claims must be checkable |
| `packages/` canonical; delete-not-merge layer0 kernel/events; port the two fixes | **AGREE** |
| Duplication gate | **AGREE** — prevents the next fork |
| `project_id` conditional on definition | **AGREE** |
| Trajectory schema locked now (their P0-L) | **AGREE — strongly; my P0-A2 extends it with model identity, sampling, divergence point** |
| Envelope lineage as the single highest-value lock (P0-A) | **AGREE** |
| Verdict enforcement at the reducer | **AGREE** |
| Replay taxonomy + cold-reader falsifier | **AGREE** |
| Wire-first, five SPIs, in_process as privilege | **AGREE** |
| Python-first; Rust behind numeric gate | **AGREE** |
| CI subject of record = production lattice | **AGREE** |
| `ChildPrincipal` merged into Principal | **AGREE** |
| Defer swarm policies, messaging, negotiation | **AGREE** |

`[INFERENCE]` Where I add beyond the Tech Lead: they evaluated the substrate as an *engineering* system and locked what engineering cannot retrofit (envelope, durability, authority). I evaluate it as an *AI* system and lock additionally what *learning* cannot retrofit: the trajectory record's content (their P0-L locks the schema; my P0-A2 specifies the AI-load-bearing fields — per-turn model identity, sampling parameters, context digest, divergence point — without which the schema exists but the science does not), complete D_H (prompt identity), and model identity as attribution. Their review treats the trajectory as "the only Phase-2 requirement expensive to retrofit"; mine argues it is *the* bridge of the entire program and specifies its content.

---

## 52. Principal Architect Review

| Architect position | My verdict |
|---|---|
| Selective convergence; strangler; no third runtime | **AGREE** |
| Recursive agent primitive with uniform spawn | **AGREE** |
| Wire-first UDS/JSON-RPC; five SPIs | **AGREE** |
| State = fold(Events); graph as projection; SQLite recursive CTEs | **AGREE** |
| Triple-digest identity | **AGREE — with my D_R model-identity addition** |
| Logical/worker decoupling; 6-D budget; worst-case lock | **AGREE** |
| Two-phase concurrency | **AGREE** |
| Exterior evaluator axiom; F1 eradication | **AGREE** |
| Meta-Harness as data evolution; forbidden autonomous core modification | **AGREE** |
| Domain generality invariant (zero core diffs per pack) | **AGREE** |
| Behavioral CI matrix replacing lexical gates | **AGREE** |
| Their 38-concept table locking `ChildPrincipal`, `Task` (merge), `Skill` (generalize), `Experiment`, `Promotion`, `Meta-Harness` (generalize) | **PARTIAL DISAGREEMENT** — locking `Experiment`/`Promotion`/`Meta-Harness` as concepts now is over-locking (concurring with Tech Lead §9.3); the refusal set is stronger than the definition set for unimplemented things |
| Their three-way matrix showing "FULL AGREEMENT" on 18 dimensions | **PARTIAL** — the agreement is real on architecture; the matrix understates the sequencing and scope disagreements the Tech Lead documents precisely |

`[INFERENCE]` The Architect review is the best *synthesis* document; its weakness is the same as all syntheses — it smooths the disagreements that matter (CI sequencing, over-locking) into consensus rows. My lane exists partly to keep those disagreements visible.

---

## 53. Four-Way Agreement / Disagreement Matrix

| Dimension | Staff Eng | Tech Lead | Architect | **AI Specialist** | Consensus code |
|---|---|---|---|---|---|
| Runtime target | Python, packages canonical | Python, packages canonical | Python, selective convergence | Python, packages canonical | **FULL AGREEMENT** |
| Packages vs layer0 | Converge (self-contradictory doc) | Delete-not-merge + duplication gate | Strangler convergence | Concur with Tech Lead | **PARTIAL (mechanics)** |
| Minimal core | ~10 primitives (§79) | ~14 + refusals | 38-concept table | ~12 + refusals + schemas | **PARTIAL (scope)** |
| Python-first | Yes | Yes | Yes | Yes | **FULL AGREEMENT** |
| Event semantics | Everything-that-changes rule | Same + placement table | Same | Same + trajectory-emitter-below-line | **FULL AGREEMENT** |
| Ledger authority | State plane | State plane + negative rule | State plane | State plane + memory/context negative rules | **FULL AGREEMENT** |
| Agent definition | Principal + HarnessInstance | Same; ChildPrincipal merged | Same; ChildPrincipal kept | Same; no runtime class | **PARTIAL (ChildPrincipal)** |
| Recursive spawn | Invariants + fields | Same + reference impl | Same | Same + harness-as-parameter + typed denial | **AI SPECIALIST MODIFICATION** |
| Swarm model | Policy not engine | Same | Same | Same + stigmergy dependency note | **FULL AGREEMENT** |
| Tool abstraction | Capabilities not intelligence | Same | Same | Same + model.infer as effect | **AI SPECIALIST MODIFICATION** |
| Skills | Artifacts, versioned | Defer concept, lock properties | Generalize concept | Defer concept, lock artifact properties | **PARTIAL** |
| Harness composition | Declarative program | Same + ceiling fix | Same | Same + **complete D_H (prompt identity)** | **AI SPECIALIST MODIFICATION** |
| Plugin boundary | Wire-first, five SPIs | Same + broker tests | Same | Same + trajectory emitter below line | **FULL AGREEMENT** |
| SPIs | Five | Five | Five | Five | **FULL AGREEMENT** |
| Model boundary | Broker/port | (implicit) | Gateway adapters | **Model identity as required attribution + effect verb** | **AI SPECIALIST MODIFICATION** |
| Memory | Plugin, never authority | Same | Same | Same + writes-are-events + poisoning provenance | **FULL AGREEMENT (+)**** |
| Context | Plugin strategies | Same | Same | Same + context_digest in trajectory | **FULL AGREEMENT (+)**** |
| Orchestrator | Decision plane, disposable | Scheduler is the mechanism | Disposable coordinator | Same + event-derived state from day one | **FULL AGREEMENT** |
| Execution graph | Projection | Projection + lock sentence | Projection + CTEs | Projection (unconstructible today without lineage) | **FULL AGREEMENT** |
| Causality | Envelope fields | Same + emitter fix | Same | Same + populated-by-construction | **FULL AGREEMENT** |
| Identity | D_H/D_R/D_X | Adopt verbatim | Adopt | Adopt + **model identity required for D_R** | **AI SPECIALIST MODIFICATION** |
| Resources | 6-dim vector | Same | Same + worst-case lock | Same + per-agent attribution on Receipt | **FULL AGREEMENT (+)**** |
| Logical/worker | K ≪ N | Same (UNKNOWN as perf) | Same | Same (UNKNOWN as perf) | **FULL AGREEMENT** |
| Concurrency | Semantics now, exec later | Same | Same | Same + cancellation/revocation semantics | **FULL AGREEMENT** |
| Evaluation | Exterior, signed | Same + reducer enforcement | Same | Same + learning-never-promotes as the anti-reward-hacking spine | **FULL AGREEMENT (+)**** |
| Trajectory | Deferred by BETA (P3) | **Locked now (schema)** | Not addressed | **Locked now (schema + AI-load-bearing content)** | **AI SPECIALIST MODIFICATION (extending Tech Lead)** |
| Experimentation | Experiment plane before distribution | Statistical-power suite is longest lead | McNemar lab | Same + E1–E3 as standing obligations | **FULL AGREEMENT** |
| Meta-Harness | Process, P3 | Defer, P3 | Data evolution, P3 | Defer + governance sentences now | **FULL AGREEMENT** |
| Self-improvement | Levels; core never autonomous | Same | Same | Same + provenance-based admission | **FULL AGREEMENT** |
| Domain generality | Smoke test early | Same | Zero-diff invariant | Same + worker.py leak as cautionary tale | **FULL AGREEMENT** |
| Security | Structural now, hardening later | Same + fail-closed | Same | Same + learning boundary is security | **FULL AGREEMENT (+)**** |
| Migration complexity | Converge | Delete-not-merge | Strangler | Concur with Tech Lead | **PARTIAL** |
| MVP complexity | Vertical slice first | Same + evidence base | Same | Same + trajectory from day one | **FULL AGREEMENT (+)**** |
| Long-term AI flexibility | Composition thesis | Same | Same | **Endorsed conditionally on the four AI obligations** | **FULL AGREEMENT (qualified)** |

**Summary:** the four lanes agree on the architecture to an unusual degree. The genuine deltas are: (1) the Tech Lead's proof-obligation rule and CI sequencing (I adopt both); (2) the Architect's over-locking of unimplemented concepts (I side with the Tech Lead's refusals); (3) **my lane's additions — trajectory content, complete D_H, model identity — which none of the three locks explicitly, and which are the difference between a substrate that can *host* agents and one that can *learn from* them.**

---

## 54. Recommended v0.6 AI Concept Lock

**The lock, in one page:**

**Architecture (ratified, not reopened):** one recursive Python substrate at `vanguard/packages/` (converged); `Agent = Principal + HarnessInstance` as a definition with no runtime class; spawn with `Capabilities(child) ⊆ Capabilities(parent)` and `Budget(child) ≼ RemainingBudget(parent)`; swarm = policy; graph = projection; ledger = the only authority (`State = fold(Events)`, SQLite WAL); wire-first JSON-RPC/UDS plugins over five SPIs; exterior signed evaluator (UID-separated, Ed25519); sequential execution with full concurrency semantics; hybrid event sourcing with CAS for bytes; identity trinity D_H/D_R/D_X; Python-first, Rust behind a numeric gate; no third tree, no graph DB, no workflow engine, no hot-swap.

**AI-load-bearing obligations (this lane's contribution, each with its falsifier):**

1. **Lineage populated by construction** — the envelope carries `principal_id`, `parent_principal_id?`, `episode_id`, `parent_episode_id?`, `harness_digest`, `causation_id`, `correlation_id`; the emitter makes them required.
2. **Trajectory records are real** — `mhf.trajectory/1` schema locked with per-turn `{context_digest, proposal, receipts, cost, model_identity, sampling}` plus signed verdict and divergence point; emitted at every `EpisodeCompleted`; the emitter is below the plugin line.
3. **D_H is complete** — prompt, ceiling, approval policy, and model routes are inside the harness digest. Prompt identity is harness identity.
4. **Model identity is attribution** — every turn is attributable to a model identity; model inference is expressible as an effect verb.
5. **The ceiling survives compilation; authority fails closed; unsigned verdicts are not verdicts** (reducer-enforced).
6. **Learning never promotes; memory never authoritative; lossy context never destroys evidence.**

**Refused as primitives:** Task, Skill, Memory, Swarm, Project (unless defined), Meta-Harness, Workflow, Graph, Orchestrator-as-monolith, Experiment, Promotion, Cache, ChildPrincipal, MetaAgent — each is composition, projection, plugin, artifact, policy, or process.

**Deferred with reversal conditions:** concurrency execution, worker pools, model broker machinery, swarm policies, skill pipeline, Meta-Harness loop, model adaptation, WASM/container tiers, multi-host.

**Sequence:** restore the evidence base (the Tech Lead's four carve-outs) → forensic register → lock the P0 set with falsifiers → mark every P1 → ADRs/SPEC v0.6 → convergence wave (CI retarget first) → coding agent on the converged substrate **with trajectories from day one** → generality smoke test → orchestrator + heterogeneous spawn → concurrency → experiment plane → Meta-Harness.

---

## 55. Suggested SPEC / ADR Implications — DO NOT APPLY

*Recommendations only; nothing below was performed.*

1. **SPEC §7 / new schema `schemas/mhf/trajectory.schema.json`** — the trajectory record becomes normative with the AI-load-bearing fields: per-turn `model_identity`, `sampling`, `context_digest`, `proposal_digest`, `receipt_digests`, `cost`; plus `verdict` (signed, oracle identity), `attribution` (prefix_hits, escalations, divergence point), `harness_digest` (D_H), `execution_digest` (D_R). Emission at every `EpisodeCompleted`, no transformation step (I-9 as written).
2. **SPEC §2.3 / ADR (harness identity)** — `FrozenHarness.digest` (D_H) is defined over the *full resolved manifest*: plugin refs + digests + configs, system prompt digest, capability ceiling, approval policy digest, model routes with resolved model identities. Two harnesses differing in any behavior-affecting field must differ in D_H.
3. **ADR (model attribution)** — model identity is a required execution-attribution dimension (D_R component); `model.infer` is an expressible effect verb (OBSERVATION sink, `model://` selector, token cost in the reservation). The `IModelProvider` port may arrive later; the attribution field may not.
4. **ADR (trajectory emitter placement)** — the trajectory emitter is below the plugin line: execution evidence is state-plane machinery, not a plugin strategy. A plugin cannot decline to record its own trajectory.
5. **SPEC §1.2 / ADR (envelope lineage)** — the lineage field set becomes mandatory and populated by construction; `LedgerEmitter.emit()` carries the full set; `causation_id`/`correlation_id` non-null on kernel-emitted events.
6. **ADR (verdict validity at the reducer)** — an unsigned `VerdictRecorded` is a ledger validation failure, enforced at the reducer (no emission path can bypass it).
7. **ADR (fail-closed authority)** — no authority predicate returns `True` on empty input; the declared capability ceiling survives compilation; the declared isolation tier matches the executed one.
8. **ADR (learning governance)** — learning never promotes; preregistration is required for confirmatory claims and promotion, not exploration; corpus admission is by provenance, not age.
9. **SPEC §9 additions to the honour table** — no `CognitiveEngine`/`MetaCognitionEngine`/`ReasoningEngine`/`SwarmEngine`/`MetaHarnessEngine`, ever; every SOTA agent pattern enters as plugin, policy, artifact, or process; a sixth SPI requires a design review.
10. **ADR (spawn semantics)** — spawn signature `spawn(parent_principal, harness_digest, requested_scope, requested_reservation) -> Principal | Denial`; invariants via `attenuation.covers()`; denial is a typed value and an event; the packages implementation is the reference; the layer0 mock is deleted.
11. **SPEC §5.1 ratification** — the outer loop as a second `IPlanner` at scheduler slot `outer` with capability-restricted effects ("meta-cognition is capability-shaped, not trust-shaped") is the correct Meta-Harness substrate shape and should be cited as such.
12. **ADR-M0-10 enforcement note** — the metaphysics documents (`vision.md`, `vanguard_body_detailed.md`) either comply or the ADR is repealed; a research program whose documents claim emergent intelligence by taxonomy will Goodhart its own narrative.

---

## 56. Suggested Future Implementation Implications — DO NOT APPLY

*Recommendations only; nothing below was performed. Ordered by leverage per unit of effort:*

1. **Trajectory schema + emitter** (P0-A2) — one JSON Schema, one emitter change, one test. Every episode run afterward is harvestable. This should be the *first* code change after the lock, before or during convergence, so the convergence-wave dogfood episodes are not lost.
2. **Compiler reads `capabilities`/`system_prompt`/`approval_policy`; `intersect_ceilings` result is used; D_H digests the full manifest** (P0-A3/A4) — three small edits to `compose/compiler.py` plus tests. Makes every harness an addressable experimental unit.
3. **`LedgerEmitter.emit()` carries full lineage; `Principal` becomes a typed value; `Receipt` gains `lease_id`/`grant_digest`** (P0-A1) — envelope work that must precede any new ledger history.
4. **Delete the fabricated emissions and the mock spawn in `layer0/scheduler/driver.py`** — emit nothing rather than emit fiction; adopt `agency/episode/engine.py::spawn()` as the reference.
5. **Verdict validation at the reducer** (P0-A7) — closes C-1 structurally at the layer no emission path can bypass.
6. **`fold.py` folds `BudgetCommitted`; replay test becomes a cold-reader diff** — makes I-4 true rather than tautological.
7. **Model identity on the execution digest + `model.infer` verb slot** (P0-A5) — a field now; the port and broker later.
8. **Broker test suite** — fault injection, timeout kill, rlimit enforcement, ceiling intersection with non-empty ceiling, illegal FSM transition, evaluator key unreachability (AT-12).
9. **CI retarget to the production lattice** — the Tech Lead's ordering: CI subject first, duplication gate, parity gate, then delete the duplicated layer0 modules.
10. **Generality smoke test** — second domain pack immediately after the coding agent; `git diff <substrate> == empty`.
11. **Orchestrator + heterogeneous spawn** — after convergence; state event-derived from day one; spawn takes `harness_digest`.
12. **Experiment plane** — A/A, paired experiments, power analysis, holdout, FDR, Pareto metrics — before distribution, before Meta-Harness.

---

## 57. Architecture Falsification Criteria

**WHAT WOULD PROVE THIS WRONG?** — for every major AI architectural recommendation in this report:

| # | Recommendation | Falsification condition |
|---|---|---|
| F-1 | Compositional substrate (no engine per capability) | If sophisticated agents (critic, tutor, researcher, architect) repeatedly require new kernel primitives or new engines, the compositional substrate is insufficient. The generality smoke test is the early-warning instrument. |
| F-2 | Recursive agency (same machine for root and child) | If recursive agents cannot use the same execution semantics as root agents — if a child needs a different dispatch path, budget regime, or event vocabulary — recursive agency is insufficient. |
| F-3 | Agent as composition (no runtime class) | If a critic, reviewer, tutor, or researcher agent ever requires a subclass rather than a manifest, the abstraction level is wrong. |
| F-4 | Harness as declarative program | If simple tool compositions (list → read → LLM → write) cannot be represented without bespoke orchestration code, or if a candidate harness cannot be compiled, measured, and compared using only existing substrate mechanisms, the harness abstraction is insufficient for meta-programming. |
| F-5 | Complete D_H (prompt identity is harness identity) | If two harnesses differing only in system prompt (or ceiling, or model route) produce the same D_H, A/B attribution is broken and the experimental unit is fictional. Test: `test_two_harnesses_differing_only_in_prompt_have_different_dh`. |
| F-6 | Trajectory as learning substrate | If trajectories harvested under the locked schema cannot support failure analysis, agent comparison, and valid DPO pair generation (U-A1), the trajectory schema is insufficient — and if the schema was not locked before the episodes ran, the data is unrecoverable. |
| F-7 | Lineage populated by construction | If any kernel-emitted event lacks episode attribution or causation, the execution graph is unconstructible and swarm behavior is unauditable. Test: `test_every_emitted_envelope_carries_full_lineage`. |
| F-8 | Model identity as attribution | If a turn's producing model cannot be identified from the ledger + trajectory alone, heterogeneous teams are unattributable and D_R is meaningless. Test: `test_every_turn_attributed_to_model_identity`. |
| F-9 | Exterior evaluation as the learning signal | If any learning loop can be fed by a self-signed or plugin-signed verdict, the anti-reward-hacking spine is broken. Test: `test_scheduler_cannot_produce_a_verdict_without_a_signature` + reducer enforcement. |
| F-10 | Logical agents ≠ workers | If N logical agents require N heavyweight runtimes (processes, model instances, workspace copies), the logical-agent abstraction is insufficient. Measured by U-A2, not asserted. |
| F-11 | Plugin substitution is measurable | If plugin substitution cannot be measured independently (E4: swap one box, prove attribution), the experimentation architecture is insufficient. |
| F-12 | Domain generality | If a second unrelated domain requires core modification, domain generality is insufficient — and per the Staff proposal's Provocation 10, this must be treated as a scientific discovery, not hidden. |
| F-13 | Swarm-as-policy | If a coordination pattern (debate, committee, stigmergy) requires substrate changes beyond lineage/dependency semantics, swarm-as-policy is insufficient. |
| F-14 | Budget conservation as the recursion governor | If a spawn tree can exceed root authority on any dimension (capability, budget, depth), the governor is insufficient. Test: `test_child_grant_wider_than_parent_is_denied_whole` + the `_exceeds` None-bound hole. |
| F-15 | The four AI-load-bearing obligations as the lock set | If a future capability requires retrofitting data that the four obligations would have captured (per-turn context, model identity, causation, ceiling), the lock set was too narrow. If, conversely, locked obligations never bind any future decision, the lock set was too wide. |

---

## 58. Research Hypotheses

The directive's H1–H7, classified:

| # | Hypothesis | Classification | Notes |
|---|---|---|---|
| **H1 — Compositional Generality** | New capabilities can be added without core changes (`ΔCore(NewDomain) = 0`) | **SUPPORTED AS RESEARCH DIRECTION** | The pack mechanism, the five SPIs, and the boundary gates make it testable; TableWorld is the embryonic witness; the early smoke test is the instrument. Not yet demonstrated on a real second domain. |
| **H2 — Recursive Agency** | Root and child agents use the same primitive execution model (`PrimitiveSet(parent) = PrimitiveSet(child)`) | **SUPPORTED AS RESEARCH DIRECTION** | The packages `spawn()` is a working single-level proof; multi-level heterogeneous trees await the orchestrator and lineage fields. |
| **H3 — Reconstructible Agent State** | Operational state can be reconstructed from event history (`fold(L) = S`) | **SUPPORTED AS RESEARCH DIRECTION — currently unproven and partially false** | The replay gate is a tautology and `fold.py` discards `BudgetCommitted`; the property is real in the packages reducers and must be *proven* by the cold-reader test, not asserted. |
| **H4 — Sparse Scaling** | Logical agents can greatly outnumber heavyweight workers (`N_workers ≪ N_agents`) | **NEEDS EXPERIMENT** | No workload measurement exists (U-A2). The semantics are cheap to lock; the claim is unmeasured. |
| **H5 — Compositional Intelligence** | System performance can improve substantially with a fixed base model through better composition (`ΔY|_{M=fixed} > 0`) | **SUPPORTED AS RESEARCH DIRECTION — the program's central hypothesis** | Requires exactly what this lock adds: complete D_H (F-5), trajectories (F-6), and the E1 fixed-model ablation. Untestable on the current as-built. |
| **H6 — Governed Self-Improvement** | Candidate harnesses can improve through controlled experimentation without the learning mechanism holding promotion authority | **SUPPORTED AS RESEARCH DIRECTION** | The governance separation (§28–29) is the enabling condition; the statistical-power suite is the long-lead prerequisite; nothing should be promoted before it exists. |
| **H7 — Cross-Domain Transfer** | Skills/plugins learned in one domain can improve another without core modification | **NEEDS EXPERIMENT** | The artifact properties (§14) make it *expressible*; U-A8 measures it. No evidence either way. |

**Additional hypotheses this lane offers:**

- **H-A1 — Trajectory sufficiency:** the per-turn record `{context_digest, proposal, receipts, cost, model_identity, sampling}` + signed verdict is sufficient to support failure analysis, agent comparison, and valid preference-pair generation without redesign. `[RESEARCH HYPOTHESIS]` Falsified by U-A1's pair-validity rate.
- **H-A2 — Prompt-identity sensitivity:** a measurable fraction of harness-level performance variance is attributable to fields currently excluded from D_H (system prompt, ceiling, model routes). `[RESEARCH HYPOTHESIS]` Testable immediately after the D_H fix via E1-style ablation.
- **H-A3 — Attribution-driven honesty:** making model identity and context digests mandatory attribution fields reduces unattributable claims and self-certified measurements by construction. `[INFERENCE]` — partially verifiable by the disappearance of C-1-class defects under reducer enforcement.

**AGI position (directive §30):** the substrate could support scientifically meaningful research into compositional intelligence, recursive agency, cross-domain transfer, meta-learning, skill reuse, self-improvement, multi-agent coordination, resource-aware intelligence, and architecture search — **without the project claiming AGI.** `[AI SYSTEMS RECOMMENDATION]` The Staff proposal's §1 epistemics are the correct posture and should be quoted in the lock: this is a *falsifiable hypothesis about generality*, never a demonstrated capability; the moment the documents claim emergence, the research program Goodharts its own narrative.

---

## 59. MVP Recommendation

**The MVP this lane recommends, precisely:**

> A single coding agent on the converged substrate (`vanguard/packages/` + promoted `layer0/spi|registry|compose`), executing the `code-default` pack with real model calls through the model port, real exterior verdicts from the UID-10002 Ed25519 daemon, complete envelope lineage on every event, a complete D_H on every harness, and a harvestable trajectory record on every episode — running sequentially, gated by behavioral CI over the production lattice.

**What the MVP includes (and nothing more):**

```text
Converged substrate (kernel + events + WAL ledger + CAS from packages;
SPIs + broker + compiler from layer0, repaired)
code-default pack (planner, context, memory, toolkits, oracle gate)
Real model adapter (one provider is enough; the port is the point)
Exterior evaluator (as built — UID 10002, Ed25519)
Envelope lineage fields, populated
Complete D_H (ceiling + prompt + policy + routes inside the digest)
Trajectory schema + emission at EpisodeCompleted
Sequential scheduler (MAX_CONCURRENCY = 1, configured)
Behavioral CI: production suite + replay cold-reader + verdict-signature +
ceiling-survives-compilation + lineage-populated + trajectory-valid
```

**What the MVP explicitly excludes:** multi-agent execution (semantics locked, machinery deferred); swarms; skills pipeline; memory beyond sqlite-kv; Meta-Harness; model adaptation; concurrency; distribution; WASM/containers beyond enum; the orchestrator (next wave).

**Why this shape:** it is the smallest agent that *ships* (real model, real tools, real evaluation, real file edits) whose *data exhaust* is already the research substrate (lineage + D_H + trajectories). Every later capability — critic, researcher, tutor, team, swarm, meta — is a composition added on top, and every episode the MVP runs becomes usable evidence for the program that improves those compositions. The two failure shapes are both avoided: no platform-before-product (the MVP is weeks, not quarters, once convergence lands), and no corner-painting (nothing in the MVP requires reversal when recursion or richer composition arrives — the spawn semantics, lineage, ceiling, and trajectory fields are already locked and exercised).

**Sequencing note (concurring with the Tech Lead, extended):** the trajectory schema should land *before or during* the convergence wave, not after — the dogfood episodes run during convergence are exactly the first corpus, and they are currently being lost.

---

## 60. Final AI Agentic Systems Recommendation

**The central question, answered:**

> What should Vanguard/AETHER lock in v0.6 so that today's simple coding agent can evolve into a substrate where tools compose into capabilities, capabilities compose into agents, agents recursively compose into teams and swarms, trajectories become evidence for learning, and increasingly general behavior can emerge through reuse of the same primitives rather than continuous expansion of the core?

**Lock the compositional architecture — it is correct.** One recursive machine; `Agent = Principal + HarnessInstance` as a definition, never a runtime class; spawn with monotone authority and budget attenuation; swarm as policy; graph as projection; the ledger as the only authority; wire-first plugins over five SPIs; the judge exterior and signed; sequential execution with concurrent semantics; Python-first. I reached this position from the AI-systems side — testing the substrate against ReAct/Reflexion/Voyager/AutoGen/MetaGPT/debate/actor patterns and finding that every one of them is expressible as plugin, policy, artifact, or process over this substrate, and none requires a primitive — not by deference to the three lanes that reached it first.

**But a compositional substrate for *agents* is more than an authority-and-events machine.** Agents are systems that *act under attribution and learn from evidence*. The three prior lanes locked what engineering cannot retrofit — the envelope, durability, the authority spine. This lane's contribution is to lock what *learning* cannot retrofit:

1. **The trajectory record** — because an episode that does not record what it saw, did, cost, and was judged cannot later become training data, failure analysis, or fitness signal, and no amount of ledger archaeology reconstructs per-turn context and model identity after the fact.
2. **Complete harness identity** — because a composition whose digest ignores its prompt, ceiling, and model routes is not an experimental unit, and the entire program — A/B measurement, marginal-contribution attribution, harness-space search — is built on compositions being addressable.
3. **Model identity as attribution** — because heterogeneous teams, provider drift, routing research, and D_R itself are meaningless if the producing model is ambient rather than recorded.
4. **Lineage populated by construction** — because the execution graph, swarm auditability, and spawn governance are all the same fields, and they are the one schema decision that costs the ledger's history to revise.

These four are cheap now — one schema, one emitter signature, one compiler fix, one digest field — and they are precisely the things the current as-built gets wrong or leaves content-free: the trajectory digest identifies nothing; the compiler drops the ceiling; the emitter drops the lineage; no tree records model identity. **The gap between the architecture and the evidence base is the gap this lock must close.**

**And refuse the rest.** Task, Skill, Memory, Swarm, Project, Meta-Harness, Workflow, Graph, Orchestrator, Experiment, Promotion — each is a composition, projection, plugin, artifact, policy, or process. The substrate's job is to make them expressible, not to pre-design them. Every refusal is a place where the core could have grown an engine and must instead grow a composition. The falsification list (§57) is the standing check: the day a new capability requires a new engine is the day the thesis is wrong — and that day should be treated as a discovery, not a surprise.

**The golden rule, honored:** not an impressive architecture — a *generative* one. Primitive + primitive → capability; capability + capability → agent; agent + agent + policy → team; team + evaluation + learning → improving system — over few stable primitives, reusable composition, DRY implementation, replaceable strategies, event-derived state, explicit causality, resource-aware execution, recursive agency, external evidence, measurable improvement, and a lean MVP. The v0.6 lock that carries the architecture *plus* the four AI-load-bearing obligations is the smallest lock that satisfies both constraints the directive set: **small enough to ship a coding agent, durable enough that nothing about it must be undone when the agents start composing.**

---

*End of independent AI Agentic Systems Specialist assessment. No repository artifact other than this file was created or modified. No commit was made.*
