"""Plugin lifecycle FSM with ledgered transitions. Isolation broker is a stub at M1."""

from __future__ import annotations

from enum import Enum

from layer0.events.emitter import LedgerEmitter
from layer0.spi.types_gen import EventKind

__all__ = ["PluginLifecycle", "PluginState"]


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
    PluginState.RETIRED: set(),
    PluginState.FAULTED: {PluginState.RETIRED},
}

_EVENT = {
    PluginState.RESOLVED: EventKind.PLUGIN_RESOLVED,
    PluginState.ACTIVATED: EventKind.PLUGIN_ACTIVATED,
    PluginState.QUIESCING: EventKind.PLUGIN_QUIESCED,
    PluginState.RETIRED: EventKind.PLUGIN_RETIRED,
    PluginState.FAULTED: EventKind.PLUGIN_FAULTED,
}


class PluginLifecycle:
    """DISCOVERED → RESOLVED → VERIFIED → ACTIVATED → QUIESCING → RETIRED."""

    def __init__(self, plugin_id: str, emitter: LedgerEmitter, *, run_id: str, principal: str) -> None:
        self.plugin_id = plugin_id
        self.state = PluginState.DISCOVERED
        self._emitter = emitter
        self._run_id = run_id
        self._principal = principal

    def resolve(self) -> None:
        self._go(PluginState.RESOLVED)

    def verify(self) -> None:
        self._go(PluginState.VERIFIED)

    def activate(self) -> None:
        self._go(PluginState.ACTIVATED)

    def quiesce(self) -> None:
        self._go(PluginState.QUIESCING)

    def retire(self) -> None:
        self._go(PluginState.RETIRED)

    def fault(self, reason: str) -> None:
        self._go(PluginState.FAULTED, extra={"reason": reason})

    def _go(self, target: PluginState, extra: dict[str, str] | None = None) -> None:
        allowed = _TRANSITIONS[self.state]
        if target not in allowed:
            raise ValueError(f"illegal transition {self.state.value} → {target.value}")
        self.state = target
        kind = _EVENT.get(target)
        if kind is not None:
            payload = {"plugin_id": self.plugin_id}
            if extra:
                payload.update(extra)
            self._emitter.emit_kind(
                kind,
                run_id=self._run_id,
                principal=self._principal,
                payload=payload,
            )
