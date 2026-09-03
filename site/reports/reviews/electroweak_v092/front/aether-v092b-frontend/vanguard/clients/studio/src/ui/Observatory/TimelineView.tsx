/**
 * AUTO-GENERATED: Observatory Timeline View
 */
import React, { useState } from "react";

export interface TimelineEvent {
  readonly id: string;
  readonly kind: string;
  readonly role: string;
  readonly opId: string;
  readonly status: "committed" | "projected" | "telemetry";
  readonly lineage: string;
  readonly capabilityGrant?: string;
  readonly artifact?: string;
  readonly summary: string;
}

export interface TimelineViewProps {
  readonly events: readonly TimelineEvent[];
}

export const TimelineView: React.FC<TimelineViewProps> = ({ events }) => {
  const [filterLineage, setFilterLineage] = useState("");
  const [filterKind, setFilterKind] = useState("");
  const [filterRole, setFilterRole] = useState("");
  const [filterOpId, setFilterOpId] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [filterCapability, setFilterCapability] = useState("");
  const [filterArtifact, setFilterArtifact] = useState("");

  const filtered = events.filter((e) => {
    if (filterLineage && !e.lineage.includes(filterLineage)) return false;
    if (filterKind && !e.kind.includes(filterKind)) return false;
    if (filterRole && !e.role.includes(filterRole)) return false;
    if (filterOpId && !e.opId.includes(filterOpId)) return false;
    if (filterStatus && e.status !== filterStatus) return false;
    if (filterCapability && (!e.capabilityGrant || !e.capabilityGrant.includes(filterCapability))) return false;
    if (filterArtifact && (!e.artifact || !e.artifact.includes(filterArtifact))) return false;
    return true;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px", padding: "16px", background: "var(--bg-canvas)", color: "var(--text-primary)" }}>
      <h2>Timeline View</h2>
      <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
        <input placeholder="Filter Lineage..." value={filterLineage} onChange={e => setFilterLineage(e.target.value)} />
        <input placeholder="Filter Kind..." value={filterKind} onChange={e => setFilterKind(e.target.value)} />
        <input placeholder="Filter Role..." value={filterRole} onChange={e => setFilterRole(e.target.value)} />
        <input placeholder="Filter OpID..." value={filterOpId} onChange={e => setFilterOpId(e.target.value)} />
        <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
          <option value="">All Statuses</option>
          <option value="committed">Committed</option>
          <option value="projected">Projected</option>
          <option value="telemetry">Telemetry</option>
        </select>
        <input placeholder="Filter Capability..." value={filterCapability} onChange={e => setFilterCapability(e.target.value)} />
        <input placeholder="Filter Artifact..." value={filterArtifact} onChange={e => setFilterArtifact(e.target.value)} />
      </div>
      
      <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
        {filtered.map(e => (
          <div key={e.id} style={{ border: "1px solid var(--border-subtle)", padding: "8px", borderRadius: "var(--radius-sm)", background: "var(--bg-card)" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <strong>{e.kind}</strong>
              <span className="badge-mono">{e.status}</span>
            </div>
            <div style={{ fontSize: "12px", color: "var(--text-secondary)", marginTop: "4px" }}>
              <span>Role: {e.role} | OpID: {e.opId} | Lineage: {e.lineage}</span>
            </div>
            <p style={{ margin: "8px 0 0 0", fontSize: "14px" }}>{e.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
