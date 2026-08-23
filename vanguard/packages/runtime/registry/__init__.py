"""Canonical packages-side plugin lifecycle primitives (ADR-0081, M-3)."""

from .lifecycle import IllegalPluginTransition, PluginLifecycle, PluginState
from .validator import (
    ManifestValidationError,
    compatible,
    parse_semver,
    satisfies,
    validate_manifest,
    validate_plugin_manifest,
    validate_tool_schema,
)
from .broker import CellState, IllegalCellTransition, PluginCell, PluginIsolationBroker, RpcResponse
from .sandbox import SandboxLimits, apply_rlimits, open_log_sink
from .compiler import ComposeError, compose

__all__ = [
    "IllegalPluginTransition",
    "PluginLifecycle",
    "PluginState",
    "ManifestValidationError",
    "compatible",
    "parse_semver",
    "satisfies",
    "validate_manifest",
    "validate_plugin_manifest",
    "validate_tool_schema",
    "CellState",
    "IllegalCellTransition",
    "PluginCell",
    "PluginIsolationBroker",
    "RpcResponse",
    "SandboxLimits",
    "apply_rlimits",
    "open_log_sink",
    "ComposeError",
    "compose",
]
