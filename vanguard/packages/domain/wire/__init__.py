"""Versioned wire-contract readers. External values acquire types by parsing."""

from .contracts import WIRE_KINDS, WireError, parse_wire

__all__ = ["WIRE_KINDS", "WireError", "parse_wire"]
