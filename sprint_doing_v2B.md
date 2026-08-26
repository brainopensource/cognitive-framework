---
id: sprint-doing-v2b-backend-delivery
class: execution-report
authority: tech-lead-delegation
status: active-handoff
owner: tech-lead
scope: backend-only (vanguard/packages, lab/, tools/, test/)
version: "1.1.0"
last_verified: 2026-08-26
subordinate_to:
  - VISION.md
  - docs/SPEC.md
  - docs/01_law/
  - accepted ADRs
  - docs/03_execution/sprint_active.md
---

# sprint_doing_v2B — Backend Delivery Report: Closing M-4…M-8 and Scaffolding M-9/M-10

> **One phrase:** finish the product by repairing the evidence chain first, then building only
> the four genuinely open backend blocks — the M-6.5 measurement instrument, the M-7
> selector/timing capture + topology lowering, and the M-8 memory/skill-promotion machinery —
> so that every milestone claim is backed by an executed, independently verifiable proof, then
> scaffold M-9/M-10 as exterior, non-authorizing horizons that never expand the kernel.

**Audience:** Senior Dev A / Senior Dev B. **Surface:** Python backend only. The TypeScript CLI /
Studio (`vanguard/clients/`) is explicitly out of scope for this report.

---

## 0. Ground truth audit (verified 2026-08-26, HEAD `a92951d`)

Everything below was verified by executing repo commands, not by reading claims.

### 0.1 What is genuinely DONE (do not rebuild)

| Area | Evidence |
|---|---|
| Kernel S0–S12, attenuation, budgets | `kernel/dispatch.py`, TCB **1,373 / 1,438 logical LOC** (headroom: 65) |
| M-4 evidence runtime | `runtime/artifacts.py`, `ports/evidence_errors.py` (C-02 taxonomy), `runtime/reproducibility.py` (RF-100 capability≠verification), trajectory `/2` dual-read (`runtime/profiles.py`, `runtime/trajectory_reader.py`) |
| RF-95 live product proof | G-M4-04 passed all 5 exit conditions; M-4 CLOSED under Director development waiver (G-M4-05 review receipt still owed before *evidence release*) |
| M-5a substrate | `mhf.event/2` envelope cutover, `domain/ledger/agent_view.py` pure projection fold, `runtime/checkpoints.py` (pin/hash fail-to-cold-fold, `REDUCER_VERSION = v1.1.0`), RF-97 AST transitive TCB closure, ADR-0098 ratified v1.0.0, benchmark re-frozen `benchmarks/baseline_m4.json` (~42.4k fold/s) |
| M-5b material run | SAT/CNF through `Runtime.execute_harness`; exterior `EvaluatorDaemon` over Unix socket, Ed25519-signed pass AND fail vectors; `runtime/formal_evidence.py` recomputes pinned digests + folds terminal axis from ledger |
| M-6 delegation | `runtime/delegation.py`: `SpawnAdapter` as ordinary S0–S12 adapter, `ADDITIVE_DIMENSIONS = ("usd_micros","millis","tokens","bytes")`, structural `depth`/`turns`, idempotent subtree settlement via `settledIntentKey`, crash ⇒ `Occurrence.UNDETERMINABLE`, typed `DelegationResult`. 28 conjunctive falsifiers green |
| M-6.5 seams | `ports/meta_controller.py` (pure SPI), `runtime/meta_controller.py::guarded_consult` (5 fail-closed guards: stale epoch, missing subject refs, nondeterministic directives, budget-bypass keys, authority keys), `domain/ledger/progress.py` (`ConfidenceRecord.contextEpoch` bound), `runtime/paired_evaluation.py`, `lab/m65_study.py` (McNemar exact, Holm–Bonferroni, bootstrap CI, `DegenerateFloorError`, `ComparabilityError` per M-18) |
| M-7 partial | `runtime/topology.py` (`parse_topology`, authority-rejecting validation, `lower_topology` → `RunPlanExtension`), `runtime/scheduler.py` (`SequentialScheduler`, `ready_operations`, `safe_read_only_group`), `lab/m701_independence.py` (analysis-only) |
| M-8 partial | `runtime/memory.py` (5-category protocols `KnowledgePort`/`ExperiencePort`/`ProjectMemoryPort`/`SkillLibrary`, `RetrievalProvenance`, capability-checked `MemoryAccess`), `runtime/skill_evaluation.py` (separated authorities, held-out split, regression budget, Ed25519 promotion evidence) |

### 0.2 Verified DEFECTS blocking honest closure (fix before any feature work)

