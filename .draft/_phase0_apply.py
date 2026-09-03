#!/usr/bin/env python3
"""ONE-SHOT assembler used 2026-09-03 to apply PHASE-0.

Do not re-run: a second run would nest spec/tasks appendices.
Authority is now docs/execution/; this script is leftover apply tooling.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / ".draft"
EXEC = ROOT / "docs" / "execution"
A = DRAFT / "DEVELOPMENT_FINAL_PLAN.md"
B = DRAFT / "DEVELOPMENT_FINAL_PLAN_B.md"
V2 = DRAFT / "DEVELOPMENT_FINAL_PLAN_v2.md"
P0 = DRAFT / "PHASE-0_DEVELOPMENT_FINAL_PLAN.md"

BANNER = (
    "> **Unused reference.** Day-to-day development authority is "
    "[`docs/execution/`](../docs/execution/): "
    "[`milestones.md`](../docs/execution/milestones.md), "
    "[`spec.md`](../docs/execution/spec.md), "
    "[`technical.md`](../docs/execution/technical.md), "
    "[`backlog.md`](../docs/execution/backlog.md), "
    "[`tasks.md`](../docs/execution/tasks.md). "
    "This draft remains forensic lock at HEAD `66aa7a3c`. Do not treat it as the work board.\n\n"
)


def lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(True)


def extract(path: Path, start: int, end: int) -> str:
    src = lines(path)
    return "".join(src[start - 1 : end])


def retarget(text: str) -> str:
    replacements = (
        ("](../VISION.md)", "](../../VISION.md)"),
        ("](../AGENTS.md)", "](../../AGENTS.md)"),
        ("](../README.md)", "](../../README.md)"),
        ("](../docs/", "](../"),
        ("](../vanguard/", "](../../vanguard/"),
        ("](../test/", "](../../test/"),
        ("](../benchmarks/", "](../../benchmarks/"),
        ("](../packs/", "](../../packs/"),
        ("](../.agents/", "](../../.agents/"),
        ("](../tools/", "](../../tools/"),
        ("](DEVELOPMENT_FINAL_PLAN.md)", "](../../.draft/DEVELOPMENT_FINAL_PLAN.md)"),
        ("](DEVELOPMENT_FINAL_PLAN_B.md)", "](../../.draft/DEVELOPMENT_FINAL_PLAN_B.md)"),
        ("](DEVELOPMENT_FINAL_PLAN_v2.md)", "](../../.draft/DEVELOPMENT_FINAL_PLAN_v2.md)"),
        ("](todo/", "](../../.draft/todo/"),
        ("](HYDRA_", "](../../.draft/HYDRA_"),
        ("](SONNET_", "](../../.draft/SONNET_"),
        ("file:///home/rock-dev/Coding/cognitive-framework/docs/execution/", ""),
        ("file:///home/rock-dev/Coding/cognitive-framework/", "../../"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def write_technical() -> None:
    parts: list[str] = []
    parts.append(
        """---
id: execution.technical
canonical_id: execution.technical
class: execution
authority: execution
truth_plane: TARGET
status: living
owner: repository-governance
canonical_for:
  - execution-technical-handbook
purpose: Self-explaining engineering handbook for future work. Present-tense architecture stays in docs/architecture and docs/backend.
derived_from:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - .draft/DEVELOPMENT_FINAL_PLAN_v2.md
  - .draft/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
lock_head: "66aa7a3c0c31"
last_verified: 2026-09-03
relationships:
  - execution.milestones
  - execution.feature_spec
  - execution.tasks
  - execution.backlog
---

# Technical Specifications (Detailed)

Developers SHALL use this file plus [`spec.md`](spec.md), [`tasks.md`](tasks.md), [`milestones.md`](milestones.md), and [`backlog.md`](backlog.md). Drafts under `.draft/DEVELOPMENT_FINAL_PLAN*.md` are unused reference.

**Present vs future.** `docs/architecture/`, `docs/backend/`, and `docs/SPEC.md` describe HEAD. This file describes how to implement remaining work and keeps `[PROPOSAL]` variants in full.

**Navigation before coding.** `uv run lda identity --json` then `uv run lda doctor --json`. Then `python3 tools/docs_rag_v0.py --file <path>` for the file you will edit. Kernel stays domain-blind (I-7). AST preflight belongs in `adapters/environment/`, never `kernel/dispatch.py` S7/S8.

**Canonical task IDs** are `T-01`… in [`tasks.md`](tasks.md). v2 `SUB-*` / `TXN-*` are aliases in [`backlog.md`](backlog.md). Live kernel pipeline package `SUB-01` in the backlog is **not** v2 admission.

