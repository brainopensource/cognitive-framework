---
id: vanguard-sota-coding-harness-engineering-roadmap
class: architecture-treatise
authority: principal-architectural-strategy
status: draft
owner: engineering-architecture-council
version: "1.0.0"
date: "2026-09-02"
supersedes: []
---

# SOTA Coding Agent Harness: Principal Architectural Blueprint & Production Roadmap

## Executive Summary & Engineering Intent

Autonomous software engineering agents require significantly more than a prompt loop wrapped around LLM tool calling. While toy benchmarks (such as single-file bugfixes on small functions) can be solved with primitive ReAct loops, **industrial-grade real-world software engineering** demands robust answers to five foundational systems challenges:

1. **Long-Horizon Agency & Horizon Collapse**: Complex tasks require 50 to 200 turns of continuous reasoning, exploration, editing, and debugging. Without structured state retention and hierarchical task decomposition, modern LLMs suffer from context dissipation, catastrophic forgetting, and attention degradation.
2. **Greenfield Architecture & Multi-File Dependency Graph Synthesis**: Constructing new subsystems, services, or multi-component features requires synthesizing code across dozens of interdependent files in topological order, establishing contracts before implementations, and bootstrapping verification harnesses before runnable tests exist.
3. **Brownfield Blast-Radius Containment & Context Economics**: Operating in multi-million-line legacy repositories requires progressive symbol-level context compilation rather than full-file dumping. The agent must accurately calculate the blast radius of changes and verify downstream contracts without exceeding token budgets or context limits.
4. **Durable State Continuity Across Process Boundaries**: Process restarts, operator interventions, network interruptions, and rate-limit suspensions must not destroy in-flight progress or induce duplicate effect execution. Resumed sessions must seamlessly rebuild cognitive state from durable ledgers.
5. **Deterministic Verification & Anti-Tampering Trust Spines**: Autonomous agents frequently attempt to declare victory prematurely by running redundant tests, modifying test assertions to pass broken code (test poisoning), or misinterpreting syntax warnings as semantic passes. A fail-closed, external exterior judge must govern completion.

This treatise provides the forensic analysis, mathematical/formal protocols, architectural diagrams, concrete pseudocode, and an actionable engineering roadmap to elevate Vanguard / AETHER to the undisputed State of the Art (SOTA) in autonomous coding harnesses.

---

## 1. Forensic Audit: The 6 Bottlenecks Blocking SOTA Agency

Through systematic review of the integrated codebase (`vanguard/packages/` across `domain`, `kernel`, `agency`, `runtime`, and `adapters`), the following concrete bottlenecks have been identified:

```
+---------------------------------------------------------------------------------------------------+
|                                 SOTA HARNESS BOTTLENECK TAXONOMY                                  |
+---------------------------------------------------------------------------------------------------+
|  1. Context-Attention Dissipation         |  2. Greenfield Blindness & Unstructured Mutations     |
|     - Sliding window forgets invariants   |     - Lack of Topological Multi-File Creation DAG     |
|     - Redundant exploration repeats       |     - Absence of Pre-Implementation Oracle Synthesis  |
+-------------------------------------------+-------------------------------------------------------+
|  3. Brownfield Blast-Radius Blindness     |  4. In-Flight Memory State Severance                  |
|     - Whole-file dumping context penalty  |     - Subprocess crash loses uncommitted session state|
|     - Cross-module signature regressions  |     - Ephemeral cache divergence on restart           |
+-------------------------------------------+-------------------------------------------------------+
|  5. Model Dialect Degeneration            |  6. Verification Livelocks & Test Tampering           |
|     - Fenced-JSON vs Native Schema drift  |     - Redundant verification looping                  |
|     - Silent tool-call syntax truncations |     - Self-grading / test mutation escape             |
+---------------------------------------------------------------------------------------------------+
```

### 1.1 Bottleneck 1: Context-Attention Dissipation in Long Runs

