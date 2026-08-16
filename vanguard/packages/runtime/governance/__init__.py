"""Declared, model-free governance processes."""

from .approvals import (
    ApprovalAuthority,
    ApprovalAuthorization,
    ApprovalChallenge,
    ApprovalDecision,
    ApprovalFlow,
    ApprovalFormatError,
    DescriptorBoundApprovalPolicy,
    normalise_unified_diff,
)
from .engine import ProcessEngine, ProcessError
from .definitions import ProcessDefinition, ProcessHistory, ProcessInstance, Transition

__all__ = [
    "ApprovalAuthority",
    "ApprovalAuthorization",
    "ApprovalChallenge",
    "ApprovalDecision",
    "ApprovalFlow",
    "ApprovalFormatError",
    "DescriptorBoundApprovalPolicy",
    "ProcessDefinition",
    "ProcessEngine",
    "ProcessError",
    "ProcessHistory",
    "ProcessInstance",
    "Transition",
    "normalise_unified_diff",
]
