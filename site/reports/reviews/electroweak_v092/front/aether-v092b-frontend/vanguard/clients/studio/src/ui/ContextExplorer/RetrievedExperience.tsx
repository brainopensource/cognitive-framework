import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const RetrievedExperience: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Retrieved Experience</h3>
    <p>Retrieved episodic/semantic knowledge with provenance and citation links.</p>
  </div>
);
