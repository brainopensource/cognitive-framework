/**
 * AUTO-GENERATED: Observatory Event Forensic Inspector
 */
import React, { useState } from "react";

export interface EventForensicInspectorProps {
  readonly eventData: {
    readonly summary: string;
    readonly payload: string;
    readonly relations: string;
    readonly authority: string;
    readonly artifacts: string;
    readonly projectionImpact: string;
    readonly telemetry: string;
    readonly envelope: string;
  };
}

export const EventForensicInspector: React.FC<EventForensicInspectorProps> = ({ eventData }) => {
  const [activeTab, setActiveTab] = useState<number>(0);
  
  const tabs = [
    "Summary",
    "Payload Validated",
    "Relations",
    "Authority/Capability",
    "Artifacts/Digests",
    "Projection Impact",
    "Telemetry",
    "Canonical Envelope"
  ];
  
  const content = [
    eventData.summary,
    eventData.payload,
    eventData.relations,
    eventData.authority,
    eventData.artifacts,
    eventData.projectionImpact,
    eventData.telemetry,
    eventData.envelope
  ];

  return (
    <div style={{ padding: "16px", background: "var(--bg-canvas)", color: "var(--text-primary)", display: "flex", flexDirection: "column", height: "100%" }}>
      <h2>Event Forensic Inspector</h2>
      
      <div style={{ display: "flex", borderBottom: "1px solid var(--border-subtle)", marginBottom: "16px" }}>
        {tabs.map((tab, idx) => (
          <button
            key={idx}
            onClick={() => setActiveTab(idx)}
            style={{
              padding: "8px 16px",
              background: activeTab === idx ? "var(--bg-panel)" : "transparent",
              border: "none",
              borderBottom: activeTab === idx ? "2px solid var(--signal-flow)" : "2px solid transparent",
              color: activeTab === idx ? "var(--text-primary)" : "var(--text-secondary)",
              cursor: "pointer"
            }}
          >
            {tab}
          </button>
        ))}
      </div>
      
      <div style={{ flex: 1, background: "var(--bg-panel)", padding: "16px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", overflow: "auto" }}>
        <pre className="font-mono" style={{ margin: 0, whiteSpace: "pre-wrap" }}>
          {content[activeTab]}
        </pre>
      </div>
    </div>
  );
};
