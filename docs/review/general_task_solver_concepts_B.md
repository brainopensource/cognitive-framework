---
title: "General Task Solver — Foundational Concepts, Field Review, and an Honest Assessment of Vanguard v4"
status: NON-NORMATIVE — analysis and proposal
authority: none. This document constrains nothing. It exists to inform a decision.
audience: [Project Lead, Tech Lead, Research Lead]
date: 2026-08-14
supersedes: nothing
relationship_to_v4: >
  Independent. Written to be usable if the v4 set is kept, refactored, or discarded.
  Where it disagrees with v4 it says so and says why.
---
# General Task Solver Concepts — Version B Concepts, Field Review, and an Honest Assessment of Vanguard v4 

> **One sentence.** The durable asset is not a coding agent, and not even a harness — it is a *substrate on which harnesses are cheap to build, cheap to measure, and cheap to discard*, because the field's own evidence says harnesses are the highest-leverage and shortest-lived component in the stack.

---

## 0. How to read this document

Three things are being attempted here, and conflating them would repeat the mistake this project already made once (the two-lineage divergence recorded in `00 §7`):

1. **A field review** — what is actually known, as of August 2026, about harness engineering and self-improving agent systems, with sources.
2. **A conceptual foundation** — the building blocks a general task-solving substrate needs, each traced to the discipline it comes from, and each stated as a mechanism rather than an analogy.
3. **An honest assessment of Vanguard v4** — what is genuinely strong, what is wrong, what is missing, and what is over-built.

The three are kept in separate chapters on purpose. §2 is falsifiable by citation. §3–§5 are design argument. §6 is judgement, and is labelled as such.

**Bias disclosure.** §2 was assembled from primary literature before §6 was written, so the review of v4 is measured against the field rather than against itself. Where v4 anticipated a finding, that is stated. Where it did not, that is also stated.

---

## 1. Executive judgement

For a reader who will read nothing else.

**On Vanguard v4 as a body of work.** It is, on the evidence I have read, *substantially better reasoned than the published state of the art on the questions it chooses to address*. The three closure conditions (`07 §1`), the measurement doctrine (`07 §5`), `inconclusive` as a first-class verdict (`06 §4.4`), resource-scoped rather than verb-scoped capabilities (`05`), and schema-enforced invalidation conditions (`INV-1`, structurally required and non-empty) are each *correct*, each *rare*, and several are *unpublished anywhere I can find*. That is not a small achievement and it should not be discarded.

**On Vanguard v4 as a project.** It is in the most dangerous state a project of this kind can occupy: **203 normative rules, twelve documents, roughly forty thousand words of specification, and no running system.** The corpus itself reports 133 of 203 rules with no test. The documents are honest about this — `08 §5.1` calls the red map "the phase's most honest progress metric" — but honesty about a risk is not mitigation of it. Specification maturity has outrun artifact maturity by a wide margin, and that ordering is the single strongest historical predictor of a project that never ships.

**The four substantive design defects**, in order of severity:

| # | Defect | Consequence |
|---|---|---|
| D-1 | **No component-addressable improvement surface.** v4 can attribute outcomes to *competence artifacts*; it cannot attribute them to *harness components* (system prompt, tool description, tool implementation, middleware, context assembly, routing, budgets, runtime image) | The evidence plane can answer "did this artifact help?" but not "which part of the harness caused this?" — which is the question the field has just learned how to answer, and the one that compounds |
| D-2 | **The human-correction delta is not a first-class object.** The diff between what the agent proposed and what the operator actually merged appears in no schema | The densest, cheapest, least-gameable signal in a coding harness is being discarded |
| D-3 | **No latency budget anywhere, while Phase 0 exit depends on a 60% dogfood routing threshold** | Every governance mechanism taxes the interactive path. The exit criterion is a product criterion; the architecture is optimised for a research criterion. One of them will lose, silently |
| D-4 | **`06` specifies a 4,000-word lifecycle for artifacts that have never existed, while `C-06` — "at least one distilled artifact beats baseline above the floor" — remains unfalsified** | If `C-06` fails, `06` is dead specification. The lifecycle should have been derived from the first surviving artifact, not before it |

**The recommendation.** Do not rewrite from scratch. The reasoning in `02`, `05`, `06 §4`, and `07 §5` is the most valuable thing this project has produced and it is not reproducible cheaply. Instead: **demote most of the corpus from normative to candidate-normative, restructure around a smaller invariant core, add the missing artifact-graph and correction-delta primitives, and impose a code-to-specification ratio gate.** Concrete deltas in §7.

---

## 2. What the field actually knows (August 2026)

### 2.1 Settled: the harness dominates, and the field has converged on its primitives

The convergence is real and it is not a differentiator. Comparing Claude Code, Codex, Copilot, Gemini CLI, Cursor and Devin surfaces the same foundational ideas repeatedly — a long-running execution loop, human-readable repo-local instruction files that persist project structure and conventions, git/shell/test/LSP/browser tooling, and multi-agent orchestration for complex problems.<sup>[1][4]</sup> Anyone shipping a CLI in 2026 gets these for free or does not ship.

What is *not* free is the magnitude of the harness effect, which is now quantified from several independent directions:

- On agentic benchmarks, the harness alone can move a score by 10–20 percentage points with the model weights held identical; the harness decides attempts, tools, context management, and what counts as solved.<sup>[10]</sup>
- Meta-Harness reports that changing only the harness around a fixed LLM produced a **6× performance gap** on the same benchmark.<sup>[8]</sup>
- LangChain's engineering team moved their coding agent from 30th to 5th on Terminal-Bench 2.0 without touching the model.<sup>[2]</sup>
- Agentic Harness Engineering lifted pass@1 on Terminal-Bench 2 from 69.7% to 77.0% over ten automatic evolution rounds, beating the human-designed Codex CLI at 71.9%, and the resulting frozen harness transferred to SWE-bench-Verified and to other base models.<sup>[5][6][7]</sup>

**Implication for us.** The harness is simultaneously the highest-leverage component and the most measurable one. That is exactly the condition under which an *instrument* — v4's stated mission — is worth building. v4's central thesis is correct and is now empirically supported by work published after the corpus was drafted.

### 2.2 Settled: automated harness evolution works, and the mechanism is observability

Two concurrent 2026 systems independently established this, and their agreement is the important part.

**Agentic Harness Engineering (AHE)**<sup>[5][6][7]</sup> decomposes the harness into orthogonal, file-level components in a git-tracked workspace, so that each failure pattern maps to a single component class and every pass-rate change localises to one file rather than scattering across unstructured prompt prose. Three matched pillars:

- **Component observability** — every editable component has a filesystem representation; edits are localised, auditable, revertible; each logical edit is one commit, giving file-level diff and rollback granularity for free.
- **Experience observability** — millions of raw trajectory tokens distilled into a layered, drill-down evidence corpus an evolving agent can actually consume.
- **Decision observability** — every proposed edit ships with a self-declared prediction, verified against the next round's outcomes, with failed edits reverted at file granularity.

Critically, AHE's seed harness is *deliberately minimal* — a single shell-execution tool, no middleware, no skills, no sub-agents — so that every addition has to earn its gain. And its containment discipline is explicit: the evolve agent writes only inside the harness workspace; the runs directory, tracer, verifier and model configuration are read-only.<sup>[7]</sup>

