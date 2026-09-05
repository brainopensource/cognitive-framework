---
id: report.electroweak-v092.grok.index
canonical_id: report.electroweak-v092.grok.index
class: report
authority: non-canonical
truth_plane: BOTH
status: snapshot
implementation_status: NOT_AUTHORIZING
owner: grok-principal-architect-review
canonical_for: []
purpose: >
  Index and executive verdict for the Grok principal harness+agent architecture
  review of Coding Max / vg-code-* / pack roles, written 2026-09-04 against
  feat/strongforce_beta_release_v093. Does not authorize work. Does not override
  docs/execution/.
audience:
  - architect
  - release-owner
  - contributor
last_verified: "2026-09-04"
pin_head: "5243866bc169c7f60cc7d4f74b9a853f60356381"
pin_branch: feat/strongforce_beta_release_v093
relationships:
  - execution.tasks
  - execution.milestones
  - execution.technical
  - execution.feature_spec
  - report.branch-consolidation-2026-09-02
---

# Grok principal review — coding agents and the Aether harness

**Authority:** `non-canonical`. This folder is a design review a CTO can use to
change the agent. It is **not** the living board. Living truth is
[`docs/execution/`](../../../execution/tasks.md). `.draft/` is lock, not product.
Research under `docs/research/` is non-canonical. Sibling octopus notes under
[`../octopus/`](../octopus/consolidation/outer-loop-orchestrator.md) are
proposals, not HEAD.

**Subject:** the coding agents this framework instantiates (Coding Max /
`vg-code-*` / pack roles), plus the substrate they sit on. Not a ticket closer.
Not a prompt pack. Not Chimera as product.

**Pin:** `5243866bc169c7f60cc7d4f74b9a853f60356381` on
`feat/strongforce_beta_release_v093` (2026-09-04). Live dogfood trial
`gf-orders-001` was run later on the same branch at `ffc3dc926e80` (see
[`05-whitepaper-…`](05-whitepaper-settlement-evolution-and-live-trial.md)).
LDA index was healthy but **STALE vs HEAD**. `dev_context_logs/context_summary.md`
was from another branch — ignored for TCB/test numbers. **Full suites were
not re-run for the original review; nothing below is `PASS` except the
explicit trial oracle and ledger facts in file 05.**

**Role constraint honored:** no second `EpisodeEngine`; no Chimera as product
path; no kernel `ast.parse`; no HYDRA-as-default; meta cannot admit `completed`
or grow budget. Official SWE/DeepSWE is G-3 measurement, not definition of done.

---

## How to read

| File | Contents |
|---|---|
| this README | Verdict, \(R\), the two changes, reading order |
| [`01-live-agent-and-holes.md`](01-live-agent-and-holes.md) | Agent as it is: tools, gate, context, state; holes vs hard SWE with `file:line` |
| [`02-theories-and-control-laws.md`](02-theories-and-control-laws.md) | Consolidated theories from this tree's research + SOTA control laws; FACT vs fiction; why-not/how/when |
| [`03-evolution-architecture.md`](03-evolution-architecture.md) | Inner loops, outer loops, framework, new capabilities, kill list |
| [`04-sota-program.md`](04-sota-program.md) | What I would actually do: greenfield, brownfield, long-run, agent-builder, 10-step order |
| [`05-whitepaper-settlement-evolution-and-live-trial.md`](05-whitepaper-settlement-evolution-and-live-trial.md) | PhD-style white paper: three-audit synthesis, board sequencing, operator dogfood, live trial `gf-orders-001` (abandoned, 0 effects), evolution program. Non-authorizing. |

Every claim about the tree is **FACT** (opened at pin) or **`[PROPOSAL]`**.
Research-doc claims and internet claims are labeled. Mechanism presence ≠
milestone CLOSED.

---

## The law this review is written under

Session success is a product, not a sum:

\[
R = \prod_t \Pr(\text{honest progress}_t \mid \text{honest state}_{t-1}).
\]

If inner-loop settlement is leaky, outer loops (campaigns, specialists, memory,
HYDRA, “super-agents”) **multiply false completions**. Propose them anyway —
tagged inner / outer / substrate — and say what must already be true.

