I'll address each task systematically with professional rigor.

# 1. CRITICAL CODE REVIEW

## Security Invariants Analysis

### dispatch.py (Kernel Attenuation)
- **K-04/K-05 Compliance**: Verified - lease acquisition (S7) occurs after action resolution (S2) and grant verification (S8) is properly scoped
- **Durability Invariant (K-47)**: Correctly implements write-ahead logging with S8a before S9
- **Resource Leak Prevention**: S11 before S12 ensures lease cleanup
- **Vulnerability**: Missing explicit validation of `widensCapability` classifier output (S4) could allow privilege escalation if classifier is compromised

### evaluation_listener.py
- **Event Deduplication**: `_processed_event_ids` set prevents replay attacks
- **Vulnerability**: No cryptographic validation of envelope integrity before processing
- **Race Condition**: Non-atomic check-then-act sequence in `process_envelope`
- **TCB Concern**: Callback mechanism could be abused for RCE if evaluator is compromised

### autonomous_grant.py
- **Boundary Enforcement**: Strict allowlisting of verbs/commands
- **Vulnerability**: Missing runtime path canonicalization could allow directory traversal
- **Integrity Gap**: No timestamp freshness validation in grant verification

## Type System Findings
- `EvaluationRequestPayload` needs Protocol Literal types
- `AutonomousGrant` should use `NewType` for signature fields
- Missing `Final` declarations for default constants

## TCB Compliance
- Total Logical LOC: 387 (well under 1438 limit)
- Kernel boundary crossings are properly gated
- Event listener maintains adequate isolation

# 2. v0.6.0 SPRINT PLAN

## Parallel Development Lanes

### ALFA Lane (Structured Artifact Graph)
```
1. Core Schema (Week 1-2)
   - Define ArtifactNode/Edge protobufs
   - Implement Merkle-DAG builder
   
2. Graph Service (Week 3-4)
   - gRPC service definition
   - In-memory reference implementation

3. Integration (Week 5-6)
   - Kernel dispatch hooks
   - Ephemeral→Durable transition
```

### BETA Lane (Semantic Vector Index)
```
1. Embedding Pipeline (Week 1-3)
   - Protocol for text→vector
   - Batch processing service

2. Index Core (Week 4-5)
   - HNSW implementation
   - Hybrid query planner

3. Operationalization (Week 6)
   - Continuous indexing
   - Kernel policy integration
```

### GAMMA Lane (SQLite WAL Event Store)
```
1. WAL Core (Week 1-2)
   - Write-optimized append
   - Cursor management

2. Query Layer (Week 3-4)
   - Range scans
   - Indexed lookups

3. Durability (Week 5-6)
   - fsync discipline
   - Crash recovery
```

# 3. SQLite WAL IMPLEMENTATION

## Core Pseudocode

```python
class SQLiteEventStore(EventStorePort):
    def __init__(self, path: Path):
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            seq INTEGER NOT NULL,
            payload BLOB NOT NULL,
            -- Additional metadata columns
            CHECK(json_valid(payload))
        ) STRICT;
        """)
        
    def append(self, envelopes: list[EventEnvelope]) -> Result[None]:
        with self.conn:
            cursor = self.conn.cursor()
            for env in envelopes:
                cursor.execute(
                    "INSERT INTO events VALUES (?, ?, ?)",
                    (env.event_id, env.seq, json.dumps(env.payload))
                )
            self.conn.commit()
```

## Vector Index AST

```typescript
interface VectorIndex {
  // Insertion
  insert(id: string, vector: Float32Array): Promise<void>;
  
  // Query
  knnSearch(
    query: Float32Array, 
    k: number,
    filter?: (id: string) => boolean
  ): Promise<Array<{id: string, score: number}>>;

  // Persistence
  snapshot(path: string): Promise<void>;
  restore(path: string): Promise<void>;
}

interface HybridQueryPlan {
  vectorQuery: VectorQuery;
  sqlFilter: string;
  joinStrategy: 'pre' | 'post' | 'pipeline';
}
```

The implementation maintains WAL's durability guarantees while enabling high-throughput event ingestion and vector-indexed retrieval through a hybrid query planner.