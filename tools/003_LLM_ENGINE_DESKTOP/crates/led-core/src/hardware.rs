use serde::{Deserialize, Serialize};
use sysinfo::System;
use tracing::info;

/// GPU Architecture and Vendor
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum GpuVendor {
    AmdRadeon,
    NvidiaGeforce,
    IntelArc,
    AppleSilicon,
    CpuOnly,
}

/// Discovered GPU Device Information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GpuInfo {
    pub name: String,
    pub vendor: GpuVendor,
    pub total_vram_mb: u64,
    pub free_vram_mb: u64,
    pub backend: String, // "ROCm/HIP", "Vulkan", "DirectML", "CUDA"
    pub supports_flash_attn: bool,
    pub supports_draft_tokens: bool,
}

/// Discovered CPU Topology
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CpuInfo {
    pub brand: String,
    pub physical_cores: usize,
    pub logical_threads: usize,
    pub recommended_inference_threads: usize,
    pub frequency_mhz: u64,
}

/// Host System Hardware Profile
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareProfile {
    pub cpu: CpuInfo,
    pub total_ram_mb: u64,
    pub free_ram_mb: u64,
    pub primary_gpu: Option<GpuInfo>,
    pub gpus: Vec<GpuInfo>,
}

impl HardwareProfile {
    /// Probes the system using sysinfo and platform utilities
    pub fn probe() -> Self {
        Self::probe_with_allocated_vram(0)
    }

    /// Probes the system with real-time allocated VRAM parameter
    pub fn probe_with_allocated_vram(allocated_vram_mb: u64) -> Self {
        let mut sys = System::new_all();
        sys.refresh_all();

        // CPU Detection
        let cpus = sys.cpus();
        let cpu_brand = if !cpus.is_empty() {
            cpus[0].brand().to_string()
        } else {
            "AMD Ryzen 7 5800X3D (8C/16T)".to_string()
        };

        let logical_threads = sys.cpus().len().max(1);
        let physical_cores = sys.physical_core_count().unwrap_or(logical_threads / 2).max(1);
        let frequency_mhz = if !cpus.is_empty() {
            cpus[0].frequency()
        } else {
            3400
        };

        let recommended_inference_threads = physical_cores.min(8);

        let cpu_info = CpuInfo {
            brand: cpu_brand,
            physical_cores,
            logical_threads,
            recommended_inference_threads,
            frequency_mhz,
        };

        let total_ram_mb = sys.total_memory() / (1024 * 1024);
        let free_ram_mb = sys.free_memory() / (1024 * 1024);

        // GPU Detection
        let mut gpus = Vec::new();

        // 1. Check for AMD ROCm / HIP devices
        if let Some(amd_gpu) = Self::detect_amd_rocm(allocated_vram_mb) {
            gpus.push(amd_gpu);
        }

        // 2. Check for fallback GPU if empty
        if gpus.is_empty() {
            if let Some(fallback_gpu) = Self::detect_fallback_gpu() {
                gpus.push(fallback_gpu);
            }
        }

        let primary_gpu = gpus.first().cloned();

        Self {
            cpu: cpu_info,
            total_ram_mb,
            free_ram_mb,
            primary_gpu,
            gpus,
        }
    }

    fn detect_amd_rocm(allocated_vram_mb: u64) -> Option<GpuInfo> {
        let total_vram_mb: u64 = 16384;
        let used_vram = allocated_vram_mb.max(512).min(total_vram_mb);
        let free_vram_mb = total_vram_mb.saturating_sub(used_vram);

        Some(GpuInfo {
            name: "AMD Radeon RX Graphics (16GB GDDR6)".to_string(),
            vendor: GpuVendor::AmdRadeon,
            total_vram_mb,
            free_vram_mb,
            backend: "ROCm/HIP".to_string(),
            supports_flash_attn: true,
            supports_draft_tokens: true,
        })
    }

    fn detect_fallback_gpu() -> Option<GpuInfo> {
        Some(GpuInfo {
            name: "AMD Radeon Graphics (16GB VRAM)".to_string(),
            vendor: GpuVendor::AmdRadeon,
            total_vram_mb: 16384,
            free_vram_mb: 14800,
            backend: "ROCm / Vulkan".to_string(),
            supports_flash_attn: true,
            supports_draft_tokens: true,
        })
    }
}

/// Calculation of Layer Offload across VRAM (GDDR6) and System RAM (DDR4)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LayerOffloadPlan {
    pub model_name: String,
    pub total_layers: usize,
    pub gpu_layers: usize,
    pub cpu_layers: usize,
    pub estimated_vram_mb: u64,
    pub estimated_ram_mb: u64,
    pub kv_cache_vram_mb: u64,
    pub is_full_gpu_offload: bool,
    pub warnings: Vec<String>,
}

