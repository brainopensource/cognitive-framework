import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const SeparationView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Separation View</h3>
    <p>Visual audit of generator vs evaluator vs promoter separation.</p>
  </div>
);
