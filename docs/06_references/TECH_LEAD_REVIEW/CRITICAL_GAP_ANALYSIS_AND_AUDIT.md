# CRITICAL GAP ANALYSIS & AUDIT — `cognitive-framework` (Vanguard/GTS v0.4.5-beta → v0.5.0)

**Auditor role:** Principal Systems Architect / AI Tech Lead
**Commit audited:** `dcab22e` (merge of `feature_v050_meta-harness`)
**Scope:** `vanguard/packages/*` (22,663 LOC Python), `vanguard/clients/*` (TS), `schemas/v4/*`, `docs/*` (~23,000 lines of Markdown spec), `lab/`, `tools/`, `benchmarkings/`
**Verdict format:** Every finding is graded **KEEP / REFACTOR / KILL** and feeds directly into `NEXT_GEN_META_HARNESS_SPECIFICATION.md`.

---

## 0. Executive Verdict

**Thesis (what the repo gets right).** Underneath the mythology, this repository contains one of the most disciplined open agent-security cores in existence: a 1,698-LOC capability kernel with a formally ordered S0–S12 dispatch sequence whose ordering rules (`K-04`…`K-47`) each encode a shipped defect; RFC 8785 (JCS) canonicalisation with golden byte-level vectors in two languages; an exterior Ed25519-signing evaluator daemon at a separate UID that the agent provably cannot reach; declarative, pure-data harness manifests (`vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-shell-only`) that already prove the *meta-harness thesis* — that a harness is data, not code; and a preregistered measurement lab with McNemar paired testing and an A/A floor. The separability thesis (`VG-02`: "what solved it must be separable, and the judge must be unreachable from the judged") is a genuinely publishable architectural contribution.

**Antithesis (what is rotten).** The project is drowning in its own narrative apparatus. A 14-tier cosmological taxonomy ("String Theory → Turing Foam → Quarks → … → Solar Systems"), three parallel and mutually contradicting sources of truth (`SYSTEM_SPEC_THEORY.md`, `SYSTEM_SPEC_ASBUILT.md`, `SYSTEM_SPEC_DRIFTS.md`), a ledger that declares **39 event kinds and emits 11**, security controls that exist as libraries + tests but are never wired into production (provenance, regrounding, revocation), type-erased `Mapping[str, Any]` ports masquerading as contracts, three distinct types all named `EffectRequest`, a "domain-agnostic" core with a 2,600-LOC coding application and a second budget kernel bolted on top, a bilingual hand-mirrored domain layer, and a repository that commits SQLite binaries, sprint-run JSONL evidence, and LLM response transcripts as if it were a lab notebook. The plugin architecture the README implies **does not exist**: adapters are compiled-in Python modules selected by a composition root; there is no discovery, no versioning, no lifecycle, no isolation boundary between plugins.

**Synthesis (the rewrite decision).** Do **not** rewrite the kernel, the canonicalisation layer, the evaluator exteriority model, the manifest concept, or the lab. Do rewrite everything around them: collapse the spec corpus to one normative document + ADRs, replace the type-erased port layer with versioned, typed SPIs, extract the coding domain into the first *domain pack* plugin, make the ledger actually replayable, and build the plugin lifecycle that the manifests already gesture at. Roughly 40% of the backend is salvageable verbatim, 30% is salvageable with refactor, 30% (plus ~80% of the documentation corpus) should be deleted.

---

## 1. Inventory & Method

| Package | LOC (py) | Role | Salvage grade |
|---|---:|---|---|
| `domain/` | 3,623 | Value objects, JCS, ledger reducers, wire contracts | **KEEP** (minus `ledger/coding_session.py`) |
| `ports/` | 738 | Abstract interfaces | **KILL & REPLACE** (type-erased) |
| `kernel/` | 1,698 | S0–S12 dispatch, attenuation, grants, budget, policy | **KEEP** (wire provenance) |
| `agency/` | 2,171 | EpisodeEngine, L1–L5 context compiler, manifests | **REFACTOR** |
| `runtime/` | 6,315 | Composition root, coordinators, governance, service | **REFACTOR** (split: 60% is misplaced app logic) |
| `adapters/` | 6,211 | Models, sandbox, evaluators, stores, environments | **REFACTOR** into plugins |
| `apps/coding/` | 1,907 | Coding coordinator/plan/progress/verification | **EXTRACT** → Domain Pack plugin |
| `docs/` + root specs | ~23,000 lines md | Specs, sprints, scrum evidence, cosmology | **KILL 80%**, keep ADRs + drift register |
| `lab/`, `tools/telemetry/` | ~2,500 | Paired measurement, preregistration, McNemar | **KEEP**, promote to first-class |
| `tools/00{1,2}_LLM_*` | ~3,000 | Router + deterministic mock/cassette server | **KEEP** as dev-plugins |

