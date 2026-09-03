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

export function emptyTraceGraph(): TraceGraph {
  return { nodes: [], edges: [] };
}

export function reduceTraceGraph(previous: TraceGraph, envelope: EventEnvelope): TraceGraph {
  const nextNode: TraceNode = {
    id: envelope.eventId,
    kind: String(envelope.payload.kind ?? "unknown"),
    seq: envelope.seq,
    runId: envelope.runId,
    principal: envelope.principal,
    occurredAt: envelope.occurredAt,
    summary:
      typeof envelope.payload.goal === "string"
        ? envelope.payload.goal
        : typeof envelope.payload.text === "string"
        ? envelope.payload.text
        : typeof envelope.payload.tool === "string"
        ? envelope.payload.tool
        : undefined,
  };

  const nextNodes = [...previous.nodes, nextNode];
  const nextEdges = [...previous.edges];
  const edgeSet = new Set(previous.edges.map((e) => e.id));

  if (typeof envelope.parentEventId === "string" && envelope.parentEventId.trim().length > 0) {
    const id = `${envelope.parentEventId}->${envelope.eventId}`;
    if (!edgeSet.has(id) && envelope.parentEventId !== envelope.eventId) {
      nextEdges.push({ id, source: envelope.parentEventId, target: envelope.eventId, relation: "causal" });
    }
  } else if (previous.nodes.length > 0) {
    const lastNode = previous.nodes[previous.nodes.length - 1]!;
    const id = `${lastNode.id}->${envelope.eventId}`;
    if (!edgeSet.has(id) && lastNode.id !== envelope.eventId) {
      nextEdges.push({ id, source: lastNode.id, target: envelope.eventId, relation: "sequence" });
    }
  }

  return { nodes: nextNodes, edges: nextEdges };
}

