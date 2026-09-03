"""AaaC example: constructs data for RuntimeService; performs no effects."""

from copy import deepcopy

AGENT_DEFINITION = {
    "schemaVersion": "aether.agent-definition/1",
    "name": "coding-agent",
    "description": "Evidence-first coding agent",
    "model": {"router": "configured", "temperature": 0.2, "maxTokens": 32000, "reasoningEffort": "high"},
    "systemPrompt": "Work only through mediated tools and require exterior verification.",
    "skills": ["repository-understanding", "surgical-patching"],
    "context": {"strategy": "l1_l5_hierarchical", "retrieval": ["event-ledger", "repository-index"]},
    "memory": {"policy": "event-sourced", "scopes": ["run", "workspace"]},
    "tools": ["fs.patch", "fs.read", "proc.exec"],
    "plugins": [],
    "budget": {"usdMicros": 2000000, "tokens": 50000, "timeoutMs": 120000, "maxDepth": 2, "maxTurns": 15},
    "approvalPolicy": {"mode": "governed-effects", "editable": True},
    "planner": {"policy": "evidence-first"},
    "recoveryPolicy": {"policy": "checkpoint-resume", "maxRetries": 2},
    "verifier": {"policy": "exterior", "exteriorRequired": True},
    "completionGate": {"policy": "verified-result", "requireVerification": True},
    "subagents": [],
    "topology": {"kind": "single_agent", "channels": []},
}


def build_composition_request() -> dict:
    """Return an inert request for submission through the canonical composition path."""

    return {
        "schema": "aether.composition-request/1",
        "agentDefinition": deepcopy(AGENT_DEFINITION),
    }
