use axum::body::{to_bytes, Body};
use axum::http::{Request, StatusCode};
use led_core::hardware::HardwareProfile;
use led_core::presets::PresetManager;
use led_core::server::{create_router, AppState};
use led_core::streaming::StreamJitterTracker;
use led_core::supervisor::{EngineKind, EngineSupervisor};
use led_core::worker_bridge::PythonWorkerBridge;
use std::sync::Arc;
use tower::ServiceExt;

fn setup_test_app() -> axum::Router {
    let workspace_root = std::env::current_dir().unwrap();
    let supervisor = EngineSupervisor::new(EngineKind::MockInference, "http://127.0.0.1:8080");
    let preset_manager = Arc::new(PresetManager::new(workspace_root.join("presets")));
    let worker_bridge = PythonWorkerBridge::new(&workspace_root);
    let jitter_tracker = StreamJitterTracker::new();
    let hardware_profile = HardwareProfile::probe();

    let state = AppState {
        supervisor,
        preset_manager,
        worker_bridge,
        jitter_tracker,
        hardware_profile,
        workspace_root,
    };

    create_router(state)
}

#[tokio::test]
async fn test_health_endpoint() {
    let app = setup_test_app();

    let response = app
        .oneshot(
            Request::builder()
                .uri("/v1/health")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
    let bytes = to_bytes(response.into_body(), usize::MAX).await.unwrap();
    let json: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
    assert_eq!(json["status"], "healthy");
}

#[tokio::test]
async fn test_models_endpoint() {
    let app = setup_test_app();

    let response = app
        .oneshot(
            Request::builder()
                .uri("/v1/models")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
    let bytes = to_bytes(response.into_body(), usize::MAX).await.unwrap();
    let json: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
    assert_eq!(json["object"], "list");
    assert!(json["data"].as_array().unwrap().len() >= 2);
}

#[tokio::test]
async fn test_telemetry_endpoint() {
    let app = setup_test_app();

    let response = app
        .oneshot(
            Request::builder()
                .uri("/v1/telemetry")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
    let bytes = to_bytes(response.into_body(), usize::MAX).await.unwrap();
    let json: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
    assert!(json["hardware"]["cpu"]["brand"].is_string());
    assert!(json["streaming_jitter"]["meets_slo"].as_bool().unwrap_or(false));
}

#[tokio::test]
async fn test_chat_completions_non_streaming() {
    let app = setup_test_app();

    let payload = serde_json::json!({
        "model": "qwen2.5-coder:14b",
        "messages": [
            {"role": "user", "content": "Write a python fibonacci function"}
        ],
        "stream": false
    });

    let response = app
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/v1/chat/completions")
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&payload).unwrap()))
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
    let bytes = to_bytes(response.into_body(), usize::MAX).await.unwrap();
    let json: serde_json::Value = serde_json::from_slice(&bytes).unwrap();
    assert_eq!(json["object"], "chat.completion");
    assert_eq!(json["model"], "qwen2.5-coder:14b");
    assert!(!json["choices"].as_array().unwrap().is_empty());
}

#[tokio::test]
async fn test_chat_completions_streaming() {
    let app = setup_test_app();

    let payload = serde_json::json!({
        "model": "qwen2.5-coder:14b",
        "messages": [
            {"role": "user", "content": "Write a python fibonacci function"}
        ],
        "stream": true
    });

    let response = app
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/v1/chat/completions")
                .header("Content-Type", "application/json")
                .body(Body::from(serde_json::to_vec(&payload).unwrap()))
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
    let content_type = response
        .headers()
        .get("content-type")
        .unwrap()
        .to_str()
        .unwrap();
    assert!(content_type.contains("text/event-stream"));
}
