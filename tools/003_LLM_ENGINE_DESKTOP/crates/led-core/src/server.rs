use axum::extract::{Json, State};
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use axum::Router;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::sync::Arc;
use tokio::net::TcpListener;
use tower_http::cors::{Any, CorsLayer};
use tower_http::trace::TraceLayer;
use tracing::info;

use crate::errors::{LedError, Result};
use crate::hardware::{HardwareProfile, LayerOffloadPlan};
use crate::presets::{PresetConfig, PresetManager};
use crate::streaming::{create_mock_sse_stream, JitterMetrics, StreamJitterTracker};
use crate::supervisor::{EngineSupervisor, SupervisorTelemetry};
use crate::worker_bridge::{AstScoreResult, PythonWorkerBridge, TunerOptimizationResult};

/// OpenAI Chat Completion Message
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatMessage {
    pub role: String,
    pub content: String,
}

/// OpenAI Chat Completion Request with Hardware/Inference Options
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatCompletionRequest {
    pub model: String,
    pub messages: Vec<ChatMessage>,
    #[serde(default)]
    pub stream: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub temperature: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_p: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max_tokens: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub num_ctx: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub num_predict: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub num_thread: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub disable_thinking: Option<bool>,
}

/// OpenAI Chat Completion Response Choice
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatCompletionChoice {
    pub index: usize,
    pub message: ChatMessage,
    pub finish_reason: String,
}

/// OpenAI Chat Completion Usage
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompletionUsage {
    pub prompt_tokens: usize,
    pub completion_tokens: usize,
    pub total_tokens: usize,
}

/// OpenAI Chat Completion Non-Streaming Response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatCompletionResponse {
    pub id: String,
    pub object: String,
    pub created: i64,
    pub model: String,
    pub choices: Vec<ChatCompletionChoice>,
    pub usage: CompletionUsage,
}

/// OpenAI Model Object
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelObject {
    pub id: String,
    pub object: String,
    pub created: i64,
    pub owned_by: String,
}

/// OpenAI Models List Response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelListResponse {
    pub object: String,
    pub data: Vec<ModelObject>,
}

/// Live System Telemetry
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SystemTelemetry {
    pub hardware: HardwareProfile,
    pub supervisor: SupervisorTelemetry,
    pub streaming_jitter: JitterMetrics,
    pub active_layer_offload: LayerOffloadPlan,
}

/// Shared Server State
#[derive(Clone)]
pub struct AppState {
    pub supervisor: EngineSupervisor,
    pub preset_manager: Arc<PresetManager>,
    pub worker_bridge: PythonWorkerBridge,
    pub jitter_tracker: StreamJitterTracker,
    pub hardware_profile: HardwareProfile,
    pub workspace_root: PathBuf,
}

/// Create the full Axum router
pub fn create_router(state: AppState) -> Router {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    Router::new()
        // OpenAI Canonical Routes
        .route("/v1/chat/completions", post(handle_chat_completions))
        .route("/v1/models", get(handle_list_models))
        // LED Management & Telemetry Routes
        .route("/v1/health", get(handle_health))
        .route("/v1/telemetry", get(handle_telemetry))
        .route("/v1/presets", get(handle_list_presets).post(handle_save_preset))
        .route("/v1/presets/apply", post(handle_apply_preset))
        .route("/v1/bench/run", post(handle_run_benchmark))
        .route("/v1/bench/stop", post(handle_stop_benchmark))
        .route("/v1/bench/results", get(handle_get_benchmark_results).delete(handle_clear_benchmark_results))
        .route("/v1/tuner/calibrate", post(handle_tuner_calibrate))
        .route("/v1/eval/ast", post(handle_eval_ast))
        .layer(cors)
        .layer(TraceLayer::new_for_http())
        .with_state(state)
}

// Handlers

async fn handle_health(State(state): State<AppState>) -> Json<serde_json::Value> {
    let sup_telemetry = state.supervisor.get_telemetry().await;
    Json(serde_json::json!({
        "status": "healthy",
        "version": env!("CARGO_PKG_VERSION"),
        "engine": sup_telemetry.status,
        "pid": sup_telemetry.pid,
        "uptime_seconds": sup_telemetry.uptime_seconds,
    }))
}

