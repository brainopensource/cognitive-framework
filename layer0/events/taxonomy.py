"""Normative event kind set and the single production emitter per kind (SPEC §1.2)."""

from __future__ import annotations

from layer0.spi.types_gen import EventKind

__all__ = ["EMITTER_SITES", "EVENT_KINDS"]

EVENT_KINDS: frozenset[str] = frozenset(kind.value for kind in EventKind)

# Package prefix that MUST contain a reachable string literal for the kind.
EMITTER_SITES: dict[str, str] = {
    "RunStarted": "layer0/scheduler",
    "EpisodeStarted": "layer0/scheduler",
    "TurnStarted": "layer0/scheduler",
    "EpisodeCompleted": "layer0/scheduler",
    "RunCompleted": "layer0/scheduler",
    "RunAborted": "layer0/scheduler",
    "RunRecovered": "layer0/scheduler",
    "ProposalProduced": "layer0/scheduler",
    "ProposalRejected": "layer0/scheduler",
    "ReflectionProduced": "layer0/scheduler",
    "AuthorizationRequested": "layer0/kernel",
    "AuthorizationDenied": "layer0/kernel",
    "CapabilityGranted": "layer0/kernel",
    "CapabilityAttenuated": "layer0/kernel",
    "CapabilityRevoked": "layer0/kernel",
    "BudgetReserved": "layer0/kernel",
    "BudgetCommitted": "layer0/kernel",
    "BudgetReleased": "layer0/kernel",
    "BudgetExhausted": "layer0/kernel",
    "EffectStarted": "layer0/kernel",
    "EffectCompleted": "layer0/kernel",
    "EffectFailed": "layer0/kernel",
    "EffectRejected": "layer0/kernel",
    "EffectReconciled": "layer0/kernel",
    "EvaluationRequested": "layer0/scheduler",
    "VerdictRecorded": "layer0/scheduler",
    "ClaimRecorded": "layer0/scheduler",
    "InvalidationChecked": "layer0/scheduler",
    "ApprovalRequested": "layer0/kernel",
    "ApprovalResolved": "layer0/kernel",
    "KernelAlarm": "layer0/kernel",
    "PluginResolved": "layer0/registry",
    "PluginActivated": "layer0/registry",
    "PluginQuiesced": "layer0/registry",
    "PluginRetired": "layer0/registry",
    "PluginFaulted": "layer0/registry",
    "Heartbeat": "layer0/scheduler",
    "CheckpointCreated": "layer0/scheduler",
    "ChildSpawned": "layer0/scheduler",
    "ChildReturned": "layer0/scheduler",
}
