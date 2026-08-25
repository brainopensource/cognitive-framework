---
status: living
id: architecture-glossary
class: architecture
authority: descriptive
canonical_for:
  - architectural-glossary
source_of_truth:
  - docs/SPEC.md
  - docs/02_decisions/INDEX.md
derived_from:
  - vanguard/packages/domain/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Architectural Glossary & Core Concepts

> **Status:** `AS_BUILT` · Descriptive View.

---

### A-B-C-D Operating Foundation
- **`A` — Authority**: The domain-blind S0–S12 reference monitor, selectors, attenuation, leases, and fail-closed policy.
- **`B` — Bundle**: The complete behavioral composition frozen into `FrozenHarness`; the Named Component Graph generalization is ratified for M-3.
- **`C` — Corpus**: Durable WAL events, derived state, trajectories, artifacts, receipts, and exterior evidence used for attribution and learning.
- **`D` — Digests**: The non-collapsible identity subjects $D_H$, $D_R$, and $D_X$.

### Three Planes of Responsibility
1. **Decision Plane**: Ephemeral, unprivileged model proposal generation and context reasoning.
2. **State Plane**: Derived truth calculated purely as $S = \text{fold}(\text{Events})$ from the ledger.
3. **Evidence Plane**: Cryptographically verifiable artifacts ($D_H$, $D_R$, $D_X$, Ed25519 signed verdicts).

### Identity Trinity
- **$D_H$ (Harness Composition Digest)**: SHA-256 digest over the complete behavioral composition (manifests, system prompts, capability ceilings, model routes, approval policies).
- **$D_R$ (Execution Digest)**: $H(D_H \parallel runtime \parallel environment \parallel model\ identity \parallel oracle\ identity)$.
- **$D_X$ (Experiment Digest)**: $H(D_R \parallel dataset \parallel protocol)$.

### Trusted Computing Base (TCB)
The minimal, domain-blind security core (`vanguard/packages/kernel/`) that enforces capability attenuation, action classification, and budget algebra. Strictly budgeted at $\le 1438$ logical lines of code.

### 6D Economic Resource Tensor
$$\mathbf{R} = \{\text{usd\_micros}, \text{tokens}, \text{bytes}, \text{charged\_millis}, \text{depth}, \text{turns}\}$$
Additive dimensions (USD, tokens, bytes, millis) are strictly conserved; structural dimensions (depth, turns) form non-additive ceilings.
