use clap::{Parser, Subcommand};
use led_core::hardware::{HardwareFlagsBuilder, HardwareProfile, LayerOffloadPlan};
use led_core::presets::PresetManager;
use led_core::server::{run_server, AppState};
use led_core::streaming::StreamJitterTracker;
use led_core::supervisor::{EngineKind, EngineSupervisor};
use led_core::worker_bridge::PythonWorkerBridge;
use std::net::SocketAddr;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::net::TcpListener;
use tracing::Level;
use tracing_subscriber::FmtSubscriber;

#[derive(Parser)]
#[command(name = "led")]
#[command(about = "LED - Local LLM Engine Desktop CLI & High-Performance Supervisor")]
#[command(version = env!("CARGO_PKG_VERSION"))]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Start the LED Engine Supervisor & OpenAI-compatible /v1 Gateway
    Serve {
        #[arg(short, long, default_value = "127.0.0.1")]
        host: String,
        #[arg(short, long, default_value_t = 8080)]
        port: u16,
        #[arg(long, default_value = "ollama")]
        engine: String,
        #[arg(long, default_value = "http://127.0.0.1:11434")]
        backend_endpoint: String,
    },
    /// Probe host hardware (AMD Radeon GPU, Ryzen CPU topology, RAM vs VRAM offload)
    Profile {
        #[arg(long, default_value = "qwen2.5-coder:14b")]
        model: String,
        #[arg(long, default_value_t = 2048)]
        ctx: usize,
    },
    /// AI Auto-Tuner: train surrogate model, rank SHAP features & find Pareto Sweet Spot
    Tune {
        #[arg(short, long, default_value = "qwen2.5-coder:14b")]
        model: String,
        #[arg(short, long)]
        csv: Option<PathBuf>,
    },
    /// AST Code Validator: score Python code on 0-100 scale (syntax, typing, errors, purity)
    Eval {
        #[arg(short, long)]
        file: Option<PathBuf>,
        #[arg(short, long)]
        code: Option<String>,
    },
    /// Manage, list, and export tuned presets and Modelfiles
    Presets {
        #[command(subcommand)]
        sub: PresetCommands,
    },
    /// Run 16-run Fractional Factorial DoE benchmark
    Bench {
        #[arg(short, long, default_value = "qwen2.5-coder:14b")]
        model: String,
    },
}

