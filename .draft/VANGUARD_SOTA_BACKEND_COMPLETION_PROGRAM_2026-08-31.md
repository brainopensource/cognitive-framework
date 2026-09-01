# Vanguard SOTA Backend Completion Program

**Document class:** non-authorizing implementation brief (`.draft/`)
**Inspected subject:** `ca47eef7da1b4075f8a69d238fe1626fa1ab4c8e`
**Date:** 2026-08-31

Status and authorization resolve through [`milestones.md`](../docs/execution/milestones.md),
[`active.md`](../docs/execution/active.md), and [`backlog.md`](../docs/execution/backlog.md).
This brief does not authorize M-9, M-10, or benchmark claims. The operator has
separately authorized up to $0.15, 300,000 tokens, and 120 OpenRouter calls for
SOTA-04 and internal SOTA-08 B1/B2 only; the ledger must fail closed.

## Current-subject findings

- Observation digests are non-placeholder evidence; OPEN-2 is `DONE`.
- Context identity, role-aware routing, bounded scheduling, meta-control, and signed skill promotion exist and require integration and qualification.
- BEP-01..03 are technical complete/reviewing. BEP-04 is a technical slice/ablation pending; BEP-05 is a technical slice/release gated.
- The tracked runtime canonicalization facade is removed; benchmark canonicalization uses the canonical domain client contract.
- CMX-07 is an internal qualification proxy, not SWE-bench; official claims require the published SWE-bench, SWE-Bench Pro, or DeepSWE protocol.
- Hermes-on-Vanguard targets the public capability surface of the MIT-licensed Hermes Agent.
- M-8 remains `BLOCKED`; M-9 and M-10 remain `UNAUTHORIZED`. Commit `4777e16` has an inaccurate completion message; history is not rewritten.

## Three-wave program

| Wave | Packages | Outcome |
|---|---|---|
| SOTA-W1 | SOTA-01..04 | Truth reconciliation, completion convergence, official benchmark bridge, frozen qualification |
| SOTA-W2 | SOTA-05..08 | Long-context/multi-file hardening, multi-model economy, measured optimization |
| SOTA-W3 | SOTA-09..12 | Qualified coordination, agent-builder integration, Hermes parity, release qualification |

The authorized build lane is SOTA-01 → SOTA-02 → SOTA-03 → SOTA-05 → SOTA-06
→ SOTA-07 → SOTA-09 → SOTA-10 → SOTA-11. The measurement lane is SOTA-04,
authorized internal SOTA-08 rungs, and blocked SOTA-12. Existing mechanisms are
extended through current ports and runtime seams; no second runtime, store,
coordinator, evaluator, router, or recovery ledger is introduced.

### SOTA-W1 — truth, completion, measurement

1. **SOTA-01** adds real `HarnessSession` falsifiers for BEP-01..03, fixes task-digest fallback asymmetry, removes duplicate outbound alias schemas while retaining inbound aliases, and proves non-placeholder observation digests.
2. **SOTA-02** makes admissible completion converge: first redundant green verification emits typed finish feedback; the second offers only `agency.finish`, `fs.read`, and `fs.search`; no auto-finish is permitted and refusal remains `ABANDONED`.
3. **SOTA-03** adds normalized task/submission/`aether.benchmark.receipt/1` contracts, isolated adapters, exact-subject receipts, and hermetic fixtures for SWE-bench Verified, SWE-Bench Pro, and DeepSWE v1.1.
4. **SOTA-04** runs CMX-06, the renamed internal CMX-07 proxy, and FIN-A1 only after preflight. Provider calls require separate spend authority; otherwise the result is `NOT_RUN`.

## Claim ladder and integrity

- B0 is hermetic instrumentation only. B1 targets 20/20 frozen internal easy tasks.
- B2 targets at least 27/30 frozen internal average tasks. B3 is a 60% internal-hard research target, not a release promise.
- B4/B5 commit to official reproducible scores without promising a score. 75% on SWE-Bench Pro/DeepSWE is research aspiration only.
- B6 permits competitor claims only from matched protocols. Internal BAAC/LAM/CMX artifacts are never official results.
- The 30-task SWE-Bench Pro pilot retains its kill criterion: `<=2/30` falsifies the flash-primary path toward 75% and forces a recorded pivot.

All claims bind task, split, patch, model, harness, evaluator, subject SHA, usage,
and receipt identity. Null empirical values carry a reason. Unknown usage, price,
model identity, evaluator, or subject fails closed. Experimental SBFL, mutation,
branch search, swarm, and self-modification ship only after measured lift.

## W2/W3 handoff

SOTA-W2 extends existing context identity with selection-policy identity, drift
validation, bounded section retrieval, patch/resume hardening, and additive routing
telemetry; it freezes 20-easy/30-average/30-hard campaigns and the 30-task Pro pilot.
SOTA-W3 qualifies scheduler reconstruction/fairness/leases, integrates the existing
composition/meta-controller/skill lifecycle, builds Hermes as a pack over the same
runtime, and performs matched and official release qualification. Neither wave may
mark M-9 or M-10 accepted without every canonical predicate and independent gate.

## Stop-ship conditions

Do not claim completion from a fabricated or stale receipt, a local benchmark, LAM
replay, an unmatched competitor comparison, or a mechanism-only test. Stop on foreign
receipts; unknown usage, price, or model; workspace/index drift without recompilation;
duplicated settled effects; scheduler over-concurrency; forged or self-evaluated skill
promotion; or missing independent acceptance. Negative or undeterminable evidence is
recorded honestly and does not unlock dependent gates.

## Developer handoff

Use the repository navigation sequence in `AGENTS.md`, preserve unrelated frontend
changes, update only canonical execution files and generated knowledge, run targeted
falsifiers plus `just docs-knowledge`, Markdown link/stale-path checks, `just check`,
and `just verify`. Stop after the authorized wave.
