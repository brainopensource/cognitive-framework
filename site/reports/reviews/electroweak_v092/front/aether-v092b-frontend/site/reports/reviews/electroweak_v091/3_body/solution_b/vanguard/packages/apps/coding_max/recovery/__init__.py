"""Failure classification and adaptive recovery (`spec §25`–`§27`)."""

from __future__ import annotations

from .failures import FailureClass, FailureClassifier, FailureVerdict, TrajectorySignals
from .policy import RecoveryAction, RecoveryDecision, RecoveryPolicy, RetryBudget

__all__ = ["FailureClass", "FailureClassifier", "FailureVerdict", "RecoveryAction",
           "RecoveryDecision", "RecoveryPolicy", "RetryBudget", "TrajectorySignals"]