#### The Phenomenon
In tasks exceeding 25 turns, the LLM context window fills with large command outputs, diff hunks, and historical tool results. Standard context compacters (such as sliding windows or naive summarizers) summarize or truncate the middle turns.
- **Consequence**: The agent forgets:
  1. Why earlier architectural decisions were made;
  2. Which candidate hypotheses were already falsified (causing the agent to re-try previously failed patches);
  3. The exact overarching plan and its completed versus pending sub-tasks.

#### Root Cause in Code
In `vanguard/packages/agency/episode/compactor.py` and `context/compiler.py`, compaction operates as an unstructured text truncation or windowed drop. While `vanguard/packages/runtime/task_state.py` defines `SemanticTaskState`, it is currently decoupled from the active prompt compilation pipeline in `EpisodeEngine.step()`:

```python
# CURRENT FLAW: vanguard/packages/agency/episode/engine.py
# The context compiled for turn N is formed by appending raw turns to the system prompt:
context = self._compiler.compile(
    system_prompt=self._system_prompt,
    history=self._history, # Linear growth, loses structured invariants upon truncation
    budget=self._remaining_tokens
)
```

### 1.2 Bottleneck 2: Greenfield Synthesis & Multi-File Dependency Blindness

#### The Phenomenon
When tasked with creating a new feature requiring 5+ new files (e.g., domain models, port protocols, adapters, wiring, and tests), the agent often:
1. Writes implementation files before port interfaces are declared;
2. Writes caller modules before callee types exist;
3. Suffers from cyclic import errors and incomplete type exports;
4. Has no mechanism to test early files before the entire feature is written.

#### Root Cause in Code
`vanguard/packages/agency/episode/episode.py` dispatches single actions atomically (`patch.apply` or `fs.write`). There is no higher-level **Topological Multi-File Transaction DAG** that forces the agent to commit declarations before definitions, and no **Synthetic Test Oracle Bootstrapper** to provide immediate executable feedback on incomplete subsystems.

### 1.3 Bottleneck 3: Brownfield Blast-Radius Miscalculation & Context Economics

#### The Phenomenon
In large repositories, modifying a utility or core protocol often breaks downstream consumers. If the agent only inspects the immediate target file:
1. Downstream typecheck and integration suites break unexpectedly at turn 40;
2. The agent panics and enters an unstructured patching frenzy, attempting local hacks in downstream files rather than preserving interface stability.

#### Root Cause in Code
While LDA (`tools/007_LLM_DOCS_ATLAS`) and the code map exist, they are invoked as ad-hoc tools rather than being built into the **Pre-Flight Mutation Protocol**. When `patch.apply` is evaluated in `vanguard/packages/adapters/environment/git.py`, it validates unified diff syntax, but does not calculate or surface the static AST caller graph or downstream impact before the write settles.

### 1.4 Bottleneck 4: In-Flight State Severance Across Process Restarts

#### The Phenomenon
Under RF-25/BETA-12, events are durably persisted to SQLite WAL. However, cognitive metadata—such as:
- `_completion_changed_files`
- `_completion_verification`
- Sub-agent task progress
- Falsified hypothesis memory
is retained in Python object memory within `HarnessSession`. If a process is killed by an operating system signal (SIGTERM/SIGKILL) or suspended for human approval, the re-instantiated session must reconstruct this state purely by re-playing and reducing raw events. If the ledger lacks structured semantic checkpoint events, recovery is partial or lossy.

### 1.5 Bottleneck 5: Model Dialect Degeneration & Tool-Calling Syntax Drift

#### The Phenomenon
Different frontier models employ vastly different tool-calling mechanisms:
- **Claude 3.5 Sonnet**: Native XML tags / JSON parameter blocks;
- **DeepSeek V3 / V4**: Markdown fenced JSON code blocks with specific escaping rules;
- **OpenAI GPT-4o**: Structured Outputs / native function call frames;
- **Local Small Models (e.g. Qwen 2.5 Coder 7B/14B)**: Inconsistent schema adherence, frequently omitting closing brackets or outputting prose before tool calls.

When a harness relies on a rigid parser, dialect degeneration produces `SyntaxError` or `instrument_error`, consuming turn budget without semantic progress.

