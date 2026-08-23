"""Fail-closed plugin lifecycle state machine for the canonical runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any


class IllegalPluginTransition(ValueError):
    """Raised when a plugin attempts a transition not allowed by ADR-0081."""


class PluginState(str, Enum):
    DISCOVERED = "discovered"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    ACTIVATED = "activated"
    QUIESCING = "quiescing"
    RETIRED = "retired"
    FAULTED = "faulted"


_TRANSITIONS = {
    PluginState.DISCOVERED: {PluginState.RESOLVED, PluginState.FAULTED},
    PluginState.RESOLVED: {PluginState.VERIFIED, PluginState.FAULTED},
    PluginState.VERIFIED: {PluginState.ACTIVATED, PluginState.FAULTED},
    PluginState.ACTIVATED: {PluginState.QUIESCING, PluginState.FAULTED},
    PluginState.QUIESCING: {PluginState.RETIRED, PluginState.FAULTED},
    PluginState.FAULTED: {PluginState.RETIRED},
    PluginState.RETIRED: set(),
}

_EVENTS = {
    PluginState.DISCOVERED: "PluginDiscovered",
    PluginState.RESOLVED: "PluginResolved",
    PluginState.VERIFIED: "PluginVerified",
    PluginState.ACTIVATED: "PluginActivated",
    PluginState.QUIESCING: "PluginQuiesced",
    PluginState.RETIRED: "PluginRetired",
    PluginState.FAULTED: "PluginFaulted",
}


class PluginLifecycle:
    """Emit exactly one registry-owned event for every entered state."""

    def __init__(self, plugin_id: str, emitter: Any, *, run_id: str, principal: str,
                 manifest_digest: str | None = None) -> None:
        if not plugin_id:
            raise ValueError("plugin_id is required")
        if not manifest_digest:
            raise ValueError("manifest_digest is required")
        self.plugin_id = plugin_id
        self.state = PluginState.DISCOVERED
        self._emitter = emitter
        self._run_id = run_id
        self._principal = principal
        self._manifest_digest = manifest_digest
        self._emit(PluginState.DISCOVERED)

    def resolve(self) -> None:
        self._go(PluginState.RESOLVED)

    def verify(self, *, graph_digest: str | None = None,
               ceiling_digest: str | None = None) -> None:
        if not graph_digest:
            raise ValueError("graph_digest is required at verification")
        if not ceiling_digest:
            raise ValueError("ceiling_digest is required at verification")
        self._go(PluginState.VERIFIED, graph_digest=graph_digest,
                 ceiling_digest=ceiling_digest)

    def activate(self) -> None:
        self._go(PluginState.ACTIVATED)

    def quiesce(self) -> None:
        self._go(PluginState.QUIESCING)

    def retire(self) -> None:
        self._go(PluginState.RETIRED)

    def fault(self, reason: str) -> None:
        if not reason:
            raise ValueError("fault reason is required")
        self._go(PluginState.FAULTED, reason=reason)

    def _go(self, target: PluginState, **extra: str | None) -> None:
        if target not in _TRANSITIONS[self.state]:
            raise IllegalPluginTransition(
                f"illegal transition {self.state.value} -> {target.value}"
            )
        self.state = target
        self._emit(target, **extra)

    def _emit(self, state: PluginState, **extra: str | None) -> None:
        payload: dict[str, str] = {"plugin_id": self.plugin_id, **{
            key: value for key, value in extra.items() if value is not None
        }}
        if self._manifest_digest:
            payload["manifest_digest"] = self._manifest_digest
        self._emitter.emit_kind(
            _EVENTS[state], run_id=self._run_id, principal=self._principal, payload=payload,
            writer="registry",
        )
