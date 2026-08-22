use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum EvidenceKind {
    AstSyntax,
    RuffLint,
    Pytest,
    MutationProbe,
    SecurityAudit,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Evidence {
    pub kind: EvidenceKind,
    pub collector_id: String,
    pub metrics: HashMap<String, serde_json::Value>,
    pub artifacts_evaluated: Vec<String>,
    pub raw_output_digest: String,
    pub timestamp: DateTime<Utc>,
}

impl Evidence {
    pub fn new(
        kind: EvidenceKind,
        collector_id: impl Into<String>,
        metrics: HashMap<String, serde_json::Value>,
        artifacts_evaluated: Vec<String>,
        raw_output: &str,
    ) -> Self {
        let mut hasher = Sha256::new();
        hasher.update(raw_output.as_bytes());
        let raw_output_digest = format!("sha256:{:x}", hasher.finalize());

        Self {
            kind,
            collector_id: collector_id.into(),
            metrics,
            artifacts_evaluated,
            raw_output_digest,
            timestamp: Utc::now(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvidenceSet {
    pub task_id: String,
    pub evidences: Vec<Evidence>,
}

impl EvidenceSet {
    pub fn new(task_id: impl Into<String>, evidences: Vec<Evidence>) -> Self {
        Self {
            task_id: task_id.into(),
            evidences,
        }
    }

    pub fn get_by_kind(&self, kind: &EvidenceKind) -> Option<&Evidence> {
        self.evidences.iter().find(|e| &e.kind == kind)
    }

    pub fn digest(&self) -> String {
        let bytes = serde_json::to_vec(self).unwrap_or_default();
        let mut hasher = Sha256::new();
        hasher.update(&bytes);
        format!("sha256:{:x}", hasher.finalize())
    }
}
