---
status: living
id: architecture-glossary
class: architecture
authority: descriptive
canonical_for:
  - architectural-glossary
source_of_truth:
  - docs/SPEC.md
  - docs/05_adr/INDEX.md
derived_from:
  - vanguard/packages/domain/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Architectural Glossary & Core Concepts

> **Status:** `AS_BUILT` · Descriptive View.

---

### A-B-C-D Operating Model
- **`A` (Actuator / Engine)**: The cognitive turn loop that observes context and proposes tool effects.
- **`B` (Boundary / Kernel)**: The 13-stage monotonic attenuation core (TCB) that enforces capabilities, budgets, and security.
- **`C` (Chronicle / Ledger)**: The single-writer, append-only SQLite WAL stream containing immutable causal events.
- **`D` (Discriminator / Evaluator)**: The physically isolated exterior judge that grades execution runs and issues signed verdicts.

### Three Planes of Responsibility
1. **Decision Plane**: Ephemeral, unprivileged model proposal generation and context reasoning.
2. **State Plane**: Derived truth calculated purely as $S = \text{fold}(\text{Events})$ from the ledger.
3. **Evidence Plane**: Cryptographically verifiable artifacts ($D_H$, $D_R$, $D_X$, Ed25519 signed verdicts).

### Identity Trinity
- **$D_H$ (Harness Composition Digest)**: SHA-256 digest over the complete behavioral composition (manifests, system prompts, capability ceilings, model routes, approval policies).
- **$D_R$ (Runtime Run Digest)**: Unique cryptographic hash of a single continuous execution episode.
- **$D_X$ (Experiment / Evaluation Digest)**: Hash over $(D_H, D_R, \text{TaskInputs}, \text{EvaluatorVersion})$.

### Trusted Computing Base (TCB)
The minimal, domain-blind security core (`vanguard/packages/kernel/`) that enforces capability attenuation, action classification, and budget algebra. Strictly budgeted at $\le 1438$ logical lines of code.

### 6D Economic Resource Tensor
$$\mathbf{R} = \{\text{usd\_micros}, \text{tokens}, \text{bytes}, \text{charged\_millis}, \text{depth}, \text{turns}\}$$
Additive dimensions (USD, tokens, bytes, millis) are strictly conserved; structural dimensions (depth, turns) form non-additive ceilings.
