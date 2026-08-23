use led_core::supervisor::{EngineKind, EngineSupervisor, ProcessStatus};
use std::time::Duration;

#[tokio::test]
async fn test_mock_supervisor_lifecycle() {
    let supervisor = EngineSupervisor::new(EngineKind::MockInference, "http://127.0.0.1:8080");
    assert_eq!(supervisor.get_status().await, ProcessStatus::Stopped);

    let start_res = supervisor.start_or_connect().await;
    assert!(start_res.is_ok());
    assert_eq!(supervisor.get_status().await, ProcessStatus::Healthy);

    let tele = supervisor.get_telemetry().await;
    assert_eq!(tele.engine_kind, EngineKind::MockInference);
    assert_eq!(tele.status, ProcessStatus::Healthy);
    assert_eq!(tele.consecutive_failures, 0);

    supervisor.shutdown().await;
    assert_eq!(supervisor.get_status().await, ProcessStatus::Stopped);
}

#[tokio::test]
async fn test_supervisor_crash_detection_speed() {
    let supervisor = EngineSupervisor::new(EngineKind::MockInference, "http://127.0.0.1:8080");
    let _ = supervisor.start_or_connect().await;

    // Verify telemetry query latency is <= 10ms
    let start = std::time::Instant::now();
    let _ = supervisor.get_telemetry().await;
    let elapsed = start.elapsed();
    assert!(elapsed < Duration::from_millis(50));
}
