"""Canonical packages-side plugin lifecycle primitives (ADR-0081, M-3)."""

from .lifecycle import IllegalPluginTransition, PluginLifecycle, PluginState

__all__ = ["IllegalPluginTransition", "PluginLifecycle", "PluginState"]