| # | Defect | Proof | Severity |
|---|---|---|---|
| D-1 | **RF-86 gate is RED.** Commit `a92951d` (labeled `docs(P2-M65)` — a mislabel) inserted **+119 lines of substrate code** (`agent_view.py` +13, `progress.py` +11, `ports/evidence_errors.py` +47, `runtime/artifacts.py` +30, `agency/provenance.py` +9) **after** the `M-5A-BASE-v2` freeze. `bash ci/rf86_gate.sh` exits 1 today. | Executed gate output | **BLOCKER** |
| D-2 | **`M-5A-BASE-v2` is local-only.** `git ls-remote --tags origin` does not list it; the board claims "Create/push … DONE". Remote CI cannot run RF-86/RF-98 historical halves. | Executed command | BLOCKER (M-5b) |
| D-3 | **Live provider key exposed.** `OPENROUTER_API_KEY` is exported in the dev shell; it broke the trust-spine falsifier once already. Treat as compromised. | `env` check | SECURITY |
| D-4 | **Overclaiming commit message.** `1b4ce1a "…close M-4"` while independent review (G-M4-05) is only WAIVED-development-only. Commit messages are evidence artifacts. | Git history | PROCESS |
| D-5 | **M7-01 capture gap.** `EffectStarted` emits `descriptorDigest/sinkClass/grantId/leaseId` but **no resolved resource selector and no timing**, so `lab/m701_independence.py` reports useful-independence `0.0` — *unmeasurable*, not *measured*. `test_m701_recorded_workload.py` fails if this closes silently. | Board §3 + falsifier | BLOCKS M-7/ADR-0099 |
| D-6 | **M-6.5 instrument absent.** The only fully-attributable offline provider is deterministic ⇒ A/A floor degenerates to 100% ⇒ `MEASUREMENT.md M-07` refuses; on never-stalling tasks the controller emits no directive ⇒ arms identical ⇒ `ComparabilityError`. | Board §3, `lab/m65_study.py` | BLOCKS M-6.5 |

### 0.3 Standing rule for this whole report

