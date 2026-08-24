---
status: living
id: contract-verdicts
class: contract-reference
authority: descriptive
canonical_for:
  - signed-verdict-contract
source_of_truth:
  - docs/SPEC.md
  - docs/02_decisions/0072-plugin-boundary-wire-first-evaluator-exterior.md
derived_from:
  - schemas/mhf/spi_payloads.schema.json
  - vanguard/packages/adapters/evaluators/signing.py
  - vanguard/packages/runtime/evaluator_gateway.py
applies_to:
  - v0.6.2
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.2"
last_verified: 2026-08-23
supersedes: []
superseded_by: null
---

# Signed Verdict Contract (`SignedVerdict`)

> **Schema:** [`schemas/mhf/spi_payloads.schema.json`](../../schemas/mhf/spi_payloads.schema.json)  
> **Status:** `AS_BUILT` · Governed by ADR-0072 / ADR-0076.

---

## Wire Format

```json
{
  "verdict": "pass",
  "signature": "base64-ed25519-signature",
  "subject_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "evaluation_request_id": "req-018f23a4-8b1c-7f89",
  "oracle_id": "eval-daemon-uid-10002",
  "nonce": "n-9a23456789abcdef",
  "key_id": "evaluator-key-1",
  "signed_at": "2026-08-21T21:00:00Z"
}
```

## Security Invariants
1. **Cryptographic Binding**: The signature covers the RFC 8785 JCS bytes of every field except `signature`.
2. **Replay & Unbound Rejection**: A verdict presented with a mismatched nonce or unbound run ID is rejected fail-closed.
3. **Single Writer**: Evaluator gateway is the sole allowed writer of `VerdictRecorded` in the ledger.
4. **M-4 Eligibility**: RF-85 requires cryptographic verification against the same composition, run,
   trajectory, oracle, image, protocol, and event-range lineage; a copied signature or asserted
   `verified` flag is not evidence.
