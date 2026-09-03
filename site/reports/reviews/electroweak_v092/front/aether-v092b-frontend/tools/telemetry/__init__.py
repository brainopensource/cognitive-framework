"""Runtime Telemetry Suite & Latency Benchmark Runner.

Owning contract: REQ-BENCH-001, VG-07 §5.6, §5.8.
"""

from .collector import TelemetryCollector
from .metrics import (
    EffectOverheadSummary,
    LatencySummary,
    TelemetryReport,
    TokenCostSummary,
    calculate_percentiles,
)
from .runner import (
    BenchmarkRunResult,
    BenchmarkTask,
    LatencyBenchmarkRunner,
    PairedComparisonResult,
)
from .tuple import (
    CompatibilityKey,
    InstrumentTuple,
    ObservationMetadata,
    StratificationFields,
    TreatmentDimensions,
)

__all__ = [
    "calculate_percentiles",
    "LatencySummary",
    "EffectOverheadSummary",
    "TokenCostSummary",
    "TelemetryReport",
    "CompatibilityKey",
    "TreatmentDimensions",
    "StratificationFields",
    "ObservationMetadata",
    "InstrumentTuple",
    "TelemetryCollector",
    "BenchmarkTask",
    "BenchmarkRunResult",
    "PairedComparisonResult",
    "LatencyBenchmarkRunner",
]
