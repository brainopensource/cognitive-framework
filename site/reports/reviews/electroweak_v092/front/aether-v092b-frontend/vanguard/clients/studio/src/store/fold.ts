import type { EventEnvelope } from "../contract/index.js";
import type { InternedRow } from "./event-store.js";

export type RunStatus =
  | "pending"
  | "running"
  | "awaiting_approval"
  | "satisfied"
  | "failed"
  | "denied"
  | "cancelled"
  | "undeterminable";

export type InvocationRecord = {
  readonly id: string;
  readonly turnNumber: number;
  readonly invocationIndex: number;
  readonly model?: string;
  readonly status: "active" | "completed" | "failed" | "escalated";
  readonly costMicros: bigint;
  readonly tokens: number;
  readonly toolCalls: readonly { name: string; status: string }[];
};

export type TurnRecord = {
  readonly turnNumber: number;
  readonly status: "active" | "completed" | "failed";
  readonly invocations: readonly InvocationRecord[];
  readonly totalCostMicros: bigint;
  readonly totalTokens: number;
};

export type PipelineStage =
  | "S0"
  | "S1"
  | "S2"
  | "S3"
  | "S4"
  | "S5"
  | "S6"
  | "S7"
  | "S8"
  | "S8a"
  | "S9"
  | "S10"
  | "S11"
  | "S12";

export type EffectOutcome =
  | "pending"
  | "authorized"
  | "denied"
  | "settled"
  | "rejected"
  | "failed"
  | "undeterminable";

export type EffectRecord = {
  readonly descriptorDigest: string;
  readonly action: string;
  readonly stage: PipelineStage;
  readonly outcome: EffectOutcome;
  readonly intentSeq?: bigint;
  readonly grantId?: string;
  readonly failureCode?: string;
  readonly denialReason?: string;
  readonly rawArgs?: Record<string, unknown>;
  readonly canonicalArgs?: string;
  readonly leaseId?: string;
  readonly costMicros?: bigint;
};

export type LeaseRecord = {
  readonly leaseId: string;
  readonly state: "reserved" | "committed" | "released";
  readonly reservedMicros: bigint;
  readonly actualMicros: bigint;
};

export type PendingApprovalRecord = {
  readonly approvalId: string;
  readonly action: string;
  readonly normalizedDiff: string;
  readonly argsDigest: string;
  readonly descriptorDigest: string;
  readonly principal: string;
  readonly expiresAt: string;
};

export type TrajectorySpan = {
  readonly spanId: string;
  readonly parentSpanId?: string;
  readonly name: string;
  readonly startMs: number;
  readonly endMs: number;
  readonly durationMs: number;
  readonly outcome: EffectOutcome | "satisfied" | "failed" | "unknown";
  readonly depth: number;
};

export type EvidenceRow = {
  readonly line: number;
  readonly title: string;
  readonly category: string;
  readonly state: "absent" | "invalid" | "unverifiable" | "present_valid";
  readonly proofArtifact?: string;
  readonly details: string;
};

export type StudioFold = {
  readonly atSeq: bigint;
  readonly runId: string;
  readonly status: RunStatus;
  readonly repo: string;
  readonly manifestRef?: string;
  readonly totalTokens: number;
  readonly totalCostMicros: bigint;
  readonly turns: readonly TurnRecord[];
  readonly effects: ReadonlyMap<string, EffectRecord>;
  readonly leases: ReadonlyMap<string, LeaseRecord>;
  readonly pendingApproval?: PendingApprovalRecord;
  readonly spans: readonly TrajectorySpan[];
  readonly evidenceRows: readonly EvidenceRow[];
  readonly thoughts: readonly string[];
  readonly toolViews: readonly { name: string; status: string }[];
  readonly unknownEvents: readonly { kind: string; seq: bigint; payload: unknown }[];
  readonly streamHealth: "empty" | "complete" | "live" | "gap" | "interrupted";
};

