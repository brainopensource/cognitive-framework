import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const RollbackControl: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Rollback Control</h3>
    <p>Immediate rollback trigger with audit log.</p>
  </div>
);