> Every phase below lands **outside `kernel/`** unless explicitly marked otherwise (none is).
> Any change touching `domain/ kernel/ ports/ runtime/ agency/` semantics requires an escalation
> per masterplan §6.3 (new wire schema field = trigger #4; new event kind = #6; weakening any
> gate = #8). The RF-86 surfaces stay frozen relative to the resolved baseline.

---

## 1. Governing invariants (binding on every line of code below)

```text
Lattice:      domain ← ports ← kernel ← agency ← runtime → adapters   (apps/ = client slot)
Kernel:       domain-blind (I-7), ≤1438 logical LOC (now 1373 — 65 LOC headroom TOTAL),
              never branches on agent.spawn / SAT / strategy / topology verbs.
Events:       small durable causal facts; single writer per kind (WRITER_ROLES);
              large bytes → blob store keyed by store-computed sha256; blob FIRST, event SECOND.
Schemas:      /1 frozen forever; readers dual-read; production writers single-write /2 (C-03).
Evidence:     ledger append failure = fatal; required artifact failure = fatal;
              optional failure ⇒ durable capture_incomplete FIRST ⇒ run non-evidentiary (C-02).
Resources:    additive = {usd_micros, millis, tokens, bytes} exactly; depth/turns = ceilings (C-05).
Replay:       fresh-process replay is the ONLY replay proof (A-3/I-4); WAL/pins = capability,
              receipts = verification (C-04).
Goals:        goalDigest (+optional artifact ref), never raw text (C-06).
Determinism:  hermetic CI, API keys UNSET; live paths explicitly selected; seeded randomness
              recorded as provenance entering D_R.
Falsifiers:   every deliverable ships a named RF-* that tries to break it; a weakened
              falsifier is itself a finding.
```

---

## 2. PHASE R — Governance repair (serial-first; nothing else merges until this closes)

Owner: Tech Lead. Est: 0.5–1 day. No milestone code.

### R-1 Adjudicate the RF-86 red (D-1)

Two lawful resolutions — pick exactly one, in an append-only recorded decision:

```text
Option A (RECOMMENDED): Successor decision (mini-ADR) declaring the post-tag additions
  (evidence-errors port taxonomy + artifact capture plumbing + AgentView/Progress
  accessors) an authorized additive correction to the M-5a window.
  Mechanics:
    - The diff is strictly ADDITIVE (no mutated signatures in the verified diff stat),
      confined to evidence-capture concerns that C-02 mandates.
    - NEVER move M-5A-BASE-v2. Advance the comparison point through explicit, recorded
      baseline succession: create M-5A-BASE-v2.1 on the repaired commit, update
      ci/rf86_gate.sh DEFAULT_BASE and the board row; keep strictness identical
      (whitelist NOTHING; docstring-only changes still count).
    - Rerun RF-98 kernel neutrality against the new tag.

Option B: Revert the six files' post-tag hunks and re-land them through a normal
  feature branch AFTER the successor decision. Use only if Option A is refused.
```

Forbidden: silently re-pointing `M-5A-BASE-v2` (board §5 prohibits movement/recreation);
weakening `ci/rf86_gate.sh`; absorbing the diff without a decision.

### R-2 Push the baseline (D-2)

```bash
git push origin M-5A-BASE-v2            # or v2.1 per R-1 outcome
git ls-remote --tags origin | grep M-5A # MUST resolve remotely; record digest on board
```

### R-3 Rotate the leaked key + mechanical hygiene gate (D-3)

Rotate `OPENROUTER_API_KEY` at the provider; purge it from any log/test artifact.
Add a fail-closed preflight linter (tooling lane):

```python
# tools/linters/check_test_hygiene.py — CI step 0, BEFORE any suite runs
import os, sys

PROVIDER_KEYS = ("OPENROUTER_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY")

def main() -> int:
    leaks = [k for k in PROVIDER_KEYS if os.environ.get(k)]
    for k in leaks:
        print(f"FATAL: {k} is exported; suites must run hermetic (unset {k}).")
    return 1 if leaks else 0

if __name__ == "__main__":
    sys.exit(main())
```

### R-4 Commit discipline (D-4)

Any commit touching `vanguard/packages/**` or `schemas/**` MUST use
`feat(...)/fix(...)/test(...)/cleanup:` prefixes — never `docs:`. Enforce mechanically:

```python
# tools/linters/check_commit_labels.py — reject docs:/chore: labels whose diff
# intersects vanguard/packages/** or schemas/**. Run in CI on PR ranges.
```

**DoD (Phase R):** `ci/rf86_gate.sh` exit 0; baseline resolves remotely; hygiene linter red
on dirty env; full suite green hermetically (`python3 -m unittest discover -s test -t .`,
expect ≈1,781+ passed / 0 failed).

---

## 3. PHASE 1 — Close M-5b and M-6 (evidence assembly; ~90% done, review-gated)

No new substrate code. Two work items.

### 1-1 M-5b closure package (Dev B)

The material run and signed verdict bundle exist. Remaining:

```text
1. After Phase R: execute ci/rf86_gate.sh against the RESOLVED remote baseline → archive
   the report artifact (RF-86 historical half flips DONE-for-real).
2. Execute the RF-98 historical comparator (tools/linters/check_kernel_neutrality.py at-tag
   vs HEAD): assert kernel verb-dispatch surface byte-identical; agency/episode
   domain-token count == 0. Archive both halves.
3. Independent cross-lane review receipt (human) over the bundle: daemon-signed pass vector
   PLUS daemon-signed FAIL vector (a judge that cannot sign "fail" is not trusted to sign
   "pass" — the negative vector stays in the bundle permanently).
4. Flip board rows only then. Generality is then empirically SUPPORTED, not asserted.
```

Adversarial acceptance test (verify it exists and stays strict):

```python
# test/falsifiers/ — keep red-by-construction; never weaken:
def test_passing_witness_over_failed_run_is_not_promotable():
    bundle = fabricate_bundle(witness="sat-pass-signed", ledger_terminal="abandoned")
    assert formal_evidence.verify(bundle) == Result.fail("terminal-mismatch")
```

### 1-2 M-6 closure package (Dev A)

Assemble the demonstration bundle; one new property test promotes conservation to a checked
invariant:

```text
bundle/m6_nested_lineage/
├── parent_trajectory.mhf.trajectory/2
├── child_tree.json                 # ChildSpawned/ChildReturned fold over ledger
├── budget_conservation_proof.json  # Σ child actualCost committed on PARENT lease
├── kill_tree_recovery.json         # SIGKILL mid-child → cold classify → UNDETERMINABLE
└── receipts/                       # signed verdicts + digests
```

```python
# test/falsifiers/test_budget_tree_conservation.py
def test_no_subtree_spends_beyond_root_ceiling(ledger, root_lineage):
    """C-05: conservation is structural — ONE accountant (the kernel committing
    AdapterOutcome.actual_cost against the parent lease) makes overspend unrepresentable."""
    for dim in delegation.ADDITIVE_DIMENSIONS:            # usd_micros, millis, tokens, bytes
        spent = sum_effect_costs(ledger, descendants_of(root_lineage))
        reserved = root_reservation(ledger, root_lineage)
        assert spent[dim] <= reserved[dim], f"conservation breach on {dim}"
    for ev in effects(ledger):                            # ceilings are NEVER costs:
        assert not (set(ev.actual_cost) & set(delegation.STRUCTURAL_CEILINGS))
```

**DoD:** review checklist signed → M-5b CLOSED and M-6 CLOSED separately.

---

## 4. PHASE 2 — M-6.5 measurement instrument (largest pure-engineering block)

Owners: Dev B (provider + task sets + study), Dev A (wiring review). All hermetic.
Blocked-by: nothing once Phase R lands. Start immediately.

### 2-1 Stochastic Attributable Provider (Dev B)

Location: `vanguard/packages/adapters/models/stall.py` (adapter lane — imports ports/domain
only; wired by runtime; never imported by agency/kernel).

Design law: randomness must be **reproducible per run** (seed recorded as provenance entering
`D_R`) yet produce **genuine arm-relevant variance**, and every deviation must be **auditable**
as `f(seed, turn_index)`.

```python
"""Seeded stall-injection wrapper over any ModelPort (B-M65 instrument)."""
from __future__ import annotations
import random
from typing import Any, Callable, Mapping, Sequence

from ...ports.event_store import Result
from ...ports.model import ContextBundle, ModelPort, Proposal, Sampling, ToolSchemas


class StochasticStallModel:
    """Wraps a base ModelPort and injects attributable stalls.

    Contract (all five falsified in test_stall_provider.py):
      C1 Determinism:  propose() depends ONLY on (base output, run_seed, turn_index).
                       Same (base transcript, seed) => byte-identical proposal sequence.
      C2 Variance:     over seeds S = [0, N), outcome discordance ∈ (0, 1) EXCLUSIVE —
                       a floor at either end re-degenerates the A/A statistic.
      C3 Attribution:  every deviation recoverable: an auditor replays the derived rng
                       stream and reproduces exactly which turns stalled and why.
      C4 No authority: a stalled proposal travels the ORDINARY parse/dispatch path;
                       the wrapper adds no capabilities, grants, or ledger writes.
      C5 Provenance:   (run_seed, p_stall, stall_decay, base_model_id) enter D_R via the
                       model-selection identity; unstated => ComparabilityError upstream.
    """

    def __init__(self, base: ModelPort, run_seed: int, *,
                 p_stall: float = 0.35, stall_decay: float = 0.9,
                 turn_source: Callable[[], int]) -> None:
        self._base, self._seed = base, run_seed
        self._p, self._decay = p_stall, stall_decay
        self._turn_source = turn_source        # injected by session; NEVER wall clock
        self.stall_log: list[dict[str, Any]] = []  # telemetry; NEVER ledger truth

    def propose(self, context: ContextBundle, tools: ToolSchemas,
                sampling: Sampling) -> Result[Proposal]:
        result = self._base.propose(context, tools, sampling)
        if not getattr(result, "ok", False):
            return result                      # instrument errors pass through untouched
        turn = self._turn_source()
        rng = random.Random(f"{self._seed}:{turn}")   # derived stream per turn (C1)
        p_t = self._p * (self._decay ** turn)         # stalls fade — late turns converge
        if rng.random() >= p_t:
            return result
        stalled = self._stall_variant(result.value, ctx_digest=_digest(context), rng=rng)
        self.stall_log.append({"turn": turn, "seed": self._seed,
                               "kind": stalled["stallKind"]})
        return Result.ok(stalled)

    def _stall_variant(self, proposal: Proposal, *, ctx_digest: str,
                       rng: random.Random) -> Proposal:
        """Three regressive families chosen from the SAME derived stream:
           repeat  – re-issue previous action (wasted-loop generator);
           regress – patch the wrong direction (forces revise_plan recovery);
           abandon – propose early conclude (forces change_verification recovery).
           The variant is an ordinary Proposal payload; nothing here is privileged."""
        ...
```

Wiring (Dev A review point): the seed must enter the run's declared model identity so
`assert_comparable()` sees arms differing ONLY on `controller_enabled`:

```python
# runtime/model_selection.py — extend the resolved route record (additive, runtime lane):
route_record["stallInstrument"] = {
    "kind": "stochastic-stall/v1",
    "seed": run_seed,                 # per-run, recorded pre-execution
    "pStall": p_stall, "stallDecay": decay,
}
```

> Escalation check: this extends a runtime record, not a frozen `/1` wire schema. If it must
> surface inside `mhf.execution-profile/*` payloads, it goes through profile `/2` semantics —
> `/1` is never touched.

Unit falsifiers (`test/adapters/models/test_stall_provider.py`, hermetic):

```text
test_same_seed_replays_identical_sequence           # C1
test_discordance_strictly_interior_over_seed_sweep  # C2: 0 < d < 1 across >=200 seeds
test_every_deviation_attributable_by_replay         # C3: auditor rebuilds the stall log
test_instrument_error_passthrough_untouched         # provider failures not masked
test_stalled_proposal_passes_ordinary_dispatch      # C4: no S0–S12 bypass
test_route_record_carries_instrument_identity       # C5
```

### 2-2 Deliberately-blockable task set (Dev B)

Location: extend `runtime/task_sets.py` (already owns digest-pinned resolution via
`resolve_task_set`) + fixtures under `packs/code-default/task_sets/blocked_v1/`.

Three archetypes, each mapping 1:1 onto a directive family the controller may emit
(`revise_plan | request_context | change_verification | abandon_hypothesis | delegate |
conclude`):

```python
BLOCKED_TASK_ARCHETYPES = (
    BlockedTask(
        task_id="t1-wrong-first-fix",
        plant=PlantedBug(obvious_fix_breaks="test_downstream"),  # symptom fix breaks suite
        elicits={"revise_plan"},
    ),
    BlockedTask(
        task_id="t2-missing-context",
        plant=HiddenDependency(path=".env.test"),                # unreadable w/o request_context
        elicits={"request_context"},
    ),
    BlockedTask(
        task_id="t3-flaky-verify",
        plant=FlakyFirstAttempt(seed_key="t3", p_fail=0.5),      # seeded flake, hermetic
        elicits={"change_verification"},
    ),
)

def materialize_task_set(seed: int) -> TaskSetManifest:
    """Both arms consume BYTE-IDENTICAL tasks (M-18 comparability precondition)."""
    tasks = tuple(t.materialize(random.Random(f"{seed}:{t.task_id}"))
                  for t in BLOCKED_TASK_ARCHETYPES)
    manifest = TaskSetManifest(tasks=tasks, seed=seed)
    manifest.manifest_digest = digest_of(jcs(manifest.to_dict()))
    return manifest
```

Hard constraints: fixed-seed generation; the flake's coin derives from the manifest seed so the
SAME task instance flakes identically in both arms (otherwise the treatment axis is
contaminated); grading is the exterior evaluator, never an in-process suite call (the
`.passed` bug class is already fixed — keep it fixed).

### 2-3 Paired study execution + verdict (Dev B)

`lab/m65_study.py` statistics are built and correct — wire, don't rewrite:

```python
report = paired_study(
    baseline  = run_arm(manifest, controller_enabled=False, seeds=N_SEEDS),
    treatment = run_arm(manifest, controller_enabled=True,  seeds=N_SEEDS),
    declared_treatment_dimensions=["controller_enabled"],   # M-18 gate
    aa_floor_seeds=A_A_SEEDS,                               # both arms OFF
)
# Inside: assert_comparable -> aa_noise_floor (raises DegenerateFloorError at 0/100%)
#         -> mcnemar_exact(discordant) -> holm_bonferroni -> paired_bootstrap_ci (M-04)
```

Decision semantics (MEASUREMENT law, unchanged): Holm-corrected significance + CI excluding
null + no regression-budget breach ⇒ report RECOMMENDS enable; default-enable stays a
Leadership call. Negative result ⇒ controller stays disabled-by-default; milestone closes as
an honest test. Either way M-6.5 CLOSES.

New falsifiers: `test_aa_floor_is_interior`, `test_blocked_task_elicits_directive`,
`test_arms_comparable_except_declared_axis`; keep `test_controller_off_path_bit_identical`
and `test_confidence_records_are_epoch_bound` strict (they exist — do not weaken).

**DoD:** non-degenerate A/A floor + paired verdict + signed report artifact → M-6.5 CLOSED.

---

## 5. PHASE 3 — M-7: effect-capture truth, topology lowering, concurrency decision

Owners: Dev A (capture + lowering + scheduler mechanism), Dev B (independence analysis +
falsifiers). Gate order: **3-1 → 3-2 → 3-3 → 3-4**.

### 3-1 EffectStarted resolved-selector + timing capture (closes D-5) — ESCALATION-GATED

Adding fields to an emitted event payload is masterplan escalation trigger #4/#6 territory.
The Tech Lead records the decision FIRST: recommended = additive OPTIONAL fields on the
existing `EffectStarted` kind under the `/2` envelope (old reducers ignore them; they are
projection-additive and reducer-total), vs a successor kind.

```python
# runtime/session.py — effect admission path (Dev A). Additive, emitter-side only:
self.emitter.emit_kind("EffectStarted",
    run_id=..., principal=..., episode_id=...,
    payload={
        **existing_fields,                     # descriptorDigest, sinkClass, grantId, leaseId
        "resolvedSelector": selector.to_canonical_dict(),  # domain selector algebra OUTPUT
        "startedMonotonicNs": t0,              # CLOCK_MONOTONIC — duration math ONLY
        "settledMonotonicNs": None,            # completed at settlement by the SAME writer
    })
```

Rules: the resolved selector is the canonical form from the domain selector algebra
(`selectors/resource_selector.py`) — never a raw string; timing uses monotonic clocks and is
coordination metadata, **never** budget `millis` (SPEC refusal); a missing field means
unknown, never zero (M-07 discipline); old ledgers replay unchanged (fields absent ⇒ pairs
dependent ⇒ report says unmeasurable, still never fabricated).

### 3-2 M7-01 independence re-run (Dev B)

With selectors present, `lab/m701_independence.py` computes real useful-independence over
recorded canonical workloads: pair independent ⟺ proven-disjoint selectors; missing selector
⇒ dependent; shared observation/advisory sinks ⇒ non-exclusive (safe-read case only).
Produce the report artifact ADR-0099 consumes. I-11 stays sequential throughout — analysis
never activates concurrency.

### 3-3 Topology lowering integration (Dev A)

`parse_topology` / `lower_topology` / `SchedulerPolicy` exist, are package-ready and NOT yet
bound into the composed run path. Integration is additive-only:

```python
# runtime/compose.py — accept the optional RunPlanExtension produced by lower_topology():
plan = plan_run(manifest, ...)
if activation.topology_extension is not None:
    ext = activation.topology_extension          # digest-pinned, authority-free (validated)
    plan.operations = lower_topology(ext)        # causal role ops + explicit may_delegate_to

# runtime/root.py — bind the reference SequentialScheduler behind SchedulerPolicy;
# readiness comes from ready_operations(operations, settled) — predecessors settled only.
```

Must-not list (each backed by an existing or new falsifier): no second workflow engine; no
topology authority (validation already rejects authority-bearing graphs — keep that red-proof);
no concurrent executor; no kernel diff (`rf86` surfaces clean); disabled-topology path
bit-identical to current behavior.

### 3-4 ADR-0099 (Leadership, evidence-driven)

From 3-2's report: implement / simplify (safe read-parallelism only — `safe_read_only_group`
already sketches the ceiling) / cancel. Default cancel if benefit < threshold. No advanced
concurrent engine without this ADR. **DoD: M-7 CLOSED.**

