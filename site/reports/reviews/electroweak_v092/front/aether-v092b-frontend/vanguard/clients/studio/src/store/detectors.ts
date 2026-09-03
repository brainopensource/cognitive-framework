import type { StudioFold } from "./fold.js";

export type AnomalyFinding = {
  readonly id: string;
  readonly code:
    | "lease_imbalance"
    | "budget_drift"
    | "stale_intent"
    | "signature_failure"
    | "replay_divergence"
    | "escalation_spike"
    | "cost_regression"
    | "lifecycle_stall"
    | "containment_refusal";
  readonly severity: "info" | "warning" | "error";
  readonly title: string;
  readonly message: string;
  readonly atSeq?: bigint;
};

// 1. Lease Imbalance Detector
export function detectLeaseImbalance(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  for (const lease of fold.leases.values()) {
    if (lease.state === "committed" && lease.actualMicros > lease.reservedMicros) {
      findings.push({
        id: `lease-imbalance-${lease.leaseId}`,
        code: "lease_imbalance",
        severity: "error",
        title: "Lease Commitment Exceeded Reservation",
        message: `Lease ${lease.leaseId} actual cost ${lease.actualMicros}µs exceeded reserved ceiling ${lease.reservedMicros}µs.`,
        atSeq: fold.atSeq,
      });
    }
  }
  return findings;
}

// 2. Budget Drift Detector
export function detectBudgetDrift(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  let summedLeaseCosts = 0n;
  for (const lease of fold.leases.values()) {
    if (lease.state === "committed" || lease.state === "released") {
      summedLeaseCosts += lease.actualMicros;
    }
  }
  if (fold.totalCostMicros < summedLeaseCosts) {
    findings.push({
      id: "budget-drift-understated",
      code: "budget_drift",
      severity: "error",
      title: "Budget Conservation Drift Detected",
      message: `Total recorded cost (${fold.totalCostMicros}µs) is lower than committed lease sum (${summedLeaseCosts}µs).`,
      atSeq: fold.atSeq,
    });
  }
  return findings;
}

// 3. Stale Intent Detector (F-22 undeterminable)
export function detectStaleIntents(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  for (const effect of fold.effects.values()) {
    if (effect.outcome === "undeterminable") {
      findings.push({
        id: `stale-intent-${effect.descriptorDigest}`,
        code: "stale_intent",
        severity: "warning",
        title: "Unreconciled S8a Intent (F-22 Undeterminable)",
        message: `Effect ${effect.action} (${effect.descriptorDigest.slice(0, 12)}...) recorded durable intent but outcome is undeterminable.`,
        atSeq: effect.intentSeq,
      });
    }
  }
  return findings;
}

// 4. Signature Failure Detector
export function detectSignatureFailures(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  const sigRow = fold.evidenceRows.find((r) => r.line === 2);
  if (sigRow && sigRow.state === "invalid") {
    findings.push({
      id: "sig-failure-evaluator",
      code: "signature_failure",
      severity: "error",
      title: "Exterior Evaluator Signature Invalid",
      message: "External judge cryptographic signature verification failed.",
      atSeq: fold.atSeq,
    });
  }
  return findings;
}

// 5. Replay Divergence Detector
export function detectReplayDivergence(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  const replayRow = fold.evidenceRows.find((r) => r.line === 1);
  if (replayRow && replayRow.state === "invalid") {
    findings.push({
      id: "replay-divergence",
      code: "replay_divergence",
      severity: "error",
      title: "I-4 Replay Parity Divergence",
      message: "Fresh-process re-execution diverged from recorded event sequence.",
      atSeq: fold.atSeq,
    });
  }
  return findings;
}

// 6. Escalation Spike Detector
export function detectEscalationSpikes(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  let escalationCount = 0;
  for (const turn of fold.turns) {
    for (const inv of turn.invocations) {
      if (inv.status === "escalated") escalationCount++;
    }
  }
  if (escalationCount > 3) {
    findings.push({
      id: "escalation-spike",
      code: "escalation_spike",
      severity: "warning",
      title: "High Invocation Escalation Rate",
      message: `${escalationCount} invocations were escalated across turns, indicating model friction or tool failure.`,
      atSeq: fold.atSeq,
    });
  }
  return findings;
}

// 7. Cost Regression Detector
export function detectCostRegression(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  // 5 USD = 5,000,000 micros ceiling for default coding run
  if (fold.totalCostMicros > 5_000_000n) {
    findings.push({
      id: "cost-regression",
      code: "cost_regression",
      severity: "warning",
      title: "Run Cost Ceilings Approached",
      message: `Run total cost (${fold.totalCostMicros}µs) exceeded $5.00 threshold.`,
      atSeq: fold.atSeq,
    });
  }
  return findings;
}

// 8. Lifecycle Stall Detector
export function detectLifecycleStall(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  if (fold.status === "awaiting_approval" && fold.pendingApproval) {
    findings.push({
      id: `lifecycle-stall-approval-${fold.pendingApproval.approvalId}`,
      code: "lifecycle_stall",
      severity: "info",
      title: "Run Suspended at F-08 Approval Gate",
      message: `Awaiting operator signature for ${fold.pendingApproval.action}.`,
      atSeq: fold.atSeq,
    });
  }
  return findings;
}

// 9. Containment Refusal Detector
export function detectContainmentRefusals(fold: StudioFold): AnomalyFinding[] {
  const findings: AnomalyFinding[] = [];
  for (const effect of fold.effects.values()) {
    if (effect.outcome === "denied") {
      findings.push({
        id: `containment-refusal-${effect.descriptorDigest}`,
        code: "containment_refusal",
        severity: "error",
        title: "Policy Authorization Denied (Fail-Closed)",
        message: `Action ${effect.action} denied by policy: ${effect.denialReason ?? "unknown"}.`,
        atSeq: fold.atSeq,
      });
    }
  }
  return findings;
}

// Run all 9 pure anomaly detectors over folded state
export function runAllAnomalyDetectors(fold: StudioFold): readonly AnomalyFinding[] {
  return [
    ...detectLeaseImbalance(fold),
    ...detectBudgetDrift(fold),
    ...detectStaleIntents(fold),
    ...detectSignatureFailures(fold),
    ...detectReplayDivergence(fold),
    ...detectEscalationSpikes(fold),
    ...detectCostRegression(fold),
    ...detectLifecycleStall(fold),
    ...detectContainmentRefusals(fold),
  ];
}
