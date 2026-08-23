---
adr: 0076
title: "Foundation execution decisions: canonical envelope, one selector algebra, JCS as sole signing byte-source, D_H vs composition_digest disambiguation, verdict binding fields, single writer construction point"
status: accepted
source_section: "v0.6 Foundation preparation (post-ADR-0075)"
---

# ADR-0076: Canonical-artifact decisions for Waves 1–4

**Context.** ADR-0075 approved the v0.6 lock and authorized Wave 0. Preparing Waves 1–4 for
execution exposed six places where two existing artifacts could each plausibly claim to be "the"
implementation of a locked concept. Left open, each would be resolved differently by different
developers — the exact drift mechanism (dual runtimes, dual algebras) this programme exists to end.
None of these decisions reopens `0069`–`0075`; each names which **existing** artifact is canonical
and which converges into it. Live evidence for each is cited.

**Decision.**

1. **Canonical event envelope = `mhf.event/1`** (`schemas/mhf/event_envelope.schema.json`),
   extended with the ADR-0070 §5 lineage fields (`project_id`, `principal_id`,
   `parent_principal_id`, `parent_episode_id`, `harness_digest` — added optional in this
   preparation wave; Wave 1 flips them required). The v4 `EventEnvelope` dataclass
   (`vanguard/packages/domain/ledger/events.py`, fourteen governance fields, no lineage) is the
   **read-path legacy shape**: the Wave-1 writer produces `mhf.event/1`; reducers read both during
   convergence; the v4 write path retires at the Wave-2 parity gate. Two live write shapes after
   Wave 2 is a duplication-detector failure.

2. **One selector algebra = `vanguard/packages/domain/selectors/resource_selector.py`**
   (total, fail-closed, JCS-canonical, documented partial order). Every selector comparison in the
   system — kernel attenuation, plugin-cell ceilings, compose intersection — MUST route through
   `parse_selector`/`decide`. `layer0/spi/ceiling.py`'s private `_selector_subset` is the second
   algebra F-16 exists to kill; it is absorbed in Wave 2 by delegation, not by parallel repair.
   **P1-17 is resolved:** `proc://exec/allow/...` URIs parse to the `generic` kind; a `process`
   selector kind does not exist in the canonical algebra and MUST NOT be emitted. Code paths
   constructing `{"kind": "process", ...}` conform to the algebra, not vice versa
   (fixes the two `test_model_invocation` selector reds in place).

3. **JCS is the only signing and digest byte-source.**
   `vanguard/packages/domain/canonicalisation/jcs.py` (RFC 8785, ADR-0009) produces the bytes for
   every signature and content digest. `canonical_verdict_bytes` in
   `adapters/evaluators/signing.py` currently uses `json.dumps(sort_keys=True)` — a second
   canonicalisation that agrees with JCS on ASCII and drifts on non-BMP strings and number forms;
   Wave 1 Sprint 1.1 replaces it with the domain JCS. No new canonicalisation code may be written
   anywhere for any purpose.

4. **`FrozenHarness.composition_digest` is NOT `D_H`.** The packages digest
   (`domain/artifacts/manifest.py`) bakes `episode_id` into its input, making it execution-scoped —
   two runs of one composition differ. It is renamed in intent (an episode-scoped instance id) and
   retired from any identity role at Wave 2. `D_H` is computed by the Wave-1 compose step over the
   **full** behavior-affecting composition per ADR-0074 §4 (resolved plugin refs + digests, system
   prompt bytes, capability-ceiling **intersection**, approval policy, model routes), via JCS.
   The layer0 compose digest shape (`layer0/compose/compiler.py`) is the shape to absorb; its two
   defects go with it: it omits prompt/policy/routes, and it computes `intersect_ceilings(...)` and
   **discards the result** (the fail-open compose ADR-0074 cites).

5. **Verdict binding fields are law** (contract landed in
   `schemas/mhf/spi_payloads.schema.json#/$defs/SignedVerdict`): `verdict`, `signature` (Ed25519
   over the JCS bytes of all other fields), `subject_digest`, `evaluation_request_id`, `oracle_id`,
   single-use `nonce`, `key_id`, `signed_at`. A `VerdictRecorded` event embeds this object and MAY
   be appended only by the evaluator gateway. The current agent-side gate
   (`adapters/evaluators/gate.py`) verifies a bare payload signature and then **discards the
   verdict without ledgering it** — Wave 1 closes that loop; the gate becomes a reader of ledgered
   verdicts, per SPEC §2.1.

6. **One writer construction point.** All production envelope construction and appends flow through
   a single `LedgerEmitter` in `vanguard/packages/runtime/` (grown from `root.py`'s
   `LedgerBridge`, which is already the only kernel-facing sink). Writer authority for privileged
   kinds (ADR-0074 §3) is enforced there by construction — callers hold role-scoped emitter
   facades, not a generic `append(any event)`. The `EvaluationListener`'s hand-rolled envelope
   fabrication (invented `seq`, pseudo-UUIDv7) converges into this emitter in Wave 1.

**Alternative considered (and rejected).** Adopt the layer0 envelope dataclass wholesale (loses the
mature WAL store integration; ADR-0069 says absorb contracts, not swap runtimes). Add a `process`
selector kind to the algebra (a second inclusion relation with no consumer that `generic` URIs do
not already serve; may be proposed later via ADR with its own relation and tests). Keep
`json.dumps` signing because "it matches JCS in practice" (drift that only appears on adversarial
input is the worst kind). Let each Wave-1 task pick its own envelope/algebra (re-creates the dual
substrate).

**Evidence / bound test / links.** `domain/artifacts/manifest.py:83` (episode_id in digest);
`layer0/compose/compiler.py:57` (discarded intersection); `adapters/evaluators/signing.py:16`
(non-JCS bytes); `adapters/evaluators/gate.py:79` (verified verdict discarded);
`runtime/evaluation_listener.py:87` (fabricated envelope identity); `layer0/spi/ceiling.py`
(second algebra). Bound falsifiers: F-01/F-04/F-05/F-11/F-16 in the `002` register; execution detail
in `docs/03_sprints/plans/`.

**Reversal condition.** A newer ADR demonstrating the canonical artifact cannot carry the locked
semantics (e.g. the domain algebra cannot express a required ceiling relation), with a failing
test. Convenience of the absorbed fork's shape is not reversal.

**Owner · status.** Engineering Director / Chief Engineer · accepted · 2026-08-20
