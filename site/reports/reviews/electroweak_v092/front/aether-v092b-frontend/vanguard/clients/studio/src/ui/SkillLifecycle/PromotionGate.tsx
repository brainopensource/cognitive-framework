import React from "react";
import type { StudioFold } from "../../store/fold.js";

export const PromotionGate: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => (
  <div>
    <h3>Promotion Gate</h3>
    <p>Multi-role promoter review, expected-version guard (CAS), and attestation verification.</p>
  </div>
);
