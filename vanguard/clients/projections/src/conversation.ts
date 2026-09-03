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

    if (kind === "ProposalProduced") {
      const note = typeof env.payload.note === "string" ? env.payload.note.trim() : "";
      if (note) {
        if (currentAgentTurn.text) {
          currentAgentTurn.text += "\n\n" + note;
        } else {
          currentAgentTurn.text = note;
        }
      }
      const action = typeof env.payload.action === "string" ? env.payload.action : "";
      if (action && action !== "finish" && action !== "abstain") {
        const alreadyHasCard = currentAgentTurn.activityCards.some((c) =>
          c.title.includes(action)
        );
        if (!alreadyHasCard) {
          currentAgentTurn.activityCards.push({
            id: `proposal-${env.eventId}`,
            kind: "tool",
            title: `Execute ${action}`,
            details: typeof env.payload.proposalDescriptor === "string"
              ? `descriptor: ${env.payload.proposalDescriptor.slice(0, 16)}...`
              : undefined,
            status: "running",
          });
        }
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
      const outcome = String(env.payload.verdict ?? env.payload.outcome ?? "satisfied");
      currentAgentTurn.verdict = outcome;
      if (
        (outcome === "instrument_error" || outcome === "runtime_error" || outcome === "failed") &&
        env.payload.detail
      ) {
        const detailStr = String(env.payload.detail);
        if (!currentAgentTurn.text.includes(detailStr)) {
          currentAgentTurn.text = currentAgentTurn.text
            ? `${currentAgentTurn.text}\n\n[Failure: ${detailStr}]`
            : `[Failure: ${detailStr}]`;
        }
      }
    }

    if (kind === "RunFailed") {
      const err = String(env.payload.error ?? env.payload.message ?? env.payload.reason ?? "Run failed");
      if (currentAgentTurn.text) {
        currentAgentTurn.text += "\n\n[Error: " + err + "]";
      } else {
        currentAgentTurn.text = "[Error: " + err + "]";
      }
      currentAgentTurn.verdict = "failed";
    }

    if (kind === "RunCancelled") {
      const reason = String(env.payload.reason ?? "User cancelled");
      if (currentAgentTurn.text) {
        currentAgentTurn.text += "\n\n[Cancelled: " + reason + "]";
      } else {
        currentAgentTurn.text = "[Cancelled: " + reason + "]";
      }
      currentAgentTurn.verdict = "cancelled";
    }
  }

  return turns.filter((t) => t.text.trim().length > 0 || t.activityCards.length > 0 || t.verdict);
}