### 1.6 Bottleneck 6: Verification Livelocks & Test Oracle Tampering

#### The Phenomenon
1. **Redundant Verification Livelock**: Once a test suite passes, the agent does not recognize completion and re-runs the test suite 5 to 10 times with tiny variations, exhausting the budget.
2. **Test Poisoning**: When faced with a difficult bug, an unattended agent sometimes alters the test file (e.g., changing `assert result == 42` to `assert True` or commenting out test cases) to manufacture a false pass.

#### Solution Status in Code
We successfully introduced loop-breaking in `session.py` (`_completion_redundant_verifications`), but test oracle isolation requires a cryptographic fence where test suites are mounted read-only and verified against an immutable hash.

---

## 2. The Target SOTA Architecture: Formal Protocols & Invariants

To eliminate these bottlenecks permanently, Vanguard must implement four architectural pillars:

```
+---------------------------------------------------------------------------------------------------+
|                                 SOTA CODING HARNESS ARCHITECTURE                                  |
+---------------------------------------------------------------------------------------------------+
|                                                                                                   |
|  +---------------------------------+             +---------------------------------------------+  |
|  |     Cognitive State Spine       |             |         Context Economics Pipeline          |  |
|  |  - SemanticTaskState (CAS)      | <---------> |  - Progressive Context Compiler (PCC)       |  |
|  |  - Hierarchical Task Backlog    |             |  - Hierarchical AST / Symbol Outliner       |  |
|  |  - Falsified Hypothesis Ledger  |             |  - Structural Compactor (Lossless Invariant)|  |
|  +---------------------------------+             +---------------------------------------------+  |
|                  |                                                      |                         |
|                  v                                                      v                         |
|  +---------------------------------+             +---------------------------------------------+  |
|  |    Multi-File Execution Mesh    |             |        Autonomous Verification Spine        |  |
|  |  - Topological Transaction DAG  | <---------> |  - Tamper-Proof Oracle Perimeter (UID 10002)|  |
|  |  - Two-Phase Commit (2PC) Patch |             |  - Synthetic Test Generator (Greenfield)    |  |
|  |  - Blast-Radius Preflight AST   |             |  - Monotonic Completion Gate (No Livelock)  |  |
|  +---------------------------------+             +---------------------------------------------+  |
|                                                                                                   |
+---------------------------------------------------------------------------------------------------+
```

### 2.1 Pillar I: The Semantic Cognitive State Spine (`SemanticTaskState`)

Instead of relying on LLM memory or raw message histories, long-running agents must maintain a **Durable Semantic State Vector** committed to the ledger after every turn.

#### Formal Contract: `vanguard/packages/domain/task_state.py`
```python
@dataclass(frozen=True, slots=True)
class TaskStep:
    step_id: str                      # Unique monotonic identifier: "step-001"
    title: str                        # Concise objective: "Define Domain Port Protocol"
    target_files: tuple[str, ...]     # Explicit target scope: ("ports/storage.py",)
    dependencies: tuple[str, ...]     # Pre-requisite step IDs: ()
    status: StepStatus                # PENDING | IN_PROGRESS | VERIFIED | BLOCKED
    falsification_evidence: str | None # Error trace if previously failed
    verification_hash: str | None     # Tree hash when verified

@dataclass(frozen=True, slots=True)
class SemanticTaskState:
    run_id: str
    revision: int
    overarching_goal: str
    active_step_id: str | None
    backlog: tuple[TaskStep, ...]
    falsified_hypotheses: tuple[str, ...]
    settled_invariants: tuple[str, ...]
    changed_files_tree_hash: str
```

#### Invariants:
- **I-STATE-1 (Monotonic Revision)**: Every update increments `revision` and emits `TaskStateCheckpoint` to the event store with a cryptographically signed SHA-256 state digest.
- **I-STATE-2 (Zero Context Amnesia)**: Compaction algorithms are strictly forbidden from altering or omitting `settled_invariants` and `falsified_hypotheses`. They are injected as the immutable cognitive prefix of every turn.

---