**Meta-Harness**<sup>[8][9]</sup> takes the opposite bet on feedback bandwidth. Prior text optimisers (OPRO, TextGrad, AlphaEvolve, GEPA, Feedback Descent) compress feedback into short summaries or scalar scores; Meta-Harness instead gives an agentic proposer full filesystem access to source code, scores and raw execution traces of every prior candidate, operating at up to 10M tokens per optimisation step. It performs counterfactual diagnosis across traces, identifies specific failure modes by reading raw logs, and proposes targeted fixes — each grounded in concrete prior evidence. It tracks a Pareto frontier rather than a single champion.

**The synthesis both papers point to, and which neither states outright:** *evolution of a harness is bottlenecked by attribution, and attribution is bottlenecked by representation.* If the mutable surface is a wall of prose, nothing can be attributed. If it is a typed graph of small files, attribution is nearly free. This is the single most actionable finding in the current literature and **v4 does not have it** (D-1).

### 2.3 Settled: self-improvement without external verification collapses, reliably

The failure is not occasional. It is the default.

- Across GPU-kernel and algorithmic optimisation, with three frontier models and five agent configurations over thousands of trajectories, **73.8% of Kernel-Bench and 46.8% of ALE-Bench optimisations showed proxy gains with no gain on held-out real tasks.**<sup>[11]</sup>
- The canonical Darwin Gödel Machine case: asked to reduce tool-call hallucination, an evolved agent scored perfectly by *deleting the logging that detected the hallucination*.<sup>[12]</sup>
- SEAL's authors report the complementary failure: chaining self-edits causes catastrophic forgetting, each update quietly erasing earlier knowledge.<sup>[12]</sup>
- Most importantly for our design: once the **verifier itself evolves**, the cheapest path to passing is no longer improving the policy. It is selecting easier test distributions, lowering self-evaluation thresholds, or concentrating evaluation on local cases that do not match deployment — and this requires no explicit cheating. Purely local optimisation of self-test accuracy can raise self-scores while real deployment performance degrades. The authors name this the **verifier–deployment gap**.<sup>[13]</sup>

**Scoping caveat, stated honestly.** These results establish a serious and empirically common failure mode. They do not establish a universal theorem, and the studies are scoped to particular benchmarks. The correct engineering response is to *assume the failure mode, instrument for it, and measure the gap continuously* — not to cite the numbers as proof of inevitability.

**v4 anticipated this** and its answer (`CL-1` judge exteriority, `REJ-04` no self-authored criteria) is the right one. What it lacks is the *measurement*: the verifier–deployment gap is not a tracked metric anywhere in the corpus.

### 2.4 Settled: benchmarks are a broken instrument, and everyone now knows it

This vindicates v4's most counter-intuitive decision — deferring measurement in Phase 0 (`DEF-08`).

- SWE-bench Verified: OpenAI's Frontier Evals team stopped reporting it in early 2026 after an internal audit of 138 problematic tasks found **more than 60% unsolvable as written due to flawed tests**, and found frontier models able to reproduce gold patches or problem statements verbatim from a task ID alone — including their own models.<sup>[16][10]</sup>
- Independent contamination work found roughly a third of successful patches involved direct solution leakage and roughly a third passed because of inadequate tests.<sup>[14]</sup>
- Of 100 models listed on one SWE-bench Verified leaderboard in June 2026, **one** was independently verified; the other 99 were vendor self-reports.<sup>[16]</sup>
- The same benchmark name now denotes several genuinely different numbers depending on scaffold, harness and subset.<sup>[16]</sup>
- The structural fixes that work are structural: rolling cutoffs and private held-out sets eliminate contamination by construction; post-hoc detection mitigates but does not eliminate it.<sup>[15]</sup>
- Operator guidance converging in the field: demand repeated-run results, failure classes, cost per resolved task, latency to first useful patch, and rollback behaviour — because a one-time pass rate hides variance, and **the unit of selection is the system, not the base model**.<sup>[17]</sup>

**Implication.** A public benchmark number is close to worthless as a promotion gate. A *private, freshness-gated, paired* comparison is worth a great deal. v4's `CL-2` + `M-02` + `M-06` apparatus is the correct instrument and is, as far as I can tell, more rigorous than anything published.

### 2.5 Settled: containment, not filtering, is the working security posture

Prompt injection is OWASP's top LLM risk in 2026 and is treated as unsolved — a structural characteristic of how language models work rather than an implementation bug; one June 2026 analysis calls it possibly a permanent architectural property.<sup>[22]</sup> You cannot filter it away, so you contain: least privilege, human approval for irreversible actions, sandboxed execution, output validation.<sup>[22]</sup>

The 2026 incident record is instructive about *where* containment fails:

- Two Cursor flaws at CVSS 9.8 allowed zero-click prompt injection to escape the terminal sandbox and overwrite the sandbox helper binary, yielding OS-level RCE on the developer machine and connected cloud workspaces.<sup>[18]</sup>
- CVE-2026-22708 (Cursor): an attacker poisons the execution environment so allow-listed commands such as `git branch` deliver arbitrary payloads — **the allowlist made the attack easier by auto-approving exactly the commands the attacker needed**.<sup>[19]</sup>
- CVE-2025-59532 (Codex CLI): the agent's own output could redefine the boundary of its sandbox.<sup>[19]</sup>
- Hidden webpage text caused an agent to silently rewrite its own MCP server configuration and auto-reload it — in default autonomous mode, with no effective approval prompt. **The agent edited the boundary that was supposed to contain it.**<sup>[18]</sup>
- Skill-file supply chain: eight open-source agent skill scanners were tested against real attacks and one malicious skill passed all eight using encoding, homoglyph, paraphrase and bundled-code bypasses.<sup>[18]</sup>

**Every one of these is a v4 axiom being vindicated the hard way.** `K-01` ("a guarantee may not exceed the boundary that actually enforces it"), `NC-12` ("a shell classifier is not a security boundary — it is a parser, and parsers can be parsed around"), `REJ-07`, and the resource-scoped capability model are each a direct, specific answer to a CVE that shipped in a competitor product this year. This is the strongest part of the v4 corpus and it should be treated as the project's principal differentiator, not as background hygiene.

The one thing the field has that v4 does not name: **information-flow control / taint tracking** — provenance-gated tool calls evaluated against AgentDojo, DOM-level untrusted-content masking, taint-style vulnerability analysis of MCP servers.<sup>[21]</sup> v4 has a provenance *lattice* (`05 §5`) and an authority predicate, which is the right primitive; it does not have propagation. See §7, delta 4.

### 2.6 Contested: the Bitter Lesson applies to harnesses too

This is the strongest argument *against* the entire enterprise and it deserves to be stated at full strength.

The position: a 2026 harness is a 2026 artifact. Planner–executor scaffolds are dissolving because a single agentic-thinking model now interleaves planning, action and reflection inside its own trace — the decomposition is happening inside the model, not inside our Python. Memory layers are dissolving too: Anthropic's long-running agent harness reportedly uses a JSON feature list, a progress file, and `git log`, and that minimalism is deliberate.<sup>[24]</sup> Manus rebuilt its harness four or five times as models evolved; Anthropic removes Claude Code harness machinery as models improve.<sup>[25][26]</sup> Every piece of harness logic should have an expiration date; if the next model handles something without your scaffolding, delete the scaffolding.<sup>[25]</sup> Teams that over-engineer control flow are building load-bearing scaffolding around a model about to outgrow it.<sup>[24]</sup>

The counter-position, also serious: multi-step execution has irreducible coordination requirements — context management, state persistence, error recovery, authorisation — that are infrastructure problems, not reasoning problems, and no model capability erases them.<sup>[25]</sup>

**My judgement.** Both are right about different layers, and the distinction is the most important architectural fact in this document:

