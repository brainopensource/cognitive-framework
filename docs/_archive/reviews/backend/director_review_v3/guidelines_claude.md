---
id: director-review-v3-autonomous-two-lane-guidelines
class: review
authority: non-authorizing
canonical_for: []
status: proposal
owner: engineering-review
version: "3.0.0"
last_verified: 2026-08-27
subordinate_to: ../../../../../VISION.md
supersedes: []
superseded_by: null
---

# AETHER — Autonomous Two-Lane Development Methodology and M-1 → M-10 Delivery Report

**Subject:** `feat_higgs_M4_M8` @ `c3dc123` (working tree, 2026-08-27)
**Method:** code-first. Every claim below was produced by executing the tree, reading source, or
querying git. Documentation claims were re-verified, not inherited.
**Purpose:** replace the current approval-gated operating model with an autonomous, linear,
two-lane, code-first methodology that carries M-1 → M-10 to a buildable, operational AETHER v0.9.

> This document is a **proposal at layer 6** of the precedence ladder. It authorizes nothing on its
> own. It becomes operative when the Project Owner adopts §7 (ownership), §10 (decision model) and
> §12 (verification), and the two lane plans described in §14 are written from it.

---

## Table of Contents

| # | Section |
|---|---|
| 0 | [Executive verdict](#0-executive-verdict) |
| 1 | [Current-state diagnosis (measured)](#1-current-state-diagnosis-measured) |
| 2 | [Documentation vs implementation — classification matrix](#2-documentation-vs-implementation--classification-matrix) |
| 3 | [Reconstruction of M-1, M-2, M-3 from the repository](#3-reconstruction-of-m-1-m-2-m-3-from-the-repository) |
| 4 | [Architectural decisions to freeze](#4-architectural-decisions-to-freeze) |
| 5 | [Conflicts between documents, and their correction](#5-conflicts-between-documents-and-their-correction) |
| 6 | [Release-version sequence](#6-release-version-sequence) |
| 7 | [Principles of the autonomous methodology](#7-principles-of-the-autonomous-methodology) |
| 8 | [Complete lane ownership model](#8-complete-lane-ownership-model) |
| 9 | [M-1 → M-10 roadmap as linear work packages](#9-m-1--m-10-roadmap-as-linear-work-packages) |
| 10 | [Work-package / task template](#10-work-package--task-template) |
| 11 | [Autonomous decision model](#11-autonomous-decision-model) |
| 12 | [Branch and integration model](#12-branch-and-integration-model) |
| 13 | [Minimum verification model](#13-minimum-verification-model) |
| 14 | [Coding standards](#14-coding-standards) |
| 15 | [Research requirements](#15-research-requirements) |
| 16 | [Structure of the two future implementation plans](#16-structure-of-the-two-future-implementation-plans) |
| 17 | [Final TODO table](#17-final-todo-table) |
| 18 | [Immediate next steps](#18-immediate-next-steps) |

---

# 0. Executive verdict

**The architecture is sound and largely built. The operating model is the defect. The project is not
blocked by engineering; it is blocked by an acceptance protocol that structurally cannot terminate
with the staffing that exists.**

Five findings drive everything that follows.

1. **The substrate is real and it runs.** 2,003 automated tests execute in 64 seconds. Twenty of
   twenty-two static architectural linters pass, including `check_boundaries`, `check_tcb_budget`
   (kernel within its 1,438 logical-LOC ceiling), `check_domain_blindness`, `check_execution_truth`,
   `check_isolation_policy` and `scan_secrets`. The hexagonal lattice
   `domain → ports → kernel → agency → runtime → adapters` is machine-enforced and holds.

2. **The most-cited blocking document is materially stale.** `TODO_PROMPT.md` §1.2 lists four "P0
   blocking classes." Three of the four were **already repaired in the tree at HEAD** and the fourth
   is misdescribed:
   - "The standalone CLI embeds a literal Ed25519 operator seed and auto-approves every governance
     challenge." — **No such seed exists at HEAD**; `scan_secrets.py` passes; `vg init` provisions
     per-install operator key material.
   - "`RuntimeService.publish_event` writes two stores and ignores the canonical result." —
     **Repaired.** `service.py:1002 _append_canonical` allocates the sequence and appends inside one
     lock against one store, raises `NotAvailableError` on failure, and notifies subscribers strictly
     after commit.
   - "`ResolveApproval` verifies nothing." — **Repaired.** `service.py:447` loads the pending
     challenge from canonical history and enforces registered-key, `argsDigest`,
     `descriptorDigest`, `expiresAt` correspondence, expiry, and signature before appending any fact.
   - "M-7 topology has a complete library with **zero call sites** in the public runtime." —
     **False at HEAD.** `root.py:283-294` parses and lowers the topology inside `run_composed` and
     fails closed on a non-sequentially-schedulable plan.

   Only the fourth item, M-8 memory authorization, remains genuinely partial — and even there
   `ports/memory.py:MemoryAccess.permitted()` is now a real issuer/subject/action/expiry/revocation
   check, not the string-emptiness test the guide describes. The fail-open branch survives **only**
   in the explicitly-non-production `InMemoryMemoryPort` fake.

3. **The measured failures are trivial and mechanical, not architectural.** Nineteen non-green
   tests, from exactly **three** root causes: a one-character path bug, and two model-price drifts.
   All three are single-commit fixes (§1.3). None touches an invariant.

4. **The real blocker is administrative and is not solvable by the current team.** Four evidence
   bundles exist on disk with valid independent reviewer envelopes. Three of them still read
   `undeterminable`. `sprint_active.md` marks `C1-GATE` as **BLOCKED** on "Leadership", a role that
   does not exist. `sprint_upcoming.md` blocks WP-A2 on "C1 independent acceptance outstanding."
   `WP-B1` is blocked on a `CONVERGENCE-BASE-v1` tag whose creation is reserved to Leadership. The
   producer structurally cannot supply its own acceptance — which is correct policy under ADR-0101
   and simultaneously a permanent deadlock under two-lane staffing. **Milestones M-4, M-5a, M-5b,
   M-7 and M-8 are all `PACKAGE_READY`/`OPEN` for this reason, not for want of code.**

5. **M-9 and M-10 have no specification of any kind, and the release-version sequence is
   contradictory.** `docs/SPEC.md:199-200` assigns v0.9.0 to M-7 and v0.9.x to M-8; `README.md` and
   the v2 DEVPLAN assign v1.0 to M-9; the Project Owner requires v0.9 **after M-10**. Three
   incompatible statements. §6 resolves them.

**Verdict:** proceed. Delete the approval layer, keep the verification layer, freeze the
architecture as-is, convert every open gate into an owner plus an operational default, and hand two
self-contained linear plans to Lane A and Lane B. The engineering distance from HEAD to a
buildable, operational v0.9 is **three mechanical repairs, two genuine implementation milestones
(M-8 durable memory/learning, M-7 live three-topology execution), and two entirely new milestones
(M-9 product integration, M-10 release hardening)**. Everything else is already in the tree.

---

# 1. Current-state diagnosis (measured)

## 1.1 Repository facts

| Fact | Measured value |
|---|---|
| Branch / HEAD | `feat_higgs_M4_M8` @ `c3dc123` |
| Commits reachable | 545 |
| Tags in repo | `v0.0.0-sprint0`, `v0.4.0-sprint4`, `v0.4.1-beta`, `M-5-BASE`, `M-5A-BASE-v2` |
| Declared package version | `vanguard-runtime 0.7.3.dev0` (`pyproject.toml`) |
| Python source files | 206 under `vanguard/` |
| Test modules | 239 under `test/` |
| Static linters | 22 under `tools/linters/` |
| CI workflows | `.github/workflows/ci.yml`, `.github/workflows/clean-candidate.yml` |
| Domain packs | `code-default`, `code-explain`, `formal-sat`, `formal-graph-coloring` |
| Console scripts | `vanguard`, `vanguard-evaluator`, `vanguard-daemon`, `vanguard-studio` |

**Critical observation on tags.** `docs/SPEC.md` assigns versions v0.6.0 → v0.7.3.dev0 to
M-0 … M-6. **No tag in the repository corresponds to any of them.** The newest tag is
`v0.4.1-beta`. The version ladder in SPEC is a documentation artifact with no release provenance.
This is not a defect to repair retroactively; it is a fact the new plan must stop depending on.
Tagging discipline restarts at M-8 (§6).

## 1.2 Source size distribution

| Package | Lines | Character |
|---|---:|---|
| `runtime/` | 20,225 | Composition, session, service, registry, governance, studio. The centre of gravity. |
| `adapters/` | 9,233 | Models, evaluators, sandbox, stores. |
| `domain/` | 8,665 | Values, wire contracts, JCS, ledger reducers, evidence. |
| `agency/` | 2,467 | Episode engine, context compiler, manifests. |
| `kernel/` | 1,747 raw / ~1,365 logical | TCB. Ceiling 1,438 logical. **Passes.** |
| `ports/` | 1,457 | Hexagonal interfaces + 5 SPI protocols. |

`runtime/` at 20k lines against a 1.4k-line kernel is the correct shape for this architecture
(domain-blind kernel, everything else as composition), but it is also the single file-contention
risk for a two-lane model. §8 partitions it explicitly.

## 1.3 Executed verification — actual results

```
python3 -m unittest discover -s test -t .
→ Ran 2003 tests in 64.186s — FAILED (failures=2, errors=17, skipped=8)
```

`TODO_PROMPT.md` §3.2 reports "1995 tests, 3 failures, 8 skipped". The tree has moved; that
baseline is superseded.

**Root cause A — 17 errors, one character.**
`vanguard/packages/agency/manifests/loader.py:24-25`:

```python
SCHEMA_PATH       = Path(__file__).resolve().parents[3] / "schemas" / "v4"  / "harness-manifest.schema.json"
NAMED_SCHEMA_PATH = Path(__file__).resolve().parents[3] / "schemas" / "mhf" / "manifest_v2.schema.json"
```

From `vanguard/packages/agency/manifests/loader.py`, `parents[3]` resolves to `vanguard/`, not the
repository root. The schemas live at repo-root `schemas/`. The loader therefore raises
`ManifestLoadError: Manifest schema is unavailable: .../vanguard/schemas/v4/harness-manifest.schema.json`
and **every manifest load fails closed**. This kills 17 tests across
`test/agency/test_manifest_loader`, `test_manifest_gene_digests`, `test_reconstructions`,
`test_approval_policy`, `test_manifest_metamorphic`, `test/contracts/test_manifest_v2_graph`,
`test_b0_baseline_characterization`, and `test/adapters/test_tableworld`.

The bug was introduced at `60a1c14` and preserved unchanged through `545ea36 feat(M-3): V0.6.1`.
Fix: `parents[3]` → `parents[4]`, or better, resolve through an explicit repository-root anchor so
the path survives packaging (see §14 and A-M1-02). **This is also a packaging blocker**: an
installed wheel has no repo-root `schemas/` directory at all, so the same failure will occur for
every installed user. It is not merely a test bug; it is the first M-9 defect, already present.

**Root cause B — 2 failures, model price drift.**
- `test/adapters/test_model_routing.py:25` — `prompt_micros_per_1m` expected `150_000`, tree has
  `140_000`.
- `test/adapters/test_openrouter.py:339` — computed `cost_usd` 0.000145 vs expected 0.00024.

Provider pricing was changed in the routing table without updating the paired accounting vectors.
This is a **contract-vector desynchronization**, exactly the class Lane B owns.

**Static gates — executed:**

| Linter | Result |
|---|---|
| `check_boundaries` | PASS |
| `check_tcb_budget` | PASS |
| `scan_secrets` | PASS |
| `check_domain_blindness` | PASS |
| `check_isolation_policy` | PASS |
| `check_execution_truth` | PASS |
| `check_stale_paths` | PASS |
| `check_event_coverage` | PASS |
| `check_duplication` | PASS |
| `check_evidence_acceptance` | PASS |
| `check_doc_metadata` | PASS |
| `check_markdown_links` | **FAIL** — 3 broken links (`docs/README.md` → two missing archived proposals; `director_review_v0/003_V060_DIRECTOR_REVIEW.md` → missing `../ARCHIVE.md`) |

## 1.4 Classification of the current state

**Valid architecture — preserve unchanged.**
Domain-blind kernel with S0–S12 dispatch and monotonic attenuation; four-dimensional additive budget
algebra (`usd_micros`, `millis`, `tokens`, `bytes`) with structural `depth`/`turns` ceilings;
single-writer SQLite-WAL event store; `State = fold(events)`; canonical chain
`mhf.manifest/2 → CanonicalManifest → FrozenComposition → ActivationPlan → RunPlan → EpisodeEngine`;
`D_H`/`D_R`/`D_X` identity separation; RFC 8785 JCS canonicalization; `AgentView` as a fold, not an
object; capability-mediated effects; assurance profiles (`product`/`local`/`sandboxed`/`hermetic`)
that fail closed; generator/evaluator/promoter separation as distinct protocols.

**Stale documentation — supersede.**
`TODO_PROMPT.md` §1.2 (three of four P0s repaired, one misdescribed) and §3.2 (test baseline moved);
its tool paths (`check_boundaries.py`, `scan_secrets.py`) omit the `tools/linters/` directory that
actually holds them. `docs/SPEC.md:199-200` version rows. `README.md` §1 "Coding agent product …
RF-95 bundle/review absent" (the bundle exists and is signed). `sprint_active.md` "Verified
baseline" block, pinned to `15fbb75` plus an uncommitted diff that has since been committed across
Waves 5B–9B.

**Missing code — genuine work.**
Durable memory adapters (SQLite metadata + CAS blob + lexical index) behind `ports/memory.py`;
production wiring of the memory ports into `RunPlan`/`EpisodeEngine`; a durable CAS composition
registry with real promotion and executed rollback; a shipped composition that actually declares
`agent.spawn` so multi-role topologies can execute live; the entire M-9 product surface (the CLI
exposes only `init`, `doctor`, `run`); the entire M-10 release surface (no wheel/sdist build job, no
migration tooling, no packaged schema resources).

**Unresolved decisions — all administrative.**
ADR-0099 (M-7 scheduler disposition: bounded read concurrency vs `SEQUENTIAL_CONFIRMED`) is written
but its input measurement M7-01 was never run. `CONVERGENCE-BASE-v1` is undefined and reserved to a
non-existent role. M-4/M-6 re-execution is authorized but unassigned. Every one of these is
converted to an owner and a default in §11.

**Duplicated concepts.**
Two memory subsystems coexist: legacy `adapters/stores/memory_engine.py` and the M-8
`ports/memory.py` + `runtime/memory.py` contracts, with `runtime/memory.py`'s own docstring
acknowledging it "sits beside the legacy IMemoryEngine." Two event schema versions
(`mhf.event/1`, `/2`) — correct and intentional under dual-read/single-write, but a live
compatibility surface. Two service surfaces: the in-process `Runtime` and the JSON-RPC
`RuntimeService` (11 commands) plus `studio_gateway`. Two CLIs: the Python `vanguard` entry point
and the TypeScript/Ink `vg` under `vanguard/clients/cli/`.

**Purely administrative blockers — delete.**
`C1-GATE` (owner: "Leadership", state: BLOCKED). "Independent reviewer" as a mandatory distinct
human under ADR-0101 §3. WP-A2's entry gate "C1 independent acceptance outstanding." The Leadership
reservation on creating `CONVERGENCE-BASE-v1`. The `Review gate` paragraph closing `backlog.md`.
The "Director developer control" and "Leadership helper" tables in `sprint_active.md`. The
`sprint_active` / `sprint_upcoming` / `backlog` / `milestones` four-board authorization ceremony.

---

# 2. Documentation vs implementation — classification matrix

Code-first. Each row was checked against source at HEAD.

| # | Documented obligation | Source of claim | Code evidence | Class |
|---|---|---|---|---|
| 1 | Domain-blind kernel, S0–S12, TCB ≤ 1438 logical LOC | SPEC A-1, I-7 | `kernel/dispatch.py`; `check_tcb_budget` PASS; `check_domain_blindness` PASS | **Implemented** |
| 2 | Hexagonal lattice enforced on every commit | SPEC, README §4 | `check_boundaries` PASS | **Implemented** |
| 3 | Single-writer canonical event append | I-4, M-2 anchor | `service.py:1002 _append_canonical` — one lock, one store, raise-on-failure, notify-after-commit | **Implemented** (was regressed; repaired) |
| 4 | Verified approval resolution (I-5) | SPEC, WP-C1 | `service.py:447 _cmd_ResolveApproval` — challenge lookup, key registration, digest correspondence, expiry, signature | **Implemented** (was regressed; repaired) |
| 5 | No embedded operator key material | WP-C1 falsifier | `scan_secrets` PASS; `vg init` provisions per-install key | **Implemented** |
| 6 | `mhf.event/1` byte-immutable; `/2` is the writer; readers dual-read | SPEC refusals | `domain/ledger/events.py:207-260` branches on `schema_version` for both | **Implemented** |
| 7 | `mhf.trajectory/2` single-write, `/1` readable | SPEC | `runtime/trajectory.py:157,219,397` | **Implemented** |
| 8 | `AgentView` as event-derived projection with checkpoints | M-5a | `domain/ledger/agent_view.py`; `session.py:749 fold_agent_view` | **Implemented** |
| 9 | Fresh-process cold continuation (RF-25) | I-4/I-9 | `adapters/stores/event_store.py:SqliteEventStore`; CI job "Replay parity (F-02, cold fold from disk)" | **Implemented** |
| 10 | Canonical recursive child runtime, no synthetic success | M-6 | `runtime/child_runtime.py`, `delegation.py`; WP-A1 merged at `ca683fd` | **Implemented** |
| 11 | M-7 topology lowering bound into the one public run path | M-7, WP-A3 | `root.py:283-294` `parse_topology`/`lower_topology`, fail-closed | **Implemented** — contradicts `TODO_PROMPT` §1.2 ("zero call sites") |
| 12 | Topology carries no authority | M-7 | `topology.py:172 _reject_authority` | **Implemented** |
| 13 | Three topologies execute live (direct; planner/executor/reviewer; fork/read/merge) | M-7 gate | Shipped default composition declares no `agent.spawn`; multi-role live execution fails closed | **Partial** |
| 14 | M7-01 independence/completeness measurement → ADR-0099 | M-7 gate | No `lab/m701_independence.py`; no M7-01 envelope in `docs/03_execution/evidence/` | **Missing** |
| 15 | Verified, scoped, revocation-aware memory authorization at use time | ADR-0100 | `ports/memory.py:MemoryAccess.permitted()` — issuer, subject, actions, expiry, revocation, verification receipt; `MemoryAuthorizationPort.verify` HMAC-bound; falsifiers in `test/security/test_m8_memory_falsifiers.py` | **Implemented** (contract layer) — contradicts `TODO_PROMPT` §1.2 ("`bool(non_empty_string)`") |
| 16 | Durable category stores (knowledge/experience/project/skills) | ADR-0100 | Only `InMemoryMemoryPort` (81 LOC, self-declared "non-production compatibility fake"); `adapters/stores/` holds no memory adapter | **Missing** |
| 17 | Authorization precedes ranking and dereference | ADR-0100 | Enforced in the fake; no production path exists to enforce it in | **Partial** |
| 18 | Retrieval provenance reaches model context | ADR-0100 | `RetrievalProvenance` produced by the fake; consumed only by `test/runtime/test_m8_turn_loop.py`. `agency/episode/engine.py` has **no** memory import | **Partial** |
| 19 | Fail-closed memory authorization with no fail-open branch | ADR-0100 | `runtime/memory.py:43,56` — `access.permitted() or (grant_ref and tenant and project and not revoked)`. **The fail-open branch survives in the fake.** | **Regressed** (scoped to the fake; must be deleted, not patched) |
| 20 | Retention/GC/legal hold/quarantine for memory | ADR-0100, WP-A4 | No implementation | **Missing** |
| 21 | Generator / evaluator / promoter as distinct authorities | ADR-0100, VISION | `runtime/skill_lifecycle.py` (91 LOC) — separate `Protocol`s, `promotable` requires 5 independent passes | **Implemented** (protocol layer) |
| 22 | Durable CAS composition registry, atomic promotion, executed rollback | M-8 gate | `governance/learning.py` (495 LOC) + `skill_evaluation.py` (519 LOC) exist; no durable CAS registry adapter; no executed rollback receipt | **Partial** |
| 23 | Held-out lift measured on a sealed workload | M-8 gate | No sealed-workload manifest, no lift report | **Missing** |
| 24 | Manifest schema loads from a packaged location | implicit | `agency/manifests/loader.py:24` `parents[3]` → wrong directory; 17 test errors | **Regressed** |
| 25 | Model routing table and cost vectors agree | A-4 one-schema | 2 failing accounting tests | **Regressed** |
| 26 | All markdown links resolve | doc gate | `check_markdown_links` FAIL ×3 | **Regressed** |
| 27 | M-4 RF-95 evidence bundle, signed, accepted | M-4 gate | `M-4-rf95-candidate-03.json` + `.acceptance.json` present, signed, envelope valid; producer outcome `undeterminable` (empty `preregistration_digest`; artifact in volatile tmpdir) | **Partial** |
| 28 | M-6 canonical recursion evidence | M-6 gate | `M-6-canonical-recursion.json` + acceptance; `pins.dirty == true` | **Partial** |
| 29 | M-5b generality evidence | M-5b gate | `M-5b-graph-coloring.json` + acceptance; `undeterminable` pending successor baseline | **Partial** |
| 30 | M-6.5 paired study accepted | M-6.5 gate | `M-6.5-attributable-paired-study.json` + acceptance envelope, verified | **Implemented / ACCEPTED** |
| 31 | `CONVERGENCE-BASE-v1` annotated remote tag + signed baseline manifest | ADR-0102 | Does not exist. Only `M-5-BASE` and `M-5A-BASE-v2` (contaminated, unpublished) | **Missing** |
| 32 | SPEC version ladder v0.6.0 → v0.7.3 | SPEC:190-202 | No corresponding tag exists in the repository | **Obsolete** |
| 33 | M-7 = v0.9.0, M-8 = v0.9.x | SPEC:199-200 | Contradicts README (M-9 = v1.0) and the Owner's target (v0.9 after M-10) | **Contradictory** |
| 34 | "Standalone CLI embeds a literal Ed25519 seed and auto-approves" | `TODO_PROMPT` §1.2.1 | Not present at HEAD | **Obsolete** |
| 35 | "`publish_event` writes two stores" | `TODO_PROMPT` §1.2.2 | Not present at HEAD | **Obsolete** |
| 36 | "M-7 library has zero call sites" | `TODO_PROMPT` §1.2.4 | Not true at HEAD | **Obsolete** |
| 37 | Linters live at `tools/check_*.py` | `TODO_PROMPT` §3.2 | They live at `tools/linters/check_*.py` | **Obsolete** |
| 38 | Clean install produces a working `vanguard` | implicit M-9 | `install_vanguard.sh` writes a `PYTHONPATH` shim hardcoded to `/usr/bin/python3` pointing back at the source checkout. This is a dev alias, not an install. | **Partial** |
| 39 | Distributable wheel/sdist | implicit M-10 | `pyproject.toml` declares scripts and `package-data`, but `schemas/` and `packs/` sit **outside** the `vanguard*` package tree and are not packaged; no build job in CI; `python -m build` unavailable | **Missing** |
| 40 | Product CLI surface (workflows, plugins, config) | M-9 | `cli.py` exposes `init`, `doctor`, `run` only | **Missing** |
| 41 | Service API surface | M-9 | 11 JSON-RPC commands in `service/contract.py`; frozen public protocol not declared | **Partial** |
| 42 | Ledger/schema migration tooling | M-10 | None | **Missing** |
| 43 | Two-lane staffing | `sprint_active.md` | Board assigns work to Dev A, Dev B, **Leadership**, and an independent reviewer | **Contradictory** |
| 44 | `dev-C` ownership removed | v2 convergence plan P0-04 | Still referenced as a defect to remove; no `dev-C` assignment survives in the active board | **Obsolete (already resolved)** |

**Summary counts:** implemented 15 · partial 10 · missing 9 · obsolete 6 · regressed 4 ·
contradictory 2. The mass of "missing" sits entirely in M-8 durability, M-9 and M-10 — which is
exactly where no plan has ever existed.

---

# 3. Reconstruction of M-1, M-2, M-3 from the repository

Nothing here is invented. Each milestone is reconstructed from `docs/SPEC.md`'s compatibility table
(the only surviving normative statement of M-0…M-3), cross-checked against surviving code, tests,
CI jobs and ADRs.

## M-0 — CI truth and falsifiers (declared v0.6.0)

**Obligation.** Establish executable falsifiers F-01…F-21 and a CI that cannot pass on unknown.
**Surviving evidence.** `.github/workflows/ci.yml` names the falsifiers inline: F-20 (`test_repo_paths`),
F-13 (`generate_types.py --check`), F-16 (`check_duplication.py --enforce`), F-02 (`ColdReplayParity`).
`tools/linters/check_falsifier_ids.py` enforces the identifier registry.
**Status.** Implemented and preserved. **Carry forward:** the falsifier-ID discipline and the
"unknown is never a pass" rule (§13).

## M-1 — Signed Ed25519 trust spine and verdicts (declared v0.6.0)

**Obligation.** An exterior signed judge; forged or unsigned verdicts fail closed (I-5).
**Surviving evidence.** `adapters/evaluators/daemon.py`, `gate.py`, `signing.py`;
`runtime/governance/approvals.py` (618 LOC); `runtime/keys.py`; container identity separation
(worker UID 10001 vs evaluator UID 10002 in `containers/`); `test/trust/`, `test/security/`.
**Regression history.** `runtime/service/` entered the tree outside the package system and briefly
nullified I-5 on the service path. Repaired in WP-C1; verified at HEAD (§1.3, matrix rows 4-5).
**Status.** Implemented, previously regressed, now restored. **Carry forward:** every security field
is explicitly parsed with no default; a verifier that cannot run reports `not_available`, never pass.

## M-2 — One runtime, truthful trajectory, cold continuation (declared v0.6.1)

**Obligation.** RF-23 truthful `mhf.trajectory`, RF-25 fresh-process continuation, exactly one event
writer.
**Surviving evidence.** `runtime/ledger_emitter.py` (436 LOC, single writer);
`adapters/stores/event_store.py` (`SqliteEventStore`, WAL); `runtime/trajectory.py` +
`trajectory_reader.py`; CI's cold-fold replay-parity job; `test/runtime/test_ledger_truth.py`.
**Regression history.** The service-layer dual write; repaired (matrix row 3).
**Status.** Implemented and preserved. **Carry forward:** the one-writer anchor is constitutional
(§4). Every new subsystem — memory, promotion, migration — appends through this writer or does not
append.

## M-3 / M-3C — Composition graph, plugin lifecycle, layer-0 removal (declared v0.6.2)

**Obligation.** RF-78…RF-84 canonical composition, activation, durability, evidence; removal of the
legacy "layer 0"; a graph/lifecycle contract for plugins.
**Surviving evidence.** `runtime/registry/` (lifecycle FSM, isolation broker, worker wire,
composition compiler); `runtime/compose.py`, `activation.py`, `run_plan.py`, `root.py`;
`agency/manifests/loader.py` with `mhf.manifest/2`; `schemas/mhf/manifest_v2.schema.json`;
`test/registry/` (a dedicated CI job); ADR-0088 (`m3c-m8-concept-lock`).
**Status.** Implemented. **Open residue:** `sprint_active.md` records "M-3 falsifier closure remains
active," and the manifest loader is currently broken by the `parents[3]` path bug (matrix row 24) —
i.e. the M-3 surface is the one carrying a live regression into M-4→M-10.
**Carry forward:** the canonical chain and the fail-closed manifest validation are constitutional.

## What M-1→M-3 means for the new plan

M-1→M-3 are **not to be reimplemented**. They become **Wave 0**: one audit-and-repair package per
lane that (a) fixes the three measured regressions, (b) proves each historical anchor still holds
with a named executable check, and (c) publishes the baseline commit the whole roadmap builds on.
That is roughly two days of work, not a milestone of construction.

---

# 4. Architectural decisions to freeze

These are **constitutional invariants**. A lane may not change them by local decision; changing one
requires an explicit written successor decision recorded in `docs/02_decisions/` **by the owning
lane** (not by an approval authority) plus a falsifier demonstrating the old rule's failure.

**Kernel and authority**
1. The kernel is domain-blind. No spawn, topology, strategy, memory, or learning semantics enter it.
   `agent.spawn` is a generic S0–S12 effect; post-intent child creation lives in a runtime adapter.
2. TCB is the transitive closure actually reachable from dispatch, not "whatever is under
   `kernel/`". The 1,438 logical-LOC ceiling stands.
3. Two authority systems: capability grants constrain agents; plugin isolation constrains plugin
   code. Neither trusts the other's subject.
4. A new authority verb requires a bound falsifier plus a TCB accounting delta. Everything else
   lands as packs, plugins, manifests, adapters, policies, or exterior pipelines.
5. Capability mediation is at the point of use. Authorization precedes ranking, dereference, and
   any content read.

**Events, state and identity**
6. Events are truth. `State = fold(events)`. Persisted history is never rewritten.
7. Exactly one event writer. Sequence allocation and append occur in one transaction against one
   store; subscribers are notified only after commit.
8. Runtime is the only concrete composition seam. `agency` never imports `runtime`.
9. The canonical chain is
   `mhf.manifest/2 → CanonicalManifest → FrozenComposition → ActivationPlan → RunPlan → EpisodeEngine`.
   Compatibility formats normalize at ingress and never become a second runtime value.
10. An agent is a projection: `Identity + Policy + Event-Derived Projection + Execution Boundary`.
    No state required for semantic continuation exists only in a live object.
11. `D_H` (composition), `D_R` (runtime/environment/model/oracle), `D_X` (dataset/protocol) are
    never collapsed.
12. Replay (fold over recorded facts) and re-execution (running the work again) are distinct
    operations with distinct guarantees and are never conflated in evidence.
13. Fresh-process cold continuation is the proof of durability. An in-memory double fold proves
    nothing.

**Content, budgets, retention**
14. Large content lives in the content-addressed artifact store; the ledger carries digests and
    references. `GoalDeclared` carries a digest, never raw goal text.
15. Additive resources are exactly `usd_micros`, `millis`, `tokens`, `bytes`. `depth` and `turns`
    are structural ceilings, not costs. Attenuation is monotonic; a child never widens a parent.
16. Retention is `digests_only | standard | full` and is **orthogonal to** capture authorization.
17. Timing is telemetry. It never mutates an event, a budget dimension, or a verdict.

**Schemas and compatibility**
18. JSON Schema + JCS + golden vectors are the wire source of truth; readers are generated.
19. `mhf.event/1` and `mhf.trajectory/1` are byte-frozen. New writers single-write `/2`; readers
    dual-read `/1|/2`. Historical identities are never rewritten.
20. Specifications are generated **or** normative, never both.

**Evidence and learning**
21. Evidence-ledger failure is fatal. Required capture failure is fatal. Optional degradation is
    admissible only after a durable `capture_incomplete` fact, and the run becomes non-evidentiary.
22. Reproducibility distinguishes *capability* (WAL + pins present) from *executed verification*
    (immutable run-bound receipts). Never report the former as the latter.
23. Generator, evaluator and promoter are semantically separate authorities with separate keys and
    stores. An agent has no method to promote itself. Rollback is a signed CAS operation that must
    change served runtime behaviour.
24. Assurance profiles (`product`/`local`/`sandboxed`/`hermetic`) are identity-bearing, enter `D_R`,
    and fail closed when the requested containment is unavailable. They never silently fall back.

**What is explicitly *not* frozen** (and therefore is a lane decision):
event-kind roster additions within `/2`; checkpoint cadence and defaults; ranking function and
tokenizer inside memory retrieval; scheduler policy inside the sequential/bounded-read envelope;
CLI command naming; storage engine choice behind a port; test organization; module decomposition
inside a lane's owned files.

---

# 5. Conflicts between documents, and their correction

| # | Conflict | Correction |
|---|---|---|
| C-1 | Documents audited at `f9d7ceb` / `624d80f` / `15fbb75`; HEAD is `c3dc123`, ~9 doc waves later | **All prior audits are historical.** The single baseline for both lane plans is the commit produced by Wave 0 (§9). No plan may cite a file, symbol or line number not re-verified at that commit. |
| C-2 | `TODO_PROMPT` §1.2 lists 3 repaired P0s + 1 misdescribed | Strike §1.2 entirely. The surviving true residue is M-8 durability (matrix rows 16-20, 22-23) and it is scheduled as Lane A M-8 packages. |
| C-3 | `TODO_PROMPT` §3.2 baseline (1995/3/8) vs measured (2003/2 failures/17 errors/8 skipped) | Replace with the Wave-0 measured baseline; then make the suite green so the baseline is a boolean, not a count. |
| C-4 | Linter paths `tools/check_*.py` vs actual `tools/linters/check_*.py` | Mechanical; every plan and script references `tools/linters/`. |
| C-5 | SPEC:199-200 (M-7 = v0.9.0, M-8 = v0.9.x) vs README/DEVPLAN (M-9 = v1.0) vs Owner (v0.9 after M-10) | Resolved in §6. Single ladder; SPEC rows are superseded. |
| C-6 | SPEC version ladder v0.6.0…v0.7.3 has **no corresponding tags** | Stop treating the ladder as release provenance. Declare it historical nomenclature. Tagging restarts at M-8 (§6). |
| C-7 | Ownership model names Dev A, Dev B, **Leadership**, and an independent reviewer; only two lanes exist | Delete Leadership and the mandatory distinct reviewer. Lane A and Lane B are permanent owners; each self-reviews and integrates (§8, §12). |
| C-8 | `dev-C` cited by the v2 plan as a defect to remove | Already absent from the active board. Ensure no lane plan reintroduces it. |
| C-9 | `C1-GATE` state `BLOCKED`, owner Leadership; blocks WP-A2, and transitively M-7 and M-8 | **Delete `C1-GATE`.** Replace with the wave integration check (§13). WP-A2's entry gate becomes "WP-A1 merged," which is already true (`ca683fd`). |
| C-10 | ADR-0101 §3 requires a reviewer distinct from the producer; two lanes cannot both produce and independently accept | Retain **producer-separation for cryptographic signing** (each lane signs its own bundles with its own key) but drop *acceptance* as a human act. Acceptance becomes: bundle verifies, its declared falsifiers pass, its pins are clean and non-dirty, and its artifacts are portable. Determinable-vs-undeterminable is a machine outcome. Cross-lane counter-signature is available where a lane's output is the other lane's input, and is mechanical, not judgmental. |
| C-11 | `CONVERGENCE-BASE-v1` gated on Leadership creating a tag | **Lane A owns baseline tags.** Wave 0 creates and pushes the annotated baseline tag with a signed manifest. No approval. |
| C-12 | M-4/M-6 bundles are `undeterminable` (empty `preregistration_digest`; volatile-tmpdir artifact; `pins.dirty=true`) | These are **instrument defects, not milestone failures**. Wave 0 fixes the runner (thread `TaskContext.preregistration`; export portable artifacts; refuse to run on a dirty tree), then re-executes once. The re-execution is scheduled work, not an authorization event. |
| C-13 | ADR-0099 (M-7 scheduler) is "pending" and blocks M-7 acceptance; its input M7-01 was never run | ADR-0099 stays a **record**, not a gate. Lane B runs M7-01. **Default: `SEQUENTIAL_CONFIRMED`.** Bounded read concurrency is adopted only if preregistered thresholds pass with zero divergence. Either outcome closes M-7. |
| C-14 | ADR-0100 named as a precondition for M-8 wiring ("no public composition wiring is added before ADR-0100" — `runtime/memory.py` docstring) | ADR-0100 is **accepted and in the index**. The precondition is satisfied. Lane A wires memory. |
| C-15 | "No M-9/M-10 feature or scaffold" (`sprint_active.md`, `milestones.md`) vs the objective of delivering v0.9 after M-10 | **Lift the prohibition** at Wave 0. Preserve its intent as an invariant: M-9/M-10 introduce **no kernel semantics and no second runtime**. Integration, packaging and operations are not architectural expansion. |
| C-16 | Four concurrent boards (`milestones`, `backlog`, `sprint_active`, `sprint_upcoming`) with divergent states | Collapse to **two lane plans** (§16) plus `milestones.md` as a stable gate reference. `sprint_active.md` and `sprint_upcoming.md` are retired; the lane plan's own cursor is the current work. |
| C-17 | Two memory subsystems (legacy `memory_engine.py`, M-8 ports) | Lane A designates `ports/memory.py` canonical, marks `memory_engine.py` deprecated-in-place, and deletes it once no import survives. Deletion, not adaptation. |
| C-18 | `InMemoryMemoryPort` retains a fail-open authorization branch | Delete the `or (...)` branch outright. A fake that is more permissive than production is a falsifier that cannot fire. |
| C-19 | `check_markdown_links` fails on archived documents | Lane B repairs or removes the three links in Wave 0; this gate returns to green and stays blocking. |
| C-20 | README §1 claims RF-95 bundle/review "absent" | Stale; bundles exist and are signed. README is refreshed once at Wave 0 and then only at release boundaries. |

---

# 6. Release-version sequence

## The conflict

Three incompatible statements exist in the tree:

- `docs/SPEC.md:199` — **M-7 = v0.9.0**; `:200` — **M-8 = v0.9.x**; `:201` — M-9/M-10 "post-MVP".
- `README.md` roadmap and `AETHER_DIRECTOR_DEVPLAN.md:1250` — **M-9 = v1.0**.
- Project Owner objective — **v0.9 delivered after M-10**.

Additionally the whole ladder v0.6.0 → v0.7.3 has **zero corresponding tags**, so no version claim
in SPEC has release provenance.

## Recommendation — one coherent ladder

| Milestone | Version | Meaning | Tag |
|---|---|---|---|
| M-1 … M-6.5 | *historical, untagged* | Development line. Nomenclature only. | — |
| Wave 0 (M-1→M-3 audit/repair) | `0.7.3` | First tagged baseline in the new model. Green suite, green linters, portable artifacts. | `v0.7.3` (annotated, signed, pushed) |
| M-7 | `0.7.5` | Three topologies live through one runtime; scheduler disposition recorded. | `v0.7.5` |
| M-8 | `0.8.0` | Durable authorized memory + governed learning. **Feature-complete substrate.** | `v0.8.0` |
| M-9 | `0.8.5` | Product integration: CLI/API/TUI, config, plugins, real workflows, clean install. **Operational beta.** | `v0.8.5` |
| M-10 | `0.9.0` | Reliability, performance, migration, security, deployment, packaging, release hardening. **Buildable, operational AETHER v0.9.** | `v0.9.0` |
| post-M-10 | `1.0.0` | Frozen public protocol + compatibility policy + field validation on real users. **Not a milestone; an earned promotion.** | `v1.0.0` |

## Rationale

- It satisfies the Owner's requirement literally: **v0.9.0 ships at the end of M-10**, nothing earlier.
- It keeps every pre-M-10 release in the `0.x` range, which is the honest signal for a substrate
  whose public JSON-RPC protocol (11 commands) is not yet frozen. Shipping v0.9.0 at M-7 would
  imply near-API-stability for a system that then goes on to add durable memory, a promotion
  registry, and an entire product surface.
- It preserves the meaning SPEC intended (M-8 as the substrate boundary) while moving the numeric
  label, because SPEC's numbers were never bound to tags and cost nothing to correct.
- It removes v1.0 from the milestone ladder entirely. v1.0 is a **compatibility promise**, which
  cannot be earned by completing a milestone; it is earned by a frozen protocol surviving real
  external use. Binding it to M-9 (as README and the v2 DEVPLAN do) forces either a premature freeze
  or a broken promise.

## Consequences

1. `docs/SPEC.md:190-202` must be rewritten as one table matching the above. This is the **only**
   normative document edit required by the version decision.
2. `README.md` roadmap line ("… → M-9 v1.0") is corrected in the same pass.
3. The public JSON-RPC protocol is **explicitly declared unstable until M-10**, and frozen with a
   written compatibility policy as an M-10 deliverable. Until then, additive-only changes are
   permitted without ceremony; breaking changes require a version bump of the command envelope.
4. Wire schemas (`mhf.event/*`, `mhf.trajectory/*`, `mhf.manifest/*`) are **already** frozen under
   dual-read/single-write and are unaffected. Version numbering is a distribution concern, not a
   wire concern; do not couple them.
5. `M-8 is the MVP boundary` (`milestones.md:116`, `SPEC.md:200`) is preserved in substance —
   M-8 = v0.8.0 = feature-complete substrate — with M-9/M-10 as productization on top.
6. Anyone holding a "v0.9 = M-7" expectation must be told once, explicitly, that the label moved.

---

# 7. Principles of the autonomous methodology

Ten rules. They replace the entire approval apparatus.

**P-1 — Human approval disappears; technical verification does not.**
No task, wave, milestone or release waits for a person to agree. Every one of them completes when a
named, automated, deterministic check passes. Deleting the checks would make "done" an opinion;
deleting the approvals only removes latency.

**P-2 — Ownership is permanent, exclusive, and file-level.**
Every file in the repository has exactly one owning lane. A lane never edits the other lane's files.
Merge conflicts between lanes become structurally impossible rather than procedurally managed.

**P-3 — Contracts are frozen before the wave, not negotiated during it.**
Each wave opens with a Contract Kit: schemas, interfaces, payload examples, golden vectors, stubs
and fixtures, published by the owning lane. Both lanes then implement against the kit. Neither lane
ever consumes the other's unfinished branch.

**P-4 — WIP is one work package per lane.**
A lane holds exactly one open package. Linear sequence, no parallel fronts inside a lane, no
context-switching cost, no half-finished surfaces at integration time.

**P-5 — Integration is mechanical and belongs to whoever finishes second.**
The lane that reaches wave-complete second performs the merge in the pre-declared order. Mechanical
conflicts are resolved by the integrator. Semantic conflicts are routed to the owner of the
contract, who decides. No meeting, no negotiation, no third party.

**P-6 — Every decision has an owner and a default.**
No decision is ever "pending." It has a named owner, an enumerated option set, a selection rule, and
a fallback that applies automatically if the rule cannot be evaluated. The owner decides, records one
paragraph of rationale, and continues.

**P-7 — A negative experimental result is a decision, not a stop.**
Experiments select between pre-declared branches. M-6.5 negative → controller stays off by default.
M-7 negative → `SEQUENTIAL_CONFIRMED`. M-8 lift negative → promotion ships disabled with the
registry intact. In all cases the milestone **closes** and the roadmap advances.

**P-8 — Done is behavioural, buildable, and checked.**
A package is done when the behaviour exists, the tree builds, and the package's own declared
automated checks pass on a clean checkout. Not when it is reviewed. Not when it is approved.

**P-9 — Unknown is never a pass.**
A check that cannot run reports `not_available` and the package is not done. Producing an
`undeterminable` result is a defect in the instrument, assigned back to the instrument's owner —
never rounded up to success and never escalated to a human for interpretation.

**P-10 — Constitutional invariants are the only thing a lane cannot decide.**
§4 lists them. Inside those bounds a lane has total authority over its own surface. Outside them,
nothing may change silently; a written successor decision plus a falsifier is required, and the
owning lane writes it.

**Explicitly abolished:** Leadership gates · approval checklists · manual sprint promotion · Tech
Lead as integration owner · Director as decision owner · mandatory independent human reviewer ·
ADRs as authorization requests · concurrent boards with divergent state · unowned open tasks ·
waiting on decisions about internal detail · requiring a positive experimental result to proceed ·
ceremonial sprints · full-suite execution after every commit.

**Explicitly retained:** falsifier-first development · signed evidence bundles · digest-addressed
artifacts · producer key separation · fail-closed defaults · `unknown ≠ pass` · the static
architectural linters · cold-replay parity · clean-checkout release validation.

---

# 8. Complete lane ownership model

## 8.1 Charter

**Lane A — Execution.** Runtime, kernel-adjacent integration, causal infrastructure, persistence,
delegation, topology execution, memory storage, service layer, CLI, packaging, deployment,
operations.

**Lane B — Contracts.** Schemas, wire contracts, projections, verification instruments, experiments,
generality, evaluation, memory retrieval semantics, skills, learning evaluation, promotion criteria,
release qualification.

The split is **write-path vs meaning-path**: Lane A owns what happens; Lane B owns what it means and
whether it is true.

## 8.2 Exclusive file ownership

| Path | Owner | Notes |
|---|---|---|
| `vanguard/packages/kernel/**` | **A** | Frozen surface. Change requires a §4 successor decision. |
| `vanguard/packages/runtime/**` except below | **A** | Lane A's centre of gravity (20k LOC). |
| `vanguard/packages/runtime/{skill_evaluation,paired_evaluation,pareto_measurement,scoring,outcome_labels}.py` | **B** | Measurement/evaluation logic. |
| `vanguard/packages/runtime/governance/learning.py` | **B** | Promotion criteria. Lane A owns `governance/{approvals,engine,definitions}.py`. |
| `vanguard/packages/agency/**` | **A** | Episode engine, context, manifest loading. |
| `vanguard/packages/adapters/models/**`, `adapters/stores/**`, `adapters/sandbox/**`, `adapters/environment/**` | **A** | Concrete I/O. |
| `vanguard/packages/adapters/evaluators/**` | **B** | Exterior judge, oracles, suites. |
| `vanguard/packages/domain/**` | **B** | Values, wire contracts, JCS, ledger reducers, evidence models, `AgentView`. |
| `vanguard/packages/ports/**` | **Shared, B-authored** | B writes the interface; A implements it. B may not add a method without publishing it in a Contract Kit first. |
| `schemas/**` | **B** | Wire source of truth. |
| `packs/**` | **B** | Domain packs and their harnesses. |
| `vanguard/clients/cli/**` (TypeScript/Ink) | **A** | Product surface. |
| `tools/linters/**`, `tools/codegen/**` | **B** | Verification instruments. |
| `tools/runners/**` | **B** | Evidence runners and bundle tooling. |
| `test/kernel`, `test/runtime`, `test/agency`, `test/registry`, `test/adapters` | **A** | |
| `test/contracts`, `test/falsifiers`, `test/security`, `test/trust`, `test/packs`, `test/benchmarks` | **B** | |
| `test/integration`, `test/fixtures`, `test/support` | **Shared** | Additive only; never edit the other lane's existing case. |
| `.github/workflows/**`, `Makefile`, `pyproject.toml`, `requirements.lock`, `install_vanguard.sh`, `containers/**` | **A** | Build, packaging, deployment. |
| `benchmarks/**`, `lab/**`, `evidence/**`, `docs/03_execution/{prereg,evidence}/**` | **B** | |
| `docs/01_law/**`, `docs/02_decisions/**`, `docs/05_contracts/**`, `docs/06_protocols/**` | **B** | Normative text. |
| `docs/04_architecture/**`, `docs/07_engineering/**`, `README.md` | **A** | As-built description. |
| `VISION.md`, `docs/SPEC.md` | **Frozen** | Edited only for a §4 successor decision or the §6 version table. |

**Contention resolution rule.** If a package requires an edit to a file the other lane owns, the
requesting lane does **not** edit it. It writes the requirement into the wave's Contract Kit; the
owning lane implements it as the first item of its next package. If the requirement blocks the
requester, the owner publishes a **stub** with the final signature and a `NotImplementedError` body
in the Contract Kit within the same wave, and the requester proceeds against the stub.

## 8.3 Shared contracts (the only cross-lane surface)

Six contracts cross the lane boundary. Each has one authoring owner and one consumer, both frozen
before the wave that uses them.

| Contract | Author | Consumer | Frozen at |
|---|---|---|---|
| `ports/memory.py` — `MemoryAccess`, `MemoryAuthorizationPort`, `KnowledgePort`, `ExperiencePort`, `ProjectMemoryPort`, `SkillLibrary`, `RetrievalProvenance`, `MemoryResult` | B | A | Wave 4 kit |
| `runtime/topology.py` — `Topology`, `RunPlanExtension`, `lower_topology` output shape | A | B | Wave 3 kit |
| `aether.evidence/1` envelope + `tools/runners/build_evidence_bundle.py` output | B | A | Wave 0 kit |
| `mhf.event/2` kind roster + `mhf.trajectory/2` fields | B | A | Wave 0 kit, additive thereafter |
| `runtime/service/contract.py` — JSON-RPC command roster and error codes | A | B | Wave 5 kit; frozen for good at M-10 |
| `ports/meta_controller.py` + `domain/ledger/progress.py` — `ProgressProjection/2` | B | A | already frozen (ADR-0103) |

## 8.4 Anti-idleness queue

When a lane finishes its package and the next one is genuinely gated on the other lane's
integration, it draws from its own pre-declared auxiliary queue rather than starting the next
package or idling:

- **Lane A:** performance profiling of append/fold/checkpoint; adapter hardening; crash-boundary
  fault injection; `docs/04_architecture/` as-built refresh; container image slimming; CLI UX.
- **Lane B:** golden-vector expansion; falsifier coverage for existing invariants; benchmark corpus
  growth; pack authoring; schema documentation; linter strengthening.

Auxiliary work is committed to the lane's own branch and never creates a divergent surface.

---

# 9. M-1 → M-10 roadmap as linear work packages

Eight waves. Each wave is a pair `(A-package, B-package)` built against a frozen Contract Kit and
closed by a mechanical integration check. Packages are strictly sequential inside a lane.

## Wave 0 — Baseline audit and repair (covers M-1, M-2, M-3)

**Target version:** `v0.7.3`. **Nothing is rewritten. Everything is verified or repaired.**

| | Lane A: `A-W0` | Lane B: `B-W0` |
|---|---|---|
| **Objective** | Make the tree green, buildable, and tagged; publish the baseline every later package cites. | Prove each M-1→M-3 anchor still holds with a named executable check; repair contract-vector drift; publish the Wave-0 Contract Kit. |
| **Tasks** | A-001 fix `agency/manifests/loader.py:24-25` path resolution and make schema location packaging-safe (importlib resources or an explicit root anchor) — clears 17 test errors. A-002 make `schemas/` and `packs/` installable package data so an installed wheel can load manifests. A-003 replace `install_vanguard.sh`'s `/usr/bin/python3` PYTHONPATH shim with a real `pip install .` path. A-004 fix `tools/runners/run_rf95_product_proof.py` to thread `TaskContext.preregistration` into the trajectory and export portable artifacts outside any tmpdir. A-005 make every evidence runner refuse to execute on a dirty working tree (kills `pins.dirty`). A-006 create, sign and push the annotated `v0.7.3` baseline tag with a signed baseline manifest (this **is** `CONVERGENCE-BASE-v1`; use the semantic name). A-007 re-execute M-4 RF-95 candidate 04 and M-6 depth≥3 recursion against the clean tagged subject. | B-001 fix `test_model_routing` / `test_openrouter` price vectors and add a linter binding the routing table to the accounting vectors so they cannot drift again. B-002 repair the 3 broken markdown links; `check_markdown_links` returns to blocking-green. B-003 write `test/falsifiers/test_m1_m3_anchors.py`: one named executable check per anchor — S0–S12 dispatch order, monotonic attenuation, budget conservation, one-writer append, `/1` byte immutability, cold fresh-process fold, canonical-chain uniqueness, fail-closed manifest validation, assurance-profile no-silent-fallback. B-004 delete the fail-open `or (...)` branch in `InMemoryMemoryPort`. B-005 publish the Wave-0 Contract Kit: `aether.evidence/1` envelope, `mhf.event/2` roster, `mhf.trajectory/2` field list, golden vectors. B-006 rewrite `docs/SPEC.md:190-202` to the §6 version ladder and correct the README roadmap line. |
| **Exit check** | `python3 -m unittest discover -s test -t .` → **0 failures, 0 errors**; all 22 linters green; `pip install .` in a clean venv yields a working `vanguard doctor`; `v0.7.3` resolves on the remote; M-4 and M-6 bundles read `determinable/pass` with non-dirty pins and portable artifacts. | Same suite green; `test_m1_m3_anchors` present and passing; Contract Kit committed under `docs/05_contracts/kits/W0/`. |

**Wave 0 closes M-1, M-2, M-3, M-4, M-5a, M-6 and M-6.5.** M-5b closes when B re-runs the
graph-coloring falsifier against `v0.7.3` as the control (B-007, same wave, no new instrument
needed — the pack and oracle already exist).

## Wave 1 — M-7 topologies and scheduler disposition

**Target version:** `v0.7.5`.

| | Lane A: `A-W1` | Lane B: `B-W1` |
|---|---|---|
| **Objective** | Make all three topology patterns execute live through `Runtime.run_composed`, and instrument correlated timing. | Measure operation independence and completeness; select the scheduler disposition; record ADR-0099. |
| **Tasks** | A-101 author (or extend) a shipped composition that declares `agent.spawn`, so planner/executor/reviewer and fork/read/merge are executable rather than fail-closed. A-102 execute all three patterns end-to-end: direct; planner→executor→reviewer; planner→2 readers→merger. A-103 `TelemetrySink` with monotonic start/end correlated by run, episode, operation, descriptor, idempotency, process epoch — never written into an event or a budget. A-104 prove disabled-topology parity: identical `D_H`/`D_R` and identical event stream with topology absent. A-105 malformed / authority-bearing / cyclic / unknown-role / crash-and-replay fail-closed cases. | B-101 `lab/m701_independence.py` (read-only): eligible-pair model — no causal order, disjoint proven selectors, compatible sinks, safe idempotency, complete timing. Unknown or missing data **serializes and counts incomplete**. B-102 report: eligible duration, critical path, sequential makespan, completeness ratio, contention, simulated bounded-read lift with intervals. B-103 order-metamorphism and missing-data-conservatism falsifiers. B-104 write ADR-0099 with the measured result. |
| **Decision** | — | **Rule:** adopt read-only `max_parallelism=2` only if preregistered thresholds pass with zero state/verdict divergence and no duplicate privileged occurrence. **Default: `SEQUENTIAL_CONFIRMED`.** Writes, spawn, promotion, and shared/unknown sinks stay sequential in either branch. Either outcome closes M-7. |
| **Exit check** | Three topologies produce three signed bundles; disabled-path parity is byte-identical; suite + linters green. | M7-01 bundle verifies; ADR-0099 present with a concrete disposition; suite + linters green. |

## Wave 2 — M-8a durable authorized memory

**Target version:** `v0.8.0-dev`.

| | Lane A: `A-W2` | Lane B: `B-W2` |
|---|---|---|
| **Objective** | Implement durable, authorized, recoverable memory behind the frozen ports. | Own the retrieval semantics, provenance contract, and the security falsifier corpus. |
| **Tasks** | A-201 SQLite-WAL scoped metadata store (tenant, project, category, selector, invalidation, retrieval receipts) under `adapters/stores/memory_store.py`. A-202 CAS blob storage for content; ledger holds digests only. A-203 lexical index adapter; refuse WAL on a network filesystem. A-204 wire the four category ports into `RunPlan` and the turn loop so retrieval provenance reaches model context. A-205 `ClaimRecorded(memory.recorded/1)` through the **single canonical writer**. A-206 invalidation, revocation-epoch enforcement, retention/GC with legal hold, quarantine for metadata-without-causal-fact, orphan detection for blob-only writes. A-207 crash-boundary and restore tests at every transaction seam. A-208 delete `adapters/stores/memory_engine.py` once no import survives. | B-201 finalize `ports/memory.py` (Wave-2 kit): `verify → AuthorizedMemoryContext` binding issuer, subject, action, selector, tenant, project, purpose, time, revocation epoch, policy, receipt. B-202 ranking contract: quantized scores, ties broken by record ID, tokenizer pinned into the receipt. B-203 authorization-before-ranking-before-dereference ordering falsifiers. B-204 forgery / expiry / revocation / cross-scope / cross-category / pre-rank-leak / cache-leak falsifiers; every denial is opaque (`Denied`, `DID_NOT_OCCUR`). B-205 provenance-reaches-context falsifier: the model's context contains the authorized refs and nothing else. B-206 performance vectors: atomic 4 KiB write p95 < 50 ms; lexical recall p95 < 100 ms at 100k records, limit ≤ 20, on the declared host. |
| **Exit check** | All B-2xx falsifiers pass against Lane A's durable implementation; crash/restore round-trips; no fail-open branch anywhere; kernel diff empty. | Same, plus performance vectors within target or an explicitly recorded declared-host deviation. |

## Wave 3 — M-8b governed learning and rollback

**Target version:** `v0.8.0`.

| | Lane A: `A-W3` | Lane B: `B-W3` |
|---|---|---|
| **Objective** | Durable CAS composition registry, atomic promotion, executed rollback that changes served behaviour. | Sealed evaluation, held-out lift measurement, promotion criteria, contamination falsifiers. |
| **Tasks** | A-301 durable composition registry over SQLite CAS with compare-and-swap on expected generation; stale CAS loses. A-302 promoter adapter: verify report signature, base digest, head digest, then swap. A-303 rollback as a signed CAS operation; assert the **served** composition behaviour actually changes. A-304 separate keys and stores for generator, evaluator, promoter. A-305 concurrent-promoter, missing-transition-receipt (→ quarantine), and every crash-boundary case. A-306 restart-durability of the promoted generation. | B-301 candidate pipeline from trajectories; sealed manifest binding base, candidate skills/policies, retrieval policy, generator identity and sources. B-302 **seal dev / held-out / adversarial / transfer digests before any evaluation runs.** B-303 paired evaluation recording present / retrieved / invoked / grounded / verified / outcome. B-304 promotion criteria: preregistered lift with CI, exact test, Holm correction, ≤5% baseline-success regression, zero critical security regressions. Presence-only gain is rejected. B-305 contamination falsifiers: generator cannot read held-out labels or promoter keys; evaluator cannot promote; role/key collapse is detected. B-306 injected-regression falsifier proving rollback fires. |
| **Decision** | — | **Rule:** if ≥1 composition shows preregistered held-out lift, promotion ships **enabled**. If not, promotion ships **disabled by default** with the registry, evaluation and rollback fully implemented and tested. **Either outcome closes M-8.** |
| **Exit check** | Rollback demonstrably alters served behaviour; concurrent promotion is serialized; restart preserves the promoted generation. | Sealed-workload evidence bundle verifies; every contamination falsifier fires on a deliberately broken variant and passes on the real one. |

## Wave 4 — M-9 product integration

**Target version:** `v0.8.5` — **operational beta**.

| | Lane A: `A-W4` | Lane B: `B-W4` |
|---|---|---|
| **Objective** | Turn the substrate into a product someone can install and use. | Prove the product does real work across domains, and qualify the operator experience. |
| **Tasks** | A-401 expand the CLI from `init`/`doctor`/`run` to the full product surface: `run`, `resume`, `status`, `logs`, `explain`, `approve`, `cancel`, `checkpoint`, `pack list/add/remove`, `config get/set`, `keys`, `doctor`, `version`. A-402 layered configuration — defaults → config file → environment → flags — with a single resolution function, `config get` showing provenance per key, and no silent fallback. A-403 plugin/pack lifecycle: discover, validate, activate, deactivate, remove; activation materializes a callable service or fails. A-404 freeze the JSON-RPC surface: version the command envelope, document all 11+ commands and the ten canonical error codes, and publish the compatibility policy (additive-only until M-10, then frozen). A-405 wire the TypeScript/Ink `vg` TUI to the frozen protocol; remove any path that bypasses it. A-406 clean install from a built wheel in a fresh container: `pip install vanguard-runtime && vanguard init && vanguard run …` with zero repository checkout. A-407 first-run experience: `vanguard init` provisions keys, workspace, default pack, and a working config in one command. | B-401 three real end-to-end workflows, one per domain family: a coding task through `code-default`; a formal task through `formal-graph-coloring`; a research/explain task through `code-explain`. Each runs to a verified terminal state with a complete trajectory. B-402 an operator scenario corpus: start → approve → cancel → checkpoint → resume → explain, executed against the frozen protocol. B-403 product-quality evaluation: success rate, cost, turns, and recovery per workflow, tracked against the Wave-0 baseline. B-404 a **third non-coding workload** proving generality beyond code, as the VISION requires. B-405 operator documentation generated from the frozen protocol, not written by hand. |
| **Exit check** | Clean-container install works; every CLI command has a passing smoke test; the protocol document is generated from `contract.py`. | Three workflows produce three verified bundles; the operator scenario corpus passes end to end. |

## Wave 5 — M-10 reliability and release hardening

**Target version:** `v0.9.0` — **the deliverable**.

| | Lane A: `A-W5` | Lane B: `B-W5` |
|---|---|---|
| **Objective** | Make it reliable, upgradeable, secure, deployable, and packaged. | Qualify the release and prove the qualification is reproducible. |
| **Tasks** | A-501 ledger and schema migration tooling: forward migration with digest-verified export/import, dry run, and a refusal to migrate an unrecognized version. A-502 recovery hardening: kill at every transaction boundary under fault injection; each one recovers or fails closed with a durable fact. A-503 performance: measure and set budgets for append, fold, checkpoint, retrieval, and end-to-end turn latency; regression-gate them. A-504 security enforcement pass: capability checks at every boundary, sandbox policy verification, secret handling, key rotation, dependency audit. A-505 deployment: container images, systemd/service unit, UDS and HTTP hardening (origin allowlist, size limits, authenticated commands), health and readiness endpoints. A-506 packaging: reproducible wheel + sdist, `schemas/` and `packs/` correctly included, checksums, a build job in CI, and an installation matrix across supported Python versions. A-507 backup/restore procedure for the ledger and CAS. | B-501 regression corpus consolidating every falsifier from Waves 0–4 into one release suite. B-502 failure-injection suite: process kill, disk full, corrupt index, clock skew, network partition on the evaluator RPC. B-503 compatibility suite: `mhf.event/1` and `/2` both read; `/1` bytes unchanged; every frozen schema round-trips its golden vectors. B-504 upgrade test: install `v0.8.5`, create a ledger with real runs, upgrade to `v0.9.0`, verify every historical run still folds, replays, and explains. B-505 release bundle: signed manifest binding commit, tree, lockfile, schema digests, test results, and performance numbers. B-506 the release qualification script — one command, exit code 0 or non-zero, no interpretation required. |
| **Exit check** | `bash ci/release_qualify.sh` exits 0 on a clean checkout in a clean container. | Same script, same result, executed independently from the release bundle's pins. |

**When that script exits 0, AETHER v0.9.0 is delivered.** That is the only completion criterion, and
no person needs to agree with it.

---

# 10. Work-package / task template

Every task in both lane plans uses exactly this template. A task that cannot fill every field is not
specified enough to hand over and must be split or investigated first.

```
### <LANE>-<NNN> — <imperative title>

1.  ID and position       — e.g. A-204; wave 2; after A-203; before A-205.
2.  Objective             — the functional result, in one sentence, stated as observable behaviour.
3.  Baseline              — the exact commit and the exact state of the files this starts from.
4.  Files and symbols     — every path this task may touch, and the functions/classes it adds or
                            changes. Files not listed here are out of scope by definition.
5.  Allowed code surface  — the lane-owned boundary; explicitly names what must NOT be touched.
6.  Public inputs/outputs — signatures, types, and the semantic contract of each.
7.  Contracts consumed    — schemas, ports, kits, golden vectors this task reads, with versions.
8.  Contracts produced    — schemas, ports, events, receipts this task publishes, with versions.
9.  Invariants preserved  — the §4 items this task is capable of breaking, and why it does not.
10. Behavioural pseudocode— causal order, I/O, error paths, and the invariant asserted at each step.
                            Specifies behaviour, not private helpers.
11. Normal cases          — the expected paths, enumerated.
12. Edge cases            — empty, boundary, concurrent, duplicate, out-of-order, oversized.
13. Error model           — every failure mode, its error code, whether it is fatal or degrading,
                            and what durable fact it appends. Degradation requires a durable fact.
14. Persistence/migration — what is written, where, in what transaction, and how existing data is
                            read forward. Never rewrite history.
15. Telemetry and events  — events emitted (kind + schema version) and telemetry recorded.
                            Telemetry never becomes an event or a budget dimension.
16. Compatibility         — backward and forward. Dual-read obligations. Frozen surfaces touched.
17. Performance           — the measurable budget, its declared host, and how it is measured.
18. Security              — capability checks, authorization order, denial opacity, key handling,
                            secret handling, isolation boundary.
19. Automatic completion  — the exact commands whose exit codes define "done". No prose criterion.
20. Build/check commands  — copy-pasteable; the developer runs these, not a described procedure.
21. Completion artifacts  — bundles, receipts, digests, or files that prove the task ran.
22. Rollback / flag       — how to disable or revert this task's effect without a code archaeology
                            expedition.
23. Next task             — the single task automatically unblocked by this one.
```

**Worked example** (abbreviated, from Wave 0, to fix the shape in the reader's mind):

```
### A-001 — Resolve manifest schema paths correctly and packaging-safely

 1. A-001; wave 0; first task; unblocks A-002.
 2. `ManifestLoader` loads `harness-manifest.schema.json` and `manifest_v2.schema.json` from both a
    source checkout and an installed wheel; the 17 manifest-load test errors go to zero.
 3. c3dc123, tree unmodified.
 4. `vanguard/packages/agency/manifests/loader.py` (SCHEMA_PATH, NAMED_SCHEMA_PATH, _load_schema).
 5. Lane A / agency. Do not touch `schemas/**` (Lane B) or any test under `test/contracts`.
 6. `ManifestLoader.validate_schema(raw: Mapping) -> None`; unchanged signature.
 7. `schemas/v4/harness-manifest.schema.json`, `schemas/mhf/manifest_v2.schema.json`.
 8. None.
 9. Fail-closed manifest validation (§4.9). A missing schema must still raise, never skip.
10. resolve schema root: try importlib.resources on the installed package; else walk up from
    __file__ to the directory containing both `schemas/` and `pyproject.toml`; else raise
    ManifestLoadError. Cache per-process. Never fall back to "skip validation".
11. Source checkout; installed wheel; editable install.
12. Missing file; unreadable file; malformed JSON; `api: mhf.manifest/2` selecting NAMED_SCHEMA_PATH.
13. `ManifestLoadError` in every failure case; fatal; no event.
14. None.
15. None.
16. No schema version change. Reader behaviour identical.
17. Schema load is once-per-process; no budget.
18. None (no authority, no secrets).
19. `python3 -m unittest discover -s test/agency -t . && python3 -m unittest discover -s test/contracts -t .`
    → 0 failures 0 errors; `python3 -m unittest test.adapters.test_tableworld` → 0 errors.
20. as above, plus `python3 tools/linters/check_boundaries.py`.
21. Test output showing 17 previously-erroring tests passing.
22. Revert the commit; behaviour returns to the current (broken) state.
23. A-002.
```

---

# 11. Autonomous decision model

## 11.1 The three decision classes

| Class | Who decides | How it is recorded | Can it be changed later |
|---|---|---|---|
| **Local implementation** — data structures, private helpers, module decomposition, naming, test organization, library choice behind a port | The developer, alone, while implementing | Code and its docstring. Nothing else. | Freely, by the same lane |
| **Shared contract** — anything crossing the lane boundary: schema fields, port signatures, event kinds, error codes, wire semantics, CLI surface | The **owning lane** (§8.3) | A Contract Kit entry, published before the wave that uses it | By publishing a superseding kit entry in a later wave; never mid-wave |
| **Constitutional invariant** — §4 | Nobody, silently | A written successor decision in `docs/02_decisions/` **plus** a falsifier demonstrating the old rule's failure, authored by the owning lane | Only by that mechanism |

**The rule that removes every remaining blocker:** if a decision is not constitutional, it is not a
decision that leaves the lane. It has an owner, and that owner decides today.

## 11.2 Every currently-open decision, resolved

| # | Decision | Owner | Options | Selection rule | Fallback | Consequence of the fallback |
|---|---|---|---|---|---|---|
| D-01 | Baseline commit for all plans | A | any commit | The first commit where the full suite and all 22 linters are green | Wave-0 exit commit | One incontestable baseline; all later citations are re-verified against it |
| D-02 | Release version ladder | A | §6 vs SPEC vs README | Owner objective: v0.9 after M-10 | §6 table | SPEC:190-202 and the README roadmap line are rewritten once |
| D-03 | `CONVERGENCE-BASE-v1` creation | **A** (was Leadership) | create / defer | Create as soon as Wave 0 is green | Tag `v0.7.3` and use that name everywhere | M-5b unblocks immediately; the ADR-0102 name becomes an alias |
| D-04 | M-4 / M-6 `undeterminable` bundles | A | re-run / waive / accept | Fix the instrument, then re-run once against the clean tag | Re-run | `undeterminable` is an instrument defect, never a milestone verdict (P-9) |
| D-05 | Independent human reviewer (ADR-0101 §3) | A + B jointly, once | keep / drop / mechanize | Cannot be satisfied by two lanes | Mechanize: bundle verifies + declared falsifiers pass + pins clean + artifacts portable = accepted | Producer key separation is retained; human judgment is removed |
| D-06 | M-5a event-kind roster additions | B | roster shape | Smallest additive change preserving `/1` and dual-read | Additive `/2` kinds only | No migration; readers unaffected |
| D-07 | Checkpoint cadence and defaults | B | interval / turn-count / event-count | Choose by benchmark against fold cost | Conservative: checkpoint every N turns where N is the smallest value with <3% overhead | Slightly larger ledgers; correctness unaffected |
| D-08 | M-5b formal oracle | B | SAT / graph-coloring / other | Simplest deterministic verifier with no search | `formal-graph-coloring` (already implemented) | Zero new instrument work |
| D-09 | Confidence / progress signal set | B | signal roster | Versioned signals; **no single signal is ever authoritative** | `ProgressProjection/2` as frozen by ADR-0103 | Already frozen; no work |
| D-10 | M-7 scheduler concurrency | B measures, A implements | bounded read parallelism / sequential | Preregistered thresholds AND zero divergence AND no duplicate privileged occurrence | **`SEQUENTIAL_CONFIRMED`** | M-7 closes either way; ADR-0099 records the measurement |
| D-11 | Shipped composition declaring `agent.spawn` | A | extend `code-default` / new pack | Whichever requires no change to a Lane-B-owned pack | New Lane-A-owned topology test composition | Three topologies become live-executable without touching Lane B's packs |
| D-12 | M-8 memory lifecycle event shape | B | full event kinds / typed claims | Smallest compatible change | Typed `ClaimRecorded(memory.recorded/1)` | No new kind roster entry; dual-read unaffected |
| D-13 | Memory storage engine | A | SQLite-WAL / other | Must match the existing ledger engine; must refuse network filesystems | SQLite-WAL | One engine, one backup story, one migration story |
| D-14 | Blob GC and legal hold policy | A | — | Retention policy is separate from execution retention | Mark-and-sweep from causal roots, with legal hold and a reviewed dry run | No orphan blobs; no accidental deletion of held data |
| D-15 | Ranking function and tokenizer | B | — | Deterministic, quantized, tie-broken by record ID, pinned in the receipt | Lexical BM25-style with a pinned tokenizer | Reproducible retrieval; provenance is checkable |
| D-16 | Promotion enabled at ship | B | enabled / disabled-by-default | ≥1 composition shows preregistered held-out lift | **Disabled by default**, registry and rollback fully implemented | M-8 closes; promotion becomes a config flag, not a milestone |
| D-17 | Multi-tenancy scope | A implements, B verifies | in / out of v0.9 | In only if a shared server is part of the v0.9 product | **Out.** Tenant/project fields stay in the data model; no shared-server isolation work | Single-tenant v0.9; the seam exists for v1.x |
| D-18 | Distributed execution | A | in / out | In only if measured need exists after M-10 performance work | **Out** | Single-process v0.9; no scheduler rewrite |
| D-19 | JSON-RPC protocol freeze point | A | M-9 / M-10 | Freeze when the product surface stops changing | **M-10**; additive-only from M-9 | Honest `0.x` semantics until v0.9.0 |
| D-20 | Python version support matrix | A | 3.10+ / 3.11+ / 3.12+ | Whatever the lockfile and CI actually exercise | `>=3.10`, CI on 3.12, install matrix tested at M-10 | Matches `pyproject.toml` today |
| D-21 | Legacy `memory_engine.py` | A | adapt / deprecate / delete | No production import may survive M-8 | Delete at end of Wave 2 | One memory subsystem |
| D-22 | TypeScript `vg` TUI scope | A | full / thin / drop | Must consume only the frozen protocol | Thin client over the frozen JSON-RPC surface | No second ontology; no bypass path |
| D-23 | Where lane plans live | A + B | — | Version-controlled beside the code | `docs/03_execution/lane_a_plan.md`, `lane_b_plan.md` | Two files, two owners, one cursor each |
| D-24 | Retirement of the four-board system | A | — | On adoption of this report | Retire `sprint_active.md` and `sprint_upcoming.md`; keep `milestones.md` as a stable gate reference | One authoritative plan per lane |

**Nothing in this table returns to the Project Owner.** Every row has an owner who can act today and
a default that applies if the owner cannot evaluate the rule.

---

# 12. Branch and integration model

## 12.1 Branches

```
main                      ← protected; only wave-integration merges land here
  ├── lane-a              ← Lane A's long-lived working branch
  └── lane-b              ← Lane B's long-lived working branch
```

Two long-lived branches. No feature branches, no PR ceremony, no review requests. A lane commits to
its own branch continuously.

**Neither lane ever pulls the other lane's branch.** Cross-lane dependencies are satisfied by the
Contract Kit's stubs and fixtures, which live on `main` and are merged into both lanes at wave start.

## 12.2 The wave cycle

```
1. KIT      The owning lane publishes the wave's Contract Kit to `main`
            (schemas, port signatures, stubs, fixtures, golden vectors).
            Both lanes rebase onto it. The kit is frozen for the wave's duration.

2. BUILD    Lane A works A-branch. Lane B works B-branch. In parallel. Independently.
            Each runs its own local checks continuously (§13 level 1).

3. READY    A lane declares wave-ready when its package's declared completion commands
            all exit 0 on its own branch. It pushes and records the commit.

4. MERGE    The lane that reaches READY *second* performs the integration, in the
            pre-declared order for that wave (see 12.3). Not a negotiation — a procedure.

5. CHECK    The integrator runs the wave integration check (§13 level 2) on the merge
            result. Green → push to `main`. The wave is closed.

6. DEFECT   A failure in the integration check is triaged by file ownership:
              - failure inside Lane A's files  → assigned to Lane A
              - failure inside Lane B's files  → assigned to Lane B
              - failure at a contract boundary → assigned to the contract's *author*
            The assignee fixes it on their own branch and re-merges. The other lane is
            NOT blocked: it starts the next wave's build phase against the next kit.
```

## 12.3 Pre-declared integration order

| Wave | Order | Reason |
|---|---:|---|
| W0 | B then A | Contract vectors and anchors first; A's baseline tag is cut from the integrated result |
| W1 | A then B | B's M7-01 measurement requires A's live topology execution |
| W2 | B then A | Ports and falsifiers define the surface A implements against |
| W3 | A then B | The registry must exist before promotion can be evaluated against it |
| W4 | A then B | Workflows exercise the product surface |
| W5 | A then B | Qualification runs against the built artifact |

## 12.4 Rules that make this safe

- **No lane edits the other lane's files.** Enforced by review of ownership at integration; a
  cross-lane diff is an automatic integration failure with a named owner.
- **Shared test directories are additive-only.** Never modify the other lane's existing case.
- **Generated files** (`domain/wire/types_gen.py`) are regenerated, never hand-edited; the codegen
  check (`generate_types.py --check`) is part of every level-1 run.
- **The kit is frozen mid-wave.** A required kit change becomes a stub published immediately plus
  the real implementation in the next wave. The requester proceeds against the stub.
- **A blocked lane never idles and never starts the next package early.** It draws from its
  auxiliary queue (§8.4).
- **`main` is always green.** A merge that fails the integration check is not pushed; it is fixed on
  the assignee's branch first.

---

# 13. Minimum verification model

Four levels. Nothing above level 1 runs more often than it needs to; nothing below level 4 is
skipped before a release.

## Level 1 — Local check (developer, continuously, seconds)

Run by the developer while implementing. The only thing between a keystroke and a commit.

```bash
python3 -m unittest discover -s test/<the-lane's-directories> -t .
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/check_domain_blindness.py
python3 tools/codegen/generate_types.py --check
```

Plus the task's own `19. Automatic completion` commands. **No full suite. No linter sweep. No
approval.** Roughly 10–20 seconds.

## Level 2 — Wave integration check (integrator, once per wave, ~2 minutes)

Run on the merge result, by whichever lane merged.

```bash
python3 -m unittest discover -s test -t .          # full suite: 0 failures, 0 errors
for f in tools/linters/check_*.py tools/linters/scan_secrets.py; do python3 "$f" || exit 1; done
python3 tools/codegen/generate_types.py --check
python3 -m unittest test.runtime.test_ledger_truth.ColdReplayParity
git diff --stat main...HEAD                        # ownership check: no cross-lane files
```

Green → push. Red → §12.2 step 6.

## Level 3 — Build smoke test (per wave from W4 on; per release always, ~5 minutes)

```bash
python3 -m build                                    # wheel + sdist
python3 -m venv /tmp/smoke && /tmp/smoke/bin/pip install dist/*.whl
/tmp/smoke/bin/vanguard doctor                      # exit 0
/tmp/smoke/bin/vanguard init --workspace /tmp/ws
/tmp/smoke/bin/vanguard run --pack code-default --brief "<fixture task>"
```

This is the check that would have caught the `parents[3]` packaging bug two years of commits ago.
It becomes mandatory from Wave 4.

## Level 4 — Release qualification (once per tagged release, one command)

`ci/release_qualify.sh`, executed on a clean checkout in a clean container. It runs level 2, level 3,
then:

- three essential end-to-end scenarios (coding, formal, research), each to a verified terminal state;
- the operator scenario corpus (start → approve → cancel → checkpoint → resume → explain);
- the compatibility suite (`/1` and `/2` both read; `/1` bytes unchanged; golden vectors round-trip);
- the upgrade test (previous version's ledger folds, replays and explains under the new version);
- the failure-injection suite;
- the performance budgets;
- release-bundle signing.

**Exit code 0 is the release. No person interprets the output.**

## Defect assignment without blocking

- A defect is assigned by **file ownership**, mechanically. Contract-boundary defects go to the
  contract's author.
- The assignee fixes it on their own branch. **The other lane continues.** A defect never becomes a
  cross-lane stop.
- A defect that would require editing the other lane's file becomes a kit stub request, satisfied in
  the same wave (§8.2).

## Negative experimental results

| Experiment | Positive branch | Negative branch | Roadmap effect |
|---|---|---|---|
| M-6.5 meta-control | Enable per accepted profile | Controller stays **off by default** | none — already ACCEPTED |
| M-7 concurrency | `max_parallelism=2` for reads | **`SEQUENTIAL_CONFIRMED`** | none — M-7 closes either way |
| M-8 held-out lift | Promotion **enabled** | Promotion **disabled by default**, registry/evaluation/rollback shipped and tested | none — M-8 closes either way |
| M-10 performance budget | Budget met | Budget recorded as the measured value + a named follow-up task | none — v0.9 ships with honest numbers |

An experiment **terminates a decision**. It never becomes an administrative prison.

## What verification is deliberately absent

No external reviewer. No approval of a result. No quality committee. No repetitive manual execution.
No full suite after every small commit. No blocking wait for a human to interpret an outcome. No
milestone that closes by prose, aggregation, or waiver.

---

# 14. Coding standards

Binding on both lanes. These are the standards the existing codebase already mostly meets; they are
written down so a lane can check itself.

**Typing.** `from __future__ import annotations` everywhere. Full annotations on every public
signature. `Protocol` for ports, `@dataclass(frozen=True, slots=True)` for value objects. No `Any`
at a public boundary — parse it into a typed value at ingress. Prefer `Mapping`/`Sequence` in
parameters, concrete types in returns.

**Modularity.** One responsibility per module. A module that needs a table of contents needs
splitting. Public surface via explicit `__all__`. No circular imports; the boundary linter is the
arbiter.

**Dependency direction.** `domain ← ports ← kernel ← agency ← runtime → adapters`. Strictly.
`agency` never imports `runtime`. `domain` imports only stdlib. `kernel` is domain-blind and stays
within its logical-LOC ceiling. Every adapter is reachable only through a port.

**Errors.** Typed exceptions with a stable code. Fail closed: an unavailable verifier is
`not_available`, never a pass. No security-relevant field has a default value. Denials are opaque —
a caller learns "denied", never *why*, and never whether the resource exists. Degradation is
admissible only after appending a durable `capture_incomplete` fact, which makes the run
non-evidentiary. Only the canonical error-code set is emitted at the service boundary.

**Logging vs events vs telemetry.** Three distinct channels, never conflated. **Events** are durable
causal facts appended through the single writer. **Telemetry** is correlated measurement that never
mutates an event, a budget, or a verdict. **Logs** are operator-facing text carrying no authority.
Never log secrets, key material, raw goal text, or memory content.

**Serialization.** RFC 8785 JCS for anything digested. JSON Schema is the source of truth; readers
are generated (`tools/codegen/generate_types.py`) and never hand-mirrored. Golden vectors accompany
every schema. Additive changes only within a version; a breaking change means a new version with
dual-read.

**Persistence.** Single writer. Sequence allocation and append in one transaction against one store.
Notify subscribers only after commit. History is append-only and is never rewritten. Large content
goes to CAS; the ledger holds digests. Refuse WAL on a network filesystem. Every write path has a
crash-boundary test.

**Concurrency.** The turn loop is sequential (I-11). Locks are narrow, explicit, and never held
across I/O. Idempotency keys on every externally-triggered command. Concurrent durable settlement is
exactly-once per command identity; physical attempts are at-least-once. Compare-and-swap on expected
generation for any registry mutation; stale loses.

**Security and capability.** Authorization at the point of use, before ranking, before dereference,
before any content read. Attenuation is monotonic. No ambient authority, no widening, no borrowing.
Key material lives at mode `0600` outside the repository and never in source, tests, or fixtures.
`scan_secrets.py` is blocking. Requested containment that is unavailable fails closed.

**Versioning and compatibility.** Schemas carry explicit versions. Writers single-write the newest;
readers dual-read. Frozen versions are byte-immutable. The JSON-RPC surface is additive-only until
M-10, frozen thereafter with a written compatibility policy.

**Performance.** Every performance claim names its declared host and its measurement method.
Budgets are asserted in tests, not in prose. Telemetry overhead on a disabled feature path must be
provably zero (identity and event-stream parity with the feature absent).

**Observability.** Bind digests, not descriptions: plan, grant, composition, result, reconciliation,
challenge, decision, checkpoint, retrieval receipt. A reader must be able to recompute what
happened from the recorded digests alone.

**Technical documentation.** Docstrings explain *why*, not *what* — the existing
`_append_canonical` docstring, which explains the failure mode it prevents, is the model. Every
module states its layer and its owning lane. As-built architecture documentation is regenerated at
wave boundaries, never maintained continuously. No document restates law; it links to it.

---

# 15. Research requirements

Restricted to concrete M-9/M-10 gaps. Each item must terminate in a decision, a contract, a
benchmark, or an algorithm. **No generic surveys.** Each is owned, timeboxed, and produces one page.

| # | Question | Owner | Must produce | Default if inconclusive |
|---|---|---|---|---|
| R-01 | How do `schemas/` and `packs/` ship inside an installed wheel without a repo checkout? | A | A packaging decision (`importlib.resources` vs `package_data` vs a data directory) plus a working `pip install` | `importlib.resources` with schemas moved under `vanguard/packages/domain/schemas/` |
| R-02 | Which Python distribution format and install path for a CLI with native-ish deps (`cryptography`)? | A | wheel + sdist decision; supported platform matrix; whether a standalone binary (PyInstaller/shiv) is warranted | wheel + sdist only; no standalone binary in v0.9 |
| R-03 | Ledger and schema migration strategy for an append-only store | A | Migration algorithm, dry-run contract, refusal conditions, digest-verified export/import format | Export/import with digest verification; no in-place mutation, ever |
| R-04 | Blob/CAS lifecycle: GC roots, legal hold, quarantine, orphan detection | A | GC algorithm and its safety proof sketch | Mark-and-sweep from causal roots, legal hold set, reviewed dry run before any sweep |
| R-05 | Recovery guarantees under fault injection: which boundaries can lose what? | A | A boundary-by-boundary table of guarantee and recovery action | Every boundary either recovers or fails closed with a durable fact |
| R-06 | Backup and restore for ledger + CAS with a consistent point in time | A | Procedure and a restore test | WAL checkpoint + CAS snapshot + digest manifest |
| R-07 | Security enforcement audit: capability checks at every boundary; key rotation | A + B | A boundary inventory with the check that guards each one; a rotation procedure | Rotation by re-provisioning; old keys marked revoked, never deleted |
| R-08 | Multi-tenancy: is a shared server part of v0.9? | A implements, B verifies | A scope decision | **Out of v0.9.** Tenant/project stay in the data model; no shared-server isolation work |
| R-09 | Plugin/pack lifecycle and SDK: discovery, validation, activation, versioning, removal | A | Lifecycle FSM (extending `runtime/registry/`) and an SDK surface | Manifest-declared packs only; no third-party SDK in v0.9 |
| R-10 | Performance: append / fold / checkpoint / retrieval / turn latency | A measures, B gates | Measured budgets on the declared host, plus a regression gate | Record measured values as the budget; regression = >20% deviation |
| R-11 | Distributed or multi-process execution: warranted for v0.9? | A | A decision grounded in R-10's numbers | **No.** Single-process. Revisit only on measured need |
| R-12 | Meta-control evaluation beyond M-6.5 | B | Whether the accepted study supports profile-specific enablement | Controller stays off by default |
| R-13 | Skill promotion and rollback in production: what makes a promotion safe to serve? | B | Promotion criteria, regression bounds, rollback trigger conditions | Promotion disabled by default; rollback on any regression above the preregistered bound |
| R-14 | Coding/research agent benchmarking: which corpus qualifies v0.9? | B | A named benchmark set with baseline numbers | The existing `benchmarks/` corpus plus the three Wave-4 workflows |
| R-15 | Operator UX: what must an operator see and control during a long run? | A | The command and view inventory that drives A-401/A-405 | Status, logs, explain, approve, cancel, checkpoint, resume |
| R-16 | Release engineering: reproducible builds, checksums, signing, publication | A | A release procedure and the `release_qualify.sh` contract | Reproducible wheel + signed manifest; no package-index publication in v0.9 |

R-01, R-03, R-05, R-10 and R-16 are **prerequisites for Wave 5 and must be completed during Wave 4**.
The rest run inside their consuming wave.

---

# 16. Structure of the two future implementation plans

Two documents. Nothing else. They are the working surface for the entire remaining program.

```
docs/03_execution/lane_a_plan.md      # owner: Lane A
docs/03_execution/lane_b_plan.md      # owner: Lane B
```

Each is **self-contained**: a developer must be able to execute it end to end without reading any
other document except the ones it explicitly links for law.

## Required structure (identical in both)

```
 1. Identity and cursor
      Lane name, owner, plan version, the single "current task" pointer.
      This cursor replaces sprint_active.md for this lane.
 2. Baseline
      Exact commit, tag, build commands, test commands, supported platforms,
      external dependencies and services.
 3. Architecture relevant to this lane
      The layers this lane owns, the dependency direction, the composition seam.
      Descriptive only; links to law, never restates it.
 4. Constitutional invariants (§4 of this report, verbatim)
      Copied identically into both plans so neither can drift.
 5. Coding standards (§14, verbatim)
 6. Ownership map
      This lane's exclusive files; the other lane's files (explicitly forbidden);
      the shared contracts and which of them this lane authors.
 7. Contracts consumed and produced
      Per wave. With versions. With the kit path.
 8. The linear task sequence
      A-001 → A-final (or B-001 → B-final), every task in the §10 template.
      Strictly ordered. No parallel tracks. No optional tasks.
 9. Behavioural pseudocode
      Inline in each task's field 10.
10. Migrations
      Every persistence change, its forward-read strategy, its refusal conditions.
11. Failure modes
      Per task, in field 13; plus a lane-level table of the failure classes this
      lane is responsible for.
12. Automatic checks
      Level-1 command set for this lane; each task's own completion commands.
13. Integration order
      The wave table from §12.3, with this lane's role in each.
14. Decision defaults
      The §11.2 rows this lane owns, verbatim.
15. Auxiliary queue
      §8.4, this lane's half. What to do when blocked.
16. Build and release procedure
      Lane A: the full procedure. Lane B: the qualification half.
17. Definition of Product Ready
      Identical in both plans: `ci/release_qualify.sh` exits 0 on a clean
      checkout in a clean container.
```

## Rules governing the two plans

- **Shared contracts appear in both plans with the same Plan ID and the same version string.** One
  plan marks it `AUTHOR`, the other `CONSUME`. If the two texts ever differ, the `AUTHOR` copy wins
  and the `CONSUME` copy is a defect.
- **Versioned in git, in the repository, beside the code.** The plan is a source file. It is updated
  by its owning lane, in the same commit as the work it describes.
- **The cursor is the only status.** No separate board. "Where are we" is answered by reading two
  lines.
- **A task is never edited once started.** Learning something mid-task means finishing the task,
  then appending a follow-up task. This keeps the sequence linear and the history honest.
- **Handover:** each lane receives its plan once, at Wave 0, and executes continuously to the end.
  The plan is amended only by its own owner, only by appending, and never to relax a completion
  criterion.

---

# 17. Final TODO table

Ordered. Owned. Every row has a concrete result and an explicit dependency.

| # | Work | Owner | Result | Depends on |
|---:|---|---|---|---|
| 1 | Adopt §6 version ladder; rewrite `SPEC.md:190-202` and the README roadmap line | A | One coherent version sequence; v0.9.0 lands at M-10 | — |
| 2 | Adopt §8 ownership map; annotate each package with its owning lane | A + B | No cross-lane file collision is possible | 1 |
| 3 | Delete `C1-GATE`, the Leadership role, and the mandatory-reviewer requirement; mechanize acceptance per D-05 | A | Five milestones stop being blocked on a non-existent role | 2 |
| 4 | Retire `sprint_active.md` and `sprint_upcoming.md`; keep `milestones.md` as a stable gate reference | A | One plan per lane; no divergent boards | 3 |
| 5 | Write `lane_a_plan.md` and `lane_b_plan.md` per §16, seeded from §9 | A + B | Two self-contained executable plans | 2, 3, 4 |
| 6 | **A-001**: fix `agency/manifests/loader.py` path resolution | A | 17 test errors → 0 | 5 |
| 7 | **A-002/A-003**: package `schemas/` and `packs/`; real `pip install` path | A | An installed wheel loads manifests | 6 |
| 8 | **B-001/B-002**: fix model-price vectors + a drift linter; repair 3 markdown links | B | 2 failures → 0; all 22 linters green | 5 |
| 9 | **B-003**: `test_m1_m3_anchors` — one executable check per M-1→M-3 anchor | B | The historical baseline is machine-verified, not asserted | 8 |
| 10 | **B-004**: delete the `InMemoryMemoryPort` fail-open branch | B | A fake that cannot be more permissive than production | 8 |
| 11 | **B-005**: publish the Wave-0 Contract Kit | B | Both lanes can build against frozen contracts | 8, 9 |
| 12 | **A-004/A-005**: bind preregistration in the runner; portable artifacts; refuse dirty trees | A | `undeterminable` becomes impossible for instrument reasons | 7 |
| 13 | **A-006**: create, sign and push annotated `v0.7.3` (= `CONVERGENCE-BASE-v1`) | A | The incontestable baseline; M-5b unblocks | 6, 7, 8, 9, 12 |
| 14 | **A-007 / B-007**: re-execute M-4 RF-95 and M-6 depth≥3; re-run M-5b against the tag | A, B | M-1…M-6.5 all closed on determinable evidence | 13 |
| 15 | **Wave 1**: A-101…A-105 live three topologies; B-101…B-104 M7-01 + ADR-0099 | A, B | **M-7 closed**; tag `v0.7.5` | 14 |
| 16 | **Wave 2**: A-201…A-208 durable authorized memory; B-201…B-206 retrieval semantics + falsifiers | A, B | Memory is durable, authorized, recoverable, provenanced | 15 |
| 17 | **Wave 3**: A-301…A-306 CAS registry + promotion + rollback; B-301…B-306 sealed evaluation + lift | A, B | **M-8 closed**; tag `v0.8.0` — feature-complete substrate | 16 |
| 18 | **R-01, R-03, R-05, R-10, R-16** research spikes | A | Packaging, migration, recovery, performance and release decisions made | 17 |
| 19 | **Wave 4**: A-401…A-407 product surface + clean install; B-401…B-405 three real workflows + operator corpus | A, B | **M-9 closed**; tag `v0.8.5` — operational beta | 17, 18 |
| 20 | **Wave 5**: A-501…A-507 reliability/migration/security/deployment/packaging; B-501…B-506 regression corpus, failure injection, compatibility, upgrade, release bundle | A, B | **M-10 closed** | 19 |
| 21 | `ci/release_qualify.sh` exits 0 on a clean checkout in a clean container | B | **AETHER v0.9.0 delivered**; tag `v0.9.0` | 20 |
| 22 | Project Owner reviews the finished product | Owner | Business acceptance | 21 |

---

# 18. Immediate next steps

Six actions, in order. The first five are documentation and take under a day. The sixth starts the
program.

1. **Decide the version ladder.** Adopt §6 or reject it. Everything downstream inherits this. If
   adopted, `docs/SPEC.md:190-202` and the README roadmap line are corrected in one commit.

2. **Delete the approval layer.** Remove `C1-GATE`, the Leadership role, the mandatory independent
   human reviewer (replaced by the mechanical criterion in D-05), and the Leadership reservation on
   baseline-tag creation. This single edit unblocks M-4, M-5a, M-5b, M-7 and M-8 simultaneously —
   they are blocked on a role, not on code.

3. **Publish the ownership map (§8.2) and paste it into both plans.** Until this exists, "two lanes"
   is an aspiration; after it exists, cross-lane conflict is structurally impossible.

4. **Retire the four-board system.** `sprint_active.md` and `sprint_upcoming.md` are deleted;
   `milestones.md` survives as a stable gate reference; the two lane plans become the working
   surface, each with its own cursor.

5. **Write the two lane plans** from §9 (roadmap), §10 (task template), §11.2 (decision defaults) and
   §16 (structure). Wave 0 must be specified to full task granularity before anyone starts; Waves 1–3
   to task granularity; Waves 4–5 to package granularity, refined at Wave 3's close when R-01/R-03/
   R-05/R-10/R-16 have landed.

6. **Start Wave 0 in parallel.** Lane A takes A-001; Lane B takes B-001. Neither waits for the
   other. Neither waits for anyone.

---

## Closing note on the shape of the remaining work

The distance from `c3dc123` to a buildable, operational AETHER v0.9 is smaller than the documentation
suggests and larger than the code alone suggests.

Smaller, because the substrate is built: the kernel is domain-blind and inside its budget, the ledger
has one writer, the trust spine verifies, topology lowering is wired into the one public run path,
and the memory authorization contract is real. Nineteen failing tests reduce to three root causes,
one of which is a single character.

Larger, because M-9 and M-10 have never been specified, and the product surface is genuinely thin: a
three-command CLI, an unpackaged schema directory, an install script that writes a `PYTHONPATH` shim
to a hardcoded interpreter, and no build job at all. That is real work, and it is the work that
separates a substrate from a product.

The one thing that is neither small nor large, but simply misplaced, is the approval apparatus.
Five milestones sit at `PACKAGE_READY` waiting for a role that does not exist to accept evidence that
already verifies. Removing that layer costs one commit and returns five milestones.

