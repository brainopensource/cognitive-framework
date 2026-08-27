import React from "react";
import type { StudioFold } from "../../store/fold.js";
import { CandidateView } from "./CandidateView.js";
import { EvaluationView } from "./EvaluationView.js";
import { PromotionGate } from "./PromotionGate.js";
import { RollbackControl } from "./RollbackControl.js";
import { SeparationView } from "./SeparationView.js";

export const SkillPipeline: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
    <h2>Phase F6: Skill Lifecycle</h2>
    <p>Gated self-improvement pipeline (Corpus - Analysis - Candidate - Evaluation - Promotion).</p>
    <CandidateView fold={fold} />
    <EvaluationView fold={fold} />
    <PromotionGate fold={fold} />
    <RollbackControl fold={fold} />
    <SeparationView fold={fold} />
  </div>
);
