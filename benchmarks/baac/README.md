# Benchmark as Code (BaaC) 2.0 — Scientific Specification & Doctoral Reference Manual

> **Normative Technical Standard, Formal Methodology, and Operational Guide for Agentic Benchmarking.**

---

## Table of Contents
1. [Theoretical Foundations & Formal Model of Agentic Benchmarking](#1-theoretical-foundations--formal-model-of-agentic-benchmarking)
2. [Canonical Taxonomy & Complexity Dimensionality](#2-canonical-taxonomy--complexity-dimensionality)
3. [Hermetic Execution Architecture & Scientific Protocols](#3-hermetic-execution-architecture--scientific-protocols)
4. [Multi-Provider Execution Spectrum & Cost Profiles](#4-multi-provider-execution-spectrum--cost-profiles)
5. [Standardized Telemetry, Log Schemas & Mathematical KPIs](#5-standardized-telemetry-log-schemas--mathematical-kpis)
6. [Formal Root-Cause Attribution Engine](#6-formal-root-cause-attribution-engine)
7. [Step-by-Step Engineering Manual: Authoring New Challenges](#7-step-by-step-engineering-manual-authoring-new-challenges)
8. [CLI Operational Reference & Execution Workflows](#8-cli-operational-reference--execution-workflows)

---

## 1. Theoretical Foundations & Formal Model of Agentic Benchmarking

### 1.1 The POMDP Formulation of Autonomous Coding
An agentic coding evaluation is modeled as a finite-horizon **Partially Observable Markov Decision Process (POMDP)** defined by the 7-tuple:

$$\mathcal{M} = \langle \mathcal{S}, \mathcal{A}, \mathcal{T}, \mathcal{R}, \Omega, \mathcal{O}, \gamma \rangle$$

- **State Space ($\mathcal{S}$)**: The complete file-system state of the workspace directory, environment variables, git history, and runtime process table:
  $$\mathcal{S} = \mathcal{F}_{\text{workspace}} \times \mathcal{E}_{\text{env}} \times \mathcal{P}_{\text{runtime}}$$
- **Action Space ($\mathcal{A}$)**: Discrete tool invocations issued by the agent:
  $$\mathcal{A} = \{\text{view\_file}(p), \text{edit\_file}(p, \Delta), \text{run\_command}(c), \text{list\_dir}(p), \text{grep\_file}(q), \text{finish\_task}(m)\}$$
- **Transition Function ($\mathcal{T}: \mathcal{S} \times \mathcal{A} \to \mathcal{S}$)**: Deterministic mutation of workspace files or state execution resulting from command side-effects.
- **Observation Space ($\Omega$)**: The stdout, stderr, AST diff receipts, and file slice projections returned to the agent context.
- **Observation Function ($\mathcal{O}: \mathcal{S} \times \mathcal{A} \to \Omega$)**: The rendering pipeline transforming raw filesystem and process states into context window tokens.
- **Reward Function ($\mathcal{R}: \mathcal{S} \to \{0, 1\}$)**: The external, hermetic ground-truth verification score evaluated strictly by the non-leaked Oracle $\mathcal{V}_{\text{oracle}}(s_{\text{final}})$.

---

### 1.2 The Cryptographic Zero-State Invariant Theorem

> **Theorem 1 (Pristine Initial State Fidelity):**  
> Let $C$ be a benchmark challenge defined over initial file tree $\mathcal{F}_0$. Let $\mathcal{H}: \mathcal{F} \to \{0, 1\}^{256}$ be a cryptographic SHA-256 hash-tree operator mapping relative file paths and byte contents to a canonical manifest digest.
> An execution episode $E$ is valid *if and only if*:
> 1. $\mathcal{H}(\mathcal{F}_{\text{source}}) = \mathcal{H}_{\text{committed}}$ at timestamp $t_{\text{pre-flight}}$.
> 2. $\mathcal{S}_{\text{agent}} \cap \mathcal{F}_{\text{oracle}} = \emptyset$ (Strict Zero-Leakage Separation).
> 3. $\mathcal{H}(\mathcal{F}_{\text{source}}) = \mathcal{H}_{\text{committed}}$ at timestamp $t_{\text{post-reset}}$ (Zero-Drift Invariance).

```
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                          CHALLENGE SOURCE REPO                           │
   │  TASK.md  |  challenge.yaml  |  manifest.sha256  |  src/  |  oracle/     │
   └─────────────────────────────────────┬────────────────────────────────────┘
                                         │  Cryptographic Manifest Check
                                         ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                   PRE-FLIGHT ZERO-STATE VERIFIER (S0)                    │
   │      Assert: SHA256(file) == manifest.sha256 for all pristine files      │
   └─────────────────────────────────────┬────────────────────────────────────┘
                                         │  Materialize (Exclude oracle/)
                                         ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                  EPHEMERAL AGENT SCRATCH SANDBOX (S1)                    │
   │               Isolated temporary directory: /tmp/baac-scratch-*          │
   │         Agent operates with attenuated tools: view, edit, bash           │
   └─────────────────────────────────────┬────────────────────────────────────┘
                                         │  Agent completes or exhausts budget
                                         ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                 ISOLATED EXTERNAL ORACLE EVALUATOR (S2)                  │
   │    Execute oracle/verify.py against scratch sandbox (Read-Only Bridge)   │
   └─────────────────────────────────────┬────────────────────────────────────┘
                                         │  Wipe scratch & pycache
                                         ▼
   ┌──────────────────────────────────────────────────────────────────────────┐
   │                  POST-RESET ZERO-STATE VERIFIER (S3)                     │
   │         Confirm pristine challenge tree suffered 0 bytes of drift        │
   └──────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Canonical Taxonomy & Complexity Dimensionality

Every BaaC challenge is indexed by a 4-dimensional coordinate vector:

$$\mathbf{X}_{\text{challenge}} = \langle \text{Scope}, \text{ContextBracket}, \text{DifficultyTier}, \text{EvalType} \rangle$$

### 2.1 Scope Taxonomy ($\text{Scope} \in \Sigma$)
- **`single`**: Single-file modification. Localized AST edit, algorithmic bugfix, or mathematical formula correction.
- **`multi`**: Multi-file coordination. Cross-module imports, dependency graphs, interface contracts, and shared state stores.
- **`greenfield`**: Empty workspace synthesis. Construction of complete modules, classes, and CLI tools from scratch based on a normative specification.
- **`refactor`**: Structural AST transformation without altering semantic invariants (e.g. converting procedural code to immutable data structures).
- **`swe`**: Real-world repository issue reproduction and regression repair.

### 2.2 Context Bracket Taxonomy ($\text{Bracket} \in \mathcal{K}$)
Token budget boundaries determining the required model context retention:

$$\mathcal{K} = \{ \text{2K} \le 2,048, \;\; \text{8K} \le 8,192, \;\; \text{16K} \le 16,384, \;\; \text{32K} \le 32,768, \;\; \text{64K} \le 65,536, \;\; \text{128K} \le 131,072 \}$$

### 2.3 Difficulty Tier Hierarchy ($T_1 \dots T_6$)

| Tier | Category | Algorithmic / Cognitive Focus | Canonical Reference Challenge |
|---|---|---|---|
| **Tier 1** | **Elementary / Pure Logic** | Single-function formula repair, boundary clamping, string deduplication | `bench_single_2K_tier-1_calculator` |
| **Tier 2** | **Stateful Coordination** | JSON persistence, OOP state machines, lifecycle management | `bench_greenfield_8K_tier-2_quiz_game` |
| **Tier 3** | **Structural Patterns** | Asynchronous in-memory event bus, pub/sub wildcards, middleware stacks | `bench_multi_16K_tier-3_event_bus` |
| **Tier 4** | **Fault Tolerance & Resilience** | Stateful circuit breaker pattern, sliding window rate limiters | `bench_multi_32K_tier-4_circuit_breaker` |
| **Tier 5** | **Advanced Data Structures** | Persistent immutable prefix trie (path copying), topological DAG engine | `bench_multi_64K_tier-5_immutable_trie` |
| **Tier 6** | **Frontier / Distributed SOTA** | MVCC snapshot isolation engine, Raft consensus state machine | `bench_multi_128K_tier-6_mvcc_db` |

### 2.4 Canonical Naming Formalism
All benchmark challenge directory names and IDs MUST conform to the regular expression:

$$\mathbf{regex} = \text{bench\_}(single|multi|greenfield|refactor|swe)\_(2K|4K|8K|16K|32K|64K|128K)\_tier\text{-}[1\text{-}6]\_[a\text{-}z0\text{-}9\_]+$$

---

## 3. Hermetic Execution Architecture & Scientific Protocols

### 3.1 The 5-Stage Scientific Cycle
1. **Pre-flight Zero-State Verification**: Compute SHA-256 digest of all files in `challenges/<tier>/<challenge>/`. Compare byte-for-byte with committed `manifest.sha256`. If discrepancies exist, abort fail-closed with `DATASET_INVALID`.
2. **Ephemeral Workspace Isolation**: Create a cryptographically random directory `/tmp/baac-scratch-<cid>-<uuid>`. Copy all challenge files **excluding** `oracle/`, `challenge.yaml`, and `manifest.sha256`.
3. **Attenuated Agent Episode**:
   - Model port configured with pre-call budget checks (request cap, turn cap, USD cost cap).
   - Agent interacts via standard tool interfaces (`view_file`, `edit_file`, `run_command`).
4. **Isolated Oracle Verification**:
   - Post-episode, run `oracle/verify.py` as an independent subprocess against the scratch directory.
   - Capture return code, stdout, stderr, assertion counts, and failed test identifiers.
5. **Deterministic Cleanup & Re-verification**:
   - Wipe temporary scratch directory.
   - Purge bytecode (`__pycache__`) and SQLite WAL logs.
   - Re-verify challenge source repository SHA-256 digests to guarantee 0 bytes of drift.

---

## 4. Multi-Provider Execution Spectrum & Cost Profiles

BaaC supports multi-model routing across four operational tiers:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            MODEL ROUTING MATRIX                             │
├─────────────────┬──────────────────┬──────────────┬─────────────────────────┤
│ Mode Flag       │ Provider Engine  │ Cost ($/M)   │ Intended Application    │
├─────────────────┼──────────────────┼──────────────┼─────────────────────────┤
│ --mode lam      │ LAM Replay Mock  │ $0.00000     │ Sub-second CI, sanity   │
│ --mode ollama   │ Local Ollama     │ $0.00000     │ Open-weight SLM test    │
│ --mode live     │ OpenRouter Free  │ $0.00000     │ Zero-cost cloud testing │
│ --mode live     │ OpenRouter Cheap │ ~$0.14-$0.28 │ High-speed matrix runs  │
│ --mode live     │ Frontier SOTA    │ ~$3.00-$75.0 │ Opus / Sonnet 3.7 / SOTA│
└─────────────────┴──────────────────┴──────────────┴─────────────────────────┘
```

### Pricing Model Formulation
Token pricing is computed per-request via:

$$\text{Cost}_{\text{call}} = \frac{N_{\text{prompt}} \cdot P_{\text{prompt}} + N_{\text{completion}} \cdot P_{\text{completion}}}{10^6}$$

Where $P_{\text{prompt}}$ and $P_{\text{completion}}$ are defined in `MODEL_PRICING_TABLE`.

---

## 5. Standardized Telemetry, Log Schemas & Mathematical KPIs

### 5.1 JSON Schema of Record (`result.json`)
Every challenge execution emits an immutable telemetry record:

```json
{
  "challengeId": "bench_single_2K_tier-1_calculator",
  "tier": "tier-1",
  "scope": "single",
  "contextBracket": "2K",
  "preset": "vg-1-forge",
  "model": "deepseek/deepseek-v4-flash-0731",
  "mode": "live",
  "status": "PASS",
  "attribution": "PASS",
  "turns": 3,
  "promptTokens": 1420,
  "completionTokens": 180,
  "totalTokens": 1600,
  "costUsd": 0.000249,
  "durationSeconds": 1.45,
  "changedFiles": ["src/calculator.py"],
  "diffPatch": "--- a/src/calculator.py\n+++ b/src/calculator.py\n@@ -2,2 +2,2 @@\n-    resultado = (A + B) + B\n+    resultado = (A + B) * B\n",
  "oracle": {
    "passed": true,
    "exitCode": 0,
    "assertionCount": 4,
    "failingAssertions": [],
    "durationSeconds": 0.04
  },
  "diagnosis": "All falsifiers green",
  "metadata": {
    "author": "Vanguard Science",
    "difficulty": 1
  }
}
```

### 5.2 Mathematical KPI Definitions
- **Pass Rate per Tier ($PR_T$)**:
  $$PR_T = \frac{\sum_{i \in T} \mathbb{I}(\text{status}_i = \text{PASS})}{|T|} \times 100\%$$
- **Token Efficiency Index (TEI)**:
  $$\text{TEI} = \frac{\text{Baseline Minimum Tokens}}{\text{Actual Observed Tokens}}$$
- **Cost per Solved Task (CPST)**:
  $$\text{CPST} = \frac{\sum \text{Cost}_{\text{USD}}}{\sum \mathbb{I}(\text{status} = \text{PASS})}$$

---

## 6. Formal Root-Cause Attribution Engine

The attribution classifier deterministically maps outcomes to scientific root causes:

```
                          ┌───────────────────────────┐
                          │   Execution Terminated    │
                          └─────────────┬─────────────┘
                                        │
                         Is Oracle Missing / Invalid?
                                ├─── YES ───► [DATASET_INVALID]
                                │
                         Did Budget / Cap Exceed?
                                ├─── YES ───► [BUDGET_EXHAUSTED]
                                │
                         Did Harness Crash / Loop?
                                ├─── YES ───► [HARNESS_ERROR]
                                │
                         Did Oracle Assertions Pass?
                                ├─── YES ───► [PASS]
                                └─── NO  ───► [LLM_COGNITIVE_ERROR]
```

| Attribution Category | Definition & Failure Semantics |
|---|---|
| **`PASS`** | Oracle verification script returned exit code `0` with all assertions passing. |
| **`LLM_COGNITIVE_ERROR`** | Agent edited code and completed turns, but logic failed external unit test assertions. |
| **`HARNESS_ERROR`** | Exception in agent harness loop, unhandled tool error, or infinite turn exhaustion without edits. |
| **`BUDGET_EXHAUSTED`** | Execution aborted fail-closed due to exceeding max request, turn, or USD budget limits. |
| **`DATASET_INVALID`** | Challenge files drifted from committed SHA-256 digest or oracle script was syntactically invalid. |

---

## 7. Step-by-Step Engineering Manual: Authoring New Challenges

To contribute a new benchmark challenge, follow this procedural recipe:

### Step 1: Establish Canonical Metadata (`challenge.yaml`)
Create `benchmarks/baac/challenges/tier-<N>/bench_<scope>_<bracket>_tier-<N>_<slug>/challenge.yaml`:
```yaml
id: bench_multi_16K_tier-3_rate_limiter
name: Sliding Window Token Bucket Rate Limiter
scope: multi
context_bracket: 16K
tier: tier-3
difficulty: 3
timeout_seconds: 35
entrypoint: src/limiter.py
eval_type: oracle
tags:
  - concurrency
  - rate_limiting
  - algorithms
metadata:
  author: "Vanguard Team"
  created_at: "2026-08-31"
  domain: "networking"
```

### Step 2: Formulate the Task Brief (`TASK.md`)
Write unambiguous, mathematically precise requirements in `TASK.md`:
```markdown
# Task: Sliding Window Token Bucket Rate Limiter

Implement `TokenBucketLimiter` in `src/limiter.py`.

## Requirements:
1. `__init__(self, capacity: int, refill_rate_per_sec: float)`
2. `acquire(self, tokens: int = 1) -> bool`: Returns `True` if tokens available, `False` otherwise.
3. Thread-safe execution under concurrent access.
```

### Step 3: Provide Starting Workspace (`src/`)
Place initial boilerplate or broken implementation in `src/`:
```python
# src/limiter.py
class TokenBucketLimiter:
    def __init__(self, capacity: int, refill_rate_per_sec: float):
        pass
```

### Step 4: Construct External Oracle (`oracle/verify.py`)
Write deterministic unittest assertions in `oracle/verify.py`:
```python
#!/usr/bin/env python3
import sys, unittest
from pathlib import Path

class TestLimiterOracle(unittest.TestCase):
    def test_rate_limiting(self):
        ws = Path(sys.argv[-1] if len(sys.argv) > 1 and sys.argv[-2] == "--workspace" else ".").resolve()
        sys.path.insert(0, str(ws / "src"))
        from limiter import TokenBucketLimiter
        
        limiter = TokenBucketLimiter(capacity=2, refill_rate_per_sec=1.0)
        self.assertTrue(limiter.acquire(1))
        self.assertTrue(limiter.acquire(1))
        self.assertFalse(limiter.acquire(1))

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestLimiterOracle)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
```

### Step 5: Generate and Verify Cryptographic Manifest
```bash
# Generate manifest.sha256
python3 -m benchmarks.baac.cli generate-manifest --single bench_multi_16K_tier-3_rate_limiter

# Verify zero-state integrity
python3 -m benchmarks.baac.cli verify --single bench_multi_16K_tier-3_rate_limiter
```

---

## 8. CLI Operational Reference & Execution Workflows

### 8.1 Catalog Inspection
```bash
# List all challenges across all tiers
python3 -m benchmarks.baac.cli catalog

# Filter catalog by tier or scope
python3 -m benchmarks.baac.cli catalog --tier tier-1
python3 -m benchmarks.baac.cli catalog --scope multi
```

### 8.2 Cryptographic Zero-State Verification
```bash
# Verify integrity of all committed challenges
python3 -m benchmarks.baac.cli verify

# Verify single challenge
python3 -m benchmarks.baac.cli verify --single bench_single_2K_tier-1_calculator
```

### 8.3 Full Scientific Cycle (Verify $\to$ Run $\to$ Clean $\to$ Verify)
```bash
# Sub-second offline replay via LAM engine ($0 cost)
python3 -m benchmarks.baac.cli cycle --mode lam

# Full cycle on Tier 1
python3 -m benchmarks.baac.cli cycle --mode lam --tier tier-1

# Live execution against OpenRouter DeepSeek V4 Flash
python3 -m benchmarks.baac.cli cycle --mode live --model deepseek/deepseek-v4-flash-0731 --single bench_single_2K_tier-1_calculator
```

### 8.4 Live Frontier SOTA Evaluation
```bash
# Evaluate Claude 3.7 Sonnet on Tier 6 with $0.50 budget ceiling
python3 -m benchmarks.baac.cli run \
  --mode live \
  --model anthropic/claude-3.7-sonnet \
  --tier tier-6 \
  --budget 0.50 \
  --max-turns 12
```

### 8.5 Workspace State Reset & Cleanup
```bash
# Clean all temporary scratch directories and purge bytecode
python3 -m benchmarks.baac.cli clean
```

### 8.6 Telemetry Inspection & Reporting
```bash
# Display latest execution report
python3 -m benchmarks.baac.cli report

# Display specific run by ID
python3 -m benchmarks.baac.cli report --run-id baac-vg-1-forge-lam-1788220164
```
