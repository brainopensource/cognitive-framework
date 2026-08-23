use serde::{Deserialize, Serialize};
use std::fmt;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum FailureKind {
    ImplementationError,
    TestCollusion,
    ContractContradiction,
    SyntaxLintError,
    SandboxResourceOom,
    SandboxTimeout,
    InfrastructureFault,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LexError {
    pub message: String,
    pub kind: FailureKind,
}

impl LexError {
    pub fn new(message: impl Into<String>, kind: FailureKind) -> Self {
        Self {
            message: message.into(),
            kind,
        }
    }

    pub fn contract_validation(message: impl Into<String>) -> Self {
        Self::new(message, FailureKind.ContractContradiction)
    }

    pub fn collusive_test(message: impl Into<String>) -> Self {
        Self::new(message, FailureKind.TestCollusion)
    }

    pub fn sandbox_timeout(message: impl Into<String>) -> Self {
        Self::new(message, FailureKind.SandboxTimeout)
    }

    pub fn sandbox_oom(message: impl Into<String>) -> Self {
        Self::new(message, FailureKind.SandboxResourceOom)
    }

    pub fn infrastructure(message: impl Into<String>) -> Self {
        Self::new(message, FailureKind.InfrastructureFault)
    }
}

impl fmt::Display for LexError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{:?}] {}", self.kind, self.message)
    }
}

impl std::error::Error for LexError {}
