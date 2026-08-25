---
id: active-sprint-board
class: execution
authority: execution
canonical_for:
  - active-sprint-tasks
  - current-milestone-gates
status: active
owner: tech-lead
version: "0.7.1"
last_verified: 2026-08-25
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Active Sprint — S-P2-01 M-4 Two-Lane Implementation

Authority: [`VISION.md`](../../VISION.md) -> [`SPEC.md`](../SPEC.md) +
[`01_law/`](../01_law/) -> accepted ADRs through
[`ADR-0097`](../02_decisions/0097-phase0-ratification-and-two-lane-activation.md) ->
[`milestones.md`](milestones.md) -> this board. This is the sole current implementation
authorization.

## 1. Activation decision and receipts

**Dev A and Dev B are authorized to start their M-4 packages from baseline**
`f9d7ceb257e8e2c7d6014bd0a29604ffcd89ee0e`.

Phase-0 decisions are closed:

- ADR-0096 v0.4.0 accepted; ADR-0097 v0.2.0 accepted.
- Strict `/1` compatibility, evidence failure/degradation, RF-100 proof semantics, resources,
  goal privacy, retention, content-capture policy, and transitive TCB measurement are decided.
- Linux RF-38…RF-45 qualification passed 13/13 on 2026-08-25, including both RF-43 UDS tests.
  CI MUST repeat this suite before merge; any failure blocks integration.
- Shared contracts, file ownership, merge order, and package/integration states are frozen below.

RF-95 remains **NO-GO** until both packages merge and the integrated prerequisites in §5 pass.

## 2. Frozen M-4 Contract Kit

The lanes implement these public outcomes; internal implementation remains owned by each Senior.

### Schema and compatibility

- `mhf.execution-profile/1` and `mhf.trajectory/1` are frozen.
- M-4 adds `/2`; readers dual-read `/1|/2`; production writers single-write `/2`.
- Historical bytes, digests, and identities are never rewritten.

### Evidence

- Exact provider input/output capture occurs at `runtime/session.py::_LayeredOperator.propose`.
- Evidence-ledger append failure is fatal.
- Required capture failure is fatal.
- Optional capture degradation requires a durable `capture_incomplete` fact and makes the run
  non-evidentiary.
- `mhf.trajectory/2` carries artifact index, context/compaction/cache provenance, exact model-I/O
  references, and `reproducibility_at_run_close`.

### Reproducibility

- State reconstruction and semantic replay separately record capability and verification.
- WAL and pins are prerequisites only.
- `verified` requires immutable run-bound executed receipts covering inputs, pins, and output digest.
- The run-close assessment is immutable; later current-state assessment is a new claim.

### Resources, privacy, and retention

- Additive resources: `usd_micros`, `millis`, `tokens`, `bytes`.
- Structural ceilings: `depth`, `turns`.
- Goal facts use `goalDigest` and optional digest-verified `goalArtifact`; no raw goal ledger text.
- Retention: `digests_only`, `standard`, `full`.
- Retention never authorizes capture. Runtime resolves capture, redaction, secret, and sensitivity
  policy before blob persistence and records policy identity/version.

## 3. Dev A — Evidence Runtime and Causal Capture

State: **READY**. WIP limit: one package.

Objective: build the production path from Runtime execution to durable, policy-authorized artifacts
and provenance without changing the event envelope, event roster, or Kernel semantics.

Required outcomes:

- Runtime `ArtifactWriter` over existing blob-store ports/adapters; blob-first/event-second;
  store-computed digest; no large content inline in events.
- Generic Agency provenance protocol plus Runtime-owned sink; no Agency -> Runtime import.
- Context-selection and compaction provenance with policy identity, parameters, input/output digests,
  and policy-authorized artifact references.
- Exact finalized provider input capture immediately before invocation and raw structured output
  capture immediately after return at `_LayeredOperator.propose`.
- Cache/cassette provenance when applicable; no claim required for a live no-cache invocation.
- Required/fatal and optional/durable-degradation behavior from ADR-0096 §14.2.
- Capture/privacy policy enforcement before any prompt, output, context, snapshot, patch, or report
  bytes are stored.

