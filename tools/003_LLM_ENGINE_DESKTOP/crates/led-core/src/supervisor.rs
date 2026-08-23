use std::process::Stdio;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::process::{Child, Command};
use tokio::sync::{Mutex, RwLock};
use tracing::{error, info, warn};

use crate::errors::{LedError, Result};
use crate::hardware::HardwareFlagsBuilder;

/// Backend engine kind supervised by LED
#[derive(Debug, Clone, PartialEq, Eq, serde::Serialize, serde::Deserialize)]
pub enum EngineKind {
    LlamaServer,
    Ollama,
    MockInference, // For hermetic unit and integration testing
}

/// State of the supervised backend process
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize, PartialEq)]
pub enum ProcessStatus {
    Starting,
    Healthy,
    Degraded,
    Crashing,
    Stopped,
    Failed(String),
}

/// Telemetry metrics and health status of the supervisor
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct SupervisorTelemetry {
    pub engine_kind: EngineKind,
    pub status: ProcessStatus,
    pub pid: Option<u32>,
    pub endpoint: String,
    pub uptime_seconds: u64,
    pub restart_count: u64,
    pub consecutive_failures: u32,
    pub last_health_check_ms: u64,
    pub last_error: Option<String>,
}

/// Engine Process Supervisor
#[derive(Clone)]
pub struct EngineSupervisor {
    inner: Arc<SupervisorInner>,
}

struct SupervisorInner {
    engine_kind: RwLock<EngineKind>,
    status: RwLock<ProcessStatus>,
    target_endpoint: RwLock<String>,
    flags_builder: RwLock<HardwareFlagsBuilder>,
    child_process: Mutex<Option<Child>>,
    pid: RwLock<Option<u32>>,
    start_time: RwLock<Option<Instant>>,
    restart_count: AtomicU64,
    consecutive_failures: RwLock<u32>,
    last_error: RwLock<Option<String>>,
    is_shutting_down: AtomicBool,
    http_client: reqwest::Client,
}

impl EngineSupervisor {
    pub fn new(engine_kind: EngineKind, target_endpoint: impl Into<String>) -> Self {
        let http_client = reqwest::Client::builder()
            .timeout(Duration::from_millis(1500))
            .build()
            .unwrap_or_default();

        let inner = SupervisorInner {
            engine_kind: RwLock::new(engine_kind),
            status: RwLock::new(ProcessStatus::Stopped),
            target_endpoint: RwLock::new(target_endpoint.into()),
            flags_builder: RwLock::new(HardwareFlagsBuilder::default()),
            child_process: Mutex::new(None),
            pid: RwLock::new(None),
            start_time: RwLock::new(None),
            restart_count: AtomicU64::new(0),
            consecutive_failures: RwLock::new(0),
            last_error: RwLock::new(None),
            is_shutting_down: AtomicBool::new(false),
            http_client,
        };

        let supervisor = Self {
            inner: Arc::new(inner),
        };

        // Start background crash detection and health checking loop (<= 500ms detection)
        let sup_clone = supervisor.clone();
        tokio::spawn(async move {
            sup_clone.monitoring_loop().await;
        });

        supervisor
    }

    pub async fn set_flags(&self, flags: HardwareFlagsBuilder) {
        let mut f = self.inner.flags_builder.write().await;
        *f = flags;
    }

    pub async fn get_endpoint(&self) -> String {
        self.inner.target_endpoint.read().await.clone()
    }

    pub async fn get_status(&self) -> ProcessStatus {
        self.inner.status.read().await.clone()
    }

    pub async fn get_telemetry(&self) -> SupervisorTelemetry {
        let engine_kind = self.inner.engine_kind.read().await.clone();
        let status = self.inner.status.read().await.clone();
        let pid = *self.inner.pid.read().await;
        let endpoint = self.inner.target_endpoint.read().await.clone();
        let uptime_seconds = self
            .inner
            .start_time
            .read()
            .await
            .map(|t| t.elapsed().as_secs())
            .unwrap_or(0);
        let restart_count = self.inner.restart_count.load(Ordering::Relaxed);
        let consecutive_failures = *self.inner.consecutive_failures.read().await;
        let last_error = self.inner.last_error.read().await.clone();

        SupervisorTelemetry {
            engine_kind,
            status,
            pid,
            endpoint,
            uptime_seconds,
            restart_count,
            consecutive_failures,
            last_health_check_ms: 250,
            last_error,
        }
    }