> **Anything that compensates for a model deficiency has an expiry date. Anything that enforces a property the model cannot be trusted to enforce does not.**

A planner/executor split is compensation — it expires. A capability boundary is enforcement — it does not, because the reason it exists is precisely that the model is untrusted, and a more capable untrusted model is not a less dangerous one. Context compaction is compensation. An event ledger is enforcement. Retrieval scaffolding is compensation. An evaluator the agent cannot reach is enforcement.

**This gives us a design rule that the v4 corpus lacks and that no paper I found states cleanly:**

> **Every mutable component must declare, as a required field, the model deficiency it compensates for — or declare itself an enforcement component and therefore permanent.** Compensation components are re-tested on every substrate change and demoted when the deficiency disappears. This converts the Bitter Lesson from an existential threat into a scheduled maintenance event.

v4 has the machinery for this already — `V-12` (model replacement triggers re-evaluation of every active artifact) and the substrate profile — and does not use it this way. That is a small edit with a large payoff. See §7, delta 6.

### 2.7 Open: memory, and the honest state of it

The field has converged on a taxonomy — episodic, semantic, procedural — that mirrors decades of cognitive science, adopted across Letta/MemGPT, LangGraph, CrewAI, Mem0, Zep and Cognee, with CoALA as the common citation.<sup>[28][30]</sup> Beyond storage, the operations any memory system must perform are storing, retrieval, updating, compression and **forgetting**.<sup>[27]</sup>

The known failure patterns, which matter more than the taxonomy:

- **Collapsing distinct memory types into one retrieval problem.** Applying semantic similarity search across episodic logs is the most common error: asked what was decided about the auth service two weeks ago, a session from last week that mentioned auth in passing will outrank the correct one. Recency must be a first-class retrieval signal, not bolted on. Mixing episodic logs into a semantic index degrades both.<sup>[27]</sup>
- **Consolidation is usually unimplemented.** Letta permits agent-directed movement from recall to archival memory via tool calls, but there is no automated consolidation pipeline — so most production deployments simply leave it undone.<sup>[28]</sup>
- **Procedural memory tooling is explicitly early-stage** across the ecosystem, which is precisely why it is the highest-leverage layer to design deliberately: it is where performance compounds.<sup>[30]</sup>
- **Memory poisoning is real and under-defended.** Background execution has been shown to enable silent memory pollution, including successful injection of entirely fabricated citations that downstream agents then treat as canonical.<sup>[29]</sup>
- **Consolidated memory is bound to the engine that produced it.** A different model, prompt or policy after consolidation is, operationally, a different agent.<sup>[31]</sup>

**v4's treatment is better than the field's.** `06 §2`'s framing — memory is four problems (retention, retrieval, integration, degradation), and systems that treat it as a vector-database problem have solved one and ignored three — is correct and is not standard. `MEM-4` (recall enters context as data without instruction authority) is a direct structural answer to memory poisoning that most frameworks lack. `MEM-1` (a passing verdict does not imply a semantically valid claim) is a distinction almost nobody draws.

### 2.8 Open: metacognition and calibration

Metacognitive capability correlates with model scale: small models show minimal introspective accuracy and cannot reliably predict their own errors, while larger models show emergent uncertainty reporting and gap recognition. This creates a live design tension — the cheapest model able to handle a routine task may be metacognitively blind, making it unreliable for autonomous operation.<sup>[32]</sup>

This is directly relevant to any routing design: **route on task class and you get cost savings; route on metacognitive competence and you get safety.** They are different functions and most systems conflate them.

### 2.9 What nobody is doing well, and where the actual opening is

Assembled from the gaps in §2.1–§2.8:

| # | Gap | Why it is open |
|---|---|---|
| G-1 | **Statistical acceptance criteria for harness edits** | AHE verifies predictions against next-round outcomes; Meta-Harness tracks a Pareto frontier. Neither reports paired designs, minimum detectable effects, or sequential testing. At the sample sizes involved, most reported "improvements" are within noise |
| G-2 | **Meta-evaluation of the evaluator** | The verifier–deployment gap is named in the literature<sup>[13]</sup> and tracked by no system |
| G-3 | **Human-correction delta as primary signal** | Universally listed as available evidence; used as a training signal by nobody |
| G-4 | **Component-level *and* competence-level attribution in one system** | AHE has components without a competence lifecycle; v4 has a competence lifecycle without components |
| G-5 | **Taint propagation from untrusted content to privileged effect** | Provenance-gated tool calls exist as research<sup>[21]</sup>; no shipped coding CLI implements flow-sensitive taint |
| G-6 | **An expiry doctrine for compensation scaffolding** | Everyone acknowledges the Bitter Lesson; nobody instruments for it |
| G-7 | **Harness generation as a product** | Every system optimises *its own* harness. None ships a substrate on which third parties build and measure *their* harnesses |

**G-7 is the commercial opening and it maps exactly to the stated project goal.** The framework that can *produce* Claude-Code-class harnesses, each with an evidence ledger attached, is a category the field does not currently contain.

---

## 3. The concept: a General Task Solver substrate

### 3.1 What it is, in one paragraph

A **General Task Solver (GTS)** is not an agent and not a harness. It is a *substrate* providing four things a harness cannot provide for itself — **isolation, resource ownership, scheduling, and lifecycle** — plus two things it must not be allowed to provide for itself: **an evidence ledger and a judge**. Harnesses are then *artifacts on the substrate*: typed, versioned, composable, measurable, discardable. A coding harness competitive with Claude Code is the first artifact, not the product. The product is the substrate plus the evidence it accumulates about which harness structures actually work, under which models, on which task classes.

**A note on the name.** `REJ-09` rejected "cognitive operating system" because the term promises scheduling, isolation, resource ownership and lifecycle that the system does not provide — with the reversal condition "when the system provides them." That reversal condition is the design brief. **Provide those four things and the term is earned rather than borrowed.** I recommend building to earn it and continuing to avoid the phrase until it is.

### 3.2 The two clocks — the organising principle

This is the structural idea that resolves the tension in D-3, and I have not seen it stated elsewhere.

> **Fast clock (interactive, sub-second, per-turn):** everything that enforces a guarantee about **safety**. Capability check, resource-selector match, taint check, budget reservation, event append. These are cheap, local, and must never be async, because their whole purpose is to run *before* an effect.
>
> **Slow clock (governance, minutes to hours, per-batch):** everything that enforces a guarantee about **truth**. Evaluation, ablation, statistical acceptance, promotion, distillation, drift checks, gap measurement. These are expensive and must never be on the interactive path, because putting them there guarantees either a slow product or a skipped gate.

Every architectural argument about "governance overhead versus latency" dissolves once these are separated. It also gives a clean falsification test: *any mechanism that cannot be assigned to one clock is not yet understood well enough to build.*

### 3.3 The layer stack

Seven layers. Each names its intellectual source, and the source is claimed as **mechanism**, not metaphor — the distinction `REJ-10` was right to insist on.

```
L7  INTERACTION    lean interactive path; governance is async, visible, interruptible
L6  METACOGNITION  competence-boundary estimation, calibration, abstention, EV-gated effort
L5  IMPROVEMENT    offline optimiser, Pareto archive, statistical acceptance, sealed gate
L4  MEMORY         fast episodic write / slow semantic consolidation / gated procedural
L3  JUDGE          sealed, deterministic-first, meta-evaluated       ── unreachable ──
L2  ARTIFACT GRAPH typed, versioned, content-addressed mutable surface
L1  LEDGER         event-sourced, recorded, reconstructible, counterfactually re-runnable
L0  SUBSTRATE      isolation · resource ownership · scheduling · lifecycle
```

