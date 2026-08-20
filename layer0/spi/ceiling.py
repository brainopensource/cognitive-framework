"""Absorb shim until 2.2-B. Canonical implementation is adapters.sandbox.ceiling.

Must not contain a second selector algebra (`_selector_subset` is gone — F-16).
"""

from __future__ import annotations

from vanguard.packages.adapters.sandbox.ceiling import ceiling_allows

__all__ = ["ceiling_allows"]