---

## 6. PHASE 4 — M-8: capability-mediated memory + skill promotion/rollback

Gate order: ADR-0100 FIRST (OD-6: reintroduce lifecycle kinds vs typed claims — recommend
typed claims via `ClaimRecorded` payloads; a new event-kind package is trigger #6 and buys
nothing), then two packages.

### 4-1 Durable category-port adapters (Dev A)

`runtime/memory.py` defines the five categories with capability checks and
`RetrievalProvenance`. Ship durable adapters in the adapter lane:

```python
# vanguard/packages/adapters/stores/memory_sqlite.py
class SqliteMemoryPort:
    """One durable backend per CATEGORY — never one universal 'memory' primitive.
    Rows are content-addressed (sha256 of JCS form); writes are append+index;
    recall returns MemoryResult + RetrievalProvenance(record_id, digests, category,
    query_digest) so anything reaching model context is provenance-visible (M4-102 path).
    Access control re-checks MemoryAccess.permitted() at READ time — revocation works."""
    def __init__(self, category: str, db_path: Path, *, scope: str) -> None: ...
    def write(self, value: Mapping[str, Any], access: MemoryAccess) -> str: ...
    def recall(self, query: str, access: MemoryAccess, limit: int = 20) -> MemoryResult: ...
    def invalidate(self, record_id: str, access: MemoryAccess) -> None: ...
```