async fn handle_list_models(State(state): State<AppState>) -> Json<ModelListResponse> {
    let endpoint = state.supervisor.get_telemetry().await.endpoint;
    let client = reqwest::Client::new();
    let mut model_objects = Vec::new();

    if let Ok(resp) = client.get(format!("{}/api/tags", endpoint.trim_end_matches('/'))).send().await {
        if let Ok(val) = resp.json::<serde_json::Value>().await {
            if let Some(models) = val.get("models").and_then(|m| m.as_array()) {
                for m in models {
                    if let Some(name) = m.get("name").and_then(|n| n.as_str()) {
                        model_objects.push(ModelObject {
                            id: name.to_string(),
                            object: "model".to_string(),
                            created: 1700000000,
                            owned_by: "local-gpu".to_string(),
                        });
                    }
                }
            }
        }
    }

    if model_objects.is_empty() {
        model_objects = vec![
            ModelObject {
                id: "qwen2.5:1.5b".to_string(),
                object: "model".to_string(),
                created: 1700000000,
                owned_by: "led-engine".to_string(),
            },
            ModelObject {
                id: "qwen2.5-coder:14b".to_string(),
                object: "model".to_string(),
                created: 1700000000,
                owned_by: "led-engine".to_string(),
            },
            ModelObject {
                id: "qwen3.8:27b-unsloth".to_string(),
                object: "model".to_string(),
                created: 1700000000,
                owned_by: "led-engine".to_string(),
            },
            ModelObject {
                id: "deepseek-r1:14b".to_string(),
                object: "model".to_string(),
                created: 1700000000,
                owned_by: "led-engine".to_string(),
            },
        ];
    }

    Json(ModelListResponse {
        object: "list".to_string(),
        data: model_objects,
    })
}

async fn handle_telemetry(State(state): State<AppState>) -> Json<SystemTelemetry> {
    let sup_telemetry = state.supervisor.get_telemetry().await;
    let jitter = state.jitter_tracker.get_metrics();
    
    // Asynchronously query live VRAM allocation from Ollama daemon (:11434/api/ps)
    let mut allocated_vram_mb: u64 = 0;
    let client = reqwest::Client::new();
    let ps_endpoint = format!("{}/api/ps", sup_telemetry.endpoint.trim_end_matches('/'));
    if let Ok(resp) = client.get(&ps_endpoint).send().await {
        if let Ok(val) = resp.json::<serde_json::Value>().await {
            if let Some(models) = val.get("models").and_then(|m| m.as_array()) {
                for m in models {
                    if let Some(vram_bytes) = m.get("size_vram").and_then(|s| s.as_u64()) {
                        allocated_vram_mb += vram_bytes / (1024 * 1024);
                    }
                }
            }
        }
    }

    let hw = HardwareProfile::probe_with_allocated_vram(allocated_vram_mb);

    let offload = LayerOffloadPlan::calculate(
        "qwen2.5-coder:14b",
        48,
        9200,
        2048,
        hw.primary_gpu.as_ref().map(|g| g.free_vram_mb).unwrap_or(16384),
        "q8_0",
    );

    Json(SystemTelemetry {
        hardware: hw,
        supervisor: sup_telemetry,
        streaming_jitter: jitter,
        active_layer_offload: offload,
    })
}

async fn handle_list_presets(State(state): State<AppState>) -> Result<Json<Vec<PresetConfig>>> {
    let presets = state.preset_manager.list_presets()?;
    Ok(Json(presets))
}

async fn handle_save_preset(
    State(state): State<AppState>,
    Json(preset): Json<PresetConfig>,
) -> Result<Json<serde_json::Value>> {
    let path = state.preset_manager.save_preset(&preset)?;
    Ok(Json(serde_json::json!({
        "status": "saved",
        "preset_name": preset.preset_name,
        "path": path.to_string_lossy(),
    })))
}

async fn handle_apply_preset(
    State(state): State<AppState>,
    Json(preset): Json<PresetConfig>,
) -> Result<Json<serde_json::Value>> {
    info!("Applying preset: {}", preset.preset_name);
    let mut flags = crate::hardware::HardwareFlagsBuilder::new(&preset.target_model);
    flags.num_ctx = preset.options.num_ctx;
    flags.num_thread = preset.options.num_thread;
    if let Some(draft) = preset.options.draft_tokens {
        flags.draft_tokens = draft;
    }
    state.supervisor.set_flags(flags).await;

    Ok(Json(serde_json::json!({
        "status": "applied",
        "preset": preset.preset_name,
        "options": preset.options,
    })))
}

