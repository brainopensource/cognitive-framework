# Suggestion — What we should do with `docs/06_references/`

**Author:** analysis pass over the 9 reference files (no code changed).
**Context:** `ADR-0075` **authorized Wave 0** (CI subject-of-record + falsifiers) and `004`'s roadmap shows M-0/M-1 done, **M-2 in flight**. So this is not a "hold-all" situation — only `M-5…M-10`, `agent.spawn`, Pack #2, and concurrency are gated (the M-4 stop line). This document records a **decision** on how to sequence the references, not an implementation; it must not contradict the locked `SPEC.md`/ADR chain.

---

## TL;DR — The decision

1. **Treat `RESEARCH_glm_harness_BETA.md` as the operating synthesis of the whole corpus.** It is the only reference that verifies claims against the working tree (`83b5009`) and is grounded in the locked law (`SPEC.md`, ADRs `0069`–`0074`). Everything else is *input/suggestion*, not law.
2. **The single highest-leverage fix is the "born-hollow" trajectory corpus** (`runtime/trajectory.py` emits `dict(_ZERO_COST)` at lines 53 & 75 → every episode produces a schema-valid, cryptographically attributable, and **unusable** training row: no per-turn cost, no model fingerprint, no verdict). *Verified on disk today.* This poisons Layer 3 (skill cards, DPO, calibrated escalation) — exactly the failure shape invariant **I-9** was written to prevent.
3. **Reject `research_Harness_Builder_Framework.md` as a competing architecture.** It is a greenfield PRD (Redis/NATS/ChromaDB/K8s/event-bus) that duplicates and contradicts the locked hexagonal `vanguard/packages/` lattice (`domain ← ports ← kernel ← agency ← runtime → adapters`). Building it would re-introduce the dual-runtime failure mode the Concept Lock exists to prevent. Mine it only as a catalog of *plugin/adapter ideas* (LLM/memory/tool adapters, prompt engine, cache), never as a second core.
4. **Adopt the research consensus that already matches the law** — "harness is the independent variable," structural retrieval before semantic, model-aware (not model-blind) adapters, exterior-signed judge, 6D leases, reflexion/active-inference kept as *policy/plugin* above the wire.
5. **Defer** the meta-cognition / Wave-6 `THEORETICAL_SYNTHESIS` and `deepseek-harness_algorithms-ideas` material as *future plugin/policy* work, not core changes. They fit the law only if they stay exterior, domain-blind, and promotion-gated (McNemar).

**Net recommendation:** Do not start the divergent framework. The **first engineering action of the next eligible wave must be trajectory-content hardening** (NOVA-1 / F-12), *before* any further Wave-3 feature work, because every episode that completes before the fix is a permanently degraded row in the only corpus Layer 3 will ever train on. (NOVA-1 is registered `PRONTA` in M-2 — it is authorized, not blocked.)

---

## Reference inventory (what each is, and the verdict)

