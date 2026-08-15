"""Vanguard Ledger Module — Event Store, State Ledger & Replay.

Owning contract: VG-04 §12, GTS-13C T3.1–T3.8, ICD §4.

Provides:
- Append-only transactional event stores: `InMemoryEventStore`, `SqliteEventStore` (T3.1).
- Rebuildable state projections: `RunSummaryProjection`, `BudgetProjection`, `AuditProjection`, `ArtifactRegistryProjection` (T3.4).
- JSONL export with redaction preserving correlation: `export_jsonl`, `import_jsonl`, `redact_envelope` (T3.5).
- External recovery scanner and lease watcher: `RecoveryScanner` (T3.6).
- Idempotent effect reconciler: `EffectReconciler` (T3.7).
- Model cassette recorder & player: `CassetteRecorder`, `CassettePlayer` (T3.8).
"""

from .cassette import (
    Cassette,
    CassettePlayer,
    CassetteRecord,
    CassetteRecorder,
)
from .export import (
    RedactionPolicy,
    export_jsonl,
    import_jsonl,
    redact_envelope,
)
from .projections import (
    ArtifactRegistryProjection,
    AuditProjection,
    BudgetProjection,
    Projection,
    RunSummaryProjection,
    rebuild_projection,
)
from .reconciliation import (
    EffectReconciler,
    ReconciliationVerdict,
)
from .recovery import (
    RecoveryRecord,
    RecoveryScanner,
)
from .store import (
    InMemoryEventStore,
    SqliteEventStore,
)

__all__ = [
    "InMemoryEventStore",
    "SqliteEventStore",
    "Projection",
    "RunSummaryProjection",
    "BudgetProjection",
    "AuditProjection",
    "ArtifactRegistryProjection",
    "rebuild_projection",
    "RedactionPolicy",
    "redact_envelope",
    "export_jsonl",
    "import_jsonl",
    "RecoveryScanner",
    "RecoveryRecord",
    "EffectReconciler",
    "ReconciliationVerdict",
    "CassetteRecord",
    "Cassette",
    "CassetteRecorder",
    "CassettePlayer",
]
