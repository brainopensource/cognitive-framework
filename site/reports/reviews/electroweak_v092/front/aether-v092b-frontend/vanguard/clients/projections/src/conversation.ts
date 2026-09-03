import type { EventEnvelope } from "@aether/contracts";

export type ConversationActivityCard = {
  id: string;
  kind: "tool" | "diff" | "verification" | "approval";
  title: string;
  details?: string;
  diff?: string;
  status: "pending" | "running" | "completed" | "failed";
  durationMs?: number;
};

export type ConversationTurn = {
  id: string;
  speaker: "user" | "agent" | "system";
  timestamp: string;
  text: string;
  activityCards: ConversationActivityCard[];
  verdict?: string;
};

export function toConversationTurns(envelopes: readonly EventEnvelope[]): ConversationTurn[] {
  const turns: ConversationTurn[] = [];
  let currentAgentTurn: ConversationTurn | null = null;

  for (const env of envelopes) {
    const kind = env.payload.kind;

    if (kind === "GoalDeclared" || kind === "UserPromptSubmitted") {
      const userText = String(env.payload.goal ?? env.payload.prompt ?? env.payload.brief ?? env.payload.text ?? "");
      turns.push({
        id: `user-${env.eventId}`,
        speaker: "user",
        timestamp: env.occurredAt,
        text: userText,
        activityCards: [],
      });
      currentAgentTurn = {
        id: `agent-${env.eventId}`,
        speaker: "agent",
        timestamp: env.occurredAt,
        text: "",
        activityCards: [],
      };
      turns.push(currentAgentTurn);
    }

    if (!currentAgentTurn) {
      currentAgentTurn = {
        id: `agent-${env.eventId}`,
        speaker: "agent",
        timestamp: env.occurredAt,
        text: "",
        activityCards: [],
      };
      turns.push(currentAgentTurn);
    }

    if (kind === "ObservationProduced" && typeof env.payload.text === "string") {
      if (currentAgentTurn.text) {
        currentAgentTurn.text += "\n\n" + env.payload.text;
      } else {
        currentAgentTurn.text = env.payload.text;
      }
    }

    if (kind === "OperatorInvoked" || kind === "EffectStarted") {
      const toolName = String(env.payload.tool ?? env.payload.verb ?? env.payload.action ?? "tool");
      currentAgentTurn.activityCards.push({
        id: `card-${env.eventId}`,
        kind: "tool",
        title: `Execute ${toolName}`,
        details: typeof env.payload.argsSummary === "string" ? env.payload.argsSummary : undefined,
        status: "running",
      });
    }

    if (kind === "EffectCompleted") {
      if (currentAgentTurn.activityCards.length > 0) {
        const last = currentAgentTurn.activityCards[currentAgentTurn.activityCards.length - 1]!;
        last.status = "completed";
        if (typeof env.payload.durationMs === "number") {
          last.durationMs = env.payload.durationMs;
        }
      }
    }

    if (kind === "ApprovalRequested") {
      currentAgentTurn.activityCards.push({
        id: `approval-${env.eventId}`,
        kind: "approval",
        title: `Approval Required: ${String(env.payload.action ?? "Mutating Action")}`,
        diff: String(env.payload.unifiedDiff ?? env.payload.diff ?? env.payload.normalizedDiff ?? ""),
        status: "pending",
      });
    }

    if (kind === "ApprovalResolved") {
      const card = currentAgentTurn.activityCards.find((c) => c.kind === "approval" && c.status === "pending");
      if (card) {
        card.status = "completed";
      }
    }

    if (kind === "EpisodeCompleted" || kind === "RunCompleted" || kind === "VerdictProduced") {
      currentAgentTurn.verdict = String(env.payload.verdict ?? env.payload.outcome ?? "satisfied");
    }
  }

  return turns.filter((t) => t.text.trim().length > 0 || t.activityCards.length > 0 || t.verdict);
}