Method: forensic read of the drift register (`SYSTEM_SPEC_DRIFTS.md` D-01…D-43) cross-checked against source; static inspection of dispatch ordering, port signatures, event emission sites, manifest schemas; LOC and type-erasure counts verified by script (16 occurrences of `Mapping[str, Any]` in `ports/` alone).

---

## 2. Architectural & Paradigm Audit

### 2.1 What is genuinely SOTA — protect these at all costs

**S-1. The dispatch spine (`kernel/dispatch.py`, 442 LOC).** S0–S12 with lease-after-resolve (K-04), grant-verify-inside-the-guard (K-05), release-before-emit (K-06), debit-reality-including-overruns (K-07), and durable intent-append with fsync *before* effect dispatch (K-47, S8a) so a crash between dispatch and emit leaves the effect *undeterminable* rather than *invisible*. Each rule is annotated with the shipped defect it prevents. This is the correct Trusted Computing Base and it is small. **KEEP verbatim as Layer-0 core.**

**S-2. Canonicalisation & golden vectors.** RFC 8785 JCS in Python and TypeScript with a shared byte-level vector corpus (`schemas/v4/vectors/canonicalisation/*`) covering astral-plane Unicode, negative zero, 2^53 boundaries, NFC non-application. This is the only sane foundation for content-addressed events, grant descriptors, and cross-language replay. **KEEP**, but see AP-6 for the dual-maintenance problem.

**S-3. Judge exteriority.** Evaluator daemon at UID 10002 over UDS, Ed25519-signed verdicts, unreadability probes, and `test/trust/spine.py` asserting the agent cannot reach the judge. Drift D-32 correctly notes the as-built (judge *outside* the worker perimeter) is *stronger* than the spec's K-40. This is the anti-reward-hacking primitive that Claude Code, OpenHands, and Aider all lack. **KEEP; amend spec to match code.**

**S-4. Harness-as-data manifests.** `vg-code-claude-shaped` and `vg-code-opencode-shaped` reconstruct competitor harnesses as pure JSON packs (system prompt, tool schemas, context/routing/approval/budget policies, skills, capability grants with typed resource selectors) with zero kernel changes. This is the embryonic Meta-Harness: the proof that a harness compiles from declarative genes. **KEEP as the seed of the plugin manifest format.**

**S-5. `FrozenHarness` composition freeze + prefix-stable L1–L5 context compiler.** The compiler is a pure function; prefix stability is a property of the type, not of call-site discipline (`compiler.py` docstring is exemplary). Registries freeze at composition; unknown names fail at compose time, not runtime. **KEEP.**

**S-6. The measurement lab.** Preregistered oracles (`preregistration.json`), paired A/A control against an undeletable `vg-shell-only` baseline, McNemar hypothesis testing, prefix-attribution telemetry, and cassette replay. Most agent frameworks measure with vibes; this one measures with statistics. **KEEP; this becomes the Phase-2 self-tuning substrate.**

**S-7. Boundary enforcement in CI.** `check_boundaries.py` enforces the unidirectional lattice `domain ← ports ← kernel ← agency ← runtime → adapters` on 115 source files, with a closed package roster stricter than the spec (D-25). **KEEP; generalise to plugin-boundary enforcement.**

### 2.2 Anti-Patterns & Abstraction Leaks

**AP-1. Narrative-driven architecture (KILL).** `docs/00_executive/vision.md` v3.0.0 maps the system onto a 14-tier continuum from "Tier 00: String Theory — The Digital Substrate (Bits, Clocks, Turing Foam)" to "Tier 13: Solar Systems — The Sovereign Self-Sustaining Cognitive Cosmos", with a parallel 10-level biological dictionary in the README ("Protons = Identity, Neutrons = Ledger, Electrons = Budget"). The taxonomy carries **zero operational semantics** — no invariant, test, or schema references a tier — yet it consumes the README's prime real estate, imposes a vocabulary tax on every contributor, and (worse) creates *false layering intuitions*: readers expect Tier-N to depend on Tier-(N-1), which the actual import lattice contradicts. The repo itself admits this ("the biological vocabulary is NOT an OOP class hierarchy… it is an emergent telemetry depth"), i.e., it is a metaphor defended by a disclaimer. Metaphors that require disclaimers are debt. Replace with the six-word truth: *event-sourced capability kernel with pluggable harnesses.*