**Recommended reading order (not a sprint):** T-01–T-08, then T-09–T-13.

**FACT STORE path:** `adapters/stores/event_store.py` (not `runtime/event_store.py`). **`domain/task_state.py` is MISSING** until T-09.

## 0. Epistemic legend

| Tag | Meaning |
|---|---|
| **FACT** | Observed in current source |
| **MECHANISM** | Code exists with tests; not a product claim |
| **INFERENCE** | Engineering conclusion from FACT + MECHANISM |
| **[PROPOSAL]** | Future work; keep the text; do not treat as HEAD |
| **ASPIRATION** | Competitive position; not a forecast |
| **CONTRADICTION** | Two authorities disagree; source wins |
| **MISSING** | Path does not exist at lock HEAD `66aa7a3c` |
| **SUPERSEDED** | Keep text, mark `[PROPOSAL]`, cite the better location |

Present docs to open while coding:

| Context | Read first |
|---|---|
| Kernel / TCB | `docs/architecture/boundaries.md`, `vanguard/packages/kernel/dispatch.py` |
| Turn loop | `docs/backend/architecture/agency.md`, `episode/engine.py`, `session.py` |
| Context | `compiler.py`, `layers.py`, `compaction.py` |
| Runtime / resume | `docs/backend/architecture/runtime-execution.md`, `app_service.py`, `task_state.py` |
| Index | `ports/index.py`, `adapters/stores/repo_index.py` |
| Packs | `packs/code-default/` |
| Memory | `docs/backend/architecture/memory-learning.md`, `ports/memory.py` |
| Eval | `docs/backend/architecture/assurance-evaluation.md` |

Wave-titled sections copied below are **capability recipes**, not a calendar.

---

## From v2 — architecture catalog and SOTA harness mechanics

Copied from [`.draft/DEVELOPMENT_FINAL_PLAN_v2.md`](../../.draft/DEVELOPMENT_FINAL_PLAN_v2.md) (locked triad). FACT / `[PROPOSAL]` tags remain binding.

"""
    )
    parts.append(retarget(extract(V2, 49, 1121)))
    parts.append(
        """

---

## From B — live inventory, gaps, formal model, lattice, workflows, file routing

Copied from [`.draft/DEVELOPMENT_FINAL_PLAN_B.md`](../../.draft/DEVELOPMENT_FINAL_PLAN_B.md).

"""
    )
    parts.append(retarget(extract(B, 298, 1324)))
    parts.append(
        """

---

## From B — references, session appendix, algorithms, operator one-pager, tool inventory, product loop

"""
    )
    parts.append(retarget(extract(B, 1540, 1820)))
    parts.append(
        """

---

## From A — what the code already provides (G-01…G-12)

Copied from [`.draft/DEVELOPMENT_FINAL_PLAN.md`](../../.draft/DEVELOPMENT_FINAL_PLAN.md).

"""
    )
    parts.append(retarget(extract(A, 274, 459)))
    parts.append(
        """

---

## From A — formal model, target architecture, capability recipes (historical wave bodies)

Do not execute these as a sprint calendar. Exit gates live in [`milestones.md`](milestones.md). Work items live in [`tasks.md`](tasks.md).

"""
    )
    parts.append(retarget(extract(A, 625, 2401)))
    parts.append(
        """

---

## From A — file ownership, prompts, models, security, verification, taxonomy, research agents

"""
    )
    parts.append(retarget(extract(A, 2403, 2889)))
    parts.append(
        """

---

## From A — per-task go/no-go checklists (renamed from sprint)

"""
    )
    parts.append(retarget(extract(A, 3036, 3088)))
    parts.append(
        """

---

## From A — bibliography, CLI, loop vs harness, four-tier memory, cross-link matrix

"""
    )
    parts.append(retarget(extract(A, 3284, 3389)))
    parts.append("\n")
    parts.append(retarget(extract(A, 3428, 3636)))
    parts.append(
        """

---

## Planning snapshots (historical; not HEAD identity)

### A §1 evidence boundary

"""
    )
    parts.append(retarget(extract(A, 159, 272)))
    parts.append("\n### B §2 evidence boundary\n\n")
    parts.append(retarget(extract(B, 168, 296)))
    parts.append("\n")
    (EXEC / "technical.md").write_text("".join(parts), encoding="utf-8")


def write_spec() -> None:
    old = (EXEC / "spec.md").read_text(encoding="utf-8")
    body = old.split("---", 2)[-1].lstrip("\n")
    parts: list[str] = []
    parts.append(
        """---