Invariants: category boundaries preserved (one adapter class, five instances, distinct
scopes); retrieval provenance flows into the existing context-provenance sink; capability
mediation enforced at the port boundary; no kernel diff. Falsifiers: cross-category isolation
(a knowledge write invisible to experience recall), revoked-access read fails closed,
provenance digest round-trips.

### 4-2 Skill candidate → evaluation → promotion → rollback (Dev B)

`runtime/skill_evaluation.py` owns the separated-authority harness. Complete the executable
lifecycle:

```text
1. Generator (analyzes trajectories)  → SkillCandidate {promptPolicy|topologyFragment|
                                          parametrizedOps}, provenance-bound to source runs.
2. Evaluator (independent authority)  → held-out suite + affected-context regression +
                                          presence-only adversarial + grounding/verification,
                                          over composition vN+1 (the UNIT is the versioned
                                          composition, never a lone skill).
3. Promoter (distinct authority)      → Ed25519 promotion evidence requires measured held-out
                                          lift; no self-promotion path exists (falsify: a
                                          generator key in the promoter ring ⇒ refuse).
4. Rollback                           → EXECUTED, not simulated: inject a regression into a
                                          promoted composition, prove atomic restore to vN
                                          restores pre-promotion behavior bit-identically.
```

Lifecycle representation follows ADR-0100. **DoD:** measured held-out lift for ≥1 promoted
composition + executed rollback + RF-98/neutrality green → M-8 CLOSED. M-9+ remains exterior,
non-authorizing horizon.

