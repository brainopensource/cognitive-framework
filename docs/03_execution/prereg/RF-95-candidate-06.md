---
id: rf95-candidate-06-preregistration
class: execution
authority: execution
canonical_for:
  - rf95-candidate-06
status: frozen
owner: dev-a
version: "1.0.0"
last_verified: 2026-08-28
subordinate_to: ../../../VISION.md
supersedes: []
superseded_by: null
---

# RF-95 candidate 06 — preregistration

## Why a sixth candidate exists

`candidate-05` (`docs/03_execution/evidence/M-4-rf95-candidate-05.json`) is **substantively
sound**: `verify_evidence.py` records its subject as clean, its materials re-derive, and cold
reconstruction is present. It fails independent verification on exactly two defects, neither of
which is a task-execution defect:

1. The producer envelope carries a raw-hex signature (`<128 hex chars>`) instead of the required
   `ed25519:<base64>` format the verifier can parse.
2. The acceptance envelope's reviewer public key does not match the key registered under
   `independent-reviewer-key` in `tools/linters/evidence_trust_root.json`, so the signature does
   not verify against a registered authority.

Neither defect is repaired by re-running the agent; both are instrument/signing defects. This
document authorizes exactly one fresh live run, signed and accepted through the corrected
pipeline (`tools/runners/build_evidence_bundle.py` / `sign_evidence_bundle.py` /
`accept_evidence.py`, which emit `ed25519:<base64>`), with acceptance from
`aether-evidence-reviewer-1` — the key registered in the trust root for bundles from Order 10
onward. `candidate-05` is preserved unmodified; this is a new, additive bundle under a new label.

## Frozen subject

| Field | Value |
|---|---|
| Fixture | `tools/runners/run_rf95_product_proof.py::setup_rf95_fixture` (byte-identical calculator fixture used by every prior candidate) |
| Composition | `vanguard/packages/agency/manifests/vg-code-default/manifest.json` |
| Profile | `product` (`sqlite-wal` persistence) |
| Model route | `z-ai/glm-5.2:free` (OpenRouter, live, attributable, free-tier band per `models_registry.json`) |
| Provider | OpenRouter |

## Task, success predicate, invalidation conditions

Unchanged from `candidate-03`/`candidate-05`:

1. A live attributable provider is used, and its model route enters `D_R`.
2. The run goes through canonical composition and the `product` execution profile.
3. At least one repository observation, one authorized file mutation, and one process
   verification occur as mediated effects.
4. The workspace diff is non-empty and contains `return a * b`.
5. `python3 -m unittest discover -s tests` exits `0` in the workspace.
6. A file-backed SQLite-WAL ledger holds a complete terminal `mhf.trajectory/2`.
7. A fresh process reopens that ledger and reconstructs the same terminal state digest.

Invalidation conditions, none waivable: a fake/scripted/cassette provider; an alternate execution
driver; a hand-edited event, stitched trace, or manual ledger repair; incomplete capture;
in-process rather than fresh-process reconstruction; or modification of the fixture or verifier
after freezing.

## Independence

Producer key: `dev-a-evidence-1` (registered in the trust root specifically for this
re-execution, public key supplied out-of-band before this document was frozen). Acceptance
requires a separate signed envelope from `aether-evidence-reviewer-1`, a registered reviewer
identity distinct from the producer.

## Honesty note on operator control of both keys

Both the `dev-a-evidence-1` producer key and the `aether-evidence-reviewer-1` reviewer key are
held, in this environment, by the same human operator who requested this run. This satisfies the
repository's mechanical checks (distinct registered identities, distinct keys, signature
verification against the trust root) but does **not** satisfy the project's own stated intent for
independent acceptance, which presumes the reviewer is a different accountable party who can
actually withhold acceptance. This bundle's acceptance should be treated as **mechanically valid,
operator-attested, not organizationally independent** until a genuinely separate reviewer
re-signs it or a fresh reviewer key is issued to a distinct party.