**AP-2. The triple-truth spec regime (KILL 80%).** Three root documents — `SYSTEM_SPEC_THEORY.md` (3,260 lines), `SYSTEM_SPEC_ASBUILT.md` (2,229), `SYSTEM_SPEC_DRIFTS.md` (412) — plus 13 backend spec files, 12 frontend spec files, a registry with precedence rules (`PR-3`), and sprint evidence trees for sprints 0–34 across two numbering systems (`sprint*` and `wave*`). Institutionalising drift as a *product* ("every row is a THEORY contract versus an ASBUILT fact") is intellectually honest but economically insane: the team now maintains a formal proof that its own documentation is wrong. Spec surface should be **one normative spec + ADR log + generated schema reference**, with CI failing on spec/code divergence rather than cataloguing it. The drift register itself is the single most valuable document in `docs/` — mine it, then retire the regime.

**AP-3. Type-erased ports = no contract at all (KILL & REPLACE).** `ports/model.py` reduces the model boundary to `propose(context: Mapping[str, Any], tools: Sequence[Mapping[str, Any]], sampling: Mapping[str, Any]) -> Result[Mapping[str, Any]]`. Sixteen `Mapping[str, Any]` occurrences across a 738-LOC package that exists *solely* to define contracts. The consequence is drift D-21: **three distinct types named `EffectRequest`** (`kernel.model`, `ports.environment`, wire `EffectDescriptor`) reconciled by a translator (`invocation.py`) whose existence is a symptom, not a feature. For a project whose thesis is byte-level determinism, having the *semantic* layer be stringly-typed is a category error: the wire is canonical but the meaning is folklore. The rewrite mandates versioned, `typing.Protocol`-based SPIs over frozen dataclasses generated from the JSON Schemas (single source of truth, D-29 resolved in the "generate" direction).

**AP-4. Domain contamination & the second kernel (EXTRACT).** Drift D-42: `runtime/coding_*` + `apps/coding/*` ≈ 2,600 LOC of coding-specific orchestration sits *above* the kernel while `domain/ledger/coding_session.py` leaks a coding projection *into* the pure domain layer — the one package sworn to import nothing. Drift D-43: `coding_budget.py` implements a **second budget controller** (pre-call worst-case USD reservation) parallel to the kernel `Governor`. The "domain-agnostic core" claim is therefore currently false: delete the coding packages and the runtime composition root no longer composes. This is precisely the embedded-domain anti-pattern the microkernel mandate exists to kill. The coding stack is good code in the wrong place — it becomes **Domain Pack #1**.