### 2.2 Pillar II: Progressive Context Economics & Dynamic Symbol Outlining

Loading entire files into the prompt window wastes tokens and dilutes attention. SOTA harnesses employ **Progressive Disclosure**:

```
Level 0: Repository Code Map & Architecture Invariants (~500 tokens)
   |
Level 1: Symbol Signatures & Docstrings of Relevant Subsystems (~2,000 tokens)
   |
Level 2: Targeted Function Slices & Direct Callers (~4,000 tokens)
   |
Level 3: Full File Body (ONLY for the immediate file being edited, max 1-2 files)
```

#### Protocol: `vanguard/packages/agency/context/progressive.py`
```python
class ProgressiveContextCompiler:
    """Compiles token-bounded context with mathematical priority guarantees."""
    
    def compile(
        self,
        task_state: SemanticTaskState,
        active_file: Path,
        token_budget: int
    ) -> CompiledPromptContext:
        # 1. Tier 0: Invariant Anchor (Immutable task brief, active step, rules)
        tier0 = self._render_invariants(task_state)
        remaining = token_budget - count_tokens(tier0)
        
        # 2. Tier 1: Falsification Memory (What NOT to do)
        tier1 = self._render_falsified_hypotheses(task_state.falsified_hypotheses)
        remaining -= count_tokens(tier1)
        
        # 3. Tier 2: Active Working Slice (AST slice of target function, not entire file)
        tier2 = self._slice_extractor.get_active_slice(active_file, task_state.active_step_id)
        remaining -= count_tokens(tier2)
        
        # 4. Tier 3: Neighboring Interface Stubs (Signatures only via LDA / tree-sitter)
        tier3 = self._symbol_outliner.extract_signatures(active_file.parent, budget=remaining)
        
        return assemble_context(tier0, tier1, tier2, tier3)
```

---

### 2.3 Pillar III: Greenfield Multi-File Synthesis & Two-Phase Commit (2PC)

To solve greenfield problems without cascading syntax errors, mutations across multiple files must follow a **Two-Phase Commit (2PC) Transaction Protocol**:

```
Agent Proposes Transaction (File A, File B, File C)
    |
Phase 1: PRE-FLIGHT (In-Memory Shadow Tree)
    |---> Syntax Check (ast.parse on all targets)
    |---> Symbol Export/Import Linkage (all referenced symbols resolve)
    |---> Type Consistency Verification (mypy / tsc dry run)
    |
Phase 2: COMMIT or ROLLBACK
    |---> If all checks PASS: Atomic write to disk, emit TransactionCommitted
    +---> If any check FAILS: Rollback shadow tree, emit TransactionRejected with exact syntax diagnostics
```

#### Protocol: `vanguard/packages/adapters/environment/transaction.py`
```python
@dataclass(frozen=True)
class FileMutation:
    path: str
    content: str
    action: Literal["create", "modify", "delete"]

class AtomicMultiFileTransactionManager:
    """Guarantees zero half-broken multi-file states."""
    
    def __init__(self, workspace_root: Path):
        self._root = workspace_root
        
    def execute_transaction(
        self,
        mutations: Sequence[FileMutation]
    ) -> Result[TransactionReceipt]:
        shadow_tree: dict[Path, str | None] = {}
        backups: dict[Path, str | None] = {}
        
        try:
            # Step 1: Pre-flight stage (read existing, stage new)
            for m in mutations:
                target = (self._root / m.path).resolve()
                backups[target] = target.read_text("utf-8") if target.exists() else None
                shadow_tree[target] = m.content if m.action != "delete" else None
                
            # Step 2: AST and Static Link Verification
            for path, content in shadow_tree.items():
                if content is not None and path.suffix == ".py":
                    ast.parse(content, filename=str(path)) # Fails fast on syntax error
                    
            # Step 3: Atomic Flush to Disk
            for path, content in shadow_tree.items():
                if content is None:
                    if path.exists(): path.unlink()
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
                    
            return Result.success(TransactionReceipt(mutated_files=tuple(m.path for m in mutations)))
            
        except Exception as exc:
            # ROLLBACK to exact pre-transaction state
            for path, original_content in backups.items():
                if original_content is None:
                    if path.exists(): path.unlink()
                else:
                    path.write_text(original_content, encoding="utf-8")
            return Result.fail("transaction_aborted", f"Preflight validation failed: {exc}")
```