| File | Kind | Weight | Verdict |
|---|---|---|---|
| `RESEARCH_glm_harness_BETA.md` | Independent advisory code review | **High** | **Adopt as the synthesis.** Verified findings, priority-ordered. |
| `RESEARCH_harness_agentic_coding_builder_research_and_framework.md` (+ `_B`) | SOTA research + AETHER application | High | **Adopt principles** (harness-is-capability, controller seam, structural retrieval, delegation-pays-rent). Reject its PRD-style folder layout as predating the locked lattice. |
| `research_Harness_Builder_Framework.md` | Greenfield PRD (event bus, Redis, Chroma, K8s) | Low/Conflicting | **Reject as architecture.** Duplicates kernel/runtime; violates ADR-0070 / `REJ-01`. Keep only as a plugin/adapter idea list. |
| `RESEARCH_THEORETICAL_SYNTHESIS.md` (+ `_B`) | Wave-6 meta-cognition math + prototype | Medium (future) | **Defer.** Prototype is correctly designed as an *exterior, domain-blind plugin* (`plugins/meta-reflector/`) consuming `mhf.trajectory/1`. Good — but depends on a *real* corpus (see #2). |
| `RESEARCH_deepseek-harness_algorithms-ideas.md` | Idea dump (MCTS, active inference, small models, pheromones) | Low/Medium | **Adopt channel ideas only** (System-1 local model, error-signature classifier, skill synthesizer) as future plugins/policies. Refuse swarm-engine/graph-DB/swarm-chatter suggestions. |
| `vanguard_body_detailed.md` | Cosmology treatise (14-tier hierarchy, periodic-table-of-verbs, latency budgets) | Low | **Keep as vision/motivation narrative only.** Contains numbers (22,174 LOC, latency pie) that are aspirational, not measured; do not cite as normative. |
| `openrouter_llm_models_suggested.md` | Model name list | Operational | **Adopt as a reference model menu** for `model_routes` in manifests. Note: it lists speculative future model names; wire only what adapters support. |

---

## The one finding that should drive sequencing

`vanguard/packages/runtime/trajectory.py` builds both its turn records and its episode summary with `dict(_ZERO_COST)` (lines 53, 75). F-12 currently asserts *schema validity*; a zero-cost, fingerprint-less, verdict-less record satisfies it. Consequences mapped to the vision:

- **Skill cards (SPEC §5.4):** need verdict **and** cost per turn. Absent.
- **DPO harvest (SPEC §7):** need per-turn cost divergence. Absent.
- **Calibrated escalation (SPEC §5.3):** need outcome + model identity per turn. Absent.

The GLM review (§4.3) recommends promoting **NOVA-1** from "ready" to "next," ahead of Wave-3 features. `004`'s roadmap already registers NOVA-1 as `PRONTA` in M-2 — so it is authorized, not hypothetical. **This suggestion agrees** and further orders it *before* the Wave-3/compose-v2 work in the priority list below. The cost of ordering it second is invisible until catastrophic: Layer 3 is built on rows that can never train it.

---

## Recommended priority order (post-approval, consistent with GLM + locked roadmap `004`)

1. **Close M-2** (Wave-2 convergence gate) — mechanical, in flight.
2. **Execute NOVA-1 / trajectory-content hardening** (non-zero per-turn cost, model fingerprint, embedded-or-explicitly-null verdict; strengthen F-12 from schema-validity to content assertions). *Highest leverage-per-cost in the whole corpus.*
3. **Make the 3.3-B component-graph decision at Wave-3 entry, before `compose v2` is written** — the one decision whose cost compounds through every pack, trajectory, and `D_H` attribution after Wave 4.
4. **Give Wave 3 the Wave-1 treatment** — protect the NOVA-4 negative suite + full echo-plugin lifecycle on the canonical path; shed breadth, never falsifiers.
5. **Add NOVA-2 suspend/resume falsifier before M-3 closes** — decides whether M-7 concurrency is a refactor or a rewrite.
6. **Hold the M-4 stop line exactly.** No `agent.spawn`, no Pack #2, until the nine-row gate is green on one real run.
7. **Post-M-4 (already scheduled):** documentation collapse; Pack #2 as the I-7 gate (add a **trajectory-parity** assertion so the non-coding pack emits the same rich `mhf.trajectory/1` rows); external benchmark run of `code-default` with cost/latency telemetry; state System-1 `<100ms` and tier-cost claims as named hypotheses (measure at M-9).
8. **M-6…M-10:** only here do the `THEORETICAL_SYNTHESIS` meta-cognition prototype, LEGO-RL / harness-native learning, and skill-card synthesis become in-scope — and only against the now-real trajectory corpus.

---

## Adoption map (research → law)

- **Adopt:** harness-as-independent-variable; flat composition surface at the *composition* layer; structural retrieval before semantic; delegation-must-pay-rent; harness-native (LEGO-RL) learning that reuses the exterior-signed, un-gameable signal; small-model channels (System-1, error classifier, skill synthesizer) as plugins/policies above the wire.
- **Adapt:** sub-5ms pre-flight filters (advisory only, never a second authorization path); Elo-decayed skill eviction (a harvester strategy, cards enter only via the paired-McNemar §5.2 pipeline); active-inference framing (keep the math in SPEC §5.3, drop the metaphysics); McNemar protocol (already law in `docs/04_annex/MEASUREMENT.md`).
- **Refuse:** "no privileged core"; swarm/DAG/graph-DB engines; vector DB as core infrastructure; RL/multi-agent-first sequencing; biological/cosmological framing in normative docs; benchmark scores as evidence without separability. All already refused by ADR-0070 / `REJ-01` / ADR-M0-10.

---

## What to do *now* (pre-M-4)

- **Execute the trajectory fix early in M-2.** NOVA-1 (F-12 hardening) is registered as `PRONTA` on the roadmap — it is authorized Wave 2 work, not blocked. Do it before Wave-3 features. (This is not a "hold" item; the M-4 stop line is the only gate.)
- **Record this decision** so the corpus doesn't get re-litigated: the divergent PRD (`research_Harness_Builder_Framework.md`) is *not* the path; the locked `vanguard/packages/` lattice is.
- **Gate correctly:** respect the M-4 stop line for anything gated (`agent.spawn`, Pack #2, M-5…M-10, concurrency). Within authorized M-2/Wave 2, code work proceeds — only the *sequencing* decision here (NOVA-1 first) matters.
- **Optional, non-blocking:** add a one-page *versioned, non-normative* vision artifact stating the three-layer goal (the GLM review §6 caution 4) so future reviews measure distance against one sentence rather than against prompts and review preambles.

---

*Advisory only. On any conflict with `docs/SPEC.md`, `docs/05_adr/`, or roadmap `002`, those win.*
