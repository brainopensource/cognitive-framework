import React from "react";
import type { StudioFold } from "../store/fold.js";

export const CompositionStudioView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 16, maxWidth: 920 }}>
    <div style={{ padding: 18, background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 8, boxShadow: "var(--shadow-glow)" }}>
      <div style={{ fontSize: 11, letterSpacing: "0.14em", textTransform: "uppercase", color: "var(--signal-flow)" }}>Composition / static authoring</div>
      <h3 style={{ margin: "10px 0 6px", color: "var(--text-primary)" }}>{fold.manifestRef ? "Canonical composition attached" : "No canonical composition attached"}</h3>
      <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: 12, lineHeight: 1.6 }}>{fold.manifestRef ? `Manifest ${fold.manifestRef} is referenced by this run. Editable registry and digest projections are not present in the current client contract.` : "The runtime has not supplied a manifest, registry projection, or canonical digest. Draft authoring stays disabled until those queries exist; this client will not invent plugin slots or identities."}</p>
    </div>
    <div style={{ padding: 14, background: "rgba(0, 210, 255, .06)", border: "1px solid var(--signal-flow)", borderRadius: 8, color: "var(--text-secondary)", fontSize: 12 }}><strong style={{ color: "var(--signal-flow)" }}>Static composition guard.</strong> The canvas may describe declarative slots only; runtime control flow remains exclusively owned by the sequential turn engine.</div>
    <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 12 }}>{["D_H / harness", "D_R / runtime", "D_X / experiment"].map((label) => <div key={label} style={{ padding: 14, background: "var(--bg-card)", border: "1px solid var(--border-subtle)", borderRadius: 7 }}><div style={{ color: "var(--text-muted)", fontSize: 11 }}>{label}</div><div style={{ marginTop: 10, fontFamily: "var(--font-mono)", color: "var(--signal-hold)", fontSize: 12 }}>unavailable</div><div style={{ marginTop: 5, color: "var(--text-muted)", fontSize: 10 }}>canonical query required</div></div>)}</div>
  </div>
);
