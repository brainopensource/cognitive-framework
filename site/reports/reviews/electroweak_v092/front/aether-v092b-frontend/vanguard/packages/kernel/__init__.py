"""The Trusted Computing Base: grants, attenuation, policy, budgets, dispatch
and provenance (`system-architecture-icd.md` §2).

Every effect passes through `Kernel.dispatch` and there is no second path
(`05 §2.1`, `AT-01`). May import `domain` and `ports` only.
"""

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
    EffectRequest,
    Event,
    FailurePath,
    Occurrence,
    SinkClass,
    Span,
    Trust,
)
from .policy import Decision, Mode, Outcome, StandardPolicy
from .provenance import Accumulation, authority_violation, combine, weakest

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