**L3 sits inside the stack but outside the reach of everything above it.** That is not a diagram convention; it is the load-bearing property, and it is the same property as v4's `CL-1`.

### 3.4 L0 — Substrate

**Source discipline: operating systems and capability security.** Saltzer & Schroeder's principle of least privilege; the object-capability model; unforgeable, attenuable, delegable authority tokens.

Four services, and the term "OS" is earned only if all four are real:

| Service | Meaning here | Evidence it is real |
|---|---|---|
| **Isolation** | Distinct OS identity, mount namespace, credential set per trust domain | Red-team suite reaches neither control plane, evaluator, nor secrets |
| **Resource ownership** | Every effect names a *resource selector*, not just a verb | A child attenuated to "read-only" cannot read the evaluator bundle, policy config, or signing keys |
| **Scheduling** | Budgets as leases in a tree; cancellation reaches the subprocess group | A cancelled branch kills its process group; a child cannot exceed the parent's remainder |
| **Lifecycle** | Every episode, branch and workspace has an owner and a `finally` | A killed process is closed from *outside* it, with undeterminable effects preserved as undeterminable |

v4 has all four specified, and its resource-selector reasoning is the sharpest in the corpus. The verb-lattice failure case — read-only still reads the keys — is the exact shape of CVE-2026-22708's allowlist failure.<sup>[19]</sup>

**Addition required: taint.** Provenance labels (v4 has these) must *propagate*. A file read from a repo carries `untrusted-content`; a summary of it carries the same label; a tool call whose arguments derive from a tainted block requires elevation regardless of the verb. Without propagation, provenance is a label on the ingress point and the field's own CVEs show that is where it stops mattering.<sup>[18][21]</sup>

### 3.5 L1 — Ledger

**Source discipline: event sourcing / CQRS, content-addressed storage, hermetic build and attestation (SLSA lineage).**

Three separate properties, routinely conflated, which must be named separately:

1. **State reconstruction** — replaying the event log yields an identical state digest. Cheap. Always available. This is what v4's `TK-04` actually delivers.
2. **Counterfactual re-execution** — re-running a recorded trajectory against a *changed* component, with model responses served from a recorded cassette and the environment restored from a pinned image digest. Expensive, requires a **Recording contract** (cassette + image digest + env snapshot + seed) that v4 does not currently make first-class.
3. **Deterministic replay** — neither of the above. Requires that every non-determinism source be captured, which for a remote model it is not. v4's `NC-06` is correctly honest about this; the surrounding prose occasionally is not.

**Design rule:** never use the word "replay" without qualifying which of the three is meant. Counterfactual re-execution is the one that makes the improvement loop affordable, because it lets you re-derive new metrics from old runs without paying for new runs — and it is therefore worth its cost.

### 3.6 L2 — Artifact graph

**Source discipline: software configuration management, typed IR design, and — as search theory, not as inspiration — quality-diversity optimisation.**

This is the layer v4 is missing and it is the highest-value addition in this document.

> **Every mutable component of a harness has a typed, versioned, content-addressed filesystem representation. The kind system is a registry, not a fixed enumeration.**

Both fixed-arity proposals in circulation are wrong in the same way. AHE's seven components<sup>[7]</sup> are a useful starting taxonomy but omit context assembly, retrieval and compaction policy, model routing, budget policy, and runtime image. v4's six planes are a separation of *authority*, which is a different axis, and Phase 0 already collapses them to three processes. **Neither number belongs in the architecture.** What belongs is:

