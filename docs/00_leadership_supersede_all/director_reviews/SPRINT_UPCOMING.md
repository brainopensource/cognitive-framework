# SPRINT_UPCOMING — M-5a Substrate Window ("Event-Derived Agent")

```text
sprint: S-P2-02 "One Window, One Tag"
promotion condition: M-4 CLOSED + ADR-0098 accepted (OD-1). Everything below is specified to
near-executable resolution in specs/SPEC_M5A_EVENT_DERIVED_AGENT.md; promotion is a scheduling
decision, not a design meeting.
exit: SPEC_M5A §9 gates green → tag M-5-BASE
```

## U-000 — Draft ADR-0098 `owner: Architect+Director` `runs during S-P2-01`
Objective: convert SPEC_M5A into the constitutional record: envelope /2 field table, kind roster
(§5) with writer/reducer/schema/vector per kind, deprecation list + reintroduction rule, checkpoint
contract, dual-read/single-write migration, exit gates, M-5-BASE criteria. Risks: roster scope
creep — the ADR must enumerate rejected candidate kinds with reasons (kind-introduction criterion).
Acceptance: Director accepted; OD-1 closed. Unresolved feeding in: OD-1, OD-2.

## Wave plan (dependencies explicit; ∥ = parallel within wave)

**Wave 1 (post-acceptance, ∥):**
- **U-101 / M5A-101** envelope /2 + codegen — files `schemas/mhf/event_envelope.schema.json`,
  `domain/wire/types_gen.py` (regen), `domain/ledger/events.py::parse_event_envelope` dispatch.
  Interfaces: reader defaults (`authoritySource="unrecorded"`); risk: digest preimage regressions →
  mitigate with mixed-chain golden fixtures before emitter cutover. Acceptance: RF-99 tests minus
  emitter leg.
- **U-103 / M5A-103** vocabulary unification — delete `_V4_ONLY_KINDS`; `DEPRECATED_KINDS`;
  rewrite `test/contracts/test_event_coverage.py`. Risk: hidden consumers of removed constant →
  `grep -rn _V4_ONLY_KINDS` must be 0 across repo incl. tests.
- **U-104 / M5A-104** execution contracts (pure domain; no deps).
- **U-110 / M5A-110** RF-97 v2 tooling (independent; CI gate flips at U-111).

**Wave 2 (→ after 101+103):**
- **U-102 / M5A-102** emitter /2 cutover + authority defaults + deprecation write-rejection —
  `runtime/ledger_emitter.py` (`WIRE_VERSION`, role→authority table, `DeprecatedKindError`).
  Risk: role-consistency matrix gaps → test forgery cases per role.
- **U-105 / M5A-105** semantic kind package (5 kinds) — schemas+vectors+ownership rows+reducer
  handlers (`domain/ledger/reducer.py`). Risk: reducer state bloat → AgentView owns semantics;
  LedgerState gains only minimal fields ADR-0098 lists.

**Wave 3 (→ after Wave 2):**
- **U-106 / M5A-106** AgentView + `fold_agent_view` (`domain/ledger/agent_view.py`).
- **U-107 / M5A-107** RF-96 falsifier (fresh-process golden; interrupted variant with
  `RecoveryScanner`). Acceptance: field-by-field equality; zero shared objects.
- **U-109 / M5A-109** `reproducibility_current` recomputation claim.

**Wave 4 (→ after 106):**
- **U-108 / M5A-108** CheckpointManager + `mhf.checkpoint/1` + role `checkpointer` +
  fail-closed-to-cold-fold + bench extension (≤20% cold-fold target; OD-2 defaults: every 500
  events or 25 turns, per-lineage — Tech Lead may tune, must record).

**Wave 5 (serial close):**
- **U-111 / M5A-111** exit gates + docs (`events.md` kind table + deprecated register;
  `RUNTIME.md §15` closure note) + bench regression check (<10% vs M4-107 baseline) + kernel-diff
  == 0 attestation + tag `M-5-BASE` + pin-set record.

## Risk register (sprint-level)
| Risk | Mitigation |
|---|---|
| Envelope digest/chain regression | mixed-version golden chain fixtures land before emitter cutover; fresh-process replay parity is a merge gate for U-102 |
| Kind roster churn post-acceptance | ADR-0098 enumerates accepted + rejected kinds; additions re-open the ADR, not the sprint |
| Reducer version skew vs checkpoints | `reducerVersion` pin check in `load_latest`; mismatch ⇒ cold fold (tested) |
| Silent kernel drift during window | RF-98 pre-check job: CI fails the window branch on any `vanguard/packages/kernel` diff |
| Fold perf regression | M4-107 baseline gate; checkpoint speedup measured before tag |

## Promotion checklist (to move this board to ACTIVE)
M-4 COMPLETE row · ADR-0098 accepted (OD-1 closed) · bench baseline artifact present ·
staffing: 1 domain dev (U-104/105/106), 1 runtime dev (U-102/108), 1 schemas/codegen dev
(U-101/103), 1 tooling dev (U-110), Tech Lead on U-107/U-111.