id: execution.feature_spec
canonical_id: execution.feature_spec
class: specification
authority: execution
status: active
owner: repository-governance
canonical_for:
  - active-feature-delta-specification
version: "2.0.0"
date: "2026-09-03"
lock_head: "66aa7a3c0c31"
derived_from:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - .draft/DEVELOPMENT_FINAL_PLAN_v2.md
  - .draft/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
normative_authority:
  - docs/SPEC.md
  - docs/architecture/boundaries.md
relationships:
  - execution.milestones
  - execution.backlog
  - execution.tasks
  - execution.technical
---

# Feature Delta Specification (execution)

This file is the typed SHALL-contract for **all remaining backend work**. Upon a task merging, promote landed contracts into present-tense `docs/architecture/` / `docs/backend/` / `docs/SPEC.md`. Modules marked **MISSING** do not exist at lock HEAD `66aa7a3c`.

Companion handbook: [`technical.md`](technical.md). Task IDs: [`tasks.md`](tasks.md).

Historical CMX-09-only delta is preserved as [Appendix H](#appendix-h-historical-cmx-09-delta).

**Kernel (I-7).** AST preflight SHALL NOT enter `kernel/dispatch.py` S7/S8. S7/S8 remain RESERVE/VERIFY. Syntax checks belong in `adapters/environment/`.

**FACT canonical path.** `ApplicationService` → Runtime → `HarnessSession` → `EpisodeEngine` → `Kernel.dispatch`. ForgeEngine and ChimeraEngine SHALL NOT be the product path (`[PROPOSAL]` quarantine: T-23).

**Admission (FACT).** Live function is `admission_required` (`runtime/session.py`): exempt `vg-code-default` / `vg-code-lex`, else `"patch.apply" in verbs`. `ADMISSION_GATED_HARNESSES` is unused. T-04 is `[PROPOSAL]` and needs an RF-25 successor baseline.

**VerificationReceipt.passed (FACT).** `exit_code == 0 and executed_test_count > 0`. Unknown counts stay 0. Forge SHALL NOT set `test_count = 1` (T-06).

**I-1 universal signed finish** (v2): `[PROPOSAL]` too strong. Per-class evidence (A §9.4) wins. Fail-to-pass is the **bugfix** class (T-38).

**Mutation score ≥ 0.80** (v2 §5.4): `[PROPOSAL]` optional treatment T-39, not default admission.

**I-STATE.** σ is a ledger fold. Do not dump `resume_state` JSON into frozen L3 (FACT current bug; T-12). `domain/task_state.py` is **MISSING** until T-09.

**Single-writer.** One writer per workspace; children that write are sequential or isolated worktrees.

**Authorize-before-retrieve.** Memory recall requires grant (`runtime/prompt_assembler.py`).

---

## From A — product thesis, SOTA definition, non-goals

"""
    )
    parts.append(retarget(extract(A, 461, 530)))
    parts.append(
        """

---

## From A — domain values, ports, verification receipt, progressive packet, campaign, single-writer

`[PROPOSAL]` catalogs below are kept in full. Implementation merge for task state is B §6.12 (see [`technical.md`](technical.md)).

"""
    )
    parts.append(retarget(extract(A, 888, 1110)))
    parts.append(
        """

---

## From A — task classes and per-class evidence

Per-class evidence wins over v2 I-1. Fail-to-pass (v2 §5.3) applies to class `bugfix`.

"""
    )
    parts.append(retarget(extract(A, 1262, 1329)))
    parts.append(
        """

---

## From A — prompt/policy, model strategy, security/operator

"""
    )
    parts.append(retarget(extract(A, 2526, 2704)))
    parts.append(
        """

---

## From A — stop, simplify, and rollback

"""
    )
    parts.append(retarget(extract(A, 2967, 2994)))
    parts.append(
        """

---

## From A — research and explanation agents; benchmark taxonomy

"""
    )
    parts.append(retarget(extract(A, 2773, 2889)))
    parts.append(
        """

---

## From v2 — TransformSpec (proposal sketch + live fields)

"""
    )
    parts.append(retarget(extract(V2, 218, 267)))
    parts.append(
        """

---

## From B — live tool/verb inventory and product target loop

"""
    )
    parts.append(retarget(extract(B, 1763, 1799)))
    parts.append(
        """

---

## Progressive context packet (binding placement)

Keep `ContextPacket`. FEATURE_SPEC 4-tier budget is **L4/L5 policy on existing `ContextCompiler`**, not a second compiler class (`PRG-01` alias → T-15).

| FEATURE_SPEC tier | Existing layer | Content |
|---|---|---|
| 0 Invariant anchor | L1 + L4 head | goal, active step, settled invariants |
| 1 Negative memory | L4 | dead ends, falsified hypotheses |
| 2 Active AST slice | L5 | current files, epoch-bound |
| 3 Symbol stubs | L5 remainder | IndexPort stubs with omissions |

## WorkspaceEpoch `[PROPOSAL]` (T-14)

```text
WorkspaceEpoch := { treeHash, indexDigest, sourceRevision, compiledAtTurn }
```

Stale epoch ⇒ refresh or fail closed. Do not put `repo_map` or σ into frozen L3.

## Dialect FACT split

Wire recovery: `adapters/models/dialect.py`. Malformed → Proposal: `agency/episode/protocol_recovery.py`. Taxonomy in Appendix H §8.

## 2PC / tamper placement

- 2PC: create `adapters/environment/transaction.py` (**MISSING**). `GitEnvironment.apply` is sequential today; `ast.parse` is post-write observation.
- Tamper: create `runtime/governance/tamper_shield.py` (**MISSING**). Enumerate tests via IndexPort (T-18); `Path.glob("test/**")` is insufficient.

---

# Appendix H — Historical CMX-09 delta

The following is the pre-PHASE-0 `spec.md` body, preserved in full.

"""
    )
    parts.append(body)
    (EXEC / "spec.md").write_text("".join(parts), encoding="utf-8")


def write_tasks() -> None:
    hist = (EXEC / "tasks.md").read_text(encoding="utf-8")
    tree = extract(P0, 317, 611)
    tree = tree.replace(
        "**T-38 Fail-to-pass reproducer (bugfix class)** (v2 §5.3, A §9.4)  \n"
        "- [ ] Pre-verify MUST fail; post-verify MUST pass; vacuous reproducer rejected  \n"
        "- [ ] Not a universal finish law (docs/research/explanation excluded)  \n",
        "**T-38 Fail-to-pass reproducer (bugfix class)** (v2 §5.3, A §9.4)  \n"
        "- [ ] Pre-verify MUST fail; post-verify MUST pass; vacuous reproducer rejected  \n"
        "- [ ] Not a universal finish law (docs/research/explanation excluded)  \n"
        "\n"
        "**T-39 Mutation score ≥ 0.80** (v2 §5.4, VER-02) `[PROPOSAL]`  \n"
        "- [ ] Optional treatment; not default admission  \n"
        "- [ ] Do not make mutation a universal finish law  \n"
        "- Alias: `VER-02`, `TLS-06`  \n",
    )
    header = """---
id: execution.tasks
canonical_id: execution.tasks
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: BACKEND_FINISH_ACTIVE
owner: repository-governance
canonical_for:
  - execution-flat-task-tree
purpose: Flat tasks and subtasks by context. No sprints, no waves, no WIP calendar. Team capacity is chosen later. requires: is the only order hint.
audience:
  - contributor
  - release-owner
version: 0.9.3
last_verified: 2026-09-03
lock_head: "66aa7a3c0c31"
normative_authority:
  - docs/SPEC.md
  - docs/execution/spec.md
  - docs/execution/technical.md
relationships:
  - execution.milestones
  - execution.backlog
  - execution.feature_spec
  - execution.technical
reviewer: repository-governance
confidence: high
---

# Execution tasks (flat, by context)

Authority: execution. Delta contracts: [`spec.md`](spec.md). Handbook: [`technical.md`](technical.md). Packages: [`backlog.md`](backlog.md). TARGET gates: [`milestones.md`](milestones.md).

**No sprints. No waves.** Check boxes as work completes. **Recommended reading order (not a schedule):** T-01–T-08, then T-09–T-13.

B §18 tickets T-01–T-35 are canonical. A §31 maps into those IDs or T-36+ (see merge map appendix). v2 `SUB-*` are aliases. Live backlog `SUB-01` (kernel S0–S12) is a different package.

Historical CMX-09 sprint DAG is in the [appendix](#appendix-historical-cmx-09-dag-do-not-execute-as-the-program).

"""
    tickets = (
        "\n---\n\n## Appendix: B §18 ticket bodies (verbatim)\n\n"
        "Canonical files/requires/falsifiers from Plan B. Expanded checkboxes above must not drop these lines.\n\n"
        + retarget(extract(B, 1326, 1510))
    )
    merge = (
        "\n---\n\n## Appendix: A §31 → T-id merge map\n\n"
        + extract(P0, 614, 644)
    )
    appendix = (
        "\n---\n\n## Appendix: historical CMX-09 DAG (do not execute as the program)\n\n"
        "Preserved from the pre-PHASE-0 `tasks.md`. T2–T7 map to T-09, T-17, T-18, T-15, T-21.\n\n"
        + hist
    )
    (EXEC / "tasks.md").write_text(
        header + tree + tickets + merge + appendix, encoding="utf-8"
    )


def write_milestones() -> None:
    existing = (EXEC / "milestones.md").read_text(encoding="utf-8")
    # Keep M-0–M-10 table + gate semantics from original §1–§2, OCT, SWE.
    # Cut living W-092 overlay out of the primary view.
    yaml_and_intro = """---
id: execution.milestones
canonical_id: execution.milestones
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: PARTIAL
owner: repository-governance
canonical_for:
  - milestone outcomes and gates
purpose: Present stable TARGET milestone outcomes, dependencies, and acceptance predicates without claiming current completion. No sprint calendar.
audience:
  - contributor
  - release-owner
version: 0.9.3
last_verified: 2026-09-03
lock_head: "66aa7a3c0c31"
derived_from:
  - .draft/DEVELOPMENT_FINAL_PLAN.md
  - .draft/DEVELOPMENT_FINAL_PLAN_B.md
  - .draft/DEVELOPMENT_FINAL_PLAN_v2.md
  - .draft/PHASE-0_DEVELOPMENT_FINAL_PLAN.md
normative_authority:
  - docs/SPEC.md#milestone-compatibility
  - docs/decisions.md
relationships:
  - execution.tasks
  - execution.backlog
  - execution.feature_spec
  - execution.technical
  - spec.core
reviewer: repository-governance
confidence: high
---

# TARGET Milestone Gates

## 1. Scope & Authority

This page defines stable release outcomes and gate predicates. It does not track day-to-day work packages (owned by [`backlog.md`](backlog.md)) or the flat task tree (owned by [`tasks.md`](tasks.md)). Mechanism presence does not infer milestone closure; closure requires producer-verifiable empirical receipts evaluated under the milestone acceptance boundary.

Day-to-day work is the flat `T-*` tree. There is no sprint calendar and no WIP lane on this page. Status of **MS-*** rows is `OPEN` until receipts exist.

"""
    # Extract original §1 table through §2 from existing file
    start = existing.find("| Milestone | TARGET Outcome |")
    gate_end = existing.find("## 3. Capability Wave Overlay")
    oct_start = existing.find("## 4. Post-M-10 Horizon")
    preserved_m_gates = existing[start:gate_end].rstrip() + "\n"
    preserved_oct_swe = existing[oct_start:].rstrip() + "\n"

    overlay = """
---

## 3. Backend-finish TARGET overlay (MS-*)

Vanguard v0.9.x backend finish contributes evidence to existing M-4–M-10 gates. Implementation details live in [`tasks.md`](tasks.md). Typed contracts live in [`spec.md`](spec.md). Engineering handbook: [`technical.md`](technical.md).

These rows recast A §0 / B §1 reliability order as **capability outcomes**, not waves.

| ID | TARGET outcome | Acceptance | Status |
|---|---|---|---|
| **MS-INSTRUMENT** | Exact-subject, schema-valid, dry-run-null empirical instrument | Enumerator digest; no `__pycache__` tasks; `subject_sha` bound; dry-run pass/cost/oracle null (B §8.4/8.5; T-01–T-03, T-24–T-25, T-40–T-41) | `OPEN` |
| **MS-TRUTH** | No `completed` without bound verification; Forge cannot invent counts; one gating function | AdmissionGate + `VerificationReceipt.passed`; A §9.7; T-04–T-08, T-42, T-38, T-23. T-04 remains `[PROPOSAL]` until RF-25 successor baseline | `OPEN` |
| **MS-RESUME** | Fresh process restores episode_id, σ, prefix L1–L3; σ not in L3 | A §10.7; T-09–T-13, T-43–T-44. `domain/task_state.py` MISSING until T-09 | `OPEN` |
| **MS-SEE** | Epoch-bound packets, omissions explicit, one ContextCompiler | A §11.9; v2 §3 target (not current L3 dump); T-14–T-16, T-36–T-37, T-45–T-46 | `OPEN` |
| **MS-CHANGE** | 2PC multi-file, adapter preflight, tamper, implicated-set, greenfield oracle | A §12.8; v2 §4.2; T-17–T-20, T-47–T-49. AST never in kernel | `OPEN` |
| **MS-CONTROL** | One EpisodeEngine coding path qualified; Forge/Chimera not in product scores | A §13.6; facade fast/balanced/max; T-26–T-27, T-51–T-52 | `OPEN` |
| **MS-META** | Controller off unless paired study valid | A §14.7; T-28 `[PROPOSAL]` | `OPEN` `[PROPOSAL]` |
| **MS-SPECIALIST** | Treatments vs control; exterior merge | A §15.6; T-29–T-30, T-53 `[PROPOSAL]` | `OPEN` `[PROPOSAL]` |
| **MS-CAMPAIGN** | Director as runtime client; CAS handoffs | A §16.8; v2 §7.1; T-31, T-54–T-55, T-34 `[PROPOSAL]` | `OPEN` `[PROPOSAL]` |
| **MS-MEMORY** | Product memory behind grants; held-out lift; rollback | A §17.7; M-8 remaining empirical; T-32, T-56–T-57 `[PROPOSAL]` product wiring | `OPEN` `[PROPOSAL]` |
| **MS-OFFICIAL** | SWE-P5 / DeepSWE wrapper; local ≠ official | A §18.8; G-3; T-33, T-58 | `OPEN` `[PROPOSAL]` / blocked on control |
| **MS-SENIOR** | Senior Developer profile | A §29.1 copied below | `OPEN` |
| **MS-STAFF** | Staff Engineer profile | A §29.2 copied below | `OPEN` |
| **MS-PRINCIPAL** | Principal Architect profile | A §29.3 copied below | `OPEN` |
| **MS-LEAD** | Tech Lead profile | A §29.4 copied below | `OPEN` |
| **MS-HYDRA** | Bifurcation + living horizon | v2 §7.3–7.4; T-55. Product implementer remains EpisodeEngine+pack, not ChimeraEngine | `OPEN` `[PROPOSAL]` |

Dual mission (v2 §1.1): (1) SOTA coding agent (`Coding Max`) on one `EpisodeEngine` path. (2) Harness builder: compose other agents from the same substrate. CLI is a client of `ApplicationService`, not a second brain.

### From A — executive reliability order (not a wave calendar)

"""
    from_a0 = retarget(extract(A, 112, 157))
    from_b1 = "\n### From B — executive decision and score-band ASPIRATION\n\n" + retarget(
        extract(B, 119, 165)
    )
    from_a36 = "\n### From A — final recommendation\n\n" + retarget(extract(A, 3391, 3425))
    from_a4 = "\n### From A — competency model\n\n" + retarget(extract(A, 532, 623))
    from_a29 = "\n### From A — definition of done by capability level\n\n" + retarget(
        extract(A, 2996, 3034)
    )
    from_b7 = "\n### From B — competency profiles\n\n" + retarget(extract(B, 828, 895))
    hydra = """
### From v2 — HYDRA TARGET (not a schedule)

Copied outcome text lives in [`technical.md`](technical.md) (v2 §7). This row does not authorize default multi-agent.

"""
    appendix = """
---

## Appendix: historical W-092-F* aliases

Old overlay IDs remain resolvable. They are **not** the living work board.

| Historical ID | Maps to | Notes |
|---|---|---|
| **W-092-F0** | MS-INSTRUMENT (partial; LDA health is present-docs/CI) | Historical `DONE` claim stays as history; do not treat as MS-* closure |
| **W-092-F1** | MS-CONTROL path + CMX-09 | Canonical product path |
| **W-092-F2** | MS-TRUTH | Alias `CMX-10A` |
| **W-092-F3** | MS-RESUME | Alias `CMX-10B` |
| **W-092-F4** | MS-SEE / MS-CHANGE | Alias `CMX-11` |
| **W-092-F5** | MS-CONTROL qualification | Blocked on MS-TRUTH…MS-SEE |
| **W-092-F6** | MS-SPECIALIST | `[PROPOSAL]` |

Historical W-092 overlay text (pre-PHASE-0):

"""
    hist_w092 = existing[
        existing.find("## 3. Capability Wave Overlay") : existing.find(
            "## 4. Post-M-10 Horizon"
        )
    ]

    (EXEC / "milestones.md").write_text(
        yaml_and_intro
        + preserved_m_gates
        + overlay
        + from_a0
        + from_b1
        + from_a36
        + from_a4
        + from_a29
        + from_b7
        + hydra
        + "\n---\n\n"
        + preserved_oct_swe
        + appendix
        + hist_w092,
        encoding="utf-8",
    )


def write_backlog() -> None:
    existing = (EXEC / "backlog.md").read_text(encoding="utf-8")
    existing = existing.replace(
        """relationships:
  - execution.active
  - execution.milestones
  - spec.core
  - repo-root-vision
""",
        """relationships:
  - execution.tasks
  - execution.milestones
  - execution.feature_spec
  - execution.technical
  - spec.core
  - repo-root-vision
lock_head: "66aa7a3c0c31"
version: 0.9.3
last_verified: 2026-09-03
purpose: Track proposed, approved, in-progress, blocked, and deferred capability packages. No sprint queue. Alias table maps T-NN and v2 SUB/TXN/SHD/PRG onto packages without restamping live SUB-01.
""",
    )
    existing = existing.replace(
        'purpose: Track proposed, approved, in-progress, blocked, and deferred capability packages and engineering work outside the active sprint WIP=1 constraint.\n',
        "",
    )
    existing = existing.replace(
        'IN_PROGRESS["IN_PROGRESS<br/>(Active in active.md)"]',
        'IN_PROGRESS["IN_PROGRESS<br/>(Checked in tasks.md)"]',
    )
    existing = existing.replace(
        "* **`APPROVED`**: Specification and falsifiers ratified; queued for active sprint execution once lane capacity (`WIP=1`) opens.\n"
        "* **`IN_PROGRESS`**: Actively under implementation by the assigned lane owner in [`active.md`](active.md).\n",
        "* **`APPROVED`**: Specification and falsifiers ratified; awaiting implementation. Team capacity is chosen later; there is no WIP=1 calendar in this file.\n"
        "* **`IN_PROGRESS`**: Actively under implementation; checkboxes live in [`tasks.md`](tasks.md).\n",
    )
    existing = existing.replace(
        "[`FEATURE_SPEC.md`](FEATURE_SPEC.md)",
        "[`spec.md`](spec.md)",
    )
    existing = existing.replace(
        "the WIP=1 lane in `active.md` records only the parts above",
        "the historical TUI lane recorded only the parts above",
    )

    queue_start = existing.find("## 3. Prioritized Next-Up Queue")
    xref_start = existing.find("## 4. Cross-References")
    head = existing[:queue_start]
    xref = existing[xref_start:]
    xref = xref.replace(
        "* **Active Execution Runway (WIP=1)**: [`tasks.md`](tasks.md)\n"
        "* **Active Feature Delta Specification**: [`FEATURE_SPEC.md`](FEATURE_SPEC.md)\n",
        "* **Flat task tree**: [`tasks.md`](tasks.md)\n"
        "* **Feature delta specification**: [`spec.md`](spec.md)\n"
        "* **Technical handbook**: [`technical.md`](technical.md)\n",
    )
    # FEATURE_SPEC already replaced globally; handle remaining FEATURE_SPEC in xref
    xref = xref.replace("FEATURE_SPEC.md", "spec.md")

    extra = """## 3. Package index (not a sprint queue)

Team capacity is chosen later. `requires:` edges live on tasks. This index maps packages to T-ids.

| Package | Aliases | Related T-ids | MS-* | Notes |
|---|---|---|---|---|
| **INSTRUMENT** | REL-01R (related) | T-01–T-03, T-24–T-25, T-40–T-41 | MS-INSTRUMENT | Enumerator, SHA, dry-run ban |
| **TRUTH** | CMX-10A, W-092-F2, v2 SUB-01† | T-04–T-08, T-42, T-38, T-23 | MS-TRUTH | †v2 SUB-01 = admission, **not** live backlog SUB-01 (kernel pipeline, DONE) |
| **STATE** | CMX-10B, W-092-F3 | T-09–T-13, T-43–T-44 | MS-RESUME | `domain/task_state.py` MISSING |
| **SEE** | CMX-11, PRG-01, W-092-F4 | T-14–T-16, T-36–T-37, T-45–T-46 | MS-SEE | One ContextCompiler; ResultDistiller T-36 |
| **CHANGE** | TXN-01, SHD-01, TLS-04/05 | T-17–T-20, T-47–T-49 | MS-CHANGE | 2PC in adapters; tamper; completeness |
| **DIALECT** | WRN-01, TLS-02 | T-21–T-22, T-50 | — | Typed failure classes; fail-closed resolve |
| **CONTROL** | CMX-07, W-092-F5 | T-26–T-27, T-51–T-52 | MS-CONTROL | Frozen preregistration + canary |
| **META** | MEM-03 | T-28 | MS-META | `[PROPOSAL]` |
| **SPECIALIST** | CMX-06, W-092-F6 | T-29–T-30, T-53 | MS-SPECIALIST | `[PROPOSAL]` |
| **CAMPAIGN** | OCT-01…04, HYD-01/02 | T-31, T-54–T-55, T-34 | MS-CAMPAIGN / MS-HYDRA | `[PROPOSAL]`; director is runtime client |
| **MEMORY** | MEM-01, MEM-04 | T-32, T-56–T-57 | MS-MEMORY | `[PROPOSAL]` product wiring; ADR-0100 |
| **OFFICIAL** | REL-03, SWE-P5 | T-33, T-58 | MS-OFFICIAL | G-3; local ≠ official |
| **LATTICE** | SUB-01 (live kernel) | T-35, T-64 | — | TCB / boundaries / I-7 AST ban |
| **CLI** | TUI-01 (related) | T-59–T-60 | — | Facade stays thin |
| **PACKS** | CMX-01, CMX-04 | T-61–T-63 | — | Task-class policy; classifier; bypass |
| **DOCS** | DOC-* | T-67–T-68 | — | Promote landed contracts; link repair |
| **MUTATION** | VER-02, TLS-06 | T-39 | — | `[PROPOSAL]` optional ≥ 0.80 |

### v2 ID → T-id aliases (not a second DAG)

| v2 / old ID | Canonical T-id | Collision note |
|---|---|---|
| v2 `SUB-01` (admission) | T-04 / T-05 | Distinct from backlog **SUB-01** S0–S12 `DONE` |
| `TXN-01` | T-17 | |
| `SHD-01` | T-18 | |
| `PRG-01` | T-15 | Not a second compiler |
| `PRG-02` / ResultDistiller | T-36 | |
| `WRN-01` | T-21 | |
| `WRN-02` pager | T-37 | |
| `VER-01` fail-to-pass | T-38 | Bugfix class only |
| `VER-02` mutation | T-39 | `[PROPOSAL]` |
| `HYD-01` / `HYD-02` | T-55 | `[PROPOSAL]` |
| `CMX-10A` | T-04–T-08 cluster | |
| `CMX-10B` | T-09–T-13 cluster | |
| `CMX-11` | T-14–T-20 cluster | |
| `W-092-F2` | MS-TRUTH | See milestones appendix |
| `OCT-01` / `OCT-02` | T-54 | Keep existing OCT rows above |

Existing CMX-01…CMX-11, REL-*, OCT-*, TLS-*, MEM-*, TUI-01, SUB-* rows in §2 remain authoritative for lifecycle state. Do not restamp **SUB-01**.

---

## 5. Decision register (from A §32)

"""
    extra += retarget(extract(A, 3156, 3216))
    extra += "\n---\n\n## 6. Open research questions (from A §33)\n\n"
    extra += retarget(extract(A, 3220, 3282))
    extra += "\n---\n\n## 7. Risks (from A §27 and B §19)\n\n### From A\n\n"
    extra += retarget(extract(A, 2891, 2965))
    extra += "\n### From B\n\n"
    extra += retarget(extract(B, 1513, 1537))
    extra += "\n---\n\n"

    (EXEC / "backlog.md").write_text(head + extra + xref, encoding="utf-8")


def write_feature_spec_stub() -> None:
    (EXEC / "FEATURE_SPEC.md").write_text(
        """---
id: execution.feature_spec.pointer
canonical_id: execution.feature_spec.pointer
class: execution
authority: execution
status: living
owner: repository-governance
purpose: Historical filename pointer. The delta contract lives in spec.md.
---

# FEATURE_SPEC.md

This filename is a **pointer**. The living feature-delta contract is [`spec.md`](spec.md).
""",
        encoding="utf-8",
    )


def banner_draft(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "Unused reference." in text:
        return
    # Insert after YAML front matter
    parts = text.split("---", 2)
    if len(parts) < 3:
        path.write_text(BANNER + text, encoding="utf-8")
        return
    new = "---" + parts[1] + "---\n\n" + BANNER + parts[2].lstrip("\n")
    path.write_text(new, encoding="utf-8")


def main() -> None:
    EXEC.mkdir(parents=True, exist_ok=True)
    write_technical()
    write_spec()
    write_tasks()
    write_milestones()
    write_backlog()
    write_feature_spec_stub()
    banner_draft(A)
    banner_draft(B)
    banner_draft(V2)
    print("wrote execution set + draft banners")
    for p in sorted(EXEC.glob("*.md")):
        print(f"  {p.name:20s} {sum(1 for _ in p.open())} lines")
    for p in (A, B, V2):
        print(f"  {p.name:40s} {sum(1 for _ in p.open())} lines")


if __name__ == "__main__":
    main()
