use serde::{Deserialize, Serialize};
use std::path::{Path, PathBuf};
use std::process::Stdio;
use tokio::process::Command;
use tracing::error;

use crate::errors::{LedError, Result};

/// Python AST Evaluation Result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AstScoreResult {
    pub total_score: u32,
    pub syntax_score: u32,
    pub signature_score: u32,
    pub types_score: u32,
    pub error_score: u32,
    pub purity_score: u32,
    pub feedback: String,
    pub is_valid: bool,
}

/// Feature Importance (SHAP weight)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FeatureImportance {
    pub feature_name: String,
    pub importance: f64,
    pub rank: usize,
}

/// AI Auto-Tuner Optimization Result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TunerOptimizationResult {
    pub status: String,
    pub target_model: String,
    pub best_preset_name: String,
    pub predicted_latency_sec: f64,
    pub predicted_tps: f64,
    pub options: serde_json::Value,
    pub feature_importances: Vec<FeatureImportance>,
    pub preset_path: String,
    pub modelfile_path: String,
}

/// Python ML Worker Bridge
#[derive(Clone)]
pub struct PythonWorkerBridge {
    workspace_root: PathBuf,
    python_bin: PathBuf,
}

impl PythonWorkerBridge {
    pub fn new(workspace_root: impl Into<PathBuf>) -> Self {
        let root = workspace_root.into();
        let venv_python = root.join(".venv/bin/python3");
        let python_bin = if venv_python.exists() {
            venv_python
        } else {
            PathBuf::from("python3")
        };

        Self {
            workspace_root: root,
            python_bin,
        }
    }

    /// Evaluates Python code using the isolated AST validator
    pub async fn evaluate_ast(&self, code: &str) -> Result<AstScoreResult> {
        let evaluator_script = self
            .workspace_root
            .join("matrix_execution/ast_evaluator.py");

        let mut child = Command::new(&self.python_bin)
            .arg(&evaluator_script)
            .arg("--stdin")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .map_err(|e| {
                LedError::internal(format!("Failed to spawn AST evaluator: {}", e))
            })?;

        if let Some(mut stdin) = child.stdin.take() {
            use tokio::io::AsyncWriteExt;
            let _ = stdin.write_all(code.as_bytes()).await;
            let _ = stdin.flush().await;
        }

        let output = child.wait_with_output().await.map_err(|e| {
            LedError::internal(format!("AST evaluator process error: {}", e))
        })?;

        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);

        if !output.status.success() {
            // Return ERR-LED-005 for syntax errors or failure
            let res = AstScoreResult {
                total_score: 0,
                syntax_score: 0,
                signature_score: 0,
                types_score: 0,
                error_score: 0,
                purity_score: 0,
                feedback: format!("Syntax: Error ({})", stderr.trim()),
                is_valid: false,
            };
            return Ok(res);
        }

        match serde_json::from_str::<AstScoreResult>(&stdout) {
            Ok(res) => Ok(res),
            Err(e) => {
                error!("Failed to parse AST evaluator output: {} | raw: {}", e, stdout);
                Err(LedError::ast_syntax_error(format!(
                    "Invalid AST evaluator response: {}",
                    e
                )))
            }
        }
    }

    /// Runs surrogate ML optimization over DoE results
    pub async fn run_surrogate_training(
        &self,
        csv_file: &Path,
        model_name: &str,
    ) -> Result<TunerOptimizationResult> {
        let script = self.workspace_root.join("matrix_execution/train_surrogate.py");

        let output = Command::new(&self.python_bin)
            .arg(&script)
            .arg(csv_file)
            .arg(model_name)
            .arg("--json-output")
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .output()
            .await
            .map_err(|e| {
                LedError::internal(format!("Failed to run surrogate trainer: {}", e))
            })?;

        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);

        if !output.status.success() {
            if stderr.contains("variance") || stdout.contains("variance") {
                return Err(LedError::autotuner_low_variance(
                    "Insufficient variance in training dataset for ML regression.",
                ));
            }
            return Err(LedError::internal(format!(
                "Surrogate training failed: {}",
                stderr
            )));
        }

        match serde_json::from_str::<TunerOptimizationResult>(&stdout) {
            Ok(res) => Ok(res),
            Err(_) => {
                // Parse fallback if stdout had extra logs
                if let Some(json_start) = stdout.find('{') {
                    if let Some(json_end) = stdout.rfind('}') {
                        let slice = &stdout[json_start..=json_end];
                        if let Ok(res) = serde_json::from_str::<TunerOptimizationResult>(slice) {
                            return Ok(res);
                        }
                    }
                }
                Err(LedError::internal(format!(
                    "Failed to parse surrogate output: {}",
                    stdout
                )))
            }
        }
    }
}
