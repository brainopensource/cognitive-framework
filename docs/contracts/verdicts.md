---
status: living
id: contract-verdicts
class: contract-reference
authority: descriptive
canonical_for:
  - signed-verdict-contract
source_of_truth:
  - docs/SPEC.md#1-system-charter-and-boundaries
  - docs/05_adr/0072-plugin-boundary-wire-first-evaluator-exterior.md
derived_from:
  - schemas/mhf/spi_payloads.schema.json
  - vanguard/packages/adapters/evaluators/signing.py
  - vanguard/packages/runtime/evaluator_gateway.py
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
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
  "evaluation_request_id": "req-018f23a4-8b1c-7f89",
  "subject_run_id": "run-018f23a4-8b1c-0001",
  "oracle_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "verdict": "pass",
  "score": 1.0,
  "nonce": "n-9a23456789abcdef",
  "evaluator_identity": {
    "evaluator_id": "eval-daemon-uid-10002",
    "public_key": "ed25519:abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
  },
  "signature": "base64:3f98ab...signed_jcs_bytes..."
}
```

## Security Invariants
1. **Cryptographic Binding**: The signature covers JCS RFC 8785 canonical bytes of $(request\_id, subject\_id, oracle\_digest, verdict, score, nonce)$.
2. **Replay & Unbound Rejection**: A verdict presented with a mismatched nonce or unbound run ID is rejected fail-closed.
3. **Single Writer**: Evaluator gateway is the sole allowed writer of `VerdictRecorded` in the ledger.