---

### 2.4 Pillar IV: Synthetic Test Oracle Engine for Greenfield Development

In brownfield codebases, existing tests provide the falsifier. In **greenfield development**, no tests exist. A naive agent writes code and immediately finishes because `pytest` finds 0 tests and exits 0.

#### The SOTA Synthetic Oracle Pattern:
Before any implementation file is written in a greenfield task, the agent MUST execute the **Oracle Synthesis Contract**:
1. **Contract Definition**: Define pure port protocols / interfaces.
2. **Oracle Synthesis**: Author a comprehensive test file (`test_feature.py`) specifying edge cases, failure paths, and expected outputs.
3. **Falsifier Confirmation**: Run the test suite against empty/stub implementations. **The test suite MUST FAIL with expected `NotImplementedError` or assertion mismatch.** If it passes on stubs, the test is vacuous and rejected.
4. **Implementation Phase**: Author implementation code until the synthetic oracle passes.
5. **Freeze Oracle**: Cryptographically freeze the test file hash so the agent cannot mutate the test during the implementation phase.

---

### 2.5 Pillar V: Resilient Model Dialect Adapter (`SelfHealingDialect`)

Modern harnesses must tolerate model non-determinism without crashing. The dialect adapter sits between raw LLM network responses and the kernel dispatch pipeline:

```
Raw Model Stream / Chunk
    |
    v
1. Strict JSON / Function Call Parser
    |---> Success -> Dispatch
    +---> Failure -> Fallback to Multi-Pattern Extractor
                        |---> Markdown Fenced JSON (```json ... ```)
                        |---> Embedded Action Blocks (<action>...</action>)
                        |---> Repaired Truncated JSON (json-repair)
                        |---> Clean Dispatch or Controlled Guidance Prompt
```

---

## 3. Concrete Module Implementation Specifications

Below are the exact file paths, class designs, and pseudocode implementations for developers to build these capabilities into Vanguard.

### 3.1 Module 1: `vanguard/packages/agency/episode/task_dag.py`
**Responsibility**: Manages the multi-step execution plan as a topological directed acyclic graph.

```python
"""Topological Task Step DAG for Complex Software Engineering Campaigns."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence, Set
import graphlib

class StepState(str, Enum):
    PENDING = "pending"
    READY = "ready"
    ACTIVE = "active"
    VERIFIED = "verified"
    FAILED = "failed"

@dataclass(frozen=True, slots=True)
class PlanStep:
    id: str
    objective: str
    target_paths: tuple[str, ...]
    dependencies: tuple[str, ...] = ()
    state: StepState = StepState.PENDING
    failure_log: str | None = None

class TaskExecutionGraph:
    def __init__(self, steps: Sequence[PlanStep]):
        self._steps: dict[str, PlanStep] = {s.id: s for s in steps}
        self._validate_acyclic()

    def _validate_acyclic(self) -> None:
        graph = {s.id: set(s.dependencies) for s in self._steps.values()}
        sorter = graphlib.TopologicalSorter(graph)
        sorter.prepare() # Raises CycleError if cyclic

    def get_executable_steps(self) -> tuple[PlanStep, ...]:
        """Returns all steps whose dependencies are strictly VERIFIED."""
        ready: list[PlanStep] = []
        for step in self._steps.values():
            if step.state != StepState.PENDING:
                continue
            deps_met = all(
                self._steps[d].state == StepState.VERIFIED 
                for d in step.dependencies
            )
            if deps_met:
                ready.append(step)
        return tuple(ready)

    def mark_step_verified(self, step_id: str, verification_hash: str) -> TaskExecutionGraph:
        updated = dict(self._steps)
        curr = updated[step_id]
        updated[step_id] = PlanStep(
            id=curr.id,
            objective=curr.objective,
            target_paths=curr.target_paths,
            dependencies=curr.dependencies,
            state=StepState.VERIFIED
        )
        return TaskExecutionGraph(tuple(updated.values()))
```

