import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const CompactedContext: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Compacted Context</h3>
    <p>Token reduction per compaction epoch.</p>
  </div>
);
