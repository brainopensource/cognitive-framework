---
id: ref.artifacts
canonical_id: ref.artifacts
class: reference
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: stores-artifacts
canonical_for:
  - blob addressing/get/put
  - artifact references
  - memory categories/actions
  - backup/restore/GC operations
purpose: Own content-addressed artifact and memory storage interfaces/lifecycle operations.
audience:
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-031
  - E-B-037
  - E-B-038
  - E-B-051
relationships:
  - arch.state.causal
  - arch.memory.learning
  - ref.ports
reviewer: documentation-specialist
confidence: high
---

# Artifact Storage & Memory Reference

## Purpose
This document is the canonical reference owner for content-addressed blob storage (CAS) interfaces, artifact reference descriptors, memory categorization, scoped memory query operations, and garbage collection / lifecycle maintenance.

## Scope
- Content-addressed blob store protocol (`BlobStorePort`) and filesystem layout.
- `ArtifactRef` wire representations and integrity verification.
- Memory categories (`episodic`, `semantic`, `procedural`, `working`).
- Memory query parameters and capability authorization checks (`INV-B-010`).
- Storage lifecycle operations: backup, restore, pruning, and compaction.

## Non-responsibilities
- High-level causal state architecture and checkpointing (owned by [`arch.state.causal`](../architecture/causal-state.md)).
- Governed learning and memory promotion policies (owned by [`arch.memory.learning`](../architecture/memory-learning.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Content-addressed artifact storage and SQLite-backed memory engines are fully implemented in `vanguard.packages.adapters.stores`.

---

## 1. Content-Addressed Blob Storage (`BlobStorePort`)

The blob store provides immutable, content-addressed storage for large payloads, outputs, and diffs:

```python
class BlobStorePort(Protocol):
    def put(self, data: bytes) -> str: ...
    def get(self, digest: str) -> bytes: ...
    def has(self, digest: str) -> bool: ...
```

### Storage Addressing Scheme
- **Digest Algorithm**: SHA-256 computed across raw bytes.
- **Filesystem Tree Layout**: Two-level fan-out prefixing:
  ```text
  .vanguard/blobs/sha256/
  └── 3f/
      └── 7a/
          └── 3f7a1b92c4e5... (full 64-hex SHA-256 digest)
  ```

---

## 2. Artifact Reference Descriptors (`ArtifactRef`)

Events and receipts refer to large data through immutable `ArtifactRef` values:

```json
{
  "digest": "3f7a1b92c4e5d68019a84b3c990a12e3456789abcdef0123456789abcdef0123",
  "size_bytes": 1048576,
  "mime_type": "text/markdown",
  "name": "analysis_report.md",
  "created_at": "2026-08-29T20:15:00Z"
}
```

---

## 3. Memory Categories & Storage Model

Memory records (`MemoryRecord`) are classified into distinct categories:

| Category | Typical Lifetime | Access Pattern | Description |
|---|---|---|---|
| `working` | Single turn / Episode | In-memory / scratch | Ephemeral scratchpad data during active turn cognition. |
| `episodic` | Multi-episode / Run | Vector / semantic search | Past turn trajectories, observations, and tool outcomes. |
| `semantic` | Persistent / Workspace | Indexed retrieval | Extracted facts, documentation fragments, code symbols. |
| `procedural` | Governed / Promoted | Exact rule matching | Verified operational recipes and policies. |

---

## 4. Scoped Authorization for Memory Retrieval (`INV-B-010`)

Memory engines require an active `CapabilityGrant` scope before executing queries or returning dereferenced content:
- **`MemoryQuery`**: Specifies `query_text`, `categories`, `limit`, `min_score`, and `capability_grant`.
- Unscoped queries or grants lacking `memory:read` permissions are rejected with `PermissionDenied`.

---

## 5. Lifecycle, Pruning & Garbage Collection

| Operation | Method / Command | Description |
|---|---|---|
| `prune` | `IMemoryEngine.prune(criteria)` | Removes expired or low-utility memory records below retention score. |
| `consolidate`| `IMemoryEngine.consolidate(hits)` | Merges similar episodic records into consolidated semantic summaries. |
| `gc_blobs` | `FilesystemBlobStore.gc(active_digests)` | Scans event ledgers and removes unreferenced blob files from disk. |

---

## Implementation Evidence

- **Port Protocols**: `vanguard/packages/ports/blob_store.py`, `vanguard/packages/ports/memory.py`.
- **Blob Store Adapter**: `vanguard/packages/adapters/stores/blob_store.py` (`FilesystemBlobStore`, `InMemoryBlobStore`).
- **Memory Engine Adapter**: `vanguard/packages/adapters/stores/memory_engine.py` (`SqliteMemoryEngine`).
- **Tests**: `test/runtime/test_blob_and_index_ports.py`, `test/adapters/test_durable_memory_port.py`, `test/security/test_m8_memory_fake_parity.py`.
