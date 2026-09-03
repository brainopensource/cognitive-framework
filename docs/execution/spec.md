---
id: execution.feature_spec
canonical_id: execution.feature_spec
class: specification
authority: execution
status: active
owner: repository-governance
canonical_for:
  - active-feature-delta-specification
version: "1.0.0"
date: "2026-09-03"
normative_authority:
  - docs/SPEC.md
  - docs/architecture/boundaries.md
relationships:
  - execution.milestones
  - execution.backlog
  - execution.tasks
---

# Feature Delta Specification: W-092-F1 / CMX-09 (Canonical Coding Max Convergence)

## 1. Architectural Base & Invariant Topography

This document is the authoritative typed delta contract for the active execution ticket **`W-092-F1 / CMX-09`**. It defines the exact interfaces, data schemas, transaction protocols, and error matrices added to the codebase. Upon gate passage and PR merge, these contracts are promoted into canonical `docs/architecture/` and `docs/SPEC.md`.

- **Base Architecture Extended**:
  - `docs/architecture/boundaries.md` (Hexagonal boundary flow: `domain <- ports <- kernel <- agency <- runtime -> adapters`)
  - `docs/architecture/data-flow.md` (Monotonic capability dispatch and immutable event emission)
- **Target Subsystems Modified**:
  - `vanguard/packages/domain/task_state.py` (New: Semantic task state vector & DAG)
  - `vanguard/packages/adapters/environment/transaction.py` (New: Two-Phase Commit Multi-File Transaction Manager)
  - `vanguard/packages/runtime/governance/tamper_shield.py` (New: Cryptographic Test Tamper Shield)
  - `vanguard/packages/agency/context/progressive.py` (New: Multi-Tier Progressive Context Compiler)
  - `vanguard/packages/adapters/models/dialect.py` (Enhanced: Multi-pattern recovery & typed failure classes)

---

## 2. Invariants & Boundary Constraints

- **INV-DELTA-1 (Hexagonal Purity)**: All state schemas (`SemanticTaskState`, `TaskStep`) in `domain/` must use Python stdlib only, serialize deterministically via RFC 8785 JCS, and contain zero I/O or adapter imports.
- **INV-DELTA-2 (TCB Line Budget Limit)**: No changes in this feature wave may increase `vanguard/packages/kernel/` beyond the strict $\le 1438$ logical LOC ceiling.
- **INV-DELTA-3 (Two-Phase Commit Atomic Safety)**: No multi-file modification may write partially to disk. All candidate file mutations must pass in-memory AST syntax validation (`ast.parse`) before disk flush. Any syntax error triggers full rollback to pre-transaction content.
- **INV-DELTA-4 (Anti-Tampering Test Isolation)**: Autonomous agents are strictly prohibited from mutating test suites during implementation. All test files are hashed at turn 0; any modification to test baselines produces immediate fail-closed rejection.
- **INV-DELTA-5 (Deterministic Progressive Context)**: System prompts and immutable invariants must form a prefix-stable anchor. Compaction must never truncate `settled_invariants` or `falsified_hypotheses`.

---

## 3. Data Contracts & Domain Schemas

### 3.1 Semantic Task State Vector (`domain/task_state.py`)

```python
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Sequence

class StepState(str, Enum):
    PENDING = "pending"
    READY = "ready"
    ACTIVE = "active"
    VERIFIED = "verified"
    FAILED = "failed"

@dataclass(frozen=True, slots=True)
class TaskStep:
    step_id: str                          # Monotonic ID: e.g. "step-001"
    title: str                            # Human-readable objective
    target_files: tuple[str, ...]         # Target files for this step
    dependencies: tuple[str, ...] = ()    # Pre-requisite step IDs
    state: StepState = StepState.PENDING
    falsification_evidence: str | None = None
    verification_digest: str | None = None

@dataclass(frozen=True, slots=True)
class SemanticTaskState:
    run_id: str
    revision: int                         # Monotonically increasing state version
    overarching_goal: str                 # Top-level immutable objective
    active_step_id: str | None            # Currently executing step
    backlog: tuple[TaskStep, ...]         # Ordered task DAG steps
    falsified_hypotheses: tuple[str, ...] # Negative memory: failed attempts not to repeat
    settled_invariants: tuple[str, ...]   # Verified architectural truths
    changed_files_tree_hash: str          # Current working tree SHA-256
```

---

## 4. Multi-File Two-Phase Commit (`2PC`) Transaction Protocol

### 4.1 Interface Specification (`adapters/environment/transaction.py`)

```python
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence
from vanguard.packages.domain.results import Result

@dataclass(frozen=True, slots=True)
class FileMutation:
    path: str
    content: str
    action: Literal["create", "modify", "delete"]

@dataclass(frozen=True, slots=True)
class TransactionReceipt:
    transaction_id: str
    mutated_files: tuple[str, ...]
    tree_hash_before: str
    tree_hash_after: str

class AtomicMultiFileTransactionManager:
    """Two-Phase Commit transaction manager guaranteeing zero half-broken multi-file states."""
    
    def __init__(self, workspace_root: Path) -> None:
        self._root = workspace_root

    def execute_transaction(
        self,
        mutations: Sequence[FileMutation],
    ) -> Result[TransactionReceipt]:
        """Phase 1: Preflight in-memory shadow tree & AST check.
        Phase 2: Atomic commit to disk, or full rollback on any failure."""
        ...
```

