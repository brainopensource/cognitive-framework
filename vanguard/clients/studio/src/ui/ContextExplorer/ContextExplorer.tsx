import React, { useState } from "react";
import type { StudioFold } from "../../store/fold.js";
import { CandidateContext } from "./CandidateContext.js";
import { SelectedContext } from "./SelectedContext.js";
import { CompactedContext } from "./CompactedContext.js";
import { RetrievedExperience } from "./RetrievedExperience.js";
import { MemoryView } from "./MemoryView.js";
import { SkillUsage } from "./SkillUsage.js";

export const ContextExplorer: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const [tab, setTab] = useState<string>("candidate");
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <h2>Phase F6: Context Explorer</h2>
      <div style={{ display: "flex", gap: 8 }}>
        <button onClick={() => setTab("candidate")}>Candidate Context</button>
        <button onClick={() => setTab("selected")}>Selected Context</button>
        <button onClick={() => setTab("compacted")}>Compacted Context</button>
        <button onClick={() => setTab("retrieved")}>Retrieved Experience</button>
        <button onClick={() => setTab("memory")}>Memory View</button>
        <button onClick={() => setTab("skill")}>Skill Usage</button>
      </div>
      {tab === "candidate" && <CandidateContext fold={fold} />}
      {tab === "selected" && <SelectedContext fold={fold} />}
      {tab === "compacted" && <CompactedContext fold={fold} />}
      {tab === "retrieved" && <RetrievedExperience fold={fold} />}
      {tab === "memory" && <MemoryView fold={fold} />}
      {tab === "skill" && <SkillUsage fold={fold} />}
    </div>
  );
};
