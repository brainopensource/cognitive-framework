---
id: adr-0110-fh1-retrieval-disposition
adr: "0110"
class: decision
authority: binding-decision
canonical_for:
  - decision-0110-fh1-retrieval-disposition
status: living
owner: engineering-director
version: "1.0"
last_verified: 2026-09-13
decision_status: accepted
---

# ADR-0110 — D-5: FH-1 disposition for T-140

T-140 pre-adopts only the existing-invariant constraints listed below, implemented through current memory, grant, provenance and ledger contracts; no proposed FH-1 wire schema becomes registered merely through this ruling.
From FH-C01 it inherits bounded reads, digest verification and authorization independent of content addressing, and from FH-C03 it inherits immutable historical facts and refusal to fabricate missing durable evidence, without adopting workspace capture or promotion.
From FH-M01 it inherits provenance/exposure separation so diagnostic or development material cannot become held-out acceptance evidence; from FH-M03/M04 it inherits immutable content identity, current authorization/revocation checks before every context admission including cached and restarted retrieval, and no reuse of revoked material.
The proposed global revocation-root algorithm, global invalidation receipt and `aether.lesson/1`, `aether.lesson-revocation/1`, `aether.retrieval-admission/1` schemas stay quarantined: existing grant/record checks provide T-140's constraint, with refusal when current authority cannot be established.
FH-C01's remaining capture/materialization protocol, FH-C02/C04 in full, FH-C03's head/generation/promotion mechanics, FH-C05–C11, all `aether.tree/1`, `aether.edit-set/1`, check-plan/candidate-check/promotion/export-journal schemas, FH-D01–D12, FH-E01–E04 and their corresponding FH-1.8 error allocations remain quarantined until T-129 package admission.
FH-M02's lift study, lesson generation/promotion/rollback, FH-M01's study partition protocol and the remaining FH-M03/M04 machinery likewise remain quarantined; production retrieval is not governed-learning acceptance, and M-8's empirical predicate is unchanged.
The claims that FH-1's proposed formulas already authorize implementations, that proposed CAS identity replaces current workspace identity, or that T-140 requires a new promotion/export journal are dead interpretations, not competing contracts; no named FH clause is deleted or declared intrinsically invalid by this bounded ruling.
Only the explicitly selected constraints apply now, the entire remaining FH-1 text stays proposed, and any disagreement about a future algorithm waits for T-129 rather than blocking T-140's current retrieval wiring.
