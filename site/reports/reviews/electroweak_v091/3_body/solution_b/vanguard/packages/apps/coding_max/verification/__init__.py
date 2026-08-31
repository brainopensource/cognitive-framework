"""Layered verification (`spec §23`, `§24`)."""

from __future__ import annotations

from .pipeline import (
    CheckResult, Layer, VerificationPipeline, VerificationResult,
    VerificationScope, select_layers,
)

__all__ = ["CheckResult", "Layer", "VerificationPipeline", "VerificationResult",
           "VerificationScope", "select_layers"]
