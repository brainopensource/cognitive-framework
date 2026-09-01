import React from "react";
import { Box, Text } from "ink";
import { theme } from "../theme/tokens.js";

export type AgentViewData = {
  goal?: string;
  plan?: string;
  strategy?: string;
  progress?: { phase: string; percent?: number };
  budget: { used: string; total: string; percent: number };
  turnCount: number;
  children: readonly { id: string; status: string }[];
};

export const AgentViewPanel: React.FC<{ data?: AgentViewData; height: number }> = (props) => {
  if (!props.data) return <Box><Text>No Agent Data</Text></Box>;
  return (
    <Box flexDirection="column" height={props.height}>
      <Text color={theme.accent}>Goal: <Text color="white">{props.data.goal ?? "N/A"}</Text></Text>
      <Text>Plan: {props.data.plan ?? "N/A"}</Text>
      <Text>Strategy: {props.data.strategy ?? "N/A"}</Text>
      <Text>Progress: {props.data.progress?.phase ?? "N/A"} ({props.data.progress?.percent ?? 0}%)</Text>
      <Text>Budget: {props.data.budget.used}/{props.data.budget.total} ({props.data.budget.percent}%)</Text>
      <Text>Turns: {props.data.turnCount}</Text>
    </Box>
  );
};