### 4.2 Preflight Validation Rules:
1. Every modified or created `.py` file is validated via `ast.parse(source, filename=path)`. Syntax errors abort immediately.
2. Every imported symbol from local modules within the transaction set must resolve.
3. If any step fails, all original file contents are restored from in-memory pre-image snapshots.

---

## 5. Synthetic Test Oracle Bootstrapping Protocol

For greenfield tasks where no test suite exists in the baseline repository:
1. **Stage 1 (Contract Synthesis)**: Agent authors pure port interfaces / protocols under `vanguard/packages/ports/` or domain types.
2. **Stage 2 (Oracle Synthesis)**: Agent creates a synthetic test suite under `test/` defining terminal behavioral assertions.
3. **Stage 3 (Falsifier Confirmation)**: Agent runs the synthetic test against empty/stub implementations. **The test MUST fail** with expected `NotImplementedError` or assertion failure. If it passes on stubs, it is vacuous and rejected.
4. **Stage 4 (Freeze Oracle)**: The test file SHA-256 is registered in `TestTamperShield`.
5. **Stage 5 (Implementation)**: Agent implements code until the synthetic oracle passes.

---

## 6. Cryptographic Test Tamper Shield (`runtime/governance/tamper_shield.py`)

```python
from __future__ import annotations
import hashlib
from pathlib import Path

class TestTamperShield:
    """Guarantees agents cannot manufacture green passes by altering test files."""
    
    def __init__(self, workspace: Path, test_patterns: tuple[str, ...] = ("test/**", "tests/**", "*_test.py")):
        self._workspace = workspace
        self._patterns = test_patterns
        self._baseline_hashes: dict[str, str] = self._snapshot_hashes()

    def _snapshot_hashes(self) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for pattern in self._patterns:
            for p in self._workspace.glob(pattern):
                if p.is_file() and p.suffix in (".py", ".ts", ".js"):
                    hashes[str(p.relative_to(self._workspace))] = hashlib.sha256(p.read_bytes()).hexdigest()
        return hashes

    def verify_integrity(self) -> tuple[bool, str]:
        """Fails closed if any test file was modified or removed."""
        for rel_path, expected_hash in self._baseline_hashes.items():
            f = self._workspace / rel_path
            if not f.exists():
                return False, f"Test file deleted: {rel_path}"
            if hashlib.sha256(f.read_bytes()).hexdigest() != expected_hash:
                return False, f"Test file tampered with: {rel_path}"
        return True, "Test integrity verified"
```

---

## 7. Progressive Context Compiler (`agency/context/progressive.py`)

Context is budgeted across 4 strict mathematical tiers:

```
Total Turn Budget (e.g., 16,000 tokens)
├── Tier 0: Invariant Anchor [Priority 100, Immutable] (~800 tokens)
│   ├── Overarching Task Goal + System Invariants
│   └── Current Active Step Specification
├── Tier 1: Negative Memory [Priority 90, Prefix-Stable] (~1,200 tokens)
│   └── Falsified Hypotheses List (Past failed patches and error signatures)
├── Tier 2: Active Working Slice [Priority 80, AST Sliced] (~4,000 tokens)
│   └── Exact AST slice of target function/class being edited (not full file)
└── Tier 3: Symbol Topology Stubs [Priority 70, Token-Bounded] (~6,000 tokens)
    └── Signatures and docstrings of directly referenced dependencies
```

---

## 8. Self-Healing Model Dialect Engine (`adapters/models/dialect.py`)

### 8.1 Typed Failure Taxonomy & Corrective Actions

| Failure Class | Root Cause Signature | Corrective Action |
|---|---|---|
| `TRANSPORT` | Socket reset, timeout, HTTP 5xx | `RETRY_TRANSPORT` with exponential backoff |
| `PROTOCOL` | Unparseable JSON, malformed schema | `DEGRADE_DIALECT` to markdown fenced JSON |
| `TRUNCATION` | Premature `finish_reason: length` | `CONTINUE_OUTPUT` requesting remainder |
| `TOOL_CALL` | Invalid tool name or missing args | `REPAIR_TOOL_CALL` feeding schema definition back |
| `PATCH` | Pre-image mismatch, hunk reject | `RELOCATE_AND_RECOMPILE` re-reading target file slice |
| `VERIFICATION` | Test failed with non-zero exit | `RECORD_FALSIFICATION` adding hypothesis to Tier 1 |
| `PERMISSION` | Capability or budget denial | `ESCALATE_APPROVAL` requiring human signature |

---

## 9. CLI Arguments & Invocation Surface

```text
vg code [OPTIONS]

Options:
  --plan PATH              Path to existing task plan DAG JSON.
  --brief PATH             Task description Markdown file (default: TASK.md).
  --preset [fast|balanced|max]
                           Execution profile preset (default: balanced).
  --budget-micros INT      Maximum cost ceiling in USD microdollars.
  --dry-run                Validate preflight syntax and AST without disk mutation.
  --tamper-shield          Enforce strict read-only test suite hash verification (default: true).
  --json                   Stream newline-delimited JSON events to stdout.
```

### Exit Codes
- `0`: Completed successfully; all task steps verified and admission gate passed.
- `1`: Verification failed; reproducer or test assertions failed.
- `2`: Invalid arguments, schema violation, or unparseable task brief.
- `3`: Unavailable; budget exhausted or provider connection refused.
- `127`: Missing system dependencies (e.g., neither `patch` nor `git` available).
