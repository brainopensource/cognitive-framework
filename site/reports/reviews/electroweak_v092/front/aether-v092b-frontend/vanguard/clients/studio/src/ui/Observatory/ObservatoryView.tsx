import React from "react";
import type { StudioFold } from "../../store/fold.js";
import { TimelineView } from "./TimelineView.js";

export const ObservatoryView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Observatory</h2>
      <TimelineView events={[]} />
    </div>
  );
};