async fn handle_eval_ast(
    State(state): State<AppState>,
    Json(payload): Json<serde_json::Value>,
) -> Result<Json<AstScoreResult>> {
    let code = payload
        .get("code")
        .and_then(|v| v.as_str())
        .unwrap_or_default();
    let res = state.worker_bridge.evaluate_ast(code).await?;
    Ok(Json(res))
}

#[derive(Debug, Deserialize)]
pub struct BenchRunRequest {
    pub model: Option<String>,
    pub runs: Option<usize>,
}

async fn handle_run_benchmark(
    State(state): State<AppState>,
    Json(req): Json<BenchRunRequest>,
) -> Result<Json<serde_json::Value>> {
    let model = req.model.unwrap_or_else(|| "qwen2.5-coder:14b".to_string());
    let runs_count = req.runs.unwrap_or(16);
    info!("Starting sequential DoE benchmark ({} runs) for model: {}", runs_count, model);

    let script = state.workspace_root.join("matrix_execution/bench_matrix_16.py");
    let python_bin = state.workspace_root.join(".venv/bin/python3");
    let py = if python_bin.exists() {
        python_bin
    } else {
        PathBuf::from("python3")
    };

    let output = tokio::process::Command::new(&py)
        .arg(&script)
        .arg(&model)
        .arg(runs_count.to_string())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .output()
        .await
        .map_err(|e| LedError::bench_timeout(format!("Benchmark execution failed: {}", e)))?;

    let stdout = String::from_utf8_lossy(&output.stdout);
    let stderr = String::from_utf8_lossy(&output.stderr);

    Ok(Json(serde_json::json!({
        "status": if output.status.success() { "completed" } else { "failed" },
        "model": model,
        "stdout": stdout,
        "stderr": stderr,
    })))
}

async fn handle_stop_benchmark() -> Result<Json<serde_json::Value>> {
    let _ = tokio::process::Command::new("pkill")
        .arg("-9")
        .arg("-f")
        .arg("bench_matrix_16.py")
        .output()
        .await;
    Ok(Json(serde_json::json!({ "status": "stopped" })))
}