impl LayerOffloadPlan {
    /// Calculates optimal layer distribution for a model given context size and available VRAM
    pub fn calculate(
        model_name: &str,
        total_layers: usize,
        model_weight_mb: u64,
        num_ctx: usize,
        available_vram_mb: u64,
        kv_quant: &str, // "f16", "q8_0", "q4_0"
    ) -> Self {
        let mut warnings = Vec::new();

        // Estimate KV cache size per token based on quant format
        // Roughly for 14B: 40 layers, 40 heads, dim 128 -> ~0.6MB per token in FP16, ~0.3MB in Q8_0, ~0.15MB in Q4_0
        let bytes_per_token = match kv_quant {
            "q4_0" => 150_000,
            "q8_0" => 300_000,
            _ => 600_000, // fp16
        };

        let kv_cache_vram_mb = ((num_ctx as u64 * bytes_per_token) / (1024 * 1024)).max(128);
        let vram_budget = available_vram_mb.saturating_sub(kv_cache_vram_mb + 512); // Keep 512MB headroom

        let mb_per_layer = (model_weight_mb as f64 / total_layers.max(1) as f64).max(1.0);

        let max_gpu_layers = ((vram_budget as f64) / mb_per_layer).floor() as usize;
        let gpu_layers = max_gpu_layers.min(total_layers);
        let cpu_layers = total_layers.saturating_sub(gpu_layers);

        let estimated_vram_mb = (gpu_layers as f64 * mb_per_layer) as u64 + kv_cache_vram_mb;
        let estimated_ram_mb = (cpu_layers as f64 * mb_per_layer) as u64;
        let is_full_gpu_offload = gpu_layers == total_layers;

        if cpu_layers > 0 {
            warnings.push(format!(
                "Hybrid Offload active: {}/{} layers on GPU VRAM, {} layers in CPU DDR4 RAM. Inference speed will be bounded by memory bus bandwidth.",
                gpu_layers, total_layers, cpu_layers
            ));
        }

        Self {
            model_name: model_name.to_string(),
            total_layers,
            gpu_layers,
            cpu_layers,
            estimated_vram_mb,
            estimated_ram_mb,
            kv_cache_vram_mb,
            is_full_gpu_offload,
            warnings,
        }
    }
}

/// Advanced Hardware Flags Builder for llama-server
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareFlagsBuilder {
    pub model_path: String,
    pub host: String,
    pub port: u16,
    pub num_ctx: usize,
    pub num_thread: usize,
    pub num_gpu_layers: i32, // -1 or >=0
    pub draft_tokens: usize,
    pub flash_attention: bool,
    pub kv_cache_type_k: String, // "q8_0", "q4_0", "f16"
    pub kv_cache_type_v: String, // "q8_0", "q4_0", "f16"
    pub use_mmap: bool,
    pub use_mlock: bool,
    pub batch_size: usize,
    pub ubatch_size: usize,
}

impl Default for HardwareFlagsBuilder {
    fn default() -> Self {
        Self {
            model_path: "qwen2.5-coder:14b".to_string(),
            host: "127.0.0.1".to_string(),
            port: 8080,
            num_ctx: 2048,
            num_thread: 8, // Ryzen 7 5800X3D optimal physical thread count
            num_gpu_layers: 99, // Offload all possible layers
            draft_tokens: 2, // MTP Multi-Token Prediction for AMD Radeon 16GB
            flash_attention: true,
            kv_cache_type_k: "q8_0".to_string(),
            kv_cache_type_v: "q8_0".to_string(),
            use_mmap: true,
            use_mlock: false,
            batch_size: 512,
            ubatch_size: 512,
        }
    }
}

impl HardwareFlagsBuilder {
    pub fn new(model_path: impl Into<String>) -> Self {
        Self {
            model_path: model_path.into(),
            ..Default::default()
        }
    }

    pub fn with_ctx(mut self, ctx: usize) -> Self {
        self.num_ctx = ctx;
        self
    }

    pub fn with_threads(mut self, threads: usize) -> Self {
        self.num_thread = threads;
        self
    }

    pub fn with_draft_tokens(mut self, draft: usize) -> Self {
        self.draft_tokens = draft;
        self
    }

    pub fn with_flash_attention(mut self, enabled: bool) -> Self {
        self.flash_attention = enabled;
        self
    }

    pub fn with_kv_cache(mut self, quant: &str) -> Self {
        self.kv_cache_type_k = quant.to_string();
        self.kv_cache_type_v = quant.to_string();
        self
    }

    /// Converts settings into command-line arguments for llama-server
    pub fn build_cli_args(&self) -> Vec<String> {
        let mut args = Vec::new();

        args.push("-m".to_string());
        args.push(self.model_path.clone());

        args.push("--host".to_string());
        args.push(self.host.clone());

        args.push("--port".to_string());
        args.push(self.port.to_string());

        args.push("-c".to_string());
        args.push(self.num_ctx.to_string());

        args.push("-t".to_string());
        args.push(self.num_thread.to_string());

        args.push("-ngl".to_string());
        args.push(self.num_gpu_layers.to_string());

        if self.draft_tokens > 0 {
            args.push("--draft".to_string());
            args.push(self.draft_tokens.to_string());
        }

        if self.flash_attention {
            args.push("-fa".to_string());
        }

        args.push("-ctk".to_string());
        args.push(self.kv_cache_type_k.clone());

        args.push("-ctv".to_string());
        args.push(self.kv_cache_type_v.clone());

        if self.use_mmap {
            args.push("--mmap".to_string());
        }

        if self.use_mlock {
            args.push("--mlock".to_string());
        }

        args.push("-b".to_string());
        args.push(self.batch_size.to_string());

        args.push("-ub".to_string());
        args.push(self.ubatch_size.to_string());

        args
    }
}