**AP-5. Dead controls / security theatre (WIRE OR DELETE).** The most dangerous class of defect in a security-first codebase: controls that exist as libraries with green tests but are not on the production path.
- Provenance spans never accumulate (`_admit_turn_result` returns `None`; tool results never enter F-09) — D-05.
- `spawn()` is provenance-blind (D-06); operator trust is a hard-coded literal `Span("brief-1", …)` at `root.py:1210` (D-07).
- `RegroundPolicy` has zero production callers (D-10); post-error re-grounding is a hard-coded `STATUS.md` read.
- `GrantIssuer.revoke` has no caller (D-15/K-49) — revocation is a fiction.
- No seccomp filter; probing `unshare --mount` is not a syscall filter; rlimits are *reported, not applied* (D-31).
- `AT-12` (capability↛verifier path proof) unimplemented; the import lattice is not that proof (D-33).
A green test suite over unwired code is worse than no control: it manufactures false assurance ("488/488 Tests Green" badge). Rewrite rule: **a control merges only with its production call site** (the repo's own `port-interfaces.md` activation rule, applied for real).

**AP-6. Split-brain bilingual core (CONSOLIDATE).** JCS, digests, primitives, selectors, and contracts are hand-maintained twice (`.py` + `.ts` siblings in `domain/`), and `parse_wire` is hand-written while reader JSON is generated (D-29 — "accept or generate; do not do both"). The golden-vector corpus makes this survivable but not cheap. Decision: Python is the runtime language; TypeScript clients consume **generated** readers from JSON Schema only. No hand-written TS domain logic.

**AP-7. Repo-as-lab-notebook (PURGE).** Committed: `tools/002_LLM_API_MOCK/lam.sqlite` (a binary database), timestamped LLM response transcripts under `tools/001_LLM_API_ROUTER/outputs/`, per-run benchmark artifacts (`runs/2026…Z/events.sanitized.json`), sprint dogfood JSONL evidence for ~10 sprints, `benchmark_results.json` at root, and a retracted-results directory. 14 MB working tree, most of it evidence exhaust. Evidence belongs in an artifact store keyed by digest (the repo *has* a `BlobStorePort`); the repo should carry code, schemas, and vectors.

**AP-8. Goodharted governance metrics (DEMOTE).** The TCB LOC budget (1315/1438) and test-count badge are optimised numbers, not safety properties. LOC ceilings incentivise density over clarity in exactly the code that must be clearest; test counts incentivise volume over discrimination (cf. AP-5: high count, unwired controls). Keep the TCB *concept* (minimal kernel), replace the metric with: (a) mutation-testing score on kernel + reducers, (b) percentage of declared controls with production call-site proofs, (c) event-kind emission coverage (declared vs emitted — currently 11/39).

**AP-9. The plugin illusion (BUILD FOR REAL).** Manifests are data, but everything they *name* is a compiled-in module resolved by `runtime/root.py`. There is no plugin discovery (no entry points, no scan path), no version negotiation, no lifecycle (load/activate/quiesce/retire), no per-plugin capability sandbox (adapters run in-process with full interpreter authority — only `proc.exec` payloads are bubblewrapped), and D-27 shows the failure mode: `vg-table-default` sits on disk, orphaned from `registry.json`, because "adding a domain" still requires touching the core. A microkernel whose extensions are compile-time imports is a monolith with good manners.

**AP-10. The ledger cannot actually replay (FIX — this breaks the headline claim).** Event-sourcing's contract is that state = fold(events). As built: `EpisodeStarted` is never written (a run has no durable beginning, D-12); `ApprovalResolved` lives in an in-process queue, so governance decisions are unreplayable (D-13); `CapabilityGranted/Revoked`, `BudgetReserved/Committed` are never emitted, so the authorisation and budget state cannot be reconstructed (D-15); heartbeats are consumed but never produced (D-14); blob and event commits are not atomic (D-19). Time-travel debugging and zero-data-loss recovery are therefore **specified, not possessed**. This is the single highest-priority correctness fix in the rewrite.

**AP-11. Miscellany.** `unittest discover` instead of pytest across a 200-file suite; the episode loop is strictly sequential with fan-out explicitly deferred (D-38) — acceptable for Phase 0, but the rewrite must make concurrency a scheduler property, not an engine rewrite; `evaluate` is outside the episode loop and triggered by `HarnessSession._evaluate` with no `EvaluationRequested` event (D-02/D-03) — trigger ownership must move into the event stream; model routing config is embedded prose in the README (§6) rather than schema-validated data.

---

## 3. Competitive Benchmark Matrix

Comparison against the four reference harnesses named in the mandate. (Landscape facts current to early 2026; treat competitor internals as directional — all four ship continuously.)

| Dimension | **Claude Code** (Anthropic) | **OpenHands** (ex-OpenDevin) | **Aider** | **Hermes** (Nous, open agent stack) | **Vanguard as-built** | **Gap verdict** |
|---|---|---|---|---|---|---|
| **Core loop** | Terminal-native agent loop; subagents; hooks pre/post tool | Event-stream architecture (actions/observations as events), CodeAct-style exec | Chat→edit→git commit loop, tightly scoped | ReAct-style tool loop over open-weight models | `EpisodeEngine` depth-1 loop through S0–S12 kernel dispatch | Vanguard's loop is the most *audited*; least *featureful* (no subagents in prod, sequential only) |
| **Extension model** | MCP servers, hooks, skills, `CLAUDE.md`/`AGENTS.md`, plugins | AgentHub/microagents; runtime plugins; MCP | Minimal by design; config + conventions | Tool registry, open configs | Data manifests exist; **no runtime plugin system** (AP-9) | **Critical gap** — the mandate's whole point |
| **Context strategy** | Automatic compaction, CLAUDE.md memory, agentic search | Condenser/summarisation over event stream | **Repo map**: tree-sitter tags + graph ranking under a token budget — best-in-class code context/token | Prompt-template centric | L1–L5 prefix-stable compiler (excellent), recency-window default, **no repo map, no AST-aware retrieval** (D-37) | Adopt Aider-class repo map as an `IContextManager` plugin |
| **Edit engine** | String-replace + file tools; model-native diffs | Multiple editors incl. LSP/OH-editor | Unified/udiff + search-replace formats tuned per model; git-native undo | Whole-file or diff | `patch.apply` verb; no AST-anchored patching | Phase-1 pack needs anchor/AST diffs beyond raw patch |
| **Sandboxing** | OS-level; permission prompts; managed sandboxes on some surfaces | Docker runtime per session; browser sandbox | None (runs in user env; git is the safety net) | None by default | Rootless bubblewrap + UID separation, **but no seccomp, rlimits unenforced** (D-31) | Vanguard leads on design, must close D-31 |
| **State & replay** | Session transcripts; resumable | Event stream persisted; replayable trajectories | Git history *is* the state | Logs | Event-sourced SQLite WAL ledger, hash-chained — **but non-replayable in practice** (AP-10) | Fix AP-10 → best-in-class; today it trails OpenHands |
| **Judge separation** | Evals external to product | Evaluation harness separate repo/process | Benchmarks external | External | **In-architecture exterior signed judge (UID 10002)** — unique | Vanguard wins outright; preserve |
| **Budget/economics** | Usage limits, model tiers | LLM cost tracking | Token accounting per edit | Manual | Micro-USD leases, reservations, tier escalation Free→Cheap→Frontier | Vanguard leads; foundation for Phase-3 market allocation |
| **Telemetry→training** | Internal | Trajectory datasets used for research/finetunes | Community benchmarks (refactor/edit leaderboards) | Open datasets ethos | LAM sqlite sessions, preregistration, prefix attribution — **no DPO/SFT export path** | Close: schema is 80% there; needs harvest+pair pipeline |
| **Multi-agent** | Subagents, teams (evolving) | Delegation between agents | No | Swarm experiments | `spawn()` exists, provenance-blind (D-06), no economics | Phase-3 target; substrate exists |
| **Determinism** | No | Partial (event replay) | Git-deterministic | No | JCS canonical bytes, seeded RNG/clock ports, cassettes | Vanguard leads decisively |

**Reading:** Vanguard already dominates the *governance axis* (determinism, capability security, judge exteriority, budget economics) where all four competitors are weak, and loses on the *product axis* (plugin ecosystem, context engineering for code, edit-engine ergonomics, concurrency) where competitors have shipped for two years. The rewrite strategy is therefore asymmetric: keep the moat, buy back the product axis as plugins — a repo-map `IContextManager`, an AST patch `IToolkit`, and a real plugin runtime.

---

## 4. Technical Debt & Scalability Risk Register

### 4.1 State-corruption vectors
| ID | Vector | Severity | Detail |
|---|---|---|---|
| R-01 | Non-replayable ledger | **Critical** | AP-10: grants/budget/approvals/lifecycle events unemitted ⇒ recovery reconstructs a *fictional* state. Any "resume from ledger" (`test_resume_from_ledger.py`) resumes an approximation. |
| R-02 | Dual ingress | High | Evaluation triggered out-of-band by `HarnessSession._evaluate` (D-02); a crash between loop end and evaluation loses the verdict linkage with no `EvaluationRequested` intent record. |
| R-03 | Blob/event non-atomicity | High | D-19: an event can reference a blob that was never durably written (or vice versa). Needs write-blob→fsync→emit-event-with-digest ordering or a single transactional store. |
| R-04 | In-process approval queue | High | D-13: human approvals bypass the ledger; replay cannot prove *who authorised what*. Governance value ≈ 0 under audit. |
| R-05 | Three `EffectRequest` types | Medium | D-21: translation layers between homonymous types are where field-drop bugs live; canonical digests computed on different shapes silently diverge. |
| R-06 | Second budget controller | Medium | D-43: kernel `Governor` and `coding_budget.py` can disagree; the ledger records only one side. |

### 4.2 Context rot & token bloat
The L1–L5 compiler prevents *prefix* rot (cache-stable) but the *content* strategy is weak: default compaction is a recency window (D-37), regrounding is dead code (D-10), there is no structural code retrieval (no tree-sitter tag index, no import-graph ranking), and skills are injected as flat cards. Consequence at scale: on repositories beyond toy size the agent's L5 fills with raw tool output, the brief survives (good) but *situational* context degrades monotonically — the classic long-horizon failure mode. Aider's repo-map result is the direct counter-evidence that structural compression beats recency truncation for code tasks. Token bloat secondary source: tool schemas and skill cards are re-serialised JSON blobs inside prompts with no dedup against the frozen prefix.

### 4.3 Plugin isolation boundaries (current = none)
All adapters share the interpreter, the process, and ambient authority; the capability kernel constrains *proposed effects*, not *adapter code*. A malicious or buggy model adapter can read the event store directly, exfiltrate keys from `env_loader`, or monkey-patch the governor — nothing in the lattice stops a same-process import at runtime (the boundary checker is static, CI-time only). The mandate's WASM/container isolation requirement is therefore not an enhancement; it is the missing other half of the security story: **the kernel governs the agent; nothing yet governs the plugins.**

### 4.4 Organisational debt
Two sprint-numbering systems; frontend specs for three clients (CLI, GUI, IDE extension) maintained against a backend that is itself mid-rewrite; benchmark suites in four directories with overlapping task sets (`benchmarkings/zero_hint_v1`, `tasks_phase2`, `tasks_phase2_LAM`, `lab/tasks`); model lists (including provider/model names) hard-coded in the README. Each is small; together they are the drag coefficient that produced a 412-line drift register in one release cycle.

---

## 5. Kill / Keep / Refactor Register (input to the rewrite)

**KEEP verbatim (Layer-0 candidates):** `kernel/` (all 8 modules), `domain/canonicalisation/`, `domain/primitives/`, `domain/ledger/{events,reducer,state}.py` (minus coding projection), `adapters/evaluators/{daemon,signing,isolated}.py`, `adapters/stores/event_store.py` (SQLite WAL, D-16), `agency/context/compiler.py`, manifest packs as seed corpus, `lab/` + `tools/telemetry/`, golden vector corpus, `check_boundaries.py` concept.

**REFACTOR:** `agency/episode/engine.py` (extract second-refusal site D-08 into kernel-emitted events; make turn ceiling a `Reservation` dimension or a documented scheduler policy D-09/D-24); `runtime/root.py` (composition root becomes plugin resolver); `adapters/models/*` (become model-provider plugins behind typed SPI); `adapters/sandbox/rootless.py` (add seccomp + enforced rlimits, D-31); tier escalation (`tier_escalation.py` around `drive_until_green` is the correct salvage shape per D-41 — it becomes the default `IPlanner` policy).

**EXTRACT into Domain Pack #1 (coding):** `apps/coding/*`, `runtime/coding_*`, `domain/ledger/coding_session.py` (generalised to `SessionProjection` with a domain tag), oracle suites, `vg-code-*` manifests.

**KILL:** cosmological/biological taxonomy and vision v3; `SYSTEM_SPEC_THEORY/ASBUILT` pair (fold surviving content into the new spec, keep DRIFTS as a historical ADR appendix); type-erased `ports/` package; committed run artifacts, transcripts, `lam.sqlite`; duplicate hand-written TS domain logic; TCB LOC badge; `MF-01…MF-37` citations (the spec's own drift register says they are fixtures, not production tests); `vanguard-gui/` and `vanguard-ide/` from the core repo (separate repos consuming the generated client contract).

---

## 6. Ten Non-Negotiable Invariants for v-next

1. **One `EffectRequest`.** A single frozen dataclass, generated from one JSON Schema, used at S0, on the wire, and in adapters.
2. **Emitted = declared.** CI computes event-kind emission coverage against production call sites; a declared kind without an emitter fails the build.
3. **A control merges with its call site** (activation-bundle rule enforced, not aspirational).
4. **State = fold(events), proven** by a replay test that reconstructs grants, budgets, approvals, and episode lifecycle from the ledger alone and diffs against live state every CI run.
5. **The judge stays exterior** — separate identity, signed verdicts, unreachable from agent and from plugins.
6. **Plugins are untrusted by default.** Isolation tier declared in the plugin manifest; in-process execution is a privilege granted by policy, not the default.
7. **The core is domain-blind.** `grep -r "coding\|ast\|pytest" layer0/` returns nothing.
8. **Specs are generated or normative — never both.** One normative document; schema references generated; drift is a CI failure, not a register.
9. **Telemetry is a dataset.** Every episode terminates in a trajectory record that is, without transformation, a valid row in the DPO harvest schema.
10. **Metaphors ship as comments, not architecture.**

---
*Companion document: `NEXT_GEN_META_HARNESS_SPECIFICATION.md` — the full rewrite blueprint that consumes this register.*
