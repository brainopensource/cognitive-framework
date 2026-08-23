pub mod errors;
pub mod hardware;
pub mod presets;
pub mod server;
pub mod streaming;
pub mod supervisor;
pub mod worker_bridge;

pub use errors::{ErrorCode, LedError, Result};
pub use hardware::{CpuInfo, GpuInfo, GpuVendor, HardwareFlagsBuilder, HardwareProfile, LayerOffloadPlan};
pub use presets::{PresetConfig, PresetManager, PresetOptions};
pub use server::{AppState, ChatCompletionRequest, ChatCompletionResponse, ChatMessage};
pub use streaming::{ChatCompletionChunk, JitterMetrics, StreamJitterTracker};
pub use supervisor::{EngineKind, EngineSupervisor, ProcessStatus, SupervisorTelemetry};
pub use worker_bridge::{AstScoreResult, FeatureImportance, PythonWorkerBridge, TunerOptimizationResult};
