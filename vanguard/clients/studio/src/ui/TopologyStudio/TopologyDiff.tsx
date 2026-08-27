import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const TopologyDiff: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Topology Version Diff</h3>
    <p>Visual diff between topology versions.</p>
  </div>
);
