import type { EventEnvelope } from "@aether/contracts";

export type TraceNode = {
  id: string;
  kind: string;
  seq: string;
  runId?: string;
  principal?: string;
  occurredAt?: string;
  summary?: string;
};

export type TraceEdge = {
  id: string;
  source: string;
  target: string;
  relation?: "causal" | "sequence";
};

export type TraceGraph = {
  nodes: TraceNode[];
  edges: TraceEdge[];
};

export function toTraceGraph(envelopes: readonly EventEnvelope[]): TraceGraph {
  const nodes: TraceNode[] = envelopes.map((env) => ({
    id: env.eventId,
    kind: String(env.payload.kind ?? "unknown"),
    seq: env.seq,
    runId: env.runId,
    principal: env.principal,
    occurredAt: env.occurredAt,
    summary:
      typeof env.payload.goal === "string"
        ? env.payload.goal
        : typeof env.payload.text === "string"
        ? env.payload.text
        : typeof env.payload.tool === "string"
        ? env.payload.tool
        : undefined,
  }));

  const edges: TraceEdge[] = [];
  const edgeSet = new Set<string>();

  const addEdge = (source: string, target: string, relation: "causal" | "sequence" = "causal") => {
    const id = `${source}->${target}`;
    if (!edgeSet.has(id) && source !== target) {
      edgeSet.add(id);
      edges.push({ id, source, target, relation });
    }
  };

  const runGroups = new Map<string, EventEnvelope[]>();

  for (const env of envelopes) {
    if (typeof env.parentEventId === "string" && env.parentEventId.trim().length > 0) {
      addEdge(env.parentEventId, env.eventId, "causal");
    }

    if (env.runId) {
      let group = runGroups.get(env.runId);
      if (!group) {
        group = [];
        runGroups.set(env.runId, group);
      }
      group.push(env);
    }
  }

  for (const group of runGroups.values()) {
    const sorted = group.slice().sort((a, b) => {
      const left = BigInt(a.seq);
      const right = BigInt(b.seq);
      return left < right ? -1 : left > right ? 1 : 0;
    });

    for (let i = 1; i < sorted.length; i++) {
      const prev = sorted[i - 1]!;
      const curr = sorted[i]!;
      if (!curr.parentEventId || curr.parentEventId.trim().length === 0) {
        addEdge(prev.eventId, curr.eventId, "sequence");
      }
    }
  }

  return { nodes, edges };
}
