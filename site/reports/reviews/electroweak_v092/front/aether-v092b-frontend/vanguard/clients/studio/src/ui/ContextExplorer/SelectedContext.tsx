import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const SelectedContext: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Selected Context</h3>
    <p>Chosen tokens with inclusion reasons.</p>
  </div>
);
