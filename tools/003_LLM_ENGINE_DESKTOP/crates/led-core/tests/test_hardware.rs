use led_core::hardware::{HardwareFlagsBuilder, HardwareProfile, LayerOffloadPlan};

#[test]
fn test_hardware_profiling() {
    let profile = HardwareProfile::probe();
    assert!(profile.cpu.physical_cores >= 1);
    assert!(profile.cpu.logical_threads >= 1);
    assert!(profile.cpu.recommended_inference_threads <= profile.cpu.physical_cores);
    assert!(profile.total_ram_mb > 0);
    assert!(profile.primary_gpu.is_some());
}

#[test]
fn test_layer_offload_plan_full_gpu() {
    // 14B Q4 model (~9.2GB) with 16GB VRAM should fit 100% on GPU
    let plan = LayerOffloadPlan::calculate("qwen2.5-coder:14b", 48, 9200, 2048, 16384, "q8_0");
    assert_eq!(plan.total_layers, 48);
    assert_eq!(plan.gpu_layers, 48);
    assert_eq!(plan.cpu_layers, 0);
    assert!(plan.is_full_gpu_offload);
    assert!(plan.warnings.is_empty());
}

#[test]
fn test_layer_offload_plan_hybrid() {
    // 70B model (~40GB) with 16GB VRAM requires hybrid CPU RAM offload
    let plan = LayerOffloadPlan::calculate("llama-3.3-70b", 80, 40000, 2048, 16384, "q8_0");
    assert_eq!(plan.total_layers, 80);
    assert!(plan.gpu_layers < 80);
    assert!(plan.cpu_layers > 0);
    assert!(!plan.is_full_gpu_offload);
    assert!(!plan.warnings.is_empty());
}

#[test]
fn test_hardware_flags_builder() {
    let flags = HardwareFlagsBuilder::new("qwen2.5-coder:14b")
        .with_ctx(2048)
        .with_threads(8)
        .with_draft_tokens(2)
        .with_flash_attention(true)
        .with_kv_cache("q8_0");

    let args = flags.build_cli_args();
    assert!(args.contains(&"-m".to_string()));
    assert!(args.contains(&"qwen2.5-coder:14b".to_string()));
    assert!(args.contains(&"-c".to_string()));
    assert!(args.contains(&"2048".to_string()));
    assert!(args.contains(&"-t".to_string()));
    assert!(args.contains(&"8".to_string()));
    assert!(args.contains(&"--draft".to_string()));
    assert!(args.contains(&"2".to_string()));
    assert!(args.contains(&"-fa".to_string()));
    assert!(args.contains(&"-ctk".to_string()));
    assert!(args.contains(&"q8_0".to_string()));
}