export function initialStudioFold(): StudioFold {
  return {
    atSeq: 0n,
    runId: "",
    status: "pending",
    repo: ".",
    totalTokens: 0,
    totalCostMicros: 0n,
    turns: [],
    effects: new Map(),
    leases: new Map(),
    spans: [],
    evidenceRows: [
      { line: 1, title: "Deterministic Replay Parity", category: "I-4 Truth", state: "unverifiable", details: "Awaiting fresh-process verification" },
      { line: 2, title: "Signed Exterior Verdict", category: "I-5 Trust Spine", state: "unverifiable", details: "Awaiting external evaluator signature" },
      { line: 3, title: "Untrusted Plugin Isolation", category: "I-6 Isolation", state: "unverifiable", details: "Awaiting canonical isolation evidence" },
      { line: 4, title: "Domain-Blind Kernel Core", category: "I-7 Architecture", state: "unverifiable", details: "Awaiting canonical linter evidence" },
      { line: 5, title: "Sequential Turn Conservation", category: "I-11 Turn Loop", state: "unverifiable", details: "Awaiting trajectory evidence" },
      { line: 6, title: "Durable Intent Reconciliation", category: "F-22 S8a Intent", state: "unverifiable", details: "Awaiting canonical intent/reconciliation evidence" },
      { line: 7, title: "Monotonic Budget Attenuation", category: "Budget Algebra", state: "unverifiable", details: "Awaiting lease and grant evidence" },
      { line: 8, title: "Truthful Trajectory Provenance", category: "I-9 Trajectory", state: "unverifiable", details: "Awaiting canonical trajectory projection" },
      { line: 9, title: "Fail-Closed Operator Approvals", category: "Governance", state: "unverifiable", details: "Awaiting signed approval evidence" },
    ],
    thoughts: [],
    toolViews: [],
    unknownEvents: [],
    streamHealth: "empty",
  };
}

export function reduceStudioFold(prev: StudioFold, row: InternedRow): StudioFold {
  const env: EventEnvelope = row.envelope;
  const kind = String(env.payload?.kind ?? "unknown");
  const payload = env.payload ?? {};

  let status = prev.status;
  let runId = prev.runId || (env.runId ?? "");
  let repo = prev.repo;
  let totalTokens = prev.totalTokens;
  let totalCostMicros = prev.totalCostMicros;
  let pendingApproval = prev.pendingApproval;

  const effects = new Map(prev.effects);
  const leases = new Map(prev.leases);
  const thoughts = [...prev.thoughts];
  const toolViews = [...prev.toolViews];
  const unknownEvents = [...prev.unknownEvents];
  const turns = [...prev.turns];
  const spans = [...prev.spans];

  // Record span representation
  const occurredMs = row.occurredAtMs;
  const duration = typeof payload.durationMs === "number" && payload.durationMs >= 0 ? payload.durationMs : 0;
  const outcomeValue = payload.outcome;
  const spanOutcome: TrajectorySpan["outcome"] = outcomeValue === "failed" ? "failed" : outcomeValue === "denied" ? "denied" : outcomeValue === "undeterminable" ? "undeterminable" : duration > 0 ? "satisfied" : "unknown";
  spans.push({
    spanId: env.spanId,
    parentSpanId: env.parentEventId,
    name: kind,
    startMs: occurredMs,
    endMs: occurredMs + duration,
    durationMs: duration,
    outcome: spanOutcome,
    depth: env.parentEventId ? 1 : 0,
  });

  switch (kind) {
    case "EpisodeStarted": {
      status = "running";
      if (typeof payload.repo === "string") repo = payload.repo;
      break;
    }
    case "EpisodeCompleted": {
      const outcome = String(payload.outcome ?? "unknown");
      if (outcome === "satisfied") status = "satisfied";
      else if (outcome === "denied") status = "denied";
      else if (outcome === "cancelled") status = "cancelled";
      else if (outcome === "undeterminable") status = "undeterminable";
      else status = "failed";
      break;
    }
    case "ObservationProduced": {
      if (typeof payload.text === "string") {
        thoughts.push(payload.text);
      }
      break;
    }
    case "OperatorInvoked": {
      toolViews.push({
        name: String(payload.tool ?? payload.verb ?? "tool"),
        status: String(payload.status ?? "invoked"),
      });
      break;
    }
    case "BudgetCommitted": {
      if (typeof payload.tokens === "number") totalTokens = payload.tokens;
      if (typeof payload.costMicros === "string" || typeof payload.costMicros === "number") {
        totalCostMicros = BigInt(payload.costMicros);
      }
      break;
    }
    case "ApprovalRequested": {
      status = "awaiting_approval";
      pendingApproval = {
        approvalId: String(payload.approvalId ?? ""),
        action: String(payload.action ?? payload.verb ?? "privileged_action"),
        normalizedDiff: String(payload.normalizedDiff ?? payload.diff ?? payload.unifiedDiff ?? ""),
        argsDigest: String(payload.argsDigest ?? ""),
        descriptorDigest: String(payload.descriptorDigest ?? ""),
        principal: String(env.principal ?? "operator"),
        expiresAt: String(payload.expiresAt ?? ""),
      };
      break;
    }
    case "ApprovalResolved": {
      if (status === "awaiting_approval") status = "running";
      pendingApproval = undefined;
      break;
    }
    case "EffectStarted": {
      const desc = String(payload.descriptor ?? payload.descriptorDigest ?? env.spanId);
      effects.set(desc, {
        descriptorDigest: desc,
        action: String(payload.action ?? "effect"),
        stage: "S8a",
        outcome: "pending",
        intentSeq: row.seq,
        grantId: typeof payload.grantId === "string" ? payload.grantId : undefined,
      });
      break;
    }
    case "AuthorizationDenied": {
      const desc = String(payload.descriptor ?? payload.descriptorDigest ?? env.spanId);
      effects.set(desc, {
        descriptorDigest: desc,
        action: String(payload.action ?? "effect"),
        stage: "S5",
        outcome: "denied",
        denialReason: String(payload.reason ?? "policy_denial"),
      });
      break;
    }
    case "EffectCompleted": {
      const desc = String(payload.descriptor ?? payload.descriptorDigest ?? env.spanId);
      const prevEffect = effects.get(desc);
      effects.set(desc, {
        ...prevEffect,
        descriptorDigest: desc,
        action: prevEffect?.action ?? "effect",
        stage: "S12",
        outcome: payload.outcome === "failed" ? "failed" : "settled",
      });
      break;
    }
    case "EffectReconciled": {
      const desc = String(payload.descriptor ?? payload.descriptorDigest ?? env.spanId);
      const uncertainty = String(payload.uncertainty ?? "");
      const outcome: EffectOutcome = uncertainty === "undeterminable" ? "undeterminable" : "settled";
      const prevEffect = effects.get(desc);
      effects.set(desc, {
        ...prevEffect,
        descriptorDigest: desc,
        action: prevEffect?.action ?? "effect",
        stage: "S12",
        outcome,
      });
      break;
    }
    case "LeaseReserved": {
      const leaseId = String(payload.leaseId ?? env.spanId);
      const resVal = payload.reservedMicros;
      const resNum = typeof resVal === "number" || typeof resVal === "string" || typeof resVal === "bigint" ? resVal : 0;
      leases.set(leaseId, {
        leaseId,
        state: "reserved",
        reservedMicros: BigInt(resNum),
        actualMicros: 0n,
      });
      break;
    }
    case "LeaseCommitted": {
      const leaseId = String(payload.leaseId ?? env.spanId);
      const existing = leases.get(leaseId);
      const actVal = payload.actualMicros;
      const actNum = typeof actVal === "number" || typeof actVal === "string" || typeof actVal === "bigint" ? actVal : 0;
      leases.set(leaseId, {
        leaseId,
        state: "committed",
        reservedMicros: existing?.reservedMicros ?? 0n,
        actualMicros: BigInt(actNum),
      });
      break;
    }
    case "LeaseReleased": {
      const leaseId = String(payload.leaseId ?? env.spanId);
      const existing = leases.get(leaseId);
      leases.set(leaseId, {
        leaseId,
        state: "released",
        reservedMicros: existing?.reservedMicros ?? 0n,
        actualMicros: existing?.actualMicros ?? 0n,
      });
      break;
    }
    default: {
      // Preserve unknown events per CT-44
      unknownEvents.push({
        kind,
        seq: row.seq,
        payload: env.payload,
      });
      break;
    }
  }

  return {
    atSeq: row.seq,
    runId,
    status,
    repo,
    manifestRef: prev.manifestRef,
    totalTokens,
    totalCostMicros,
    turns,
    effects,
    leases,
    pendingApproval,
    spans,
    evidenceRows: prev.evidenceRows,
    thoughts,
    toolViews,
    unknownEvents,
    streamHealth: prev.streamHealth === "empty" ? "complete" : prev.streamHealth,
  };
}