---

## 7. Execution order, ownership, and gates

```text
PHASE R (governance repair)                       ← SERIAL-FIRST, blocks everything
   └─► PHASE 1 (close M-5b ∥ close M-6)           ← evidence + review receipts only
   └─► PHASE 2 (M-6.5 instrument)                 ← start immediately after R; hermetic
         └─► PHASE 3 (M-7: 3-1→3-2→3-3→ADR-0099)  ← 3-1 gated on TL schema decision
               └─► PHASE 4 (M-8: ADR-0100 → 4-1 ∥ 4-2)
                     └─► PHASE 5 (M-9/M-10 exterior scaffold; non-authorizing)
```

| Phase | Owner | Merge order | Exit gate |
|---|---|---|---|
| R | Tech Lead | serial | rf86 exit 0; tag pushed; hygiene linter green |
| 1 (M-5b/M-6) | Dev B ∥ Dev A | either (disjoint) | review receipts; board flips |
| 2 (M-6.5) | Dev B (+ Dev A wiring review) | B → A → integrated | non-degenerate A/A + paired verdict |
| 3 (M-7) | A capture/lowering; B analysis | A → B → ADR-0099 | interpretable M7-01 + ADR-0099 |
| 4 (M-8) | A adapters; B pipeline | A → B → integrated | lift + executed rollback + neutrality |
| 5 (M-9/M-10) | Exterior lab/packs only | never into kernel | scaffold compiles; zero kernel diff |

