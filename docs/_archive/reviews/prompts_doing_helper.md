# Prompt for Dev A (WP-A1 — Canonical recursion / M-4 + M-6):

▎ Execute Sprint C1, package WP-A1, per docs/03_execution/backlog.md §WP-A1 and docs/03_execution/sprint_active.md "Immediate execution order" item 1. Objective: restore RF-95 and replace the synthetic delegation success path (volatile IDs, unconserved parent balance, callback-only execution) with real recursive runtime capability, in runtime/delegation.py, wiring.py, session.py, root.py, plus recovery/ledger and a minimal ChildRuntimePort in Ports. Kernel/Agency semantics must not change. Implement: immutable SpawnIntent/ChildRunPlan/ChildRuntimePort; child_id=H(parent_episode_id, idempotency_key); attenuated action/selector scope; per-dimension budget reservation against parent remaining; depth/turn lowering; ChildSpawned/ChildReturned events via Runtime.run_composed; settlement/refund; replay-safe reconciliation (UNDETERMINABLE on open/unknown). Cover the required falsifiers: missing runner, restart-stable ID, collision, each budget dimension, depth/turn/scope widening, transcript leakage, depth≥3 cold fold, crash boundaries, settled replay, project isolation, kill-tree, RF-98. Do not fabricate the RF-95 evidence bundle — either verify a recovered original or preregister exactly one new candidate. Deliver a digest-addressed aether.evidence/1 bundle for M-4 and M-6 separately. Report back as task -> code -> test -> evidence -> blocker against this contract; do not start WP-A2/M-6.5, WP-A3/M-7, or any M-8/M-9/M-10 work.

---

Prompt for Dev B (WP-B1 — Baseline succession / M-5a + M-5b):

▎ Execute Sprint C1, package WP-B1, per docs/03_execution/backlog.md §WP-B1 and docs/03_execution/sprint_active.md "Immediate execution order" items 2 and 5. Objective: record the invalid M-5A-BASE-v2 control's provenance as machine-verifiable forensics (it is CONTAMINATED_UNPUBLISHED at local ref 1b4ce1a, per ADR-0102 — do not move, recreate, or re-validate it by prose), and build the aether.baseline/1 signed-tag verifier (remote/local identity, commit/tree/lock/schema/reducer pin, ancestry/contamination checks, fail-closed on missing/weak/lightweight/unpushed/contaminated). Only after Leadership creates and pushes the annotated CONVERGENCE-BASE-v1 tag may you implement the pack-local graph-coloring falsifier (candidate assigns colors in [0,k); exterior oracle checks completeness/range/edges with no search; canonical sorted input; SAT pack stays as regression only — not the generality proof). Cover: baseline resolution/signature/tree/pin/contamination falsifiers; satisfiable/edge/incomplete/range/malformed/duplicate/order vectors; a fresh-process material run; RF-86/RF-98 passing green. Work stays entirely in baseline/evidence tooling and the new pack — do not touch Dev A's runtime hotspots. Report back as task -> code -> test -> evidence -> blocker; do not start WP-B2/M-6.5, WP-B3/M-7, or any M-8/M-9/M-10 work.

---

Both prompts intentionally exclude C2–C4 scope — that stays frozen in sprint_upcoming.md/backlog.md until WP-A1/WP-B1 close and ADR-0099 exists, per the earlier discussion.

✻ Worked for 17s · done 12:50 AM

❯ ok good but give me two prompts with the files to read so they dont drift or halucinate

Prompt for Dev A (WP-A1 — Canonical recursion / M-4 + M-6):