---

### 3.2 Module 2: `vanguard/packages/agency/context/blast_radius.py`
**Responsibility**: Computes downstream caller blast radius before code edits settle.

```python
"""Static AST and Dependency Blast Radius Calculator."""

from __future__ import annotations
import ast
from pathlib import Path
from typing import Set

class BlastRadiusAnalyzer:
    def __init__(self, workspace_root: Path):
        self._root = workspace_root

    def calculate_affected_symbols(self, target_file: Path, modified_source: str) -> Set[str]:
        """Identifies symbols whose signatures or presence changed in the diff."""
        original_symbols = self._extract_toplevel_signatures(target_file)
        new_ast = ast.parse(modified_source, filename=str(target_file))
        new_symbols = {
            node.name: ast.dump(node.args) 
            for node in ast.iter_child_nodes(new_ast) 
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        
        changed: Set[str] = set()
        for name, sig in original_symbols.items():
            if name not in new_symbols or new_symbols[name] != sig:
                changed.add(name)
        return changed

    def find_downstream_dependents(self, changed_symbols: Set[str]) -> tuple[Path, ...]:
        """Scans workspace imports for references to modified symbols using fast ripgrep."""
        # Integrates directly with tools/007_LLM_DOCS_ATLAS symbols index
        ...
```

---

### 3.3 Module 3: `vanguard/packages/runtime/governance/test_tamper_shield.py`
**Responsibility**: Enforces test suite read-only integrity during automated runs.

```python
"""Tamper-Proof Test Suite Isolation & Integrity Shield."""

from __future__ import annotations
import hashlib
from pathlib import Path
from vanguard.packages.domain.canonicalisation.digest import digest_of

class TestTamperShield:
    def __init__(self, workspace: Path, test_patterns: tuple[str, ...] = ("test/**", "tests/**", "*_test.py")):
        self._workspace = workspace
        self._patterns = test_patterns
        self._baseline_hashes: dict[str, str] = self._snapshot_test_hashes()

    def _snapshot_test_hashes(self) -> dict[str, str]:
        hashes: dict[str, str] = {}
        for p in self._workspace.rglob("test*.py"):
            hashes[str(p.relative_to(self._workspace))] = hashlib.sha256(p.read_bytes()).hexdigest()
        return hashes

    def verify_no_test_tampering(self) -> tuple[bool, str]:
        """Fails closed if the agent altered test files to manufacture a green exit."""
        for rel_path, original_hash in self._baseline_hashes.items():
            current_file = self._workspace / rel_path
            if not current_file.exists():
                return False, f"Test file deleted by agent: {rel_path}"
            current_hash = hashlib.sha256(current_file.read_bytes()).hexdigest()
            if current_hash != original_hash:
                return False, f"Test file tampered with by agent: {rel_path} (original {original_hash[:8]}, current {current_hash[:8]})"
        return True, "Test integrity verified"
```

---

## 4. Operational Guidelines: Complex Problem Workflows

### 4.1 Greenfield Campaign Workflow (Creating New Multi-File Subsystems)

```
[OPERATOR BRIEF: Create New Subsystem]
       |
       v
STAGE 1: ARCHITECTURAL DECOMPOSITION (Turn 1-2)
  - Inspect existing ports and domain types using `fs.search` / `lda_symbol`.
  - Author `TASK_PLAN.json` declaring step dependencies in topological order.
  - DO NOT write any implementation code in this stage.
       |
       v
STAGE 2: CONTRACT DEFINITION (Turn 3-5)
  - Create `domain/` pure types and `ports/` protocols.
  - Execute AST validation. Ensure stdlib-only boundary compliance.
       |
       v
STAGE 3: SYNTHETIC TEST ORACLE CREATION (Turn 6-8)
  - Author test suite under `test/contracts/` or `test/subsystem/`.
  - RUN TESTS: Verify tests FAIL with `NotImplementedError` or `ImportError`.
  - Freeze baseline test SHA-256 in `TestTamperShield`.
       |
       v
STAGE 4: TOPOLOGICAL IMPLEMENTATION (Turn 9-N)
  - Implement modules in dependency order using `AtomicMultiFileTransactionManager`.
  - Re-run synthetic tests after each step until green.
       |
       v
STAGE 5: VERIFICATION & ADMISSION (Terminal Turn)
  - Tamper shield confirms zero test mutations.
  - Exterior evaluator certifies pass. Emit `agency.finish`.
```