async fn handle_get_benchmark_results(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>> {
    let base_dir = state.workspace_root.join("bench_finetune");
    let mut runs = Vec::new();

    if base_dir.exists() {
        if let Ok(entries) = std::fs::read_dir(&base_dir) {
            for entry in entries.flatten() {
                let p = entry.path();
                if p.is_dir() {
                    let csv = p.join("benchmark_results_16.csv");
                    if csv.exists() {
                        if let Ok(content) = std::fs::read_to_string(&csv) {
                            let mut lines = content.lines();
                            let header = lines.next();
                            if header.is_some() {
                                for line in lines {
                                    let parts: Vec<&str> = line.split(',').collect();
                                    if parts.len() >= 16 {
                                        runs.push(serde_json::json!({
                                            "run_id": parts[2].split('_').next().unwrap_or(parts[2]),
                                            "full_id": parts[2],
                                            "model": parts[3],
                                            "ctx": if parts[4] == "1" { "2048" } else { "Default" },
                                            "think": if parts[5] == "1" { "noThink" } else { "stdThink" },
                                            "samp": if parts[6] == "1" { "greedy" } else { "temp 0.7" },
                                            "thr": if parts[7] == "1" { "8 cores" } else { "Def (16)" },
                                            "cap": if parts[8] == "1" { "600" } else { "unlim" },
                                            "prompt_tps": parts[10].parse::<f64>().unwrap_or(0.0),
                                            "tps": parts[12].parse::<f64>().unwrap_or(0.0),
                                            "lat": parts[13].parse::<f64>().unwrap_or(0.0),
                                            "score": parts[14].parse::<i64>().unwrap_or(0),
                                            "feedback": parts[15],
                                        }));
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Ok(Json(serde_json::json!({ "runs": runs })))
}

async fn handle_clear_benchmark_results(
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>> {
    let base_dir = state.workspace_root.join("bench_finetune");
    if base_dir.exists() {
        let _ = std::fs::remove_dir_all(&base_dir);
        let _ = std::fs::create_dir_all(&base_dir);
    }
    Ok(Json(serde_json::json!({ "status": "cleared" })))
}

#[derive(Debug, Deserialize)]
pub struct CalibrateRequest {
    pub model: Option<String>,
}

async fn handle_tuner_calibrate(
    State(state): State<AppState>,
    Json(req): Json<CalibrateRequest>,
) -> Result<Json<TunerOptimizationResult>> {
    let model = req.model.unwrap_or_else(|| "qwen2.5:1.5b".to_string());
    info!("Triggering AI Auto-Tuner calibration for: {}", model);

    // Dynamic folder resolution matching model name
    let clean_model = if model.contains("14b") {
        "qwen_25C_14B"
    } else if model.contains("1.5b") {
        "qwen_25_15B"
    } else if model.contains("7b") {
        "qwen_25C_7B"
    } else {
        "qwen_38_27B"
    };

    let mut csv_file = state
        .workspace_root
        .join(format!("bench_finetune/{}/benchmark_results_16.csv", clean_model));

    // Fallback if specific model benchmark has not been run yet
    if !csv_file.exists() {
        let base_bench = state.workspace_root.join("bench_finetune");
        if let Ok(entries) = std::fs::read_dir(&base_bench) {
            for entry in entries.flatten() {
                let candidate = entry.path().join("benchmark_results_16.csv");
                if candidate.exists() {
                    csv_file = candidate;
                    break;
                }
            }
        }
    }

    let res = state
        .worker_bridge
        .run_surrogate_training(&csv_file, &model)
        .await?;

    Ok(Json(res))
}

async fn handle_chat_completions(
    State(state): State<AppState>,
    Json(req): Json<ChatCompletionRequest>,
) -> Response {
    let id = format!("chatcmpl-{}", uuid::Uuid::new_v4());
    let backend_url = state.supervisor.get_telemetry().await.endpoint;

    if req.stream {
        let msg_values: Vec<serde_json::Value> = req
            .messages
            .iter()
            .map(|m| serde_json::json!({ "role": &m.role, "content": &m.content }))
            .collect();

        crate::streaming::create_real_sse_stream(
            id,
            req.model,
            backend_url,
            msg_values,
            req.temperature,
            req.num_ctx,
            req.num_predict,
            req.num_thread,
            state.jitter_tracker.clone(),
        )
        .into_response()
    } else {
        let client = reqwest::Client::new();
        let mut options = serde_json::json!({
            "temperature": req.temperature.unwrap_or(0.7),
            "num_ctx": req.num_ctx.unwrap_or(2048),
        });
        if let Some(predict) = req.num_predict {
            options["num_predict"] = serde_json::json!(predict);
        }
        if let Some(thread) = req.num_thread {
            options["num_thread"] = serde_json::json!(thread);
        }

        let payload = serde_json::json!({
            "model": &req.model,
            "messages": &req.messages,
            "stream": false,
            "options": options,
        });

        let endpoint = format!("{}/api/chat", backend_url.trim_end_matches('/'));
        let assistant_reply = match client.post(&endpoint).json(&payload).send().await {
            Ok(resp) => {
                if let Ok(val) = resp.json::<serde_json::Value>().await {
                    val.get("message")
                        .and_then(|m| m.get("content"))
                        .and_then(|c| c.as_str())
                        .unwrap_or("No response generated")
                        .to_string()
                } else {
                    "Error parsing backend JSON".to_string()
                }
            }
            Err(e) => format!("Error connecting to backend: {}", e),
        };

        let completion = ChatCompletionResponse {
            id,
            object: "chat.completion".to_string(),
            created: chrono::Utc::now().timestamp(),
            model: req.model,
            choices: vec![ChatCompletionChoice {
                index: 0,
                message: ChatMessage {
                    role: "assistant".to_string(),
                    content: assistant_reply,
                },
                finish_reason: "stop".to_string(),
            }],
            usage: CompletionUsage {
                prompt_tokens: 20,
                completion_tokens: 42,
                total_tokens: 62,
            },
        };
        (StatusCode::OK, Json(completion)).into_response()
    }
}

/// Runs the Axum HTTP server on a specified listener
pub async fn run_server(listener: TcpListener, state: AppState) -> std::io::Result<()> {
    let router = create_router(state);
    info!("Axum OpenAI Gateway bound to {:?}", listener.local_addr());
    axum::serve(listener, router).await
}
