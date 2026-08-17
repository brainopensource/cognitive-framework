import { useState } from "react";
import { Background, Controls, ReactFlow, type Node, type Edge } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { toTraceGraph, type EventEnvelope } from "@vanguard/client-core";
import { SlotFrame } from "./files";

export function TraceSlot({ events }: { events: EventEnvelope[] }) {
  const graph = toTraceGraph(events); const [selected, setSelected] = useState<EventEnvelope>();
  const nodes: Node[] = graph.nodes.map((node, index) => ({ id: node.id, position: { x: (index % 3) * 220, y: Math.floor(index / 3) * 110 }, data: { label: `${node.kind}\nseq ${node.seq}` }, type: "default" }));
  const edges: Edge[] = graph.edges.map(edge => ({ id: edge.id, source: edge.source, target: edge.target }));
  return <SlotFrame title="VG-04 EVENT VISUALIZER"><div className="flow-wrap"><ReactFlow nodes={nodes} edges={edges} fitView onNodeClick={(_, node) => setSelected(events.find(event => event.eventId === node.id))}><Background /><Controls /></ReactFlow></div>{selected && <aside className="payload-drawer"><b>{selected.payload.kind}</b><pre>{JSON.stringify(selected.payload, null, 2)}</pre></aside>}<p className="muted">{graph.nodes.length} nodes · passive VG-04 event stream · no dispatch</p></SlotFrame>;
}
