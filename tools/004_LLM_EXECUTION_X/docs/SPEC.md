# Technical Specification (SPEC) — LEX Engine v1.0 (Normative)

> **Document Class:** Normative Technical Law (RFC-2119)  
> **Target Subsystem:** `tools/004_LLM_EXECUTION_X/`  
> **Version:** `1.0.0-normative`  
> **Status:** Binding Law for Implementation  
> **Authors:** AI Agentic Architecture Group (Principal Systems Architect)  

---

## 1. Scope & Conformance (RFC-2119)

The keywords **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in RFC-2119.

An implementation conforms to the LEX Specification if and only if it satisfies all **MUST** and **SHALL** requirements defined in Sections 2 through 7.

---

## 2. Normative Data Contracts & Wire Schemas

### 2.1. The `TaskGraph IR` Schema
The Architect model MUST output a structured JSON payload conforming to the `TaskGraph IR` schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["project_id", "docstring", "risk_class", "tasks"],
  "properties": {
    "project_id": {"type": "string"},
    "docstring": {"type": "string"},
    "risk_class": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]},
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "artifact_target", "test_target", "dependencies", "interface_contracts", "invariants", "acceptance_criteria", "verification_requirements"],
        "properties": {
          "id": {"type": "string"},
          "artifact_target": {"type": "string"},
          "test_target": {"type": "string"},
          "dependencies": {"type": "array", "items": {"type": "string"}},
          "interface_contracts": {"type": "array", "items": {"type": "string"}},
          "invariants": {"type": "array", "items": {"type": "string"}},
          "acceptance_criteria": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "description", "severity", "oracle_type"],
              "properties": {
                "id": {"type": "string"},
                "description": {"type": "string"},
                "severity": {"type": "string", "enum": ["CRITICAL", "HIGH", "NORMAL", "LOW"]},
                "oracle_type": {"type": "string", "enum": ["EXCEPTION_RAISED", "BOOLEAN_EXACT", "EQUALITY", "NUMERICAL_DELTA"]}
              }
            }
          },
          "verification_requirements": {
            "type": "object",
            "required": ["min_mutation_score", "require_ast_assertion_density", "sandbox_tier_required"],
            "properties": {
              "min_mutation_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
              "require_ast_assertion_density": {"type": "number", "minimum": 1.0},
              "sandbox_tier_required": {"type": "string", "enum": ["TIER_A_BUBBLEWRAP", "TIER_B_USER_NS", "RESTRICTED_EXECUTION"]}
            }
          }
        }
      }
    }
  }
}
```

### 2.2. Prompt Decoupling Rule
Prompt strings (`coder_prompt`, `tester_prompt`) **MUST NOT** be embedded within the `TaskGraph IR` contract. All prompt strings **MUST** be generated just-in-time by a `PromptCompiler<Profile>` implementation consuming the semantic `TaskNode`.

---

## 3. Evidence & Verification Authority

### 3.1. Evidence Producer Protocol
Validation stages and linters **MUST NOT** emit boolean verdicts (`PASS`/`FAIL`). All validation stages **MUST** implement the `IEvidenceCollector` interface and return an immutable `Evidence` value object:

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Evidence {
    pub kind: EvidenceKind,              // AstSyntax, RuffLint, Pytest, MutationProbe, SecurityAudit
    pub collector_id: String,
    pub timestamp: DateTime<Utc>,
    pub metrics: HashMap<String, serde_json::Value>,
    pub artifacts_evaluated: Vec<String>,
    pub raw_output_digest: String,      // SHA-256 of raw stdout/stderr
}
```

### 3.2. Verification Authority & Policy
The `VerificationPolicy` is the **sole authority** permitted to issue a binding `Verdict`. A `Verdict` of `VERIFIED_DELIVERABLE` **SHALL ONLY** be granted if:
1. `EvidenceKind.AST`: `syntax_valid == True` AND `unwhitelisted_imports == []`.
2. `EvidenceKind.RUFF`: `violation_count == 0`.
3. `EvidenceKind.PYTEST`: `tests_failed == 0` AND `tests_passed >= len(task.acceptance_criteria)`.
4. `EvidenceKind.MUTATION`: `mutation_score >= task.verification_requirements.min_mutation_score`.

