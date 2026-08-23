use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use tracing::{error, info};

use crate::errors::{LedError, Result};

fn default_num_ctx() -> usize {
    2048
}
fn default_num_thread() -> usize {
    8
}
fn default_temperature() -> f64 {
    0.0
}
fn default_top_k() -> usize {
    1
}

/// Preset options conforming to LEDPresetConfig schema
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PresetOptions {
    #[serde(default = "default_num_ctx")]
    pub num_ctx: usize,
    #[serde(default = "default_num_thread")]
    pub num_thread: usize,
    #[serde(default = "default_temperature")]
    pub temperature: f64,
    #[serde(default = "default_top_k")]
    pub top_k: usize,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top_p: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub num_predict: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub draft_tokens: Option<usize>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stop: Option<Vec<String>>,
}

impl Default for PresetOptions {
    fn default() -> Self {
        Self {
            num_ctx: 2048,
            num_thread: 8,
            temperature: 0.0,
            top_k: 1,
            top_p: Some(1.0),
            num_predict: Some(600),
            draft_tokens: Some(2),
            stop: Some(vec![
                "<|im_end|>".to_string(),
                "\n# Example".to_string(),
                "```\n".to_string(),
            ]),
        }
    }
}

/// Canonical Calibrated Preset Configuration
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct PresetConfig {
    pub preset_name: String,
    pub target_model: String,
    #[serde(default)]
    pub options: PresetOptions,
    #[serde(default)]
    pub predicted_latency_sec: f64,
    #[serde(default)]
    pub predicted_tps: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub system_prompt: Option<String>,
}

impl PresetConfig {
    pub fn sweet_spot_qwen14b() -> Self {
        Self {
            preset_name: "qwen_25C_14B_turbo".to_string(),
            target_model: "qwen2.5-coder:14b".to_string(),
            options: PresetOptions {
                num_ctx: 2048,
                num_thread: 8,
                temperature: 0.0,
                top_k: 1,
                top_p: Some(1.0),
                num_predict: Some(600),
                draft_tokens: Some(2),
                stop: Some(vec![
                    "<|im_end|>".to_string(),
                    "\n# Example".to_string(),
                    "```\n".to_string(),
                ]),
            },
            predicted_latency_sec: 14.85,
            predicted_tps: 41.2,
            system_prompt: Some(
                "You are a Python compiler. Output pure code only. Do not use <think> tags. Do not explain."
                    .to_string(),
            ),
        }
    }

    /// Generates Ollama / llama.cpp Modelfile.turbo content
    pub fn generate_modelfile(&self) -> String {
        let mut out = String::new();
        out.push_str(&format!("# LED Auto-Tuned Modelfile: {}\n", self.preset_name));
        out.push_str(&format!("FROM {}\n\n", self.target_model));

        out.push_str(&format!("PARAMETER num_ctx {}\n", self.options.num_ctx));
        out.push_str(&format!("PARAMETER num_thread {}\n", self.options.num_thread));
        out.push_str(&format!("PARAMETER temperature {}\n", self.options.temperature));
        out.push_str(&format!("PARAMETER top_k {}\n", self.options.top_k));

        if let Some(top_p) = self.options.top_p {
            out.push_str(&format!("PARAMETER top_p {}\n", top_p));
        }
        if let Some(num_predict) = self.options.num_predict {
            out.push_str(&format!("PARAMETER num_predict {}\n", num_predict));
        }
        if let Some(stops) = &self.options.stop {
            for s in stops {
                out.push_str(&format!("PARAMETER stop \"{}\"\n", s));
            }
        }

        if let Some(sys) = &self.system_prompt {
            out.push_str(&format!("\nSYSTEM \"\"\"{}\"\"\"\n", sys));
        }

        out
    }

    /// Saves preset to JSON file
    pub fn save_to_file(&self, path: impl AsRef<Path>) -> Result<()> {
        let path = path.as_ref();
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent).map_err(|e| {
                LedError::internal(format!("Failed to create preset dir: {}", e))
            })?;
        }

        let json = serde_json::to_string_pretty(self).map_err(|e| {
            LedError::internal(format!("Failed to serialize preset JSON: {}", e))
        })?;

        std::fs::write(path, json).map_err(|e| {
            LedError::internal(format!("Failed to write preset to {:?}: {}", path, e))
        })?;

        info!("Saved preset to {:?}", path);
        Ok(())
    }

    /// Loads preset from JSON file
    pub fn load_from_file(path: impl AsRef<Path>) -> Result<Self> {
        let path = path.as_ref();
        let content = std::fs::read_to_string(path).map_err(|e| {
            LedError::internal(format!("Failed to read preset from {:?}: {}", path, e))
        })?;

        let preset: Self = serde_json::from_str(&content).map_err(|e| {
            LedError::internal(format!("Failed to parse preset JSON from {:?}: {}", path, e))
        })?;

        Ok(preset)
    }
}

/// Preset Store Manager
pub struct PresetManager {
    presets_dir: PathBuf,
}

impl PresetManager {
    pub fn new(presets_dir: impl Into<PathBuf>) -> Self {
        let dir = presets_dir.into();
        let _ = std::fs::create_dir_all(&dir);
        Self { presets_dir: dir }
    }

    pub fn list_presets(&self) -> Result<Vec<PresetConfig>> {
        let mut presets = Vec::new();
        if !self.presets_dir.exists() {
            return Ok(presets);
        }

        let entries = std::fs::read_dir(&self.presets_dir).map_err(|e| {
            LedError::internal(format!("Failed to read presets directory: {}", e))
        })?;

        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("json") {
                match PresetConfig::load_from_file(&path) {
                    Ok(p) => presets.push(p),
                    Err(e) => error!("Skipping invalid preset file {:?}: {}", path, e),
                }
            }
        }

        // If no presets found, add default sweet spot preset
        if presets.is_empty() {
            let default_preset = PresetConfig::sweet_spot_qwen14b();
            let default_path = self.presets_dir.join("qwen2.5_coder_14b_turbo.json");
            let _ = default_preset.save_to_file(&default_path);
            presets.push(default_preset);
        }

        Ok(presets)
    }

    pub fn save_preset(&self, preset: &PresetConfig) -> Result<PathBuf> {
        let filename = format!("{}.json", preset.preset_name);
        let path = self.presets_dir.join(filename);
        preset.save_to_file(&path)?;
        Ok(path)
    }
}
