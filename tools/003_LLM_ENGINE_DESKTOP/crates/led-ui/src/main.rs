use axum::response::{Html, IntoResponse, Response};
use axum::routing::get;
use clap::Parser;
use led_core::hardware::HardwareProfile;
use led_core::presets::PresetManager;
use led_core::server::{create_router, AppState};
use led_core::streaming::StreamJitterTracker;
use led_core::supervisor::{EngineKind, EngineSupervisor};
use led_core::worker_bridge::PythonWorkerBridge;
use std::net::SocketAddr;
use std::sync::Arc;
use tokio::net::TcpListener;
use tracing::Level;
use tracing_subscriber::FmtSubscriber;

const EMBEDDED_INDEX_HTML: &str = include_str!("../ui/index.html");
const EMBEDDED_APP_JS: &str = include_str!("../ui/app.js");
const EMBEDDED_LOGO_PNG: &[u8] = include_bytes!("../ui/logo.png");

#[derive(Parser, Debug)]
#[command(name = "led-studio")]
#[command(about = "LED Studio - Local LLM Engine Desktop GUI Host & Inference Workbench")]
#[command(version = env!("CARGO_PKG_VERSION"))]
struct Args {
    #[arg(long, default_value = "127.0.0.1")]
    host: String,

    #[arg(short, long, default_value_t = 8080)]
    port: u16,

    #[arg(long, default_value = "ollama")]
    engine: String,

    #[arg(long, default_value = "http://127.0.0.1:11434")]
    backend_endpoint: String,

    #[arg(long)]
    no_open: bool,
}

async fn serve_index() -> Html<&'static str> {
    Html(EMBEDDED_INDEX_HTML)
}

async fn serve_app_js() -> Response {
    (
        [(axum::http::header::CONTENT_TYPE, "application/javascript")],
        EMBEDDED_APP_JS,
    )
        .into_response()
}

async fn serve_logo_png() -> Response {
    (
        [(axum::http::header::CONTENT_TYPE, "image/png")],
        EMBEDDED_LOGO_PNG,
    )
        .into_response()
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber).ok();

    let args = Args::parse();
    let workspace_root = std::env::current_dir()?;

    let engine_kind = match args.engine.to_lowercase().as_str() {
        "llama" | "llama-server" => EngineKind::LlamaServer,
        "mock" => EngineKind::MockInference,
        _ => EngineKind::Ollama,
    };

    let supervisor = EngineSupervisor::new(engine_kind.clone(), args.backend_endpoint.clone());
    supervisor.start_or_connect().await?;

    let preset_manager = Arc::new(PresetManager::new(workspace_root.join("presets")));
    let worker_bridge = PythonWorkerBridge::new(&workspace_root);
    let jitter_tracker = StreamJitterTracker::new();
    let hardware_profile = HardwareProfile::probe();

    let state = AppState {
        supervisor: supervisor.clone(),
        preset_manager,
        worker_bridge,
        jitter_tracker,
        hardware_profile,
        workspace_root: workspace_root.clone(),
    };

    let api_router = create_router(state);

    // Static UI Routes
    let app = api_router
        .route("/", get(serve_index))
        .route("/index.html", get(serve_index))
        .route("/app.js", get(serve_app_js))
        .route("/logo.png", get(serve_logo_png))
        .route("/favicon.ico", get(serve_logo_png))
        .route("/favicon.png", get(serve_logo_png));

    let addr: SocketAddr = format!("{}:{}", args.host, args.port).parse()?;
    let listener = TcpListener::bind(addr).await?;
    let url = format!("http://{}:{}", args.host, args.port);

    println!("\n╔════════════════════════════════════════════════════════════════════╗");
    println!("║       ⚡ LED STUDIO — LOCAL LLM ENGINE DESKTOP HOST RUNNING         ║");
    println!("╠════════════════════════════════════════════════════════════════════╣");
    println!("║  Studio URL:   {:<51} ║", url);
    println!("║  API Gateway:  http://{:<47} ║", format!("{}:{}/v1", args.host, args.port));
    println!("║  Architecture: Pure Rust Backend (Axum/Tokio) + Desktop Studio GUI ║");
    println!("║  Features:     • [Tab 1] Zero-GIL SSE Streaming Chat & Code Studio ║");
    println!("║                • [Tab 2] Empirical Bench Lab (16-Run DoE Matrix)   ║");
    println!("║                • [Tab 3] AI Auto-Tuner (Scikit-Learn Surrogate)    ║");
    println!("║                • [Tab 4] Hardware Topology & VRAM vs RAM Offload   ║");
    println!("╚════════════════════════════════════════════════════════════════════╝\n");

    if !args.no_open {
        let _ = open::that(&url);
    }

    axum::serve(listener, app).await?;
    Ok(())
}