export class StudioFoldEngine {
  private snapshots: Array<{ atSeq: bigint; fold: StudioFold }> = [];
  private currentFold: StudioFold = initialStudioFold();

  public foldAll(rows: readonly InternedRow[]): StudioFold {
    let f = initialStudioFold();
    this.snapshots = [{ atSeq: 0n, fold: f }];

    for (let i = 0; i < rows.length; i++) {
      f = reduceStudioFold(f, rows[i]!);
      if ((i + 1) % 100 === 0) {
        this.snapshots.push({ atSeq: rows[i]!.seq, fold: f });
      }
    }

    this.currentFold = f;
    return f;
  }

  public foldToSeq(targetSeq: bigint, rows: readonly InternedRow[]): StudioFold {
    // Find nearest snapshot at or before targetSeq
    let base = this.snapshots[0] ?? { atSeq: 0n, fold: initialStudioFold() };
    for (const snap of this.snapshots) {
      if (snap.atSeq <= targetSeq) {
        base = snap;
      } else {
        break;
      }
    }

    let f = base.fold;
    const remainingRows = rows.filter((r) => r.seq > base.atSeq && r.seq <= targetSeq);
    for (const r of remainingRows) {
      f = reduceStudioFold(f, r);
    }
    return f;
  }

  public getCurrentFold(): StudioFold {
    return this.currentFold;
  }
}
