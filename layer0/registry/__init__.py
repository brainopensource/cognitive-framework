"""Plugin registry: lifecycle FSM, isolation broker, capability ceilings."""

from .broker import CellState, IllegalCellTransition, PluginIsolationBroker
from .grants import CeilingViolation, intersect_ceilings
from .isolation import IsolationBroker, IsolationTier
from .lifecycle import PluginLifecycle, PluginState
from .sandbox import SandboxLimits
from .validator import ManifestValidationError, validate_manifest

__all__ = [
    "CellState",
    "CeilingViolation",
    "IllegalCellTransition",
    "IsolationBroker",
    "IsolationTier",
    "ManifestValidationError",
    "PluginIsolationBroker",
    "PluginLifecycle",
    "PluginState",
    "SandboxLimits",
    "intersect_ceilings",
    "validate_manifest",
]
