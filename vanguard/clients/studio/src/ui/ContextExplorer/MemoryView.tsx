import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const MemoryView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Memory View</h3>
    <p>Scoped memory stores and session state.</p>
  </div>
);
