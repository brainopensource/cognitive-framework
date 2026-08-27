import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const LoweredView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Lowered Execution Plan Preview</h3>
    <p>Backend-lowered execution plan preview (simulation, non-execution).</p>
  </div>
);