Exclusive files/surfaces:

- `vanguard/packages/runtime/session.py`
- `vanguard/packages/runtime/artifacts.py`
- `vanguard/packages/runtime/provenance.py`
- `vanguard/packages/runtime/wiring.py`
- `vanguard/packages/runtime/root.py`
- `vanguard/packages/runtime/ledger_emitter.py`
- Agency provenance/compiler integration

Dev A MUST NOT edit Dev B-owned profile/trajectory schemas or readers. Dev A reaches
`PACKAGE_READY` on its isolated contract suite and frozen Dev-B fixtures; integrated trajectory and
RF-100 checks occur after merge.

## 4. Dev B — Scientific Contracts and Verification

State: **READY**. WIP limit: one package.

Objective: implement versioned scientific contracts and falsifiers that prevent evidence claims from
exceeding executed proof.

Required outcomes:

- `mhf.execution-profile/2` with retention, capture-required/evidence semantics, and identity preimage.
- `mhf.trajectory/2` with artifact/provenance/reproducibility sections.
- Dual-read `/1|/2`, single-write `/2`, strict golden vectors, and historical-reader tests.
- Proof-honest RF-100 derivation and immutable verification-receipt contract.
- Append/fold benchmark baseline for M-5a.
- M7-01 analysis may begin over existing ledgers but MUST NOT add concurrency, scheduling, workers,
  claims, leases, or topology.

Exclusive files/surfaces:

- `vanguard/packages/runtime/profiles.py`
- `vanguard/packages/runtime/reproducibility.py`
- `vanguard/packages/runtime/trajectory.py`
- `vanguard/packages/runtime/trajectory_reader.py`
- execution-profile and trajectory schemas/vectors/readers

Dev B MUST NOT edit Dev A-owned Runtime capture/wiring surfaces. Dev B reaches `PACKAGE_READY` on
schema, reader, RF-100, and benchmark tests using frozen artifact/provenance fixtures.

## 5. Integration and RF-95

Package states are distinct:

```text
READY -> IN_PROGRESS -> PR_OPEN -> REVIEW -> PACKAGE_READY -> MERGED -> GATE_ACCEPTED
```

Merge order:

1. Dev B merges profile/trajectory contracts and readers.
2. Dev A rebases on main and merges production capture wiring.
3. Leadership runs the combined suite; both packages become `GATE_ACCEPTED` together.

RF-95 may run only after:

- both packages are `GATE_ACCEPTED`;
- full Python/TypeScript, architecture, TCB, secrets, event, and governance gates are green;
- RF-38…RF-45 is green in CI;
- a non-trivial live task and verifier are frozen before execution;
- profile `/2` resolves `retention=standard` and `capture.required=true`;
- the live provider is attributable and is not fake/cassette.

The single candidate must produce a terminal `mhf.trajectory/2`, exact model-I/O artifacts,
context/compaction/cache provenance, proof-honest reproducibility, real workspace diff, passing
verifier receipt, durable WAL, and fresh-process reconstruction receipt. Failure is preserved without
manual repair and keeps M-4 open. Independent review plus Leadership acceptance closes M-4.

## 6. Explicit non-scope

- No event-envelope or event-kind change before accepted ADR-0098 and M-5a.
- No `agent.spawn`, topology, scheduler, memory, skills, or meta-control implementation in M-4.
- No Kernel semantic change, second runtime, upward dependency, or weakened falsifier.
- No historical ADR rewrite or movement/deletion of the historical `M-5-BASE` tag.
- M-5a implementation remains blocked on M-4 closure and ADR-0098.
- After M-5a, M-5b and M-6 may run in parallel from immutable `M-5A-BASE-v2`.

## 7. Required verification

```bash
python3 -m unittest discover -s test -t .
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/scan_secrets.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_isolation_policy.py
python3 tools/linters/check_event_coverage.py
python3 tools/linters/check_falsifier_ids.py
python3 tools/linters/check_duplication.py --enforce
python3 tools/linters/check_markdown_links.py
python3 tools/linters/check_stale_paths.py
npm run typecheck --workspaces --if-present
npm test --workspaces --if-present
```
