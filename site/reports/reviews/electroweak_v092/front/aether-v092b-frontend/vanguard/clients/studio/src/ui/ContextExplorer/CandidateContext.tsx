import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const CandidateContext: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Candidate Context</h3>
    <p>Available candidate tokens and context sources.</p>
  </div>
);
