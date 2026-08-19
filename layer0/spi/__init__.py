"""Layer-0 SPI package: generated types + frozen protocols."""

from .interfaces import (
    IContextManager,
    IEvaluationGate,
    IMemoryEngine,
    IPlanner,
    IToolkit,
)
from .result import Err, Ok, Result
from .types_gen import EffectRequest, Proposal, Receipt, Reservation

__all__ = [
    "EffectRequest",
    "Err",
    "IContextManager",
    "IEvaluationGate",
    "IMemoryEngine",
    "IPlanner",
    "IToolkit",
    "Ok",
    "Proposal",
    "Receipt",
    "Reservation",
    "Result",
]