▎ Before writing any code, read these files in full and treat them as the sole authority — do not rely on memory, prior chat, or assumptions about the codebase:
▎ - docs/03_execution/sprint_active.md (current authorization, milestone status table, prohibited scope, execution order)
▎ - docs/03_execution/backlog.md §WP-A1 (implementation-ready contract: surface, interfaces, algorithm, failure/security, tests, evidence/DoD)
▎ - VISION.md and docs/SPEC.md (constitutional constraints on Kernel/Runtime/Agency boundaries)
▎ - docs/02_decisions/ — ADR-0101 and ADR-0102 (evidence methodology and baseline succession rules you must follow)
▎ - Current source: runtime/delegation.py, wiring.py, session.py, root.py, and the existing recovery/ledger and Ports modules they depend on — read them before editing, do not guess their current shape.
▎ - docs/05_contracts/ — any existing schemas for events/spawn/budget you will bind to or extend.
▎
▎ Execute Sprint C1, package WP-A1, exactly as specified in backlog.md §WP-A1 and sprint_active.md "Immediate execution order" item 1. Objective: restore RF-95 and replace the synthetic delegation success path (volatile IDs, unconserved parent balance, callback-only execution) with real recursive runtime capability. Kernel/Agency semantics must not change. Implement: immutable SpawnIntent/ChildRunPlan/ChildRuntimePort; child_id=H(parent_episode_id, idempotency_key); attenuated action/selector scope; per-dimension budget reservation against parent remaining; depth/turn lowering; ChildSpawned/ChildReturned events via Runtime.run_composed; settlement/refund; replay-safe reconciliation (UNDETERMINABLE on open/unknown). Cover all required falsifiers listed in the contract table (missing runner, restart-stable ID, collision, each budget dimension, depth/turn/scope widening, transcript leakage, depth≥3 cold fold, crash boundaries, settled replay, project isolation, kill-tree, RF-98). Do not fabricate the RF-95 evidence bundle — verify a recovered original or preregister exactly one new candidate. Deliver digest-addressed aether.evidence/1 bundles for M-4 and M-6 separately. If anything in the contract is ambiguous against the actual code you read, stop and report the discrepancy rather than guessing. Report back as task -> code -> test -> evidence -> blocker. Do not start WP-A2/M-6.5, WP-A3/M-7, or any M-8/M-9/M-10 work.



---





# Prompt for Dev B (WP-B1 — Baseline succession / M-5a + M-5b):

▎ Before writing any code, read these files in full and treat them as the sole authority — do not rely on memory, prior chat, or assumptions about the codebase:
▎ - docs/03_execution/sprint_active.md (current authorization, M-5A-BASE-v2 disposition, milestone status table, prohibited scope, execution order)
▎ - docs/03_execution/backlog.md §WP-B1 (implementation-ready contract: surface, interfaces, algorithm, failure/security, tests, evidence/DoD)
▎ - VISION.md and docs/SPEC.md (baseline/evidence constitutional rules)
▎ - docs/02_decisions/ — ADR-0101 and ADR-0102 (evidence methodology and baseline succession rules; ADR-0102 is the authority for the CONTAMINATED_UNPUBLISHED disposition and the succession decision tree you must follow)
▎ - Run git cat-file -p 1b4ce1a / git log -1 1b4ce1a yourself to independently confirm the local contaminated ref before writing forensics tooling — do not trust a paraphrase of it.
▎ - schemas/mhf/ and docs/05_contracts/ for any existing baseline/tag/evidence schema you must extend as aether.baseline/1.
▎ - Existing SAT pack and evaluator code (test/ and lab/ under the M-5b area) to understand what stays as regression coverage versus what the new pack replaces.
▎
▎ Execute Sprint C1, package WP-B1, exactly as specified in backlog.md §WP-B1 and sprint_active.md "Immediate execution order" items 2 and 5. Objective: record the invalid M-5A-BASE-v2 control's provenance as machine-verifiable forensics — do not move, recreate, or re-validate it by prose — and build the aether.baseline/1 signed-tag verifier (remote/local identity, commit/tree/lock/schema/reducer pin, ancestry/contamination checks, fail-closed on missing/weak/lightweight/unpushed/contaminated). Only after Leadership creates and pushes the annotated CONVERGENCE-BASE-v1 tag may you implement the pack-local graph-coloring falsifier (candidate assigns colors in [0,k); exterior oracle checks completeness/range/edges with no search; canonical sorted input; SAT pack stays as regression only, not the generality proof). Cover all required falsifiers listed in the contract table (baseline resolution/signature/tree/pin/contamination; satisfiable/edge/incomplete/range/malformed/duplicate/order vectors; fresh-process material run; RF-86/RF-98 green). Work stays entirely in baseline/evidence tooling and the new pack — do not touch Dev A's runtime hotspots. If anything in the contract is ambiguous against the actual code/tags you inspect, stop and report the discrepancy rather than guessing. Report back as task -> code -> test -> evidence -> blocker. Do not start WP-B2/M-6.5, WP-B3/M-7, or any M-8/M-9/M-10 work.