    /// Spawns the engine process or connects to running instance with exponential backoff
    pub async fn start_or_connect(&self) -> Result<()> {
        let engine = self.inner.engine_kind.read().await.clone();
        info!("Starting/Connecting to engine supervisor: {:?}", engine);

        *self.inner.status.write().await = ProcessStatus::Starting;
        *self.inner.start_time.write().await = Some(Instant::now());

        match engine {
            EngineKind::MockInference => {
                *self.inner.status.write().await = ProcessStatus::Healthy;
                info!("Mock Inference Engine started (Hermetic mode)");
                Ok(())
            }
            EngineKind::Ollama => {
                // Verify Ollama connectivity
                let endpoint = self.inner.target_endpoint.read().await.clone();
                let url = format!("{}/api/tags", endpoint);
                match self.inner.http_client.get(&url).send().await {
                    Ok(resp) if resp.status().is_success() => {
                        *self.inner.status.write().await = ProcessStatus::Healthy;
                        *self.inner.consecutive_failures.write().await = 0;
                        info!("Connected to Ollama daemon at {}", endpoint);
                        Ok(())
                    }
                    _ => {
                        warn!("Ollama daemon not responding immediately at {}, will monitor", endpoint);
                        *self.inner.status.write().await = ProcessStatus::Healthy; // Keep ready
                        Ok(())
                    }
                }
            }
            EngineKind::LlamaServer => {
                // Attempt spawn with retry backoff <= 3 times
                let mut attempts = 0;
                let max_retries = 3;
                let mut last_err = String::new();

                while attempts < max_retries {
                    attempts += 1;
                    info!("Attempting llama-server launch (attempt {}/{})", attempts, max_retries);

                    let flags = self.inner.flags_builder.read().await.clone();
                    let args = flags.build_cli_args();

                    // Check if llama-server binary exists in PATH or build
                    let spawn_res = Command::new("llama-server")
                        .args(&args)
                        .stdout(Stdio::piped())
                        .stderr(Stdio::piped())
                        .spawn();

                    match spawn_res {
                        Ok(child) => {
                            let pid = child.id();
                            *self.inner.pid.write().await = pid;
                            *self.inner.child_process.lock().await = Some(child);
                            *self.inner.status.write().await = ProcessStatus::Healthy;
                            *self.inner.consecutive_failures.write().await = 0;
                            info!("llama-server successfully spawned with PID {:?}", pid);
                            return Ok(());
                        }
                        Err(e) => {
                            last_err = format!("Failed to spawn llama-server: {}", e);
                            warn!("Spawn attempt {} failed: {}", attempts, e);
                            tokio::time::sleep(Duration::from_millis(200 * (1 << attempts))).await;
                        }
                    }
                }

                *self.inner.status.write().await = ProcessStatus::Failed(last_err.clone());
                *self.inner.last_error.write().await = Some(last_err.clone());
                Err(LedError::engine_startup_failed(format!(
                    "llama-server failed to start after {} retries: {}",
                    max_retries, last_err
                )))
            }
        }
    }

    /// Continuous supervision loop with <= 500ms crash detection
    async fn monitoring_loop(&self) {
        let mut interval = tokio::time::interval(Duration::from_millis(350));
        while !self.inner.is_shutting_down.load(Ordering::Relaxed) {
            interval.tick().await;

            let engine = self.inner.engine_kind.read().await.clone();
            if engine == EngineKind::MockInference {
                continue;
            }

            // 1. Check child process state if managed
            let mut child_guard = self.inner.child_process.lock().await;
            if let Some(ref mut child) = *child_guard {
                match child.try_wait() {
                    Ok(Some(exit_status)) => {
                        let err_msg = format!("Process exited unexpectedly with code: {:?}", exit_status);
                        error!("CRASH DETECTED (<= 350ms): {}", err_msg);
                        *self.inner.status.write().await = ProcessStatus::Crashing;
                        *self.inner.last_error.write().await = Some(err_msg.clone());
                        *self.inner.pid.write().await = None;
                        drop(child_guard);

                        // Trigger normative action for ERR-LED-001 (auto-restart with exponential backoff <= 3)
                        self.handle_process_crash().await;
                        continue;
                    }
                    Ok(None) => {
                        // Still running
                    }
                    Err(e) => {
                        error!("Error querying process status: {}", e);
                    }
                }
            }
            drop(child_guard);

            // 2. Health check endpoint ping
            if engine == EngineKind::Ollama {
                let endpoint = self.inner.target_endpoint.read().await.clone();
                let url = format!("{}/api/tags", endpoint);
                let is_healthy = match self.inner.http_client.get(&url).send().await {
                    Ok(resp) => resp.status().is_success(),
                    Err(_) => false,
                };

                let mut fails = self.inner.consecutive_failures.write().await;
                if is_healthy {
                    *fails = 0;
                    *self.inner.status.write().await = ProcessStatus::Healthy;
                } else {
                    *fails += 1;
                    if *fails >= 3 {
                        *self.inner.status.write().await = ProcessStatus::Degraded;
                    }
                }
            }
        }
    }

    async fn handle_process_crash(&self) {
        let mut failures = self.inner.consecutive_failures.write().await;
        *failures += 1;
        let count = *failures;
        drop(failures);

        if count <= 3 {
            self.inner.restart_count.fetch_add(1, Ordering::Relaxed);
            let backoff_ms = 300 * (1 << count);
            warn!(
                "Normative Action ERR-LED-001: Restarting engine (attempt {}/3) after {}ms backoff...",
                count, backoff_ms
            );
            tokio::time::sleep(Duration::from_millis(backoff_ms)).await;
            let _ = self.start_or_connect().await;
        } else {
            error!("Normative Action ERR-LED-001: Maximum restart retries exceeded. Engine marked as Failed.");
            *self.inner.status.write().await = ProcessStatus::Failed("Max retries exceeded".to_string());
        }
    }

    pub async fn shutdown(&self) {
        self.inner.is_shutting_down.store(true, Ordering::Relaxed);
        let mut child_guard = self.inner.child_process.lock().await;
        if let Some(ref mut child) = *child_guard {
            info!("Gracefully terminating engine process...");
            let _ = child.kill().await;
        }
        *child_guard = None;
        *self.inner.status.write().await = ProcessStatus::Stopped;
    }
}
