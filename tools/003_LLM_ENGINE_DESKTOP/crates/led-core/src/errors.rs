use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use serde::{Deserialize, Serialize};
use std::fmt;
use thiserror::Error;

/// Normative error codes conforming to SPEC-LED-2026-V1 (Section 5).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ErrorCode {
    /// ERR-LED-001: llama-server process failed to start or port 8080 busy.
    #[serde(rename = "ERR-LED-001")]
    ErrLed001EngineStartupFailed,
    /// ERR-LED-002: GPU VRAM out-of-memory during model weight allocation.
    #[serde(rename = "ERR-LED-002")]
    ErrLed002VramOom,
    /// ERR-LED-003: API connection timed out during benchmark run.
    #[serde(rename = "ERR-LED-003")]
    ErrLed003BenchTimeout,
    /// ERR-LED-004: Insufficient variance in training dataset for ML regression.
    #[serde(rename = "ERR-LED-004")]
    ErrLed004AutoTunerLowVariance,
    /// ERR-LED-005: Generated code has fatal unclosed syntax error.
    #[serde(rename = "ERR-LED-005")]
    ErrLed005AstSyntaxError,
    /// Generic internal server or I/O error
    #[serde(rename = "ERR-LED-999")]
    ErrLedGenericInternal,
}

impl ErrorCode {
    pub fn as_str(&self) -> &'static str {
        match self {
            ErrorCode::ErrLed001EngineStartupFailed => "ERR-LED-001",
            ErrorCode::ErrLed002VramOom => "ERR-LED-002",
            ErrorCode::ErrLed003BenchTimeout => "ERR-LED-003",
            ErrorCode::ErrLed004AutoTunerLowVariance => "ERR-LED-004",
            ErrorCode::ErrLed005AstSyntaxError => "ERR-LED-005",
            ErrorCode::ErrLedGenericInternal => "ERR-LED-999",
        }
    }

    pub fn subsystem(&self) -> &'static str {
        match self {
            ErrorCode::ErrLed001EngineStartupFailed => "Engine",
            ErrorCode::ErrLed002VramOom => "Hardware",
            ErrorCode::ErrLed003BenchTimeout => "Bench Lab",
            ErrorCode::ErrLed004AutoTunerLowVariance => "Auto-Tuner",
            ErrorCode::ErrLed005AstSyntaxError => "AST",
            ErrorCode::ErrLedGenericInternal => "System",
        }
    }

    pub fn severity(&self) -> &'static str {
        match self {
            ErrorCode::ErrLed001EngineStartupFailed => "CRITICAL",
            ErrorCode::ErrLed002VramOom => "HIGH",
            ErrorCode::ErrLed003BenchTimeout => "MEDIUM",
            ErrorCode::ErrLed004AutoTunerLowVariance => "LOW",
            ErrorCode::ErrLed005AstSyntaxError => "LOW",
            ErrorCode::ErrLedGenericInternal => "HIGH",
        }
    }

    pub fn normative_action(&self) -> &'static str {
        match self {
            ErrorCode::ErrLed001EngineStartupFailed => {
                "Fallback to retry with exponential backoff (<= 3 retries)."
            }
            ErrorCode::ErrLed002VramOom => {
                "Automatically reduce num_ctx by 50% and offload layers to CPU RAM."
            }
            ErrorCode::ErrLed003BenchTimeout => {
                "Record run as failed, flush partial CSV record, continue next run."
            }
            ErrorCode::ErrLed004AutoTunerLowVariance => {
                "Warn user, suggest running full 32-run grid."
            }
            ErrorCode::ErrLed005AstSyntaxError => {
                "Assign S_syntax = 0, record feedback traceback."
            }
            ErrorCode::ErrLedGenericInternal => "Log error telemetry and return 500 Internal Error.",
        }
    }
}

impl fmt::Display for ErrorCode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.as_str())
    }
}

/// Structured LED engine error
#[derive(Debug, Error, Serialize, Deserialize)]
#[error("[{code}] {message}")]
pub struct LedError {
    pub code: ErrorCode,
    pub message: String,
    pub subsystem: String,
    pub severity: String,
    pub system_action: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub details: Option<String>,
}

impl LedError {
    pub fn new(code: ErrorCode, message: impl Into<String>) -> Self {
        Self {
            subsystem: code.subsystem().to_string(),
            severity: code.severity().to_string(),
            system_action: code.normative_action().to_string(),
            code,
            message: message.into(),
            details: None,
        }
    }

    pub fn with_details(mut self, details: impl Into<String>) -> Self {
        self.details = Some(details.into());
        self
    }

    pub fn engine_startup_failed(msg: impl Into<String>) -> Self {
        Self::new(ErrorCode::ErrLed001EngineStartupFailed, msg)
    }

    pub fn vram_oom(msg: impl Into<String>) -> Self {
        Self::new(ErrorCode::ErrLed002VramOom, msg)
    }

    pub fn bench_timeout(msg: impl Into<String>) -> Self {
        Self::new(ErrorCode::ErrLed003BenchTimeout, msg)
    }

    pub fn autotuner_low_variance(msg: impl Into<String>) -> Self {
        Self::new(ErrorCode::ErrLed004AutoTunerLowVariance, msg)
    }

    pub fn ast_syntax_error(msg: impl Into<String>) -> Self {
        Self::new(ErrorCode::ErrLed005AstSyntaxError, msg)
    }

    pub fn internal(msg: impl Into<String>) -> Self {
        Self::new(ErrorCode::ErrLedGenericInternal, msg)
    }
}

impl IntoResponse for LedError {
    fn into_response(self) -> Response {
        let status = match self.code {
            ErrorCode::ErrLed001EngineStartupFailed => StatusCode::SERVICE_UNAVAILABLE,
            ErrorCode::ErrLed002VramOom => StatusCode::INSUFFICIENT_STORAGE,
            ErrorCode::ErrLed003BenchTimeout => StatusCode::GATEWAY_TIMEOUT,
            ErrorCode::ErrLed004AutoTunerLowVariance => StatusCode::UNPROCESSABLE_ENTITY,
            ErrorCode::ErrLed005AstSyntaxError => StatusCode::BAD_REQUEST,
            ErrorCode::ErrLedGenericInternal => StatusCode::INTERNAL_SERVER_ERROR,
        };

        let body = serde_json::json!({
            "error": {
                "code": self.code.as_str(),
                "message": self.message,
                "subsystem": self.subsystem,
                "severity": self.severity,
                "system_action": self.system_action,
                "details": self.details,
            }
        });

        (status, axum::Json(body)).into_response()
    }
}

pub type Result<T> = std::result::Result<T, LedError>;
