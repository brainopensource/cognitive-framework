"""Declared, model-free governance processes."""

from .approvals import (
    ApprovalAuthority,
    ApprovalAuthorization,
    ApprovalChallenge,
    ApprovalDecision,
    ApprovalFlow,
    ApprovalFormatError,
    DescriptorBoundApprovalPolicy,
    OperatorSigner,
    normalise_unified_diff,
)
from .engine import ProcessEngine, ProcessError
from .definitions import ProcessDefinition, ProcessHistory, ProcessInstance, Transition
from .learning import (
    CompositionCandidate,
    DurableCompositionRegistry,
    EvaluationReport,
    EvaluatorProtocol,
    GeneratorProtocol,
    NotAvailableError,
    PromoterProtocol,
    PromotionEvidence,
    WorkloadSuite,
)

__all__ = [
    "ApprovalAuthority",
    "ApprovalAuthorization",
    "ApprovalChallenge",
    "ApprovalDecision",
    "ApprovalFlow",
    "ApprovalFormatError",
    "CompositionCandidate",
    "DescriptorBoundApprovalPolicy",
    "DurableCompositionRegistry",
    "EvaluationReport",
    "EvaluatorProtocol",
    "GeneratorProtocol",
    "NotAvailableError",
    "OperatorSigner",
    "ProcessDefinition",
    "ProcessEngine",
    "ProcessError",
    "ProcessHistory",
    "ProcessInstance",
    "PromoterProtocol",
    "PromotionEvidence",
    "Transition",
    "WorkloadSuite",
    "normalise_unified_diff",
]
