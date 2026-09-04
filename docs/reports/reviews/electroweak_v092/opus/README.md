# AETHER / Vanguard — Opus Review, `electroweak_v092`

**Subject:** `github.com/brainopensource/cognitive-framework`, branch `feat/strongforce_beta_release_v093`, HEAD `5243866b`
**Reviewer:** Claude Opus 5
**Date:** 2026-09-04
**Method:** direct source reading of `vanguard/packages/` (60,497 LOC), full enumeration and
statistical aggregation of every result artifact under `benchmarks/` (247 JSON files), SQLite
inspection of `.lda/index.db` and `.vanguard/events.sqlite3`, git history analysis (200 commits),
and reconciliation against the peer reviews in `../octopus/` and `../../main/`.

**Nature of this document:** descriptive and advisory. It is a *review*, not law. It modifies no
ADR, no `VISION.md`, no `docs/execution/spec.md`. Under the precedence ladder it sits at layer 5
(Communication) and introduces no architecture of its own authority. Everything it proposes must
pass through the repository's normal ADR and backlog promotion process before any code lands.

---

## Reading order

| # | Document | What it answers |
|---|---|---|
| 1 | [`part1-evidence.md`](part1-evidence.md) | What do the artifacts *actually* say? Every number, with the command that produced it. |
| 2 | [`part2-diagnosis.md`](part2-diagnosis.md) | Seven structural diagnoses. Why the substrate is strong and the agent is not. |
| 3 | [`part3-sota-agent-engineering.md`](part3-sota-agent-engineering.md) | The full technical treatise: tools, editing, AST, retrieval, context, cache, memory, skills, cognition, metacognition, outer loop, supervisor, ledger, benchmarking. |
| 4 | [`part4-target-architecture.md`](part4-target-architecture.md) | What I would build from scratch, and the delta from what exists. |
| 5 | [`part5-roadmap.md`](part5-roadmap.md) | Ordered execution plan with acceptance gates and falsifiers. |
| 6 | [`part6-antipatterns-and-framework-feedback.md`](part6-antipatterns-and-framework-feedback.md) | What *not* to do, and Vanguard's standing as a framework for building agents. |

If you read only one section, read **Part 2 §D1** and **Part 5 §Sprint 1**.

---

## The finding in one paragraph

AETHER is a genuinely excellent *substrate* carrying a *coding agent that does not yet work*. The
event-sourced ledger, the hexagonal lattice, the 1,386-LOC domain-blind kernel, and the L1–L5
prefix-stable context compiler are real, correct, and rare — I would keep all of them unchanged.
But the agent-facing surface those systems mediate is five tools, one tool call per turn, no
directory listing, a four-binary command allowlist, and a unified-diff edit primitive. On the
27-task `frontier_v090` live run, the result was `NO_PATCH` **27 out of 27**, every one with
terminal reason `completed_without_source_patch`. On `benchmark_20_suite`, 2/21 with all 21 runs
terminating at turn 1. The repository's own best asset — a 77,610-edge code/doc graph in
`.lda/index.db` — is wired to the *developer* and not to the *agent*, whose `IndexPort` resolves
to a five-regex file scan. The rigor of this project has been aimed at governing the work rather
than at the agent's capability surface. Redirecting it is roughly four weeks of wiring, touches
no kernel code, and preserves every architectural property the Vision protects.

---

## Relationship to the peer reviews

This review was written after reading, and independently corroborates, the following:

| Peer finding | Source | Status here |
|---|---|---|
| F1 — "100% vs 9.5%" is n=1 vs n=21, not a comparison | `../octopus/agents/draft-synthesis-evidence-audit.md` | **Confirmed independently** (Part 1 §1.4) |
| F2 — the 9.5% run terminated at turn 1 on all 21 tasks | same | **Confirmed independently**, and extended: the same signature appears in `frontier_v090` at a different layer (Part 1 §1.3) |
| F3 — `failure_escalation` routing key is read by no code | same | Not re-verified; accepted |
| Outer loop / Director layer is the missing tier | `../octopus/consolidation/outer-loop-orchestrator.md` | **Endorsed with one structural amendment** (Part 3 §11) |
| `falsified` paths are the highest-value memory field | `../octopus/agents/long-horizon-context-engine.md` | **Strongly endorsed** (Part 3 §7.4) |
| `ProgressVector` + closed pathology vocabulary | `../octopus/agents/meta-conductor.md` | **Endorsed, with sequencing objection** (Part 3 §10, Part 6 §N4) |
| Authority calculus / proposal-not-program thesis | `../../main/aether_technical_report_part1_foundations.md` | Accepted as the correct reading of the kernel |

Where this review differs from its peers, it says so explicitly and gives the evidence. The main
divergence is one of **ordering**: the peer corpus proposes building the outer loop, the conductor,
and the context engine on top of the current inner loop. My position is that the inner loop's tool
surface must be fixed *first*, because an outer loop that dispatches a harness which cannot patch a
file multiplies zero.
