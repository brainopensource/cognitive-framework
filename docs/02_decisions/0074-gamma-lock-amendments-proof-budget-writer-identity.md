---
adr: 0074
title: "GAMMA lock amendments: proof obligations, typed budget algebra, writer authority, complete D_H, Project definition, trajectory schema"
status: accepted
source_section: "v0.6 Concept Lock GAMMA"
---

# ADR-0074: GAMMA lock amendments

**Context.** ADRs `0069`–`0073` locked the v0.6 architecture (Python-first, packages canonical,
recursive Agent, ledger authority, identity trinity, wire-first plugins, exterior evaluator,
sequential execution, deferred list). Independent advisory reviews then showed that those ADRs
under-specified *how a lock is proven* and several algebraic/identity details. GAMMA
(`docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md`) independently
validated a small set of strengthenings. ADRs are append-only (`ADR-0000`); this entry records them
without silently editing `0069`–`0073`.

**Decision.** The following are law for v0.6. They do not reopen `0069`–`0073`; they tighten them.

1. **Proof obligations.** Every locked concept MUST name a falsifier (a test or gate that fails on
   the wrong implementation). A concept without a bound falsifier is not locked. Wiring those tests
   is Wave 0 of the code programme, not a claim that they already pass. Lexical E-COV is not I-2.
   Folding the same in-memory list twice is not I-4.

2. **Typed budget algebra.** The six-dimension reservation (`ADR-M0-07`) is **not** one additive
   algebra. Additive conserved quantities: `usd_micros`, `tokens`, `bytes`, charged `millis`
   (compute time, not wall-clock under concurrency). Structural ceilings: `depth` (path constraint:
   `child.depth = parent.depth + 1 ≤ root.max_depth`; sibling depths are not summed) and `turns`.
   Unbounded child under bounded parent is deny.

3. **Event-kind writer authority.** Privileged kinds (`CapabilityGranted`/`Revoked`,
   `BudgetReserved`/`Committed`/`Released`, `EffectStarted` and terminals, `VerdictRecorded`,
   `ApprovalResolved`, plugin lifecycle, run/episode lifecycle) MAY be originated only by their
   owning authority. Untrusted coordination MUST NOT generic-append them. Hash-chain integrity does
   not imply semantic truth.

4. **Complete `D_H`.** FrozenHarness digest MUST include every behavior-affecting input: resolved
   plugin refs and digests, system prompt, capability ceiling, approval policy, model routes.
   Two harnesses that differ in any of these MUST differ in `D_H`. Prompt identity is harness
   identity.

5. **Project.** A Project is a durable named scope that owns one ledger stream, one capability
   ceiling, and one root budget. Every Episode, Principal, and Artifact belongs to exactly one
   Project. `project_id` is the consistency unit.

6. **Principal.** `Principal` is a typed value `(id, parent_id?, depth)`, not a bare string.
   `ChildPrincipal` is not a second type. `SubAgent = Principal(parent_id=…) + HarnessInstance`.

7. **Trajectory.** `mhf.trajectory/1` is a required schema and MUST be emitted at every
   `EpisodeCompleted` without a transformation step (I-9). Digesting `{ids, n}` is not a trajectory.
   Harvest/DPO/promotion pipelines remain deferred (`ADR-0073`).

8. **Signed verdict binding.** A `VerdictRecorded` accepted into the ledger MUST carry a signature
   bound to evaluation-request id, subject digest, oracle identity, and a single-use nonce.
   Fabricating `{verdict: "pass"}` remains defect F1 (`ADR-0072`).

**Alternative considered (and rejected).** Fold these into silent edits of `0069`–`0073` (violates
append-only). Defer proof obligations until after code (repeats false-gate lock). Keep homogeneous
six-D additive conservation (mathematically false for `depth`). Keep `D_H` as plugin-refs-only
(blinds A/B of prompts and ceilings).

**Evidence / bound test / links.** GAMMA §§2–5; forensic F1 `layer0/scheduler/driver.py:138-139`;
fail-open `layer0/spi/ceiling.py:21-22`; compose dropping capabilities
`layer0/compose/compiler.py`; tautological replay `test/layer0/replay/test_parity.py`. Bound tests
are the falsifier table in
`docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.
`REQ-TRUST-001`.

**Reversal condition.** A newer ADR that (a) names a different consistency unit than Project, (b)
redefines `millis` as wall-clock and accepts non-additive concurrency accounting, or (c) permits
unsigned verdicts. Preference for fewer envelope fields is not reversal.

**Owner · status.** Principal Staff Engineer / Tech Lead · accepted · 2026-08-20 · accepted
