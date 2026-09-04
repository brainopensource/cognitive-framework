import type { EventEnvelope } from "@aether/contracts";

/**
 * Semantic class of an activity card.
 *
 * The backend's writable vocabulary (`domain/ledger/events.py` `WRITABLE_KINDS`,
 * derived from `schemas/mhf/event_envelope.schema.json`) carries far more than
 * tool calls: budget accounting, capability attenuation, sub-agent lifecycle,
 * checkpoint/branch points and plugin health are all first-class events. Folding
 * them all onto `"tool"` would render a coding session as an undifferentiated
 * list, so each family gets its own class and renderers group on it.
 */
export type ConversationActivityCardKind =
  | "tool"
  | "diff"
  | "verification"
  | "approval"
  | "plan"
  | "reflection"
  | "checkpoint"
  | "child"
  | "budget"
  | "context"
  | "capability"
  | "artifact"
  | "plugin"
  | "alarm"
  | "conflict";

export type ConversationActivityCardStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed"
  | "rejected"
  | "info";

export type ConversationActivityCard = {
  id: string;
  kind: ConversationActivityCardKind;
  title: string;
  details?: string;
  diff?: string;
  status: ConversationActivityCardStatus;
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

/** Read a string field, trying several payload spellings, else `""`. */
function str(payload: Record<string, unknown>, ...keys: string[]): string {
  for (const key of keys) {
    const value = payload[key];
    if (typeof value === "string" && value.trim()) return value;
    if (typeof value === "number") return String(value);
  }
  return "";
}

function num(payload: Record<string, unknown>, ...keys: string[]): number | undefined {
  for (const key of keys) {
    const value = payload[key];
    if (typeof value === "number" && Number.isFinite(value)) return value;
  }
  return undefined;
}

/** Append a paragraph to a turn's prose without duplicating it. */
function appendText(turn: ConversationTurn, text: string): void {
  const trimmed = text.trim();
  if (!trimmed || turn.text.includes(trimmed)) return;
  turn.text = turn.text ? `${turn.text}\n\n${trimmed}` : trimmed;
}

/**
 * Mark the most recent card matching `kind` (and still open) as finished.
 *
 * Effects complete out of band from the card that opened them, so the fold
 * closes the newest still-open card of that class rather than assuming the
 * last card pushed is the one that just finished.
 */
function closeCard(
  turn: ConversationTurn,
  kinds: readonly ConversationActivityCardKind[],
  status: ConversationActivityCardStatus,
  durationMs?: number,
  details?: string
): boolean {
  for (let i = turn.activityCards.length - 1; i >= 0; i--) {
    const card = turn.activityCards[i]!;
    if (!kinds.includes(card.kind)) continue;
    if (card.status !== "pending" && card.status !== "running") continue;
    card.status = status;
    if (durationMs !== undefined) card.durationMs = durationMs;
    if (details && !card.details) card.details = details;
    return true;
  }
  return false;
}

/**
 * Fold a ledger event stream into renderable conversation turns.
 *
 * Covers every kind in `WRITABLE_KINDS` that carries meaning for a coding
 * session. Kinds the backend never writes are still accepted where older
 * ledgers and replay fixtures contain them (see `LEGACY_*` notes below):
 * `EventEnvelope.payload.kind` is an open string, and CT-44 requires a reader
 * to preserve rather than reject a kind it does not recognise.
 */
export function toConversationTurns(envelopes: readonly EventEnvelope[]): ConversationTurn[] {
  const turns: ConversationTurn[] = [];
  let currentAgentTurn: ConversationTurn | null = null;
  // Run-scoped: the brief, recovered from `EpisodeStarted.objective`.
  let briefText = "";

  const openAgentTurn = (env: EventEnvelope): ConversationTurn => {
    const turn: ConversationTurn = {
      id: `agent-${env.eventId}`,
      speaker: "agent",
      timestamp: env.occurredAt,
      text: "",
      activityCards: [],
    };
    turns.push(turn);
    return turn;
  };

  for (const env of envelopes) {
    const kind = env.payload.kind;
    const p = env.payload as Record<string, unknown>;

    // The brief travels on `EpisodeStarted`, not on `GoalDeclared`: goal text
    // in an append-only store would be unwithdrawable (ADR-0098 Decision 5),
    // so the ledger's goal event carries digests only. Capture the objective
    // here so the user bubble below has something to show.
    if (kind === "EpisodeStarted") {
      briefText = briefText || str(p, "objective", "brief", "goal");
    }

    // ---- Turn boundaries -------------------------------------------------
    // `UserPromptSubmitted` is not in WRITABLE_KINDS; it is the optimistic
    // turn the TUI injects locally before the daemon has echoed anything.
    if (kind === "GoalDeclared" || kind === "UserPromptSubmitted") {
      const userText = str(p, "goal", "prompt", "brief", "text") || briefText;
      // A live run produces both the optimistic local turn and the ledger's
      // `GoalDeclared` for the same prompt. Rendering both shows the user
      // their own message twice -- and because `GoalDeclared` is digest-only,
      // the second copy would be an empty bubble. Reconcile onto the turn
      // that already exists instead of appending beside it.
      const existingUserTurn = turns.find(
        (t) => t.speaker === "user" && (t.text === userText || (!t.text && !!userText))
      );
      if (existingUserTurn) {
        if (!existingUserTurn.text) existingUserTurn.text = userText;
      } else {
        turns.push({
          id: `user-${env.eventId}`,
          speaker: "user",
          timestamp: env.occurredAt,
          text: userText,
          activityCards: [],
        });
      }
      currentAgentTurn = openAgentTurn(env);
    }

    if (!currentAgentTurn) {
      currentAgentTurn = openAgentTurn(env);
    }
    const turn = currentAgentTurn;

    // `RunStarted`/`EpisodeStarted`/`TurnStarted` open a fresh agent turn only
    // when the current one already carries content, so a run that begins with
    // its own lifecycle events does not render a leading empty bubble.
    if (kind === "RunStarted" || kind === "EpisodeStarted" || kind === "TurnStarted") {
      if (turn.text || turn.activityCards.length > 0 || turn.verdict) {
        currentAgentTurn = openAgentTurn(env);
      }
      continue;
    }

    // ---- Model prose -----------------------------------------------------
    if (kind === "ObservationProduced" && typeof p.text === "string") {
      appendText(turn, p.text);
    }

    if (kind === "ReflectionProduced") {
      const text = str(p, "reflection", "text", "note", "rationale");
      if (text) {
        turn.activityCards.push({
          id: `reflection-${env.eventId}`,
          kind: "reflection",
          title: "Reflection",
          details: text,
          status: "info",
        });
      }
    }

    if (kind === "ProposalProduced") {
      appendText(turn, str(p, "note"));
      const action = typeof p.action === "string" ? p.action : "";
      if (action && action !== "finish" && action !== "abstain") {
        const alreadyHasCard = turn.activityCards.some((c) => c.title.includes(action));
        if (!alreadyHasCard) {
          turn.activityCards.push({
            id: `proposal-${env.eventId}`,
            kind: "tool",
            title: `Execute ${action}`,
            details: typeof p.proposalDescriptor === "string"
              ? `descriptor: ${p.proposalDescriptor.slice(0, 16)}...`
              : undefined,
            status: "running",
          });
        }
      }
    }

    if (kind === "ProposalRejected") {
      const reason = str(p, "reason", "detail", "message") || "rejected";
      if (!closeCard(turn, ["tool", "diff"], "rejected", undefined, reason)) {
        turn.activityCards.push({
          id: `proposal-rejected-${env.eventId}`,
          kind: "tool",
          title: `Proposal rejected: ${reason}`,
          status: "rejected",
        });
      }
    }

    // ---- Planning --------------------------------------------------------
    if (kind === "PlanRevised" || kind === "StrategyChanged") {
      const label = kind === "PlanRevised" ? "Plan revised" : "Strategy changed";
      const summary = str(p, "plan", "strategy", "summary", "detail", "reason");
      const steps = Array.isArray(p.steps)
        ? (p.steps as unknown[]).map((s, i) => `${i + 1}. ${String(s)}`).join("\n")
        : "";
      turn.activityCards.push({
        id: `plan-${env.eventId}`,
        kind: "plan",
        title: summary ? `${label}: ${summary}` : label,
        details: steps || undefined,
        status: "info",
      });
    }

    if (kind === "ProgressAssessed") {
      const assessment = str(p, "assessment", "progress", "status", "detail");
      if (assessment) {
        turn.activityCards.push({
          id: `progress-${env.eventId}`,
          kind: "plan",
          title: `Progress: ${assessment}`,
          status: "info",
        });
      }
    }

    // ---- Effect (tool) lifecycle ----------------------------------------
    // `OperatorInvoked` is deprecated for new writes but stays readable: old
    // ledgers legally contain it (ADR-0098 Decision 4).
    if (kind === "OperatorInvoked" || kind === "EffectStarted") {
      turn.activityCards.push({
        id: `card-${env.eventId}`,
        kind: "tool",
        title: `Execute ${str(p, "tool", "verb", "action") || "tool"}`,
        details: typeof p.argsSummary === "string" ? p.argsSummary : undefined,
        status: "running",
      });
    }

    if (kind === "EffectPreviewed") {
      const diff = str(p, "unifiedDiff", "diff", "normalizedDiff", "preview");
      turn.activityCards.push({
        id: `preview-${env.eventId}`,
        kind: diff ? "diff" : "tool",
        title: `Preview ${str(p, "tool", "verb", "action") || "effect"}`,
        diff: diff || undefined,
        details: diff ? undefined : str(p, "summary", "detail"),
        status: "info",
      });
    }

    if (kind === "EffectCompleted") {
      const durationMs = num(p, "durationMs", "elapsedMs");
      // Preserve the original behaviour of closing the trailing card when no
      // open tool card is found, so replay fixtures keep folding as before.
      if (!closeCard(turn, ["tool", "diff", "verification"], "completed", durationMs)) {
        const last = turn.activityCards[turn.activityCards.length - 1];
        if (last) {
          last.status = "completed";
          if (durationMs !== undefined) last.durationMs = durationMs;
        }
      }
    }

    if (kind === "EffectFailed") {
      const reason = str(p, "error", "reason", "message", "detail") || "effect failed";
      if (!closeCard(turn, ["tool", "diff", "verification"], "failed", num(p, "durationMs"), reason)) {
        turn.activityCards.push({
          id: `effect-failed-${env.eventId}`,
          kind: "tool",
          title: `Failed: ${str(p, "tool", "verb", "action") || "effect"}`,
          details: reason,
          status: "failed",
        });
      }
    }

    if (kind === "EffectRejected") {
      const reason = str(p, "reason", "policy", "detail", "message") || "rejected by policy";
      if (!closeCard(turn, ["tool", "diff"], "rejected", undefined, reason)) {
        turn.activityCards.push({
          id: `effect-rejected-${env.eventId}`,
          kind: "tool",
          title: `Rejected: ${str(p, "tool", "verb", "action") || "effect"}`,
          details: reason,
          status: "rejected",
        });
      }
    }

    if (kind === "EffectReconciled") {
      turn.activityCards.push({
        id: `reconciled-${env.eventId}`,
        kind: "tool",
        title: `Reconciled ${str(p, "tool", "verb", "action") || "effect"}`,
        details: str(p, "outcome", "detail", "resolution") || undefined,
        status: "completed",
      });
    }

    if (kind === "ArtifactCreated") {
      turn.activityCards.push({
        id: `artifact-${env.eventId}`,
        kind: "artifact",
        title: `Artifact: ${str(p, "path", "name", "artifactId", "uri") || "created"}`,
        details: str(p, "digest", "summary", "mediaType") || undefined,
        status: "completed",
      });
    }

    // ---- Verification ----------------------------------------------------
    if (kind === "VerdictRecorded") {
      const verdict = str(p, "verdict", "outcome", "decision");
      const detail = str(p, "detail", "reason", "message");
      turn.activityCards.push({
        id: `verdict-${env.eventId}`,
        kind: "verification",
        title: `Verdict: ${verdict || "recorded"}`,
        details: detail || undefined,
        status: verdict === "satisfied" || verdict === "pass" ? "completed" : "failed",
      });
      if (verdict) turn.verdict = verdict;
    }

    if (kind === "ClaimRecorded" || kind === "EvidenceClaimProduced") {
      const claim = str(p, "claim", "statement", "text", "summary");
      if (claim) {
        turn.activityCards.push({
          id: `claim-${env.eventId}`,
          kind: "verification",
          title: `Claim: ${claim}`,
          details: str(p, "evidence", "citation", "support") || undefined,
          status: "info",
        });
      }
    }

    if (kind === "ConflictDetected") {
      turn.activityCards.push({
        id: `conflict-${env.eventId}`,
        kind: "conflict",
        title: `Conflict: ${str(p, "summary", "detail", "reason", "path") || "detected"}`,
        status: "failed",
      });
    }

    if (kind === "InvalidationChecked") {
      const invalidated = p.invalidated === true || p.stale === true;
      if (invalidated) {
        turn.activityCards.push({
          id: `invalidation-${env.eventId}`,
          kind: "verification",
          title: `Invalidated: ${str(p, "target", "reason", "detail") || "prior evidence"}`,
          status: "failed",
        });
      }
    }

    // ---- Approval & authorization ---------------------------------------
    if (kind === "ApprovalRequested" || kind === "AuthorizationRequested") {
      turn.activityCards.push({
        id: `approval-${env.eventId}`,
        kind: "approval",
        title: `Approval Required: ${str(p, "action", "capability", "verb") || "Mutating Action"}`,
        diff: String(p.unifiedDiff ?? p.diff ?? p.normalizedDiff ?? ""),
        status: "pending",
      });
    }

    if (kind === "ApprovalResolved") {
      const decision = str(p, "decision", "outcome", "resolution");
      const denied = decision === "reject" || decision === "rejected" || decision === "deny";
      const card = turn.activityCards.find((c) => c.kind === "approval" && c.status === "pending");
      if (card) card.status = denied ? "rejected" : "completed";
    }

    if (kind === "AuthorizationDenied") {
      const reason = str(p, "reason", "detail", "policy") || "denied";
      if (!closeCard(turn, ["approval"], "rejected", undefined, reason)) {
        turn.activityCards.push({
          id: `authz-denied-${env.eventId}`,
          kind: "approval",
          title: `Authorization denied: ${reason}`,
          status: "rejected",
        });
      }
    }

    // ---- Capability ------------------------------------------------------
    if (kind === "CapabilityGranted" || kind === "CapabilityRevoked" || kind === "CapabilityAttenuated") {
      const verb = kind === "CapabilityGranted"
        ? "granted"
        : kind === "CapabilityRevoked"
          ? "revoked"
          : "attenuated";
      turn.activityCards.push({
        id: `capability-${env.eventId}`,
        kind: "capability",
        title: `Capability ${verb}: ${str(p, "capability", "name", "scope") || "unnamed"}`,
        details: str(p, "reason", "detail", "constraint") || undefined,
        status: kind === "CapabilityGranted" ? "completed" : "info",
      });
    }

    // ---- Sub-agents ------------------------------------------------------
    if (kind === "ChildSpawned") {
      turn.activityCards.push({
        id: `child-${str(p, "childRunId", "childId", "runId") || env.eventId}`,
        kind: "child",
        title: `Sub-agent: ${str(p, "role", "agent", "preset", "childId") || "spawned"}`,
        details: str(p, "goal", "brief", "task") || undefined,
        status: "running",
      });
    }

    if (kind === "ChildReturned") {
      const childId = str(p, "childRunId", "childId", "runId");
      const outcome = str(p, "outcome", "verdict", "status");
      const existing = childId
        ? turn.activityCards.find((c) => c.kind === "child" && c.id === `child-${childId}`)
        : undefined;
      const target = existing ?? turn.activityCards.slice().reverse()
        .find((c) => c.kind === "child" && c.status === "running");
      if (target) {
        target.status = outcome === "failed" || outcome === "error" ? "failed" : "completed";
        if (outcome && !target.details) target.details = `outcome: ${outcome}`;
      } else {
        turn.activityCards.push({
          id: `child-returned-${env.eventId}`,
          kind: "child",
          title: `Sub-agent returned: ${outcome || "done"}`,
          status: "completed",
        });
      }
    }

    // ---- Budget ----------------------------------------------------------
    if (kind === "BudgetExhausted") {
      turn.activityCards.push({
        id: `budget-${env.eventId}`,
        kind: "budget",
        title: `Budget exhausted: ${str(p, "dimension", "resource", "kind") || "limit reached"}`,
        details: str(p, "limit", "consumed", "detail") || undefined,
        status: "failed",
      });
    }

    if (kind === "BudgetReserved" || kind === "BudgetCommitted" || kind === "BudgetReleased") {
      // Spend is a running total, not a per-event card: fold it onto one card
      // per turn so a long session does not bury the transcript in accounting.
      const micros = num(p, "usdMicros", "costMicros", "amountMicros", "micros");
      if (kind === "BudgetCommitted" && micros !== undefined) {
        const existing = turn.activityCards.find((c) => c.kind === "budget" && c.status === "info");
        const total = (existing?.durationMs ?? 0) + micros;
        if (existing) {
          existing.durationMs = total;
          existing.title = `Cost: $${(total / 1_000_000).toFixed(4)}`;
        } else {
          turn.activityCards.push({
            id: `budget-spend-${env.eventId}`,
            kind: "budget",
            title: `Cost: $${(total / 1_000_000).toFixed(4)}`,
            durationMs: total,
            status: "info",
          });
        }
      }
    }

    // ---- Context management ---------------------------------------------
    if (kind === "ContextCompacted") {
      const before = num(p, "beforeTokens", "tokensBefore");
      const after = num(p, "afterTokens", "tokensAfter");
      turn.activityCards.push({
        id: `context-${env.eventId}`,
        kind: "context",
        title: before !== undefined && after !== undefined
          ? `Context compacted: ${before} → ${after} tokens`
          : "Context compacted",
        details: str(p, "reason", "strategy", "detail") || undefined,
        status: "info",
      });
    }

    if (kind === "EpisodeStateChanged" || kind === "ActivationChanged") {
      const to = str(p, "to", "state", "status", "phase");
      if (to) {
        turn.activityCards.push({
          id: `state-${env.eventId}`,
          kind: "context",
          title: `State: ${to}`,
          details: str(p, "from", "reason") || undefined,
          status: "info",
        });
      }
    }

    // ---- Checkpoints (branch / fork points) ------------------------------
    if (kind === "CheckpointCreated") {
      const branch = str(p, "branchId", "branch") || "main";
      const label = str(p, "checkpointId", "label", "name", "id");
      turn.activityCards.push({
        id: `checkpoint-${label || env.eventId}`,
        kind: "checkpoint",
        title: `Checkpoint ${label || ""}`.trim() + (branch !== "main" ? ` (${branch})` : ""),
        details: str(p, "reason", "summary", "digest") || undefined,
        status: "completed",
      });
    }

    // ---- Plugin lifecycle ------------------------------------------------
    if (
      kind === "PluginFaulted" ||
      kind === "PluginQuiesced" ||
      kind === "PluginRetired" ||
      kind === "PluginActivated" ||
      kind === "PluginVerified" ||
      kind === "PluginDiscovered" ||
      kind === "PluginResolved"
    ) {
      const name = str(p, "plugin", "name", "pluginId") || "plugin";
      const verb = kind.replace("Plugin", "").toLowerCase();
      // Healthy lifecycle chatter stays out of the transcript; only a fault or
      // a forced quiesce/retire changes what the operator should do next.
      const isProblem = kind === "PluginFaulted" || kind === "PluginQuiesced" || kind === "PluginRetired";
      if (isProblem) {
        turn.activityCards.push({
          id: `plugin-${env.eventId}`,
          kind: "plugin",
          title: `Plugin ${verb}: ${name}`,
          details: str(p, "reason", "error", "detail") || undefined,
          status: kind === "PluginFaulted" ? "failed" : "info",
        });
      }
    }

    if (kind === "KernelAlarm") {
      turn.activityCards.push({
        id: `alarm-${env.eventId}`,
        kind: "alarm",
        title: `Kernel alarm: ${str(p, "alarm", "reason", "code", "detail") || "raised"}`,
        details: str(p, "detail", "message") || undefined,
        status: "failed",
      });
    }

    // ---- Terminal outcomes ----------------------------------------------
    // `VerdictProduced` is not in WRITABLE_KINDS; kept for replay fixtures.
    if (kind === "EpisodeCompleted" || kind === "RunCompleted" || kind === "VerdictProduced") {
      const outcome = str(p, "verdict", "outcome") || "satisfied";
      turn.verdict = outcome;
      if (
        (outcome === "instrument_error" || outcome === "runtime_error" || outcome === "failed") &&
        p.detail
      ) {
        appendText(turn, `[Failure: ${String(p.detail)}]`);
      }
    }

    if (kind === "RunAborted") {
      const reason = str(p, "reason", "detail", "message") || "Run aborted";
      appendText(turn, `[Aborted: ${reason}]`);
      turn.verdict = "aborted";
    }

    if (kind === "RunRecovered") {
      const from = str(p, "from", "checkpointId", "reason");
      appendText(turn, `[Recovered${from ? ` from ${from}` : ""}]`);
      // Recovery reopens the run: clear the terminal verdict so the transcript
      // does not show a finished run that is in fact still executing.
      turn.verdict = undefined;
    }

    // `RunFailed`/`RunCancelled` are not in WRITABLE_KINDS -- the daemon
    // surfaces transport-level failure under these names and replay fixtures
    // contain them, so both stay folded.
    if (kind === "RunFailed") {
      appendText(turn, `[Error: ${str(p, "error", "message", "reason") || "Run failed"}]`);
      turn.verdict = "failed";
    }

    if (kind === "RunCancelled") {
      appendText(turn, `[Cancelled: ${str(p, "reason") || "User cancelled"}]`);
      turn.verdict = "cancelled";
    }
  }

  return turns.filter((t) => t.text.trim().length > 0 || t.activityCards.length > 0 || t.verdict);
}
