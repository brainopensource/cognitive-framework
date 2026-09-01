import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const EvaluationView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Evaluation View</h3>
    <p>Isolated evaluation test results (presence, invocation, grounding, verification, transfer tests).</p>
  </div>
);
