import type { AgentViewData } from "../components/agent-view-panel.js";

export function useAgentView(viewModel: any): AgentViewData {
  return {
    goal: viewModel.goal ?? "N/A",
    plan: viewModel.plan ?? "N/A",
    budget: viewModel.budget ?? { used: "0", total: "100", percent: 0 },
    turnCount: viewModel.turnCount ?? 0,
    children: viewModel.children ?? [],
  };
}
