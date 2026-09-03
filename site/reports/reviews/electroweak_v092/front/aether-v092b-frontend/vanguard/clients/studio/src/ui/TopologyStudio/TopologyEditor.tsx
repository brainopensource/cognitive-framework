import React, { useState } from "react";
import type { StudioFold } from "../../store/fold.js";
import { DeclaredView } from "./DeclaredView.js";
import { LoweredView } from "./LoweredView.js";
import { RealizedView } from "./RealizedView.js";

export const TopologyEditor: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const [viewMode, setViewMode] = useState<"declared" | "lowered" | "realized">("declared");
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Phase F5: Topology Studio & Workflow Studio</h2>
      <div style={{ display: "flex", gap: 8 }}>
        <button onClick={() => setViewMode("declared")}>Declared View</button>
        <button onClick={() => setViewMode("lowered")}>Lowered View</button>
        <button onClick={() => setViewMode("realized")}>Realized View</button>
      </div>
      {viewMode === "declared" && <DeclaredView fold={fold} />}
      {viewMode === "lowered" && <LoweredView fold={fold} />}
      {viewMode === "realized" && <RealizedView fold={fold} />}
    </div>
  );
};
