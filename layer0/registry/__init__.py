"""Plugin registry: lifecycle FSM, isolation broker, capability ceilings."""

from .grants import CeilingViolation, intersect_ceilings
from .isolation import IsolationBroker, IsolationTier
from .lifecycle import PluginLifecycle, PluginState

__all__ = [
    "CeilingViolation",
    "IsolationBroker",
    "IsolationTier",
    "PluginLifecycle",
    "PluginState",
    "intersect_ceilings",
]