## 8. Global Definition of Done (every phase)

1. Canonical suite green hermetically: `python3 -m unittest discover -s test -t .` with all
   provider keys unset (enforced by R-3 linter).
2. Static gates green: `check_boundaries.py`, `check_tcb_budget.py` (**≤1438 logical LOC;
   65 LOC headroom — treat as scarce; new logic goes to runtime/adapters/lab, never
   kernel**), `scan_secrets.py`, `check_domain_blindness.py`, `check_duplication.py
   --enforce`, `ci/rf86_gate.sh`.
3. Every new module ships its named falsifier; no falsifier weakened anywhere in the diff.
4. Claims ≤ proof: every board flip cites an executed artifact (bundle digest, signed report,
   review receipt), never configuration or intention.
5. No new Markdown under `docs/`; decisions land as append-only ADRs; status lives only in
   `docs/03_execution/sprint_active.md`.

## 9. New falsifier register (allocate IDs via check_falsifier_ids before landing)

| Candidate ID (TL allocates) | Attacks | Phase |
|---|---|---|
| stall-provider reproducibility / variance / attribution trio | C1/C2/C3 above | 2 |
| aa-floor-interior + arms-comparable | manufactured improvement | 2 |
| blocked-task-elicits-directive (×3 archetypes) | task-set vacuity | 2 |
| effect-selector-presence (fails if gap "silently" closes wrong) | D-5 regression | 3 |
| topology-disabled-path-bit-identity | smuggled engine | 3 |
| memory cross-category isolation + revocation-fail-closed | memory conflation | 4 |
| generator-in-promoter-ringback refusal | self-promotion | 4 |
| injected-regression atomic rollback | fake rollback | 4 |
| sidecar-no-kernel-diff (M-9/M-10) | trust-surface pollution | 5 |

---

## 10. PHASE 5 — M-9 / M-10: preparation scaffold + MVP overview

> **Status: exterior, non-authorizing horizon.** M-9 (v1.0 integrated framework) and M-10
> (post-v1 continuous learning) do NOT authorize production substrate code now. This section
> is a **preparation scaffold** only: it names the interfaces to reserve, the pack/lab
> surfaces where experiments live, and the invariants that must survive unchanged. No kernel
> change, no new event kind, no second runtime. A scaffold that does not compile or that
> touches the TCB is a finding, not a deliverable.

### 10.0 Why scaffold now

The M-4…M-8 plan above produces the substrate on which v1.0 rests. Scaffolding M-9/M-10 now —
while the frozen contracts are fresh — does two things: (a) it proves the substrate is
*general enough* by expressing post-v1 ambitions as ordinary packs/plugins/sidecars, and (b)
it gives the M-8 promotion pipeline a concrete first consumer (the M-10 experience-compaction
sidecar feeds candidates to `skill_evaluation.py`). Both must be possible with **zero** new
semantics in `domain/`, `kernel/`, or the generic episode loop.

### 10.1 M-9 — Dynamic lineage topologies as exterior packs (v1.0 integration)

**Definition.** M-9 integrates everything: `direct`, `planner/executor`, `critic/reviser`,
`debate`, `research fan-out`, and `tree search` become **different configurations of the same
operational language** (VISION cap. 16) — declarative topologies lowered to ordinary
capability-mediated spawn, never a second engine.

**Scaffold (packs + lab only):**

```text
packs/dynamic-topology/
├── manifest.yaml                    # /2 manifest; composition-only, no new authority
├── topology_templates/              # direct, planner_executor, critic_reviser, debate, search
│   └── *.topology.yaml              # digest-pinned role graphs with explicit may_delegate_to
└── policy/                          # role->policy bindings (prompt policy, strategy)

lab/m9_topology_demo.py              # runs ONE template end-to-end against Runtime.execute_harness
```