### 4.2 Brownfield Refactoring Campaign Workflow (Deep Complex Bugfixes)

```
[OPERATOR BRIEF: Bug Report / Refactor]
       |
       v
STAGE 1: MINIMAL REPRODUCTION (Turn 1-3)
  - Locate failing site via `fs.search` and symbol graph.
  - Execute existing test suite via `proc.exec`. Capture exact failure text.
  - If no regression test exists, write ONE reproduction test case.
       |
       v
STAGE 2: CAUSAL LOCALIZATION (Turn 4-6)
  - Formulate competing hypotheses. Record in `SemanticTaskState`.
  - Extract AST slices of candidate functions.
  - Identify blast radius: downstream consumers of target symbols.
       |
       v
STAGE 3: SURGICAL EDIT (Turn 7-9)
  - Apply smallest viable patch via `surgical_patch` / `patch.apply`.
  - Run reproduction test first.
       |
       v
STAGE 4: REGRESSION CLEARANCE (Turn 10-12)
  - Run full package regression suite.
  - If regression occurs: record falsified hypothesis in durable state.
  - DO NOT retry the identical patch. Pivot to next hypothesis.
       |
       v
STAGE 5: ADMISSION
  - Redundant verification detector prevents spinning.
  - Verify changed file tree hash against verification receipt.
  - Emit `agency.finish`.
```

---

## 5. Phased Engineering Roadmap: Waves 8 to 12

| Milestone | Target Capability | Primary Deliverables | Key Test Falsifiers |
|---|---|---|---|
| **Wave 8** | **Cognitive State Spine** | `task_dag.py`, `SemanticTaskState` persistence in SQLite WAL, checkpoint reducer. | `test_task_dag_topological_execution`, `test_state_restoration_across_sigkill` |
| **Wave 9** | **Progressive Context Engine** | AST symbol slicer, token-bounded tier compiler, LDA caller graph integration. | `test_context_stays_under_budget_at_turn_100`, `test_invariant_prefix_preserved` |
| **Wave 10** | **Atomic Multi-File 2PC** | `AtomicMultiFileTransactionManager`, preflight syntax and type linkage validator. | `test_multi_file_rollback_on_syntax_error`, `test_atomic_cross_file_rename` |
| **Wave 11** | **Synthetic Oracle & Anti-Tamper Shield** | `TestTamperShield`, synthetic test runner, read-only test filesystem mounting. | `test_rejection_of_tampered_test_assertions`, `test_synthetic_oracle_fail_closed` |
| **Wave 12** | **Full SOTA Benchmark Qualification** | 100-turn marathon agent evaluation, SWE-bench / HumanEval verification arm. | Real-world qualification runs using DeepSeek V4 Flash / Claude 3.5 Sonnet |

---

## 6. Verification Checklist for Developers

When implementing components from this treatise, contributors and autonomous agents MUST verify:
- [ ] Hexagonal boundary invariants are preserved (`domain <- ports <- kernel <- agency <- runtime -> adapters`).
- [ ] Kernel line-of-code budget does not exceed the $\le 1438$ threshold (`python3 tools/linters/check_tcb_budget.py`).
- [ ] No live Python objects cross serialization boundaries; all state contracts serialize via JCS canonical JSON.
- [ ] Subprocess executions utilize `sys.executable` and inherit controlled environment variables.
- [ ] Knowledge base is regenerated after touching packages (`python3 tools/generate_knowledge_base.py`).
- [ ] All automated tests pass hermetically without live network access (`npm test` and `python3 -m unittest discover`).
