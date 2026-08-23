use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum StorageKind {
    Inline,
    WorkspaceFile,
    CasBlobRef,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StorageRef {
    pub kind: StorageKind,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub uri: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ArtifactRef {
    pub path: String,
    pub action: String,
    pub digest: String,
    pub byte_size: usize,
    pub storage: StorageRef,
}

impl ArtifactRef {
    pub fn from_content(path: impl Into<String>, content: impl Into<String>, uri: Option<String>) -> Self {
        let p = path.into();
        let c = content.into();
        let bytes = c.as_bytes();
        let mut hasher = Sha256::new();
        hasher.update(bytes);
        let digest = format!("sha256:{:x}", hasher.finalize());
        let byte_size = bytes.len();

        let storage = StorageRef {
            kind: if uri.is_some() {
                StorageKind::WorkspaceFile
            } else {
                StorageKind::Inline
            },
            uri,
            content: Some(c),
        };

        Self {
            path: p,
            action: "CREATED".to_string(),
            digest,
            byte_size,
            storage,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelInvocationMetric {
    pub role: String,
    pub model: String,
    pub latency_ms: u64,
    pub prompt_tokens: usize,
    pub completion_tokens: usize,
    pub tokens_per_sec: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenMetrics {
    pub measurement_status: String,
    pub total_prompt_tokens: usize,
    pub total_completion_tokens: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExecutionAccounting {
    pub total_clock_time_ms: u64,
    pub token_metrics: TokenMetrics,
    pub swarm_breakdown: Vec<ModelInvocationMetric>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GovernanceGrants {
    pub workspace_root: String,
    pub allowed_read_globs: Vec<String>,
    pub allowed_write_globs: Vec<String>,
    pub network_access: String,
}

impl Default for GovernanceGrants {
    fn default() -> Self {
        Self {
            workspace_root: "/tmp".to_string(),
            allowed_read_globs: vec!["**/*".to_string()],
            allowed_write_globs: vec!["*.py".to_string()],
            network_access: "DISABLED".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BudgetAllocation {
    pub max_wall_clock_ms: u64,
    pub max_total_tokens: usize,
    pub max_healing_cycles: usize,
}

impl Default for BudgetAllocation {
    fn default() -> Self {
        Self {
            max_wall_clock_ms: 30000,
            max_total_tokens: 6000,
            max_healing_cycles: 3,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntentPayload {
    pub prompt: String,
    pub target_language: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskRequestEnvelope {
    pub protocol_version: String,
    pub request_id: String,
    pub intent: IntentPayload,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub governance_grants: Option<GovernanceGrants>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub budget: Option<BudgetAllocation>,
    #[serde(default)]
    pub extensions: HashMap<String, serde_json::Value>,
}

impl TaskRequestEnvelope {
    pub fn simple(prompt: impl Into<String>) -> Self {
        Self {
            protocol_version: "1.0.0".to_string(),
            request_id: format!("req-{}", uuid::Uuid::new_v4().simple()),
            intent: IntentPayload {
                prompt: prompt.into(),
                target_language: "python".to_string(),
            },
            governance_grants: None,
            budget: None,
            extensions: HashMap::new(),
        }
    }
}