A chatbot with `patch.apply` is a fail. That is exactly this agent when
`vg-code-default` can `finish` with zero effects.

---

## Executive verdict (one page)

The product coding agent is **not a class**. It is pack + profile + tools +
admission over one loop:

```text
ApplicationService → HarnessSession → EpisodeEngine → Kernel.dispatch (S0–S12)
```

`vg-code-fast`, `vg-code-balanced`, `vg-code-max` are **name aliases** of the
same four verbs (`fs.read`, `fs.search`, `patch.apply`, `proc.exec`) and the
same `vg-code-default` prompt/skill. They are not three phenotypes.

**What is already SOTA-shaped (FACT, MECHANISM, not all CLOSED):** domain-blind
kernel, one `EpisodeEngine`, prefix-stable L1–L3 compiler, distiller, omission
ledger, epoch after write, 2PC for multi-file, tamper **module**, vacuous-oracle
**policy**, implicated-set **builder**, dialect recovery, resume σ
(MS-RESUME `CLOSED`). Meta controller exists as a powerless advisor.

**What is not SOTA (FACT holes):**

1. `vg-code-default` is admission-exempt (`session.py` `ADMISSION_GATE_EXEMPT`).
   T-04 is `[PROPOSAL]` until an RF-25 successor baseline.
2. Tamper is unwired on session admit. Spec already records this.
3. Session does not pass `implicated_files` / `callers_by_symbol` into pack
   completeness. A 40-file signature change can “complete” after one file +
   unrelated pytest.
4. Greenfield evidence mapping aliases `structural_passed` =
   `behavioral_passed` = `verification.passed` and never sets
   `oracle_failed_on_stub`. Prompt law (“do not read first”) fights pack policy
   (scaffold + oracle-fail-on-stub).
5. Product arms have no `tool-policy.json` → ungated loop. Phased ladder is not
   the product path and would break reproduce-first if turned on blindly.
6. Outer loop is mostly `[PROPOSAL]`. `runtime/campaign/` and
   `runtime/outer_loop/` **do not exist**.
7. Memory SPI exists; product wiring is gated (T-32, M-8 empirical still open).
8. Fast/balanced/max being identical is a product lie.

**The two changes that most increase the chance of finishing a multi-day
greenfield or a 40-file brownfield without a lying `completed`:**

1. **Inner (do first):** settlement as the inner loop — admit on every coding
   arm including `vg-code-default` (T-04 as an explicit successor-baseline
   decision), **tamper on admit**, **implicated tests as the verification
   subject**, patch conflicts recover through re-read not silent/fuzzy apply.
2. **Outer (only after that):** a campaign director with **zero mutating
   tools**, children in worktrees, merge **by implicated-test verdict**. Not
   HYDRA. Not Chimera. Not a second `EpisodeEngine`.

Until (1), do not claim the product agent cannot lie. Until (1), (2) is a
false-completion factory with extra DAG nodes.

---

## What this review is not

- Not authorization to shrink `ADMISSION_GATE_EXEMPT` without the RF-25
  successor baseline named in T-04.
- Not a prompt rewrite. AHE-class evidence: tools/middleware/memory beat
  system prompts. Do not spend a quarter on `system-prompt.txt`.
- Not an official SWE/DeepSWE score. G-3.
- Not a claim that octopus `ORCH-*` packs, SONNET four paradigms, or
  `future_improvements_sota_harness_2808.md` “RATIFIED” badges are HEAD.

---

## Sibling corpus (read as lock / research, not law)

| Corpus | Use |
|---|---|
| `docs/execution/` | Law and living board |
| `docs/research/coding_harness/*` | Theories; many paths stale vs HEAD |
| `docs/research/features/HYDRA_*`, `SONNET_SUPER_AGENT.md` | Non-canonical topologies |
| `.draft/todo/SOTA_CODING_HARNESS_ENGINEERING_ROADMAP.md` | Intent; cites `episode/compactor.py` which is **not** in this tree |
| `../octopus/` | Director-layer proposal; kernel-unchanged is right; evolutionary policy is not product |
| Canvas beside chat (session artifact) | Same verdict, scannable |

End of index.
