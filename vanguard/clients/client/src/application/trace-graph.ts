import type { EventEnvelope } from "@aether/contracts";

export type TraceNode = { id: string; kind: string; seq: string; runId?: string };
export type TraceEdge = { id: string; source: string; target: string };

export function toTraceGraph(envelopes: readonly EventEnvelope[]): { nodes: TraceNode[]; edges: TraceEdge[] } {
  const nodes: TraceNode[] = envelopes.map((env) => ({
    id: env.eventId,
    kind: String(env.payload.kind ?? "unknown"),
    seq: env.seq,
    runId: env.runId,
  }));

  const edges: TraceEdge[] = [];
  const edgeSet = new Set<string>();

  // Helper to add unique edge
  const addEdge = (source: string, target: string) => {
    const id = `${source}->${target}`;
    if (!edgeSet.has(id)) {
      edgeSet.add(id);
      edges.push({ id, source, target });
    }
  };

  // Group envelopes by runId for linear fallback chaining
  const runGroups = new Map<string, EventEnvelope[]>();

  for (const env of envelopes) {
    // Explicit parentEventId edge
    if (typeof env.parentEventId === "string" && env.parentEventId.trim().length > 0) {
      addEdge(env.parentEventId, env.eventId);
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

  // Linear fallback edges for envelopes in the same runId without parentEventId
  for (const group of runGroups.values()) {
    const sorted = group.slice().sort((a, b) => {
      const left = BigInt(a.seq);
      const right = BigInt(b.seq);
      return left < right ? -1 : left > right ? 1 : 0;
    });

    for (let i = 1; i < sorted.length; i++) {
      const prev = sorted[i - 1]!;
      const curr = sorted[i]!;
      // Only add linear chain edge if curr does not have an explicit parentEventId
      if (typeof curr.parentEventId !== "string" || curr.parentEventId.trim().length === 0) {
        addEdge(prev.eventId, curr.eventId);
      }
    }
  }

  return { nodes, edges };
}
