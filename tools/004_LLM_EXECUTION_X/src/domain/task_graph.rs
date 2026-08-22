use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::{HashMap, HashSet};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Severity {
    Critical,
    High,
    Normal,
    Low,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum OracleType {
    ExceptionRaised,
    BooleanExact,
    Equality,
    NumericalDelta,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum RiskClass {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AcceptanceCriterion {
    pub id: String,
    pub description: String,
    pub severity: Severity,
    pub oracle_type: OracleType,
}

impl AcceptanceCriterion {
    pub fn new(id: impl Into<String>, description: impl Into<String>) -> Self {
        Self {
            id: id.into(),
            description: description.into(),
            severity: Severity::Normal,
            oracle_type: OracleType::Equality,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationRequirements {
    pub min_mutation_score: f64,
    pub require_ast_assertion_density: f64,
    pub sandbox_tier_required: String,
}

impl Default for VerificationRequirements {
    fn default() -> Self {
        Self {
            min_mutation_score: 0.85,
            require_ast_assertion_density: 1.0,
            sandbox_tier_required: "RESTRICTED_EXECUTION".to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskNode {
    pub id: String,
    pub artifact_target: String,
    pub test_target: String,
    #[serde(default)]
    pub dependencies: Vec<String>,
    #[serde(default)]
    pub interface_contracts: Vec<String>,
    #[serde(default)]
    pub invariants: Vec<String>,
    #[serde(default)]
    pub acceptance_criteria: Vec<AcceptanceCriterion>,
    #[serde(default)]
    pub verification_requirements: VerificationRequirements,
}

impl TaskNode {
    pub fn new(
        id: impl Into<String>,
        artifact_target: impl Into<String>,
        test_target: impl Into<String>,
    ) -> Self {
        Self {
            id: id.into(),
            artifact_target: artifact_target.into(),
            test_target: test_target.into(),
            dependencies: Vec::new(),
            interface_contracts: Vec::new(),
            invariants: Vec::new(),
            acceptance_criteria: Vec::new(),
            verification_requirements: VerificationRequirements::default(),
        }
    }

    pub fn digest(&self) -> String {
        let json_bytes = serde_json::to_vec(self).unwrap_or_default();
        let mut hasher = Sha256::new();
        hasher.update(&json_bytes);
        format!("sha256:{:x}", hasher.finalize())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TaskGraph {
    pub project_id: String,
    pub docstring: String,
    pub risk_class: RiskClass,
    pub tasks: Vec<TaskNode>,
}

impl TaskGraph {
    pub fn topological_order(&self) -> Vec<TaskNode> {
        let task_map: HashMap<String, TaskNode> = self
            .tasks
            .iter()
            .map(|t| (t.id.clone(), t.clone()))
            .collect();
        let mut visited: HashSet<String> = HashSet::new();
        let mut order: Vec<TaskNode> = Vec::new();

        for task in &self.tasks {
            Self::visit(&task.id, &task_map, &mut visited, &mut order);
        }
        order
    }

    fn visit(
        task_id: &str,
        task_map: &HashMap<String, TaskNode>,
        visited: &mut HashSet<String>,
        order: &mut Vec<TaskNode>,
    ) {
        if visited.contains(task_id) {
            return;
        }
        if let Some(node) = task_map.get(task_id) {
            for dep in &node.dependencies {
                Self::visit(dep, task_map, visited, order);
            }
            visited.insert(task_id.to_string());
            order.push(node.clone());
        }
    }
}