---

## 4. Mathematical Invariants & Anti-Thrashing

### 4.1. Mutation Score Formula
The mutation score **MUST** be computed as:
$$\text{MutationScore} = \frac{\text{Killed Mutants}}{\text{Valid Non-Equivalent Mutants Generated}}$$
Where a mutant is considered *killed* if the test suite exits with non-zero exit code on the mutated AST.

### 4.2. State Hash & Circuit Breaker Invariant
The engine **MUST** compute state hashes at each iteration $n$:
$$\text{RepairStateHash}_n = \text{SHA256}(\text{ArtifactHashes} \parallel \text{FailingClaimSet} \parallel \text{DiagnosticFingerprint})$$

If $\text{RepairStateHash}_n == \text{RepairStateHash}_{n-2}$, the engine **MUST** immediately trip the circuit breaker and transition to `REPLAN_ESCALATION` or `FAIL_CLOSED_ABORT`.

---

## 5. Security & Rootless Sandbox Invariants

1. **Zero In-Process Untrusted Execution:** Untrusted code generated by an LLM **MUST NEVER** be executed in-process within the orchestrator runtime (via `exec()`, `eval()`, or in-process `pytest.main()`).
2. **Fail-Closed Fallback:** If neither Bubblewrap (`bwrap`) nor User Namespaces (`unshare -U -n -r`) are available on the host, the sandbox adapter **MUST** enter `Tier C: Static Analysis Only` and raise `SandboxUnavailableError` for dynamic execution requests.
3. **No `preexec_fn` in Threaded Runtimes:** Subprocess execution **MUST NOT** use Python's `preexec_fn` parameter due to thread deadlock risks. Resource boundaries **MUST** be configured via launcher processes or wrapper arguments.
4. **Guaranteed Ephemeral Cleanup:** All temporary sandbox directories **MUST** use UUID suffixes (`/tmp/lex_sandbox_<uuid>`) and **MUST** be registered with `atexit` finalizers to guarantee disk purge on abnormal termination.

---

## 6. Hardware VRAM Lifecycle & Active Polling Protocol

1. **Active Drain Confirmation:** Before dispatching Level 3 Worker models, the model adapter **MUST** issue an unload command (`POST /api/generate` with `keep_alive: 0`) for the Level 2 Architect model and actively poll `GET /api/ps` until `size_vram == 0` is confirmed.
2. **Worker Concurrency Limit:** The local inference runtime **MUST** be configured with `OLLAMA_NUM_PARALLEL=2` to allow simultaneous evaluation of Coder and Tester slots without context eviction.

---

## 7. Error Taxonomy & Codes

| Error Class | Exit Code | Trigger Condition |
|:---|:---:|:---|
| `ContractValidationError` | `10` | JSON schema validation failure on `TaskGraph IR` or envelopes. |
| `CollusiveTestError` | `11` | Tests contain 0 assertions or fail the mutation sanity probe. |
| `HealingExhaustedError` | `20` | Max healing retry budget exceeded without PASS verdict. |
| `CircuitBreakerError` | `21` | State hash oscillation or non-progress stagnation detected. |
| `SandboxTimeoutError` | `30` | Execution exceeded wall-clock limit (10s). |
| `SandboxOOMError` | `31` | Subprocess exceeded memory ulimit (256MB) / SIGKILL. |
| `SandboxUnavailableError` | `32` | No Tier A or Tier B rootless sandbox available on host. |
| `ToolNotInstalledError` | `40` | Missing required host binary (`ruff`, `pytest`, `ollama`). |
| `OllamaConnectionError` | `50` | Local Ollama daemon unreachable at configured endpoint. |
