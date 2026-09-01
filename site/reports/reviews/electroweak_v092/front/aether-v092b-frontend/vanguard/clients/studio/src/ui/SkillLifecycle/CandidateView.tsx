import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const CandidateView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Candidate View</h3>
    <p>Candidate origin, generating evidence, and skill artifact version.</p>
  </div>
);
