import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const SkillUsage: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Skill Usage</h3>
    <p>Active skills invoked in prompt with provenance tracking.</p>
  </div>
);
