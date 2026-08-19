"""Layer-0 attenuation kernel (verbatim S0–S12 port, retargeted to types_gen)."""

from .attenuation import AttenuationDenied, AttenuationResult, Constraints, Scope, attenuate
from .budget import BudgetDenied, Governor, Lease, LeaseState, Reservation
from .classifier import HeldAuthority, SinkMismatch, SinkRegistry, StandardClassifier
from .dispatch import DispatchResult, Kernel, KernelAlarm, SuspensionToken
from .grants import (
    Grant,
    GrantIssuer,
    GrantVerification,
    HmacAuthenticator,
    MissingDescriptorBinding,
    descriptor_of,
)
from .model import (
    ALERTABLE,
    AdapterOutcome,
    Event,
    FailurePath,
    Occurrence,
    Span,
    Trust,
)
from .policy import Decision, Mode, Outcome, StandardPolicy
from .provenance import Accumulation, authority_violation, combine, weakest
from layer0.spi.types_gen import EffectRequest, SinkClass

__all__ = [
    "ALERTABLE", "Accumulation", "AdapterOutcome", "AttenuationDenied",
    "AttenuationResult", "BudgetDenied", "Constraints", "Decision",
    "DispatchResult", "EffectRequest", "Event", "FailurePath", "Governor",
    "Grant", "GrantIssuer", "GrantVerification", "HeldAuthority",
    "HmacAuthenticator", "Kernel", "KernelAlarm", "Lease", "LeaseState",
    "MissingDescriptorBinding", "Mode", "Occurrence", "Outcome", "Reservation",
    "Scope", "SinkClass", "SinkMismatch", "SinkRegistry", "Span",
    "StandardClassifier", "StandardPolicy", "SuspensionToken", "Trust",
    "attenuate", "authority_violation", "combine", "descriptor_of", "weakest",
]