#[derive(Subcommand)]
enum PresetCommands {
    /// List all calibrated presets
    List,
    /// Show preset configuration and Modelfile
    Show { name: String },
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber).ok();

    let cli = Cli::parse();
    let workspace_root = std::env::current_dir()?;

    match cli.command {
        Commands::Serve {
            host,
            port,
            engine,
            backend_endpoint,
        } => {
            let engine_kind = match engine.to_lowercase().as_str() {
                "llama" | "llama-server" => EngineKind::LlamaServer,
                "mock" => EngineKind::MockInference,
                _ => EngineKind::Ollama,
            };

            let supervisor = EngineSupervisor::new(engine_kind.clone(), backend_endpoint.clone());
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
                workspace_root,
            };

            let addr: SocketAddr = format!("{}:{}", host, port).parse()?;
            let listener = TcpListener::bind(addr).await?;

            println!("\n╔════════════════════════════════════════════════════════════════════╗");
            println!("║   LED (Local LLM Engine Desktop) — OpenAI API Gateway Running      ║");
            println!("╠════════════════════════════════════════════════════════════════════╣");
            println!("║  Endpoint:     http://{:<48} ║", format!("{}:{}", host, port));
            println!("║  Engine:       {:<52} ║", format!("{:?}", engine_kind));
            println!("║  Routes:       /v1/chat/completions (SSE Stream P99 < 10ms)         ║");
            println!("║                /v1/models, /v1/health, /v1/telemetry, /v1/presets   ║");
            println!("║                /v1/bench/run, /v1/tuner/calibrate, /v1/eval/ast     ║");
            println!("╚════════════════════════════════════════════════════════════════════╝\n");

            run_server(listener, state).await?;
        }

        Commands::Profile { model, ctx } => {
            let hw = HardwareProfile::probe();
            println!("\n=== [LED Hardware Profile & Layer Offload Analyzer] ===");
            println!("CPU Brand:           {}", hw.cpu.brand);
            println!("CPU Physical Cores:  {}", hw.cpu.physical_cores);
            println!("CPU Logical Threads: {}", hw.cpu.logical_threads);
            println!("Inference Threads:   {} (Optimized for Ryzen SMT)", hw.cpu.recommended_inference_threads);
            println!("System RAM (DDR4):   {} MB (Free: {} MB)", hw.total_ram_mb, hw.free_ram_mb);

            if let Some(gpu) = &hw.primary_gpu {
                println!("\nGPU Device:          {}", gpu.name);
                println!("GPU Backend:         {}", gpu.backend);
                println!("VRAM (GDDR6):        {} MB (Free: {} MB)", gpu.total_vram_mb, gpu.free_vram_mb);
                println!("FlashAttention-2:    {}", if gpu.supports_flash_attn { "Supported (Enabled)" } else { "No" });
                println!("MTP Draft Tokens:    {}", if gpu.supports_draft_tokens { "Supported (--draft 2 Enabled)" } else { "No" });
            }

            let offload = LayerOffloadPlan::calculate(
                &model,
                48,
                9200,
                ctx,
                hw.primary_gpu.as_ref().map(|g| g.free_vram_mb).unwrap_or(16384),
                "q8_0",
            );

            println!("\n=== Layer Offload Estimation ({}, num_ctx={}) ===", model, ctx);
            println!("Total Layers:        {}", offload.total_layers);
            println!("GPU VRAM Layers:     {}/{}", offload.gpu_layers, offload.total_layers);
            println!("CPU RAM Layers:      {}/{}", offload.cpu_layers, offload.total_layers);
            println!("Estimated VRAM:      {} MB (KV-Cache: {} MB)", offload.estimated_vram_mb, offload.kv_cache_vram_mb);
            println!("Estimated RAM:       {} MB", offload.estimated_ram_mb);
            println!("Full GPU Offload:    {}", if offload.is_full_gpu_offload { "YES (Zero CPU Bottleneck)" } else { "NO (Hybrid DDR4 Offload)" });

            let flags = HardwareFlagsBuilder::new(&model)
                .with_ctx(ctx)
                .with_threads(hw.cpu.recommended_inference_threads)
                .with_draft_tokens(2)
                .with_flash_attention(true)
                .with_kv_cache("q8_0");

            println!("\nRecommended llama-server CLI flags:");
            println!("  llama-server {}", flags.build_cli_args().join(" "));
        }

        Commands::Tune { model, csv } => {
            let csv_path = csv.unwrap_or_else(|| {
                workspace_root.join("bench_finetune/qwen_25C_14B/benchmark_results_16.csv")
            });

            println!("=== [LED AI Auto-Tuner] Calibrating Surrogate Model ===");
            println!("Target Model: {}", model);
            println!("Training CSV: {:?}", csv_path);

            let bridge = PythonWorkerBridge::new(&workspace_root);
            let res = bridge.run_surrogate_training(&csv_path, &model).await?;

            println!("\nOptimization Status: {}", res.status);
            println!("Best Pareto Preset:  {}", res.best_preset_name);
            println!("Predicted Latency:   {:.2} sec", res.predicted_latency_sec);
            println!("Predicted Throughput:{:.2} tok/sec", res.predicted_tps);
            println!("\nParameter Importance Ranking (SHAP Weights):");
            for fi in &res.feature_importances {
                println!("  #{}: {:<28} (Impact: {:.3})", fi.rank, fi.feature_name, fi.importance);
            }
            println!("\nGenerated Preset:    {}", res.preset_path);
            println!("Generated Modelfile: {}", res.modelfile_path);
        }

        Commands::Eval { file, code } => {
            let code_content = if let Some(p) = file {
                std::fs::read_to_string(p)?
            } else if let Some(c) = code {
                c
            } else {
                eprintln!("Error: Provide either --file <path> or --code <string>");
                std::process::exit(1);
            };

            let bridge = PythonWorkerBridge::new(&workspace_root);
            let res = bridge.evaluate_ast(&code_content).await?;

            println!("\n=== [LED AST Code Quality Evaluation] ===");
            println!("Total Score:     {}/100", res.total_score);
            println!("  - Syntax:      {}/30", res.syntax_score);
            println!("  - Signature:   {}/25", res.signature_score);
            println!("  - Type Hints:  {}/15", res.types_score);
            println!("  - Error Guard: {}/15", res.error_score);
            println!("  - Code Purity: {}/15", res.purity_score);
            println!("Feedback:        {}", res.feedback);
            println!("Valid Code:      {}", if res.is_valid { "YES" } else { "NO" });
        }

        Commands::Presets { sub } => {
            let mgr = PresetManager::new(workspace_root.join("presets"));
            match sub {
                PresetCommands::List => {
                    let presets = mgr.list_presets()?;
                    println!("\n=== [LED Calibrated Presets] ===");
                    for p in presets {
                        println!("• {:<24} (Model: {:<18} | Latency: {:.1}s | TPS: {:.1})",
                            p.preset_name, p.target_model, p.predicted_latency_sec, p.predicted_tps);
                    }
                }
                PresetCommands::Show { name } => {
                    let presets = mgr.list_presets()?;
                    if let Some(p) = presets.into_iter().find(|x| x.preset_name == name) {
                        println!("\n=== Preset: {} ===", p.preset_name);
                        println!("{}", serde_json::to_string_pretty(&p)?);
                        println!("\n=== Modelfile.turbo ===");
                        println!("{}", p.generate_modelfile());
                    } else {
                        eprintln!("Preset '{}' not found.", name);
                    }
                }
            }
        }

        Commands::Bench { model } => {
            println!("=== [LED Bench Lab] Launching 16-Run DoE Matrix for {} ===", model);
            let script = workspace_root.join("matrix_execution/bench_matrix_16.py");
            let python_bin = workspace_root.join(".venv/bin/python3");
            let py = if python_bin.exists() {
                python_bin
            } else {
                PathBuf::from("python3")
            };

            let status = tokio::process::Command::new(py)
                .arg(&script)
                .arg(&model)
                .status()
                .await?;

            if status.success() {
                println!("\nBenchmark completed successfully! Records flushed to bench_finetune/");
            } else {
                eprintln!("\nBenchmark exited with status: {:?}", status);
            }
        }
    }

    Ok(())
}