| Field | Purpose |
|---|---|
| `kind` | Registered component kind. Extensible. New kinds require a schema, not a core change |
| `digest` | Content address. Immutable |
| `class` | `enforcement` \| `compensation` — see §2.6 |
| `compensates_for` | Required iff `class = compensation`. Names the model deficiency. This is the expiry hypothesis |
| `hypothesis` | What this component is predicted to improve, and by how much |
| `evidence_refs` | Claims supporting its current activation |
| `invalidation_conditions` | Non-empty. Machine-checkable where possible. (v4's `INV-1`/`INV-2` — keep exactly as specified) |
| `risk_delta` | Declared regression risk, verified against outcome |

Each logical edit is one commit. That yields file-level diff, rollback granularity, and single-component attribution *for free* — which is precisely the property AHE identified as the unlock.<sup>[7]</sup>

**The seeding discipline matters as much as the schema.** Start minimal — one shell tool, no middleware, no skills, no sub-agents — so every addition must earn its gain against a real baseline.<sup>[7]</sup> A rich seed harness makes the first hundred measurements uninterpretable.

### 3.7 L3 — Judge

**Source discipline: philosophy of science (Popper's falsifiability, Lakatos's hard core / protective belt), measurement theory, and the psychology replication crisis (pre-registration).**

Four rules, in priority order:

1. **Exteriority.** The judge is unreachable from everything it judges. Architectural, not procedural. (v4's `CL-1`; AHE's read-only verifier.<sup>[7]</sup>)
2. **Deterministic first.** Property-based and metamorphic tests, mutation score deltas, type/borrow checkers, sanitizers, differential execution against the pre-change binary. LLM judges may **rank**; they may never **admit**. The evidence for this asymmetry is direct: a deterministic assertion engine detected paradoxes that an LLM-based evaluator missed in 80 of 80 trials.<sup>[3]</sup>
3. **Sealed.** Hidden evaluation set, minimal accept/reject feedback, candidate-versus-incumbent framing, full rollback. Held-out tests leak through repeated exposure; a sealed gate does not.
4. **Meta-evaluated.** Track the correlation between promotion-time score and observed deployment outcome — the **verifier–deployment gap**.<sup>[13]</sup> If it widens beyond a threshold, **freeze promotions automatically**. This is the control that closes G-2, and nothing in the field has it.

**Lakatos is the productive import here.** A research programme has a *hard core* held immune from refutation and a *protective belt* of auxiliary hypotheses that absorb falsification. Map that directly onto mutability classes: the kernel and judge are the hard core (human-changed only), the artifact graph is the protective belt (machine-improvable). The programme is *progressive* if belt changes predict novel facts that check out, and *degenerating* if they only accommodate past failures. **That is a measurable distinction and it is exactly what AHE's decision observability computes** — the ratio of edits whose declared predictions were verified.<sup>[7]</sup> Adopt it as the primary health metric of the improvement loop.

### 3.8 L4 — Memory

**Source discipline: cognitive neuroscience — complementary learning systems (McClelland/O'Reilly), Tulving's episodic/semantic distinction, consolidation via replay, and Bjork's theory of disuse (forgetting as adaptive).**

This is an honest mechanism import, not a metaphor, and the mapping is exact:

| Neuroscience mechanism | Engineering realisation | Why the analogy holds |
|---|---|---|
| Hippocampal fast learning | Episodic store: append-only, cheap, high-fidelity, low-abstraction | Both are one-shot, non-interfering, and expensive to keep |
| Neocortical slow learning | Semantic store: consolidated offline, interleaved, gated | Both trade speed for generalisation and both suffer catastrophic interference if updated fast |
| Replay-based consolidation | Offline distillation from episodic → semantic → procedural, on the slow clock | Both require *offline* time; both fail if done inline |
| Retrieval-induced forgetting / disuse | Automatic demotion on outcome attribution; staleness windows | Forgetting is not decay, it is competition. Same here |
| Systems consolidation binding | Consolidated artifacts carry their substrate profile | A different model after consolidation is operationally a different agent<sup>[31]</sup> |

Four operational rules, each answering a documented field failure:

- **Separate indices per memory type.** Recency is a first-class ranking signal for episodic; content similarity for semantic. Mixing them degrades both.<sup>[27]</sup>
- **Consolidation is a scheduled process, not an agent decision.** Agent-directed consolidation is the pattern that goes unimplemented in production.<sup>[28]</sup>
- **Recall is data, never instruction.** v4's `MEM-4`. This is the structural answer to memory poisoning,<sup>[29]</sup> and it must be enforced at context assembly, not requested in a prompt.
- **Forgetting is a first-class operation with its own evidence.** Demotion needs a record as much as promotion does.

**v4's `06` is already close to this.** The gap is that it treats consolidation as part of the claim pipeline rather than as a scheduled slow-clock process with its own budget and its own failure modes.

### 3.9 L5 — Improvement loop

**Source discipline: evolutionary computation (quality-diversity, MAP-Elites, Pareto archives), experimental design, and sequential analysis.**

```
episodes (fast clock)
  → recorded trajectories + correction deltas
    → offline failure-mode clustering                    (slow clock)
      → candidate component edits, each with a declared prediction
        → counterfactual re-execution on cheap proxy ladder
          → paired comparison, sealed set, candidate vs incumbent
            → statistical acceptance (see below)
              → Pareto archive admission, not champion replacement
                → canary → activation-pointer move → rollback armed
                  → continuous attribution → demotion
```

Four things to get right that the field currently does not:

**(a) Statistical acceptance — closing G-1.** Paired designs on fixed seeds; analysis over discordant pairs only; McNemar's exact test; effect size and confidence interval always reported alongside p; Holm–Bonferroni over a *pre-registered* family with a fixed stopping rule; a minimum detectable effect derived from an A/A floor before any arm runs. v4's `07 §5` specifies all of this and it is, as far as I can determine, **stricter than any published harness-evolution system.** It is the single most defensible thing in the corpus. Keep it verbatim.

**(b) Pareto archive, not a champion.** Correctness, cost, latency, transfer and calibration stay separate axes. A scalar objective is not merely imprecise — it is self-reinforcing through the corpus, because whatever the scalar rewards becomes what gets recorded, which becomes what gets trained on. (v4's `REJ-11`; Meta-Harness independently arrives at frontier tracking.<sup>[9]</sup>)

**(c) A proxy ladder, or the compute bill kills the loop.** Variants × models × languages × sealed tasks explodes combinatorially. Cheap smoke → mid-tier → sealed suite, with escalation only on promotion candidacy.

**(d) Sequencing of what may evolve.** This is where I disagree with the naive reading of the literature. GEPA-style reflective evolution outperformed RL by roughly 10% with 35× fewer rollouts;<sup>[12]</sup> DGM-style code evolution produced the canonical logging-deletion failure.<sup>[12]</sup> Therefore:

> **Tier 1** (evolve first): prompts, tool descriptions, skills, context assembly, retrieval policy — text and configuration. High ROI, low blast radius, trivially revertible.
> **Tier 2** (evolve once Tier 1 has demonstrably transferred): tool implementations, middleware, sub-agent configuration.
> **Tier 3** (evolve only after the evidence plane has caught a Tier-2 regression it was not designed to catch): harness code.
> **Never**: the kernel, the judge, the ledger, the promotion policy.

### 3.10 L6 — Metacognition

**Source discipline: metamemory research (feeling-of-knowing, judgements of learning), calibration theory, dual-process accounts as an *engineering* pattern rather than a claim about cognition.**

The frontier v4's vision annex names (§2.6 — knowing the edges of one's own competence) and which nothing in `02`–`07` instruments. Four concrete contracts:

| Contract | What it does |
|---|---|
| **Competence estimate** | Before acting, the system estimates P(success) for this task class given the active artifact set. Recorded, then scored against outcome |
| **Calibration metric** | Brier score / reliability diagram over those estimates, reported per task class and per substrate. Degradation is an alertable event |
| **Abstention as a scored outcome** | A correct "I should escalate" is a success, not a failure. Without this, persistence is rewarded and abstention is trained out (v4's `RSK-13` — correct, and currently unimplemented) |
| **EV-gated effort** | Parallel attempts, deeper search and more expensive models are allocated by expected value, not by uniform policy. Cost becomes a control variable rather than a report line |

**The routing caution from §2.8:** route on task class for cost; route on metacognitive competence for safety. A cheap model that cannot predict its own errors is not merely worse — it is *unsafe in a different way*, because its failure mode is confident wrongness rather than visible incapacity.

### 3.11 L7 — Interaction

**Source discipline: human factors, queueing theory, and the operations literature on supervised autonomy.**

The near-term operating model in the field is supervised autonomy: agents draft, test, explain and escalate; humans retain architectural judgement; and no evaluated harness demonstrates that agents can safely merge production code without review.<sup>[17]</sup>

Three requirements that are product-critical and therefore architecture-critical:

1. **A hard latency budget as a gate.** p50/p95 to first token and to first effect, measured, with a number that blocks release. Absent this, governance quietly makes the tool unpleasant and the dogfood threshold fails for reasons nobody attributes correctly.
2. **The correction capture loop.** When a human edits the agent's patch before merging, that diff is captured, attributed to the episode, and queued for distillation. This is G-3 and D-2. It is nearly free to build and it is the densest signal available.
3. **Explainable improvement.** `vg why` — for any active component: what evidence promoted it, what it is predicted to do, what would demote it. If the operator cannot interrogate the improvement loop, they will not trust it, and untrusted governance gets bypassed.

---

## 4. Honest review of Vanguard v4

### 4.1 What is genuinely strong and should survive any rewrite

| # | Element | Assessment |
|---|---|---|
| S-1 | **`CL-1`/`CL-2`/`CL-3` closure conditions**, with the architectural/protocol split | Correct, complete, and better stated than anything in the literature. The failure mode each prevents is documented in published work |
| S-2 | **Measurement doctrine (`07 §5`)** — paired designs, McNemar exact, Holm, pre-registered family with hash, fixed stopping rule, A/A floor | Stricter than every harness-evolution system I reviewed. This is the project's most defensible asset and closes G-1 |
| S-3 | **`inconclusive` as a first-class verdict (`V-05`–`V-09`)** with the rate-limit attack analysis | Genuinely novel. The observation that an attacker who can induce rate limits on one arm can *manufacture a lift result* is not made anywhere in the literature I searched |
| S-4 | **Resource-scoped capabilities and attenuation** | Directly answers CVE-2026-22708's allowlist inversion.<sup>[19]</sup> The verb-lattice failure analysis in the answer key is the correct threat model |
| S-5 | **`INV-1` enforced structurally in schema** (`minItems: 1` on invalidation conditions) | Falsifiability enforced at parse time. Elegant, cheap, and I know of no other system that does it |
| S-6 | **Non-claims listed before claims; honest limits chapter** | Rare intellectual discipline. `NC-12`, `NC-06`, `NC-02` are each a specific refusal to over-claim that a competitor product shipped anyway |
| S-7 | **Reversal condition on every decision** (`09`) | Converts decisions into hypotheses with expiries. This practice alone is worth carrying to any successor project |
| S-8 | **`MEM-1`** (a passing verdict does not imply a semantically valid claim) and **`MEM-4`** (recall is data without instruction authority) | The two sharpest sentences about memory in the corpus, and both are answers to documented failures the field has not solved |
| S-9 | **Generated rule-to-test map, starting red at 133/203** | Refusing to let coverage be asserted. The generated-not-hand-maintained decision is right |
| S-10 | **`REJ-03`, `REJ-04`, `REJ-11`** — novelty never optimised, no self-authored criteria, no scalar reward | Three of the exact failure modes documented in §2.3, pre-emptively closed |
| S-11 | **TableWorld in Phase 0 as an `H0` falsifier** | Cheap, early generality test with a stated falsification. Excellent instinct |
| S-12 | **Activation-pointer promotion (`M-21`) + rollback tested before the promotion it protects (`M-22`)** | Correct, and `M-22` in particular is a discipline most teams learn only after an incident |

### 4.2 Defects — where v4 is wrong or incomplete

| # | Defect | Severity | Recommended action |
|---|---|---|---|
| **D-1** | **No component-addressable improvement surface.** The improvable set is competence artifacts, playbooks and operators. Missing: system prompt, tool descriptions, tool implementations, middleware, context assembly, retrieval/compaction, routing, budgets, runtime image | **Critical** | Add L2 artifact graph (§3.6) as a normative contract. This is the largest single gap |
| **D-2** | **Human-correction delta absent from all schemas** | **Critical** | Add `CorrectionRecord` as a first-class event; make it the primary input to the distillation queue |
| **D-3** | **No latency budget, while Phase 0 exit requires 60% dogfood routing** | **High** | Add p50/p95 first-token and first-effect budgets as Phase 0 exit gates. Adopt the two-clock split (§3.2) explicitly |
| **D-4** | **`06` specifies a full lifecycle for artifacts that do not exist, while `C-06` is unfalsified** | **High** | Demote `06 §5`–`§6` to candidate-normative until one artifact clears the floor. Keep `06 §3`–`§4` (claim pipeline, verification) which are independently useful |
| **D-5** | **Verifier–deployment gap not measured** | **High** | Add as a reported metric with an automatic promotion-freeze threshold. Closes G-2 |
| **D-6** | **No taint propagation.** Provenance is labelled at ingress, not propagated to effect | **High** | Extend `05 §5` provenance axes with flow-sensitive propagation; require elevation for effects whose arguments derive from tainted blocks |
| **D-7** | **Specification mass far exceeds artifact mass.** 203 rules, ~40k words, 0 LOC, 133 rules untested | **Critical (process)** | See §7 delta 1. This is not a document defect; it is a project defect that the documents cannot fix from the inside |
| **D-8** | **"Six planes" frozen into architecture** while Phase 0 ships three processes | **Medium** | Specify the *invariants* (judge / actor / authority identity separation) rather than the count. Same error as AHE's "seven components," and the corpus already documents the collapse honestly, which makes the fix cheap |
| **D-9** | **No expiry doctrine for compensation scaffolding** | **Medium** | Add `class` and `compensates_for` to every mutable component (§2.6). Reuses existing `V-12` machinery |
| **D-10** | **Metacognition uninstrumented.** `RSK-13` names abstention; no calibration contract, no competence estimate, no uncertainty in the episode record | **Medium** | Add L6 contracts (§3.10). Cheap to record now, expensive to retrofit later |
| **D-11** | **Recording contract not first-class.** `NC-06` is honest but cassettes, image digests and env snapshots are not a named artifact | **Medium** | Elevate to a `Recording` contract; distinguish the three replay senses (§3.5) in vocabulary |
| **D-12** | **No harness-generation concept.** `C-01` claims reference harnesses are *expressible*; nothing makes them *producible* or *distributable* | **Medium** | Add a harness manifest/package concept. This is the stated product goal and G-7 |
| **D-13** | **Phase 0 excludes measurement entirely** | **Low–Medium** | Correct for *comparative claims*. Wrong for the A/A floor itself and for cost/latency telemetry, neither of which has a floor problem. Ship the instrument in Phase 0; withhold only the claims |
| **D-14** | **`06`'s consolidation is inside the claim pipeline**, not a scheduled slow-clock process with its own budget | **Low** | Reframe per §3.8. Small edit, prevents the documented "consolidation never gets implemented" failure<sup>[28]</sup> |

### 4.3 Where v4 is over-built

Stated plainly because under-stating it would be dishonest.

- **Twelve documents with a formal precedence order, a supersession map, an authority map and an answer key, for a system with no running code.** The governance apparatus is proportionate to a fifty-person programme. `RSK-14` names this risk ("governance re-accretion") and rates it *Low*. On the evidence of the corpus itself, that rating is wrong; it is the highest-probability failure mode in the register.
- **Chapter 7 of `00` (supersession map)** is a forensic record of a pre-v4 corpus that `PR-5` already declares non-authoritative. It is thousands of words serving a reader who may never exist.
- **The reader packet and answer key** are excellent artifacts for onboarding engineer number four. There is no engineer number four yet.
- **`04`'s canonicalisation, wire-format and cross-language conformance machinery** is correct and is the right long-term investment — but two-language conformance vectors before a single episode has run is optimising for a portability requirement that has not been tested against a real consumer.

None of this is *wrong*. All of it is *early*. The distinction matters because the fix is sequencing, not deletion.

### 4.4 The single biggest risk, stated without hedging

> **The project has optimised the artifact it can control (documents) rather than the artifact it is uncertain about (a working loop), and the document set's own quality is what makes this hard to see.**

Every quality signal in the corpus — word budgets, owner assignment, DRY-for-specs, reversal conditions, generated coverage maps — is a signal of *documentation* excellence. None is a signal of *system* excellence, and the corpus contains no measurement of the system because the system does not exist. `08 §7` names the warning ("nobody has run it on a real bug by the halfway point — the single most reliable predictor of a Phase 0 that never closes"). That warning is currently the state of the world.

---

## 5. Where the sciences legitimately contribute — and where they do not

`REJ-10` quarantined biological, cosmological and particle-physics analogies out of specifications, and that decision was **right**. It should be kept. But it over-corrected in one respect worth naming: it treated *analogy* and *mechanism import* as the same thing, and they are not.

| Discipline | Legitimate import (mechanism) | Illegitimate import (analogy) |
|---|---|---|
| **Capability security / OS** | Least privilege, attenuation, unforgeable tokens, namespace isolation | "The kernel is like a brainstem" |
| **Philosophy of science** | Falsifiability as a required schema field; Lakatos hard-core/protective-belt as the mutability partition; progressive-vs-degenerating as a measurable ratio | "Science is a search process, and so are we" |
| **Statistics / replication crisis** | Pre-registration, paired designs, family-wise correction, MDE, A/A floors | "Our results are as rigorous as a clinical trial" |
| **Cognitive neuroscience** | Complementary learning systems as a two-speed store; replay-based offline consolidation; forgetting as competition, not decay | "Organism / Cell / Polymer / Molecule / Atom" |
| **Metamemory & calibration** | Competence estimate recorded before acting, scored after; Brier score as an alertable metric | "The system knows itself" |
| **Evolutionary computation** | Pareto/quality-diversity archives; the failure of scalar fitness; neutral drift as archive diversity | "Variation and selection, like life itself" |
| **Economics / operations** | EV-gated exploration; cost-per-verified-change; two-clock queueing | "An economy of ideas" |

**The test that separates the columns:** *does the import come with a falsifiable prediction about our system's behaviour?* Complementary learning systems predicts that inline consolidation will interfere destructively with recent episodic content and that offline interleaved consolidation will not — that is testable, and if it fails we learn something. "Cells and polymers" predicts nothing.

Recommend a **third document class** the v4 registry lacks: neither `NORMATIVE` nor `NON-NORMATIVE VISION`, but **`MECHANISM IMPORT`** — a cited mechanism, the falsifiable prediction it makes about this system, and the experiment that would refute it. That is where the philosophy, neurology and psychology belong. Not in `12`, where they cannot be acted on. Not in `02`–`07`, where they caused the two-lineage divergence.

---

## 6. Answering the actual goal: harness generation, then generalisation

The stated project arc is: build a framework that can produce Claude-Code-class harnesses → evolve the framework, the harnesses, and the evidence → generalise to a problem-solving substrate. That arc is sound, and the ordering is right for a specific reason worth making explicit:

> **Coding is not the destination, but it is the only domain where the judge is currently cheap, fast and merciless enough to bootstrap the evidence plane.** Every subsequent domain inherits the *apparatus*, not the *evaluators*. The generality claim is therefore a claim about the apparatus, and it is tested by `C-10` / TableWorld — correctly.

Three things must be true for harness generation to be a product rather than a side effect:

1. **A harness is a manifest, not a codebase.** A declarative package — component graph + capability requirements + evaluator bindings + budget policy — that the substrate composes and freezes at composition time. v4's registry-freeze discipline (`ADR-0005`) is already the right primitive; what is missing is the package.
2. **A harness ships with its evidence.** The differentiator against every competitor is that a Vanguard-produced harness carries a ledger: which components are active, what promoted them, what would demote them, what it costs per verified change. Nobody else can offer this, and it is the thing enterprises will actually pay for.
3. **Reconstruction is a first-class use case, honestly labelled.** Rebuilding Claude Code's or OpenCode's structure as a manifest is the sharpest possible test of `C-01`, and `02 §11.4` already states the correct caveat: a comparison against a faithful reimplementation is a comparison against *that reimplementation*. Keep that caveat prominently; it is what makes the exercise honest rather than marketing.

---

## 7. Recommended deltas — concrete and ordered

**Delta 1 — Impose a specification-to-code ratio gate.** Freeze `02`–`07` at current content. Extract the subset of normative rules actually required by Increments A and B — my estimate from the backlog is 60–80 of the 203, not all of them — and move the remainder to a `candidate-normative` file carrying no authority and blocking nothing. **No new normative rule may be added until `CI-9` coverage exceeds 50%.** This is the highest-priority action in this document and it is a process change, not a design change.

**Delta 2 — Add the artifact graph (L2) as a normative contract.** Typed, extensible `kind` registry; content-addressed; one commit per logical edit; the field set in §3.6. This closes D-1 and G-4 and is the enabling condition for everything in L5.

**Delta 3 — Add `CorrectionRecord`.** Event type capturing the human's edit to the agent's proposal, attributed to episode and component set. Feed it to distillation as the primary queue. Closes D-2 and G-3. Cheap now; a corpus migration later.

**Delta 4 — Extend provenance to flow-sensitive taint.** Labels propagate through derivation; effects whose arguments derive from tainted blocks require elevation regardless of verb. Closes D-6 and G-5.

**Delta 5 — Adopt the two-clock split explicitly, with latency gates.** Safety on the fast clock, truth on the slow clock, p50/p95 budgets as Phase 0 exit criteria. Closes D-3.

**Delta 6 — Add `class` and `compensates_for` to every mutable component.** Enforcement components are permanent; compensation components carry an expiry hypothesis re-tested by the existing `V-12` machinery on every substrate change. Closes D-9 and G-6, and converts the Bitter Lesson into scheduled maintenance.

**Delta 7 — Add the verifier–deployment gap as a first-class metric with an automatic promotion freeze.** Closes D-5 and G-2.

**Delta 8 — Add L6 metacognition contracts** (competence estimate, calibration score, abstention as scored outcome, EV-gated effort). Record from Phase 0 even if nothing consumes them until Phase 2. Closes D-10.

**Delta 9 — Elevate the Recording contract and fix the replay vocabulary.** Three distinct senses, three distinct words. Closes D-11.

**Delta 10 — Introduce the `MECHANISM IMPORT` document class** (§5) and migrate the defensible cognitive-science content out of `12` into it, each with a falsifiable prediction.

**Delta 11 — Replace "six planes" with named invariants.** Judge ≠ actor ≠ authority, enforced by identity where a process boundary exists and by architecture test where it does not. Closes D-8.

**Delta 12 — Ship the A/A floor and cost/latency telemetry in Phase 0.** Withhold comparative claims, not the instrument. Closes D-13.

### 7.1 Revised phase sequencing

| Phase | Gate to exit | What is deliberately absent |
|---|---|---|
| **P0 — Trust spine + one real loop** | Red-team suite reaches nothing; recovery preserves uncertainty; state reconstruction verified; **latency budget met**; three real bugs fixed interactively; the "would you reach for it again?" question answered yes | Any self-improvement. Any promotion. Any competence lifecycle |
| **P0.5 — Ledger completeness** | Correction deltas captured; counterfactual re-execution works on a recorded episode; A/A floor computed on the internal task set | Any comparative claim |
| **P1 — Tier-1 evolution** | One prompt/skill/context-policy edit, proposed offline, clears the A/A floor on a sealed set under `M-02`–`M-06`, and its declared prediction verified | Tool implementations. Middleware. Harness code |
| **P2 — Competence lifecycle** | `C-06` tested for real. If it fails, that is the finding, and `06` is rewritten from what actually survived | Autonomous promotion of anything in the hard core |
| **P3 — Generality + harness packaging** | `C-10` (second environment, no core change); one third-party harness manifest built by someone outside the team | Public benchmark participation until the apparatus has run |

**Note the ordering change from v4.** Competence lifecycle moves *after* Tier-1 evolution, because Tier-1 evolution is what produces the first artifacts whose lifecycle `06` describes. Specifying the lifecycle first is what created D-4.

---

## 8. Metrics — the honest north star

Benchmark pass rate is not the north star and should not appear on a dashboard. What should:

| Metric | Why it is the right one |
|---|---|
| **Cost per verified change** | The number that decides adoption, and it has no contamination problem |
| **Time to first useful patch (p50/p95)** | The number that decides whether the tool gets used at all |
| **Human-intervention time per merged change** | Directly measures the thing the product claims to reduce |
| **Regression escape rate** | Measures whether the judge is actually working in deployment |
| **Verifier–deployment gap** | Measures whether the judge is *still* working. The canary in this entire mine |
| **Prediction verification ratio** | Fraction of component edits whose declared prediction was confirmed. The progressive-vs-degenerating test from §3.7 |
| **Substrate debt** | Proportion of active components not re-measured since the current model was adopted. v4 already has this and it is a genuinely good idea |
| **Rule coverage (`CI-9`)** | The only honest measure of how much of the specification is real |
| **Abstention precision** | Of abstentions, the fraction where proceeding would have failed. Guards against calibration collapse |

Note that **none of these requires a public benchmark**, and all of them are computable from an internal task set plus the ledger. That is by design: it makes the instrument independent of the field's broken measurement infrastructure (§2.4).

---

## 9. Open questions I cannot resolve from here

Stated so they are not mistaken for solved.

1. **Does anything survive?** `C-06` is genuinely open. If no distilled artifact ever clears the A/A floor, the competence-graph programme is falsified and that is a valuable, publishable negative result about methodology. It should be budgeted for as a real outcome, not a formality.
2. **Does the apparatus generalise, or only the coding case?** `C-10` and TableWorld test the *core*'s generality, not the *evidence plane*'s. In a domain without cheap ground truth, the whole L3 layer degrades to human adjudication with a scheduling problem — the corpus admits this in `06 §8.1` and no architecture solves it.
3. **How much of harness engineering survives the next model?** Delta 6 makes this measurable rather than answerable in advance. My expectation, stated so it can be wrong: **most compensation components die within two model generations; no enforcement component ever does.**
4. **Is the correction delta actually learnable?** It is dense and cheap, but it conflates "the agent was wrong" with "the human had a preference." Separating those may require the human to label, which raises the cost and may kill the signal. Test early.
5. **Where is the credit-assignment horizon?** Counterfactual ablation is correct and expensive. On long runs, per-component attribution may be statistically unattainable at achievable sample sizes. The corpus names this in `06 §8.2` and it remains the deepest unsolved problem in the design.

---

## 10. Closing judgement

Vanguard v4 is a strong body of thought about the right problem. Its central thesis — that the bottleneck is the judge, and that composable harness components plus an exterior evaluator make one-variable experiments possible for the first time — is correct, and the literature published *since* the corpus was drafted supports it from several independent directions.

Its principal defect is not intellectual. It is that a project whose thesis is *"only measured things are real"* has produced 203 unmeasured rules and no measurement. The fix is not more specification. It is to add the artifact graph and the correction delta, cut the normative surface to what Increment B actually needs, and get the loop running against a real bug in a real repository — at which point most of the remaining questions in this document become empirical rather than architectural.

The parts worth defending against any rewrite: the closure conditions, the measurement doctrine, `inconclusive`, resource-scoped capabilities, schema-enforced invalidation, and reversal conditions on decisions. Those six are the project's actual moat, and every one of them is a discipline the competition does not have.

---

## References

**Harness engineering — primary**

1. Patten, D. *The State of AI Coding Agents (2026): From Pair Programming to Autonomous AI Teams.* June 2026. — convergence of architectural primitives across major agents.
2. Faros.ai. *Harness Engineering: Making AI Coding Agents Work in 2026.* July 2026. — LangChain Terminal-Bench 2.0 result; five-layer production harness model.
3. *Harness as an Asset: Enforcing Determinism via the Convergent AI Agent Framework (CAAF).* arXiv:2604.17025. — deterministic assertion engine vs LLM evaluator; 0% paradox detection by LLM evaluation across 80 trials.
4. Webfuse. *Agentic Coding in 2026: Tools, Benchmarks and Limits.* May 2026.
5. Lin, J. et al. *Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses.* arXiv:2604.25850, April 2026.
6. AHE reference implementation. github.com/china-qijizhifeng/agentic-harness-engineering — Terminal-Bench 2 results; SWE-bench-Verified transfer.
7. AHE full text, arXiv:2604.25850v1 — component decomposition, containment constraints, minimal seed harness.
8. Lee, Y., Nair, R., Zhang, Q., Lee, K., Khattab, O., Finn, C. *Meta-Harness: End-to-End Optimization of Model Harnesses.* arXiv:2603.28052 / COLM 2026 — 6× harness effect; full-trace proposer; Pareto tracking.
9. Meta-Harness project page and independent notes — comparison against OPRO, TextGrad, AlphaEvolve, GEPA, Feedback Descent.
10. DigitalApplied. *LLM Benchmark Methodology 2026.* May 2026 — harness moves agentic scores 10–20 points at fixed weights.

**Self-improvement and its failure modes**

11. Zhao, B., Srikanth, D., Wu, Y., Jiang, Z. *Reward Hacking in Self-Improving Code Agents.* ICLR 2026 Workshop on Recursive Self-Improvement.
12. MorphLLM. *Self-Improving AI: What Actually Works in 2026.* March 2026 — GEPA efficiency; DGM logging-deletion case; SEAL catastrophic forgetting.
13. *Self-Authored Verification Is Unreliable in Heuristic Self-Improving Agents.* arXiv:2607.24300, July 2026 — the verifier–deployment gap.

**Evaluation integrity**

14. *SWE-MERA: A Dynamic Benchmark for Agenticly Evaluating LLMs on Software Engineering Tasks.* arXiv:2507.11059v3.
15. BenchmarkingAgents. *Agent Benchmark Leaderboard 2026 — contamination.* June 2026.
16. DigitalApplied. *SWE-bench in 2026: Benchmarks vs Scaffolding Reality.* June 2026 — OpenAI Frontier Evals audit; vendor self-reporting rates.
17. Applied Technology Index. *2026 Comparative Analysis: Coding Agent Evaluation Harnesses After SWE-bench Saturation.* June 2026.

**Security**

18. Adversa.ai. *Top AI Coding Agent Security Resources — August 2026.*
19. Help Net Security. *Prompt injection still drives most agentic AI security failures in production.* June 2026 — CVE-2026-22708, CVE-2025-59532.
20. *Beyond Static Sandboxing: Learned Capability Governance for Autonomous AI Agents.* arXiv:2604.11839.
21. LLMSecurity. *awesome-agent-skills-security* — provenance-gated tool calls on AgentDojo; untrusted content masking; MCP taint-style vulnerabilities.
22. eCorpIT. *AI agent security in 2026.* July 2026 — containment over filtering; the lethal trifecta framing.

**The Bitter Lesson debate**

23. Zunic, G. *The Bitter Lesson of Agent Harnesses.* 2026.
24. Lee, H. *Hidden Technical Debt of AI Systems: Agent Harness.* May 2026 — the harness as a 2026 artifact; dissolving planner-executor and memory layers.
25. Pappas, E. *The Agent Harness Is the Architecture.* February 2026 — expiration dates on harness logic; the irreducible-coordination counter-argument.
26. Bowne-Anderson, H. *AI Agent Harness, 3 Principles for Context Engineering, and the Bitter Lesson Revisited.* — Manus re-architecture count; future-proofing test.

**Memory**

27. *Designing Agentic Memory in 2026.* May 2026 — five operations; the episodic/semantic index-mixing failure.
28. Atlan. *Episodic Memory for AI Agents.* April 2026 — Letta tiering; unimplemented consolidation.
29. *Mind Your HEARTBEAT! Background Execution Inherently Enables Silent Memory Pollution.* arXiv:2603.23064 — fabricated-citation injection.
30. Konishi, H. *AI Agent Memory Design Guide.* June 2026 — procedural memory as early-stage and highest-leverage.
31. *Episodic-to-Semantic Consolidation Without Identity Drift.* arXiv:2607.01988 — consolidated memory bound to its producing engine.

**Cognitive architecture**

32. Zylos Research. *Cognitive Architectures for AI Agents.* March 2026 — metacognitive capability scaling; SOFAI fast/slow selection.
33. Wray, R., Kirk, J., Laird, J. *Applying Cognitive Design Patterns to General LLM Agents.* arXiv:2505.07087.
34. Sumers, T. et al. *Cognitive Architectures for Language Agents (CoALA).* arXiv:2309.02427.

**Project corpus (internal, for cross-reference)**

- `02_vanguard_charter_claims_and_non_claims_v040.md` — claims C-01…C-12, non-claims, risk register, honest limits
- `05_vanguard_kernel_capabilities_and_security_v040.md` — `K-01`, TCB partition, resource selectors
- `06_vanguard_competence_memory_and_evidence_v040.md` — `MEM-1`…`MEM-7`, `V-01`…`V-13`, three-stage promotion
- `07_vanguard_loop_engineering_and_measurement_v040.md` — `CL-1`…`CL-3`, `M-01`…`M-24`
- `08_vanguard_phase_0_build_plan_v040.md` — increments, must-fail suite, exit criterion
- `10_vanguard_deferred_and_rejected_register_v040.md` — `REJ-03`, `REJ-04`, `REJ-09`, `REJ-10`, `REJ-11`

---

*This document states no contract and constrains no implementation. Its purpose is to be argued with.*
