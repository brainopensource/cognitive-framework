import type {
  EventEnvelope,
  WorkflowExecutionView,
  AgentParticipantState,
} from "@aether/contracts";

export function reduceMultiAgentExecution(
  events: EventEnvelope[],
  workflowId: string = "default-workflow",
  workflowTitle: string = "Autonomous Multi-Agent Workflow"
): WorkflowExecutionView {
  const participantsMap = new Map<string, AgentParticipantState>();
  let currentStage = "Initial";
  const intermediateArtifacts: string[] = [];
  let isTerminal = false;

  for (const env of events) {
    const kind = String(env.payload.kind ?? "");
    const payload = env.payload;
    const timestamp = env.occurredAt || new Date().toISOString();

    if (kind === "AgentSpawned" || kind === "AgentActivated") {
      const agentId = String(payload.agentId ?? payload.childAgentId ?? "child-agent");
      const role = String(payload.role ?? "Specialist");
      const parentAgentId = payload.parentAgentId ? String(payload.parentAgentId) : undefined;
      participantsMap.set(agentId, {
        agentId,
        role,
        status: "active",
        currentActivity: "Starting turn",
        parentAgentId,
        handoffTimestamp: timestamp,
      });
    }

    if (kind === "AgentHandoff" || kind === "TaskDelegated") {
      const fromAgent = String(payload.fromAgentId ?? "parent");
      const toAgent = String(payload.toAgentId ?? "child");
      const role = String(payload.targetRole ?? "Delegate");
      participantsMap.set(toAgent, {
        agentId: toAgent,
        role,
        status: "active",
        currentActivity: String(payload.taskDescription ?? "Handling delegated task"),
        parentAgentId: fromAgent,
        handoffTimestamp: timestamp,
      });
      const currentFrom = participantsMap.get(fromAgent);
      if (currentFrom) {
        currentFrom.status = "waiting";
        currentFrom.currentActivity = `Waiting for handoff from ${toAgent}`;
      }
    }

    if (kind === "AgentCompleted" || kind === "AgentDeactivated") {
      const agentId = String(payload.agentId ?? "");
      const current = participantsMap.get(agentId);
      if (current) {
        current.status = "completed";
        current.currentActivity = "Execution finished";
      }
    }

    if (kind === "StageTransitioned") {
      currentStage = String(payload.stage ?? payload.stageName ?? currentStage);
    }

    if (kind === "ArtifactProduced" && payload.artifactId) {
      intermediateArtifacts.push(String(payload.artifactId));
    }

    if (kind === "RunCompleted" || kind === "WorkflowCompleted" || kind === "VerdictProduced") {
      isTerminal = true;
    }
  }

  // Ensure default root agent if map is empty
  if (participantsMap.size === 0) {
    participantsMap.set("primary-agent", {
      agentId: "primary-agent",
      role: "Lead Coordinator",
      status: isTerminal ? "completed" : "active",
      currentActivity: isTerminal ? "Workflow Completed" : "Coordinating Turn",
    });
  }

  return {
    workflowId,
    title: workflowTitle,
    currentStage,
    participants: Array.from(participantsMap.values()),
    intermediateArtifacts,
    isTerminal,
  };
}
