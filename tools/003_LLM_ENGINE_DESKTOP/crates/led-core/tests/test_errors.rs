use axum::response::IntoResponse;
use led_core::errors::{ErrorCode, LedError};

#[test]
fn test_normative_error_codes() {
    assert_eq!(ErrorCode::ErrLed001EngineStartupFailed.as_str(), "ERR-LED-001");
    assert_eq!(ErrorCode::ErrLed002VramOom.as_str(), "ERR-LED-002");
    assert_eq!(ErrorCode::ErrLed003BenchTimeout.as_str(), "ERR-LED-003");
    assert_eq!(ErrorCode::ErrLed004AutoTunerLowVariance.as_str(), "ERR-LED-004");
    assert_eq!(ErrorCode::ErrLed005AstSyntaxError.as_str(), "ERR-LED-005");
}

#[test]
fn test_error_severity_and_normative_actions() {
    let err1 = LedError::engine_startup_failed("Port 8080 already in use");
    assert_eq!(err1.code, ErrorCode::ErrLed001EngineStartupFailed);
    assert_eq!(err1.severity, "CRITICAL");
    assert_eq!(err1.subsystem, "Engine");
    assert!(err1.system_action.contains("exponential backoff"));

    let err2 = LedError::vram_oom("Out of VRAM allocating KV cache");
    assert_eq!(err2.code, ErrorCode::ErrLed002VramOom);
    assert_eq!(err2.severity, "HIGH");
    assert!(err2.system_action.contains("reduce num_ctx by 50%"));

    let err5 = LedError::ast_syntax_error("Unexpected EOF");
    assert_eq!(err5.code, ErrorCode::ErrLed005AstSyntaxError);
    assert_eq!(err5.severity, "LOW");
    assert!(err5.system_action.contains("S_syntax = 0"));
}

#[test]
fn test_error_http_response() {
    let err = LedError::bench_timeout("Request timed out");
    let resp = err.into_response();
    assert_eq!(resp.status(), axum::http::StatusCode::GATEWAY_TIMEOUT);
}