```python
# lab/m9_topology_demo.py — proof of generality, NOT a production engine:
def demo_topology(template: Path, manifest: Path) -> RunResult:
    """Lower a digest-pinned topology template through the M-7 lowering path and run it.
    The ONLY substrate symbols touched are parse_topology/lower_topology/SchedulerPolicy —
    already shipped in M-7. If any template cannot be expressed, that is counter-evidence
    against generality (escalate), never a reason to add kernel semantics."""
    topo = parse_topology(load_digest_pinned(template))
    ext = lower_topology(topo)                     # → RunPlanExtension (M-7, authority-free)
    return Runtime.execute_harness(manifest_path=manifest, topology_extension=ext, ...)
```

**MVP acceptance (M-9):** ≥3 distinct topology templates run end-to-end through the UNCHANGED
M-7/M-8 substrate; each produces a complete `mhf.trajectory/2`; `rf86`/`check_kernel_neutrality`
stay clean; disabled-topology path remains bit-identical. This is the integration milestone —
it demonstrates, rather than documents, that direct/planner/critic/debate/search are one
language.

### 10.2 M-10 — Continuous experience compaction sidecar (post-v1 learning)

**Definition.** A **sidecar service** that subscribes to the SQLite-WAL event stream,
asynchronously cluster-compacts episodic trajectories into the M-8 memory indexes, and emits
`SkillCandidate`s into the existing promotion pipeline. It is NOT in-process and NOT a new
runtime value; the kernel never learns it exists (VISION cap. 18).

**Scaffold (adapters/lab only — sidecar pattern):**

```text
lab/m10_experience_sidecar/
├── wal_tail.py         # read-only SQLite-WAL tail (reuse EventStorePort read range)
├── compactor.py        # episodic cluster/compaction → MemoryResult + RetrievalProvenance
└── candidate_emitter.py# → SkillCandidate (consumed by runtime/skill_evaluation.py)
```

```python
# lab/m10_experience_sidecar/wal_tail.py — read-only; never writes the ledger:
class WalTail:
    """Tail the event stream and hand compacted experience to the M-8 promotion pipeline.
    Read-only over EventStorePort. It produces candidates; it never promotes."""
    def __init__(self, store: EventStorePort, memory: MemoryPort, *,
                 since_offset: int) -> None: ...
    def drain(self) -> Sequence[SkillCandidate]:
        events = self.store.read(EventRange(after=self._offset))  # read-only
        clusters = cluster_and_compact(events)                    # deterministic, digest-pinned
        self.memory.write(compact_form(clusters), access=EXPERIENCE_WRITE)
        return [candidate(cluster) for cluster in clusters]
```

**MVP acceptance (M-10):** the sidecar runs OUT-OF-PROCESS against a recorded WAL; compaction
is deterministic under pinned seeds; every candidate is provenance-bound to its source runs;
promotion still requires the M-8 independent evaluator + promoter authorities; `rf86` clean;
no event kind is added (candidates travel as `ClaimRecorded` payloads per ADR-0100).

### 10.3 Non-negotiable M-9/M-10 boundary (the single most important paragraph)

```text
1. Kernel = smallest possible.  Any M-9/M-10 feature that "needs" a kernel change is the
   architectural finding to escalate (masterplan §15.2 falsification path), never a hack.
2. Generator ≠ Evaluator ≠ Promoter.  The sidecar GENERATES; it never grades or promotes.
3. Sidecar is exterior.  It reads the WAL, writes candidates; it is not a second truth,
   not a second runtime, not an in-process authority.
4. Zero trust-surface growth.  RF-97 transitive closure must not include any M-9/M-10 path
   in the production kernel entry modules; if it does, the scaffold is wrong.
5. Everything digest-pinned and provenance-visible, exactly as M-4…M-8 require.
```

### 10.4 MVP definition of "delivered"

```text
M-4 CLOSED  — one attributable live coding run with complete causal capture + review receipt.
M-5a CLOSED — AgentView projection + immutable M-5A-BASE-v2 baseline (pushed, reviewed).
M-5b CLOSED — SAT generality falsifier with RF-86/RF-98 green against the resolved baseline.
M-6  CLOSED — nested-lineage delegation with conservation + kill-tree recovery evidence.
M-6.5 CLOSED— measured meta-control verdict (enable OR honest negative result).
M-7  CLOSED — interpretable M7-01 report + ADR-0099 disposition (I-11 honored).
M-8  CLOSED — capability-mediated memory + promoted composition with executed rollback.
M-9  SCAFFOLDED — ≥3 topology templates run on the unchanged substrate (exterior).
M-10 SCAFFOLDED — out-of-process experience sidecar feeds candidates (exterior).
```

The product is delivered when M-4…M-8 are closed on executed evidence and M-9/M-10 are
demonstrated as exterior packs/sidecars over the unchanged, domain-blind, ≤1438-LOC kernel.
