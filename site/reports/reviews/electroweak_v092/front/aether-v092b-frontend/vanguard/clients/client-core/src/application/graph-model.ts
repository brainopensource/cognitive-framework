/**
 * @file AUTO-GENERATED
 */

export interface GraphNode {
  readonly id: string;
  readonly kind: string;
  readonly label: string;
  readonly status: string;
  readonly refs: readonly string[];
  readonly semanticClass: string;
}

export interface GraphEdge {
  readonly id: string;
  readonly source: string;
  readonly target: string;
  readonly relation: string;
  readonly authoritative: boolean;
}

export function buildCausalGraph(events: readonly any[]): { nodes: readonly GraphNode[]; edges: readonly GraphEdge[] } {
  return { nodes: [], edges: [] };
}

export function buildArchitectureGraph(
  components: readonly any[],
  activeRun?: any
): { nodes: readonly GraphNode[]; edges: readonly GraphEdge[] } {
  return { nodes: [], edges: [] };
}
