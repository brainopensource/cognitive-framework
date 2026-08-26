---
id: sprint-doing-v2b-backend-delivery
class: execution-report
authority: tech-lead-delegation
status: active-handoff
owner: tech-lead
scope: backend-only (vanguard/packages, lab/, tools/, test/)
version: "1.0.0"
last_verified: 2026-08-26
subordinate_to:
  - VISION.md
  - docs/SPEC.md
  - docs/01_law/
  - accepted ADRs
  - docs/03_execution/sprint_active.md
---

# sprint_doing_v2B — Backend Delivery Report: Closing M-4…M-8

---

## 0. Ground truth audit (verified 2026-08-26, HEAD `a92951d`)

Everything below was verified by executing repo commands, not by reading claims.

### 0.1 What is genuinely DONE (do not rebuild)

| Area | Evidence |
|---|---|
| Kernel S0–S12, attenuation, budgets | `kernel/dispatch.py`, TCB **1,373 / 1,438 logical LOC** (headroom: 65) |
| M-4 evidence runtime | `runtime/artifacts.py`, `ports/evidence_errors.py` (C-02 taxonomy), `runtime/reproducibility.py` (RF-100 capability≠verification), trajectory `/2` dual-read (`runtime/profiles.py`, `runtime/trajectory_reader.py`) |
| RF-95 live product proof | G-M4-04 passed all 5 exit conditions; M-4 CLOSED under Director development waiver (G-M4-05 review receipt still owed before *evidence release*) |

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
Replay:       fresh-process replay is the ONLY replay proof (A-3/I-4); WAL/pins = capability,
              receipts = verification (C-04).
Goals:        goalDigest (+optional artifact ref), never raw text (C-06).
Determinism:  hermetic CI, API keys UNSET; live paths explicitly selected; seeded randomness
              recorded as provenance entering D_R.
Falsifiers:   every deliverable ships a named RF-* that tries to break it; a weakened
              falsifier is itself a finding.
```
| M-5a substrate | `mhf.event/2` envelope cutover, `domain/ledger/agent_view.py` pure projection fold, `runtime/checkpoints.py` (pin/hash fail-to-cold-fold, `REDUCER_VERSION = v1.1.0`), RF-97 AST transitive TCB closure, ADR-0098 ratified v1.0.0, benchmark re-frozen `benchmarks/baseline_m4.json` (~42.4k fold/s) |
| M-5b material run | SAT/CNF through `Runtime.execute_harness`; exterior `EvaluatorDaemon` over Unix socket, Ed25519-signed pass AND fail vectors; `runtime/formal_evidence.py` recomputes pinned digests + folds terminal axis from ledger |
| M-6 delegation | `runtime/delegation.py`: `SpawnAdapter` as ordinary S0–S12 adapter, `ADDITIVE_DIMENSIONS = ("usd_micros","millis","tokens","bytes")`, structural `depth`/`turns`, idempotent subtree settlement via `settledIntentKey`, crash ⇒ `Occurrence.UNDETERMINABLE`, typed `DelegationResult`. 28 conjunctive falsifiers green |
| M-6.5 seams | `ports/meta_controller.py` (pure SPI), `runtime/meta_controller.py::guarded_consult` (5 fail-closed guards: stale epoch, missing subject refs, nondeterministic directives, budget-bypass keys, authority keys), `domain/ledger/progress.py` (`ConfidenceRecord.contextEpoch` bound), `runtime/paired_evaluation.py`, `lab/m65_study.py` (McNemar exact, Holm–Bonferroni, bootstrap CI, `DegenerateFloorError`, `ComparabilityError` per M-18) |
| M-7 partial | `runtime/topology.py` (`parse_topology`, authority-rejecting validation, `lower_topology` → `RunPlanExtension`), `runtime/scheduler.py` (`SequentialScheduler`, `ready_operations`, `safe_read_only_group`), `lab/m701_independence.py` (analysis-only) |
| M-8 partial | `runtime/memory.py` (5-category protocols `KnowledgePort`/`ExperiencePort`/`ProjectMemoryPort`/`SkillLibrary`, `RetrievalProvenance`, capability-checked `MemoryAccess`), `runtime/skill_evaluation.py` (separated authorities, held-out split, regression budget, Ed25519 promotion evidence) |

> **One phrase:** finish the product by repairing the evidence chain first, then building only
> the four genuinely open backend blocks — the M-6.5 measurement instrument, the M-7
> selector/timing capture + topology lowering, and the M-8 memory/skill-promotion machinery —
> so that every milestone claim is backed by an executed, independently verifiable proof.

**Audience:** Senior Dev A / Senior Dev B. **Surface:** Python backend only. The TypeScript CLI /
Studio (`vanguard/clients/`) is explicitly out of scope for this report.
